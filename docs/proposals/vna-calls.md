# Draft: logical calls for vector network analyzers (VNA)

Status: **draft for discussion**. Nothing here is in `schema/` or `instruments_lib.json` yet. A command goes into the library only when the manual of the instrument documents it.

## 1. What the LiteVNA manual says (LiteVNA User Guide, appendix "USB data interface", pages 25-30)

* The LiteVNA (62, 64, 67) is a *T/R* VNA: it measures **S11 and S21 only** (reflection and transmission from port 1), 50 kHz to 6.3 GHz.
* It is a USB CDC virtual serial port with a **binary register protocol** (the SAA2 / NanoVNA-APP protocol), **not SCPI and not text**. The baud rate does not matter on USB. The host sends opcodes (`0x10` READ, `0x20` WRITE, `0x22` WRITE4, `0x23` WRITE8, `0x18` READFIFO, ...) and little-endian register values; there is no terminator.
* Sweep: registers `sweepStartHz` (uint64, 0x00), `sweepStepHz` (uint64, 0x10), `sweepPoints` (uint16, 0x20; 1 to 65535 over USB). **There is no "stop frequency"**: stop = start + step x (points - 1). Writing any of these registers puts the device in "USB data mode" and stops the on-device UI.
* Other registers: `Average` (0x40, 1-80: an FFT multiplier that changes the IF bandwidth, not a value in Hz), `LowFrequencyPower` / `HighFrequencyPower` (0x41 / 0x42, levels 1-3, **not dBm**), `ChannelSelect` (0x44: 0x01 S11, 0x02 S21, 0x00 both), `rawSamplesMode` (0x26), `battery value` (0x5C), identification registers `deviceVariant` (0xF0), `hardwareRevision` (0xF2), `firmwareMajor/Minor` (0xF3/0xF4).
* Data: a FIFO (`valuesFIFO`, 0x30) of **32-byte records**: reference wave `fwd0` and incoming waves `rev0` (S11) and `rev1` (S21) as int32 real/imaginary pairs plus a frequency index. The values are **raw**: "user calibrations are never applied and cannot be read over USB", and each value is at a random phase, so the host must divide by the reference channel (complex division). The sweep runs continuously; for an on-demand sweep the FIFO is cleared (write to the FIFO address) before reading. A read is limited to 255 records, so 1024 points need several READFIFO commands.

### Consequences

1. The LiteVNA cannot be a plain "step plan" like the SCPI instruments: the number of reads depends on the number of points, the data needs complex arithmetic, and the calibration has to be done **in software** by the host. It is a **`driver`** model (`access: "driver"`, as for the Analog Discovery) implemented in Python (pyserial); the library entry only names the driver functions.
2. The logical calls must hide the differences: *frequency start/stop/points* for the user, *start/step/points* inside the driver; *S-parameters* as a list; *calibration* as something the instrument does (SCPI VNAs) or the driver does (LiteVNA).
3. A call the LiteVNA cannot do stays "not supported" (`CALL-001`); a value it cannot do (S12, S22, a power in dBm) is "not handled by this model" (`CALL-002`), exactly as for the other categories.

## 2. Hypothesis: calls

Names follow the existing categories. *Requirement* is a first guess: the real one is decided by the rule "mandatory = documented in the manual of every model of the category" once the other manuals are chosen.

| Call | Kind | Arguments | Result | Guess | LiteVNA |
|---|---|---|---|---|---|
| `identification_query` | query | - | string | mandatory | driver builds it from `deviceVariant` + hardware + firmware |
| `reset` | action | - | - | optional | - |
| `clear_status`, `error_query`, `self_test` | | | | optional | not supported |
| `set_frequency_sweep` | set | `start_frequency` (Hz), `stop_frequency` (Hz), `points` (int) | - | mandatory | start, step = (stop - start)/(points - 1), points |
| `set_frequency_start`, `set_frequency_stop`, `set_frequency_center`, `set_frequency_span`, `set_sweep_points` | set | value | - | optional | not supported (only the combined call) |
| `set_sweep_type` | set | `LINEAR`, `LOG`, `SEGMENT` | - | optional | `LINEAR` only |
| `set_if_bandwidth` | set | Hz | - | optional | not handled (the LiteVNA has an averaging multiplier, not Hz) |
| `set_source_power` | set | dBm | - | optional | not handled (levels 1-3, not dBm) |
| `set_averaging` | set | count (int), state | - | optional | `Average` register (1-80), meaning documented as a multiplier |
| `select_sparameters` | set | list of `S11`, `S21`, `S12`, `S22` | - | mandatory | `S11`, `S21`, both; others `CALL-002` |
| `run_sweep` | action | - | - | mandatory | clear the FIFO and wait for a full sweep |
| `read_sparameters` | query | - | `sparameters` | mandatory | FIFO read, division by the reference, software calibration if applied |
| `query_frequencies` | query | - | list of Hz | optional | computed from start/step/points |
| `calibration_measure` | action | `standard` (`OPEN`, `SHORT`, `LOAD`, `THRU`, ...), `port` | - | optional | driver stores the raw sweep of the standard |
| `calibration_apply` | action | `kind` (`NONE`, `OSL_1PORT`, `FULL_2PORT`...) | - | optional | driver computes the error terms and applies them to `read_sparameters` |
| `set_correction_state` | set | bool | - | optional | driver on/off |
| `save_calibration`, `recall_calibration` | set | name | - | optional | driver, to a file |
| `set_local`, `set_remote` | action | - | - | optional | not supported |

New result type **`sparameters`**: a dict with `frequency` (Hz, array), one complex array per requested parameter (`s11`, `s21`, ...), and `calibrated` (bool). Complex numbers are returned as a pair of arrays (real, imaginary) so that the value is plain JSON and numpy-free.

## 3. Decisions (owner) and what was built

1. **Calibration** is done by a *calibration tool* of the application ("Calibrate VNA": it reads the VNA of the `.inst` file, runs the calibration calls of the model and tells the operator what to connect). The LiteVNA driver calibrates in software, so that for the application the LiteVNA is **identical** to the other instruments. The tool itself is not written yet.
2. **Complex data**: arrays of real and imaginary parts (`sparameters` type).
3. **VNAs the owner does not have** are `experimental` (hidden unless the user enables experimental instruments): none has been tested on a real instrument.
4. **Models**: Zenko LiteVNA 62/64/67 (driver), Siglent SNA5000A, SNA5000X-E, SNA6000A and SHN900A (one SCPI series, 19 models), R&S ZNB and ZNL/ZNLE (16 models) and the older R&S ZVA, ZVB, ZVT and ZVL (14 models, `Rohde_Schwarz_ZVx_Series`).

### Calls (schema `vna.json`)

`identification_query`, `set_frequency_sweep(start_frequency, stop_frequency, points)`, `run_sweep`, `read_sparameters(sparameters)`, the calibration flow `calibration_begin(kind, port, port2)` -> `calibration_measure(standard, port, port2)` (once per standard) -> `calibration_apply`, `set_correction_state`, `calibration_clear` (all mandatory), and the optional `set_source_power`, `set_if_bandwidth` (the LiteVNA has neither).

Differences from the first draft: there is **no `select_sparameters`** (a step plan cannot remember a selection, and the Siglent read needs the parameter in the command): `read_sparameters` takes the list of parameters; the calibration needs a **`calibration_begin`** because the SCPI VNAs choose the calibration type before the standards are measured.

### Notes on the SCPI entries

* The channel is always 1.
* Siglent reads each parameter directly with `:SENSe1:DATA:CORRdata? S<XY>` (real, imaginary pairs, ASCII) and the frequencies with `:SENSe1:FREQuency:DATA?`; the sweep is a single sweep (`:INITiate1:CONTinuous OFF`, `:INITiate1:IMMediate`, `*OPC?`). A THRU measurement uses the response port first (`:THRU <port2>,<port>`).
* R&S creates one trace per parameter (`CALCulate1:PARameter:SDEFine 'OLA<n>','S11'`), sweeps once inside `read_sparameters`, selects each trace and reads `CALCulate1:DATA? SDATa` (complex, corrected when the correction is on); the frequencies come from `CALCulate1:DATA:STIMulus?`. The calibration is named `OLA`; the load is the `MATCh` standard; a transmission calibration is `FTRans`, in which the lower port number is the source (so `port` must be lower than `port2`).
* Only the ASCII data format is used. Not verified on an instrument: that a trace that is not shown in a diagram can be read (R&S), and the behaviour of `CORRdata?` when the correction is off (Siglent).

### Open points

* The calibration tool of the application: the sequence of standards for each calibration kind, with the instructions for the operator.
* Software calibration assumes ideal standards (no offsets or fringing capacitance).
* **R&S ZVA/ZVB/ZVT/ZVL** (added): the same commands as the ZNB/ZNL (checked in the ZVA/ZVB/ZVT and ZVL manuals) with two differences: the transmission calibration type is `FRTRans` (both directions; the ZNB also has `FTRans`) and the power command has no port suffix (`SOURce1:POWer:LEVel:IMMediate:AMPLitude`). The manuals give no model table: the frequency range and the number of ports depend on the options and are not in the library (except the ZVL3).
* **Not used yet**: Agilent E506x/E507x user guides (no SCPI command reference: the Programmer's Guide PDF is needed), HP 8700 HP-IB quick reference (scanned image, no text), HP 8753C (HP-IB mnemonics, not SCPI), Agilent 871x (a different SCPI dialect with numbered standards: possible with its own series). Time-domain functions (TDR/DTF) are out of the first version.

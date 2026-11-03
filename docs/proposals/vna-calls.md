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

## 3. Decisions (owner)

1. **Calibration** is done by a *calibration tool* of the application: the user chooses "Calibrate VNA", the tool reads the VNA of the `.inst` file, runs the calibration calls of the model and tells the operator what to connect. For an instrument without calibration data over its interface (the LiteVNA) the **driver** performs the calibration in software, so that for the application the LiteVNA is **identical** to the other instruments.
2. **Complex data**: arrays of real and imaginary parts (`sparameters` type, see `schema/vna.json`).
3. **Sweep**: `run_sweep` then `read_sparameters`; `read_sparameters` starts a sweep by itself if none was started since the last `set_frequency_sweep`.
4. **VNAs the owner does not have** (LiteVNA and the SCPI models to come) are inserted in the library as **`experimental`** (hidden unless the user enables experimental instruments): they have never been tested on a real instrument. Anyone who owns one can verify it with `TESTING.md`.

Done so far: `schema/vna.json` (provisional), the LiteVNA 62/64/67 as `driver` models, and the driver with a simulated instrument in the application repository.

## 3b. Open points

* The calibration tool itself (application): the sequence of standards to connect for each calibration kind and for the SCPI VNAs.
* Calibration kits: the software calibration assumes ideal standards (no offsets or fringing capacitance).
* Time-domain functions (TDR/DTF): out of the first version.

## 4. Models to choose next (SCPI, "serious")

Candidates, to be checked against their programming manuals before anything is written:

* **Keysight ENA E5061B / E5063A**: very common, a complete public SCPI manual; the reference for the command names (`SENSe:FREQuency`, `CALCulate:PARameter`, `CALCulate:DATA:SDATa?`, `SENSe:CORRection:COLLect`).
* **Rohde & Schwarz ZNL3 / ZNB**: public manuals, clear command tree, same ideas with different names (so a good test of the translation layer).
* **Siglent SNA5000A**: the affordable one, SCPI close to Keysight's; likely the one a user of this software owns.

A text-protocol alternative for small VNAs is the NanoVNA family (a serial shell with `sweep`, `frequencies`, `data`); it can be a later addition.

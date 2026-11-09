# SCPI command name reference — instruments_lib.json

This document lists the **canonical call names** (`common_scpi_commands` and `scpi_commands` in `instruments_lib.json`) and what they refer to.

The software that uses this library must call the instruments through these names: **same operation = same name** (at least within the same category). The underlying SCPI syntax varies from manufacturer to manufacturer and is given per series.

## Naming conventions

- `snake_case` with a verb prefix: `set_*` (setting), `query_*` (state/configuration query), `read_*` (reading of a measurement), `enable_*` / `disable_*` (enabling/disabling protections), `clear_*`, `force_*`, `select_*`, `trigger_*`
- Parameters use `{placeholder}` templates (e.g. `{value}`, `{channel_number}`)
- Same name in different series = same logical operation, but the SCPI syntax can (and normally must) differ
- **Intentional** differences between categories: `set_voltage`/`set_current` (power supplies) vs `set_voltage_level`/`set_current_level` (loads), `output_on`/`output_off` (power supplies) vs `load_on`/`load_off` (loads)

## Series abbreviations

| Abbreviation | Series | Category |
|---|---|---|
| OWON ODP | OWON_ODP_Series | Power supplies |
| K. E36300 | Keysight_E36300_Series | Power supplies |
| TDK GEN | TDK_Lambda_GEN_Series | Power supplies |
| R&S HMP | Rohde_Schwarz_HMP_Series | Power supplies |
| HP E3631A | HP_E3631A_Series | Power supplies |
| K. 3497X | Keysight_3497X_Series | Dataloggers |
| K. DAQ97x | Keysight_DAQ97x_Series | Dataloggers |
| A. 3499A | Agilent_3499A_Series | Switch units (`switch_units_series`) |
| HP 3478A | HP_3478A_Series | Multimeters |
| A. 34401A | Agilent_34401A_Series | Multimeters |
| Tek MSO5 | Tektronix_5_Series_MSO | Oscilloscopes |
| Rigol DS1000Z | Rigol_DS1000Z_Series | Oscilloscopes |
| Sig. SDS HD | Siglent_SDS_HD_Series | Oscilloscopes |
| Chroma 6330A | Chroma_6330A_Series | Loads |
| K. EL4900 | Keysight_EL4900_Series | Loads |
| Sig. SDL1000X | Siglent_SDL1000X_E_Series | Loads |
| AD2 scope | Digilent_AnalogDiscovery_Scope_Series | Oscilloscopes |
| AD2 generator | Digilent_AnalogDiscovery_Series | Function generators (`function_generators_series`) |
| Rigol DG1000 | Rigol_DG1000_Series | Function generators |
| A. 33120A | Agilent_33120A_Series | Function generators |
| LiteVNA | Zenko_LiteVNA_Series | Network analyzers (`network_analyzers_series`) |
| Sig. SNA | Siglent_SNA_Series | Network analyzers |
| R&S ZN / ZV | Rohde_Schwarz_ZNx_Series, Rohde_Schwarz_ZVx_Series | Network analyzers |

## Common commands (IEEE-488.2 and status)

> **HP 3478A exception**: pre-IEEE-488.2 instrument — no `*RST`/`*IDN?`/`*CLS` commands. The corresponding functions use `CLEAR` (reset), `E` (errors, 2 octal digits), `K` (clear status), `SPOLL` (status byte), `GET` (trigger).

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `reset` | Instrument reset | `*RST` (all except HP 3478A, which uses `CLEAR`) | — |
| `clear_status` | Clear status registers | `*CLS` (all except HP 3478A, which uses `K`) | — |
| `identification_query` | Instrument identification | `*IDN?` (all except HP 3478A — it has no IDN) | string |
| `error_query` | Reads the error queue | `SYST:ERR?` (OWON, K. E36300, K. 3497X); `SYSTem:ERRor?` (TDK GEN, R&S HMP, A. 34401A, A. 3499A, Rigol, Sig. SDS HD); `EVMsg?` (Tek MSO5 — the SYSTem group does not exist); `E` (HP 3478A — 2 octal digits) | string |
| `self_test` | Self test | `*TST?` (all except Chroma, EL4900, HP 3478A) | int |
| `query_status_byte` | Status byte | `*STB?` (K. 3497X, Rigol, Chroma); `SPOLL` (HP 3478A) | int |
| `query_event_status_register` | Event status register | `*ESR?` (K. 3497X, Rigol, Chroma) | int |
| `enable_event_status_register` | Enables ESR bits | `*ESE {value}` (K. 3497X, Rigol, Chroma) | — |
| `query_event_status_enable` | Reads the ESE mask | `*ESE?` (K. 3497X, Rigol, Chroma) | int |
| `operation_complete_query` | Operation complete | `*OPC?` (Sig. SDS HD) | int |

## Power supplies (PSU)

### Voltage / current

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_voltage` | Sets the output voltage (selected channel) | `VOLT {value}` (OWON, K. E36300, TDK GEN, R&S HMP); `APPLy {output},{voltage}` (HP E3631A, output P6V/P25V/N25V) | — |
| `set_current` | Sets the current limit (selected channel) | `CURR {value}` (OWON, K. E36300, TDK GEN, R&S HMP); `APPLy {output},{voltage},{current}` (HP E3631A) | — |
| `read_voltage` | Measures the output voltage | `MEAS:VOLT?` (OWON, TDK GEN, R&S HMP); `MEAS:VOLT? CH{channel_number}` (K. E36300); `MEASure:VOLTage:DC?` (HP E3631A, selected channel) | float |
| `read_current` | Measures the output current | `MEAS:CURR?` (OWON, TDK GEN, R&S HMP); `MEAS:CURR? CH{channel_number}` (K. E36300); `MEASure:CURRent:DC?` (HP E3631A) | float |
| `read_power` | Measures the output power | `MEAS:POW?` (OWON) | float |
| `read_programmed_voltage` | Reads the programmed voltage | `VOLT?` (TDK GEN, R&S HMP); `APPLy? {output}` (HP E3631A) | float |
| `read_programmed_current` | Reads the programmed current | `CURR?` (TDK GEN, R&S HMP) | float |

### Output

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `output_on` | Turns the output on | `OUTP ON` (OWON, K. E36300, R&S HMP); `OUTPut:STATe ON` (TDK GEN); `OUTPut:STATe ON` (HP E3631A) | — |
| `output_off` | Turns the output off | `OUTP OFF` (OWON, K. E36300, R&S HMP); `OUTPut:STATe OFF` (TDK GEN); `OUTPut:STATe OFF` (HP E3631A) | — |
| `output_state_query` | Output state | `OUTP?` (OWON); `OUTPut?` (TDK GEN, R&S HMP, HP E3631A) | int (0/1) |

### Channels

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `select_channel` | Selects a channel by name | `INST:NSEL {channel_number}` (OWON); `INST:SEL CH{channel_number}` (K. E36300); `INST:SEL OUT{channel_number}` (R&S HMP); `INSTrument:SELect {output}` (HP E3631A: P6V, P25V, N25V) | — |
| `select_channel_numeric` | Selects a channel by number | `INST:NSEL {channel_number}` (K. E36300, query `INST:NSEL?`); `INSTrument:NSELect {channel_number}` (HP E3631A) | — |
| `query_selected_channel` | Selected channel | `INST:SEL?` (R&S HMP); `INSTrument:SELect?` (HP E3631A) | string |

### Other PSU functions

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `apply` | Sets voltage and current together | `APPL CH{channel_number}, {voltage}, {current}` (K. E36300, query `APPL? CH{channel_number}`); `APPLy {output},{voltage},{current}` (HP E3631A, query `APPLy? {output}`) | string |
| `set_local_remote` | Switches between local and remote | `SYSTem:SET {mode}` (TDK GEN, query `SYSTem:SET?`) | int |
| `set_ovp_level` | OVP threshold | `VOLT:PROTection:LEVel {value}` (TDK GEN, query `VOLT:PROTection:LEVel?`) | float |
| `query_ovp_tripped` | OVP trip state | `VOLT:PROTection:TRIPped?` (TDK GEN) | int |

## Electronic loads (EL)

### Input / mode

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `load_on` | Turns the load on | `LOAD ON` (Chroma); `INP\|OUTP ON` (K. EL4900); `INPut ON` (Sig. SDL1000X, query `INPut?`) | — |
| `load_off` | Turns the load off | `LOAD OFF` (Chroma); `INP\|OUTP OFF` (K. EL4900); `INPut OFF` (Sig. SDL1000X) | — |
| `query_input_state` | Input state | `LOAD?` (Chroma); `INP?` (K. EL4900) | int (0/1) |
| `set_mode` | Selects the operating mode | `MODE {mode}` (Chroma); `FUNC\|MODE {mode}` (K. EL4900: CURRent, VOLTage, POWer, RESistance, CVCC, CRCC, CVCR, AUTO); `FUNC {mode}` (Sig. SDL1000X: CURRent, VOLTage, POWer, RESistance, LED) | — |
| `query_mode` | Active mode | `MODE?` (Chroma) | string |
| `short` | Shorts the input | `INP\|OUTP:SHORt ON` (K. EL4900) | — |
| `open` | Opens the input | `INP\|OUTP:SHORt OFF` (K. EL4900) | — |
| `query_short_state` | Short state | `INP:SHORt?` (K. EL4900) | int (0/1) |

### Levels

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_current_level` | Current level | `CURR:STAT:L1 {value}` (Chroma, query `CURR:STAT:L1?`); `CURR {value}` (K. EL4900, Sig. SDL1000X) | float |
| `set_voltage_level` | Voltage level | `VOLT:L1 {value}` (Chroma, query `VOLT:L1?`); `VOLT {value}` (K. EL4900, Sig. SDL1000X) | float |
| `set_power_level` | Power level | `POW:STAT:L1 {value}` (Chroma, query `POW:STAT:L1?`); `POW {value}` (K. EL4900, Sig. SDL1000X) | float |
| `set_resistance_level` | Resistance level | `RES:L1 {value}` (Chroma, query `RES:L1?`); `RES {value}` (K. EL4900, Sig. SDL1000X) | float |

### Measurements

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `read_voltage` | Measures the input voltage | `MEAS:VOLT?` (Chroma, K. EL4900, Sig. SDL1000X) | float |
| `read_current` | Measures the input current | `MEAS:CURR?` (Chroma, K. EL4900, Sig. SDL1000X) | float |
| `read_power` | Measures the input power | `MEAS:POW?` (Chroma, K. EL4900, Sig. SDL1000X) | float |

### Slew rate

| Key | Description | SCPI syntax | Return type |
|---|---|---|---|
| `set_current_slew_rate` | Current slew rate (positive) | `CURR:SLEW {value}` (K. EL4900) | — |
| `set_current_slew_rate_neg` | Current slew rate (negative) | `CURR:SLEW:NEG {value}` (K. EL4900) | — |
| `set_voltage_slew_rate` | Voltage slew rate (positive) | `VOLT:SLEW {value}` (K. EL4900) | — |
| `set_voltage_slew_rate_neg` | Voltage slew rate (negative) | `VOLT:SLEW:NEG {value}` (K. EL4900) | — |

### Protections

| Key | Description | SCPI syntax | Return type |
|---|---|---|---|
| `enable_ovp` / `disable_ovp` | Enables/disables OVP | `VOLT:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_ovp_level` | OVP threshold | `VOLT:PROT {value}` (K. EL4900) | — |
| `enable_ocp` / `disable_ocp` | Enables/disables OCP | `CURR:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_ocp_level` | OCP threshold | `CURR:PROT {value}` (K. EL4900) | — |
| `enable_opp` / `disable_opp` | Enables/disables OPP | `POW:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_opp_level` | OPP threshold | `POW:PROT {value}` (K. EL4900) | — |
| `enable_ucp` / `disable_ucp` | Enables/disables UCP | `CURR:UND:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_ucp_level` | UCP threshold | `CURR:UND:PROT {value}` (K. EL4900) | — |
| `enable_uvp` / `disable_uvp` | Enables/disables UVP | `VOLT:UND:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_uvp_level` | UVP threshold | `VOLT:UND:PROT {value}` (K. EL4900) | — |
| `clear_protection_fault` | Clears the protection fault | `INP\|OUTP:PROTection:CLEar` (K. EL4900) | — |

### Channels / dynamic

| Key | Description | SCPI syntax | Return type |
|---|---|---|---|
| `select_channel` | Selects the channel/slot | `CHAN {channel_number}` (Chroma, query `CHAN?`) | int |
| `set_dynamic_level_high` | Dynamic high level | `CURR:DYN:L1 {value}` (Chroma, model) | — |
| `set_dynamic_level_low` | Dynamic low level | `CURR:DYN:L2 {value}` (Chroma, model) | — |

## Dataloggers (DL)

| Key | Description | SCPI syntax | Return type |
|---|---|---|---|
| `select_channels` | Selects the scan list | `ROUT:SCAN (@{channels})` (K. 3497X); `ROUTe:SCAN (@{channels})` (A. 3499A, `@snn` format) | — |
| `close_channel` | Closes one or more channels | `ROUT:CLOSe (@{channels})` (K. 3497X); `ROUTe:CLOSe (@{channels})` (A. 3499A) | — |
| `open_channels` | Opens the channels | `ROUT:OPEN (@{channels})` (K. 3497X); `ROUTe:OPEN (@{channels})` (A. 3499A) | — |
| `initiate_scan` | Starts the scan | `INITiate` (K. 3497X); `ROUTe:SCAN INITiate` (A. 3499A) | — |
| `read_scan` | Starts the scan and reads the measurements | `READ?` (K. 3497X — do not use with a BUS trigger, it causes a deadlock) | string |
| `fetch_readings` | Reads the measurements of the last scan | `FETCh?` (K. 3497X) | string |
| `set_trigger_source` | Trigger source | `TRIG:SOUR {source}` (K. 3497X: BUS, IMMediate, EXTernal, TIMer, ALARm1..4); `TRIGger:SOURce {source}` (A. 3499A: IMMediate, BUS, EXternal, TTLTrg0..2, STIMulus) | — |
| `set_trigger_count` | Number of triggers | `TRIG:COUN {count}` (K. 3497X). **Does NOT exist on the 3499A** (use `ARM:COUNt`) | — |
| `set_arm_count` | Number of arms of the 3499A | `ARM:COUNt {count}` (A. 3499A, only one: e.g. 1..99999, MAX, INFinity) | — |
| `trigger_bus` | Bus trigger | `*TRG` (K. 3497X, A. 3499A) | — |
| `configure_dc_voltage` | Configures a DCV measurement on the channels | `CONF:VOLT:DC {range},{resolution},(@{channels})` (K. 3497X) | — |
| `measure_dc_voltage` | Immediate DCV measurement | `MEAS:VOLT:DC? {range},{resolution},(@{channels})` (K. 3497X) | float |
| `set_voltage_range` | DCV measurement range | `SENS:VOLT:DC:RANG {range},(@{channels})` (K. 3497X) | — |

> **Note on the K. 3497X series** (models 34970A and 34972A): 172 commands checked against the dedicated manual (34970A/72A Command Reference): subsystems CALCulate (AVERage/LIMit/SCALe/COMPare), DATA (POINts?, REMove?, LAST?), DISPlay, FORMat:READing (ALARm/CHANnel/TIME/UNIT), OUTPut:ALARm*, ROUTe (CLOSe:EXCLusive, CHANnel:ADVance, MONitor), SOURce (34907A), UNIT:TEMPerature, TRIGger:TIMer. 3-digit channel format `(@101:120)`. `READ?` does not accept a scan list (34972A only).

> **Note on the 3499A**: switching/scanning mainframe **without a measurement engine** — no `MEASure?`/`FETCh?`/`READ?` commands; measurements are made on an external device.

## Multimeters (MTR)

### Function and range

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_function` | Selects the measurement function | `F{function}` (HP 3478A: F1=DC volts, F2=AC volts, F3=2-wire Ω, F4=4-wire Ω, F5=DC current, F6=AC current, F7=extended Ω); `FUNCtion "{function}"` (A. 34401A: DCV, ACV, DCI, ACI, RES, FRES, FREQ, PER, CONT, DIOD) | — |
| `query_function` | Current function | `FUNCtion?` (A. 34401A) | string |
| `set_range` | Measurement range (the smallest range that holds the value) | `R{range_code}` (HP 3478A: R-2 = 30 mV, R-1 = 0.3 V, R0 = 3 V, R1 = 30 V … R7 = 30 MΩ); `{function}:RANGe {range}` (A. 34401A, active function) | — |
| `set_auto_range` | Auto range | `RA` (HP 3478A; turning it off is done with `set_range`); `{function}:RANGe:AUTO {state}` (A. 34401A) | — |
| `set_resolution` | Resolution (A. 34401A) | `{function}:RESolution {resolution}` (A. 34401A) | — |
| `set_display_digits` | Digits displayed (HP 3478A only: it selects digits, not a resolution in measurement units) | `N{digits}` (HP 3478A: N3..N5 = 3½..5½ digits) | — |
| `set_measurement_rate` | Measurement rate | `{function}:NPLCycles {nplc}` (A. 34401A: 0.02..100) | — |

### Measurement

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `read_measurement` | Reads the measurement | no command on the HP 3478A: it talks when addressed (a `read` step, 13-byte ASCII); `READ?` (A. 34401A) | float |
| `measure_dc_voltage` | Immediate DCV measurement | `MEASure:VOLTage:DC? {range},{resolution}` (A. 34401A) | float |
| `measure_ac_voltage` | Immediate ACV measurement | `MEASure:VOLTage:AC? {range},{resolution}` (A. 34401A) | float |
| `measure_dc_current` | Immediate DCI measurement | `MEASure:CURRent:DC? {range},{resolution}` (A. 34401A) | float |
| `measure_ac_current` | Immediate ACI measurement | `MEASure:CURRent:AC? {range},{resolution}` (A. 34401A) | float |
| `measure_resistance` | Immediate Ω measurement | `MEASure:RESistance? {range},{resolution}` (A. 34401A) | float |
| `measure_resistance_4wire` | 4-wire Ω measurement | `MEASure:FRESistance? {range},{resolution}` (A. 34401A) | float |
| `measure_frequency` | Frequency measurement | `MEASure:FREQuency? {range},{resolution}` (A. 34401A) | float |
| `measure_period` | Period measurement | `MEASure:PERiod? {range},{resolution}` (A. 34401A) | float |
| `measure_continuity` | Continuity | `MEASure:CONTinuity?` (A. 34401A) | float |
| `measure_diode` | Diode test | `MEASure:DIODe?` (A. 34401A) | float |
| `fetch_readings` | Measurements from the last trigger | `FETCh?` (A. 34401A) | string |
| `query_reading_count` | Number of readings in memory | `DATA:POINts?` (A. 34401A) | int |

### Configuration and status

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_trigger_source` | Trigger source | `T{source}` (HP 3478A: T1 = internal, T2 = external, T4 = Group Execute Trigger, i.e. `BUS`); `TRIGger:SOURce {source}` (A. 34401A: BUS, IMMediate, EXTernal) | — |
| `trigger_bus` | Bus trigger | `*TRG` (A. 34401A). The HP 3478A's Group Execute Trigger is an HP-IB bus message, not a text command: not available yet | — |
| `set_autozero` | Autozero | `Z{autozero}` (HP 3478A: Z0=off, Z1=on); `SENSe:ZERO:AUTO {mode}` (A. 34401A) | — |
| `clear_status` | Clear status registers | `K` (HP 3478A); `*CLS` (A. 34401A) | — |
| `error_query` | Last error | `E` (HP 3478A — 2 octal digits); `SYSTem:ERRor?` (A. 34401A) | string |
| `query_status_byte` | Status byte | `*STB?` (A. 34401A). The HP 3478A's serial poll is an HP-IB bus message, not a text command: not available yet | int |
| `reset` | Instrument reset | `*RST` (A. 34401A). The HP 3478A's device clear is an HP-IB bus message, not a text command: not available yet | — |
| `set_math_function` | Math function | `CALCulate:FUNCtion {function}` (A. 34401A: NULL, DB, DBM, AVERage, LIMit — one at a time) | — |
| `set_sample_count` | Readings per trigger | `SAMPle:COUNt {count}` (A. 34401A) | — |
| `initiate_measurement` | Starts the triggered measurement | `INITiate` (A. 34401A) | — |
| `query_scpi_version` | SCPI version | `SYSTem:VERSion?` (A. 34401A) | string |

> **Note on the 3478A**: pre-IEEE-488.2 — classic HP command language, no `*IDN?`/`*RST`/SCPI. It is reached over HP-IB only. Its reset, Group Execute Trigger and serial poll are bus messages, which the library does not send yet. The 3478A manual in the repository is the service manual (scanned, no text).
>
> **Note on the 34401A**: the `measure_*` and `configure_*` calls take a number or `MIN`/`MAX`/`DEF` for range and resolution (default `DEF`), as in the manual.

## Oscilloscopes (OSC)

### Automatic setup

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `auto_setup` | Automatic setup | `AUTOSet EXECute` (Tek MSO5); `:AUToscale` (Rigol DS1000Z); `:AUToset` (Sig. SDS HD) | — |

### Channels

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_channel_coupling` | Channel coupling | `CH{channel_number}:COUPling {coupling_type}` (Tek: DC, AC, DCREJ); `:CHANnel{channel_number}:COUPling {coupling_type}` (Rigol, Sig.: AC, DC, GND) | — |
| `set_channel_scale` | Vertical scale | `CH{channel_number}:SCAle {value}` (Tek); `:CHANnel{channel_number}:SCALe {value}` (Rigol, Sig.) | — |
| `set_channel_offset` | Vertical offset | `CH{channel_number}:OFFSet {value}` (Tek); `:CHANnel{channel_number}:OFFSet {value}` (Rigol, Sig.) | — |
| `query_channel_scale` | Current vertical scale | `CH{channel_number}:SCAle?` (Tek); `:CHANnel{channel_number}:SCALe?` (Rigol, Sig.) | float |
| `query_channel_offset` | Current vertical offset | `CH{channel_number}:OFFSet?` (Tek); `:CHANnel{channel_number}:OFFSet?` (Rigol, Sig.) | float |

### Timebase

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_timebase_scale` | Horizontal scale | `HORizontal:MODE:SCAle {value}` (Tek); `:TIMebase:SCALe {value}` (Rigol, Sig.) | — |
| `query_timebase_scale` | Current horizontal scale | `HORizontal:MODE:SCAle?` (Tek); `:TIMebase:SCALe?` (Rigol, Sig.) | float |
| `set_timebase_delay` | Timebase delay | `:TIMebase:DELay {value}` (Sig. SDS HD) | — |
| `set_horizontal_mode` | Horizontal mode | `HORizontal:MODE {mode}` (Tek: AUTO, MANual) | — |

### Trigger

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_trigger_mode` | Trigger mode | `TRIGger:A:MODE {mode}` (Tek: AUTO, NORMal); `:TRIGger:MODE {mode}` (Rigol, Sig.) | — |
| `set_trigger_source` | Trigger source | `TRIGger:A:EDGE:SOUrce CH{channel_number}` (Tek); `:TRIGger:EDGE:SOURce CHAN{channel_number}` (Rigol); `:TRIGger:EDGE:SOURce C{channel_number}` (Sig.) | — |
| `set_trigger_slope` | Trigger slope | `TRIGger:A:EDGE:SLOpe {slope}` (Tek: RISe, FALL, EITher); `:TRIGger:EDGe:SLOPe {slope}` (Rigol: POSitive, NEGative, RFALl); `:TRIGger:EDGE:SLOPe {slope}` (Sig.: RISing, FALLing, ALTernate) | string (query) |
| `set_trigger_level` | Trigger level | `TRIGger:A:LEVel:CH{channel_number} {value}` (Tek); `:TRIGger:EDGE:LEVel {value}` (Rigol, Sig.) | — |
| `query_trigger_level` | Current trigger level | `TRIGger:A:LEVel:CH{channel_number}?` (Tek); `:TRIGger:EDGE:LEVel?` (Rigol, Sig.) | float |
| `set_trigger_type` | Trigger type | `TRIGger:A:TYPe {type}` (Tek: EDGE, WIDth, TIMEOut, RUNt, WINdow, LOGIc, SETHold, TRANsition, BUS) | — |
| `force_trigger` | Forces a trigger | `TRIGger FORCe` (Tek); `:TFORce` (Rigol) | — |
| `query_trigger_status` | Trigger/acquisition state | `:TRIGger:STATus?` (Rigol: TD, WAIT, RUN, AUTO, STOP) | string |

### Acquisition

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `run_acquisition` | Starts the acquisition | `ACQuire:STATE RUN` (Tek); `:RUN` (Rigol); `:TRIGger:RUN` (Sig.) | — |
| `stop_acquisition` | Stops the acquisition | `ACQuire:STATE STOP` (Tek); `:STOP` (Rigol); `:TRIGger:STOP` (Sig.) | — |
| `acquire_single` | Single-shot acquisition | `ACQuire:STATE RUN;*OPC` (Tek — requires `set_acquisition_stop_after SEQuence`); `:SINGle` (Rigol); `:TRIGger:MODE SINGle` (Sig.) | — |
| `set_acquisition_mode` | Sampling mode | `ACQuire:MODe {mode}` (Tek: SAMple, PEAKdetect, HIRes, AVErage, ENVelope) | — |
| `set_acquisition_stop_after` | Behaviour at the end of the sequence | `ACQuire:STOPAfter {mode}` (Tek: RUNSTop, SEQuence) | — |
| `set_acquisition_depth` | Memory depth | `:ACQuire:MDEPth {value}` (Rigol, query `:ACQuire:MDEPth?`); `:ACQuire:MDEPth {depth}` (Sig.) | int |

### Waveform

| Key | Description | SCPI syntax per series | Return type |
|---|---|---|---|
| `set_waveform_source` | Waveform data source | `DATa:SOUrce CH{channel_number}` (Tek, query `DATa:SOUrce?`); `:WAVeform:SOURce CHAN{channel_number}` (Rigol); `:WAVeform:SOURce C{channel_number}` (Sig.) | string |
| `set_waveform_format` | Waveform data format | `:WAVeform:FORMat {format_type}` (Rigol: ASCii, BYTE, WORD); `:WAVeform:WIDTh {format_type}` (Sig.: BYTE, WORD) | — |
| `query_waveform_preamble` | Waveform preamble | `WFMOutpre?` (Tek); `:WAVeform:PREamble?` (Rigol, Sig.) | string (CSV) |
| `query_waveform_data` | Waveform data | `CURVe?` (Tek — binary with a `#9` header); `:WAVeform:DATA?` (Rigol, Sig.) | string (binary/ASCII) |
| `query_waveform_all` | Preamble + data together | `WAVFrm?` (Tek) | string |

## Channel IDs (not standardized!)

Channels do not have uniform IDs: always check the series before using them.

| Manufacturer | Channel ID | Example |
|---|---|---|
| OWON | Numeric | `1`, `2`, `3` |
| Keysight (PSU) | `CH` + number | `CH1`, `CH2`, `CH3` |
| HP E3631A | Numeric + output identifier | `1`/`2`/`3`, selected with `INSTrument:SELect P6V|P25V|N25V` |
| Keysight (datalogger) | String range (slot + 3-digit channel) | `"101:120"` → `(@101:120)` |
| Agilent 3499A | `@snn` format (slot + 2-digit channel) | `"100:107"` → `(@100:107)` |
| HP/Agilent multimeters | Single channel (no channel parameter) | — |
| R&S | `OUT` + number | `OUT1`..`OUT4` |
| Tektronix | `CH` + number | `CH1`..`CH8` |
| Siglent | `C` + number | `C1`..`C4` |
| TDK-Lambda | `CH1` (single channel) | `CH1` |
| Digilent Analog Discovery 2 (scope and generator) | `CH1`, `CH2` (two inputs; two outputs W1 and W2 on the board) | `CH1` |
| Rigol DG1000 (generator) | `CH` + number | `CH1`, `CH2` |
| Agilent 33120A (generator) | single channel | `CH1` |

## Function generators (FGEN)

The logical calls and their SCPI syntax per series are in [COMMAND_NAMES.md](../COMMAND_NAMES.md), section 3.8 (generated from `schema/function_generator.json`). Points that are specific to the Analog Discovery 2:

- `set_amplitude` takes the **peak-to-peak** voltage. The driver sends half of it to the SDK (`PEAK_PER_VPP` = 0.5). Measured on an oscilloscope: 1 Vpp set gives 1.02 Vpp, 5 Vpp set gives 5.05 Vpp.
- The range of the amplitude (0.02 to 10 Vpp) and of the offset (±5 V) come from the device, not from the library: a value outside them is refused as `CALL-002`.
- `PULSE` and `ARBITRARY` waveforms are not handled; `set_waveform_shape` refuses them.
- `set_output_state` **without** `channel_number` starts all the channels that were given a setting through the driver with one start of the whole generator, so W1 and W2 start in phase (under 1° of spread over 10 starts; with one start per channel the spread was about 300°). With a `channel_number` only that channel changes. Without a channel and nothing configured, the first channel is used.

## Network analyzers (VNA)

The logical calls are in [COMMAND_NAMES.md](../COMMAND_NAMES.md), section 3.7, generated from `schema/vna.json`. No network analyzer has been tested on a real instrument yet.

## Notes

- Models with `"experimental": false` are supported. `DL_Agilent_34970A` was tested over RS-232. The Siglent `OSC_Siglent_SDS804X_HD`, `OSC_Siglent_SDS814X_HD` and `OSC_Siglent_SDS824X_HD` share one SCPI command set; the SDS824X HD was tested on hardware, the others were not tested individually. The Analog Discovery 2 models (`OSC_Digilent_AnalogDiscovery2`, `FGEN_Digilent_AnalogDiscovery2`) are supported for **the oscilloscope and the function generator only**: the logic analyzer is not supported yet, and the flag returns to `true` when a logic analyzer library is written and tested. Every other model has `"experimental": true`.
- The Analog Discovery 2 **scope**: the library reports the range of the device input. With a probe attenuation set (`set_probe_attenuation`) the scale limits are multiplied by it, and the upper limit is the range the device really gives (measured: 5.49 and 60.36 V at x1, 54.91 and 603.62 V at x10; a request is served by the first real range that is not smaller). A scale the device cannot give is refused, not rounded. The offset limit with a probe is not measured yet.
- The Siglent SDS HD **ignores the settings of a channel that is off**: enable the channel first (`set_channel_state`), then the probe and the scale.
- `query_waveform_data` with BYTE/WORD format returns binary data with a `#<n><len>` (TMC) header, not text.
- On Tektronix `error_query` uses `EVMsg?` because the `SYSTem` group does not exist.

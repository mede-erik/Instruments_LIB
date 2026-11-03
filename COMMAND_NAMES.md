# COMMAND_NAMES.md

Reference list of the **call names** (keys of `common_scpi_commands` / `scpi_commands`) that Open-Lab-Automation uses to reach the correct SCPI command on each instrument.

The software never builds SCPI strings by itself: it looks a call name up in `instruments_lib.json` and sends whatever syntax the library defines for that instrument. A call name therefore has to mean the same *action* on every instrument of a category, even if the SCPI syntax differs.

## 1. Rules

1. **Mandatory call**: the action is documented in **every** reference manual of the category. A series of that category must define it, otherwise the software cannot support the instrument.
2. **Non-mandatory (optional) call**: the action is documented in **at least one**, but not all, reference manuals of the category. A series defines it only if its own manual documents it.
3. **A command must be real.** A call is added to a series only when the command is documented in that series' manual (`documentation_path`). Nothing is added from memory or by analogy.
4. A call that is missing from the library must be treated by the software as "not supported by this instrument", never replaced by a guessed SCPI string.
5. Existing call names are not renamed. Where an older series uses a different name for the same action, it is listed under *Legacy names* in section 6.

### Naming convention

| Prefix | Meaning |
|---|---|
| `set_<x>` | write a setting (the `query` part of the same entry reads it back when the instrument supports it) |
| `query_<x>` | read a configuration or status value |
| `read_<x>` | read a measurement |
| `measure_<x>`, `configure_<x>` | one-shot measurement / function configuration (multimeters, dataloggers) |
| `enable_<x>`, `disable_<x>` | turn a feature on/off |
| `<x>_on`, `<x>_off` | switch an output/input on/off |

Channel, range and value placeholders use the names `channel_number`, `channels`, `value`.

## 2. Reference manuals used

| Category | Manuals read (`docs/`) | Status |
|---|---|---|
| Power supplies | OWON ODP, Keysight E36300, TDK-Lambda GEN (IEEE + LAN manual), R&S HMP, HP E3631A | complete |
| Electronic loads | Chroma 6330A, Keysight EL4900, Siglent SDL1000X | complete |
| Oscilloscopes | Tektronix 5 Series MSO, Rigol DS1000Z, Siglent SDS800X HD | complete |
| Multimeters | Agilent 34401A, HP 3478A | **provisional**: the 3478A PDF is a scanned image without text, and there are only two manuals |
| Dataloggers | Keysight 34970A/34972A, Keysight DAQ970A/DAQ973A | complete |
| Switch units | Agilent 3499A | **provisional**: only one manual |
| Vector network analyzers | Zenko LiteVNA 62/64/67 | **provisional, experimental**: one manual (binary USB protocol, software calibration); the SCPI VNAs will be added from their programming manuals. No VNA has been tested on a real instrument |

## 3. Calls per category

The tables of mandatory and optional calls are **generated from the machine-readable call schemas** in `schema/` (one file per category, see `schema/README.md`); the schema file is the source of truth. Regenerate this document with `python3 schema/generate_command_names.py` and verify the library against the schemas with `python3 Tests/check_conformance.py`.

Calls shared by every category: `identification_query` and `reset` are mandatory everywhere; `clear_status`, `error_query` and `self_test` are optional where a manual does not document them (see section 5).

<!-- BEGIN GENERATED power_supplies_series -->
### 3.1 Power supplies (`power_supplies_series`)

Generated from `schema/power_supply.json` — do not edit this section by hand. 11 mandatory and 71 optional calls.

Logical calls of programmable DC power supplies. channel_number is 1-based; the library selects the output (steps) or maps it to the instrument's own identifier.

Logical types:

* `bool`: true / false

**Mandatory**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `identification_query` | query |  | string | identification string (*IDN?) |
| `reset` | action |  |  | restore factory defaults |
| `set_voltage` | set | `channel_number` (int, 1.., optional)<br>`value` (float, V, 0..) |  | voltage setpoint of an output |
| `set_current` | set | `channel_number` (int, 1.., optional)<br>`value` (float, A, 0..) |  | current limit/setpoint of an output |
| `read_voltage` | query | `channel_number` (int, 1.., optional) | float, V | measured output voltage |
| `read_current` | query | `channel_number` (int, 1.., optional) | float, A | measured output current |
| `output_on` | action |  |  | enable the output(s) (all outputs of the instrument) |
| `output_off` | action |  |  | disable the output(s) (all outputs of the instrument) |
| `output_state_query` | query |  | bool | output state (true = on) |
| `set_remote` | action |  |  | enter remote mode |
| `set_local` | action |  |  | return to local mode |

**Optional**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `clear_status` | action |  |  | clear status registers |
| `error_query` | query |  | string | read and clear the oldest error |
| `self_test` | query |  | int | run self test, 0 = pass |
| `read_power` | query | `channel_number` (int, 1.., optional) | float, W | measured output power |
| `select_channel` | set | `channel_number` (int, 1..) |  | select the output addressed by the following commands (low level; set_voltage etc. already select it) |
| `select_channel_numeric` | set | `channel_number` (int, 1..) |  | select the output by number (low level) |
| `select_channel_named` | set | `channel_number` (int, 1..) |  | select the output by name (low level) |
| `apply` | set | `channel_number` (int, 1..)<br>`voltage` (float, V)<br>`current` (float, A) |  | select an output and set voltage and current together |
| `apply_voltage` | set | `values` (string) |  | set the voltage of all channels without changing the selected channel; values is a comma separated list "CH1[,CH2[,CH3]]" (series-specific) |
| `apply_current` | set | `values` (string) |  | set the current of all channels without changing the selected channel; values is a comma separated list "CH1[,CH2[,CH3]]" (series-specific) |
| `read_voltage_all` | query |  | string | read the voltage measured on the output terminals of all channels (series-specific) |
| `read_current_all` | query |  | string | read the current measured on the output terminals of all channels (series-specific) |
| `set_channel_outputs` | set | `states` (string) |  | enable/disable the output of each channel without changing the selected channel; states is "CH1,CH2,CH3" with 1/0 or ON/OFF (series-specific) |
| `set_track_mode` | set | `state` (string) |  | enable/disable track mode of CH1 and CH2 (triple output models only) (series-specific) |
| `set_series_mode` | set | `state` (string) |  | enable/disable series mode of CH1 and CH2 (triple output models only) (series-specific) |
| `set_parallel_mode` | set | `state` (string) |  | enable/disable parallel mode of CH1 and CH2 (triple output models only) (series-specific) |
| `set_ovp_level` | set | `value` (float) |  | overvoltage protection (OVP) value of the selected channel (series-specific) |
| `set_ocp_level` | set | `value` (float) |  | overcurrent protection (OCP) value of the selected channel (series-specific) |
| `set_ovp_level_all` | set | `values` (string) |  | OVP value of all channels; values is "CH1[,CH2[,CH3]]" (series-specific) |
| `set_ocp_level_all` | set | `values` (string) |  | OCP value of all channels; values is "CH1[,CH2[,CH3]]" (series-specific) |
| `enable_ocp` | set |  |  | enable overcurrent protection on the selected channel (series-specific) |
| `disable_ocp` | action |  |  | disable overcurrent protection on the selected channel (series-specific) |
| `query_ovp_tripped` | query |  | int | 1 if the overvoltage protection has tripped on the selected channel (series-specific) |
| `query_ocp_tripped` | query |  | int | 1 if the overcurrent protection has tripped on the selected channel (series-specific) |
| `clear_protection` | action |  |  | clear tripped protections (OVP/OCP/OTP) on all outputs (series-specific) |
| `save_state` | set | `location` (int) |  | store the instrument state in a memory location (0-9) (series-specific) |
| `recall_state` | set | `location` (int) |  | recall the instrument state from a memory location (0-9) (series-specific) |
| `read_programmed_voltage` | query |  | float | read programmed voltage (series-specific) |
| `read_programmed_current` | query |  | float | read programmed current (series-specific) |
| `set_local_remote` | set | `mode` (int) |  | set local remote (series-specific) |
| `set_remote_lock` | action |  |  | remote mode with front panel local button disabled (local lockout) (series-specific) |
| `query_selected_channel` | query |  | string | query selected channel (series-specific) |
| `set_triggered_voltage` | set | `value` (float) |  | program pending triggered voltage level, transferred to output on trigger (series-specific) |
| `set_triggered_current` | set | `value` (float) |  | program pending triggered current level, transferred to output on trigger (series-specific) |
| `set_coupling` | set | `output_list` (string) |  | couple triggered levels between logical outputs (list of output identifiers) (series-specific) |
| `initiate_trigger` | action |  |  | initiate the trigger system (transfers triggered levels) (series-specific) |
| `set_trigger_source` | set | `source` (string) |  | select trigger source (default BUS at *RST) (series-specific) |
| `set_trigger_delay` | set | `seconds` (float) |  | delay between trigger detection and output change, 0..3600 s (bus trigger source only) (series-specific) |
| `trigger_bus` | action |  |  | generate a bus trigger (IEEE-488 GET); over RS-232 requires SYSTem:REMote (series-specific) |
| `operation_complete` | action |  |  | set Operation Complete bit (bit 0) of Standard Event register when pending operations complete (series-specific) |
| `operation_complete_query` | query |  | int | returns '1' when pending operations complete (series-specific) |
| `wait_to_complete` | action |  |  | wait for all pending operations to complete before executing further commands (series-specific) |
| `query_status_byte` | query |  | int | query Status Byte summary register (bit 3=QUES, 4=MAV, 5=ESB, 6=RQS) (series-specific) |
| `query_event_status_register` | query |  | int | query Standard Event register (bit 0=OPC, 2=QYE, 3=DDE, 4=EXE, 5=CME, 7=PON) (series-specific) |
| `enable_event_status_register` | set | `value` (int) |  | enable bits in the Standard Event enable register (series-specific) |
| `query_event_status_enable` | query |  | int | query Standard Event enable register (series-specific) |
| `set_service_request_enable` | set | `value` (int) |  | enable bits in the Status Byte enable register for SRQ generation (series-specific) |
| `query_service_request_enable` | query |  | int | query Status Byte enable register (series-specific) |
| `set_power_on_status_clear` | set | `state` (int) |  | power-on status clear: 1 clears enable masks at power-on, 0 preserves them (series-specific) |
| `set_display_state` | set | `state` (string) |  | turn front-panel display off or on (series-specific) |
| `display_text` | set | `text` (string) |  | display a message on the front panel (up to 12 characters) (series-specific) |
| `clear_display_text` | action |  |  | clear the message displayed on the front panel (series-specific) |
| `beep` | action |  |  | issue a single beep immediately (series-specific) |
| `query_scpi_version` | query |  | string | query SCPI language version, returns string YYYY.V (series-specific) |
| `set_local_mode` | action |  |  | return to local mode over RS-232 (GPIB uses GTL/Local key instead) (series-specific) |
| `set_remote_mode` | action |  |  | place in remote mode over RS-232 (must be sent before RS-232 programming) (series-specific) |
| `query_questionable_status` | query |  | int | query Questionable Status event register (bit 4=FAN, bit 13=ISUM); also clears it (series-specific) |
| `enable_questionable_status` | set | `value` (int) |  | enable bits in Questionable Status enable register (series-specific) |
| `query_questionable_instrument_status` | query |  | int | query Questionable Instrument event register (bit 1=+6V, bit 2=+25V, bit 3=-25V overload) (series-specific) |
| `enable_questionable_instrument_status` | set | `value` (int) |  | set Questionable Instrument enable register (series-specific) |
| `query_instrument_summary` | query | `channel_number` (int) | int | query Questionable Instrument ISUM event register for one output (bit 0=voltage unregulated, bit 1=current unregulated) (series-specific) |
| `query_instrument_summary_condition` | query | `channel_number` (int) | int | query CV/CC operating condition of one output: 0=off/unregulated, 1=CC, 2=CV, 3=hardware failure (series-specific) |
| `enable_instrument_summary` | set | `channel_number` (int)<br>`value` (int) |  | set Questionable Instrument ISUM enable register for one output (series-specific) |
| `calibration_count_query` | query |  | int | query number of times the unit has been calibrated (series-specific) |
| `calibration_secure_state` | set | `state` (string)<br>`code` (string) |  | secure/unsecure calibration (requires the security code) (series-specific) |
| `calibration_secure_code` | set | `code` (string) |  | change the calibration security code (series-specific) |
| `calibration_string` | set | `text` (string) |  | store/query calibration message (up to 40 characters) (series-specific) |
| `calibration_voltage_data` | set | `value` (float) |  | enter voltage value read from external meter for calibration (requires unsecured state) (series-specific) |
| `calibration_voltage_level` | set | `level` (string) |  | select voltage calibration point (MIN must be entered first, then MAX) (series-specific) |
| `calibration_current_data` | set | `value` (float) |  | enter current value read from external meter for calibration (requires unsecured state) (series-specific) |
| `calibration_current_level` | set | `level` (string) |  | select current calibration point (MIN must be entered first, then MAX) (series-specific) |

<!-- END GENERATED power_supplies_series -->

<!-- BEGIN GENERATED electronic_loads_series -->
### 3.2 Electronic loads (`electronic_loads_series`)

Generated from `schema/electronic_load.json` — do not edit this section by hand. 17 mandatory and 38 optional calls.

Logical calls of programmable DC electronic loads (single input).

Logical types:

* `bool`: true / false
* `load_mode`: `CC`, `CV`, `CR`, `CP`

**Mandatory**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `identification_query` | query |  | string | identification string (*IDN?) |
| `reset` | action |  |  | restore factory defaults |
| `clear_status` | action |  |  | clear status registers |
| `load_on` | action |  |  | enable the load input |
| `load_off` | action |  |  | disable the load input |
| `query_input_state` | query |  | bool | input state (true = on) |
| `set_mode` | set | `mode` (load_mode) |  | operating mode: constant current/voltage/resistance/power |
| `query_mode` | query |  | load_mode | operating mode |
| `set_current_level` | set | `value` (float, A, 0..) |  | constant-current level |
| `set_voltage_level` | set | `value` (float, V, 0..) |  | constant-voltage level |
| `set_resistance_level` | set | `value` (float, Ohm, 0..) |  | constant-resistance level |
| `set_power_level` | set | `value` (float, W, 0..) |  | constant-power level |
| `read_voltage` | query |  | float, V | measured input voltage |
| `read_current` | query |  | float, A | measured input current |
| `read_power` | query |  | float, W | measured input power |
| `set_current_slew_rate_rise` | set | `value` (float, A/us, 0..) |  | current slew rate, rising edge |
| `set_current_slew_rate_fall` | set | `value` (float, A/us, 0..) |  | current slew rate, falling edge |

**Optional**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `error_query` | query |  | string | read and clear the oldest error |
| `self_test` | query |  | int | run self test, 0 = pass |
| `set_dynamic_level_high` | set | `value` (float, A, 0..) |  | dynamic mode: high current level |
| `set_dynamic_level_low` | set | `value` (float, A, 0..) |  | dynamic mode: low current level |
| `set_dynamic_timing` | set | `frequency` (float, Hz, 0..)<br>`duty` (float, %, 0..100, default 50) |  | dynamic mode: repetition frequency and duty cycle (the library computes the instrument's own timing parameters) |
| `enable_dynamic_mode` | action |  |  | switch to the constant-current dynamic mode |
| `disable_dynamic_mode` | action |  |  | return to the static constant-current mode |
| `query_status_byte` | query |  | int | query status byte (series-specific) |
| `query_event_status_register` | query |  | int | query event status register (series-specific) |
| `enable_event_status_register` | set | `value` (int) |  | enable event status register (series-specific) |
| `query_event_status_enable` | query |  | int | query event status enable (series-specific) |
| `select_channel` | set | `channel_number` (int) |  | select channel (series-specific) |
| `enable_ovp` | action |  |  | enable ovp (series-specific) |
| `disable_ovp` | action |  |  | disable ovp (series-specific) |
| `set_ovp_level` | set | `value` (float) |  | set ovp level (series-specific) |
| `enable_ocp` | action |  |  | enable ocp (series-specific) |
| `set_ocp_level` | set | `value` (float) |  | set ocp level (series-specific) |
| `enable_opp` | action |  |  | enable opp (series-specific) |
| `set_opp_level` | set | `value` (float) |  | set opp level (series-specific) |
| `set_voltage_slew_rate` | set | `value` (float) |  | set voltage slew rate (series-specific) |
| `set_voltage_slew_rate_neg` | set | `value` (float) |  | set voltage slew rate neg (series-specific) |
| `set_current_slew_rate` | set | `value` (float) |  | set current slew rate (series-specific) |
| `set_current_slew_rate_neg` | set | `value` (float) |  | set current slew rate neg (series-specific) |
| `short` | action |  |  | short (series-specific) |
| `open` | action |  |  | open (series-specific) |
| `enable_ucp` | action |  |  | enable ucp (series-specific) |
| `set_ucp_level` | set | `value` (float) |  | set ucp level (series-specific) |
| `set_uvp_level` | set | `value` (float) |  | set uvp level (series-specific) |
| `enable_uvp` | action |  |  | enable uvp (series-specific) |
| `clear_protection_fault` | action |  |  | clear protection fault (series-specific) |
| `disable_ocp` | action |  |  | disable ocp (series-specific) |
| `disable_opp` | action |  |  | disable opp (series-specific) |
| `disable_ucp` | action |  |  | disable ucp (series-specific) |
| `disable_uvp` | action |  |  | disable uvp (series-specific) |
| `query_short_state` | query |  | int | query short state (series-specific) |
| `set_dynamic_mode_type` | set | `mode_type` (string) |  | transient operating mode of the constant-current function (series-specific) |
| `set_dynamic_width_high` | set | `value` (float) |  | transient level A width (s) (series-specific) |
| `set_dynamic_width_low` | set | `value` (float) |  | transient level B width (s) (series-specific) |

<!-- END GENERATED electronic_loads_series -->

<!-- BEGIN GENERATED oscilloscopes_series -->
### 3.3 Oscilloscopes (`oscilloscopes_series`)

Generated from `schema/oscilloscope.json` — do not edit this section by hand. 29 mandatory and 34 optional calls.

Logical calls every oscilloscope must implement (mandatory) or may implement (optional). Argument names and logical types are the same for all instruments.

Logical types:

* `bool`: true / false
* `coupling`: `DC`, `AC`, `GND`
* `slope`: `RISE`, `FALL`, `EITHER` (accepted aliases: `RISING`→`RISE`, `FALLING`→`FALL`, `BOTH`→`EITHER`, `ALTERNATE`→`EITHER`, `RIS`→`RISE`)
* `trigger_mode`: `AUTO`, `NORMAL`, `SINGLE` (accepted aliases: `NORM`→`NORMAL`, `SING`→`SINGLE`)
* `trigger_mode_state`: `AUTO`, `NORMAL`, `SINGLE`, `FORCED`
* `waveform`: dict with arrays "time" (s) and "voltage" (V) and the acquisition values: points, sample_interval, vertical_gain, vertical_offset, trigger_delay, timebase
* `trigger_status`: `ARMED`, `READY`, `AUTO`, `TRIGGERED`, `STOPPED`
* `acquisition_type`: `NORMAL`, `AVERAGE`, `PEAK`, `HIRES`
* `waveform_format`: `BYTE`, `WORD`, `ASCII`

**Mandatory**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `identification_query` | query |  | string | identification string (*IDN?) |
| `reset` | action |  |  | restore factory defaults |
| `operation_complete_query` | query |  | int | 1 when all pending operations are complete |
| `auto_setup` | action |  |  | automatic setup of the instrument |
| `run_acquisition` | action |  |  | start continuous acquisition |
| `stop_acquisition` | action |  |  | stop acquisition |
| `acquire_single` | action |  |  | arm a single acquisition |
| `force_trigger` | action |  |  | force one triggered acquisition |
| `set_timebase_scale` | set | `value` (float, s/div) |  | horizontal scale |
| `set_timebase_delay` | set | `value` (float, s) |  | horizontal delay/offset (trigger point position) |
| `set_channel_state` | set | `channel_number` (int, 1..)<br>`state` (bool) |  | show/hide a channel |
| `set_channel_scale` | set | `channel_number` (int, 1..)<br>`value` (float, V/div) |  | vertical scale |
| `set_channel_offset` | set | `channel_number` (int, 1..)<br>`value` (float, V) |  | vertical offset |
| `set_channel_coupling` | set | `channel_number` (int, 1..)<br>`coupling_type` (coupling) |  | input coupling |
| `set_channel_bandwidth_limit` | set | `channel_number` (int, 1..)<br>`bandwidth` (float, Hz, 0..) |  | channel bandwidth limit; 0 = no limit (full bandwidth) |
| `set_probe_attenuation` | set | `channel_number` (int, 1..)<br>`value` (float, ratio) |  | probe attenuation ratio (10 = 10:1) |
| `set_trigger_source` | set | `channel_number` (int, 1..) |  | edge trigger source |
| `set_trigger_level` | set | `value` (float, V)<br>`channel_number` (int, 1.., optional) |  | edge trigger level; some instruments set it per channel, then channel_number is the trigger source channel |
| `set_trigger_slope` | set | `slope` (slope) |  | edge trigger slope |
| `set_trigger_mode` | set | `mode` (trigger_mode) |  | trigger sweep mode |
| `set_trigger_holdoff` | set | `value` (float, s) |  | trigger holdoff time |
| `query_trigger_status` | query |  | trigger_status | state of the triggering system |
| `set_acquisition_type` | set | `acquisition_type` (acquisition_type) |  | acquisition type |
| `set_acquisition_depth` | set | `depth` (int, points, 1..) |  | memory depth in points |
| `query_sample_rate` | query |  | float, Sa/s | current sample rate |
| `set_waveform_source` | set | `channel_number` (int, 1..) |  | source of the waveform transfer |
| `set_waveform_format` | set | `format_type` (waveform_format) |  | format of the transferred waveform data |
| `query_waveform_preamble` | query |  | raw | scaling/descriptor of the waveform to transfer (model dependent: text for Tektronix and Rigol, a binary descriptor for Siglent) |
| `query_waveform_data` | query |  | binary | waveform data of the selected source |

**Optional**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `clear_status` | action |  |  | clear status registers |
| `error_query` | query |  | string | read and clear the oldest error |
| `self_test` | query |  | int | run self test, 0 = pass |
| `query_timebase_scale` | query |  | float, s/div | horizontal scale |
| `query_timebase_delay` | query |  | float, s | horizontal delay/offset |
| `query_channel_scale` | query | `channel_number` (int, 1..) | float, V/div | vertical scale |
| `query_channel_offset` | query | `channel_number` (int, 1..) | float, V | vertical offset |
| `query_channel_coupling` | query | `channel_number` (int, 1..) | coupling | input coupling |
| `set_channel_invert` | set | `channel_number` (int, 1..)<br>`state` (bool) |  | invert a channel |
| `set_channel_impedance` | set | `channel_number` (int, 1..)<br>`impedance` (string) |  | input impedance |
| `set_channel_unit` | set | `channel_number` (int, 1..)<br>`unit` (string) |  | channel unit |
| `query_trigger_source` | query |  | string | edge trigger source |
| `query_trigger_level` | query | `channel_number` (int, 1.., optional) | float, V | edge trigger level |
| `query_trigger_mode` | query |  | trigger_mode_state | trigger sweep mode |
| `set_trigger_type` | set | `trigger_type` (string) |  | trigger type |
| `set_trigger_coupling` | set | `coupling_type` (string) |  | trigger coupling |
| `read_waveform` | query | `channel_number` (int, 1..)<br>`bits` (int, 8..16, default 8, optional)<br>`start` (int, points, 0.., default 0, optional)<br>`points` (int, points, 0.., default 0, optional) | waveform | read a channel waveform as time and voltage arrays (needs a parser for the model) |
| `set_waveform_start` | set | `value` (int, points, 0..) |  | first point to transfer |
| `set_waveform_points` | set | `value` (int, points, 1..) |  | number of points to transfer |
| `set_waveform_interval` | set | `value` (int, points, 1..) |  | interval between transferred points |
| `query_waveform_max_points` | query |  | int, points | maximum number of points that can be transferred |
| `set_waveform_byte_order` | set | `order` (string) |  | byte order of transferred data |
| `query_status_byte` | query |  | int | status byte (*STB?) |
| `query_event_status_register` | query |  | int | standard event status register (*ESR?) |
| `enable_event_status_register` | set | `value` (int, 0..255) |  | standard event status enable mask (*ESE) |
| `query_event_status_enable` | query |  | int | standard event status enable mask (*ESE?) |
| `set_acquisition_stop_after` | set | `mode` (string) |  | acquisition end: keep running or stop after one sequence (model dependent, Tektronix) |
| `set_acquisition_mode` | set | `mode` (string) |  | legacy name of set_acquisition_type (Tektronix); use set_acquisition_type |
| `set_horizontal_mode` | set | `mode` (string) |  | horizontal mode (model dependent, Tektronix) |
| `query_waveform_all` | query |  | binary | preamble and data in one answer (model dependent, Tektronix) |
| `set_measurement_item` | set | `item` (string)<br>`state` (bool) |  | add/remove a built-in measurement |
| `set_measurement_source` | set | `channel_number` (int, 1..) |  | source of the built-in measurements |
| `query_measurement_value` | query | `item` (string) | float | value of a built-in measurement |
| `set_remote` | set | `state` (bool) |  | remote lock of the front panel |

<!-- END GENERATED oscilloscopes_series -->

### 3.4 Multimeters (`multimeters_series`) — provisional

Based on the two manuals available. The 3478A manual is scanned, so its coverage was taken from the existing library entries. **Needs more manuals before it is final.**

**Mandatory (provisional)**: `reset`, `set_function`, `set_range`, `set_resolution`, `set_autozero`, `set_trigger_source`, `trigger_bus`, `read_measurement`.

**Optional**: `identification_query` (not on the 3478A), `clear_status`, `error_query`, `query_status_byte`, `measure_*`, `configure_*`, `fetch_readings`, `set_auto_range`, `set_trigger_count`, `set_trigger_delay`, `set_sample_count`, `set_math_*`, `set_limit_*`, `set_nulls`, display commands.

<!-- BEGIN GENERATED dataloggers_series -->
### 3.5 Dataloggers (`dataloggers_series`)

Generated from `schema/datalogger.json` — do not edit this section by hand. 57 mandatory and 119 optional calls.

Logical calls of data acquisition / datalogger mainframes (Keysight 34970A/34972A and DAQ970A/DAQ973A). Channels use the 3-digit form of the instrument, e.g. "101:120". Optional calls are generated from the library.

Logical types:

* `float_list`: list of numbers (readings of the scan list, in scan order)

**Mandatory**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `reset` | action |  |  | Factory reset: abort scan, clear scan list, restore all measurement parameters to factory settings |
| `clear_status` | action |  |  | Clear event registers, error queue and alarm queue (does not clear enable registers) |
| `identification_query` | query |  | string | Identification query (HEWLETT-PACKARD,34970A,0,XX-Y-Z on the 34970A) |
| `self_test` | query |  | string | run the instrument self test (takes several seconds, may reset the instrument); 0 = pass |
| `operation_complete_query` | query |  | int | Operation complete query, returns 1 when the current operation completes |
| `trigger_bus` | action |  |  | Software (bus) trigger, used with TRIGger:SOURce BUS |
| `save_state` | set | `location` (int) |  | Save the present instrument state to the specified location |
| `recall_state` | set | `location` (int) |  | Recall the instrument state stored at the specified location |
| `abort` | action |  |  | Abort a measurement in progress from a scan (readings remain in memory) |
| `initiate_scan` | action |  |  | Change the triggering system from idle to wait-for-trigger state; readings are stored in memory |
| `fetch_readings` | query |  | float_list | Transfer readings from memory to the output buffer (list of readings) |
| `read_scan` | query |  | float_list | Place the instrument in the wait-for-trigger state, scan the present scan list once and send readings to the output buffer (list of readings) |
| `read_and_remove` | query | `max_count` (int) | float_list | Read and erase up to <max_count> readings from memory, starting with the oldest (list of readings) |
| `preset` | action |  |  | Instrument preset to a known configuration (aborts measurement, does not clear scan list) |
| `query_card_type` | query | `slot` (int) | string | identity of the module in a slot (slot = 1, 2 or 3; the 34970A addresses slots as 100, 200, 300) |
| `set_local` | action |  |  | Place the instrument in local mode (front panel fully functional; not allowed over GPIB on the 34970A) |
| `set_remote` | action |  |  | Place the instrument in remote mode (most front panel keys disabled) |
| `select_channels` | set | `channels` (string) |  | Select the channels to be included in the scan list (channels are 4-digit channel numbers in the (@ch_list) form, e.g. (@101:120); use ROUT:SCAN (@) to clear) |
| `query_scan_size` | query |  | int | Return the number of channels in the scan list |
| `close_channel` | set | `channels` (string) |  | Close the specified channels on a multiplexer or switch module |
| `close_channel_exclusive` | set | `channels` (string) |  | Open all channels on the module, then close the specified channels (one at a time) |
| `open_channels` | set | `channels` (string) |  | Open the specified channels on a multiplexer or switch module |
| `set_channel_advance_source` | set | `source` (string) |  | Select the channel advance source for external scanning (internal DMM disabled), {EXTernal\|BUS\|IMMediate} |
| `set_channel_delay` | set | `seconds` (float)<br>`channels` (string) |  | Add a delay (0 to 60 s, 1 ms resolution) between multiplexer channels in the scan list |
| `query_relay_done` | query |  | int | Return 1 when all relay operations on cards not involved in the scan are finished |
| `monitor_channel` | set | `channel` (string) |  | Select the channel to be displayed on the front panel (single channel, e.g. (@103)) |
| `query_monitor_data` | query |  | float_list | reading of the monitored channel (empty list when the monitor is off) |
| `set_monitor_state` | set | `mode` (string) |  | Enable/disable the Monitor mode (continuous measurements on a single channel) |
| `set_trigger_source` | set | `source` (string) |  | Select the trigger source for each sweep through the scan list |
| `set_trigger_count` | set | `count` (string) |  | Specify the number of times to sweep through the scan list |
| `set_trigger_timer` | set | `seconds` (number_or_keyword, or MIN/MAX)<br>`minmax` (string) |  | Set the trigger-to-trigger interval (0 to 359,999 s, 1 ms resolution) for the TIMer trigger source |
| `configure_dc_voltage` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels for DC voltage measurements (does not initiate the scan) |
| `configure_ac_voltage` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels for AC voltage measurements (resolution fixed at 6 1/2 digits) |
| `configure_dc_current` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels (34901A/34902A ch 21/22 only) for DC current measurements |
| `configure_ac_current` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels (34901A/34902A ch 21/22 only) for AC current measurements |
| `configure_resistance` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels for 2-wire resistance measurements |
| `configure_fresistance` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels for 4-wire resistance measurements (channels auto-paired with Bank 2) |
| `configure_frequency` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels for frequency measurements |
| `configure_period` | set | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels for period measurements |
| `configure_temperature` | set | `probe_type` (string)<br>`type` (string)<br>`resolution` (number_or_keyword, or MIN/MAX/DEF)<br>`channels` (string) |  | Configure the specified channels for temperature measurements |
| `configure_totalize` | set | `mode` (string)<br>`channels` (string) |  | Configure the specified totalizer channels on the multifunction module (34907A) |
| `measure_dc_voltage` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure DC voltage (equivalent to CONFigure:VOLTage:DC followed by READ?) |
| `measure_ac_voltage` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure AC voltage |
| `measure_dc_current` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure DC current (34901A/34902A ch 21/22 only) |
| `measure_ac_current` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure AC current (34901A/34902A ch 21/22 only) |
| `measure_resistance` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure 2-wire resistance |
| `measure_fresistance` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure 4-wire resistance |
| `measure_frequency` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure frequency |
| `measure_period` | query | `range` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`resolution` (number_or_keyword, or AUTO/MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure period |
| `measure_temperature` | query | `probe_type` (string)<br>`type` (string)<br>`resolution` (number_or_keyword, or MIN/MAX/DEF)<br>`channels` (string) | float | Configure and measure temperature |
| `query_data_points` | query |  | int | Return the total number of readings currently stored in reading memory |
| `query_last_reading` | query | `num_rdgs` (int)<br>`channel` (string) | string | Return the most recent reading(s) taken on the specified channel during the scan |
| `display_text` | set | `quoted_string` (string) |  | Display a text message (up to 12 characters) on the front panel |
| `clear_display_text` | action |  |  | Clear the text message on the front-panel display |
| `set_temperature_unit` | set | `units` (string)<br>`channels` (string) |  | Select the temperature units (Celsius, Fahrenheit, Kelvin) on the specified channels |
| `set_function` | set | `function` (string)<br>`channels` (string) |  | Select the measurement function on the specified channels (function name in quotes, e.g. FUNC "VOLT:DC") |
| `error_query` | query |  | string | read and clear one error from the error queue (up to 20 errors, FIFO) |

**Optional**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `query_status_byte` | query |  | int | Read the Status Byte Register |
| `query_event_status_register` | query |  | int | Read and clear the Standard Event Status Register |
| `enable_event_status_register` | set | `value` (int) |  | Enable bits in the Standard Event Status Register enable register |
| `query_event_status_enable` | query |  | int | Read the Standard Event Status Register enable register |
| `enable_service_request_enable` | set | `value` (int) |  | Enable bits in the Service Request Enable register |
| `query_service_request_enable` | query |  | int | Read the Service Request Enable register |
| `set_operation_complete` | action |  |  | Set Operation Complete bit (bit 0) in the Standard Event Register at the end of the current scan |
| `wait_to_continue` | action |  |  | Wait-to-continue: prevent further commands until all pending operations complete |
| `set_power_on_status_clear` | set | `state` (string) |  | Power-on status clear: enable/disable clearing of enable registers at power-on |
| `input_impedance_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable automatic input resistance (>10 GOhm on 100 mV, 1 V, 10 V ranges) for DC voltage measurements |
| `card_power_on` | set | `slot` (string) |  | Reset the module in the specified slot to its power-on state |
| `set_date` | set | `year` (int)<br>`month` (int)<br>`day` (int) |  | Set/query the instrument calendar (readings and alarms are stored with date) |
| `set_time` | set | `hour` (int)<br>`minute` (int)<br>`second` (float) |  | Set/query the instrument time-of-day clock |
| `query_scan_start_time` | query |  | string | Return the time and date at the start of the most recent scan (yyyy,mm,dd,hh,mm,ss.sss) |
| `set_interface` | set | `interface` (string) |  | Select the remote interface (34970A only: GPIB or RS-232; only one interface enabled at a time) |
| `query_line_frequency` | query |  | int | Return the power-line reference frequency used for NPLC integration (50 or 60) |
| `query_scpi_version` | query |  | string | Return the version of the SCPI standard with which the instrument complies (1994.0) |
| `query_alarm` | query |  | string | Read one alarm event from the alarm queue (read and delete, FIFO, up to 20 alarms) |
| `set_remote_lock` | action |  |  | Local lockout mode (all front panel keys disabled) |
| `instrument_dmm` | set | `state` (string) |  | Disable/enable the internal DMM (changing state issues a Factory Reset) |
| `query_dmm_installed` | query |  | int | Return 1 if the internal DMM is installed |
| `set_channel_delay_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable automatic channel delay on the specified channels |
| `set_four_wire` | set | `state` (string)<br>`channels` (string) |  | Configure the specified channels for 4-wire external scanning without the internal DMM (34901A/34902A only) |
| `configure_digital_byte` | set | `channels` (string) |  | Configure the instrument to scan the specified digital input channels (34907A) as byte data |
| `query_configuration` | query | `channels` (string) | string | Return the present function, range and resolution configuration on the specified channels |
| `measure_totalize` | query | `mode` (string)<br>`channels` (string) | float | Configure and measure totalizer count (34907A) |
| `measure_digital_byte` | query | `channels` (string) | int | Configure and measure digital input byte data (34907A) |
| `remove_readings` | query | `num_rdgs` (int) | string | Read and erase the specified number of readings from memory, starting with the oldest |
| `set_memory_threshold` | set | `num_rdgs` (int) |  | Set the number of readings that sets the Memory Threshold bit (bit 9) in the Standard Operation event register |
| `set_display` | set | `state` (string) |  | Disable/enable the front-panel display |
| `format_reading_alarm` | set | `state` (string) |  | Enable/disable the inclusion of alarm status information with retrieved readings |
| `format_reading_channel` | set | `mode` (string) |  | Enable/disable the inclusion of channel number information with retrieved readings |
| `format_reading_time` | set | `mode` (string) |  | Enable/disable the inclusion of a time stamp with retrieved readings |
| `format_reading_time_type` | set | `format` (string) |  | Select the time format for time stamps: absolute (time of day with date) or relative (seconds since start of scan) |
| `format_reading_unit` | set | `mode` (string) |  | Enable/disable the inclusion of measurement units (VDC, OHM, etc.) with retrieved readings |
| `set_alarm_mode` | set | `mode` (string) |  | Select the configuration of the four TTL alarm output lines: latch or track mode |
| `set_alarm_slope` | set | `edge` (string) |  | Select the slope of the pulse from the four TTL alarm outputs |
| `alarm_source` | set | `alarm` (int)<br>`channels` (string) |  | Assign one of four alarm numbers (1-4) to report any alarm conditions on the specified channels |
| `clear_alarms` | action |  |  | Clear all four alarm output lines |
| `clear_alarm` | set | `alarm` (int) |  | Clear the specified alarm output line |
| `set_voltage_range` | set | `range` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the DC voltage measurement range (100 mV to 300 V) |
| `set_voltage_range_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable autoranging for DC voltage measurements |
| `set_voltage_resolution` | set | `resolution` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the DC voltage measurement resolution (setting resolution also sets integration time) |
| `set_voltage_nplc` | set | `plcs` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the integration time in number of power line cycles (PLCs) for DC voltage measurements |
| `set_voltage_aperture` | set | `time` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Enable the aperture mode and set the integration time in seconds for DC voltage measurements |
| `set_ac_voltage_range` | set | `range` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the AC voltage measurement range (100 mV to 300 V) |
| `set_ac_voltage_range_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable autoranging for AC voltage measurements |
| `set_ac_bandwidth` | set | `filter` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Select the lowest expected input frequency (3, 20 or 200 Hz) to choose the AC filter for AC voltage measurements |
| `set_dc_current_range` | set | `range` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the DC current measurement range (10 mA to 1 A, ch 21/22 of 34901A/34902A) |
| `set_dc_current_range_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable autoranging for DC current measurements |
| `set_dc_current_nplc` | set | `plcs` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the integration time in power line cycles for DC current measurements |
| `set_ac_current_range` | set | `range` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the AC current measurement range |
| `set_ac_current_range_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable autoranging for AC current measurements |
| `set_ac_current_bandwidth` | set | `filter` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Select the lowest expected input frequency (3, 20 or 200 Hz) to choose the AC filter for AC current measurements |
| `set_resistance_range` | set | `range` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the 2-wire resistance measurement range |
| `set_resistance_range_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable autoranging for 2-wire resistance measurements |
| `set_resistance_nplc` | set | `plcs` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the integration time in power line cycles for 2-wire resistance measurements |
| `set_resistance_resolution` | set | `resolution` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the 2-wire resistance measurement resolution in ohms |
| `set_fresistance_range` | set | `range` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the 4-wire resistance measurement range |
| `set_fresistance_range_auto` | set | `state` (string)<br>`channels` (string) |  | Enable/disable autoranging for 4-wire resistance measurements |
| `set_fresistance_nplc` | set | `plcs` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the integration time in power line cycles for 4-wire resistance measurements |
| `set_fresistance_resolution` | set | `resolution` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the 4-wire resistance measurement resolution in ohms |
| `set_frequency_range_lower` | set | `frequency` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the lowest expected input frequency (3 to 300,000 Hz) for frequency measurements |
| `set_frequency_aperture` | set | `seconds` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the aperture time in seconds for frequency measurements |
| `set_period_aperture` | set | `seconds` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the aperture time in seconds (default 100 ms) for period measurements |
| `set_temperature_nplc` | set | `plcs` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the integration time in power line cycles for temperature measurements |
| `set_temperature_aperture` | set | `seconds` (number_or_keyword, or MIN/MAX/DEF)<br>`channels` (string) |  | Enable the aperture mode and set the integration time in seconds for temperature measurements |
| `query_reference_junction` | query | `channels` (string) | float | Return the internal reference junction temperature |
| `set_temperature_transducer_type` | set | `type` (string)<br>`channels` (string) |  | Select the temperature transducer type: TCouple, RTD, FRTD or THERmistor |
| `set_tc_type` | set | `type` (string)<br>`channels` (string) |  | Select the thermocouple type (B, E, J, K, N, R, S, T) for temperature measurements |
| `set_rtd_type` | set | `type` (int)<br>`channels` (string) |  | Select the RTD type (85 or 91: 0.00385 or 0.00391 alpha) for temperature measurements |
| `set_frtd_type` | set | `type` (int)<br>`channels` (string) |  | Select the FRTD type (85 or 91) for temperature measurements |
| `set_thermistor_type` | set | `type` (int)<br>`channels` (string) |  | Select the thermistor type (2252, 5000 or 10000 ohms) for temperature measurements |
| `set_tc_rjunction` | set | `temperature` (number_or_keyword, or MIN/MAX)<br>`channels` (string) |  | Set the thermocouple reference junction temperature in Celsius |
| `set_tc_rjunction_type` | set | `type` (string)<br>`channels` (string) |  | Select the thermocouple reference junction type (fixed or internal) |
| `set_tc_check` | set | `state` (string)<br>`channels` (string) |  | Enable/disable the thermocouple open-check function |
| `query_digital_data` | query | `channels` (string) | int | Configure the specified channels as inputs and read an 8-bit byte or 16-bit word digital pattern (34907A) |
| `set_zero_auto` | set | `mode` (string)<br>`channels` (string) |  | Enable/disable the autozero mode on the specified channels |
| `set_totalize_type` | set | `mode` (string)<br>`channels` (string) |  | Select the totalizer mode (read or read-and-reset) on the specified channels (34907A) |
| `set_totalize_slope` | set | `edge` (string)<br>`channels` (string) |  | Configure the specified totalizer channels to count on the rising or falling edge (34907A) |
| `totalize_clear` | set | `channels` (string) |  | Clear the totalizer count on the specified channels (34907A) |
| `totalize_start` | set | `channels` (string) |  | Start the totalizer counting on the specified channels (34907A) |
| `totalize_stop` | set | `channels` (string) |  | Stop the totalizer counting on the specified channels (34907A) |
| `query_totalize_data` | query | `channels` (string) | int | Read the totalizer count on the specified channels (34907A) |
| `query_average` | query | `channels` (string) | float | Return the average (arithmetic mean) of readings on the specified channels |
| `query_average_min` | query | `channels` (string) | float | Return the minimum reading on the specified channels |
| `query_average_max` | query | `channels` (string) | float | Return the maximum reading on the specified channels |
| `query_average_count` | query | `channels` (string) | int | Return the number of readings taken on the specified channels |
| `query_average_ptpeak` | query | `channels` (string) | float | Return the peak-to-peak value of readings on the specified channels |
| `clear_average` | set | `channels` (string) |  | Clear all statistical (average) data on the specified channels |
| `set_lower_limit` | set | `lo_limit` (float)<br>`channels` (string) |  | Set the lower alarm limit on the specified channels |
| `set_lower_limit_state` | set | `mode` (string)<br>`channels` (string) |  | Enable/disable the lower alarm limit on the specified channels |
| `set_upper_limit` | set | `hi_limit` (float)<br>`channels` (string) |  | Set the upper alarm limit on the specified channels |
| `set_upper_limit_state` | set | `mode` (string)<br>`channels` (string) |  | Enable/disable the upper alarm limit on the specified channels |
| `set_scale_gain` | set | `gain` (float)<br>`channels` (string) |  | Set the Mx+B scaling gain on the specified channels |
| `set_scale_offset` | set | `offset` (float)<br>`channels` (string) |  | Set the Mx+B scaling offset on the specified channels |
| `null_offset` | set | `channels` (string) |  | Set the Mx+B scaling offset to the present reading on the specified channels |
| `set_scale_state` | set | `state` (string)<br>`channels` (string) |  | Enable/disable Mx+B scaling on the specified channels |
| `set_scale_unit` | set | `quoted_string` (string)<br>`channels` (string) |  | Set the Mx+B scaling measurement label (up to 3 characters) |
| `compare_data` | set | `data` (int)<br>`channels` (string) |  | Set the digital compare data pattern on the specified channels (34907A) |
| `compare_mask` | set | `mask` (int)<br>`channels` (string) |  | Set the digital compare mask on the specified channels (34907A) |
| `compare_state` | set | `state` (string)<br>`channels` (string) |  | Enable/disable the digital compare mode on the specified channels (34907A) |
| `compare_type` | set | `mode` (string)<br>`channels` (string) |  | Select the digital compare mode: EQUal or NEQual (34907A) |
| `query_alarm_condition` | query |  | int | Read the condition register for the Alarm Register group (uses only bit 4) |
| `enable_alarm_status` | set | `enable_val` (int) |  | Enable bits in the enable register for the Alarm Register group |
| `query_alarm_event` | query |  | int | Read and clear the event register for the Alarm Register group |
| `query_operation_condition` | query |  | int | Read the condition register for the Standard Operation Register group |
| `enable_operation_status` | set | `enable_val` (int) |  | Enable bits in the enable register for the Standard Operation Register group |
| `query_operation_event` | query |  | int | Read and clear the event register for the Standard Operation Register group |
| `query_questionable_condition` | query |  | int | Read the condition register for the Questionable Data Register group |
| `enable_questionable_status` | set | `enable_val` (int) |  | Enable bits in the enable register for the Questionable Data Register group |
| `query_questionable_event` | query |  | int | Read and clear the event register for the Questionable Data Register group |
| `status_preset` | action |  |  | Preset all status registers to a known state |
| `digital_output` | set | `data` (int)<br>`channels` (string) |  | Write an 8-bit byte or 16-bit word digital pattern to the specified digital I/O channels (34907A) |
| `query_digital_output_state` | query | `channels` (string) | int | Return the direction (input or output) of the specified digital I/O channels (34907A) |
| `set_analog_output` | set | `voltage` (float)<br>`channels` (string) |  | Set the analog output voltage (0 to +12 V) on the specified channels (34907A) |
| `operation_complete` | action |  |  | set the OPC bit when all pending operations complete |
| `set_trigger_delay` | set | `seconds` (number_or_keyword, or MIN/MAX/DEF) |  | delay between the trigger and the first channel of the scan, in seconds |
| `set_internal_dmm` | set | `state` (string) |  | enable/disable the internal DMM (the instrument issues a factory reset when the state changes) |

<!-- END GENERATED dataloggers_series -->

### 3.6 Switch units (`switch_units_series`) — provisional

New category for mainframes that only route signals (no measurement engine). Reference manual: Agilent 3499A. The 3499A keeps its model id `DL_Agilent_3499A` so saved projects stay valid.

**Mandatory (provisional)**: `identification_query`, `reset`, `clear_status`, `select_channels`, `open_channels`, `close_channel`, `monitor_channel`, `initiate_scan`, `abort_scan`, `query_scan_size`, `set_trigger_source`, `trigger_bus`, `set_channel_delay`, `set_local`, `set_remote`.

**Optional**: relay-cycle, digital I/O, card pairing and state save/recall calls.

<!-- BEGIN GENERATED network_analyzers_series -->
### 3.7 Vector network analyzers (`network_analyzers_series`)

Generated from `schema/vna.json` — do not edit this section by hand. 5 mandatory and 4 optional calls.

Logical calls of vector network analyzers (VNA). PROVISIONAL: written from the LiteVNA manual only; mandatory / optional will be revised when the manuals of the SCPI VNAs are added (mandatory = documented in every manual of the category). Complex results are returned as arrays of real and imaginary parts.

Logical types:

* `sparameter`: `S11`, `S21`, `S12`, `S22`
* `sparameter_list`: list of S-parameters
* `calibration_standard`: `OPEN`, `SHORT`, `LOAD`, `THRU`
* `calibration_kind`: `ONE_PORT`, `TRANSMISSION_RESPONSE`
* `sparameters`: dict with "frequency" (array, Hz), "parameters" ({name: {"real": array, "imaginary": array}} for each selected S-parameter) and "calibrated" (bool: the calibration of the application or of the instrument was applied)

**Mandatory**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `identification_query` | query |  | string | instrument identification (manufacturer, model, hardware and firmware) |
| `set_frequency_sweep` | action | `start_frequency` (float, Hz, 0..)<br>`stop_frequency` (float, Hz, 0..)<br>`points` (int, points, 1..) |  | linear frequency sweep from start to stop frequency with a number of points |
| `select_sparameters` | action | `sparameters` (sparameter_list) |  | S-parameters measured by the next sweeps |
| `run_sweep` | action |  |  | start a sweep and discard the data of the previous one (read_sparameters then returns this sweep) |
| `read_sparameters` | query |  | sparameters | frequency and complex values of the selected S-parameters of the last sweep |

**Optional**

| Call | Kind | Arguments | Result | Description |
|---|---|---|---|---|
| `calibration_measure` | action | `standard` (calibration_standard)<br>`port` (int, 1.., default 1, optional) |  | measure a calibration standard connected to a test port |
| `calibration_apply` | action | `kind` (calibration_kind) |  | compute the calibration from the measured standards and use it for the next read_sparameters |
| `set_correction_state` | action | `state` (bool) |  | use (true) or bypass (false) the calibration in read_sparameters |
| `calibration_clear` | action |  |  | forget the measured standards and the calibration |

<!-- END GENERATED network_analyzers_series -->

## 4. Translation layer (arguments and answers)

The same logical call has the same arguments and logical values for every brand; the library translates them for each instrument: `map` (argument values), `response_map` / `bool` / `split` / `as_list` (answers), `steps` (several commands), derived parameters (`from`, `expr`) and defaults. The format is described in `schema/README.md`.

## 5. Known gaps and legacy names

* **OWON ODP**: the manual does not document `*CLS`, `SYSTem:ERRor?` and `*TST?`. `clear_status`, `error_query` and `self_test` exist in the library but are **not confirmed by the manual** (to be verified on the instrument).
* **Agilent 34970A** (datalogger): tested on a real instrument over RS-232 (null-modem cable, 57600 baud, XON/XOFF): 38 of the 39 calls tried were accepted (the other, `fetch_readings`, needs fresh data) and the readings of the configured channels were correct in the application. It is no longer marked `experimental`. The 34972A (same series), DAQ970A and DAQ973A are still experimental.
* **Siglent SDS HD**: the programming guide documents only `*IDN`, `*OPC` and `*RST` as common commands. Tested on a real SDS824X HD (FW 4.8.12.1.1.6.5): `error_query` (`SYSTem:ERRor?` → `0,"No error"`) works and `clear_status` (`*CLS`) is accepted, so both are kept although the guide does not list them. `self_test` (`*TST?` → 0) also works. `query_trigger_mode` can answer `FTRIG` after a forced trigger; it is mapped to `FORCED`. Verified on the same instrument: `*IDN?`, `*OPC?`, trigger status and mode, timebase, vertical settings, sample rate, and the waveform transfer (`:WAVeform:PREamble?` is a 346-byte binary descriptor, `:WAVeform:DATA?` a binary block of 400 000 bytes = 10 divisions × 20 µs/div × 2 GSa/s).
* **Rigol DS1000Z**: the manual lists `RUN` as a trigger state without defining it; the library maps it to `ARMED` (to be verified).
* **Siglent SDS HD** `set_trigger_slope`: `EITHER` is mapped to `ALTernate`, which the guide describes as alternating edges.
* **Siglent SDS2000X HD** `set_acquisition_depth`: the table of memory depths is the union of the single-channel and dual-channel values of the guide.
* **Chroma 6330A** `set_mode`: the low range (`CCL`, `CRL`, `CPL`) is selected; the high range has no logical call yet.
* **Multimeters** (HP 3478A, Agilent 34401A): there is no schema yet and no instrument available for testing. The library entries come from the manuals only and have never been run on a real instrument.
* **HP 3478A** `read_measurement`: the library entry `ENTER` is a GPIB read, not a command string. A read-only step is needed in the executor, and the manual is a scanned image (no text).
* **OWON ODP** `select_channel` uses `INST:NSEL` (numeric); by the convention of the other power supplies that should be `select_channel_numeric`. The by-name variant is `select_channel_named`.
* Legacy duplicates kept for compatibility: Tektronix `set_acquisition_mode` (same command as `set_acquisition_type`), HP E3631A `set_local_mode`/`set_remote_mode` (same commands as `set_local`/`set_remote`), TDK-Lambda GEN `set_local_remote`.

## 6. Model-specific commands

A series defines the calls shared by all its models (`common_scpi_commands`). When one model behaves slightly differently, the difference is written in that model's `scpi_commands`, keyed by the **same call name**. The software resolves the final command set of a model with `LoadInstruments.resolve_model_commands()` (also used by the remote panel), so the call names never change, only their definition.

Each entry of a model's `scpi_commands` has one of three forms:

| Form | Effect |
|---|---|
| a full definition (`"set"` and/or `"query"`, `"parameters"`) | **replaces** the series definition of that call |
| `null` | the call is **removed**: the model does not support it |
| `{"patch": {...}}` | the fields are **deep-merged** into the series definition (dicts are merged, lists and scalars replaced); use it to change only one syntax or one list of allowed values |

Examples (for a hypothetical model `X` whose memory depth allows other values and whose manual has no `force_trigger`):

```json
"scpi_commands": {
  "set_acquisition_depth": {
    "patch": { "parameters": { "depth": { "values": ["20k", "200k", "2M"] } } }
  },
  "set_trigger_holdoff": {
    "set": { "syntax": ":TRIGger:EDGE:HOLDoff {value}" },
    "query": { "syntax": ":TRIGger:EDGE:HOLDoff?", "return_type": "float" },
    "parameters": { "value": { "type": "float" } }
  },
  "force_trigger": null
}
```

Rules:
* Patching a call that the series does not define is ignored (a warning is logged); define the full call instead.
* Keep the parameter names of the series definition, so the software can fill the placeholders the same way on every model.
* A model-specific difference is written only when the model's manual documents it (rule 3 in section 1).

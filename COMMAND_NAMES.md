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
| Dataloggers | Keysight 34970A/34972A, Keysight DAQ970A | **provisional**: the DAQ970A manual is not yet in `docs/` |
| Switch units | Agilent 3499A | **provisional**: only one manual |

## 3. Common calls (all categories)

| Call | Action | Mandatory? |
|---|---|---|
| `identification_query` | `*IDN?` | mandatory (except 3478A, which has no `*IDN?`) |
| `reset` | `*RST` or equivalent | mandatory |
| `clear_status` | `*CLS` | optional (not in OWON ODP, Siglent SDS HD manuals) |
| `error_query` | read next error from the queue | optional (not in OWON ODP, Chroma 6330A, Siglent SDL1000X, Siglent SDS HD) |
| `self_test` | `*TST?` | optional (not in OWON ODP, Chroma 6330A, Siglent SDS HD) |
| `operation_complete_query` | `*OPC?` | optional for power supplies and loads, mandatory for oscilloscopes |

## 4. Mandatory and optional calls per category

### 4.1 Power supplies (`power_supplies_series`)

Verified in all five manuals.

**Mandatory**

| Call | Action |
|---|---|
| `identification_query` | identification string |
| `reset` | factory defaults |
| `set_voltage` | set voltage setpoint (the `query` part reads the setpoint back) |
| `set_current` | set current limit/setpoint (the `query` part reads it back) |
| `read_voltage` | measured output voltage |
| `read_current` | measured output current |
| `output_on` | enable output |
| `output_off` | disable output |
| `output_state_query` | read output state |
| `set_remote` | enter remote mode |
| `set_local` | return to local mode |

**Optional**

| Call | Action | Documented in |
|---|---|---|
| `clear_status` | clear status registers | all except OWON ODP |
| `error_query` | read error queue | all except OWON ODP |
| `self_test` | self test | all except OWON ODP |
| `select_channel` / `select_channel_numeric` / `select_channel_named` | select the channel that following commands address | multi-channel series (not the single-output TDK-Lambda GEN) |
| `query_selected_channel` | read selected channel | OWON ODP, R&S HMP, Keysight E36300, HP E3631A |
| `read_power` | measured output power | OWON ODP |
| `set_ovp_level` | overvoltage protection level | OWON ODP, Keysight E36300, TDK-Lambda GEN, R&S HMP (not HP E3631A) |
| `set_ocp_level` | overcurrent protection level | OWON ODP, Keysight E36300 |
| `enable_ocp` / `disable_ocp` | overcurrent protection state | Keysight E36300, TDK-Lambda GEN, R&S HMP (FUSE) |
| `query_ovp_tripped`, `query_ocp_tripped` | protection tripped | Keysight E36300, TDK-Lambda GEN, R&S HMP |
| `clear_protection` | clear tripped protection | Keysight E36300, R&S HMP |
| `apply_voltage`, `apply_current` | set value on all channels without changing the selected channel | OWON ODP |
| `apply` | select channel and set voltage and current together | Keysight E36300, R&S HMP, HP E3631A |
| `read_voltage_all`, `read_current_all` | measured value of all channels | OWON ODP |
| `set_channel_outputs` | per-channel output state in one command | OWON ODP |
| `set_track_mode` | tracking of channels | OWON ODP, HP E3631A |
| `set_series_mode`, `set_parallel_mode` | channels in series/parallel | OWON ODP |
| `save_state`, `recall_state` | store/recall setup | all except OWON ODP |

### 4.2 Electronic loads (`electronic_loads_series`)

Verified in all three manuals.

**Mandatory**

| Call | Action |
|---|---|
| `identification_query`, `reset`, `clear_status` | common |
| `load_on`, `load_off` | enable/disable the input |
| `query_input_state` | read input state |
| `set_mode` | select operating mode (CC/CV/CR/CP) |
| `query_mode` | read operating mode |
| `set_current_level` | constant-current level |
| `set_voltage_level` | constant-voltage level |
| `set_resistance_level` | constant-resistance level |
| `set_power_level` | constant-power level |
| `read_voltage`, `read_current`, `read_power` | measurements |
| `set_current_slew_rate_rise`, `set_current_slew_rate_fall` | current slew rate (rising / falling) |

**Optional**

| Call | Action | Documented in |
|---|---|---|
| `error_query`, `self_test` | | Keysight EL4900 (`error_query`); Siglent SDL1000X (`self_test`) |
| `select_channel` | channel select | Chroma 6330A |
| `short`, `open`, `query_short_state` | input short circuit | Keysight EL4900, Siglent SDL1000X |
| `set_ovp_level`, `set_ocp_level`, `set_opp_level`, `set_uvp_level`, `set_ucp_level` and their `enable_*`/`disable_*` | protections | Keysight EL4900, Siglent SDL1000X |
| `clear_protection_fault` | | Keysight EL4900 |
| `set_dynamic_level_high`, `set_dynamic_level_low`, `set_dynamic_frequency`, `enable_dynamic_mode`, `disable_dynamic_mode` | dynamic/transient load (used by the Pulse Generator tool) | Chroma 6330A, Siglent SDL1000X (the EL4900 has no dedicated dynamic mode) |
| `set_von_level` | load-on voltage | Chroma 6330A, Keysight EL4900, Siglent SDL1000X (to be confirmed per manual) |

### 4.3 Oscilloscopes (`oscilloscopes_series`)

Verified in all three manuals.

**Mandatory**

| Call | Action |
|---|---|
| `identification_query`, `reset`, `operation_complete_query` | common |
| `auto_setup` | automatic setup |
| `run_acquisition`, `stop_acquisition`, `acquire_single`, `force_trigger` | acquisition control |
| `set_timebase_scale`, `set_timebase_delay` | horizontal scale and delay/position |
| `set_channel_state` | show/hide channel |
| `set_channel_scale`, `set_channel_offset`, `set_channel_coupling` | vertical settings |
| `set_channel_bandwidth_limit` | bandwidth limit filter |
| `set_probe_attenuation` | probe attenuation factor |
| `set_trigger_source`, `set_trigger_level`, `set_trigger_slope`, `set_trigger_mode`, `set_trigger_holdoff` | edge trigger |
| `query_trigger_status` | trigger/acquisition state |
| `set_acquisition_type`, `set_acquisition_depth` | acquisition type (normal/average/peak) and memory depth |
| `query_sample_rate` | current sample rate |
| `set_waveform_source`, `set_waveform_format`, `query_waveform_preamble`, `query_waveform_data` | waveform transfer |

**Optional**

| Call | Action | Documented in |
|---|---|---|
| `clear_status`, `error_query`, `self_test` | | Tektronix, Rigol (not Siglent SDS HD) |
| `query_<x>` for each `set_<x>` above | read-back of a setting | per manual |
| `set_channel_invert` | invert channel | Rigol, Siglent SDS HD |
| `set_channel_impedance` | input impedance | Tektronix, Siglent SDS HD |
| `set_channel_unit` | channel unit (V/A) | Rigol, Siglent SDS HD |
| `set_trigger_type` | trigger type | all three, syntax differs (to be confirmed per series) |
| `set_trigger_coupling` | trigger coupling | Rigol, Siglent SDS HD |
| `set_waveform_start`, `set_waveform_points`, `set_waveform_interval`, `query_waveform_max_points`, `set_waveform_byte_order` | waveform transfer window | Siglent SDS HD, Rigol (partly) |
| `set_measurement_item`, `set_measurement_source`, `query_measurement_value` | built-in measurements | Siglent SDS HD, Rigol, Tektronix (different models) |
| `set_remote` | remote lock | Siglent SDS HD |

### 4.4 Multimeters (`multimeters_series`) — provisional

Based on the two manuals available. The 3478A manual is scanned, so its coverage was taken from the existing library entries. **Needs more manuals before it is final.**

**Mandatory (provisional)**: `reset`, `set_function`, `set_range`, `set_resolution`, `set_autozero`, `set_trigger_source`, `trigger_bus`, `read_measurement`.

**Optional**: `identification_query` (not on the 3478A), `clear_status`, `error_query`, `query_status_byte`, `measure_*`, `configure_*`, `fetch_readings`, `set_auto_range`, `set_trigger_count`, `set_trigger_delay`, `set_sample_count`, `set_math_*`, `set_limit_*`, `set_nulls`, display commands.

### 4.5 Dataloggers (`dataloggers_series`) — provisional

Reference manuals: 34970A/34972A and DAQ970A. **The DAQ970A manual must be added to `docs/` before this list is final**; until then the list below comes from the 34970A/34972A manual only.

**Mandatory (provisional)**: `identification_query`, `reset`, `clear_status`, `error_query`, `select_channels`, `open_channels`, `close_channel`, `monitor_channel`, `initiate_scan`, `read_scan`, `fetch_readings`, `abort`, `read_measurement`, `configure_*`/`measure_*` for each function in the manual, `set_function`, `set_trigger_source`, `set_trigger_count`, `set_trigger_timer`, `trigger_bus`, `set_channel_delay`.

**Optional**: alarm, scale, totalizer and digital I/O calls.

### 4.6 Switch units (`switch_units_series`) — provisional

New category for mainframes that only route signals (no measurement engine). Reference manual: Agilent 3499A. The 3499A keeps its model id `DL_Agilent_3499A` so saved projects stay valid.

**Mandatory (provisional)**: `identification_query`, `reset`, `clear_status`, `select_channels`, `open_channels`, `close_channel`, `monitor_channel`, `initiate_scan`, `abort_scan`, `query_scan_size`, `set_trigger_source`, `trigger_bus`, `set_channel_delay`, `set_local`, `set_remote`.

**Optional**: relay-cycle, digital I/O, card pairing and state save/recall calls.

## 5. Implementation status

| Series | Status |
|---|---|
| OWON ODP | calls from section 4.1 added where the manual documents the command |
| Siglent SDS HD | calls from section 4.3 added where the manual documents the command |
| all other series | not yet aligned to this list |

## 6. Known gaps and legacy names

* **OWON ODP**: the manual does not document `*CLS`, `SYSTem:ERRor?` and `*TST?`. The entries `clear_status`, `error_query` and `self_test` exist in the library but are **not confirmed by the manual**.
* **Siglent SDS HD**: the programming guide documents only `*IDN`, `*OPC` and `*RST` as common commands. `clear_status`, `error_query` and `self_test` exist in the library but are **not confirmed by the guide**. `force_trigger` is `:TRIGger:MODE FTRIG`.
* **Siglent SDS HD** `set_acquisition_depth`: the guide defines `<memory_size>` as a string such as `10k`/`100M`; the library declares an `int`.
* **OWON ODP** `select_channel` uses `INST:NSEL` (numeric); by the convention of the other power supplies that should be `select_channel_numeric`. The by-name variant is added as `select_channel_named`.
* Legacy names for the same action: `set_local_mode` / `set_remote_mode` (HP E3631A) and `set_local_remote` (TDK-Lambda GEN) correspond to `set_local` / `set_remote`.

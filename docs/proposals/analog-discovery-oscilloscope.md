# Digilent Analog Discovery 2: the oscilloscope (AnalogIn)

Status: model `OSC_Digilent_AnalogDiscovery2` in `oscilloscopes_series` (series `Digilent_AnalogDiscovery_Scope_Series`), **experimental**; the waveform generator of the same device is in `function_generators_series`. The source is the AnalogIn chapter of the WaveForms SDK reference manual (`docs/Digilent/Analog_Discovery_Series/`). It is a **driver** model (`access: driver`, `driver_id: waveforms`, connection kind `dwf`, address `DWF::<serial number>`): the application's `ola/drivers/waveforms.py` implements the calls. A generator and a scope of the same address share the open device.

## The calls

| Call | WaveForms | Notes |
|---|---|---|
| `set_channel_state` | `FDwfAnalogInChannelEnableSet` | |
| `set_channel_scale` / `query_channel_scale` | `FDwfAnalogInChannelRangeSet` / `Get` | the range is **peak to peak**: volts per division x **10** (the SDK has no divisions: a convention of the driver); a value outside `...RangeInfo` is not handled |
| `set_channel_offset` / `query_channel_offset` | `FDwfAnalogInChannelOffsetSet` / `Get` | outside `...OffsetInfo`: not handled |
| `set_probe_attenuation` | `FDwfAnalogInChannelAttenuationSet` | tells the library about an attenuation applied outside; it does not change the device |
| `set_channel_coupling` | - | the SDK has no coupling control: `DC` is accepted, `AC` and `GND` are not handled |
| `set_timebase_scale` | - | time per division, **10 divisions** of record; used when the acquisition starts |
| `set_acquisition_depth` | `FDwfAnalogInBufferSizeSet` | outside `...BufferSizeInfo`: not handled |
| `run_acquisition`, `acquire_single` | `FDwfAnalogInFrequencySet` (= depth / record, limited to the ADC range), `FDwfAnalogInConfigure` | one single acquisition of the buffer |
| `stop_acquisition` | `FDwfAnalogInStatus` until Done, `FDwfAnalogInStatusData` | the device has **no frozen screen**: the call completes the running capture and keeps the samples of every enabled channel (so two channels come from the same capture), it does not interrupt it |
| `read_waveform`, `query_waveform_max_points` | `FDwfAnalogInStatusData` | voltage in volts; `time` is relative to the middle of the buffer (the default trigger position); the whole capture is one block; the generic whole-memory read of the application works |
| `query_sample_rate` | `FDwfAnalogInFrequencyGet` | |
| `set_trigger_source`, `set_trigger_level`, `set_trigger_slope`, `set_trigger_mode`, `set_trigger_holdoff`, `query_trigger_status` | `FDwfAnalogInTriggerSourceSet` (`trigsrcDetectorAnalogIn`), `...ChannelSet`, `...LevelSet`, `...ConditionSet`, `...AutoTimeoutSet`, `...HoldOffSet`, `FDwfAnalogInStatus` | slope `RISE` / `FALL` (no `EITHER`); mode `AUTO` = auto trigger after 1 s, `NORMAL` and `SINGLE` = wait |
| `reset` | `FDwfAnalogInReset` | the generator is not touched |

**Not supported (`CALL-001`)**, the mandatory calls the device has no equivalent for (they are defined with the function `unsupported_<call>`, so every model has every mandatory call and the driver answers with the reason): `operation_complete_query`, `auto_setup`, `force_trigger`, `set_timebase_delay`, `set_channel_bandwidth_limit` (the SDK filters decimate or average, they do not limit the bandwidth), `set_acquisition_type`, and the SCPI waveform transfer (`set_waveform_source`, `set_waveform_format`, `query_waveform_preamble`, `query_waveform_data`: `read_waveform` is used instead). The Bode measurement, for example, sends `set_channel_coupling` (use `DC`), the optional bandwidth limit only when asked, and none of the others.

## To verify on the device (the owner has an Analog Discovery 2)

1. **The numeric constants** of `dwf.h` / `dwfconstants.py` (not in the reference manual): the acquisition states (Ready 0, Armed 1, Done 2, Triggered 3, Config 4, Prefill 5, Wait 7), `trigsrcDetectorAnalogIn` 2, `trigcondRisingPositive` 0, `trigcondFallingNegative` 1. Compare with `dwfconstants.py` of the installation.
2. **The range**: the manual says "peak to peak values"; with the 10-division convention a requested 0.5 V/div sets a 5 V range; check the value the device reports (`query_channel_scale`).
3. **The time axis and the trigger**: the buffer is acquired with the trigger at its middle by default; check with the generator of the same device (W1 to scope channel 1 and 2): a 1 kHz sine, 5 cycles on screen, must read about 1 kHz and 0 degrees between the two channels.
4. **Auto trigger**: with the source `trigsrcNone` after a reset an acquisition should start at once; if the device waits for a trigger, set the trigger mode `AUTO`.

# Function generators: logical calls

Status: the **schema** (`schema/function_generator.json`, category `function_generators_series`) is in; the library has **no generator model yet**. A command goes into the library only when the manual of the instrument documents it, so the first models need their programming manuals (for example a Rigol DG1000Z / DG800, Siglent SDG, Keysight 33500B, GW Instek AFG, Tektronix AFG).

## Why

The Bode plot measurement of the application needs a generator that drives the circuit under test and two oscilloscope channels that read the input and the output. The scope side already exists in `oscilloscope.json`; this category adds the generator side.

## The calls

| Call | Requirement | Arguments |
|---|---|---|
| `identification_query` | mandatory | - |
| `reset` | mandatory | - |
| `set_output_state` | mandatory | `channel_number` (int, optional), `state` (bool) |
| `set_frequency` | mandatory | `channel_number` (int, optional), `value` (Hz) |
| `set_amplitude` | mandatory | `channel_number` (int, optional), `value` (**Vpp**) |
| `set_waveform_shape` | optional | `channel_number` (int, optional), `shape` (`SINE`, `SQUARE`, `TRIANGLE`, `RAMP`, `PULSE`, `NOISE`, `DC`, `ARBITRARY`) |
| `set_offset` | optional | `channel_number` (int, optional), `value` (V) |
| `clear_status`, `error_query`, `set_remote` | optional | - |

* `channel_number` is optional (as for the power supplies): a single-output generator ignores it; the application always passes it.
* The mandatory set is what the Bode measurement sends plus `*IDN?` and `*RST`, which every SCPI instrument has. If a manual of a model we add later lacks one of them, the call goes to optional (the rule is "mandatory = in the manual of every model of the category").
* The measurement switches every output **off** before it starts and when it ends, also after an error (`set_output_state` with `state: false`).
* The amplitude is peak-to-peak as set on the generator. What the circuit sees also depends on the **output load** setting (50 ohm or high impedance) of the generator; the application does not change it and the logical calls do not include it. If it turns out to be needed, it is added as an optional call (`set_output_load`) together with the manual that documents it.
* A shape a model does not list is "not handled by this model" (`CALL-002`); a model without `set_waveform_shape` keeps whatever shape it has after `reset` (a sine on the usual generators).

## What is still needed

1. The programming manuals of the generators to support, to write the entries (series, models, SCPI, transports, channels, frequency / amplitude limits in `capabilities`).
2. In the application: the type `function_generator` in the instrument list (add / edit dialogs, translations) and the role category used by the Bode module (`generator`).

## First manual received: FeelTech FY3200S series (`docs/fy32xxs_series_users_manual_v1.4.pdf`)

Read in full (15 pages). **It documents the instrument, not its remote protocol**: the only mention is "each function can be adjusted by host computer" and a "square port USB wire" in the accessories; there is no command, no serial setting, no baud rate. A model cannot be added to `instruments_lib.json` from it, because a command goes into the library only if it is documented or verified (and a series without the mandatory calls fails `Tests/check_conformance.py`). **The communication protocol document of the FY series (from FeelTech) is needed**, or a verified session on the instrument.

What the manual does give, to be used for the `capabilities` of the models when the protocol is there:

| | FY3206S | FY3212S | FY3220S | FY3224S |
|---|---|---|---|---|
| Sine frequency | 0 - 6 MHz | 0 - 12 MHz | 0 - 20 MHz | 0 - 24 MHz |
| Square, triangle, arbitrary frequency | 0 - 6 MHz | 0 - 6 MHz | 0 - 6 MHz | 0 - 6 MHz |

* Two independent output channels (**CH1 = main "MF"**, **CH2 = subsidiary "SF"**), each can be switched off and on separately; frequency resolution 10 mHz (0.01 Hz), accuracy 5 ppm.
* Amplitude "Vpp" up to 20 Vpp **with no load**, output impedance 50 ohm (+/-10 %): the same caveat as above about the load; DC offset +/-10 V; square duty 0.1 % to 99.9 %; phase of CH2 against CH1 0 to 359 degrees; sampling rate 250 MSa/s, 12 bit.
* Waveforms on the display: `SINE`, `SQUR`, `TRGL`, 4 user arbitrary memories `ARB1`-`ARB4`, and ten built-in ones `PRE1`-`PRE10` (Lorentz pulse, multitone, random noise, ECG, trapezoid, sinc, narrow pulse, white Gaussian noise, AM, FM). The sawtooth is a triangle with a duty cycle other than 50 %. There is **no plain DC or pulse shape** in the list: a call with `DC` or `PULSE` would be "not handled by this model" (`CALL-002`), `TRIANGLE` and `SINE` are fine.
* Counter / frequency meter (CH1 input), linear and logarithmic sweep (CH1), 20 memories: nothing in the logical calls yet.

This is why `TRIANGLE` was added to `waveform_shape`.

## First model: Digilent Analog Discovery 2 (`FGEN_Digilent_AnalogDiscovery2`)

The WaveForms SDK reference manual (`docs/Digilent/Analog_Discovery_Series/waveforms_sdk_reference_manual.pdf`, AnalogOut chapter) documents everything the mandatory calls need, so the AD2 is the first model. It is a **driver** model (`access: driver`, `driver_id: waveforms`) with its own connection kind `dwf` (the WaveForms runtime, address `DWF::<serial number>`), implemented by `ola/drivers/waveforms.py` of the application.

| Call | WaveForms |
|---|---|
| `set_output_state` | `FDwfAnalogOutNodeEnableSet` (carrier) + `FDwfAnalogOutConfigure` (start / stop); channel number 1-based, SDK index 0-based |
| `set_frequency` | `FDwfAnalogOutNodeFrequencySet` (Hz) |
| `set_amplitude` | `FDwfAnalogOutNodeAmplitudeSet` |
| `set_offset` | `FDwfAnalogOutNodeOffsetSet` |
| `set_waveform_shape` | `FDwfAnalogOutNodeFunctionSet`: `SINE` funcSine, `SQUARE` funcSquare, `TRIANGLE` funcTriangle, `RAMP` funcRampUp, `NOISE` funcNoise, `DC` funcDC. `PULSE` and `ARBITRARY` are not handled (a custom waveform needs its data) |
| `reset` | `FDwfAnalogOutReset` (all channels) |
| `identification_query` | `FDwfEnumDeviceName` + `FDwfEnumSN` |

**Experimental, to verify on the device (the owner has an AD2):**

1. **Amplitude.** The manual says "Volts" and not whether it is peak or peak-to-peak. The driver sends half of the Vpp (the usual WaveForms meaning is the peak). Check with the scope of the same device: W1 to scope channel 1, 1 Vpp requested should read 1 Vpp. If it does not, the factor is one constant of the driver.
2. **Numeric constants.** `enumfilterAll`, the node ids and the `FUNC` values are in `dwf.h` / `dwfconstants.py` of the SDK, **not in the reference manual**; the driver uses the values of those files (carrier 0, enumfilterAll 0, funcDC 0, funcSine 1, funcSquare 2, funcTriangle 3, funcRampUp 4, funcRampDown 5, funcNoise 6): compare them with `dwfconstants.py` of the installation.
3. **Switching off.** `set_output_state(false)` stops the channel and disables the carrier node; check that the output goes to 0 V on the idle setting of the device.
4. Number of channels and the ranges are read from the device; the manual has no figure for it.

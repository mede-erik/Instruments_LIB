# Function generators: logical calls and first models

Status: schema `schema/function_generator.json` (category `function_generators_series`) and three models in the library, **all experimental** (none was tested on an instrument except what the owner can try, see the last section). A command goes into the library only if a manual documents it or it was verified on the instrument.

## Why

The Bode plot measurement of the application needs a generator that drives the circuit under test and two oscilloscope channels that read the input and the output. The scope side already exists in `oscilloscope.json`; this category adds the generator side.

## The calls

The rule is the one of the other categories: **mandatory = documented in the manual of every model of the category**, so the list follows the manuals received (Digilent WaveForms SDK, Rigol DG1000 programming guide, Agilent 33120A user's guide):

| Call | Requirement | Arguments |
|---|---|---|
| `identification_query` | mandatory | - |
| `set_frequency` | mandatory | `channel_number`, `value` (Hz) |
| `set_amplitude` | mandatory | `channel_number`, `value` (**Vpp**) |
| `set_offset` | mandatory | `channel_number`, `value` (V) |
| `set_waveform_shape` | mandatory | `channel_number`, `shape` (`SINE`, `SQUARE`, `TRIANGLE`, `RAMP`, `PULSE`, `NOISE`, `DC`, `ARBITRARY`) |
| `set_output_state` | optional | `channel_number`, `state` |
| `reset` | optional | - |
| `clear_status`, `error_query`, `set_remote` | optional | - |

* **`set_output_state` and `reset` are optional because of the manuals**: the Agilent 33120A has **no output on / off** in its command set (only the output load and the sync output), and the Rigol DG1000 guide lists `*IDN?` as the only IEEE 488.2 command (**no `*RST`**). A measurement that must switch the output off (the Bode) has to handle `CALL-001` for those models.
* `channel_number` is optional with default 1; a single-output generator accepts only channel 1 (another channel is "not handled by this model", `CALL-002`).
* The amplitude is peak-to-peak as set on the generator; what the circuit sees also depends on the **output load** (50 ohm or high impedance), which the logical calls do not change. If it turns out to be needed it is added as an optional call (`set_output_load`), with the manual that documents it (`OUTPut:LOAD` exists in both the Rigol and the Agilent commands).
* A shape a model does not list is "not handled by this model" (`CALL-002`).

## Models in the library

| Model | Manual (`docs/`) | Connection | Notes |
|---|---|---|---|
| **Digilent Analog Discovery 2** (`FGEN_Digilent_AnalogDiscovery2`) | `Digilent/Analog_Discovery_Series/waveforms_sdk_reference_manual.pdf` | WaveForms runtime, address `DWF::<serial number>` (kind `dwf`) | driver model (`driver_id: waveforms`, `ola/drivers/waveforms.py`); `PULSE` and `ARBITRARY` not handled; see below |
| **Rigol DG1022, DG1022A** (`FGEN_Rigol_DG1022`, `..._DG1022A`) | `Rigol/DG1000_Series/DG1000_ProgrammingGuide_EN.pdf` (Jan 2014; the older `DG1022_ProgrammingGuide_EN.pdf`, Aug 2009, is kept too) | USB device port (USB-TMC) | two channels: CH2 commands end with `:CH2` (a derived parameter `suffix`); `TRIANGLE` is a ramp with 50 % symmetry, `RAMP` is not handled; the amplitude is sent after `VOLTage:UNIT VPP`; sweep and modulation only on CH1 (no logical call) |
| **Agilent (HP) 33120A** (`FGEN_Agilent_33120A`) | `Agilent/33120A_Series/Agilent_33120A_Users_Guide.pdf` | HP-IB (GPIB) and RS-232 (9600 baud, 8 data bits, no parity, **2 stop bits**, DTR / DSR; `SYSTem:REMote` first) | single channel; no output switch, no pulse waveform; `set_remote`, `reset`, `clear_status` and `error_query` documented |

### Analog Discovery 2: to verify on the device (the owner has one)

1. **Amplitude.** The reference manual says only "Volts", not peak or peak-to-peak. The driver sends half of the Vpp. Check with the scope of the same device: W1 to scope channel 1, 1 Vpp requested should read 1 Vpp. If it does not, the factor is one constant of the driver (`PEAK_PER_VPP`).
2. **Numeric constants.** `enumfilterAll`, the node ids and the `FUNC` values are in `dwf.h` / `dwfconstants.py` of the SDK, **not in the reference manual**; the driver uses the values of those files (carrier 0, enumfilterAll 0, funcDC 0, funcSine 1, funcSquare 2, funcTriangle 3, funcRampUp 4, funcRampDown 5, funcNoise 6): compare them with `dwfconstants.py` of the installation.
3. **Switching off.** `set_output_state(false)` stops the channel and disables the carrier node; check that the output goes to 0 V.

## Manuals received that cannot give a model yet

* **Rigol DG1000Z** (`docs/Rigol/DG1000Z_Series/DG1000Z_User_Guide.pdf`, 180 pages): the user guide has a "Remote Control" chapter that only says how to connect (USB, LAN as an LXI Core 2011 device, GPIB option); **it has no command reference**. The programming guide of the DG1000Z series is needed.
* **FeelTech FY3200S series** (`docs/FeelTech/FY3200S_Series/fy32xxs_series_users_manual_v1.4.pdf`, 15 pages): the user manual of the instrument, **no remote protocol** (it only says "each function can be adjusted by host computer" and lists a USB cable). See `fy3200s-protocol-test-plan.md`.

What the FY3200S manual does give, for the `capabilities` of the models when the protocol is there:

| | FY3206S | FY3212S | FY3220S | FY3224S |
|---|---|---|---|---|
| Sine frequency | 0 - 6 MHz | 0 - 12 MHz | 0 - 20 MHz | 0 - 24 MHz |
| Square, triangle, arbitrary frequency | 0 - 6 MHz | 0 - 6 MHz | 0 - 6 MHz | 0 - 6 MHz |

Two independent channels (**CH1 = main "MF"**, **CH2 = subsidiary "SF"**) each with its own output on / off; frequency resolution 10 mHz; amplitude up to 20 Vpp **with no load**, output impedance 50 ohm; DC offset +/-10 V; 250 MSa/s, 12 bit; waveforms `SINE`, `SQUR`, `TRGL`, four arbitrary memories and ten built-in ones (no plain DC or pulse: `DC` and `PULSE` would be "not handled by this model"); counter and linear / logarithmic sweep (no logical calls yet).

## What is still needed

1. The **DG1000Z programming guide** and the **FY series communication protocol**.
2. In the application, for the Bode: the role category `generator` of the measurement uses `function_generator`; the type is already in the instrument lists.

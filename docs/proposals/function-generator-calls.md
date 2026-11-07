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
| `set_waveform_shape` | optional | `channel_number` (int, optional), `shape` (`SINE`, `SQUARE`, `RAMP`, `PULSE`, `NOISE`, `DC`, `ARBITRARY`) |
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

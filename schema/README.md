# schema/

One file per instrument category. A schema file is the **contract** of that category: the logical calls the software uses, their arguments (names, types, units, logical values) and the type of their result. The software never knows vendor syntax; the library (`instruments_lib.json`) says, for every instrument, which SCPI strings implement each logical call.

| File | Library category |
|---|---|
| `oscilloscope.json` | `oscilloscopes_series` |
| `power_supply.json` | `power_supplies_series` |
| `electronic_load.json` | `electronic_loads_series` |
| `function_generator.json` | `function_generators_series` (see `docs/proposals/function-generator-calls.md`) |

More categories are added one at a time (power supplies, electronic loads, dataloggers, multimeters, switch units).

## Schema file format

```json
{
  "schema_version": 1,
  "category": "oscilloscopes_series",
  "types": { "coupling": { "kind": "enum", "values": ["DC", "AC", "GND"] } },
  "calls": {
    "set_channel_coupling": {
      "requirement": "mandatory",
      "kind": "set",
      "description": "input coupling",
      "args": {
        "channel_number": { "type": "int", "min": 1 },
        "coupling_type":  { "type": "coupling" }
      }
    }
  }
}
```

| Field | Meaning |
|---|---|
| `requirement` | `mandatory`: every series of the category must define the call. `optional`: define it only if the manual documents it |
| `kind` | `action` (write, no result), `set` (write, may also read back), `query` (read) |
| `args` | argument name -> `type`, optional `unit`, `min`, `max`, `required` (default true), `description` |
| `result` | for queries: `type` and `unit` of the logical value |
| `types` | named logical types: `enum` (fixed list of logical values) and `bool` |

Base types: `int`, `float`, `string`, `binary` (IEEE 488.2 block, bytes), `raw` (the answer as the instrument gives it: text or bytes, model dependent), `number_or_keyword`, plus the names in `types` (`enum`, `bool`, `list` of an item type, `mapping`). Units are SI-based (`V`, `V/div`, `s`, `s/div`, `Hz`, `Sa/s`, `points`, `ratio`).

An argument with `"required": false` may be ignored by instruments that do not need it (for example `channel_number` in `set_trigger_level`, which only some instruments set per channel). The software always passes every argument it has.

## How a library entry implements a call (translation layer)

The library entry keeps the schema argument names. Where the instrument's own values differ from the logical ones, the entry translates them.

### Single string (current form, still valid)

```json
"set_trigger_level": { "set": { "syntax": ":TRIGger:EDGE:LEVel {value}" }, "parameters": { "value": { "type": "float" } } }
```

### Several commands: `steps`

```json
"acquire_single": {
  "set": { "steps": [
    { "op": "write", "text": "ACQuire:STOPAfter SEQuence" },
    { "op": "write", "text": "ACQuire:STATE RUN" }
  ]}
}
```

A step has `op` (`write`, `query`, `delay`), `text` (the string, with `{argument}` placeholders), `ms` (for `delay`), optional `timeout_ms`, and for a query `returns` (`float`, `int`, `string`, `binary`; default `string`). Steps are sent in order; they are never joined into one message.

### Steps that depend on an argument, and steps repeated per list item

A step with `"when": {"kind": "ONE_PORT"}` (or a list of values) is used only when the argument has that value; a calibration kind that needs different commands is written as one step per kind. A step (or a group of `"steps"`) with `"foreach": "sparameters"` is repeated for every item of a list argument, with `{item}`, `{index}` (from 0) and `{n}` (from 1) in the text; `{sparameters}` is the comma-separated list and `{sparameters_count}` its length. A list argument is validated item by item (the schema type is `{"kind": "list", "item": "<type>"}`) and may be given as a list or as comma-separated text.

### Named parsers: `parse`

When the answer is several raw answers combined into one logical value (a waveform, the S-parameters of a network analyzer), the query half names a parser of the application (`ola/parsers.py`): `"parse": {"name": "vna_sparameters", "from_steps": "queries", "args": ["sparameters"], "skip_queries": 1}`. `from_steps` is a list of step indexes or `"queries"` (the answers of all the query steps, in order); `skip_queries` drops the first answers (for example an `*OPC?`); `args` are logical arguments the parser needs. Parsers: `siglent_waveform` (an SDS waveform) and `vna_sparameters` (ASCII answers of an SCPI VNA: correction state, frequencies, one list of real/imaginary pairs per S-parameter).

### Argument translation: `map`

```json
"parameters": { "slope": { "type": "string", "map": { "RISE": "RISe", "FALL": "FALL", "EITHER": "EITher" } } }
```

`map` goes from the logical value to the text the instrument expects. A logical value that is not in the map is **not handled by this model** (error `CALL-002`). Without a `map`, an argument of type `bool` is sent as `ON`/`OFF`.

### Derived parameters: one logical argument, several instrument values

A library parameter with `"from"` is computed from the logical arguments instead of being passed by the caller. With a `map` it translates one argument into several texts (Tektronix waveform format: `DATa:ENCdg` and `DATa:WIDth`). With `"expr"` it is a formula over logical arguments (numbers, names, `+ - * / **`, parentheses) for instruments whose own parameters differ from the logical ones (dynamic load timing):

```json
"t_high": { "from": ["frequency", "duty"], "expr": "duty / 100 / frequency" }
```

A schema argument can have a `"default"` (for example `duty`: 50) that is used when the caller omits it.

### Response translation: `response_map`

```json
"query": { "syntax": "TRIGger:STATE?", "return_type": "string",
           "response_map": { "ARMED": "ARMED", "READY": "READY", "AUTO": "AUTO", "TRIGGER": "TRIGGERED", "SAVE": "STOPPED" } }
```

`response_map` goes from the instrument's text to the logical value. A response that is not in the map is an error (`CALL-005`). Other response options: `"bool": {"true": ["1", "ON"], "false": ["0", "OFF"]}` and `"split": ","` with `"index"` for answers that contain several values.

These fields are the format agreed for the translation layer; the planner that reads them is not written yet, so the current software ignores `steps`, `map` and `response_map`.

## `access` (how a model's calls are executed)

A model may declare `"access"` at model level. There are exactly two values:

| Value | Meaning |
|---|---|
| `scpi` (default) | the call is a **step plan** (`write` / `query` / `delay`) run by the generic executor; it is also used for non-SCPI **text** protocols (a serial shell) |
| `driver` | the call is not a command string: it is delegated to a driver (for example Digilent WaveForms for the Analog Discovery, or the binary register protocol of the LiteVNA) as `{"driver": {"function": "<name>"}}`. The call names and the argument schema are the same, so the software does not change |

A `driver` model has no `steps`; the conformance check accepts a driver entry as an implemented call. A mandatory call a driver has no equivalent for is still defined, with the function `unsupported_<call>`: the driver answers "not supported" (`CALL-001`) with the reason (the Analog Discovery oscilloscope does this for the SCPI waveform transfer and a few others).

## `transports` (how a connection is opened)

An entry of `interface.supported_connection_types` can list the transports the model accepts on that connection, **only when the manual states them**:

| `kind` | Fields |
|---|---|
| `vxi11` | - (VISA address `TCPIP0::<ip>::inst0::INSTR`) |
| `raw_socket` | `port` (and `port_configurable: true` if the user can change it) |
| `usbtmc` | - |
| `dwf` | - (the Digilent WaveForms runtime, not VISA; address `DWF` for the first device or `DWF::<serial number>`; the model has `access: driver` and `driver_id: waveforms`) |
| `serial` | `baud`, `data_bits`, `parity` (`N`/`E`/`O`), `stop_bits`, `flow_control` (`none`, `xon_xoff`, `rts_cts`, `dtr_dsr`), `write_termination`, `read_termination`; `factory_defaults: true` means the values are the manual's factory settings and the instrument's front-panel menu may differ (a project can override them per instrument) |

Example (Siglent SDS HD, from its programming guide): `"transports": [{"kind": "vxi11"}, {"kind": "raw_socket", "port": 5025}]`. Models without `transports` are not specified yet: the software must not assume a transport for them.

## Manual instruments are not in the library

A *manual instrument* is an instrument without remote control (a bench power supply or an electronic load operated by hand). It is a **generic** instrument defined by the user in the project (type, name, channels and limits such as maximum voltage and current), **not** a model of this library: there is no entry for it in `instruments_lib.json`, no SCPI, no transport. The application operates it by asking the operator to set and read values, using the same logical call names and the same argument limits as the schemas of its category. Do not add manual or generic instruments to `instruments_lib.json`.

## Documentation

`COMMAND_NAMES.md` contains tables of the mandatory and optional calls of every category **generated from these schema files**. After changing a schema run:

```bash
python3 schema/generate_command_names.py          # rewrite the generated sections
python3 schema/generate_command_names.py --check  # exit 1 if COMMAND_NAMES.md is out of date
```

## Conformance check

```bash
python3 Tests/check_conformance.py            # errors fail, TODO items are listed
python3 Tests/check_conformance.py --strict   # TODO items fail too
```

* **ERROR**: a mandatory call is missing, an argument name is not in the schema, or a call has the wrong half (set/query).
* **TODO**: the library still gives vendor values where the schema defines logical ones (it needs a `map`), or a call is not in the schema.

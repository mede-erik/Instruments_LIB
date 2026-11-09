# Instruments_LIB

Data-only JSON library that acts as a **rule engine** for a Python SCPI driver. It contains no code: the file `instruments_lib.json` describes the series, models, SCPI commands, physical interfaces and hardware limits of every instrument, so that the driver can validate data, format requests, manage connections and interpret responses dynamically.

To check the library against a real instrument see [TESTING.md](TESTING.md).

## File structure

The file `instruments_lib.json` is a single object with the key `instrument_library`, containing 7 categories:

| Key | Category | Examples |
|---|---|---|
| `power_supplies_series` | Power supplies | OWON ODP, Keysight E36300, TDK-Lambda GEN, R&S HMP, HP E3631A |
| `dataloggers_series` | Data loggers (mainframes) | Keysight 34970A/34972A, Keysight DAQ970A |
| `switch_units_series` | Switch units (no measurement engine) | Agilent 3499A |
| `datalogger_modules` | Datalogger cards (modules) | Keysight 34901A, 34902A, 34908A, DAQM900A, DAQM901A |
| `multimeters_series` | Multimeters | HP 3478A, Agilent 34401A |
| `oscilloscopes_series` | Oscilloscopes | Tektronix 5 Series MSO, Rigol DS1000Z, Siglent SDS HD |
| `electronic_loads_series` | Electronic loads | Chroma 6330A, Keysight EL4900, Siglent SDL1000X-E |

```json
{
  "instrument_library": {
    "power_supplies_series": [],
    "dataloggers_series": [],
    "switch_units_series": [],
    "datalogger_modules": [],
    "multimeters_series": [],
    "oscilloscopes_series": [],
    "electronic_loads_series": []
  }
}
```

## Standard structure: Series → Models

All categories (except the dataloggers, see below) follow the same two-level scheme: a **series** that groups instruments sharing the same set of SCPI commands, and a list of **models** that specify the hardware variants.

### The series

```json
{
  "series_id": "OWON_ODP_Series",
  "series_name": "OWON ODP Series Programmable DC Power Supplies",
  "common_scpi_commands": { ... },
  "models": [ ... ]
}
```

| Field | Type | Description |
|---|---|---|
| `series_id` | string | Unique identifier of the series |
| `series_name` | string | Readable name of the series |
| `common_scpi_commands` | object | SCPI commands shared by all models of the series |
| `models` | array | List of the models of the series |

### The model

```json
{
  "id": "PSU_OWON_ODP3033",
  "name": "OWON ODP3033",
  "manufacturer": "OWON Technology",
  "model": "ODP3033",
  "documentation_path": "docs/OWON/ODP_Series/ODP_Series_Power_Supply_Programming_Manual.pdf",
  "interface": { ... },
  "capabilities": { ... },
  "scpi_commands": {},
  "experimental": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier, format `{TYPE}_{MANUFACTURER}_{MODEL}` |
| `name` | string | yes | Commercial name |
| `manufacturer` | string | yes | Manufacturer |
| `model` | string | yes | Model code |
| `documentation_path` | string | yes | Path of the PDF manual |
| `interface` | object | yes | Supported connection types |
| `capabilities` | object | yes | Physical limits and features |
| `scpi_commands` | object | no | Model-specific commands: they replace, remove (`null`) or modify (`{"patch": {...}}`) those of the series, see `COMMAND_NAMES.md` section 7 |
| `experimental` | bool | yes | `true` = not yet validated on real hardware |

## The `interface` block

Defines the supported communication protocols. Each connection type is an object with:

| Field | Description |
|---|---|
| `type` | Protocol: `LXI`, `USB-TMC`, `SERIAL`, `GPIB` |
| `visa_resource_id_template` | VISA identification template |
| `address_format_example` | Example of the pyvisa connection string |

```json
"interface": {
  "supported_connection_types": [
    {
      "type": "LXI",
      "visa_resource_id_template": "LXI_PSU_{unique_id}",
      "address_format_example": "TCPIP0::{IP_ADDRESS}::inst0::INSTR"
    },
    {
      "type": "USB-TMC",
      "visa_resource_id_template": "USB_PSU_{serial_number}",
      "address_format_example": "USB0::{VENDOR_ID}::{PRODUCT_ID}::{SERIAL_NUMBER}::INSTR"
    },
    {
      "type": "SERIAL",
      "visa_resource_id_template": "SERIAL_PSU_{unique_id}",
      "address_format_example": "ASRL{COM_PORT}::INSTR"
    }
  ]
}
```

## The `capabilities` block

Contains the physical limits of the instrument, used by the driver to validate user input before sending commands. The fields vary by category:

**Power supplies** — channels with limits per output:
```json
"capabilities": {
  "number_of_channels": 3,
  "channels": [
    {
      "channel_id": "1",
      "label": "CH1 (30V/3A)",
      "voltage_output": { "min": 0, "max": 30 },
      "current_output": { "min": 0, "max": 3 }
    }
  ],
  "trigger_output": false
}
```

**Oscilloscopes** — acquisition specifications:
```json
"capabilities": {
  "number_of_channels": 4,
  "bandwidth_mhz": 50,
  "sample_rate_gsa_s": 1.0,
  "memory_depth_mpts": 12,
  "measurement_types": ["VMAX", "VMIN", "VPP", "RMS", "FREQ"],
  "trigger_modes": ["EDGE", "PULS", "VIDeo"],
  "waveform_formats": ["ASCii", "BYTE", "WORD"],
  "channels": [
    { "channel_id": "CHAN1", "label": "Channel 1" }
  ]
}
```

**Electronic loads** — operating modes and power limits:
```json
"capabilities": {
  "number_of_channels": 1,
  "operating_modes": ["CC", "CV", "CR", "CP"],
  "max_voltage_v": 30,
  "max_current_a": 30,
  "max_power_w": 150
}
```

## The `common_scpi_commands` block

This is the heart of the rule engine. Each command is an object with three phases: **write** (`set`), **read** (`query`) and **validation** (`parameters`).

### Write phase (`set`)

```json
"set_voltage": {
  "description": "set voltage",
  "set": {
    "syntax": "VOLT {value}",
    "args": ["value"]
  },
  "query": null,
  "parameters": {
    "value": { "type": "float" }
  }
}
```

| Field | Description |
|---|---|
| `syntax` | Raw SCPI string with `{name}` placeholders |
| `args` | Ordered list of the variables to inject into the string |

### Read phase (`query`)

```json
"read_voltage": {
  "description": "read voltage",
  "set": null,
  "query": {
    "syntax": "MEAS:VOLT?",
    "return_type": "float"
  }
}
```

The `return_type` field tells the driver how to convert the response:

| `return_type` | Conversion |
|---|---|
| `string` | No conversion |
| `int` | Cast to integer |
| `float` | Cast to decimal number |
| `binary` | Block read (e.g. waveforms) |

### Validation phase (`parameters`)

| Field | Description |
|---|---|
| `type` | Data type: `int`, `float`, `string` |
| `values` | Fixed list of allowed values (static constraint) |

```json
"parameters": {
  "source": {
    "type": "string",
    "values": ["IMMediate", "BUS", "EXTernal", "TIMer", "MANual"]
  }
}
```

A command can be `set` only (`query: null`), `query` only (`set: null`), or both.

## Special structure: the Data Loggers

The dataloggers are split into **two separate categories**: the mainframe (`dataloggers_series`) and the interchangeable cards (`datalogger_modules`).

### The mainframe (`dataloggers_series`)

It follows the standard series → models structure. The mainframe model declares the slots and the compatible modules:

```json
"capabilities": {
  "number_of_slots": 3,
  "compatible_modules": ["34901A", "34902A", "34908A"]
}
```

The SCPI commands that operate on channels use the Keysight **3-digit** range format (slot + channel, Keysight 3497X for the 34970A and 34972A): `"101:120"` → `(@101:120)`:
```json
"select_channels": {
  "set": {
    "syntax": "ROUT:SCAN (@{channels})",
    "args": ["channels"]
  },
  "parameters": {
    "channels": { "type": "string" }
  }
}
```

> **Agilent 3499A exception** (category `switch_units_series`, see below): it uses the `@snn` format (slot + 2-digit channel, e.g. `(@101)`, `(@100:107)`). The value of `capabilities.channels` is a string like `"100:107"` — the `@` is part of the SCPI syntax (`(@{channels})`), not of the channel ID. The 3499A is also a switching mainframe **without a measurement engine** (no `MEAS?`/`FETCh?`/`READ?`).

### The cards (`datalogger_modules`)

Flat array of interchangeable modules, **without** SCPI commands of their own (they work through the mainframe commands). All physical limits are inside `capabilities`:

```json
{
  "id": "34901A",
  "name": "Keysight 34901A 20-Channel Multiplexer Module",
  "capabilities": {
    "number_of_channels": 20,
    "measurement_types": ["VOLT:DC", "VOLT:AC", "TEMP"],
    "max_voltage": 300.0,
    "speed": 60
  },
  "documentation_path": "docs/Keysight/3497X_Series/34901A_manual.pdf"
}
```

| Field | Description |
|---|---|
| `id` | Module identifier (e.g. `34901A`) |
| `name` | Full name of the module |
| `capabilities.number_of_channels` | Number of channels |
| `capabilities.measurement_types` | Supported measurement types (e.g. `VOLT:DC`, `TEMP`) |
| `capabilities.max_voltage` | Maximum voltage |
| `capabilities.speed` | Scan speed (channels/s) |
| `not_enabled` | `true` = module not yet defined/fully described |
| `documentation_path` | Percorso del manuale PDF |

Modules that are not yet enabled (e.g. switches and RF matrices) still keep the minimal structure:

```json
{
  "id": "34903A",
  "name": "Keysight 34903A 20-Channel Actuator/GP Switch Module",
  "not_enabled": true,
  "capabilities": {
    "number_of_channels": 20
  }
}
```

## Naming conventions

### Model IDs

IDs follow `{TYPE}_{MANUFACTURER}_{MODEL}`:

| Type | Prefix | Example |
|---|---|---|
| Power supply | `PSU_` | `PSU_OWON_ODP3033` |
| Data logger | `DL_` | `DL_Keysight_34972A` |
| Multimeter | `MTR_` | `MTR_Agilent_34401A` |
| Oscilloscope | `OSC_` | `OSC_Tek_MSO54` |
| Electronic load | `EL_` | `EL_Chroma_6330A` |

### Channel IDs

**They are not standardized** — they depend on the manufacturer and must be checked in the series:

| Manufacturer | Channel ID | Example |
|---|---|---|
| OWON | Numeric | `1`, `2`, `3` |
| Keysight (PSU) | `CH` + number | `CH1`, `CH2`, `CH3` |
| Keysight (datalogger) | String range (slot + 3-digit channel) | `"101:120"` → `(@101:120)` |
| Agilent 3499A | `@snn` format (slot + 2-digit channel) | `"100:107"`, `"101"` — rendered `(@100:107)` |
| HP/Agilent multimeters | Single channel (no channel parameter) | — |
| R&S | `OUT` + number | `OUT1`..`OUT4` |
| Tektronix | `CH` + number | `CH1`..`CH8` |
| Siglent | `C` + number | `C1`..`C4` |
| TDK-Lambda | `CH1` (single channel) | `CH1` |

## The `experimental` flag

- Most models have `"experimental": true` = **not yet validated on real hardware** — the SCPI commands may differ from the manual.
- 87 of the 91 models have `"experimental": true`. The four without it are the three **Siglent SDS800X HD** models (`OSC_Siglent_SDS804X_HD`, `OSC_Siglent_SDS814X_HD`, `OSC_Siglent_SDS824X_HD`, partially tested) and the **Agilent 34970A** (`DL_Agilent_34970A`, tested on a real instrument).

### Tested model per series

| Series | Tested model |
|---|---|
| OWON ODP | X |
| Keysight E36300 | X |
| TDK-Lambda GEN | X |
| R&S HMP | X |
| HP E3631A | X |
| Keysight 3497X (34970A, 34972A) | X |
| Agilent 3499A | X |
| Datalogger modules (34901A..34908A) | X |
| HP 3478A | X |
| Agilent 34401A | X |
| Tektronix 5 Series MSO | X |
| Rigol DS1000Z | X |
| **Siglent SDS800X HD** | **SDS824X HD** |
| Siglent SDS1000X/SDS2000X HD | X |
| Chroma 6330A | X |
| Keysight EL4900 | X |
| Siglent SDL1000X | X |

`X` = no model of the series validated on real hardware (`experimental: true`).

## Documentation

- **`docs/COMMANDS.md` — reference of the canonical call names** of the SCPI commands (key, description, syntax per series). Use these names to call the instruments: same operation = same name.
- The PDF manuals live in `docs/{Manufacturer}/{Series}/`. Note: the folder of the Siglent manuals uses the spelling **Sigilent** (consistent with the references in the JSON).

All `documentation_path` values referenced by the JSON now point to PDFs that really exist in the repository. The manual `docs/Tektronix/4-5-6-Series-MSO_Programmer_077189804.pdf` is present as an additional secondary reference.

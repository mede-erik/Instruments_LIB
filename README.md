# Instruments_LIB

Libreria JSON data-only che funge da **motore di regole** (Rule Engine) per un driver Python SCPI. Non contiene codice: il file `instruments_lib.json` descrive serie, modelli, comandi SCPI, interfacce fisiche e limiti hardware di ogni strumento, permettendo al driver di validare i dati, formattare le richieste, gestire le connessioni e interpretare le risposte in modo dinamico.

## Struttura del file

Il file `instruments_lib.json` è un unico oggetto con la chiave `instrument_library`, contenente 6 categorie:

| Chiave | Categoria | Esempi |
|---|---|---|
| `power_supplies_series` | Alimentatori | OWON ODP, Keysight E36300, TDK-Lambda GEN, R&S HMP, HP E3631A |
| `dataloggers_series` | Data logger (mainframe) | Keysight 34970A/34972A, Agilent 3499A |
| `datalogger_modules` | Datalogger card (moduli) | Keysight 34901A, 34902A, 34908A |
| `multimeters_series` | Multimetri | HP 3478A, Agilent 34401A |
| `oscilloscopes_series` | Oscilloscopi | Tektronix 5 Series MSO, Rigol DS1000Z, Siglent SDS HD |
| `electronic_loads_series` | Carichi elettronici | Chroma 6330A, Keysight EL4900, Siglent SDL1000X-E |

```json
{
  "instrument_library": {
    "power_supplies_series": [],
    "dataloggers_series": [],
    "datalogger_modules": [],
    "multimeters_series": [],
    "oscilloscopes_series": [],
    "electronic_loads_series": []
  }
}
```

## Struttura standard: Serie → Modelli

Tutte le categorie (eccetto i datalogger, vedi sotto) seguono lo stesso schema a due livelli: una **serie** che raggruppa strumenti con lo stesso set di comandi SCPI, e una lista di **modelli** che specificano le varianti hardware.

### La serie

```json
{
  "series_id": "OWON_ODP_Series",
  "series_name": "OWON ODP Series Programmable DC Power Supplies",
  "common_scpi_commands": { ... },
  "models": [ ... ]
}
```

| Campo | Tipo | Descrizione |
|---|---|---|
| `series_id` | string | Identificatore univoco della serie |
| `series_name` | string | Nome leggibile della serie |
| `common_scpi_commands` | object | Comandi SCPI condivisi da tutti i modelli della serie |
| `models` | array | Lista dei modelli della serie |

### Il modello

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

| Campo | Tipo | Obbligatorio | Descrizione |
|---|---|---|---|
| `id` | string | sì | Identificatore univoco, formato `{TYPE}_{MANUFACTURER}_{MODEL}` |
| `name` | string | sì | Nome commerciale |
| `manufacturer` | string | sì | Produttore |
| `model` | string | sì | Codice modello |
| `documentation_path` | string | sì | Percorso del manuale PDF |
| `interface` | object | sì | Tipi di connessione supportati |
| `capabilities` | object | sì | Limiti fisici e funzionalità |
| `scpi_commands` | object | no | Comandi specifici del modello (sovrascrivono/estendono la serie) |
| `experimental` | bool | sì | `true` = non ancora validato su hardware reale |

## Il blocco `interface`

Definisce i protocolli di comunicazione supportati. Ogni tipo di connessione è un oggetto con:

| Campo | Descrizione |
|---|---|
| `type` | Protocollo: `LXI`, `USB-TMC`, `SERIAL`, `GPIB` |
| `visa_resource_id_template` | Template di identificazione VISA |
| `address_format_example` | Esempio della stringa di connessione pyvisa |

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

## Il blocco `capabilities`

Contiene i limiti fisici dello strumento, usati dal driver per validare l'input dell'utente prima di inviare comandi. I campi variano per categoria:

**Alimentatori** — canali con limiti per uscita:
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

**Oscilloscopi** — specifiche di acquisizione:
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

**Carichi elettronici** — modalità operative e limiti di potenza:
```json
"capabilities": {
  "number_of_channels": 1,
  "operating_modes": ["CC", "CV", "CR", "CP"],
  "max_voltage_v": 30,
  "max_current_a": 30,
  "max_power_w": 150
}
```

## Il blocco `common_scpi_commands`

È il cuore del motore di regole. Ogni comando è un oggetto con tre fasi: **scrittura** (`set`), **lettura** (`query`) e **validazione** (`parameters`).

### Fase di scrittura (`set`)

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

| Campo | Descrizione |
|---|---|
| `syntax` | Stringa SCPI grezza con placeholder `{nome}` |
| `args` | Elenco ordinato delle variabili da iniettare nella stringa |

### Fase di lettura (`query`)

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

Il campo `return_type` istruisce il driver su come convertire la risposta:

| `return_type` | Conversione |
|---|---|
| `string` | Nessuna conversione |
| `int` | Cast a intero |
| `float` | Cast a numero decimale |
| `binary` | Lettura in blocchi (es. forme d'onda) |

### Fase di validazione (`parameters`)

| Campo | Descrizione |
|---|---|
| `type` | Tipo del dato: `int`, `float`, `string` |
| `values` | Elenco fisso di valori ammessi (vincolo statico) |

```json
"parameters": {
  "source": {
    "type": "string",
    "values": ["IMMediate", "BUS", "EXTernal", "TIMer", "MANual"]
  }
}
```

Un comando può essere solo `set` (`query: null`), solo `query` (`set: null`), o entrambi.

## Struttura speciale: i Data Logger

I datalogger sono divisi in **due categorie separate**: il mainframe (`dataloggers_series`) e le card intercambiabili (`datalogger_modules`).

### Il mainframe (`dataloggers_series`)

Segue la struttura standard serie → modelli. Il modello del mainframe dichiara gli slot e i moduli compatibili:

```json
"capabilities": {
  "number_of_slots": 3,
  "compatible_modules": ["34901A", "34902A", "34908A"]
}
```

I comandi SCPI che operano sui canali usano il formato a range Keysight a **3 cifre** (slot + canale, K. 3497X per 34970A e 34972A): `"101:120"` → `(@101:120)`:
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

> **Eccezione Agilent 3499A**: usa il formato `@snn` (slot + canale a 2 cifre, es. `(@101)`, `(@100:107)`). Il valore di `capabilities.channels` è una stringa tipo `"100:107"` — la `@` fa parte della sintassi SCPI (`(@{channels})`), non dell'ID canale. Il 3499A è inoltre un mainframe di switching **senza motore di misura** (niente `MEAS?`/`FETCh?`/`READ?`).

### Le card (`datalogger_modules`)

Array piatto di moduli intercambiabili, **senza** comandi SCPI propri (operano tramite i comandi del mainframe). Tutti i limiti fisici stanno dentro `capabilities`:

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

| Campo | Descrizione |
|---|---|
| `id` | Identificatore del modulo (es. `34901A`) |
| `name` | Nome completo del modulo |
| `capabilities.number_of_channels` | Numero di canali |
| `capabilities.measurement_types` | Tipi di misura supportati (es. `VOLT:DC`, `TEMP`) |
| `capabilities.max_voltage` | Tensione massima |
| `capabilities.speed` | Velocità di scansione (canali/s) |
| `not_enabled` | `true` = modulo non ancora definito/completamente descritto |
| `documentation_path` | Percorso del manuale PDF |

I moduli non ancora abilitati (es. switch e matrici RF) mantengono comunque la struttura minima:

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

## Convenzioni di naming

### ID dei modelli

Gli ID seguono `{TYPE}_{MANUFACTURER}_{MODEL}`:

| Tipo | Prefisso | Esempio |
|---|---|---|
| Alimentatore | `PSU_` | `PSU_OWON_ODP3033` |
| Data logger | `DL_` | `DL_Keysight_34972A` |
| Multimetro | `MTR_` | `MTR_Agilent_34401A` |
| Oscilloscopio | `OSC_` | `OSC_Tek_MSO54` |
| Carico elettronico | `EL_` | `EL_Chroma_6330A` |

### ID dei canali

**Non sono standardizzati** — dipendono dal produttore e vanno verificati nella serie:

| Produttore | ID canale | Esempio |
|---|---|---|
| OWON | Numerico | `1`, `2`, `3` |
| Keysight (PSU) | `CH` + numero | `CH1`, `CH2`, `CH3` |
| Keysight (datalogger) | Range stringa (slot + canale 3 cifre) | `"101:120"` → `(@101:120)` |
| Agilent 3499A | Formato `@snn` (slot + canale a 2 cifre) | `"100:107"`, `"101"` — renderizzato `(@100:107)` |
| HP/Agilent multimetri | Canale singolo (nessun parametro canale) | — |
| R&S | `OUT` + numero | `OUT1`..`OUT4` |
| Tektronix | `CH` + numero | `CH1`..`CH8` |
| Siglent | `C` + numero | `C1`..`C4` |
| TDK-Lambda | `CH1` (canale singolo) | `CH1` |

## Flag `experimental`

- La maggior parte dei modelli ha `"experimental": true` = **non ancora validati su hardware reale** — i comandi SCPI possono differire dal manuale.
- Tutti i modelli hanno `"experimental": true` (non ancora validati su hardware reale), eccetto la famiglia **Siglent SDS800X HD** (`OSC_Siglent_SDS804X_HD`, `OSC_Siglent_SDS814X_HD`, `OSC_Siglent_SDS824X_HD`, testata parzialmente).

### Modello testato per serie

| Serie | Modello testato |
|---|---|
| OWON ODP | X |
| Keysight E36300 | X |
| TDK-Lambda GEN | X |
| R&S HMP | X |
| HP E3631A | X |
| Keysight 3497X (34970A, 34972A) | X |
| Agilent 3499A | X |
| Moduli datalogger (34901A..34908A) | X |
| HP 3478A | X |
| Agilent 34401A | X |
| Tektronix 5 Series MSO | X |
| Rigol DS1000Z | X |
| **Siglent SDS800X HD** | **SDS824X HD** |
| Siglent SDS1000X/SDS2000X HD | X |
| Chroma 6330A | X |
| Keysight EL4900 | X |
| Siglent SDL1000X | X |

`X` = nessun modello della serie validato su hardware reale (`experimental: true`).

## Documentazione

- **`docs/COMMANDS.md` — riferimento dei nomi di richiamo canonici** dei comandi SCPI (chiave, descrizione, sintassi per serie). Usare questi nomi per chiamare gli strumenti: stessa operazione = stesso nome.
- I manuali PDF vivono in `docs/{Manufacturer}/{Series}/`. Attenzione: la cartella dei manuali Siglent usa l'ortografia **Sigilent** (coerente con i riferimenti nel JSON).

Tutti i percorsi `documentation_path` referenziati dal JSON ora puntano a PDF realmente presenti nel repo. Il manuale `docs/Tektronix/4-5-6-Series-MSO_Programmer_077189804.pdf` è presente come riferimento secondario aggiuntivo.

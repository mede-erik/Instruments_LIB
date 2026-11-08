# Tests

Script to test the SCPI commands defined in `instruments_lib.json` against real instruments, through PyVISA with the `pyvisa-py` backend (NI-VISA does not need to be installed).

## Installation

```bash
pip install -r Tests/requirements.txt
```

## Quick start

```bash
# List the models available in the database
python3 Tests/test_instrument.py --list-models

# Test with a forced model (recommended)
python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --visa "USB0::2363::4416::SERIAL::INSTR"

# Auto-identification of the model from *IDN?
python3 Tests/test_instrument.py --visa "TCPIP0::192.168.1.50::inst0::INSTR"

# Connection check only
python3 Tests/test_instrument.py --visa "TCPIP0::192.168.1.50::inst0::INSTR" --idn-only

# Preview of the commands without connecting
python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --dry-run
```

## Main options

| Option | Description |
|---|---|
| `--model ID` | model id in the JSON (e.g. `PSU_OWON_ODP3033`) |
| `--visa ADDR` | VISA address: `USB0::VID::PID::SN::INSTR`, `TCPIP0::IP::inst0::INSTR`, `GPIB0::5::INSTR`, `ASRL/dev/ttyUSB0::INSTR` |
| `--dangerous` | also runs the **write** commands (`set_*`, `output_on`, `load_on`, `*RST`...) |
| `--channel N` | replaces the default channel (`1`/`CH1`/`C1`/`OUT1`...) in parametrized commands |
| `--only KEY` | runs only the given commands (repeatable) |
| `--exclude KEY` | skips the given commands (repeatable) |
| `--timeout MS` | query timeout (default 3000) |
| `--delay S` | pause between commands (default 0.2) |
| `--baud N` | baud rate for serial (default 9600) |
| `--no-error-queue` | does not query the error queue after every command |
| `--report FILE.json` | saves the results as JSON |
| `-v` | also shows the PASS commands |

## Behaviour

1. **Loads** `instruments_lib.json` and resolves the model (forced with `--model` or deduced from `*IDN?`).
2. **Identifies** the instrument with `*IDN?` and checks that it matches the model.
3. **Runs** all the commands of the series (`common_scpi_commands` + the model's `scpi_commands`):
   - reads (`query_*`, `read_*`, `*STB?`, `*ESR?`, `error_query`...) always;
   - writes (`set_*`, `output_on/off`, `load_on/off`, reset...) **only with `--dangerous`**.
4. The command parameters are filled in automatically: channel = first channel of the model, enum = first allowed value, float = `0.1`, int = `1`. If a parameter cannot be handled the case is marked `SKIP`.
5. **Validates** every response (type expected from `return_type`) and queries the instrument's **error queue** after every query to detect wrong syntax.
6. Final **summary** with counts and exit code: `0` = ok, `1` = at least one FAIL/TIMEOUT.

## Result states

| State | Meaning |
|---|---|
| `PASS` | command ok, valid response, clean error queue |
| `FAIL` | invalid response or error reported by the instrument |
| `WARN` | error queue cannot be queried (instrument without `SYST:ERR?`/`EVMsg?`) |
| `SKIP` | unhandled parameter or write command without `--dangerous` |
| `TIMEOUT` | no response within the time given by `--timeout` (useful to find unrecognised syntax) |

## Safety notes

- **Never use `--dangerous`** with instruments connected to loads, DUTs or powered circuits: the write commands change the real state of the instrument.
- Before a real session, always do a trial with `--dry-run` to see what would be sent.
- The values written are minimal and should not cause damage, but this is not a guarantee: `--channel` and `--only` let you limit the scope.
- Power supplies: never connect the output to anything during the tests.

# Tests

Script per testare i comandi SCPI definiti in `instruments_lib.json` contro strumenti reali, via PyVISA con il backend `pyvisa-py` (non serve NI-VISA installato).

## Installazione

```bash
pip install -r Tests/requirements.txt
```

## Uso rapido

```bash
# Elenca i modelli disponibili nel database
python3 Tests/test_instrument.py --list-models

# Test con modello forzato (consigliato)
python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --visa "USB0::2363::4416::SERIAL::INSTR"

# Auto-identificazione del modello da *IDN?
python3 Tests/test_instrument.py --visa "TCPIP0::192.168.1.50::inst0::INSTR"

# Solo verifica connessione
python3 Tests/test_instrument.py --visa "TCPIP0::192.168.1.50::inst0::INSTR" --idn-only

# Anteprima dei comandi senza connettersi
python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --dry-run
```

## Opzioni principali

| Opzione | Descrizione |
|---|---|
| `--model ID` | id del modello nel JSON (es. `PSU_OWON_ODP3033`) |
| `--visa ADDR` | indirizzo VISA: `USB0::VID::PID::SN::INSTR`, `TCPIP0::IP::inst0::INSTR`, `GPIB0::5::INSTR`, `ASRL/dev/ttyUSB0::INSTR` |
| `--dangerous` | esegue anche i comandi di **scrittura** (`set_*`, `output_on`, `load_on`, `*RST`...) |
| `--channel N` | sostituisce il canale di default (`1`/`CH1`/`C1`/`OUT1`...) nei comandi parametrizzati |
| `--only KEY` | esegue solo i comandi indicati (ripetibile) |
| `--exclude KEY` | salta i comandi indicati (ripetibile) |
| `--timeout MS` | timeout query (default 3000) |
| `--delay S` | pausa tra i comandi (default 0.2) |
| `--baud N` | baud rate per seriale (default 9600) |
| `--no-error-queue` | non interroga la coda errori dopo ogni comando |
| `--report FILE.json` | salva i risultati in JSON |
| `-v` | mostra anche i comandi PASS |

## Comportamento

1. **Carica** `instruments_lib.json` e risolve il modello (forzato con `--model` oppure dedotto da `*IDN?`).
2. **Identifica** lo strumento con `*IDN?` e verifica la coerenza col modello.
3. **Esegue** tutti i comandi della serie (`common_scpi_commands` + `scpi_commands` del modello):
   - letture (`query_*`, `read_*`, `*STB?`, `*ESR?`, `error_query`...) sempre;
   - scritture (`set_*`, `output_on/off`, `load_on/off`, reset...) **solo con `--dangerous`**.
4. I parametri dei comandi vengono riempiti automaticamente: canale = primo canale del modello, enum = primo valore ammesso, float = `0.1`, int = `1`. Se un parametro non è gestibile il caso è marcato `SKIP`.
5. **Valida** ogni risposta (tipo atteso da `return_type`) e interroga la **coda errori** dello strumento dopo ogni query per individuare sintassi errate.
6. **Riepilogo** finale con conteggi e exit code: `0` = ok, `1` = almeno un FAIL/TIMEOUT.

## Stati dei risultati

| Stato | Significato |
|---|---|
| `PASS` | comando ok, risposta valida, coda errori pulita |
| `FAIL` | risposta non valida o errore segnalato dallo strumento |
| `WARN` | coda errori non interrogabile (strumento senza `SYST:ERR?`/`EVMsg?`) |
| `SKIP` | parametro non gestito o comando di scrittura senza `--dangerous` |
| `TIMEOUT` | nessuna risposta nel tempo indicato da `--timeout` (utile per capire sintassi non riconosciute) |

## Note di sicurezza

- **Mai usare `--dangerous`** con strumenti connessi a carichi, DUT o circuiti alimentati: i comandi di scrittura cambiano lo stato reale dello strumento.
- Prima di una sessione vera, fare sempre una prova con `--dry-run` per vedere cosa verrebbe inviato.
- I valori scritti sono minimi e non dovrebbero causare danni, ma non sono una garanzia: `--channel` e `--only` permettono di limitare il raggio d'azione.
- Alimentatori: non connettere mai l'uscita a nulla durante i test.

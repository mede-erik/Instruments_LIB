# Testing the instrument library

This guide explains how anyone can check the library (`instruments_lib.json` and `schema/`) against a **real instrument**, and how to report what was found. You do not need to know SCPI: the test tool uses the same *logical calls* as the application and shows the exact commands it sends.

Three levels, from safest to most invasive. Do them in order and stop at the level your situation allows.

| Level | Needs hardware | Changes the instrument | What it proves |
|---|---|---|---|
| 1. Offline checks | no | no | the library files are consistent with the schemas and the planner |
| 2. Dry run | no | no | the commands a call would send (read them against the manual) |
| 3. Live test | yes | read-only first, then optionally writes | the commands work and the answers are understood |

## 1. Setup

You need the application repository (it contains the test tool) with the library as its `Instruments_LIB` submodule.

```bash
git clone --recurse-submodules https://github.com/mede-erik/Open-Lab-Automation
cd Open-Lab-Automation
pip install -r requirements.txt
```

To test a library branch that is not merged yet:

```bash
cd Instruments_LIB
git fetch
git checkout <branch>
git pull
cd ..
```

The tool prints the library file it uses when it starts (`Library: ...`). **Check that line**: an old checkout of the submodule is the most common reason for a missing model or call.

Requirements: a recent Python 3; `pyvisa`, `pyvisa-py` and `pyserial` (installed by `requirements.txt`). A vendor VISA (NI-VISA, Keysight) is optional; without it the tool uses `pyvisa-py`.

## 2. Level 1: offline checks

Run these after any change to the library or the schemas. They need no instrument.

```bash
# in Instruments_LIB
python3 Tests/check_conformance.py --strict   # library against schema/*.json, must print 0 errors, 0 todo
python3 schema/generate_command_names.py --check   # COMMAND_NAMES.md is up to date

# in Open-Lab-Automation
python3 -m pytest -q tests                    # planner, parsers, tester, instrument handle
```

`check_conformance.py` reports:

* **ERROR**: a mandatory call is missing, an argument name is not in the schema, or a call has the wrong half (set/query).
* **TODO**: the library still gives vendor values where the schema defines logical ones (it needs a `map`), or a call is not in the schema. `--strict` makes TODO fail too.

## 3. Level 2: dry run (no hardware)

Shows the commands a call would send, so you can compare them with the programming manual.

```bash
python3 scripts/dry_run_call.py --model OSC_Siglent_SDS824X_HD --call set_channel_scale \
    --arg channel_number=1 --arg value=0.5

# translate the answer of a query (--answer is what the instrument would send)
python3 scripts/dry_run_call.py --model OSC_Tek_MSO54 --call query_trigger_status --answer TRIGGER

# every call of a project file
python3 scripts/dry_run_call.py --model OSC_Rigol_DS1054Z --was project.was
```

Model ids are in the library (`id` of each model) and listed by the interactive tool.

## 4. Level 3: live test with the interactive tool

```bash
python3 scripts/instrument_shell.py          # real instrument
python3 scripts/instrument_shell.py --sim    # same menus with a fake instrument (to learn the tool)
```

The tool asks for the **category**, the **model** and the **interface**, then the connection address.

### Connection examples

| Interface | Address example | Notes |
|---|---|---|
| LAN (LXI / VXI-11) | `TCPIP0::192.168.1.222::inst0::INSTR` | the instrument and the PC on the same network |
| LAN raw socket | the tool asks for the host (`192.168.1.222`) and the port (default from the library, for example 5025) | |
| USB-TMC | `USB0::<vendor>::<product>::<serial>::INSTR` | list the resources with `python3 -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"` |
| RS-232 | VISA address of the port: `ASRL/dev/ttyUSB0::INSTR` (Linux, pyvisa-py), `ASRL3::INSTR` (Windows, NI-VISA, port number) | see below |

### RS-232 (serial) tips

* The settings (baud rate, data bits, parity, stop bits, flow control, terminators) come from the library when the manual gives them. The instrument's own menu may differ: set it to the same values, or change them in the tool with the `serial` command. Many instruments ship with other defaults than the manual's.
* Most benchtop instruments are **DTE** and need a **null-modem** cable (crossed TX/RX). A straight cable gives timeouts on every query. If every query times out, try `loopback` (join pins 2 and 3 of the adapter: `hello` must come back) to check the adapter, then `probe` to search the baud rate and flow control the instrument answers to.
* With NI-VISA the serial ports are numbered `ASRL1`, `ASRL2`; on Linux the tool uses `pyvisa-py` and addresses like `ASRL/dev/ttyUSB0::INSTR`.
* Put the instrument in remote mode if the manual says so (the 34970A needs `SYSTem:REMote`; the library call is `set_remote`).

### Commands inside the tool

| Command | What it does |
|---|---|
| `calls` | the calls this model defines (`[M]` mandatory, `[O]` optional) |
| `missing` | mandatory calls the model does not define |
| `plan NAME [a=v ...]` | the commands a call would send, **without sending them** |
| `call NAME [a=v ...]` | run a call; missing arguments are asked |
| `readback NAME [a=v]` | read back the value of a `set_...` call |
| `test` | run every query that needs no argument (read-only) |
| `test writes` | also the actions that need no argument, and `self_test` (**changes the instrument**, asks to confirm) |
| `test all` | also list the calls that were skipped, and why |
| `raw TEXT` | send a text as it is and show the answer (debugging) |
| `save FILE.csv [N]`, `stats` | save / summarise the last waveform |
| `serial`, `probe`, `loopback` | RS-232 settings and diagnostics |
| `reconnect`, `quit` | |

The up and down arrows recall earlier commands (also from earlier sessions, kept in `~/.ola_instrument_shell_history`) and Tab completes command and call names. On Windows this needs `pyreadline3` (in `requirements.txt`).

Every call shows `commands:` (what was sent) and `result:` (what the library translated the answer into).

### Recommended procedure

1. `missing`: the list must be empty, otherwise the model lacks mandatory calls (report it).
2. `call error_query` and `call clear_status`: confirms that the link works and the instrument reports errors.
3. `test`: every read-only call. Read the **commands** column against the manual and check each **result** with the instrument's display or settings. A call that fails is a library problem or an unsupported feature, not necessarily a defect of your instrument.
4. Compare values with what you see on the instrument (for example `query_timebase_scale` against the screen). A number that is consistent but wrong (wrong unit, a factor 2 or 256) is the typical library error and is not detected by `check_conformance.py`.
5. Only if you accept that settings change: set a value and read it back, for example
   ```
   call set_channel_scale channel_number=1 value=0.5
   readback set_channel_scale channel_number=1
   ```
   then `test writes` for the actions.
6. For calls with a translation (`map`), try every logical value the schema lists and check the instrument really changed.

### Safety

* `test writes` and `call set_...` **change the instrument**. Do not run them on an instrument used in a running experiment.
* **Power supplies and electronic loads**: disconnect the load (or the device under test) before any write test. Output-enable, setpoint and mode changes are real. Start with the output off and low limits.
* **Switch units / relays**: disconnect the signals before switching tests.
* `self_test` can take about a minute and may reset the instrument; it is excluded from `test` and runs only with `test writes`.

## 5. Checklists by instrument type

Each list gives a safe order. Replace the channel numbers and values with ones that suit your setup. `plan` shows the commands without sending them, so use it first when a value could be dangerous.

### Oscilloscope

1. `call error_query`, `call clear_status`, `test` (read-only).
2. Horizontal and vertical settings: `call set_timebase_scale value=1e-3`, `readback set_timebase_scale`, then the same for `set_channel_scale channel_number=1`, `set_channel_offset`, `set_channel_coupling` (try every logical value: `DC`, `AC`, `GND`).
3. Trigger: `set_trigger_source`, `set_trigger_level`, `set_trigger_slope` (`RISE`, `FALL`, `EITHER`), `set_trigger_mode` (`AUTO`, `NORMAL`, `SINGLE`), then `call query_trigger_status` while the instrument is running, stopped and after `call force_trigger`. A state the library does not know gives `CALL-005`: report its exact text.
4. Waveform transfer, with the probe-compensation signal (about 3 V peak-peak, 1 kHz) connected to channel 1 and the acquisition stopped (`call stop_acquisition`) so that every read comes from the same capture:
   ```
   call read_waveform channel_number=1
   stats
   save wave.csv 5000
   ```
   Check against the instrument: peak-peak voltage (about 3 V), the time span (`points` x `sample_interval` must equal 10 x the timebase when the whole screen is transferred), and the `vertical_gain` printed against `call query_channel_scale channel_number=1`. A peak-peak value wrong by a constant factor (2, 256, ...) means a wrong scale in the parser or in the library entry.
5. Long memories: if the instrument can transfer fewer points than its memory depth, read the blocks with `start`, for example `call read_waveform channel_number=1 start=5000000`, and check that the time axis of the second block continues after the first. The 16-bit format is `bits=16` (default is 8).

### Power supply

Disconnect the load first. Keep the output off while setting values.

1. `call identification_query`, `call output_state_query` (must be off), `test`.
2. `call set_voltage channel_number=1 value=1.0`, `call set_current channel_number=1 value=0.1`, `readback` both.
3. `call output_on`, `call read_voltage`, `call read_current`, `call output_off`. Compare `read_voltage` with the display and with an external multimeter if you have one.
4. Several channels: repeat for each channel number the model has, and check that the right channel changed on the front panel.

### Electronic load

Connect a power source that suits the load, with current limited, only for the steps that need input.

1. `test`, `call query_mode`, `call query_input_state` (must be off).
2. `call set_mode mode=CC` and each other mode of the schema (`CV`, `CR`, `CP`); a mode the model does not support must answer `CALL-002`, not change the instrument.
3. `call set_current_level value=0.1`, `call load_on`, `call read_voltage`, `call read_current`, `call read_power`, `call load_off`.
4. Slew rate and dynamic (pulse) calls only after the static ones work.

### Datalogger

1. `call identification_query`, `call self_test` (about a minute, may reset the instrument), `call query_card_type slot=1`.
2. Configure the channels with a `configure_...` call and `select_channels`, then `call read_scan`. Check each value against a known source (a shorted input reads about 0 V, a resistor reads its value).
3. `fetch_readings` returns the last scan: run it after `read_scan`.
4. Switching calls (`close_channel`, `open_channels`) only with the signals disconnected.

### Multimeter and switch unit

Follow the same pattern: `test` first, then a measurement of a known source. These categories are not yet fully covered by the schema: report what is missing.

### Checking a translation

When a call has a `map`, test **every** logical value in the schema, not only one: a missing or wrong value shows up as `CALL-002` (not handled) or as the wrong behaviour on the instrument. Use `plan NAME ...` to see the text sent, `readback` to see that the instrument holds the value, and compare with the front panel.

## 6. Reporting results

Please send, for each instrument tested:

* the model id and the firmware (the answer of `*IDN?`, printed when the tool connects);
* the interface and, for RS-232, the settings and the cable type;
* the output of the session (copy the terminal text; for a large waveform use `stats` and `save FILE.csv 5000`, not the full file);
* for every failing or doubtful call: the call name, the `commands:` line, the `result:` or error line (for example `[CALL-005] ...`), and what the manual or the instrument display says it should be.

Error codes start with `CALL-`: `CALL-001` the model does not support the call, `CALL-002` a value is not handled by the model, `CALL-003` invalid argument, `CALL-004` a command failed (see the transport message), `CALL-005` the answer was not recognised. The full list is in `ERROR_CODES.md` of the application.

Results that are confirmed on real hardware are recorded in `COMMAND_NAMES.md`, section *Known gaps and legacy names*, so the next person knows what is verified and what is only taken from the manual.

## 7. Troubleshooting

| Symptom | Likely cause |
|---|---|
| a model or category is missing from the menu | old `Instruments_LIB` checkout: see *Setup* and check the `Library:` line |
| `VI_ERROR_RSRC_NFOUND` | wrong address, or (serial) `pyserial` not installed / port not accessible (on Linux add your user to `dialout`) |
| every query ends in a timeout (RS-232) | straight instead of null-modem cable, wrong baud rate or flow control: use `loopback` and `probe` |
| timeout only on one long call | the call needs more time (for example a large waveform, a self test); report it |
| `[CALL-001] ... is not supported` | the library has no command for this model; if the manual documents one, report it |
| `[CALL-005] answer not recognised` | the instrument answered with a text the library does not know; report the exact text |
| binary data cut or garbled | the answer is a binary block: the library entry must declare `returns: binary` |
| waveform values wrong by a constant factor | check the scale fields against the screen; report gain, offset and a screenshot |
| a call works from `raw` but not from `call` | the library syntax differs from what you typed; compare `plan NAME` with your text |

## 8. Adding or correcting a command

A command goes into the library **only if it is documented in the instrument's manual or verified on the instrument**. See `COMMAND_NAMES.md` for the call names (mandatory and optional per category), `schema/README.md` for the entry format (`steps`, `map`, `response_map`, `parse`), and run level 1 before opening a pull request.

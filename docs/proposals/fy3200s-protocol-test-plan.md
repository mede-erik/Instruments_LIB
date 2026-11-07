# FeelTech FY3200S: what is known and how to find the protocol

Status: **no model in the library**. The user manual in `docs/FeelTech/FY3200S_Series/` has no remote protocol, and a model needs documented or verified commands (a series without the mandatory calls fails `Tests/check_conformance.py`). This note prepares the work for when the protocol document (or a session on the instrument) is available. A person the owner knows has a FY3200S.

## What is already known (from the manual)

See the table in `function-generator-calls.md`: four models (FY3206S, FY3212S, FY3220S, FY3224S), two channels (main "MF", subsidiary "SF"), frequency resolution 10 mHz, up to 20 Vpp with no load on 50 ohm, offset +/-10 V, shapes `SINE`, `SQUR`, `TRGL`, `ARB1`-`ARB4`, `PRE1`-`PRE10`, USB cable in the accessories (a "square port" USB). Memories M0-M19.

## What the library entry needs and the manual does not say

1. **Connection**: how the PC sees the instrument (a USB serial port of a USB-serial chip, or something else), baud rate, data bits, parity, stop bits, flow control, **terminator** of a command and of an answer. For a serial port: the `serial` entry of the model (`transports`, `factory_defaults`).
2. **The commands** for: output on / off of each channel, frequency (and in which unit and with how many digits), amplitude (Vpp, with or without load), offset, waveform selection (the codes of `SINE`, `SQUR`, `TRGL`...), and which of them have a read-back.
3. Whether the instrument answers to anything (an acknowledgement after a command, an error text) and whether it has **no identification** (very likely: then `identification_query` cannot be a `*IDN?`, and the identity would come from the USB descriptor, see `ola/identity.py` of the application).
4. How each channel is addressed (the two channels have separate command families?).

## Where to look

* The communication protocol document of the FY series from the manufacturer (FeelTech): it is usually a separate short PDF or a page of the software package ("PC software", "communication protocol", "upper computer"); the software package itself may contain it.
* The program that controls the generator from the PC: its serial settings and a capture of what it sends.

## Test session with the instrument (for the owner's acquaintance)

With the terminal tester of the application (`scripts/instrument_shell.py`, see `TESTING.md`): the commands `serial` (set baud rate and the other serial parameters), `raw TEXT` (send a text exactly as typed and show the raw answer), `probe` (try the baud rates) and `loopback`. The points to write down, one per line, for every command tried: the exact text sent (with the terminator), what the instrument answered, what happened on the instrument (display, output). **Only what is written down with its result goes into the library.** Start with the settings of the port, then one harmless command at a time (a frequency, an amplitude on an unconnected output), and look at the display to confirm it changed. The scope of the same bench (or the Analog Discovery) gives the true value of frequency and amplitude, to check units and the load.

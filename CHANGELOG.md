# Changelog

All notable changes of the library (`instruments_lib.json`, `schema/`, the call names and the documentation) are written here, newest first.

## Versions

The version is the tag of the repository (`v1.0`, `v1.1`, ...). The application packages use the **latest published release** of the library for alpha, beta, rc and final builds; publish the library release before tagging the application.

| Change | Version |
|---|---|
| A call, argument, logical value or model `id` is renamed or removed; the meaning of an argument changes; a call becomes mandatory in a schema (a series may no longer conform) | **major** (2.0) |
| A new model, series, category, optional call or logical type; a model changes the `experimental` flag; a command is corrected to what the manual says | **minor** (1.1, 1.2, ...) |
| A fix that changes no behaviour: documentation, typos, tests, file names | **patch** (1.0.1), or goes with the next minor |

Call names are never renamed inside a major version (see `COMMAND_NAMES.md`, section 1).

## 1.0 (to be tagged)

First release of the library.

### Content

- **10 categories, 34 series, 130 models** in `instruments_lib.json`:
  - power supplies (OWON ODP, Keysight E36300, TDK-Lambda GEN, R&S HMP, HP E3631A, HP 6034A);
  - dataloggers and switch units (Keysight 34970A/34972A and DAQ970A/DAQ973A with their cards, Agilent 3499A);
  - multimeters (HP 3478A, Agilent 34401A);
  - electronic loads (Chroma 6330A, Keysight EL4900, Siglent SDL1000X-E);
  - oscilloscopes (Tektronix 5 Series MSO, Rigol DS1000Z/MSO1000Z, DHO800/DHO900 and MSO5000, Siglent SDS HD, GW Instek GDS-1000B, Digilent Analog Discovery 2);
  - function generators (Rigol DG1000 and DG1000Z, Agilent 33120A, Analog Discovery 2);
  - RF signal generators (Keysight EXG N5171B/N5172B, MXG N5181B/N5182B);
  - spectrum analyzers (Rigol DSA800 and RSA3000, Siglent SSA3000X Plus);
  - vector network analyzers (Zenko LiteVNA 62/64/67, Siglent SNA/SHN, R&S ZNB/ZNL/ZVA/ZVB/ZVT/ZVL).
- **Call schemas** in `schema/` (one per category), the translation layer (`map`, `response_map`, derived parameters, `parse`, `steps` with `write`, `query`, `read`, `delay` and `until`) and `access: driver` for instruments without text commands.
- **Documentation**: `README.md`, `COMMAND_NAMES.md` (the canonical call names, generated from the schemas), `docs/COMMANDS.md` (syntax per series), `TESTING.md` (how to test on hardware and when a model stops being experimental), the manuals in `docs/`.
- **Checks**: `Tests/check_conformance.py --strict` and `python3 -m pytest Tests`.

### Tested on real instruments (`"experimental": false`)

| Model | What was tested |
|---|---|
| Agilent 34970A (`DL_Agilent_34970A`) | over RS-232: 38 of 39 calls accepted; the 34972A is not tested |
| Siglent SDS824X HD | over LAN: readings, settings, 8/16-bit waveforms, whole-memory transfers; the SDS804X HD and SDS814X HD share its command set and were not tried individually |
| Digilent Analog Discovery 2 | oscilloscope and function generator through the WaveForms runtime; the logic analyzer is not supported |
| Keysight N5171B | carrier, power, RF output and modulation; the N5172B, N5181B and N5182B share its command set and were not tried individually |
| Zenko LiteVNA 67 | whole library path: sweep, S11/S21, one-port calibration |

The other 119 models are `experimental`: their commands come from the manuals and have not been run on an instrument.

### Known limitations

- No remote protocol manual for the FeelTech FY3200S; no documentation of the I/Q modulation of the N5172B; the bus messages of the HP 3478A are not covered.
- LiteVNA: two-port calibration, thru, calibrated S21 and a calibration kit with real values are not tested; the LiteVNA 62 and 64 entries are not tested.
- The HP 6034A, the multimeters, the spectrum analyzers, the GW Instek GDS-1000B, the Rigol DHO/MSO5000 and DG1000/DG1000Z are not tested on an instrument.
- Spectrum analyzers: no tracking generator, channel-power type measurements, demodulation or real-time mode.
- Analog Discovery 2: the path from the library entry to the driver (`ProjectConnector`) is not tested yet.

## Before 1.0

`v0.1` (2026-08-04), `v0.2` (2026-08-05) and `v0.3` (2026-09-14) were pre-releases: the first tested models (Siglent SDS800X HD, Agilent 34970A, merged into the Keysight 3497X series) and the first schemas.

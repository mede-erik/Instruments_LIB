# VNA calibration types: the vocabulary of the library

This page explains the calibration kinds and standards that the logical calls of the network analyzer
category understand (`schema/vna.json`), which model can do which, and the commands the library sends.
**Nothing here has been tried on a real instrument**: it was written from the manuals in `docs/`
(sources at the end), and every Siglent and Rohde & Schwarz model stays `experimental`.

The calls are a flow: `calibration_begin` (kind, ports), `calibration_measure` (once per standard),
`calibration_apply`. An instrument with an electronic calibration unit can instead do everything with one
`calibration_ecal`. What a model can do is in its `capabilities`:

| Capability | Meaning |
|---|---|
| `calibration` | `instrument`: the instrument calibrates and keeps the result; `software`: a driver calibrates (LiteVNA) |
| `calibration_kinds` | the kinds `calibration_begin` accepts for this model, with the standards measured one at a time |
| `ecal_kinds` | the kinds `calibration_ecal` accepts (an electronic calibration unit must be connected) |

A kind is listed only when `calibration_begin` has a command for it **and** every standard it needs can be measured.

## The kinds

"Port" is the source port, "port2" the other one. Standards: `OPEN`, `SHORT`, `LOAD` (the matched
termination: *match* for R&S), `THRU`, `REFLECT`, `LINE`, `TRL_THRU`, `UNKNOWN_THRU`, `ISOLATION`,
`ATTENUATION`, `NETWORK`.

| Kind | Standards | Corrects | Other names |
|---|---|---|---|
| `REFLECTION_OPEN`, `REFLECTION_SHORT` | OPEN or SHORT on `port` | reflection tracking only | Siglent *Response (Open / Short)*; R&S *Reflection normalization* (`REFL`, `RSHort`) |
| `ONE_PORT` | OPEN, SHORT, LOAD on `port` | directivity, source match, reflection tracking | OSL, SOL; Siglent *OSL* (`SOLT1`); R&S *Reflection OSM* (`FOPort`) |
| `TRANSMISSION_RESPONSE` | THRU `port` to `port2` | transmission tracking | Siglent *Response (Thru)*; R&S *Transmission normalization* (`FTRans`; on the ZVA/ZVB/ZVT/ZVL only the version for both directions, `FRTRans`, exists) |
| `TRANSMISSION_RESPONSE_BOTH` | THRU | the same in both directions | R&S `FRTRans` |
| `ENHANCED_RESPONSE` | OPEN, SHORT, LOAD on `port`, THRU | source match, directivity, reflection and transmission tracking (one direction) | Siglent *Enhanced Response*; R&S *One Path Two Ports* (`OPTPort`); Keysight *Enhanced Response* |
| `TWO_PORT` | OPEN, SHORT, LOAD on both ports, THRU (and, optionally, ISOLATION) | the twelve-term model: all the above plus load match and, with ISOLATION, crosstalk | SOLT, TOSM; Siglent *SOLT* (`SOLT2`); R&S `TOSM` |
| `TWO_PORT_UNKNOWN_THRU` | OPEN, SHORT, LOAD on both ports, UNKNOWN_THRU | as TOSM; the through only has to be reciprocal | UOSM, SOLR; R&S `UOSM` |
| `TOM` | OPEN, LOAD on both ports, THRU | as TOSM | R&S `TOM` |
| `TSM` | SHORT, LOAD on both ports, THRU | as TOSM | R&S `TSM` |
| `TRM` | REFLECT on both ports, LOAD on both ports, THRU | as TOSM | R&S `TRM` |
| `TRL` | REFLECT on both ports, TRL_THRU, LINE | as TOSM, with no matched load (the line sets the reference); limited bandwidth per line | Siglent *TRL* (`TRL2`); R&S `TRL` |
| `TNA` | THRU, ATTENUATION, NETWORK | as TOSM, with the least demanding standards | R&S `TNA` |

The kinds up to `ENHANCED_RESPONSE` need a source on one port only. `TWO_PORT` and every kind after it need the
instrument to measure in both directions (S11, S21, S12 and S22). A **forward-only analyzer** (the LiteVNA measures
S11 and S21 only) can therefore do `REFLECTION_*`, `ONE_PORT`, `TRANSMISSION_RESPONSE` and, in principle,
`ENHANCED_RESPONSE`, and never the two-port kinds. The library cannot tell this by itself: `calibration_kinds` of the
model is the only place, so keep that list honest.

## Who can do what

| Series | `calibration_kinds` | `ecal_kinds` |
|---|---|---|
| Zenko LiteVNA | `ONE_PORT`, `TRANSMISSION_RESPONSE` (software, in the driver) | none |
| Siglent SNA5000A, SNA5000X-E, SNA6000A, SHN900A | `ONE_PORT`, `REFLECTION_OPEN`, `REFLECTION_SHORT`, `TRANSMISSION_RESPONSE`, `ENHANCED_RESPONSE`, `TWO_PORT`, `TRL` | `ONE_PORT`, `TRANSMISSION_RESPONSE`, `ENHANCED_RESPONSE`, `TWO_PORT` |
| R&S ZNB | all of the Siglent ones plus `TRANSMISSION_RESPONSE_BOTH`, `TWO_PORT_UNKNOWN_THRU`, `TOM`, `TSM`, `TRM`, `TNA` | `ONE_PORT`, `REFLECTION_OPEN`, `REFLECTION_SHORT`, `TRANSMISSION_RESPONSE`, `TRANSMISSION_RESPONSE_BOTH`, `ENHANCED_RESPONSE`, `TWO_PORT` |
| R&S ZNL, ZNLE | as the ZNB without `TOM`, `TSM`, `TRM`, `TNA` | as the ZNB |
| R&S ZVA, ZVB, ZVT | `ONE_PORT`, `REFLECTION_OPEN`, `REFLECTION_SHORT`, `TRANSMISSION_RESPONSE`, `TRANSMISSION_RESPONSE_BOTH`, `ENHANCED_RESPONSE`, `TWO_PORT`, `TWO_PORT_UNKNOWN_THRU`, `TOM`, `TRM`, `TRL`, `TNA` | none (older command, see below) |
| R&S ZVL | `ONE_PORT`, `TRANSMISSION_RESPONSE`, `TRANSMISSION_RESPONSE_BOTH`, `ENHANCED_RESPONSE`, `TWO_PORT` | none |

The 2-port kinds are listed for every model of the series; the models with more ports (ZNB with 4 ports, SNA with
4 ports) are calibrated two ports at a time.

## The commands

Siglent (`:SENSe1:CORRection:COLLect`, VNA series programming guide §3.3):

| Kind | `calibration_begin` | Standards (`calibration_measure`) |
|---|---|---|
| `ONE_PORT` | `METHod:SOLT1 <port>` | `ACQuire:OPEN\|SHORt\|LOAD <port>` |
| `REFLECTION_OPEN` / `_SHORT` | `METHod:OPEN <port>` / `METHod:SHORt <port>` | `ACQuire:OPEN <port>` / `ACQuire:SHORt <port>` |
| `TRANSMISSION_RESPONSE` | `METHod:THRU <port2>,<port>` | `ACQuire:THRU <port2>,<port>` |
| `ENHANCED_RESPONSE` | `METHod:ERESponse <port2>,<port>` | OPEN, SHORT, LOAD on `port`, `ACQuire:THRU <port2>,<port>` |
| `TWO_PORT` | `METHod:SOLT2 <port>,<port2>` | OPEN, SHORT, LOAD on both, `ACQuire:THRU`, optional `ACQuire:ISOLation <port2>,<port>` |
| `TRL` | `METHod:TRL2 <port>,<port2>` | `ACQuire:TRLReflect <port>` on each port, `ACQuire:TRLThru <port2>,<port>`, `ACQuire:TRLLine <port2>,<port>` |
| ECal | `ECal:SOLT1 <port>`, `ECal:THRU`, `ECal:ERESponse`, `ECal:SOLT2` | none: one call |

In the Siglent commands the **response port comes first** and the stimulus (source) port second (`THRU <response>,<stimulus>`).
After the standards `calibration_apply` sends `SAVE`.

Rohde & Schwarz (`SENSe1:CORRection:COLLect`, ZNB user manual §4.5.1 and the SCPI reference):

| Kind | `METHod:DEFine 'OLA', <type>, ports` | Standards (`ACQuire:SELected <standard>, ports`) |
|---|---|---|
| `ONE_PORT` | `FOPort` | `OPEN`, `SHORt`, `MATCh` |
| `REFLECTION_OPEN` / `_SHORT` | `REFL` / `RSHort` | `OPEN` / `SHORt` |
| `TRANSMISSION_RESPONSE` | `FTRans` (ZVx: `FRTRans`) | `THRough` |
| `TRANSMISSION_RESPONSE_BOTH` | `FRTRans` | `THRough` |
| `ENHANCED_RESPONSE` | `OPTPort` (first port: the one that is fully calibrated) | `OPEN`, `SHORt`, `MATCh` on it, `THRough` |
| `TWO_PORT` | `TOSM` | `OPEN`, `SHORt`, `MATCh` on both, `THRough`, optional `ISOLation` |
| `TWO_PORT_UNKNOWN_THRU` | `UOSM` | as TOSM, with `UTHRough` |
| `TOM`, `TSM`, `TRM` | `TOM`, `TSM`, `TRM` | the standards of the table above (`REFL` for the reflect of TRM) |
| `TRL` | `TRL` | `REFL` on both ports, `THRough`, `LINe1` |
| `TNA` | `TNA` | `THRough`, `ATT`, `NET` |
| ECal | `AUTO:TYPE <type>, '', ports` with the same type names | none: one call |

`calibration_apply` sends `SAVE:SELected`. A calibration unit is found by the analyzer; the factory
characterization of the unit is used (the empty string).

## What is not covered

Not in the vocabulary (yet), although the manuals describe them: the multi-line TRL of R&S (`NTRL`), adapter removal
(`ARTosm`), sliding load and offset-short standards, calibrations of three or more ports (`SOLT3`, `SOLT4`, `FNPort`),
the power calibrations (source, receiver, SMARTerCal), mixer and frequency-converting calibrations, the METAS
calibration with uncertainties, the partial recalculation of Siglent (`PARTial:SAVE`), the ECal confidence check,
orientation and the unknown-thru state, and the R&S command for the ZVx calibration unit (`COLLect:AUTO ' ', <port>`,
older than `AUTO:TYPE`).

Not selected by the library: the **calibration kit** (connector type, standard values) and the **connector gender**. The
instrument uses the kit that is active in its own settings. R&S: `SENSe:CORRection:CKIT:SELect`; for the software
calibration of the LiteVNA the values travel with `set_calibration_kit`.

Two behaviours to know:

* **Siglent `TWO_PORT` can behave as an unknown thru.** The preference `:SYSTem:PREFerences:CORRection:SOLR[:STATe]` (on by default)
  replaces SOLT by SOLR when the connectors of the DUT have the same gender and the delay of the thru is zero. The library does
  not change this preference and has no `TWO_PORT_UNKNOWN_THRU` for Siglent: the manual gives the same `ACQuire:THRU` for the menu
  entries *SOLT > Thru* and *SOLR > Unknown Thru*, and which one applies is decided by that preference.
* **ECal on R&S** can fail to detect the unit ports when the test setup has a high attenuation (the manual then asks for
  `AUTO:PORTs:TYPE` with the ports given by hand). The library does not use that command.

## Sources

* Siglent: `docs/Siglent/VNA_Series_ProgrammingGuide_EN05A.pdf`, §3.3.1 (calibration type and standards), §3.3.4 (ECal),
  §3.16.1.47 (SOLR preference); `docs/Siglent/SNA5000A_Series/SNA5000A_UserManual_EN08A.pdf` §7.2, Table 7-2
  (calibration types and items). The SNA5000X-E, SNA6000A and SHN900A manuals list the same types.
* R&S ZNB: `docs/Rohde_Schwarz/ZNB_Series/ZNB_UserManual_en_74.pdf`, §4.5.1 Table 4-7 (types, standards, error terms),
  `CORRection:COLLect:METHod:DEFine` (p. 1364), `ACQuire:SELected` (p. 1328), `AUTO:TYPE` (p. 1350).
* R&S ZNL / ZNLE: `docs/Rohde_Schwarz/ZNL-ZNLE_Series/ZNL_ZNLE_UserManual_en_23.pdf`, `METHod:DEFine` (p. 953).
* R&S ZVA, ZVB, ZVT: `docs/Rohde_Schwarz/ZVA_ZVB_ZVT_OperatingManual_en_33.pdf`, channel menu, calibration (p. 430 and following);
  ZVL: `docs/Rohde_Schwarz/ZVL_Series/ZVL3--Operating_Manual.pdf`.
* Keysight is named only to compare the vocabulary (SOLT, Enhanced Response, TRL, Unknown Thru, ECal): its manuals are not in
  `docs/` and no Keysight analyzer is in the library.

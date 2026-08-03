# Riferimento nomi comando SCPI — instruments_lib.json

Questo documento elenca i **nomi di richiamo canonici** (`common_scpi_commands` e `scpi_commands` in `instruments_lib.json`) e a cosa si riferiscono.

Il software che usa questa libreria deve chiamare gli strumenti tramite questi nomi: **stessa operazione = stesso nome** (almeno all'interno della stessa categoria). La sintassi SCPI sottostante varia da produttore a produttore ed è riportata per serie.

## Convenzioni di naming

- `snake_case` con prefisso verbo: `set_*` (impostazione), `query_*` (interrogazione di stato/configurazione), `read_*` (lettura di una misura), `enable_*` / `disable_*` (attivazione/disattivazione protezioni), `clear_*`, `force_*`, `select_*`, `trigger_*`
- I parametri usano template `{placeholder}` (es. `{value}`, `{channel_number}`)
- Stesso nome in serie diverse = stessa operazione logica, ma la sintassi SCPI può (e normalmente deve) differire
- Differenze **volute** tra categorie: `set_voltage`/`set_current` (alimentatori) vs `set_voltage_level`/`set_current_level` (carichi), `output_on`/`output_off` (alimentatori) vs `load_on`/`load_off` (carichi)

## Abbreviazioni serie

| Abbreviazione | Serie | Categoria |
|---|---|---|
| OWON ODP | OWON_ODP_Series | Alimentatori |
| K. E36300 | Keysight_E36300_Series | Alimentatori |
| TDK GEN | TDK_Lambda_GEN_Series | Alimentatori |
| R&S HMP | Rohde_Schwarz_HMP_Series | Alimentatori |
| K. 3497X | Keysight_3497X_Series | Datalogger |
| Tek MSO5 | Tektronix_5_Series_MSO | Oscilloscopi |
| Rigol DS1000Z | Rigol_DS1000Z_Series | Oscilloscopi |
| Sig. SDS HD | Siglent_SDS_HD_Series | Oscilloscopi |
| Chroma 6330A | Chroma_6330A_Series | Carichi |
| K. EL4900 | Keysight_EL4900_Series | Carichi |
| Sig. SDL1000X | Siglent_SDL1000X_E_Series | Carichi |

## Comandi comuni (IEEE-488.2 e stato)

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `reset` | Reset strumento | `*RST` (tutte le serie) | — |
| `clear_status` | Azzera registri di stato | `*CLS` (tutte le serie) | — |
| `identification_query` | Identificazione strumento | `*IDN?` (tutte le serie) | string |
| `error_query` | Legge la coda errori | `SYST:ERR?` (OWON, K. E36300, K. 3497X); `SYSTem:ERRor?` (TDK GEN, R&S HMP, Rigol, Sig. SDS HD); `EVMsg?` (Tek MSO5 — il gruppo SYSTem non esiste) | string |
| `self_test` | Self test | `*TST?` (tutte tranne Chroma, EL4900) | int |
| `query_status_byte` | Status byte | `*STB?` (K. 3497X, Rigol, Chroma) | int |
| `query_event_status_register` | Event status register | `*ESR?` (K. 3497X, Rigol, Chroma) | int |
| `enable_event_status_register` | Abilita bit ESR | `*ESE {value}` (K. 3497X, Rigol, Chroma) | — |
| `query_event_status_enable` | Legge maschera ESE | `*ESE?` (K. 3497X, Rigol, Chroma) | int |
| `operation_complete_query` | Operazione completata | `*OPC?` (Sig. SDS HD) | int |

## Alimentatori (PSU)

### Tensione / corrente

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_voltage` | Imposta tensione di uscita (canale selezionato) | `VOLT {value}` (OWON, K. E36300, TDK GEN, R&S HMP) | — |
| `set_current` | Imposta corrente limite (canale selezionato) | `CURR {value}` (OWON, K. E36300, TDK GEN, R&S HMP) | — |
| `read_voltage` | Misura tensione di uscita | `MEAS:VOLT?` (OWON, TDK GEN, R&S HMP); `MEAS:VOLT? CH{channel_number}` (K. E36300) | float |
| `read_current` | Misura corrente di uscita | `MEAS:CURR?` (OWON, TDK GEN, R&S HMP); `MEAS:CURR? CH{channel_number}` (K. E36300) | float |
| `read_power` | Misura potenza di uscita | `MEAS:POW?` (OWON) | float |
| `read_programmed_voltage` | Legge tensione programmata | `VOLT?` (TDK GEN, R&S HMP) | float |
| `read_programmed_current` | Legge corrente programmata | `CURR?` (TDK GEN, R&S HMP) | float |

### Uscita

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `output_on` | Accende l'uscita | `OUTP ON` (OWON, K. E36300, R&S HMP); `OUTPut:STATe ON` (TDK GEN) | — |
| `output_off` | Spegne l'uscita | `OUTP OFF` (OWON, K. E36300, R&S HMP); `OUTPut:STATe OFF` (TDK GEN) | — |
| `output_state_query` | Stato dell'uscita | `OUTP?` (OWON); `OUTPut?` (TDK GEN, R&S HMP) | int (0/1) |

### Canali

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `select_channel` | Seleziona canale per nome | `INST:NSEL {channel_number}` (OWON); `INST:SEL CH{channel_number}` (K. E36300); `INST:SEL OUT{channel_number}` (R&S HMP) | — |
| `select_channel_numeric` | Seleziona canale per numero | `INST:NSEL {channel_number}` (K. E36300, query `INST:NSEL?`) | — |
| `query_selected_channel` | Canale selezionato | `INST:SEL?` (R&S HMP) | string |

### Altre funzioni PSU

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `apply` | Imposta tensione e corrente insieme | `APPL CH{channel_number}, {voltage}, {current}` (K. E36300, query `APPL? CH{channel_number}`) | string |
| `set_local_remote` | Passa da locale a remoto | `SYSTem:SET {mode}` (TDK GEN, query `SYSTem:SET?`) | int |
| `set_ovp_level` | Soglia OVP | `VOLT:PROTection:LEVel {value}` (TDK GEN, query `VOLT:PROTection:LEVel?`) | float |
| `query_ovp_tripped` | Stato scatto OVP | `VOLT:PROTection:TRIPped?` (TDK GEN) | int |

## Carichi elettronici (EL)

### Ingresso / modalità

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `load_on` | Attiva il carico | `LOAD ON` (Chroma); `INP\|OUTP ON` (K. EL4900); `INPut ON` (Sig. SDL1000X, query `INPut?`) | — |
| `load_off` | Disattiva il carico | `LOAD OFF` (Chroma); `INP\|OUTP OFF` (K. EL4900); `INPut OFF` (Sig. SDL1000X) | — |
| `query_input_state` | Stato dell'ingresso | `LOAD?` (Chroma); `INP?` (K. EL4900) | int (0/1) |
| `set_mode` | Seleziona modalità di funzionamento | `MODE {mode}` (Chroma); `FUNC\|MODE {mode}` (K. EL4900: CURRent, VOLTage, POWer, RESistance, CVCC, CRCC, CVCR, AUTO); `FUNC {mode}` (Sig. SDL1000X: CURRent, VOLTage, POWer, RESistance, LED) | — |
| `query_mode` | Modalità attiva | `MODE?` (Chroma) | string |
| `short` | Cortocircuita l'ingresso | `INP\|OUTP:SHORt ON` (K. EL4900) | — |
| `open` | Apre l'ingresso | `INP\|OUTP:SHORt OFF` (K. EL4900) | — |
| `query_short_state` | Stato cortocircuito | `INP:SHORt?` (K. EL4900) | int (0/1) |

### Livelli

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_current_level` | Livello di corrente | `CURR:STAT:L1 {value}` (Chroma, query `CURR:STAT:L1?`); `CURR {value}` (K. EL4900, Sig. SDL1000X) | float |
| `set_voltage_level` | Livello di tensione | `VOLT:L1 {value}` (Chroma, query `VOLT:L1?`); `VOLT {value}` (K. EL4900, Sig. SDL1000X) | float |
| `set_power_level` | Livello di potenza | `POW:STAT:L1 {value}` (Chroma, query `POW:STAT:L1?`); `POW {value}` (K. EL4900, Sig. SDL1000X) | float |
| `set_resistance_level` | Livello di resistenza | `RES:L1 {value}` (Chroma, query `RES:L1?`); `RES {value}` (K. EL4900, Sig. SDL1000X) | float |

### Misure

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `read_voltage` | Misura tensione di ingresso | `MEAS:VOLT?` (Chroma, K. EL4900, Sig. SDL1000X) | float |
| `read_current` | Misura corrente di ingresso | `MEAS:CURR?` (Chroma, K. EL4900, Sig. SDL1000X) | float |
| `read_power` | Misura potenza di ingresso | `MEAS:POW?` (Chroma, K. EL4900, Sig. SDL1000X) | float |

### Slew rate

| Chiave | Descrizione | Sintassi SCPI | Return type |
|---|---|---|---|
| `set_current_slew_rate` | Velocità di variazione corrente (positiva) | `CURR:SLEW {value}` (K. EL4900) | — |
| `set_current_slew_rate_neg` | Velocità di variazione corrente (negativa) | `CURR:SLEW:NEG {value}` (K. EL4900) | — |
| `set_voltage_slew_rate` | Velocità di variazione tensione (positiva) | `VOLT:SLEW {value}` (K. EL4900) | — |
| `set_voltage_slew_rate_neg` | Velocità di variazione tensione (negativa) | `VOLT:SLEW:NEG {value}` (K. EL4900) | — |

### Protezioni

| Chiave | Descrizione | Sintassi SCPI | Return type |
|---|---|---|---|
| `enable_ovp` / `disable_ovp` | Attiva/disattiva OVP | `VOLT:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_ovp_level` | Soglia OVP | `VOLT:PROT {value}` (K. EL4900) | — |
| `enable_ocp` / `disable_ocp` | Attiva/disattiva OCP | `CURR:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_ocp_level` | Soglia OCP | `CURR:PROT {value}` (K. EL4900) | — |
| `enable_opp` / `disable_opp` | Attiva/disattiva OPP | `POW:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_opp_level` | Soglia OPP | `POW:PROT {value}` (K. EL4900) | — |
| `enable_ucp` / `disable_ucp` | Attiva/disattiva UCP | `CURR:UND:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_ucp_level` | Soglia UCP | `CURR:UND:PROT {value}` (K. EL4900) | — |
| `enable_uvp` / `disable_uvp` | Attiva/disattiva UVP | `VOLT:UND:PROT:STAT ON/OFF` (K. EL4900) | — |
| `set_uvp_level` | Soglia UVP | `VOLT:UND:PROT {value}` (K. EL4900) | — |
| `clear_protection_fault` | Azzera il fault di protezione | `INP\|OUTP:PROTection:CLEar` (K. EL4900) | — |

### Canali / dinamica

| Chiave | Descrizione | Sintassi SCPI | Return type |
|---|---|---|---|
| `select_channel` | Seleziona canale/slot | `CHAN {channel_number}` (Chroma, query `CHAN?`) | int |
| `set_dynamic_level_high` | Livello alto dinamico | `CURR:DYN:L1 {value}` (Chroma, modello) | — |
| `set_dynamic_level_low` | Livello basso dinamico | `CURR:DYN:L2 {value}` (Chroma, modello) | — |

## Datalogger (DL)

| Chiave | Descrizione | Sintassi SCPI | Return type |
|---|---|---|---|
| `select_channels` | Seleziona la lista di scansione | `ROUT:SCAN (@{channels})` (K. 3497X) | — |
| `close_channel` | Chiude uno o più canali | `ROUT:CLOSe (@{channels})` (K. 3497X) | — |
| `open_channels` | Apre i canali | `ROUT:OPEN (@{channels})` (K. 3497X) | — |
| `initiate_scan` | Avvia la scansione | `INITiate` (K. 3497X) | — |
| `read_scan` | Avvia la scansione e legge le misure | `READ?` (K. 3497X — non usare con trigger BUS, causa deadlock) | string |
| `fetch_readings` | Legge le misure dell'ultima scansione | `FETCh?` (K. 3497X) | string |
| `set_trigger_source` | Sorgente di trigger | `TRIG:SOUR {source}` (K. 3497X: BUS, IMMediate, EXTernal, TIMer, ALARm1..4) | — |
| `set_trigger_count` | Numero di trigger | `TRIG:COUN {count}` (K. 3497X) | — |
| `trigger_bus` | Trigger via bus | `*TRG` (K. 3497X) | — |
| `configure_dc_voltage` | Configura misura DCV sui canali | `CONF:VOLT:DC {range},{resolution},(@{channels})` (K. 3497X) | — |
| `measure_dc_voltage` | Misura DCV immediata | `MEAS:VOLT:DC? {range},{resolution},(@{channels})` (K. 3497X) | float |
| `set_voltage_range` | Range DCV di misura | `SENS:VOLT:DC:RANG {range},(@{channels})` (K. 34972A, modello) | — |

## Oscilloscopi (OSC)

### Setup automatico

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `auto_setup` | Impostazione automatica | `AUTOSet EXECute` (Tek MSO5); `:AUToscale` (Rigol DS1000Z); `:AUToset` (Sig. SDS HD) | — |

### Canali

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_channel_coupling` | Accoppiamento canale | `CH{channel_number}:COUPling {coupling_type}` (Tek: DC, AC, DCREJ); `:CHANnel{channel_number}:COUPling {coupling_type}` (Rigol, Sig.: AC, DC, GND) | — |
| `set_channel_scale` | Scala verticale | `CH{channel_number}:SCAle {value}` (Tek); `:CHANnel{channel_number}:SCALe {value}` (Rigol, Sig.) | — |
| `set_channel_offset` | Offset verticale | `CH{channel_number}:OFFSet {value}` (Tek); `:CHANnel{channel_number}:OFFSet {value}` (Rigol, Sig.) | — |
| `query_channel_scale` | Scala verticale attuale | `CH{channel_number}:SCAle?` (Tek); `:CHANnel{channel_number}:SCALe?` (Rigol, Sig.) | float |
| `query_channel_offset` | Offset verticale attuale | `CH{channel_number}:OFFSet?` (Tek); `:CHANnel{channel_number}:OFFSet?` (Rigol, Sig.) | float |

### Base tempi

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_timebase_scale` | Scala orizzontale | `HORizontal:MODE:SCAle {value}` (Tek); `:TIMebase:SCALe {value}` (Rigol, Sig.) | — |
| `query_timebase_scale` | Scala orizzontale attuale | `HORizontal:MODE:SCAle?` (Tek); `:TIMebase:SCALe?` (Rigol, Sig.) | float |
| `set_timebase_delay` | Ritardo base tempi | `:TIMebase:DELay {value}` (Sig. SDS HD) | — |
| `set_horizontal_mode` | Modalità orizzontale | `HORizontal:MODE {mode}` (Tek: AUTO, MANual) | — |

### Trigger

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_trigger_mode` | Modalità trigger | `TRIGger:A:MODE {mode}` (Tek: AUTO, NORMal); `:TRIGger:MODE {mode}` (Rigol, Sig.) | — |
| `set_trigger_source` | Sorgente trigger | `TRIGger:A:EDGE:SOUrce CH{channel_number}` (Tek); `:TRIGger:EDGE:SOURce CHAN{channel_number}` (Rigol); `:TRIGger:EDGE:SOURce C{channel_number}` (Sig.) | — |
| `set_trigger_level` | Livello trigger | `TRIGger:A:LEVel:CH{channel_number} {value}` (Tek); `:TRIGger:EDGE:LEVel {value}` (Rigol, Sig.) | — |
| `query_trigger_level` | Livello trigger attuale | `TRIGger:A:LEVel:CH{channel_number}?` (Tek); `:TRIGger:EDGE:LEVel?` (Rigol, Sig.) | float |
| `set_trigger_type` | Tipo trigger | `TRIGger:A:TYPe {type}` (Tek: EDGE, WIDth, TIMEOut, RUNt, WINdow, LOGIc, SETHold, TRANsition, BUS) | — |
| `force_trigger` | Forza un trigger | `TRIGger FORCe` (Tek); `:TFORce` (Rigol) | — |
| `query_trigger_status` | Stato trigger/acquisizione | `:TRIGger:STATus?` (Rigol: TD, WAIT, RUN, AUTO, STOP) | string |

### Acquisizione

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `run_acquisition` | Avvia acquisizione | `ACQuire:STATE RUN` (Tek); `:RUN` (Rigol); `:TRIGger:RUN` (Sig.) | — |
| `stop_acquisition` | Ferma acquisizione | `ACQuire:STATE STOP` (Tek); `:STOP` (Rigol); `:TRIGger:STOP` (Sig.) | — |
| `acquire_single` | Acquisizione single shot | `ACQuire:STATE RUN;*OPC` (Tek — richiede `set_acquisition_stop_after SEQuence`); `:SINGle` (Rigol); `:TRIGger:MODE SINGle` (Sig.) | — |
| `set_acquisition_mode` | Modalità di campionamento | `ACQuire:MODe {mode}` (Tek: SAMple, PEAKdetect, HIRes, AVErage, ENVelope) | — |
| `set_acquisition_stop_after` | Comportamento a fine sequenza | `ACQuire:STOPAfter {mode}` (Tek: RUNSTop, SEQuence) | — |
| `set_acquisition_depth` | Profondità di memoria | `:ACQuire:MDEPth {value}` (Rigol, query `:ACQuire:MDEPth?`); `:ACQuire:MDEPth {depth}` (Sig.) | int |

### Waveform

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_waveform_source` | Sorgente dati waveform | `DATa:SOUrce CH{channel_number}` (Tek, query `DATa:SOUrce?`); `:WAVeform:SOURce CHAN{channel_number}` (Rigol); `:WAVeform:SOURce C{channel_number}` (Sig.) | string |
| `set_waveform_format` | Formato dati waveform | `:WAVeform:FORMat {format_type}` (Rigol: ASCii, BYTE, WORD); `:WAVeform:WIDTh {format_type}` (Sig.: BYTE, WORD) | — |
| `query_waveform_preamble` | Preambolo waveform | `WFMOutpre?` (Tek); `:WAVeform:PREamble?` (Rigol, Sig.) | string (CSV) |
| `query_waveform_data` | Dati waveform | `CURVe?` (Tek — binario headerato `#9`); `:WAVeform:DATA?` (Rigol, Sig.) | string (binario/ASCII) |
| `query_waveform_all` | Preambolo + dati insieme | `WAVFrm?` (Tek) | string |

## ID dei canali (non standardizzati!)

I canali non hanno ID uniformi: verificare sempre la serie prima di usarli.

| Produttore | ID canale | Esempio |
|---|---|---|
| OWON | Numerico | `1`, `2`, `3` |
| Keysight (PSU) | `CH` + numero | `CH1`, `CH2`, `CH3` |
| Keysight (datalogger) | Range stringa | `"1001:1020"` |
| R&S | `OUT` + numero | `OUT1`..`OUT4` |
| Tektronix | `CH` + numero | `CH1`..`CH8` |
| Siglent | `C` + numero | `C1`..`C4` |
| TDK-Lambda | `CH1` (canale singolo) | `CH1` |

## Note

- La maggior parte dei modelli ha `"experimental": true`: i comandi non sono ancora stati validati su hardware reale e possono differire dal manuale. Solo `OSC_Tek_MSO54`, `OSC_Tek_MSO58` e `EL_Siglent_SDL1030X_E` sono `false`.
- `query_waveform_data` con formato BYTE/WORD restituisce dati binari con header `#<n><len>` (TMC), non testo.
- Su Tektronix `error_query` usa `EVMsg?` perché il gruppo `SYSTem` non esiste.

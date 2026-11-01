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
| HP E3631A | HP_E3631A_Series | Alimentatori |
| K. 3497X | Keysight_3497X_Series | Datalogger |
| A. 3499A | Agilent_3499A_Series | Unità di commutazione (`switch_units_series`) |
| HP 3478A | HP_3478A_Series | Multimetri |
| A. 34401A | Agilent_34401A_Series | Multimetri |
| Tek MSO5 | Tektronix_5_Series_MSO | Oscilloscopi |
| Rigol DS1000Z | Rigol_DS1000Z_Series | Oscilloscopi |
| Sig. SDS HD | Siglent_SDS_HD_Series | Oscilloscopi |
| Chroma 6330A | Chroma_6330A_Series | Carichi |
| K. EL4900 | Keysight_EL4900_Series | Carichi |
| Sig. SDL1000X | Siglent_SDL1000X_E_Series | Carichi |

## Comandi comuni (IEEE-488.2 e stato)

> **Eccezione HP 3478A**: strumento pre-IEEE-488.2 — nessun comando `*RST`/`*IDN?`/`*CLS`. Le funzioni corrispondenti usano `CLEAR` (reset), `E` (errori, 2 cifre ottali), `K` (clear status), `SPOLL` (status byte), `GET` (trigger).

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `reset` | Reset strumento | `*RST` (tutte tranne HP 3478A, che usa `CLEAR`) | — |
| `clear_status` | Azzera registri di stato | `*CLS` (tutte tranne HP 3478A, che usa `K`) | — |
| `identification_query` | Identificazione strumento | `*IDN?` (tutte tranne HP 3478A — priva di IDN) | string |
| `error_query` | Legge la coda errori | `SYST:ERR?` (OWON, K. E36300, K. 3497X); `SYSTem:ERRor?` (TDK GEN, R&S HMP, A. 34401A, A. 3499A, Rigol, Sig. SDS HD); `EVMsg?` (Tek MSO5 — il gruppo SYSTem non esiste); `E` (HP 3478A — 2 cifre ottali) | string |
| `self_test` | Self test | `*TST?` (tutte tranne Chroma, EL4900, HP 3478A) | int |
| `query_status_byte` | Status byte | `*STB?` (K. 3497X, Rigol, Chroma); `SPOLL` (HP 3478A) | int |
| `query_event_status_register` | Event status register | `*ESR?` (K. 3497X, Rigol, Chroma) | int |
| `enable_event_status_register` | Abilita bit ESR | `*ESE {value}` (K. 3497X, Rigol, Chroma) | — |
| `query_event_status_enable` | Legge maschera ESE | `*ESE?` (K. 3497X, Rigol, Chroma) | int |
| `operation_complete_query` | Operazione completata | `*OPC?` (Sig. SDS HD) | int |

## Alimentatori (PSU)

### Tensione / corrente

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_voltage` | Imposta tensione di uscita (canale selezionato) | `VOLT {value}` (OWON, K. E36300, TDK GEN, R&S HMP); `APPLy {output},{voltage}` (HP E3631A, output P6V/P25V/N25V) | — |
| `set_current` | Imposta corrente limite (canale selezionato) | `CURR {value}` (OWON, K. E36300, TDK GEN, R&S HMP); `APPLy {output},{voltage},{current}` (HP E3631A) | — |
| `read_voltage` | Misura tensione di uscita | `MEAS:VOLT?` (OWON, TDK GEN, R&S HMP); `MEAS:VOLT? CH{channel_number}` (K. E36300); `MEASure:VOLTage:DC?` (HP E3631A, canale selezionato) | float |
| `read_current` | Misura corrente di uscita | `MEAS:CURR?` (OWON, TDK GEN, R&S HMP); `MEAS:CURR? CH{channel_number}` (K. E36300); `MEASure:CURRent:DC?` (HP E3631A) | float |
| `read_power` | Misura potenza di uscita | `MEAS:POW?` (OWON) | float |
| `read_programmed_voltage` | Legge tensione programmata | `VOLT?` (TDK GEN, R&S HMP); `APPLy? {output}` (HP E3631A) | float |
| `read_programmed_current` | Legge corrente programmata | `CURR?` (TDK GEN, R&S HMP) | float |

### Uscita

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `output_on` | Accende l'uscita | `OUTP ON` (OWON, K. E36300, R&S HMP); `OUTPut:STATe ON` (TDK GEN); `OUTPut:STATe ON` (HP E3631A) | — |
| `output_off` | Spegne l'uscita | `OUTP OFF` (OWON, K. E36300, R&S HMP); `OUTPut:STATe OFF` (TDK GEN); `OUTPut:STATe OFF` (HP E3631A) | — |
| `output_state_query` | Stato dell'uscita | `OUTP?` (OWON); `OUTPut?` (TDK GEN, R&S HMP, HP E3631A) | int (0/1) |

### Canali

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `select_channel` | Seleziona canale per nome | `INST:NSEL {channel_number}` (OWON); `INST:SEL CH{channel_number}` (K. E36300); `INST:SEL OUT{channel_number}` (R&S HMP); `INSTrument:SELect {output}` (HP E3631A: P6V, P25V, N25V) | — |
| `select_channel_numeric` | Seleziona canale per numero | `INST:NSEL {channel_number}` (K. E36300, query `INST:NSEL?`); `INSTrument:NSELect {channel_number}` (HP E3631A) | — |
| `query_selected_channel` | Canale selezionato | `INST:SEL?` (R&S HMP); `INSTrument:SELect?` (HP E3631A) | string |

### Altre funzioni PSU

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `apply` | Imposta tensione e corrente insieme | `APPL CH{channel_number}, {voltage}, {current}` (K. E36300, query `APPL? CH{channel_number}`); `APPLy {output},{voltage},{current}` (HP E3631A, query `APPLy? {output}`) | string |
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
| `select_channels` | Seleziona la lista di scansione | `ROUT:SCAN (@{channels})` (K. 3497X); `ROUTe:SCAN (@{channels})` (A. 3499A, formato `@snn`) | — |
| `close_channel` | Chiude uno o più canali | `ROUT:CLOSe (@{channels})` (K. 3497X); `ROUTe:CLOSe (@{channels})` (A. 3499A) | — |
| `open_channels` | Apre i canali | `ROUT:OPEN (@{channels})` (K. 3497X); `ROUTe:OPEN (@{channels})` (A. 3499A) | — |
| `initiate_scan` | Avvia la scansione | `INITiate` (K. 3497X); `ROUTe:SCAN INITiate` (A. 3499A) | — |
| `read_scan` | Avvia la scansione e legge le misure | `READ?` (K. 3497X — non usare con trigger BUS, causa deadlock) | string |
| `fetch_readings` | Legge le misure dell'ultima scansione | `FETCh?` (K. 3497X) | string |
| `set_trigger_source` | Sorgente di trigger | `TRIG:SOUR {source}` (K. 3497X: BUS, IMMediate, EXTernal, TIMer, ALARm1..4); `TRIGger:SOURce {source}` (A. 3499A: IMMediate, BUS, EXternal, TTLTrg0..2, STIMulus) | — |
| `set_trigger_count` | Numero di trigger | `TRIG:COUN {count}` (K. 3497X). **NON esiste su 3499A** (usa `ARM:COUNt`) | — |
| `set_arm_count` | Numero di arm del 3499A | `ARM:COUNt {count}` (A. 3499A, unico: es. 1..99999, MAX, INFinity) | — |
| `trigger_bus` | Trigger via bus | `*TRG` (K. 3497X, A. 3499A) | — |
| `configure_dc_voltage` | Configura misura DCV sui canali | `CONF:VOLT:DC {range},{resolution},(@{channels})` (K. 3497X) | — |
| `measure_dc_voltage` | Misura DCV immediata | `MEAS:VOLT:DC? {range},{resolution},(@{channels})` (K. 3497X) | float |
| `set_voltage_range` | Range DCV di misura | `SENS:VOLT:DC:RANG {range},(@{channels})` (K. 3497X) | — |

> **Nota serie K. 3497X** (modelli 34970A e 34972A): 172 comandi verificati sul manuale dedicato (Command Reference 34970A/72A): sottosistemi CALCulate (AVERage/LIMit/SCALe/COMPare), DATA (POINts?, REMove?, LAST?), DISPlay, FORMat:READing (ALARm/CHANnel/TIME/UNIT), OUTPut:ALARm*, ROUTe (CLOSe:EXCLusive, CHANnel:ADVance, MONitor), SOURce (34907A), UNIT:TEMPerature, TRIGger:TIMer. Formato canali a 3 cifre `(@101:120)`. `READ?` non accetta scan-list (solo 34972A).

> **Nota 3499A**: mainframe di switching/scanning **senza motore di misura** — nessun comando `MEASure?`/`FETCh?`/`READ?`; le misure avvengono su dispositivo esterno.

## Multimetri (MTR)

### Funzione e range

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_function` | Seleziona funzione di misura | `F{function}` (HP 3478A: F1=FDCV, F2=ACV, F3=DCA, F4=ACA, F5=Ω2, F6=Ω4, F7=FREQ); `FUNCtion "{function}"` (A. 34401A: DCV, ACV, DCI, ACI, RES, FRES, FREQ, PER, CONT, DIOD) | — |
| `query_function` | Funzione attuale | `FUNCtion?` (A. 34401A) | string |
| `set_range` | Range di misura | `R{range}` (HP 3478A: R-2..R7, RA; es. R3 = 30V); `{function}:RANGe {range}` (A. 34401A, funzione attiva) | — |
| `set_auto_range` | Auto range | `{function}:RANGe:AUTO {state}` (A. 34401A) | — |
| `set_resolution` | Risoluzione | `N{digits}` (HP 3478A: N3..N5 = 3½..5½ digit); `{function}:RESolution {resolution}` (A. 34401A) | — |
| `set_measurement_rate` | Velocità di misura | `{function}:NPLCycles {nplc}` (A. 34401A: 0.02..100) | — |

### Misura

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `read_measurement` | Legge la misura | `ENTER` (HP 3478A — lettura 13 byte ASCII via HP-IB); `READ?` (A. 34401A) | float |
| `measure_dc_voltage` | Misura DCV immediata | `MEASure:VOLTage:DC? {range},{resolution}` (A. 34401A) | float |
| `measure_ac_voltage` | Misura ACV immediata | `MEASure:VOLTage:AC? {range},{resolution}` (A. 34401A) | float |
| `measure_dc_current` | Misura DCI immediata | `MEASure:CURRent:DC? {range},{resolution}` (A. 34401A) | float |
| `measure_ac_current` | Misura ACI immediata | `MEASure:CURRent:AC? {range},{resolution}` (A. 34401A) | float |
| `measure_resistance` | Misura Ω immediata | `MEASure:RESistance? {range},{resolution}` (A. 34401A) | float |
| `measure_resistance_4wire` | Misura Ω 4 fili | `MEASure:FRESistance? {range},{resolution}` (A. 34401A) | float |
| `measure_frequency` | Misura frequenza | `MEASure:FREQuency? {range},{resolution}` (A. 34401A) | float |
| `measure_period` | Misura periodo | `MEASure:PERiod? {range},{resolution}` (A. 34401A) | float |
| `measure_continuity` | Continuità | `MEASure:CONTinuity?` (A. 34401A) | float |
| `measure_diode` | Test diodo | `MEASure:DIODe?` (A. 34401A) | float |
| `fetch_readings` | Misure dall'ultimo trigger | `FETCh?` (A. 34401A) | string |
| `query_reading_count` | Numero di letture in memoria | `DATA:POINts?` (A. 34401A) | int |

### Configurazione e stato

| Chiave | Descrizione | Sintassi SCPI per serie | Return type |
|---|---|---|---|
| `set_trigger_source` | Sorgente trigger | `T{source}` (HP 3478A: T1=BUS, T2=EXT, T3=INT); `TRIGger:SOURce {source}` (A. 34401A: BUS, IMMediate, EXTernal) | — |
| `trigger_bus` | Trigger via bus | `GET` (HP 3478A — comando HP-IB); `*TRG` (A. 34401A) | — |
| `set_autozero` | Auto zero | `Z{autozero}` (HP 3478A: Z0=off, Z1=on); `SENSe:ZERO:AUTO {mode}` (A. 34401A) | — |
| `clear_status` | Azzera registri stato | `K` (HP 3478A); `*CLS` (A. 34401A) | — |
| `error_query` | Ultimo errore | `E` (HP 3478A — 2 cifre ottali); `SYSTem:ERRor?` (A. 34401A) | string |
| `query_status_byte` | Status byte | `SPOLL` (HP 3478A — serial poll); `*STB?` (A. 34401A) | int |
| `reset` | Reset strumento | `CLEAR` (HP 3478A — device clear); `*RST` (A. 34401A) | — |
| `set_math_function` | Funzione matematica | `CALCulate:FUNCtion {function}` (A. 34401A: NULL, DB, DBM, AVERage, LIMit — una alla volta) | — |
| `set_sample_count` | Letture per trigger | `SAMPle:COUNt {count}` (A. 34401A) | — |
| `initiate_measurement` | Avvia la misura triggerata | `INITiate` (A. 34401A) | — |
| `query_scpi_version` | Versione SCPI | `SYSTem:VERSion?` (A. 34401A) | string |

> **Nota 3478A**: pre-IEEE-488.2 — linguaggio di comandi HP classico, nessun `*IDN?`/`*RST`/SCPI. Identificazione via risposta a `E` + s/n, oppure serial poll.

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
| `set_trigger_slope` | Fronte del trigger | `TRIGger:A:EDGE:SLOpe {slope}` (Tek: RISe, FALL, EITher); `:TRIGger:EDGe:SLOPe {slope}` (Rigol: POSitive, NEGative, RFALl); `:TRIGger:EDGE:SLOPe {slope}` (Sig.: RISing, FALLing, ALTernate) | string (query) |
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
| HP E3631A | Numerico + output identifier | `1`/`2`/`3`, selezionati con `INSTrument:SELect P6V|P25V|N25V` |
| Keysight (datalogger) | Range stringa (slot + canale 3 cifre) | `"101:120"` → `(@101:120)` |
| Agilent 3499A | Formato `@snn` (slot + canale 2 cifre) | `"100:107"` → `(@100:107)` |
| HP/Agilent multimetri | Canale singolo (nessun parametro canale) | — |
| R&S | `OUT` + numero | `OUT1`..`OUT4` |
| Tektronix | `CH` + numero | `CH1`..`CH8` |
| Siglent | `C` + numero | `C1`..`C4` |
| TDK-Lambda | `CH1` (canale singolo) | `CH1` |

## Note

- Tutti i modelli hanno `"experimental": true` (comandi non ancora validati su hardware reale), eccetto la famiglia **Siglent SDS800X HD** (`OSC_Siglent_SDS804X_HD`, `OSC_Siglent_SDS814X_HD`, `OSC_Siglent_SDS824X_HD`, testata parzialmente).
- `query_waveform_data` con formato BYTE/WORD restituisce dati binari con header `#<n><len>` (TMC), non testo.
- Su Tektronix `error_query` usa `EVMsg?` perché il gruppo `SYSTem` non esiste.

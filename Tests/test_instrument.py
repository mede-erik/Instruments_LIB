#!/usr/bin/env python3
# Copyright (C) 2025-2026 Erik Medeossi
# This file is part of Open Lab Automation.
# Licensed under the GNU General Public License v3.0; see the LICENSE file.

"""Tests the SCPI commands defined in instruments_lib.json against a real instrument.

Uses PyVISA with the pyvisa-py backend, so no NI-VISA installation is required.

Examples:
    python3 Tests/test_instrument.py --list-models
    python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --visa "USB0::...::INSTR"
    python3 Tests/test_instrument.py --visa "TCPIP0::192.168.1.50::inst0::INSTR"
    python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --visa "USB0::...::INSTR" --dangerous
    python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --visa "USB0::...::INSTR" --dry-run --verbose
    python3 Tests/test_instrument.py --model PSU_OWON_ODP3033 --visa "USB0::...::INSTR" --channel 2 --report out.json
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "instruments_lib.json"

SAFE_ONLY = {
    "output_state_query",
    "query_input_state",
    "query_short_state",
    "query_mode",
    "query_load_state",
    "query_trigger_status",
    "query_selected_channel",
    "query_ovp_tripped",
    "query_ocp_tripped",
    "fetch_readings",
}


def load_db():
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)["instrument_library"]


def build_index(db):
    index = []
    for category, series_list in db.items():
        for series in series_list:
            for model in series.get("models", []):
                index.append(
                    {
                        "category": category,
                        "series_id": series["series_id"],
                        "series_name": series.get("series_name", series["series_id"]),
                        "model": model,
                    }
                )
    return index


def model_channel_ids(model):
    caps = model.get("capabilities") or {}
    channels = caps.get("channels")
    if not channels:
        channels = model.get("channels")
    if isinstance(channels, list):
        ids = [c.get("channel_id") for c in channels if isinstance(c, dict) and c.get("channel_id")]
        return [str(i) for i in ids]
    if isinstance(channels, str) and channels:
        return [channels]
    return []


def channel_number(channel_id):
    if channel_id is None:
        return "1"
    m = re.search(r"\d+", str(channel_id))
    return m.group(0) if m else "1"


def fill_syntax(syntax, parameters, channel_id, channel_override):
    params = parameters or {}

    def repl(m):
        name = m.group(1)
        if name in ("channel_number", "channel", "channels"):
            if channel_override is not None:
                return channel_override
            p = params.get(name)
            if p and p.get("type") == "int":
                return channel_number(channel_id)
            if channel_id is not None:
                return channel_id
        p = params.get(name)
        if p is None:
            raise ValueError(f"no parameter entry for '{name}'")
        ptype = p.get("type")
        if ptype == "string":
            values = p.get("values") or []
            if values:
                return values[0]
            return "TEST"
        if ptype == "int":
            return "1"
        if ptype == "float":
            return "0.1"
        return "0"

    return re.sub(r"\{(\w+)\}", repl, syntax)


def build_cases(commands, channel_id, channel_override):
    cases = []
    for key, cmd in commands.items():
        for part in ("set", "query"):
            spec = cmd.get(part)
            if not spec:
                continue
            syntax = spec.get("syntax", "")
            try:
                filled = fill_syntax(syntax, cmd.get("parameters"), channel_id, channel_override)
                skip = None
            except Exception as exc:
                filled = syntax
                skip = str(exc)
            cases.append(
                {
                    "key": key,
                    "part": part,
                    "syntax": filled,
                    "query": part == "query",
                    "return_type": spec.get("return_type"),
                    "skip": skip,
                    "dangerous": part == "set" or key in ("output_on", "output_off", "load_on", "load_off", "reset", "clear_protection_fault"),
                }
            )
    return cases


def connect(address, timeout_ms, baud):
    try:
        import pyvisa
    except ImportError:
        sys.exit("PyVISA non installato. Installa le dipendenze: pip install -r Tests/requirements.txt")
    try:
        rm = pyvisa.ResourceManager("@py")
    except Exception as exc:
        sys.exit(f"Impossibile inizializzare il backend pyvisa-py: {exc}")
    kwargs = {"open_timeout": 5000}
    if address.upper().startswith("ASRL"):
        kwargs.update(
            {
                "baud_rate": baud or 9600,
                "data_bits": 8,
                "parity": pyvisa.constants.Parity.none,
                "stop_bits": pyvisa.constants.StopBits.one,
                "read_termination": "\n",
                "write_termination": "\n",
            }
        )
    if address.upper().endswith("::SOCKET"):
        kwargs.update({"read_termination": "\n", "write_termination": "\n"})
    inst = rm.open_resource(address, **kwargs)
    inst.timeout = timeout_ms
    return inst


def identify(inst):
    return inst.query("*IDN?").strip()


def match_model(idn, index):
    low = idn.lower()
    best_score = 0
    best = None
    for entry in index:
        model = entry["model"]
        mf = str(model.get("manufacturer", "")).lower()
        mo = str(model.get("model", "")).lower()
        score = 0
        if mf and mf in low:
            score += 1
        if mo and mo in low:
            score += 2
        if score > best_score:
            best_score = score
            best = entry
    return best if best_score >= 1 else None


def resolve_model(model_id, index):
    wanted = model_id.lower()
    for entry in index:
        if entry["model"]["id"].lower() == wanted:
            return entry
    sys.exit(f"Nessun modello con id '{model_id}' nel database. Usa --list-models per elencarli.")


def check_errors(inst, cmds):
    eq = cmds.get("error_query")
    if not eq or "query" not in eq:
        return None
    try:
        resp = inst.query(eq["query"]["syntax"])
    except Exception:
        return "WARN"
    r = resp.strip().lower()
    if re.match(r"^(0,)?(\"?no error\"?|ok)", r):
        return None
    return resp.strip()


def validate_response(resp, case):
    if resp is None or case.get("return_type") not in ("float", "integer"):
        return None
    try:
        if case["return_type"] == "float":
            float(resp)
        else:
            int(resp)
    except ValueError:
        return f"atteso {case['return_type']}, ricevuto {resp!r}"
    return None


def run_cases(inst, cases, cmds, args):
    results = []
    for case in cases:
        entry = {"case": case}
        if case["skip"]:
            entry["status"] = "SKIP"
            entry["detail"] = case["skip"]
            results.append(entry)
            continue
        if case["dangerous"] and not args.dangerous:
            entry["status"] = "SKIP"
            entry["detail"] = "comando di scrittura: usa --dangerous"
            results.append(entry)
            continue
        if args.only and case["key"] not in args.only:
            continue
        if case["key"] in args.exclude:
            continue
        start = time.monotonic()
        try:
            if case["query"]:
                try:
                    resp = inst.query(case["syntax"])
                except UnicodeDecodeError:
                    inst.write(case["syntax"])
                    raw = inst.read_raw()
                    resp = f"<binario {len(raw)} byte>"
                    entry["binary"] = True
            else:
                inst.write(case["syntax"])
                resp = None
            entry["response"] = resp
        except Exception as exc:
            entry["status"] = "TIMEOUT"
            entry["detail"] = f"{type(exc).__name__}: {exc}"
            if not args.no_error_queue:
                eq = cmds.get("error_query")
                if eq and "query" in eq:
                    try:
                        inst.query(eq["query"]["syntax"])
                    except Exception:
                        pass
            results.append(entry)
            continue
        entry["duration_ms"] = round((time.monotonic() - start) * 1000, 1)
        bad_type = validate_response(resp, case)
        if bad_type:
            entry["status"] = "FAIL"
            entry["detail"] = bad_type
            results.append(entry)
            continue
        if not args.no_error_queue and case["query"] and case["key"] != "error_query":
            err = check_errors(inst, cmds)
            if err == "WARN":
                entry["status"] = "WARN"
                entry["detail"] = "coda errori non interrogabile"
            elif err:
                entry["status"] = "FAIL"
                entry["detail"] = f"error_queue: {err}"
            else:
                entry["status"] = "PASS"
        else:
            entry["status"] = "PASS"
        results.append(entry)
        if args.delay:
            time.sleep(args.delay)
    return results


def print_results(results, verbose):
    for r in results:
        case = r["case"]
        line = f"[{r['status']:<6}] {case['key']:<24} {case['part']:<5} {case['syntax']}"
        if r.get("response") is not None:
            resp = str(r["response"]).strip()
            if len(resp) > 70:
                resp = resp[:67] + "..."
            line += f"  ->  {resp}"
        if r.get("duration_ms") is not None:
            line += f"  ({r['duration_ms']} ms)"
        if r.get("detail"):
            line += f"  -- {r['detail']}"
        if r["status"] == "PASS" and not verbose:
            continue
        print(line)


def main():
    ap = argparse.ArgumentParser(description="Testa i comandi SCPI di instruments_lib.json su uno strumento reale.")
    ap.add_argument("--model", help="id del modello nel JSON (es. PSU_OWON_ODP3033)")
    ap.add_argument("--visa", help="indirizzo VISA (es. USB0::...::INSTR, TCPIP0::IP::inst0::INSTR, ASRL/dev/ttyUSB0::INSTR)")
    ap.add_argument("--list-models", action="store_true", help="elenca i modelli disponibili nel database")
    ap.add_argument("--dangerous", action="store_true", help="esegue anche i comandi di scrittura (set_*, output_on, ...)")
    ap.add_argument("--dry-run", action="store_true", help="stampa i comandi che verrebbero inviati senza connettersi")
    ap.add_argument("--idn-only", action="store_true", help="invia solo *IDN? e termina")
    ap.add_argument("--timeout", type=int, default=3000, help="timeout query in ms (default 3000)")
    ap.add_argument("--channel", help="sostituisce il canale di default nei comandi con parametro canale")
    ap.add_argument("--baud", type=int, help="baud rate per connessioni seriali (default 9600)")
    ap.add_argument("--delay", type=float, default=0.2, help="pausa in secondi tra i comandi (default 0.2)")
    ap.add_argument("--only", action="append", help="esegue solo questi comandi (ripetibile)")
    ap.add_argument("--exclude", action="append", default=[], help="salta questi comandi (ripetibile)")
    ap.add_argument("--no-error-queue", action="store_true", help="non interroga la coda errori dopo ogni comando")
    ap.add_argument("--report", help="salva i risultati in un file JSON")
    ap.add_argument("-v", "--verbose", action="store_true", help="mostra anche i PASS")
    args = ap.parse_args()

    db = load_db()
    index = build_index(db)

    if args.list_models:
        current = None
        for e in sorted(index, key=lambda x: (x["category"], x["series_id"], x["model"]["id"])):
            if (e["category"], e["series_id"]) != current:
                current = (e["category"], e["series_id"])
                print(f"\n{e['category']} / {e['series_name']}")
            exp = "" if e["model"].get("experimental") else "  (testato)"
            print(f"  {e['model']['id']:<36} {e['model']['name']}{exp}")
        return 0

    entry = resolve_model(args.model, index) if args.model else None

    if args.idn_only:
        if not args.visa:
            ap.error("--idn-only richiede --visa")
        inst = connect(args.visa, args.timeout, args.baud)
        print(identify(inst))
        return 0

    if not args.visa and not args.dry_run:
        ap.error("serve --visa (o --idn-only); usa --list-models per vedere i modelli disponibili")

    inst = None
    idn = None
    if args.dry_run:
        if not entry:
            sys.exit("--dry-run richiede --model")
    else:
        inst = connect(args.visa, args.timeout, args.baud)
        try:
            idn = identify(inst)
        except Exception as exc:
            sys.exit(f"Identificazione fallita su {args.visa}: {exc}")
        print(f"*IDN? -> {idn}")
        if not entry:
            entry = match_model(idn, index)
            if not entry:
                sys.exit("Nessun modello riconosciuto dall'IDN. Usa --model per forzare.")
            print(f"Modello riconosciuto: {entry['model']['id']}")
        else:
            mf = str(entry["model"].get("manufacturer", "")).lower()
            mo = str(entry["model"].get("model", "")).lower()
            if mf and mf in idn.lower() or mo and mo in idn.lower():
                print(f"Modello coerente con l'IDN: {entry['model']['id']}")
            else:
                print(f"WARN: {entry['model']['id']} non coincide con l'IDN")

    model = entry["model"]
    series_common = next((s for s in db[entry["category"]] if s["series_id"] == entry["series_id"]), {})
    cmds = dict(series_common.get("common_scpi_commands") or {})
    cmds.update(model.get("scpi_commands") or {})

    channel_ids = model_channel_ids(model)
    if not channel_ids and entry["category"] in ("dataloggers_series", "switch_units_series"):
        channel_ids = ["101:120"]
    channel_id = channel_ids[0] if channel_ids else None

    cases = build_cases(cmds, channel_id, args.channel)
    if args.only:
        cases = [c for c in cases if c["key"] in args.only]
    if args.exclude:
        cases = [c for c in cases if c["key"] not in args.exclude]

    print(f"\n== {model['id']} @ {args.visa} ==")
    if channel_id is not None:
        print(f"canali rilevati: {', '.join(channel_ids)} (default: {channel_id})")
    print(f"comandi totali: {len(cmds)} | casi di test: {len(cases)}")

    if args.dry_run:
        print("\n-- dry run (nessuna connessione) --")
        for c in cases:
            status = "SKIP" if c["skip"] else ("WRITE" if c["dangerous"] else "READ ")
            if c["skip"]:
                print(f"[{status}] {c['key']:<24} {c['part']:<5} {c['syntax']}  -- {c['skip']}")
            else:
                print(f"[{status}] {c['key']:<24} {c['part']:<5} {c['syntax']}")
        return 0

    results = run_cases(inst, cases, cmds, args)
    print("\n-- risultati --")
    print_results(results, args.verbose)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\nriepilogo:", ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    print(f"totale: {len(results)} casi")

    if args.report:
        payload = {
            "model_id": model["id"],
            "visa": args.visa,
            "idn": idn,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dangerous": args.dangerous,
            "results": results,
        }
        Path(args.report).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"report salvato in {args.report}")

    return 1 if counts.get("FAIL") or counts.get("TIMEOUT") else 0


if __name__ == "__main__":
    sys.exit(main())

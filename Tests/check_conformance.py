#!/usr/bin/env python3
"""Check the instrument library against the call schemas in schema/.

For every category that has a schema file, every series of that category is
checked:

ERRORS (exit code 1)
  * a mandatory call is missing (and not disabled with null by every model);
  * a call implements a different half than the schema says (kind set/query/action);
  * an argument name that is not in the schema (typo or divergent naming);
  * a required schema argument that the series does not take (and the call has parameters);
  * a model scpi_commands entry that patches/overrides a call unknown to the series and schema.

TODO (reported, not an error unless --strict)
  * an argument whose values are still vendor values: the schema defines a logical
    enum/type and the library gives no "map" yet (this is the work of the translation step);
  * a call that is in the library but not in the schema.

Usage:
    python3 Tests/check_conformance.py
    python3 Tests/check_conformance.py --strict
    python3 Tests/check_conformance.py --category oscilloscopes_series
"""

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGICAL_NUMERIC = {"int", "float"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _is_number(x):
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


def placeholders(syntax):
    return set(re.findall(r"\{(\w+)\}", syntax or ""))


def check_series(category, schema, series, report):
    sid = series.get("series_id", "?")
    calls = schema["calls"]
    types = schema.get("types", {})
    common = series.get("common_scpi_commands", {})

    # models that disable a call with null
    removed_by_all = {}
    for model in series.get("models", []):
        for name, definition in (model.get("scpi_commands") or {}).items():
            if definition is None:
                removed_by_all.setdefault(name, set()).add(model.get("id"))
    n_models = len(series.get("models", []))

    for name, spec in calls.items():
        if spec["requirement"] == "mandatory" and name not in common:
            if len(removed_by_all.get(name, ())) == 0 or n_models == 0:
                report.error(sid, name, "mandatory call missing")

    for name, cmd in common.items():
        spec = calls.get(name)
        if spec is None:
            report.todo(sid, name, "call not in schema")
            continue
        kind = spec["kind"]
        has_set = bool(cmd.get("set"))
        has_query = bool(cmd.get("query"))
        if kind == "set" and not has_set:
            report.error(sid, name, "schema kind 'set' but the call has no set half")
        if kind == "query" and not has_query:
            report.error(sid, name, "schema kind 'query' but the call has no query half")
        if kind == "action" and not has_set:
            report.error(sid, name, "schema kind 'action' but the call has no set half")

        res = spec.get("result") or {}
        if res.get("type") in types and types[res["type"]]["kind"] == "enum" and has_query:
            q = cmd["query"]
            logical = types[res["type"]]["values"]
            rmap = q.get("response_map")
            if not rmap:
                report.todo(sid, name, f"result is logical {logical}: the query needs a response_map")
            else:
                bad = sorted(set(rmap.values()) - set(logical))
                if bad:
                    report.error(sid, name, f"response_map gives values {bad} that are not in {logical}")
        if res.get("type") in types and types[res["type"]]["kind"] == "bool" and has_query:
            if not cmd["query"].get("bool"):
                report.todo(sid, name, "result is logical bool: the query needs a 'bool' spec")
        schema_args = spec.get("args", {})
        params = cmd.get("parameters") or {}
        used = set()
        for part in ("set", "query"):
            if cmd.get(part):
                used |= placeholders(cmd[part].get("syntax"))
                step_texts = [s.get("text", "") for s in cmd[part].get("steps", [])]
                for t in step_texts:
                    used |= placeholders(t)
        derived = {n for n, d in params.items() if d.get("from")}
        for n in derived:
            src = params[n]["from"]
            for s_ in src if isinstance(src, list) else [src]:
                if s_ not in schema_args:
                    report.error(sid, name, f"derived parameter '{n}' comes from '{s_}', "
                                            f"not a schema argument")
        for p in (set(params) | used) - derived:
            if p not in schema_args:
                report.error(sid, name, f"argument '{p}' is not in the schema "
                                        f"(schema args: {sorted(schema_args) or 'none'})")
        for p, a in schema_args.items():
            if a.get("required", True) and (params or used) and p not in params and p not in used:
                report.error(sid, name, f"required schema argument '{p}' is not used by the series")

        for p, pdef in params.items():
            if p in derived:
                continue
            a = schema_args.get(p)
            if not a:
                continue
            t = a["type"]
            vals = pdef.get("values")
            ptype = pdef.get("type")
            if pdef.get("map"):
                continue
            if any(d.get("from") == p and d.get("map") for d in params.values()):
                continue  # the logical value is translated by derived parameters
            if t == "bool":
                if vals and sorted(map(str, vals)) != ["OFF", "ON"]:
                    report.todo(sid, name, f"argument '{p}' is bool but values are {vals} (needs map)")
            elif t in types and types[t]["kind"] == "enum":
                logical = types[t]["values"]
                if vals is None or sorted(vals) != sorted(logical):
                    report.todo(sid, name, f"argument '{p}' is logical {logical}, "
                                           f"library gives {vals if vals else ptype} (needs map)")
            elif t == "number_or_keyword":
                continue
            elif t in LOGICAL_NUMERIC:
                numeric_hint = bool(vals) and all(_is_number(x) for x in vals)
                if ptype not in LOGICAL_NUMERIC or (vals and not numeric_hint):
                    report.todo(sid, name, f"argument '{p}' is numeric ({t}), "
                                           f"library gives {vals if vals else ptype} (needs map/format)")
            elif t == "string" and ptype not in ("string", None):
                report.todo(sid, name, f"argument '{p}' is a string, library gives {ptype}")

    for model in series.get("models", []):
        for name, definition in (model.get("scpi_commands") or {}).items():
            if name not in common and name not in calls:
                if not (isinstance(definition, dict) and ("set" in definition or "query" in definition)):
                    report.error(sid, name, f"model {model.get('id')}: override/patch of unknown call")


class Report:
    def __init__(self):
        self.errors, self.todos = [], []

    def error(self, sid, name, msg):
        self.errors.append((sid, name, msg))

    def todo(self, sid, name, msg):
        self.todos.append((sid, name, msg))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="TODO items fail the check too")
    ap.add_argument("--category", help="check only this library category key")
    ap.add_argument("--library", default=os.path.join(ROOT, "instruments_lib.json"))
    ap.add_argument("--schema-dir", default=os.path.join(ROOT, "schema"))
    ap.add_argument("--quiet-todo", action="store_true", help="do not print TODO lines, only the count")
    args = ap.parse_args()

    lib_file = load(args.library)
    library = lib_file["instrument_library"]
    report = Report()
    checked = 0
    for path in sorted(glob.glob(os.path.join(args.schema_dir, "*.json"))):
        schema = load(path)
        category = schema["category"]
        if args.category and category != args.category:
            continue
        if "schema_version" in lib_file and lib_file["schema_version"] != schema["schema_version"]:
            report.error("-", os.path.basename(path),
                         f"schema_version {schema['schema_version']} != library {lib_file['schema_version']}")
        for series in library.get(category, []):
            check_series(category, schema, series, report)
            checked += 1

    for sid, name, msg in report.errors:
        print(f"ERROR  {sid}: {name}: {msg}")
    if not args.quiet_todo:
        for sid, name, msg in report.todos:
            print(f"TODO   {sid}: {name}: {msg}")
    print(f"\n{checked} series checked: {len(report.errors)} errors, {len(report.todos)} todo")
    failed = bool(report.errors) or (args.strict and bool(report.todos))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

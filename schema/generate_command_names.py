#!/usr/bin/env python3
# Copyright (C) 2025-2026 Erik Medeossi
# This file is part of Open Lab Automation.
# Licensed under the GNU General Public License v3.0; see the LICENSE file.

"""Regenerate the per-category call tables of COMMAND_NAMES.md from schema/*.json.

The sections between the markers

    <!-- BEGIN GENERATED <category> -->
    <!-- END GENERATED <category> -->

are replaced; everything else in COMMAND_NAMES.md is hand-written and left untouched.

    python3 schema/generate_command_names.py          # rewrite the file
    python3 schema/generate_command_names.py --check  # exit 1 if the file is out of date
"""

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TITLES = {
    "power_supplies_series": "Power supplies",
    "electronic_loads_series": "Electronic loads",
    "oscilloscopes_series": "Oscilloscopes",
    "multimeters_series": "Multimeters",
    "dataloggers_series": "Dataloggers",
    "network_analyzers_series": "Vector network analyzers",
    "function_generators_series": "Function generators",
}


NUMBERS = {
    "power_supplies_series": "3.1",
    "electronic_loads_series": "3.2",
    "oscilloscopes_series": "3.3",
    "multimeters_series": "3.4",
    "dataloggers_series": "3.5",
    "network_analyzers_series": "3.7",
    "function_generators_series": "3.8",
}


def fmt_arg(name, spec):
    parts = [spec["type"]]
    if spec.get("unit"):
        parts.append(spec["unit"])
    if "min" in spec or "max" in spec:
        lo = spec.get("min", "")
        hi = spec.get("max", "")
        parts.append(f"{lo}..{hi}")
    if spec.get("keywords"):
        parts.append("or " + "/".join(spec["keywords"]))
    if "default" in spec:
        parts.append(f"default {spec['default']}")
    if spec.get("required") is False:
        parts.append("optional")
    return f"`{name}` ({', '.join(parts)})"


def fmt_result(result):
    if not result:
        return ""
    text = result["type"]
    if result.get("unit"):
        text += f", {result['unit']}"
    return text


def table(schema, requirement):
    rows = [
        (name, c)
        for name, c in schema["calls"].items()
        if c["requirement"] == requirement
    ]
    if not rows:
        return "_none_\n"
    out = ["| Call | Kind | Arguments | Result | Description |", "|---|---|---|---|---|"]
    for name, c in rows:
        args = "<br>".join(fmt_arg(n, a) for n, a in c.get("args", {}).items())
        desc = (c.get("description") or "").replace("|", "\\|")
        out.append(f"| `{name}` | {c['kind']} | {args} | {fmt_result(c.get('result'))} | {desc} |")
    return "\n".join(out) + "\n"


def types_block(schema):
    items = []
    for name, t in schema.get("types", {}).items():
        if t["kind"] == "enum":
            vals = ", ".join(f"`{v}`" for v in t["values"])
            alias = ""
            if t.get("aliases"):
                alias = " (accepted aliases: " + ", ".join(
                    f"`{a}`→`{b}`" for a, b in t["aliases"].items()) + ")"
            items.append(f"* `{name}`: {vals}{alias}")
        elif t["kind"] == "bool":
            items.append(f"* `{name}`: true / false")
        else:
            items.append(f"* `{name}`: {t.get('description', t['kind'])}")
    return "\n".join(items) + "\n" if items else ""


def block(schema, fname, number):
    cat = schema["category"]
    n_m = sum(1 for c in schema["calls"].values() if c["requirement"] == "mandatory")
    n_o = len(schema["calls"]) - n_m
    lines = [
        f"<!-- BEGIN GENERATED {cat} -->",
        f"### {number} {TITLES.get(cat, cat)} (`{cat}`)",
        "",
        f"Generated from `schema/{fname}` — do not edit this section by hand. "
        f"{n_m} mandatory and {n_o} optional calls.",
        "",
    ]
    if schema.get("description"):
        lines += [schema["description"], ""]
    tb = types_block(schema)
    if tb:
        lines += ["Logical types:", "", tb]
    lines += ["**Mandatory**", "", table(schema, "mandatory"),
              "**Optional**", "", table(schema, "optional"),
              f"<!-- END GENERATED {cat} -->"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--doc", default=os.path.join(ROOT, "COMMAND_NAMES.md"))
    args = ap.parse_args()

    with open(args.doc, encoding="utf-8", newline="") as f:
        text = f.read()
    original = text
    for number, path in enumerate(sorted(glob.glob(os.path.join(ROOT, "schema", "*.json"))), 1):
        with open(path, encoding="utf-8") as f:
            schema = json.load(f)
        cat = schema["category"]
        pattern = re.compile(
            rf"<!-- BEGIN GENERATED {cat} -->.*?<!-- END GENERATED {cat} -->", re.S)
        m = pattern.search(text)
        if not m:
            print(f"missing markers for {cat} in {args.doc}", file=sys.stderr)
            return 1
        num = NUMBERS.get(cat, f"3.{number}")
        text = text[: m.start()] + block(schema, os.path.basename(path), num) + text[m.end():]
    if args.check:
        if text != original:
            print("COMMAND_NAMES.md is out of date: run python3 schema/generate_command_names.py")
            return 1
        print("COMMAND_NAMES.md is up to date")
        return 0
    with open(args.doc, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("COMMAND_NAMES.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

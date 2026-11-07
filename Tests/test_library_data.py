# Copyright (C) 2025-2026 Erik Medeossi
# This file is part of Open Lab Automation.
# Licensed under the GNU General Public License v3.0; see the LICENSE file.

"""Offline checks of the library data (instruments_lib.json and schema/*.json).

They need only Python and pytest (no application, no instrument) and complement
``check_conformance.py`` (library against the call schemas) with the structural rules of
``schema/README.md``: unique ids, valid steps and placeholders, valid transports and serial
settings, existing documentation and modules.

Run:  python3 -m pytest Tests -q
"""

import glob
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_FILE = os.path.join(ROOT, "instruments_lib.json")
SCHEMA_FILES = sorted(glob.glob(os.path.join(ROOT, "schema", "*.json")))

BASE_TYPES = {"int", "float", "string", "binary", "raw", "number_or_keyword", "bool"}
TYPE_KINDS = {"enum", "bool", "list", "mapping"}
CALL_KINDS = {"set", "query", "action"}
REQUIREMENTS = {"mandatory", "optional"}
STEP_OPS = {"write", "query", "read", "delay"}
STEP_FIELDS = {"op", "text", "ms", "timeout_ms", "returns", "when", "foreach"}
GROUP_FIELDS = {"steps", "foreach", "when"}  # a group of steps repeated with foreach
RETURNS = {"string", "float", "int", "binary"}
TRANSPORT_KINDS = {"vxi11", "raw_socket", "usbtmc", "serial", "hislip", "gpib", "dwf"}
FLOW_CONTROL = {"none", "xon_xoff", "rts_cts", "dtr_dsr"}
PLACEHOLDER = re.compile(r"\{(\w+)\}")

# Known gaps of the library. The tests fail when a new gap appears and also when a listed gap
# is fixed, so remove the entry together with the fix.
KNOWN_MISSING_DOCUMENTATION = set()
KNOWN_UNKNOWN_MODULES = set()


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


LIB = _load(LIBRARY_FILE)
LIBRARY = LIB["instrument_library"]
SCHEMAS = {s["category"]: s for s in map(_load, SCHEMA_FILES)}
SERIES = [
    (category, series)
    for category, series_list in LIBRARY.items()
    for series in series_list
    if "models" in series
]
MODELS = [(category, series, model) for category, series in SERIES for model in series["models"]]
MODEL_IDS = [m["id"] for _, _, m in MODELS]


def _resolved_commands(series, model):
    """Series commands with the model overrides (null removes, patch merges, else replaces)."""
    commands = dict(series.get("common_scpi_commands") or {})
    for name, definition in (model.get("scpi_commands") or {}).items():
        if definition is None:
            commands.pop(name, None)
        elif (
            isinstance(definition, dict)
            and "patch" in definition
            and not ({"set", "query", "driver"} & set(definition))
        ):
            continue  # patches only change fields of a series command
        else:
            commands[name] = definition
    return commands


def _all_commands():
    """(where, name, definition) of every command written in the library."""
    for _, series in SERIES:
        for name, d in (series.get("common_scpi_commands") or {}).items():
            yield series["series_id"], name, d
        for model in series["models"]:
            for name, d in (model.get("scpi_commands") or {}).items():
                if isinstance(d, dict) and ({"set", "query", "driver"} & set(d)):
                    yield model["id"], name, d


COMMANDS = list(_all_commands())


# ---------------------------------------------------------------- files


@pytest.mark.parametrize(
    "path", [LIBRARY_FILE] + SCHEMA_FILES, ids=lambda p: os.path.relpath(p, ROOT)
)
def test_json_is_valid_utf8_without_duplicate_keys(path):
    def no_duplicates(pairs):
        keys = [k for k, _ in pairs]
        duplicated = sorted({k for k in keys if keys.count(k) > 1})
        assert not duplicated, f"duplicated keys {duplicated}"
        return dict(pairs)

    with open(path, encoding="utf-8") as f:
        json.load(f, object_pairs_hook=no_duplicates)


def test_schema_versions_match():
    for category, schema in SCHEMAS.items():
        assert schema["schema_version"] == LIB["schema_version"], category


def test_every_schema_has_a_library_category():
    for category in SCHEMAS:
        assert LIBRARY.get(category), f"schema for '{category}' but the library has no series"


def test_command_names_document_is_up_to_date():
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "schema", "generate_command_names.py"), "--check"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_conformance_strict():
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "Tests", "check_conformance.py"), "--strict"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout


# ---------------------------------------------------------------- schemas


@pytest.mark.parametrize("category", sorted(SCHEMAS))
def test_schema_structure(category):
    schema = SCHEMAS[category]
    types = schema.get("types", {})
    for name, t in types.items():
        assert t.get("kind") in TYPE_KINDS, f"type {name}: kind {t.get('kind')!r}"
        if t["kind"] == "enum":
            values = t.get("values")
            assert values and len(values) == len(set(values)), f"type {name}: values"
            for alias, target in (t.get("aliases") or {}).items():
                assert target in values, f"type {name}: alias {alias} -> {target}"
    known_types = BASE_TYPES | set(types)
    for call, spec in schema["calls"].items():
        where = f"{category}.{call}"
        assert spec.get("requirement") in REQUIREMENTS, where
        assert spec.get("kind") in CALL_KINDS, where
        assert spec.get("description"), f"{where}: no description"
        if spec["kind"] == "query":
            assert spec.get("result", {}).get("type") in known_types, f"{where}: result type"
        for arg, a in (spec.get("args") or {}).items():
            assert a.get("type") in known_types, f"{where}.{arg}: type {a.get('type')!r}"
            if "min" in a and "max" in a:
                assert a["min"] <= a["max"], f"{where}.{arg}: min > max"
            if a.get("type") == "number_or_keyword":
                assert a.get("keywords"), f"{where}.{arg}: no keywords"
            if "default" in a and types.get(a["type"], {}).get("kind") == "enum":
                assert a["default"] in types[a["type"]]["values"], f"{where}.{arg}: default"


def test_call_names_follow_the_naming_rules():
    """Call names are lower-case snake_case (see COMMAND_NAMES.md)."""
    bad = []
    for category, schema in SCHEMAS.items():
        for call in schema["calls"]:
            if not re.fullmatch(r"[a-z][a-z0-9_]*", call):
                bad.append(f"{category}.{call}")
    assert bad == []


# ---------------------------------------------------------------- series and models


def test_series_ids_are_unique():
    ids = [s["series_id"] for _, s in SERIES]
    assert sorted({i for i in ids if ids.count(i) > 1}) == []


def test_model_ids_are_unique():
    assert sorted({i for i in MODEL_IDS if MODEL_IDS.count(i) > 1}) == []


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_model_fields(model_id):
    _, series, model = next(x for x in MODELS if x[2]["id"] == model_id)
    for key in ("name", "manufacturer", "model"):
        assert isinstance(model.get(key), str) and model[key].strip(), key
    assert isinstance(model.get("capabilities", {}), dict)
    assert isinstance(model.get("experimental", False), bool)
    assert model.get("access", "scpi") in ("scpi", "driver")
    assert series.get("series_name")


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_interface_and_transports(model_id):
    _, _, model = next(x for x in MODELS if x[2]["id"] == model_id)
    conns = model.get("interface", {}).get("supported_connection_types")
    assert conns, "no supported_connection_types"
    for conn in conns:
        # "type" is a label shown to the user (LXI, USB-TMC, "LXI raw socket", ...)
        assert isinstance(conn.get("type"), str) and conn["type"].strip(), conn
        for t in conn.get("transports") or []:
            kind = t.get("kind")
            assert kind in TRANSPORT_KINDS, kind
            if kind == "raw_socket":
                assert isinstance(t.get("port"), int) and 0 < t["port"] < 65536
            if kind == "serial":
                assert isinstance(t.get("baud"), int) and t["baud"] > 0
                assert t.get("data_bits", 8) in (5, 6, 7, 8)
                assert t.get("parity", "N") in ("N", "E", "O")
                assert t.get("stop_bits", 1) in (1, 1.5, 2)
                assert t.get("flow_control", "none") in FLOW_CONTROL
                for key in ("write_termination", "read_termination"):
                    # empty for a binary protocol without terminator (LiteVNA)
                    assert isinstance(t.get(key, "\n"), str)


def test_documentation_files_exist():
    missing = set()
    items = [m for _, _, m in MODELS] + list(LIBRARY.get("datalogger_modules", []))
    for item in items:
        path = item.get("documentation_path")
        if path and not os.path.isfile(os.path.join(ROOT, path)):
            missing.add(item["id"])
    assert missing - KNOWN_MISSING_DOCUMENTATION == set(), "documentation_path not found"
    assert KNOWN_MISSING_DOCUMENTATION - missing == set(), "fixed: update the known list"


def test_datalogger_modules():
    modules = LIBRARY.get("datalogger_modules", [])
    ids = [m.get("id") for m in modules]
    assert all(ids) and len(ids) == len(set(ids))
    for module in modules:
        assert module.get("name"), module["id"]
        assert isinstance(module.get("capabilities", {}), dict)
    unknown = set()
    for category, _, model in MODELS:
        if category != "dataloggers_series":
            continue  # switch-unit cards are not datalogger modules
        for module_id in model.get("capabilities", {}).get("compatible_modules", []):
            if module_id not in ids:
                unknown.add((model["id"], module_id))
    assert unknown - KNOWN_UNKNOWN_MODULES == set(), "compatible module not in datalogger_modules"
    assert KNOWN_UNKNOWN_MODULES - unknown == set(), "fixed: update the known list"


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_power_supply_and_load_channels(model_id):
    category, _, model = next(x for x in MODELS if x[2]["id"] == model_id)
    channels = model.get("capabilities", {}).get("channels")
    if not isinstance(channels, list):
        return
    ids = [str(c.get("channel_id")) for c in channels]
    assert len(ids) == len(set(ids)), f"duplicated channel ids {ids}"
    n = model["capabilities"].get("number_of_channels")
    if isinstance(n, int):
        assert n == len(channels)
    for channel in channels:
        for key, spec in channel.items():
            if isinstance(spec, dict) and "min" in spec and "max" in spec:
                assert spec["min"] <= spec["max"], f"channel {channel.get('channel_id')} {key}"


# ---------------------------------------------------------------- commands


def _halves(definition):
    for half in ("set", "query"):
        if definition.get(half):
            yield half, definition[half]


def test_commands_have_an_implementation():
    bad = [
        f"{where}.{name}"
        for where, name, d in COMMANDS
        if not (d.get("set") or d.get("query") or d.get("driver"))
    ]
    assert bad == []


def _flat(steps):
    """The steps of a plan with the groups (``{"steps": [...], "foreach": ...}``) opened."""
    for step in steps:
        if "steps" in step and "op" not in step:
            yield from _flat(step["steps"])
        else:
            yield step


def _check_steps(steps, where, bad):
    for i, s in enumerate(steps):
        tag = f"{where}[{i}]"
        if "steps" in s and "op" not in s:  # a group
            if set(s) - GROUP_FIELDS:
                bad.append(f"{tag}: unknown group fields {sorted(set(s) - GROUP_FIELDS)}")
            if not s["steps"]:
                bad.append(f"{tag}: empty group")
            _check_steps(s["steps"], tag, bad)
            continue
        if set(s) - STEP_FIELDS:
            bad.append(f"{tag}: unknown fields {sorted(set(s) - STEP_FIELDS)}")
        op = s.get("op")
        if op not in STEP_OPS:
            bad.append(f"{tag}: op {op!r}")
        if op in ("write", "query") and not s.get("text"):
            bad.append(f"{tag}: '{op}' without text")
        if op == "delay" and not (isinstance(s.get("ms"), (int, float)) and s["ms"] >= 0):
            bad.append(f"{tag}: delay without ms >= 0")
        if "returns" in s and (op not in ("query", "read") or s["returns"] not in RETURNS):
            bad.append(f"{tag}: returns {s['returns']!r} on {op}")
        if "when" in s and not (isinstance(s["when"], dict) and s["when"]):
            bad.append(f"{tag}: 'when' must map an argument to its value(s)")
        if "foreach" in s and not isinstance(s["foreach"], str):
            bad.append(f"{tag}: 'foreach' must name a list argument")


def test_steps_are_valid():
    bad = []
    for where, name, d in COMMANDS:
        for half, h in _halves(d):
            if "steps" in h and "syntax" in h:
                bad.append(f"{where}.{name}.{half}: both 'steps' and 'syntax'")
            if "steps" not in h and not h.get("syntax"):
                bad.append(f"{where}.{name}.{half}: neither 'steps' nor 'syntax'")
            steps = h.get("steps", [])
            _check_steps(steps, f"{where}.{name}.{half}", bad)
            if (
                half == "query"
                and steps
                and not any(st.get("op") in ("query", "read") for st in _flat(steps))
            ):
                bad.append(f"{where}.{name}.query: no query/read step")
            if "result_step" in h and not 0 <= h["result_step"] < max(len(steps), 1):
                bad.append(f"{where}.{name}.{half}: result_step out of range")
            source = h.get("parse", {}).get("from_steps", [])  # step indexes, or "queries"
            if isinstance(source, str):
                if source != "queries":
                    bad.append(f"{where}.{name}.{half}: parse reads from {source!r}")
            elif any(i >= len(steps) for i in source):
                bad.append(f"{where}.{name}.{half}: parse reads a missing step")
            # a note in brackets is tolerated ("string (2 octal digits)"): the planner reads
            # the base type only
            rt = h.get("return_type")
            if rt is not None and rt.split(" (")[0] not in RETURNS | {"bool", "raw", "list"}:
                bad.append(f"{where}.{name}.{half}: return_type {rt!r}")
    assert bad == []


FOREACH_VARS = {"item", "index", "n"}


def _texts(steps, in_foreach):
    """(text, inside a foreach) of every step, groups included."""
    for step in steps:
        inside = in_foreach or "foreach" in step
        if "steps" in step and "op" not in step:
            yield from _texts(step["steps"], inside)
        else:
            yield step.get("text") or "", inside


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_placeholders_are_declared(model_id):
    """Every {placeholder} of a command is a library parameter or a schema argument of the
    call, so the software can fill it."""
    category, series, model = next(x for x in MODELS if x[2]["id"] == model_id)
    calls = SCHEMAS.get(category, {}).get("calls", {})
    bad = []
    for name, d in _resolved_commands(series, model).items():
        if not isinstance(d, dict) or "driver" in d:
            continue
        declared = set(d.get("parameters") or {}) | set(calls.get(name, {}).get("args", {}))
        # a list argument also gives {<name>_count}; inside foreach: {item}, {index}, {n}
        declared |= {f"{a}_count" for a in declared}
        for half, h in _halves(d):
            texts = [(h.get("syntax") or "", False)] + list(_texts(h.get("steps", []), False))
            for text, in_foreach in texts:
                for p in PLACEHOLDER.findall(text):
                    if p not in declared and not (in_foreach and p in FOREACH_VARS):
                        bad.append(f"{name}.{half}: '{{{p}}}' is not declared")
    assert bad == []


def test_derived_parameters_are_complete():
    bad = []
    for where, name, d in COMMANDS:
        params = d.get("parameters") or {}
        for pname, p in params.items():
            if "from" not in p:
                continue
            if "expr" not in p and not p.get("map"):
                bad.append(f"{where}.{name}.{pname}: 'from' without 'map' or 'expr'")
            if "expr" in p:
                names = set(re.findall(r"[A-Za-z_]\w*", p["expr"]))
                sources = set(p["from"] if isinstance(p["from"], list) else [p["from"]])
                if names - sources:
                    bad.append(f"{where}.{name}.{pname}: expr uses {sorted(names - sources)}")
    assert bad == []


def test_maps_translate_to_text():
    bad = []
    for where, name, d in COMMANDS:
        for pname, p in (d.get("parameters") or {}).items():
            for key, value in (p.get("map") or {}).items():
                if not isinstance(value, (str, int, float)) or isinstance(value, bool):
                    bad.append(f"{where}.{name}.{pname}: {key} -> {value!r}")
            if p.get("map_default") not in (None, "pass"):
                bad.append(f"{where}.{name}.{pname}: map_default {p['map_default']!r}")
        for half, h in _halves(d):
            for key, value in (h.get("response_map") or {}).items():
                if not isinstance(value, str):
                    bad.append(f"{where}.{name}.{half}: response_map {key} -> {value!r}")
            if "bool" in h:
                both = set(map(str, h["bool"].get("true", []))) & set(
                    map(str, h["bool"].get("false", []))
                )
                if both or not h["bool"].get("true") or not h["bool"].get("false"):
                    bad.append(f"{where}.{name}.{half}: bool true/false lists")
    assert bad == []


def test_model_overrides_refer_to_known_calls():
    bad = []
    for category, series, model in MODELS:
        common = series.get("common_scpi_commands") or {}
        for name, d in (model.get("scpi_commands") or {}).items():
            if d is None and name not in common:
                bad.append(f"{model['id']}.{name}: null for a call the series does not define")
            if isinstance(d, dict) and "patch" in d and name not in common:
                bad.append(f"{model['id']}.{name}: patch of a call the series does not define")
            if isinstance(d, dict) and not ({"set", "query", "driver", "patch"} & set(d)):
                bad.append(f"{model['id']}.{name}: entry without set/query/driver/patch")
    assert bad == []


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_driver_models_use_drivers(model_id):
    _, series, model = next(x for x in MODELS if x[2]["id"] == model_id)
    if model.get("access", "scpi") != "driver":
        return
    for name, d in _resolved_commands(series, model).items():
        assert "driver" in d and d["driver"].get("function"), name

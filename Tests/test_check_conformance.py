# Copyright (C) 2025-2026 Erik Medeossi
# This file is part of Open Lab Automation.
# Licensed under the GNU General Public License v3.0; see the LICENSE file.

"""check_conformance.py must report what it promises: these tests feed it small libraries with
one known defect each and check the exit code and the message."""

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(ROOT, "Tests", "check_conformance.py")

SCHEMA = {
    "schema_version": 1,
    "category": "widgets_series",
    "types": {"mode": {"kind": "enum", "values": ["FAST", "SLOW"]}},
    "calls": {
        "reset": {"requirement": "mandatory", "kind": "action", "description": "reset"},
        "set_level": {
            "requirement": "mandatory",
            "kind": "set",
            "description": "level",
            "args": {"channel_number": {"type": "int"}, "value": {"type": "float"}},
        },
        "set_mode": {
            "requirement": "optional",
            "kind": "set",
            "description": "mode",
            "args": {"mode": {"type": "mode"}},
        },
        "query_mode": {
            "requirement": "optional",
            "kind": "query",
            "description": "mode",
            "result": {"type": "mode"},
        },
    },
}


def good_series():
    return {
        "series_id": "W",
        "series_name": "Widgets",
        "common_scpi_commands": {
            "reset": {"set": {"syntax": "*RST"}, "query": None},
            "set_level": {
                "set": {"syntax": "LEV{channel_number} {value}"},
                "query": None,
                "parameters": {"channel_number": {"type": "int"}, "value": {"type": "float"}},
            },
        },
        "models": [{"id": "W1"}],
    }


def run(tmp_path, series, strict=False, schema_version=1):
    (tmp_path / "schema").mkdir(exist_ok=True)
    (tmp_path / "schema" / "widgets.json").write_text(json.dumps(SCHEMA), encoding="utf-8")
    lib = {"schema_version": schema_version, "instrument_library": {"widgets_series": [series]}}
    (tmp_path / "lib.json").write_text(json.dumps(lib), encoding="utf-8")
    args = [
        sys.executable,
        CHECKER,
        "--library",
        str(tmp_path / "lib.json"),
        "--schema-dir",
        str(tmp_path / "schema"),
    ]
    if strict:
        args.append("--strict")
    return subprocess.run(args, capture_output=True, text=True)


def test_conforming_series_passes(tmp_path):
    result = run(tmp_path, good_series(), strict=True)
    assert result.returncode == 0, result.stdout
    assert "0 errors, 0 todo" in result.stdout


def _broken(change):
    series = good_series()
    change(series["common_scpi_commands"], series)
    return series


@pytest.mark.parametrize(
    "change,message",
    [
        (lambda c, s: c.pop("reset"), "mandatory call missing"),
        (lambda c, s: c["reset"].update(set=None, query={"syntax": "X?"}), "no set half"),
        (
            lambda c, s: c["set_level"]["parameters"].update(chanel={"type": "int"}),
            "argument 'chanel' is not in the schema",
        ),
        (
            lambda c, s: c.update(
                query_mode={
                    "set": None,
                    "query": {"syntax": "MODE?", "response_map": {"F": "FAST", "X": "TURBO"}},
                }
            ),
            "not in ['FAST', 'SLOW']",
        ),
        (
            lambda c, s: s["models"][0].update(scpi_commands={"nonsense": {"patch": {}}}),
            "override/patch of unknown call",
        ),
    ],
)
def test_errors_fail(tmp_path, change, message):
    result = run(tmp_path, _broken(change))
    assert result.returncode == 1
    assert "ERROR" in result.stdout and message in result.stdout, result.stdout


def test_schema_version_mismatch_is_an_error(tmp_path):
    result = run(tmp_path, good_series(), schema_version=2)
    assert result.returncode == 1 and "schema_version" in result.stdout


def test_vendor_values_are_todo_and_fail_only_with_strict(tmp_path):
    def add_vendor_mode(c, s):
        c["set_mode"] = {
            "set": {"syntax": "MODE {mode}"},
            "query": None,
            "parameters": {"mode": {"type": "string", "values": ["F", "S"]}},
        }

    series = _broken(add_vendor_mode)
    assert run(tmp_path, series).returncode == 0
    strict = run(tmp_path, series, strict=True)
    assert strict.returncode == 1 and "needs map" in strict.stdout


def test_a_map_resolves_the_todo(tmp_path):
    def add_mapped_mode(c, s):
        c["set_mode"] = {
            "set": {"syntax": "MODE {mode}"},
            "query": None,
            "parameters": {"mode": {"type": "string", "map": {"FAST": "F", "SLOW": "S"}}},
        }

    assert run(tmp_path, _broken(add_mapped_mode), strict=True).returncode == 0


def test_a_mandatory_call_disabled_by_every_model_is_accepted(tmp_path):
    def disable(c, s):
        c.pop("reset")
        s["models"][0]["scpi_commands"] = {"reset": None}

    assert run(tmp_path, _broken(disable)).returncode == 0

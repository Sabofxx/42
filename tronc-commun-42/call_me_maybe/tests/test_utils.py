"""Tests for src/utils.py — JSON loading and result writing."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.utils import (
    load_function_definitions,
    load_function_tests,
    write_results,
)


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_load_definitions_ok(tmp_path: Path) -> None:
    f = tmp_path / "defs.json"
    _write_json(
        f,
        [
            {
                "name": "fn_add",
                "description": "Add",
                "parameters": {"a": {"type": "number"}},
                "returns": {"type": "number"},
            }
        ],
    )
    defs = load_function_definitions(f)
    assert len(defs) == 1
    assert defs[0].name == "fn_add"


def test_load_definitions_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_function_definitions(tmp_path / "missing.json")


def test_load_definitions_invalid_json(tmp_path: Path) -> None:
    f = tmp_path / "bad.json"
    f.write_text("{not json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_function_definitions(f)


def test_load_definitions_not_an_array(tmp_path: Path) -> None:
    f = tmp_path / "obj.json"
    _write_json(f, {"oops": True})
    with pytest.raises(ValueError):
        load_function_definitions(f)


def test_load_definitions_invalid_schema(tmp_path: Path) -> None:
    f = tmp_path / "schema.json"
    _write_json(f, [{"name": "fn"}])  # missing description, parameters...
    with pytest.raises(ValidationError):
        load_function_definitions(f)


def test_load_tests_ok(tmp_path: Path) -> None:
    f = tmp_path / "tests.json"
    _write_json(f, [{"prompt": "hi"}, {"prompt": "hello"}])
    tests = load_function_tests(f)
    assert [t.prompt for t in tests] == ["hi", "hello"]


def test_write_results_creates_parent(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "deeper" / "results.json"
    write_results(
        [{"prompt": "hi", "name": "fn", "parameters": {"a": 1.0}}], out
    )
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == [
        {"prompt": "hi", "name": "fn", "parameters": {"a": 1.0}}
    ]

"""Tests for the Pydantic models in src/models.py."""

import pytest
from pydantic import ValidationError

from src.models import (
    FunctionCallResult,
    FunctionCallTest,
    FunctionDefinition,
    ParameterType,
)


def test_parameter_type_accepts_known_types() -> None:
    for t in ("number", "string", "boolean"):
        assert ParameterType(type=t).type == t


def test_parameter_type_rejects_unknown() -> None:
    with pytest.raises(ValidationError):
        ParameterType(type="integer")


def test_function_definition_minimal() -> None:
    fd = FunctionDefinition(
        name="fn_add",
        description="Add two numbers.",
        parameters={"a": {"type": "number"}, "b": {"type": "number"}},
        returns={"type": "number"},
    )
    assert fd.name == "fn_add"
    assert fd.parameters["a"].type == "number"


def test_function_call_test_requires_prompt() -> None:
    assert FunctionCallTest(prompt="hi").prompt == "hi"
    with pytest.raises(ValidationError):
        FunctionCallTest()  # type: ignore[call-arg]


def test_function_call_result_uses_subject_keys() -> None:
    """The output schema MUST be {prompt, name, parameters}."""
    r = FunctionCallResult(
        prompt="What is the sum of 2 and 3?",
        name="fn_add_numbers",
        parameters={"a": 2.0, "b": 3.0},
    )
    dumped = r.model_dump()
    assert set(dumped.keys()) == {"prompt", "name", "parameters"}
    assert dumped["parameters"] == {"a": 2.0, "b": 3.0}

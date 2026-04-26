#!/usr/bin/env python3
"""Helpers for loading the input JSON files and writing the result file."""

import json
from pathlib import Path
from typing import Any

from src.models import FunctionCallTest, FunctionDefinition


def load_function_definitions(route: Path) -> list[FunctionDefinition]:
    """
    Loads and validates function definitions from a JSON file.

    Args:
        route: Path to the JSON file containing function definitions.

    Returns:
        A list of validated FunctionDefinition objects.
    """
    with open(route, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    if not isinstance(raw_data, list):
        raise ValueError(
            f"{route}: expected a JSON array of function definitions.")
    return [FunctionDefinition(**item) for item in raw_data]


def load_function_tests(route: Path) -> list[FunctionCallTest]:
    """
    Loads and validates test cases from a JSON file.

    Args:
        route: Path to the JSON file containing function calling tests.

    Returns:
        A list of validated FunctionCallTest objects.
    """
    with open(route, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    if not isinstance(raw_data, list):
        raise ValueError(
            f"{route}: expected a JSON array of test prompts.")
    return [FunctionCallTest(**item) for item in raw_data]


def write_results(results: list[dict[str, Any]], output_path: Path) -> None:
    """
    Saves the generated function calling results to a JSON file.

    Creates the parent directories if they do not exist.

    Args:
        results: List of dictionaries containing the generation results.
        output_path: Path object specifying where to save the file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

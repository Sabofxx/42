#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Any

from src.models import FunctionCallTest, FunctionDefinition


def load_function_definitions(route: Path) -> list[FunctionDefinition]:
    with open(route, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    if not isinstance(raw_data, list):
        raise ValueError(
            f"{route} : un tableau JSON de définitions de fonctions est attendu.")
    return [FunctionDefinition(**item) for item in raw_data]


def load_function_tests(route: Path) -> list[FunctionCallTest]:
    with open(route, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    if not isinstance(raw_data, list):
        raise ValueError(
            f"{route} : un tableau JSON de prompts de test est attendu.")
    return [FunctionCallTest(**item) for item in raw_data]


def write_results(results: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

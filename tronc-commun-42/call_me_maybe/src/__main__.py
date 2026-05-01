#!/usr/bin/env python3
"""
Entry point for the Call Me Maybe LLM function-calling tool.

Reads a list of function definitions and a list of natural-language test
prompts, then uses constrained decoding on a small LLM to produce a
structured JSON file with one entry per prompt:
    { "prompt": ..., "name": ..., "parameters": { ... } }
"""

import argparse
import json
import sys
import time
from pathlib import Path

from pydantic import ValidationError

from llm_sdk import Small_LLM_Model
from src.constrained_dec import VocabularyMapper, build_trie
from src.generator import FunctionCaller
from src.utils import (
    load_function_definitions,
    load_function_tests,
    write_results,
)


DEFAULT_FUNCTIONS_DEFINITION = "data/input/functions_definition.json"
DEFAULT_INPUT = "data/input/function_calling_tests.json"
DEFAULT_OUTPUT = "data/output/function_calling_results.json"


def _parse_args() -> argparse.Namespace:
    """Parse the three file-path arguments described in the subject."""
    parser = argparse.ArgumentParser(
        description="42 Call Me Maybe - LLM Function Caller"
    )
    parser.add_argument(
        "--functions_definition",
        default=DEFAULT_FUNCTIONS_DEFINITION,
        type=str,
        help="Path to the JSON file describing available functions.",
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        type=str,
        help="Path to the JSON file containing the natural-language prompts.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        type=str,
        help="Path where the structured JSON results will be written.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the full constrained-decoding pipeline end-to-end."""
    args = _parse_args()

    definitions_path = Path(args.functions_definition)
    tests_path = Path(args.input)
    output_path = Path(args.output)

    try:
        functions = load_function_definitions(definitions_path)
        tests = load_function_tests(tests_path)
        print(
            f"Loaded {len(functions)} function definitions "
            f"and {len(tests)} prompts."
        )
    except FileNotFoundError as e:
        print(f"Error: file not found - {e.filename}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON - {e.msg}")
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: data does not match schema - {e}")
        sys.exit(1)

    print("Initializing LLM...")
    try:
        model = Small_LLM_Model()
    except Exception as e:
        print(f"Error: could not initialize the LLM - {e}")
        sys.exit(1)
    print("LLM ready.")

    mapper = VocabularyMapper(model)
    trie = build_trie(functions, model)
    caller = FunctionCaller(model, mapper, trie, functions)

    results: list[dict[str, object]] = []
    start = time.time()
    for test in tests:
        try:
            result = caller.call(test.prompt)
            results.append(result.model_dump())
        except Exception as e:
            print(f"Error processing prompt {test.prompt!r}: {e}")

    elapsed = time.time() - start
    print(f"Total time: {elapsed:.2f} seconds")

    try:
        write_results(results, output_path)
        print(f"Wrote {len(results)} entries to {output_path}.")
    except OSError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

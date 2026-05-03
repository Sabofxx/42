#!/usr/bin/env python3
"""
Point d'entrée de l'outil de function-calling LLM Call Me Maybe.

Lit une liste de définitions de fonctions et une liste de prompts
de test en langage naturel, puis utilise le constrained decoding
sur un petit LLM pour produire un fichier JSON structuré avec une
entrée par prompt :
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
    """Parse les trois arguments de chemins décrits dans le sujet."""
    parser = argparse.ArgumentParser(
        description="42 Call Me Maybe - Appelant de fonction LLM"
    )
    parser.add_argument(
        "--functions_definition",
        default=DEFAULT_FUNCTIONS_DEFINITION,
        type=str,
        help="Chemin vers le fichier JSON décrivant les fonctions disponibles.",
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        type=str,
        help="Chemin vers le fichier JSON contenant les prompts en langage naturel.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        type=str,
        help="Chemin où les résultats JSON structurés seront écrits.",
    )
    return parser.parse_args()


def main() -> None:
    """Lance le pipeline complet de constrained-decoding de bout en bout."""
    args = _parse_args()

    definitions_path = Path(args.functions_definition)
    tests_path = Path(args.input)
    output_path = Path(args.output)

    try:
        functions = load_function_definitions(definitions_path)
        tests = load_function_tests(tests_path)
        print(
            f"Chargé {len(functions)} définitions de fonctions "
            f"et {len(tests)} prompts."
        )
    except FileNotFoundError as e:
        print(f"Erreur : fichier introuvable - {e.filename}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Erreur : JSON invalide - {e.msg}")
        sys.exit(1)
    except ValidationError as e:
        print(f"Erreur : les données ne correspondent pas au schéma - {e}")
        sys.exit(1)

    print("Initialisation du LLM...")
    try:
        model = Small_LLM_Model()
    except Exception as e:
        print(f"Erreur : impossible d'initialiser le LLM - {e}")
        sys.exit(1)
    print("LLM prêt.")

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
            print(f"Erreur lors du traitement du prompt {test.prompt!r} : {e}")

    elapsed = time.time() - start
    print(f"Temps total : {elapsed:.2f} secondes")

    try:
        write_results(results, output_path)
        print(f"Écrit {len(results)} entrées dans {output_path}.")
    except OSError as e:
        print(f"Erreur lors de l'écriture du fichier de sortie : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

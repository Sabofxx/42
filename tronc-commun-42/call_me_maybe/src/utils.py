#!/usr/bin/env python3
"""Helpers pour charger les fichiers JSON d'entrée et écrire le fichier de résultat."""

import json
from pathlib import Path
from typing import Any

from src.models import FunctionCallTest, FunctionDefinition


def load_function_definitions(route: Path) -> list[FunctionDefinition]:
    """
    Charge et valide les définitions de fonctions depuis un fichier JSON.

    Arguments :
        route : Chemin vers le fichier JSON contenant les définitions.

    Retourne :
        Une liste d'objets FunctionDefinition validés.
    """
    with open(route, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    if not isinstance(raw_data, list):
        raise ValueError(
            f"{route} : un tableau JSON de définitions de fonctions est attendu.")
    return [FunctionDefinition(**item) for item in raw_data]


def load_function_tests(route: Path) -> list[FunctionCallTest]:
    """
    Charge et valide les cas de test depuis un fichier JSON.

    Arguments :
        route : Chemin vers le fichier JSON contenant les tests.

    Retourne :
        Une liste d'objets FunctionCallTest validés.
    """
    with open(route, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    if not isinstance(raw_data, list):
        raise ValueError(
            f"{route} : un tableau JSON de prompts de test est attendu.")
    return [FunctionCallTest(**item) for item in raw_data]


def write_results(results: list[dict[str, Any]], output_path: Path) -> None:
    """
    Sauvegarde les résultats du function-calling dans un fichier JSON.

    Crée les dossiers parents s'ils n'existent pas.

    Arguments :
        results : Liste de dictionnaires contenant les résultats générés.
        output_path : Objet Path indiquant où sauvegarder le fichier.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

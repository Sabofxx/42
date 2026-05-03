#!/usr/bin/env python3
"""
Modèles de validation des données pour le function-calling, basés sur Pydantic.
Garantit un typage strict pour les définitions d'entrée et les résultats de sortie.
"""

from pydantic import BaseModel
from typing import Dict, Any, Literal


class ParameterType(BaseModel):
    """
    Schéma définissant le type de donnée d'un paramètre de fonction
    ou d'une valeur de retour.

    Attributs :
        type : La chaîne de type autorisée (number, string ou boolean).
    """
    type: Literal["number", "string", "boolean"]


class FunctionDefinition(BaseModel):
    """
    Représente le schéma et les métadonnées d'une fonction appelable.

    Attributs :
        name : L'identifiant unique de la fonction.
        description : Une brève explication de ce que fait la fonction.
        parameters : Un dictionnaire associant les noms de paramètres
                    à leurs définitions de type.
        returns : Le type de retour attendu de la fonction.
    """
    name: str
    description: str
    parameters: Dict[str, ParameterType]
    returns: ParameterType


class FunctionCallTest(BaseModel):
    """
    Représente un cas de test individuel pour le function-calling.

    Attributs :
        prompt : La requête en langage naturel à traiter par le LLM.
    """
    prompt: str


class FunctionCallResult(BaseModel):
    """
    Schéma de la sortie finale d'une opération de function-calling.

    Correspond à la structure exigée par le sujet :
    les clés sont 'prompt', 'name' et 'parameters'.

    Attributs :
        prompt : Le prompt d'entrée d'origine.
        name : Le nom de la fonction identifiée par le modèle.
        parameters : Un dictionnaire de paires clé-valeur représentant
                    les arguments générés avec leurs valeurs typées.
    """
    prompt: str
    name: str
    parameters: Dict[str, Any]

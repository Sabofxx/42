#!/usr/bin/env python3
from __future__ import annotations

from typing import TYPE_CHECKING

from src.constrained_dec import (
    FunctionTrie,
    VocabularyMapper,
    generate_argument,
    select_function,
)
from src.models import FunctionCallResult, FunctionDefinition

if TYPE_CHECKING:  # pragma: no cover - import utilisé uniquement pour le typage
    from llm_sdk import Small_LLM_Model


class FunctionCaller:
    """
    Orchestre le pipeline de sélection de fonction et de génération d'arguments.

    Utilise le constrained decoding pour sélectionner la bonne fonction et
    générer chaque argument selon le schéma de la fonction.
    """
    def __init__(
            self,
            model: Small_LLM_Model,
            mapper: VocabularyMapper,
            trie: FunctionTrie,
            functions: list[FunctionDefinition]) -> None:
        """
        Initialise le générateur avec les composants LLM et de décodage.

        Arguments :
            model : L'instance du modèle LLM.
            mapper : Utilitaire pour convertir entre tokens et chaînes.
            trie : Arbre de préfixes contenant les noms de fonctions valides.
            functions : Liste des schémas de fonctions disponibles.
        """
        self.model = model
        self.mapper = mapper
        self.trie = trie
        self.functions = functions

    def call(self, prompt: str) -> FunctionCallResult:
        """
        Traite un prompt pour retourner un appel de fonction structuré.

        Sélectionne d'abord le nom de la fonction puis génère itérativement
        chaque argument selon le schéma de la fonction identifiée.

        Arguments :
            prompt : La requête en langage naturel de l'utilisateur.

        Retourne :
            Un objet FunctionCallResult avec les clés 'prompt', 'name'
            et 'parameters' comme exigé par le sujet.
        """
        # Étape 1 : identifier la fonction à appeler via constrained decoding
        fn_name = select_function(prompt, self.model, self.trie)
        if fn_name is None:
            raise ValueError(
                f"Impossible de sélectionner une fonction pour le prompt : {prompt}")
        print(f"Fonction sélectionnée : {fn_name}")
        selected_function = None
        for function in self.functions:
            if function.name == fn_name:
                selected_function = function
                break

        if selected_function is None:
            raise ValueError(f"Fonction {fn_name} introuvable dans les définitions")
        parameters: dict[str, str | float | bool] = {}
        # Étape 2 : générer chaque argument selon son type défini
        for param_name, param_type in selected_function.parameters.items():
            value = generate_argument(
                prompt, param_type.type, self.model, self.mapper,
                param_name=param_name)
            parameters[param_name] = value

        return FunctionCallResult(
            prompt=prompt, name=fn_name, parameters=parameters)

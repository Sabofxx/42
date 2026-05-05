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

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


class FunctionCaller:
    def __init__(
            self,
            model: Small_LLM_Model,
            mapper: VocabularyMapper,
            trie: FunctionTrie,
            functions: list[FunctionDefinition]) -> None:
        self.model = model
        self.mapper = mapper
        self.trie = trie
        self.functions = functions

    def _build_selection_context(self, prompt: str) -> str:
        lines = [
            "You are a function-calling router. "
            "Pick the single best function to handle the user request.",
            "",
            "Available functions:",
        ]
        for fn in self.functions:
            lines.append(f"- {fn.name}: {fn.description}")
        lines.append("")
        lines.append(f"User request: {prompt}")
        lines.append("Function name to call:")
        return "\n".join(lines)

    def call(self, prompt: str) -> FunctionCallResult:
        selection_prompt = self._build_selection_context(prompt)
        fn_name = select_function(selection_prompt, self.model, self.trie)
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
        for param_name, param_type in selected_function.parameters.items():
            value = generate_argument(
                prompt, param_type.type, self.model, self.mapper,
                param_name=param_name)
            parameters[param_name] = value

        return FunctionCallResult(
            prompt=prompt, fn_name=fn_name, args=parameters)

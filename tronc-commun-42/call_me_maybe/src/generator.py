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

if TYPE_CHECKING:  # pragma: no cover - import is only used for type hints
    from llm_sdk import Small_LLM_Model


class FunctionCaller:
    """
    Orchestrates the function selection and argument generation pipeline.

    Uses constrained decoding to select the correct function and generate
    each argument based on the function schema.
    """
    def __init__(
            self,
            model: Small_LLM_Model,
            mapper: VocabularyMapper,
            trie: FunctionTrie,
            functions: list[FunctionDefinition]) -> None:
        """
        Initializes the generator with necessary LLM and decoding components.

        Args:
            model: The LLM model instance.
            mapper: Utility to map between tokens and strings.
            trie: Prefix tree containing valid function names.
            functions: List of available function schemas.
        """
        self.model = model
        self.mapper = mapper
        self.trie = trie
        self.functions = functions

    def call(self, prompt: str) -> FunctionCallResult:
        """
        Processes a prompt to return a structured function call.

        First selects the function name and then iteratively generates each
        argument based on the identified function's schema.

        Args:
            prompt: The user's natural language request.

        Returns:
            A FunctionCallResult object with keys 'prompt', 'name',
            and 'parameters' as required by the subject.
        """
        # Step 1: Identify the function to call using constrained decoding
        fn_name = select_function(prompt, self.model, self.trie)
        if fn_name is None:
            raise ValueError(
                f"Could not select a function for prompt: {prompt}")
        print(f"Function selected: {fn_name}")
        selected_function = None
        for function in self.functions:
            if function.name == fn_name:
                selected_function = function
                break

        if selected_function is None:
            raise ValueError(f"Function {fn_name} not found in definitions")
        parameters: dict[str, str | float | bool] = {}
        # Step 2: Generate each argument according to its defined type
        for param_name, param_type in selected_function.parameters.items():
            value = generate_argument(
                prompt, param_type.type, self.model, self.mapper,
                param_name=param_name)
            parameters[param_name] = value

        return FunctionCallResult(
            prompt=prompt, name=fn_name, parameters=parameters)

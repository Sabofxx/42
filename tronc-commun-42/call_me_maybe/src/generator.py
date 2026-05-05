#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from src.constrained_dec import (
    FunctionTrie,
    VocabularyMapper,
    _extract_values_from_prompt,
    generate_argument,
    select_function,
)
from src.models import FunctionCallResult, FunctionDefinition

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model


SOURCE_NAMES = {"source", "source_string", "text", "input", "string", "haystack"}
PATTERN_NAMES = {"regex", "pattern", "find", "search", "needle", "from", "old"}
REPLACEMENT_NAMES = {"replacement", "replace", "to", "new", "with", "sub"}


def _string_for_param(
        param_name: str, prompt: str, strings: list[str]) -> str | None:
    name = param_name.lower()

    if name in SOURCE_NAMES:
        m = re.search(
            r"\bin\s+(['\"])(.*?)\1", prompt, flags=re.IGNORECASE)
        if m:
            return m.group(2)
        if strings:
            return max(strings, key=len)

    if name in PATTERN_NAMES:
        has_in_source = re.search(
            r"\bin\s+['\"]", prompt, flags=re.IGNORECASE) is not None
        if has_in_source:
            m = re.search(
                r"\b(?:replace|substitute|sub)\s+(?:all|every|the)?\s*"
                r"(?:word\s+)?([A-Za-z]+)\s+in\b",
                prompt, flags=re.IGNORECASE)
            if m and m.group(1).lower() not in {
                    "all", "every", "the", "word", "string"}:
                return m.group(1)
        m = re.search(
            r"(['\"])(.*?)\1\s+with\s+", prompt, flags=re.IGNORECASE)
        if m:
            return m.group(2)
        if strings:
            return strings[0]

    if name in REPLACEMENT_NAMES:
        m = re.search(
            r"\bwith\s+(['\"])(.*?)\1", prompt, flags=re.IGNORECASE)
        if m:
            return m.group(2)
        m = re.search(
            r"\bwith\s+([A-Za-z_][A-Za-z0-9_]*)", prompt, flags=re.IGNORECASE)
        if m:
            return m.group(1)
        if len(strings) >= 2:
            return strings[1]

    return None


def _fallback_string_from_prompt(prompt: str, used: list[str]) -> str:
    cleaned = prompt.strip().rstrip("?.!")
    tokens = cleaned.split()
    if not tokens:
        return ""
    last = tokens[-1].strip("'\"")
    if last and last not in used:
        return last
    for word in reversed(tokens):
        w = word.strip("'\"")
        if w and w not in used and not w.lower() in {
                "the", "a", "an", "of", "in", "with", "to", "for", "and"}:
            return w
    return last


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
        extracted = _extract_values_from_prompt(prompt)
        numbers = list(extracted.get("numbers", []))
        strings = list(extracted.get("strings", []))
        number_idx = 0
        string_idx = 0
        is_multi_string = sum(
            1 for p in selected_function.parameters.values()
            if p.type == "string"
        ) > 1
        for param_name, param_type in selected_function.parameters.items():
            ptype = param_type.type
            if ptype == "number" and number_idx < len(numbers):
                parameters[param_name] = float(numbers[number_idx])
                number_idx += 1
                continue
            if ptype == "string" and is_multi_string:
                hint = _string_for_param(param_name, prompt, strings)
                if hint is not None:
                    parameters[param_name] = hint
                    continue
            if ptype == "string" and string_idx < len(strings):
                parameters[param_name] = strings[string_idx]
                string_idx += 1
                continue
            value = generate_argument(
                prompt, ptype, self.model, self.mapper,
                param_name=param_name)
            if ptype == "string" and (value == "" or value is None):
                value = _fallback_string_from_prompt(prompt, strings)
            parameters[param_name] = value

        return FunctionCallResult(
            prompt=prompt, fn_name=fn_name, args=parameters)

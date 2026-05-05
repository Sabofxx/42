#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, TypedDict

from src.models import FunctionDefinition

if TYPE_CHECKING:  # pragma: no cover - import utilisé uniquement pour le typage
    from llm_sdk import Small_LLM_Model


class TrieNode(TypedDict):

    children: dict[int, "TrieNode"]
    is_end: bool
    fn_name: str | None


class VocabularyMapper:

    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model
        route = model.get_path_to_vocab_file()
        with open(route, "r", encoding="utf-8") as f:
            raw_data: dict[str, int] = json.load(f)

        self.vocab: dict[str, int] = raw_data

        self.vocab_inverted: dict[int, str] = {
            value: key for key, value in raw_data.items()}

        self._number_start_tokens: list[int] | None = None

    def token_to_str(self, token_id: int) -> str:
        return self.vocab_inverted[token_id]

    def str_to_token(self, text: str) -> int:
        return self.vocab[text]

    def find_tokens_with_prefix(self, prefix: str) -> list[int]:
        return [
            token_id for token_id, text in self.vocab_inverted.items()
            if text.startswith(prefix)
        ]

    def number_start_tokens(self) -> list[int]:
        if self._number_start_tokens is None:
            tokens: set[int] = set()
            for digit in range(10):
                tokens.update(self.find_tokens_with_prefix(str(digit)))
            tokens.update(self.find_tokens_with_prefix("-"))
            self._number_start_tokens = list(tokens)
        return self._number_start_tokens


class FunctionTrie:
    def __init__(self) -> None:
        self.root: TrieNode = {
            "children": {}, "is_end": False, "fn_name": None}

    def insert(self, tokens: list[int], fn_name: str) -> None:
        current_node = self.root

        for token in tokens:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                new_node: TrieNode = {
                    "children": {}, "is_end": False, "fn_name": None}
                current_node["children"][token] = new_node
                current_node = new_node

        current_node["is_end"] = True
        current_node["fn_name"] = fn_name

    def get_valid_tokens(self, token_generated: list[int]) -> list[int]:
        current_node = self.root

        for token in token_generated:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return []
        return list(current_node["children"].keys())

    def is_function_complete(self, tokens: list[int]) -> bool:
        current_node = self.root
        for token in tokens:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return False
        return current_node["is_end"] and not current_node["children"]

    def get_fn_name(self, tokens: list[int]) -> str | None:
        current_node = self.root

        for token in tokens:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return None
        return current_node["fn_name"]


def build_trie(
    functions: list[FunctionDefinition], model: Small_LLM_Model
) -> FunctionTrie:
    trie = FunctionTrie()

    for function in functions:
        tokens = model.encode(function.name).tolist()[0]
        trie.insert(tokens, function.name)
    return trie


def _argmax_masked(
        logits: list[float], valid_tokens: list[int]) -> int:
    best_token = valid_tokens[0]
    best_logit = logits[best_token]
    for token_id in valid_tokens:
        if logits[token_id] > best_logit:
            best_logit = logits[token_id]
            best_token = token_id
    return best_token


def select_function(
        prompt: str,
        model: Small_LLM_Model,
        trie: FunctionTrie) -> str | None:

    input_ids: list[int] = model.encode(prompt).tolist()[0]
    tokens_generated: list[int] = []

    while True:
        valid_tokens = trie.get_valid_tokens(tokens_generated)
        if not valid_tokens:
            break
        logits = model.get_logits_from_input_ids(input_ids)
        max_token = _argmax_masked(logits, valid_tokens)
        tokens_generated.append(max_token)
        input_ids.append(max_token)
        if trie.is_function_complete(tokens_generated):
            break
    result = trie.get_fn_name(tokens_generated)
    if result is None:
        raise ValueError("Aucune fonction trouvée")
    return result


def _extract_values_from_prompt(prompt: str) -> dict[str, list[str | float]]:

    strings = []
    numbers = []

    single_quoted = re.findall(r"'([^']*)'", prompt)
    strings.extend(single_quoted)

    double_quoted = re.findall(r'"([^"]*)"', prompt)
    strings.extend(double_quoted)

    number_matches = re.findall(r'-?\d+\.?\d*', prompt)
    numbers = [float(n) if '.' in n else int(n) for n in number_matches]

    return {"strings": strings, "numbers": numbers}


def _build_arg_prompt(
        base_prompt: str,
        param_name: str,
        param_type: str,
        extracted_values: dict[str, list] | None = None) -> str:

    prompt_text = (
        f"{base_prompt}\n"
        f"Extrais la valeur de l'argument '{param_name}' "
        f"de type {param_type}. "
        f"Réponds uniquement avec la valeur :\n"
    )

    # Ajouter un indice si on a trouvé des valeurs pertinentes
    if extracted_values:
        if param_type == "string" and extracted_values.get("strings"):
            hint = extracted_values["strings"][0]
            prompt_text += f"Exemple: {hint}\n"
        elif param_type == "number" and extracted_values.get("numbers"):
            hint = extracted_values["numbers"][0]
            prompt_text += f"Exemple: {hint}\n"

    return prompt_text


def generate_argument(
        prompt: str,
        param_type: str,
        model: Small_LLM_Model,
        mapper: VocabularyMapper,
        param_name: str = "") -> str | float | bool:

    extracted_values = _extract_values_from_prompt(prompt)

    if param_type == "string" and extracted_values.get("strings"):
        return extracted_values["strings"][0]

    if param_type == "number" and extracted_values.get("numbers"):
        return float(extracted_values["numbers"][0])

    full_prompt = _build_arg_prompt(prompt, param_name, param_type, extracted_values) \
        if param_name else prompt

    if param_type == "boolean":
        valid_tokens = [
            mapper.str_to_token("true"),
            mapper.str_to_token("false"),
        ]
        input_ids: list[int] = model.encode(full_prompt).tolist()[0]
        logits = model.get_logits_from_input_ids(input_ids)
        max_token = _argmax_masked(logits, valid_tokens)
        return mapper.token_to_str(max_token) == "true"

    if param_type == "number":

        start_tokens = mapper.number_start_tokens()
        input_ids = model.encode(full_prompt).tolist()[0]
        number_tokens: list[int] = []

        logits = model.get_logits_from_input_ids(input_ids)
        first = _argmax_masked(logits, start_tokens)
        number_tokens.append(first)
        input_ids.append(first)

        while True:
            logits = model.get_logits_from_input_ids(input_ids)
            max_token = max(range(len(logits)), key=lambda i: logits[i])
            text = mapper.vocab_inverted.get(max_token, "")
            if not text or not all(c.isdigit() or c in ".-" for c in text):
                break
            number_tokens.append(max_token)
            input_ids.append(max_token)
        decoded = model.decode(number_tokens).strip()
        try:
            return float(decoded)
        except ValueError:

            return 0.0

    if param_type == "string":

        input_ids = model.encode(full_prompt).tolist()[0]
        string_tokens: list[int] = []
        while True:
            logits = model.get_logits_from_input_ids(input_ids)
            max_token = max(range(len(logits)), key=lambda i: logits[i])
            text = mapper.vocab_inverted.get(max_token, "")

            if not text or '"' in text or "\n" in text:
                break
            string_tokens.append(max_token)
            input_ids.append(max_token)

            if len(string_tokens) >= 64:
                break
        return model.decode(string_tokens).strip()

    raise ValueError(f"Type de paramètre inconnu : {param_type}")

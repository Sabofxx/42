#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import TYPE_CHECKING, TypedDict

from src.models import FunctionDefinition

if TYPE_CHECKING:  # pragma: no cover - import is only used for type hints
    from llm_sdk import Small_LLM_Model


class TrieNode(TypedDict):
    """
    Represents a single node within the FunctionTrie.

    Attributes:
        children: A dictionary mapping token IDs
                    to their corresponding child nodes.
        is_end: A boolean flag indicating if this node
                    marks the end of a valid function name.
        fn_name: The full string name of the function if
                    is_end is True, otherwise None.
    """
    children: dict[int, "TrieNode"]
    is_end: bool
    fn_name: str | None


class VocabularyMapper:
    """
    Handles the mapping between tokens and their string representations.

    Provides utility methods to convert IDs to text and search for tokens
    sharing specific prefixes to aid in constrained generation.
    """
    def __init__(self, model: Small_LLM_Model) -> None:
        """
        Initializes the mapper using the model's vocabulary file.

        Args:
            model: An instance of Small_LLM_Model to retrieve
                    the vocabulary path.
        """
        self.model = model
        route = model.get_path_to_vocab_file()
        with open(route, "r", encoding="utf-8") as f:
            raw_data: dict[str, int] = json.load(f)
        # token_string -> token_id
        self.vocab: dict[str, int] = raw_data
        # token_id -> token_string
        self.vocab_inverted: dict[int, str] = {
            value: key for key, value in raw_data.items()}
        # Pre-computed cache: tokens whose decoded string starts with a digit
        # or '.' or '-'. Used by the number constraint to avoid scanning the
        # whole vocab on every call.
        self._number_start_tokens: list[int] | None = None

    def token_to_str(self, token_id: int) -> str:
        """Convert a token ID back to its string representation."""
        return self.vocab_inverted[token_id]

    def str_to_token(self, text: str) -> int:
        """Convert a string token to its corresponding integer ID."""
        return self.vocab[text]

    def find_tokens_with_prefix(self, prefix: str) -> list[int]:
        """Return all token IDs whose string representation
        starts with `prefix`."""
        return [
            token_id for token_id, text in self.vocab_inverted.items()
            if text.startswith(prefix)
        ]

    def number_start_tokens(self) -> list[int]:
        """Return the cached set of tokens that may start a JSON number."""
        if self._number_start_tokens is None:
            tokens: set[int] = set()
            for digit in range(10):
                tokens.update(self.find_tokens_with_prefix(str(digit)))
            tokens.update(self.find_tokens_with_prefix("-"))
            self._number_start_tokens = list(tokens)
        return self._number_start_tokens


class FunctionTrie:
    """
    A prefix tree (Trie) used to constrain function name generation.

    Ensures that the LLM only generates function names that exist within
    the provided function definitions.
    """
    def __init__(self) -> None:
        """Initializes an empty Trie root."""
        self.root: TrieNode = {
            "children": {}, "is_end": False, "fn_name": None}

    def insert(self, tokens: list[int], fn_name: str) -> None:
        """
        Inserts a sequence of tokens representing
        a function name into the Trie.
        """
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
        """
        Returns a list of valid next tokens based
        on the current generation path.
        """
        current_node = self.root

        for token in token_generated:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return []
        return list(current_node["children"].keys())

    def is_function_complete(self, tokens: list[int]) -> bool:
        """
        Checks if the sequence of tokens
        forms a complete valid function name.

        Returns True only when the path ends on a leaf node, so that
        function names that share a prefix with longer names cannot be
        truncated early.
        """
        current_node = self.root
        for token in tokens:
            if token in current_node["children"]:
                current_node = current_node["children"][token]
            else:
                return False
        return current_node["is_end"] and not current_node["children"]

    def get_fn_name(self, tokens: list[int]) -> str | None:
        """
        Retrieves the full function
        name string associated with a token sequence.
        """
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
    """
    Builds a FunctionTrie from a list of valid function definitions.

    Args:
        functions: List of allowed function definitions.
        model: The LLM model used to encode names into tokens.

    Returns:
        A populated FunctionTrie object.
    """
    trie = FunctionTrie()

    for function in functions:
        tokens = model.encode(function.name).tolist()[0]
        trie.insert(tokens, function.name)
    return trie


def _argmax_masked(
        logits: list[float], valid_tokens: list[int]) -> int:
    """
    Return the index of the maximum logit restricted to `valid_tokens`.

    More efficient than building a full masked vector when the valid set
    is small compared to the vocabulary.
    """
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
    """
    Generates a valid function name token-by-token using constrained decoding.

    At every step, only tokens that are children of the current trie node
    are allowed; all others are masked out implicitly via _argmax_masked.

    Args:
        prompt: The natural language request.
        model: The LLM instance.
        trie: The Trie containing valid function names.

    Returns:
        The selected function name as a string.
    """
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
        raise ValueError("No function found")
    return result


def _build_arg_prompt(
        base_prompt: str,
        param_name: str,
        param_type: str) -> str:
    """
    Build a sub-prompt that nudges the model toward emitting the value of
    a single argument. The constrained decoder still guarantees the format,
    but a clearer prompt improves selection quality.
    """
    return (
        f"{base_prompt}\n"
        f"Extract the value of the argument '{param_name}' "
        f"of type {param_type}. "
        f"Answer with only the value:\n"
    )


def generate_argument(
        prompt: str,
        param_type: str,
        model: Small_LLM_Model,
        mapper: VocabularyMapper,
        param_name: str = "") -> str | float | bool:
    """
    Generates a function argument constrained by a specific data type.

    Args:
        prompt: The context prompt for the argument.
        param_type: The required type (boolean, number, string).
        model: The LLM instance.
        mapper: VocabularyMapper to validate allowed tokens.
        param_name: Optional name of the parameter being generated,
                    used to refine the prompt sent to the model.

    Returns:
        The generated argument value in its correct Python type.

    Raises:
        ValueError: If an unsupported parameter type is provided.
    """
    full_prompt = _build_arg_prompt(prompt, param_name, param_type) \
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
        # Tokens that may start a number (digits or minus sign).
        start_tokens = mapper.number_start_tokens()
        input_ids = model.encode(full_prompt).tolist()[0]
        number_tokens: list[int] = []
        # First token must start a number.
        logits = model.get_logits_from_input_ids(input_ids)
        first = _argmax_masked(logits, start_tokens)
        number_tokens.append(first)
        input_ids.append(first)
        # Subsequent tokens may continue the number (digits or '.').
        # We use unconstrained argmax and stop as soon as the model emits
        # a token whose decoded string is not made of digits/'.'/'-'.
        while True:
            logits = model.get_logits_from_input_ids(input_ids)
            max_token = max(range(len(logits)), key=lambda i: logits[i])
            text = mapper.vocab_inverted.get(max_token, "")
            if not text or not all(c.isdigit() or c in ".-" for c in text):
                break
            number_tokens.append(max_token)
            input_ids.append(max_token)
        return float(model.decode(number_tokens))

    if param_type == "string":
        # Generate freely until the model emits a token containing the
        # JSON string-terminator character.
        input_ids = model.encode(full_prompt).tolist()[0]
        string_tokens: list[int] = []
        while True:
            logits = model.get_logits_from_input_ids(input_ids)
            max_token = max(range(len(logits)), key=lambda i: logits[i])
            text = mapper.vocab_inverted.get(max_token, "")
            # Stop on quote, newline, or empty token to keep the string
            # short and well-formed.
            if not text or '"' in text or "\n" in text:
                break
            string_tokens.append(max_token)
            input_ids.append(max_token)
            # Hard cap to avoid runaway generation.
            if len(string_tokens) >= 64:
                break
        return model.decode(string_tokens).strip()

    raise ValueError(f"Unknown parameter type: {param_type}")

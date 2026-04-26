"""Tests for the FunctionTrie in src/constrained_dec.py.

The trie is used at the token level, but its logic is independent from
the underlying tokenizer — we exercise it directly with token-id lists.
"""

from src.constrained_dec import FunctionTrie


def test_insert_and_complete_single_function() -> None:
    trie = FunctionTrie()
    trie.insert([1, 2, 3], "fn_add")
    assert trie.is_function_complete([1, 2, 3]) is True
    assert trie.get_fn_name([1, 2, 3]) == "fn_add"


def test_partial_path_is_not_complete() -> None:
    trie = FunctionTrie()
    trie.insert([1, 2, 3], "fn_add")
    assert trie.is_function_complete([1, 2]) is False
    assert trie.get_fn_name([1, 2]) is None


def test_valid_tokens_at_each_step() -> None:
    trie = FunctionTrie()
    trie.insert([10, 20, 30], "fn_a")
    trie.insert([10, 25, 35], "fn_b")
    assert sorted(trie.get_valid_tokens([])) == [10]
    assert sorted(trie.get_valid_tokens([10])) == [20, 25]
    assert trie.get_valid_tokens([10, 20]) == [30]


def test_prefix_collision_does_not_truncate_longer_name() -> None:
    """If 'fn_get' is a prefix of 'fn_get_square_root' we must require
    the longer match to be reachable when more tokens are available."""
    trie = FunctionTrie()
    trie.insert([1, 2], "fn_get")
    trie.insert([1, 2, 3, 4], "fn_get_square_root")
    # The shorter name has children, so completion is NOT declared.
    assert trie.is_function_complete([1, 2]) is False
    # The full longer path is the actual completion.
    assert trie.is_function_complete([1, 2, 3, 4]) is True


def test_unknown_token_returns_empty() -> None:
    trie = FunctionTrie()
    trie.insert([1, 2], "fn")
    assert trie.get_valid_tokens([99]) == []
    assert trie.get_fn_name([99]) is None

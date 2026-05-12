"""Simple tokenizer tuned for code + prose.

Splits camelCase, snake_case, dotted names and keeps short alphanumeric tokens.
A small stopword list is removed for English prose. Identifiers are also
lower-cased.
"""

from __future__ import annotations

import re
from typing import List

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "of", "in",
    "on", "to", "for", "with", "by", "as", "is", "it", "this", "that",
    "these", "those", "be", "are", "was", "were", "from", "at", "into",
    "your", "you", "we", "our", "i", "me", "my", "do", "does", "did",
    "have", "has", "had", "can", "will", "would", "should",
}

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase identifier-friendly tokens."""
    if not text:
        return []
    parts = _SPLIT_RE.split(text)
    tokens: List[str] = []
    for part in parts:
        if not part:
            continue
        for sub in _CAMEL_RE.split(part):
            sub_lower = sub.lower()
            if len(sub_lower) < 2:
                continue
            if sub_lower in _STOPWORDS:
                continue
            tokens.append(sub_lower)
    return tokens


def tokenize_batch(texts: List[str]) -> List[List[str]]:
    """Tokenize a list of texts."""
    return [tokenize(t) for t in texts]

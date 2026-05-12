"""Chunking strategies for Python and Markdown/text files.

Each chunk records the character offsets in the *original* file so that the
recall@k evaluator can compute overlaps against the ground-truth source
spans.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    """A piece of a file together with its character offsets."""

    file_path: str
    first_character_index: int
    last_character_index: int
    text: str

    def char_len(self) -> int:
        """Return the number of characters in the chunk text."""
        return self.last_character_index - self.first_character_index


def _split_oversized(
    file_path: str,
    text: str,
    start: int,
    end: int,
    max_chunk_size: int,
) -> List[Chunk]:
    """Split a chunk that is too large into ~equal sub-chunks with overlap."""
    chunks: List[Chunk] = []
    size = end - start
    if size <= max_chunk_size:
        return [Chunk(file_path, start, end, text[start:end])]

    overlap = max_chunk_size // 10
    step = max_chunk_size - overlap
    pos = start
    while pos < end:
        sub_end = min(pos + max_chunk_size, end)
        chunks.append(Chunk(file_path, pos, sub_end, text[pos:sub_end]))
        if sub_end >= end:
            break
        pos += step
    return chunks


def chunk_python(
    file_path: str,
    text: str,
    max_chunk_size: int = 2000,
) -> List[Chunk]:
    """Chunk a Python file using its AST.

    Strategy: each top-level function/class becomes one chunk. Module-level
    statements between them (imports, constants, etc.) are grouped into a
    "preamble" chunk. Any chunk exceeding ``max_chunk_size`` characters is
    sub-split with a small sliding-window overlap.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return chunk_text(file_path, text, max_chunk_size)

    chunks: List[Chunk] = []
    lines = text.split("\n")
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    def lc_to_offset(lineno: int, col: int) -> int:
        idx = max(0, min(lineno - 1, len(line_offsets) - 1))
        return min(line_offsets[idx] + col, len(text))

    top_level = [
        node
        for node in tree.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        )
    ]

    cursor = 0
    for node in top_level:
        start = lc_to_offset(node.lineno, node.col_offset)
        end_lineno = getattr(node, "end_lineno", node.lineno) or node.lineno
        end_col = getattr(node, "end_col_offset", 0) or 0
        end = lc_to_offset(end_lineno, end_col)

        if start > cursor:
            pre = text[cursor:start].strip()
            if pre:
                chunks.extend(
                    _split_oversized(file_path, text, cursor, start, max_chunk_size)
                )
        chunks.extend(
            _split_oversized(file_path, text, start, end, max_chunk_size)
        )
        cursor = end

    if cursor < len(text):
        tail = text[cursor:].strip()
        if tail:
            chunks.extend(
                _split_oversized(file_path, text, cursor, len(text), max_chunk_size)
            )

    if not chunks:
        chunks = _split_oversized(file_path, text, 0, len(text), max_chunk_size)

    return [c for c in chunks if c.text.strip()]


def chunk_markdown(
    file_path: str,
    text: str,
    max_chunk_size: int = 2000,
) -> List[Chunk]:
    """Chunk a Markdown file by ATX headers (#, ##, ...).

    Each header starts a new chunk; oversized sections fall back to sliding
    windows.
    """
    if not text:
        return []

    lines = text.split("\n")
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    section_starts: List[int] = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            section_starts.append(line_offsets[i])
    if not section_starts or section_starts[0] != 0:
        section_starts.insert(0, 0)

    boundaries = section_starts + [len(text)]
    chunks: List[Chunk] = []
    for i in range(len(boundaries) - 1):
        start, end = boundaries[i], boundaries[i + 1]
        if text[start:end].strip():
            chunks.extend(
                _split_oversized(file_path, text, start, end, max_chunk_size)
            )
    return chunks


def chunk_text(
    file_path: str,
    text: str,
    max_chunk_size: int = 2000,
) -> List[Chunk]:
    """Generic fallback: paragraph-aware sliding window."""
    if not text:
        return []
    return _split_oversized(file_path, text, 0, len(text), max_chunk_size)


def chunk_file(
    file_path: str,
    text: str,
    max_chunk_size: int = 2000,
) -> List[Chunk]:
    """Dispatch to the right chunker based on file extension."""
    lower = file_path.lower()
    if lower.endswith(".py"):
        return chunk_python(file_path, text, max_chunk_size)
    if lower.endswith((".md", ".markdown", ".rst")):
        return chunk_markdown(file_path, text, max_chunk_size)
    return chunk_text(file_path, text, max_chunk_size)

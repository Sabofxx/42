"""Filesystem ingestion: walk the repository and collect files to index."""

from __future__ import annotations

import os
from typing import Iterator, List, Tuple

from tqdm import tqdm

ALLOWED_EXTENSIONS = (".py", ".md", ".markdown", ".rst", ".txt")
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "build",
    "dist",
    ".tox",
}


def iter_files(root: str) -> Iterator[str]:
    """Yield absolute paths of indexable files under ``root``."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith(ALLOWED_EXTENSIONS):
                yield os.path.join(dirpath, name)


def read_file_safely(path: str) -> str:
    """Read a file as UTF-8, ignoring decoding errors."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def collect_files(root: str, relative_to: str | None = None) -> List[Tuple[str, str]]:
    """Return a list of (relative_path, content) for every indexable file."""
    base = relative_to or root
    files: List[Tuple[str, str]] = []
    paths = list(iter_files(root))
    for abs_path in tqdm(paths, desc="Reading files", unit="file"):
        text = read_file_safely(abs_path)
        if not text.strip():
            continue
        rel = os.path.relpath(abs_path, base)
        files.append((rel, text))
    return files

"""BM25 + optional dense (sentence-transformers) indexing and retrieval.

The index stores chunks in a sidecar JSON file. BM25 is built with bm25s for
speed. Dense embeddings are optional and used only for the bonus hybrid
retrieval path. We never call out to a remote service.
"""

from __future__ import annotations

import json
import os
import pickle
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple

import numpy as np
from tqdm import tqdm

from .chunking import Chunk, chunk_file
from .ingest import collect_files
from .tokenizer import tokenize, tokenize_batch

try:
    import bm25s  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "bm25s is required. Install it via `uv sync`."
    ) from exc


CHUNKS_FILENAME = "chunks.json"
BM25_DIRNAME = "bm25_index"
DENSE_DIRNAME = "dense_index"
META_FILENAME = "meta.json"


class KnowledgeBase:
    """Indexed knowledge base with BM25 and optional dense embeddings."""

    def __init__(
        self,
        chunks: List[Chunk],
        bm25: "bm25s.BM25",
        dense_embeddings: Optional[np.ndarray] = None,
        embedder_name: Optional[str] = None,
    ) -> None:
        self.chunks = chunks
        self.bm25 = bm25
        self.dense_embeddings = dense_embeddings
        self.embedder_name = embedder_name
        self._embedder = None  # lazy

    # ---------- building ----------

    @classmethod
    def build(
        cls,
        repo_root: str,
        max_chunk_size: int = 2000,
        use_embeddings: bool = False,
        embedder_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> "KnowledgeBase":
        """Walk ``repo_root``, chunk every file, build BM25 (and dense)."""
        print(f"[index] scanning {repo_root}")
        files = collect_files(repo_root, relative_to=repo_root)
        print(f"[index] {len(files)} files to chunk")

        chunks: List[Chunk] = []
        for rel_path, text in tqdm(files, desc="Chunking", unit="file"):
            chunks.extend(chunk_file(rel_path, text, max_chunk_size))
        print(f"[index] {len(chunks)} chunks created")

        corpus_tokens = tokenize_batch([c.text for c in chunks])
        bm25 = bm25s.BM25()
        bm25.index(corpus_tokens, show_progress=True)

        dense: Optional[np.ndarray] = None
        if use_embeddings:
            dense = _encode_corpus(chunks, embedder_name)

        return cls(chunks, bm25, dense, embedder_name if use_embeddings else None)

    # ---------- persistence ----------

    def save(self, directory: str) -> None:
        """Persist the index to disk."""
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, CHUNKS_FILENAME), "w", encoding="utf-8") as fh:
            json.dump([asdict(c) for c in self.chunks], fh)

        bm25_dir = os.path.join(directory, BM25_DIRNAME)
        os.makedirs(bm25_dir, exist_ok=True)
        self.bm25.save(bm25_dir)

        meta: Dict[str, Optional[str]] = {
            "embedder_name": self.embedder_name,
            "n_chunks": str(len(self.chunks)),
        }
        with open(os.path.join(directory, META_FILENAME), "w", encoding="utf-8") as fh:
            json.dump(meta, fh)

        if self.dense_embeddings is not None:
            os.makedirs(os.path.join(directory, DENSE_DIRNAME), exist_ok=True)
            np.save(
                os.path.join(directory, DENSE_DIRNAME, "embeddings.npy"),
                self.dense_embeddings,
            )

    @classmethod
    def load(cls, directory: str) -> "KnowledgeBase":
        """Load an index previously saved with ``save``."""
        with open(os.path.join(directory, CHUNKS_FILENAME), "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        chunks = [Chunk(**c) for c in raw]

        bm25_dir = os.path.join(directory, BM25_DIRNAME)
        bm25 = bm25s.BM25.load(bm25_dir, load_corpus=False)

        meta_path = os.path.join(directory, META_FILENAME)
        embedder_name: Optional[str] = None
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as fh:
                meta = json.load(fh)
                embedder_name = meta.get("embedder_name")

        dense: Optional[np.ndarray] = None
        dense_path = os.path.join(directory, DENSE_DIRNAME, "embeddings.npy")
        if os.path.exists(dense_path):
            dense = np.load(dense_path)

        return cls(chunks, bm25, dense, embedder_name)

    # ---------- retrieval ----------

    def search_bm25(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """Return (chunk_index, score) pairs from BM25 only."""
        if not query.strip():
            return []
        tokens = tokenize(query)
        if not tokens:
            return []
        docs, scores = self.bm25.retrieve(
            [tokens],
            k=min(k, len(self.chunks)),
            show_progress=False,
        )
        out: List[Tuple[int, float]] = []
        for idx, score in zip(docs[0], scores[0]):
            out.append((int(idx), float(score)))
        return out

    def _get_embedder(self) -> object:
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer  # type: ignore

            assert self.embedder_name is not None
            self._embedder = SentenceTransformer(self.embedder_name)
        return self._embedder

    def search_dense(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """Return (chunk_index, score) pairs using dense cosine similarity."""
        if self.dense_embeddings is None or self.embedder_name is None:
            return []
        embedder = self._get_embedder()
        q_vec = embedder.encode([query], normalize_embeddings=True)  # type: ignore
        sims = self.dense_embeddings @ q_vec[0]
        top_n = min(k, len(self.chunks))
        idxs = np.argpartition(-sims, top_n - 1)[:top_n]
        idxs = idxs[np.argsort(-sims[idxs])]
        return [(int(i), float(sims[i])) for i in idxs]

    def search_hybrid(
        self,
        query: str,
        k: int = 10,
        rrf_k: int = 60,
    ) -> List[Tuple[int, float]]:
        """Reciprocal Rank Fusion of BM25 and dense retrieval."""
        pool = max(k * 4, 20)
        bm25_hits = self.search_bm25(query, k=pool)
        dense_hits = self.search_dense(query, k=pool) if self.dense_embeddings is not None else []

        scores: Dict[int, float] = {}
        for rank, (idx, _) in enumerate(bm25_hits):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)
        for rank, (idx, _) in enumerate(dense_hits):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)

        if not scores:
            return []
        ranked = sorted(scores.items(), key=lambda x: -x[1])[:k]
        return ranked

    def search(
        self,
        query: str,
        k: int = 10,
        mode: str = "auto",
    ) -> List[Chunk]:
        """High-level retrieval returning chunks. ``mode`` ∈ {auto,bm25,dense,hybrid}."""
        if mode == "auto":
            mode = "hybrid" if self.dense_embeddings is not None else "bm25"
        if mode == "bm25":
            hits = self.search_bm25(query, k)
        elif mode == "dense":
            hits = self.search_dense(query, k)
        else:
            hits = self.search_hybrid(query, k)
        return [self.chunks[idx] for idx, _ in hits]


# ---------- helpers ----------


def _encode_corpus(chunks: List[Chunk], model_name: str) -> np.ndarray:
    """Encode chunks into normalized dense vectors."""
    from sentence_transformers import SentenceTransformer  # type: ignore

    print(f"[index] loading embedder {model_name}")
    model = SentenceTransformer(model_name)
    texts = [c.text for c in chunks]
    print(f"[index] encoding {len(texts)} chunks (this is the slow step)")
    vectors = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return np.asarray(vectors, dtype=np.float32)


__all__ = ["KnowledgeBase"]


# Keep pickle out of the public API; reserved for future caches.
_ = pickle  # noqa: F841

"""Command-line interface (Python Fire).

Commands:
    index            Build the knowledge-base index from a raw repository.
    search           Search a single query.
    search_dataset   Run a dataset of questions and save StudentSearchResults.
    answer           Answer a single question with retrieved context.
    answer_dataset   Generate answers for a saved search_results file.
    evaluate         Compute recall@k against ground truth.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from tqdm import tqdm

from .evaluate import evaluate as _evaluate
from .generator import get_generator
from .index import KnowledgeBase
from .models import (
    MinimalAnswer,
    MinimalSearchResults,
    MinimalSource,
    RagDataset,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)

DEFAULT_RAW_DIR = "data/raw/vllm-0.10.1"
DEFAULT_INDEX_DIR = "data/processed"
DEFAULT_OUTPUT_DIR = "data/output"


def _resolve_repo(raw_dir: str) -> str:
    """If ``raw_dir`` exists as-is use it; else try its only subdirectory."""
    if os.path.isdir(raw_dir):
        entries = [e for e in os.listdir(raw_dir) if not e.startswith(".")]
        subdirs = [
            os.path.join(raw_dir, e)
            for e in entries
            if os.path.isdir(os.path.join(raw_dir, e))
        ]
        if len(subdirs) == 1 and not any(
            f.endswith(".py") or f.endswith(".md")
            for f in entries
            if os.path.isfile(os.path.join(raw_dir, f))
        ):
            return subdirs[0]
    return raw_dir


class CLI:
    """RAG against the machine — student CLI."""

    def index(
        self,
        repo_path: str = DEFAULT_RAW_DIR,
        save_directory: str = DEFAULT_INDEX_DIR,
        max_chunk_size: int = 2000,
        use_embeddings: bool = False,
        embedder_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> str:
        """Build and save the index. Set ``use_embeddings=True`` for bonus hybrid."""
        repo = _resolve_repo(repo_path)
        if not os.path.isdir(repo):
            raise FileNotFoundError(f"repo not found: {repo}")
        kb = KnowledgeBase.build(
            repo_root=repo,
            max_chunk_size=max_chunk_size,
            use_embeddings=use_embeddings,
            embedder_name=embedder_name,
        )
        kb.save(save_directory)
        msg = f"Ingestion complete! Indices saved under {save_directory}/"
        print(msg)
        return msg

    def search(
        self,
        query: str,
        index_directory: str = DEFAULT_INDEX_DIR,
        k: int = 10,
        mode: str = "auto",
    ) -> str:
        """Search the index for a single query and print top-k sources."""
        kb = KnowledgeBase.load(index_directory)
        chunks = kb.search(query, k=k, mode=mode)
        sources = [
            MinimalSource(
                file_path=c.file_path,
                first_character_index=c.first_character_index,
                last_character_index=c.last_character_index,
            )
            for c in chunks
        ]
        out = json.dumps([s.model_dump() for s in sources], indent=2)
        print(out)
        return out

    def search_dataset(
        self,
        dataset_path: str,
        index_directory: str = DEFAULT_INDEX_DIR,
        save_directory: str = f"{DEFAULT_OUTPUT_DIR}/search_results",
        k: int = 10,
        mode: str = "auto",
    ) -> str:
        """Run retrieval over every question in a dataset."""
        with open(dataset_path, "r", encoding="utf-8") as fh:
            dataset = RagDataset.model_validate_json(fh.read())
        kb = KnowledgeBase.load(index_directory)

        results: list[MinimalSearchResults] = []
        for q in tqdm(dataset.rag_questions, desc="Searching", unit="q"):
            chunks = kb.search(q.question, k=k, mode=mode)
            retrieved = [
                MinimalSource(
                    file_path=c.file_path,
                    first_character_index=c.first_character_index,
                    last_character_index=c.last_character_index,
                )
                for c in chunks
            ]
            results.append(
                MinimalSearchResults(
                    question_id=q.question_id,
                    question=q.question,
                    retrieved_sources=retrieved,
                )
            )

        payload = StudentSearchResults(search_results=results, k=k)
        os.makedirs(save_directory, exist_ok=True)
        out_path = os.path.join(save_directory, os.path.basename(dataset_path))
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(payload.model_dump_json(indent=2))
        msg = f"Saved student_search_results to {out_path}"
        print(msg)
        return msg

    def answer(
        self,
        question: str,
        index_directory: str = DEFAULT_INDEX_DIR,
        k: int = 10,
        mode: str = "auto",
        max_context_length: int = 2000,
    ) -> str:
        """Retrieve context and generate an answer to a single question."""
        kb = KnowledgeBase.load(index_directory)
        chunks = kb.search(question, k=k, mode=mode)
        gen = get_generator(max_context_length=max_context_length)
        text = gen.generate(question, chunks)
        print(text)
        return text

    def answer_dataset(
        self,
        student_search_results_path: str,
        save_directory: str = f"{DEFAULT_OUTPUT_DIR}/search_results_and_answer",
        index_directory: str = DEFAULT_INDEX_DIR,
        max_context_length: int = 2000,
    ) -> str:
        """Generate answers for every question of a previously-saved search batch."""
        with open(student_search_results_path, "r", encoding="utf-8") as fh:
            search = StudentSearchResults.model_validate_json(fh.read())
        kb = KnowledgeBase.load(index_directory)
        gen = get_generator(max_context_length=max_context_length)

        chunks_by_offset = {
            (c.file_path, c.first_character_index, c.last_character_index): c
            for c in kb.chunks
        }
        answers: list[MinimalAnswer] = []
        print(f"Loaded {len(search.search_results)} questions from "
              f"{student_search_results_path}")
        for i, sr in enumerate(
            tqdm(search.search_results, desc="Answering", unit="q"), 1
        ):
            ctx = []
            for s in sr.retrieved_sources:
                key = (s.file_path, s.first_character_index, s.last_character_index)
                chunk = chunks_by_offset.get(key)
                if chunk is not None:
                    ctx.append(chunk)
            text = gen.generate(sr.question, ctx)
            answers.append(
                MinimalAnswer(
                    question_id=sr.question_id,
                    question=sr.question,
                    retrieved_sources=sr.retrieved_sources,
                    answer=text,
                )
            )
        print(f"Processed {len(answers)} of {len(search.search_results)} questions")

        out_payload = StudentSearchResultsAndAnswer(
            search_results=answers, k=search.k
        )
        os.makedirs(save_directory, exist_ok=True)
        out_path = os.path.join(
            save_directory, os.path.basename(student_search_results_path)
        )
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(out_payload.model_dump_json(indent=2))
        msg = f"Saved student_search_results_and_answer to {out_path}"
        print(msg)
        return msg

    def evaluate(
        self,
        student_results_path: str,
        dataset_path: str,
        k: int = 10,
        max_context_length: int = 2000,
    ) -> str:
        """Compute and print recall@1/3/5/10 against ground truth."""
        _ = (k, max_context_length)  # forwarded for compatibility
        report = _evaluate(student_results_path, dataset_path)
        text = report.pretty()
        print(text)
        return text


def main() -> None:
    """Entry point for ``python -m student``."""
    import fire  # type: ignore

    fire.Fire(CLI)

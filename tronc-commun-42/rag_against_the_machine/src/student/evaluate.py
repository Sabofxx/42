"""Recall@k evaluation against ground-truth source spans.

A retrieved source counts as a hit for a ground-truth source if they share
the same ``file_path`` and at least 5% character overlap (intersection over
ground-truth length).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List

from .models import (
    AnsweredQuestion,
    MinimalSource,
    RagDataset,
    StudentSearchResults,
)

OVERLAP_THRESHOLD = 0.05


@dataclass
class EvalReport:
    """Aggregate recall metrics over a dataset."""

    n_questions: int
    recall_at: Dict[int, float]

    def pretty(self) -> str:
        lines = [
            "Evaluation Results",
            "=" * 40,
            f"Questions evaluated: {self.n_questions}",
        ]
        for k in sorted(self.recall_at):
            lines.append(f"Recall@{k:>2}: {self.recall_at[k]:.3f}")
        return "\n".join(lines)


def overlap_ratio(retrieved: MinimalSource, truth: MinimalSource) -> float:
    """Return |retrieved ∩ truth| / |truth| if same file, else 0."""
    if retrieved.file_path != truth.file_path:
        return 0.0
    truth_len = max(1, truth.last_character_index - truth.first_character_index)
    lo = max(retrieved.first_character_index, truth.first_character_index)
    hi = min(retrieved.last_character_index, truth.last_character_index)
    inter = max(0, hi - lo)
    return inter / truth_len


def question_recall(
    retrieved: List[MinimalSource],
    truth: List[MinimalSource],
    k: int,
) -> float:
    """Recall@k for a single question."""
    if not truth:
        return 0.0
    top = retrieved[:k]
    found = 0
    for t in truth:
        for r in top:
            if overlap_ratio(r, t) >= OVERLAP_THRESHOLD:
                found += 1
                break
    return found / len(truth)


def evaluate(
    student_results_path: str,
    dataset_path: str,
    ks: tuple[int, ...] = (1, 3, 5, 10),
) -> EvalReport:
    """Compute recall@k for the student's search results."""
    with open(student_results_path, "r", encoding="utf-8") as fh:
        student = StudentSearchResults.model_validate_json(fh.read())
    with open(dataset_path, "r", encoding="utf-8") as fh:
        dataset = RagDataset.model_validate_json(fh.read())

    truth_by_id: Dict[str, List[MinimalSource]] = {}
    for q in dataset.rag_questions:
        if isinstance(q, AnsweredQuestion):
            truth_by_id[q.question_id] = q.sources

    sums: Dict[int, float] = {k: 0.0 for k in ks}
    n = 0
    for sr in student.search_results:
        truth = truth_by_id.get(sr.question_id)
        if not truth:
            continue
        n += 1
        for k in ks:
            sums[k] += question_recall(sr.retrieved_sources, truth, k)
    avg = {k: (sums[k] / n if n else 0.0) for k in ks}
    return EvalReport(n_questions=n, recall_at=avg)


def evaluate_to_json(
    student_results_path: str,
    dataset_path: str,
    output_path: str | None = None,
) -> Dict[str, float]:
    """Run evaluation and optionally save a JSON report."""
    report = evaluate(student_results_path, dataset_path)
    payload: Dict[str, float] = {
        "n_questions": float(report.n_questions),
    }
    for k, v in report.recall_at.items():
        payload[f"recall@{k}"] = v
    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    return payload

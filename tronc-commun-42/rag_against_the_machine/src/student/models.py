"""Pydantic data models required by the RAG pipeline specification."""

from __future__ import annotations

import uuid
from typing import List, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class MinimalSource(BaseModel):
    """A minimal source: a slice of a file by character offsets."""

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """A question that has not been answered yet."""

    model_config = ConfigDict(populate_by_name=True)

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str = Field(
        validation_alias=AliasChoices("question", "question_str")
    )


class AnsweredQuestion(UnansweredQuestion):
    """A question with a ground-truth answer and its source slices."""

    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """A dataset of RAG questions (answered or unanswered)."""

    rag_questions: List[Union[AnsweredQuestion, UnansweredQuestion]]


class MinimalSearchResults(BaseModel):
    """Search results for a single question."""

    model_config = ConfigDict(populate_by_name=True)

    question_id: str
    question_str: str = Field(
        validation_alias=AliasChoices("question_str", "question")
    )
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Search results enriched with a generated answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """Full batch of search results emitted by the student system."""

    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    """Batch of search results plus generated answers."""

    search_results: List[MinimalAnswer]  # type: ignore[assignment]

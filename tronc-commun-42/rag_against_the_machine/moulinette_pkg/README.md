# Moulinette

Evaluation system for RAG student submissions. Validates student search results and calculates recall metrics.

## Installation

```bash
uv venv && uv sync
direnv allow  # or source .envrc
```

## CLI Commands

### evaluate_student_search_results

Evaluate student search results against ground truth dataset.

```bash
uv run python -m moulinette evaluate_student_search_results \
    <student_results_path> \
    <dataset_path> \
    [--k K] \
    [--max_context_length MAX_LENGTH] \
    [--threshold THRESHOLD]
```

**Arguments:**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `student_results_path` | str | required | Path to student search results JSON |
| `dataset_path` | str | required | Path to ground truth dataset JSON |
| `--k` | int | 10 | Maximum number of sources per question |
| `--max_context_length` | int | 2000 | Maximum context length per source |
| `--threshold` | float | None | If set, check Recall@5 against this value (0.0–1.0) and print PASS/FAIL |

**Example:**
```bash
# Evaluate docs dataset
uv run python -m moulinette evaluate_student_search_results \
    ../data/output/search_results/dataset_docs_private.json \
    ../data/datasets/private/AnsweredQuestions/dataset_docs_private.json \
    --k 10 --max_context_length 2000 --threshold 0.80

# Evaluate code dataset
uv run python -m moulinette evaluate_student_search_results \
    ../data/output/search_results/dataset_code_private.json \
    ../data/datasets/private/AnsweredQuestions/dataset_code_private.json \
    --k 10 --max_context_length 2000 --threshold 0.50
```

**Output:**
- Validates student data format
- Calculates Recall@1, Recall@3, Recall@5, Recall@10
- If `--threshold` is set: prints `PASS` or `FAIL` with the Recall@5 value

### list_valid_questions

List which dataset questions have their sources successfully retrieved by the student.

```bash
uv run python -m moulinette list_valid_questions \
    <student_results_path> \
    <dataset_path> \
    [--k K] \
    [--require_all_sources BOOL] \
    [--minimal_iou_threshold FLOAT]
```

**Arguments:**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `student_results_path` | str | required | Path to student search results JSON |
| `dataset_path` | str | required | Path to ground truth dataset JSON |
| `--k` | int | 10 | Number of top results to consider |
| `--require_all_sources` | bool | True | If True, all sources must be found for VALID |
| `--minimal_iou_threshold` | float | 0.05 | Minimum IoU overlap to count a source as found |

**Example:**
```bash
uv run python -m moulinette list_valid_questions \
    ../data/output/search_results/dataset_docs_private.json \
    ../data/datasets/private/AnsweredQuestions/dataset_docs_private.json \
    --k 10
```

**Output:**
- Lists each question as `[VALID]` or `[INVALID]` with question text
- Summary count of valid/total questions

### evaluate_student_answers

Evaluate student-generated answers (not yet implemented).

```bash
uv run python -m moulinette evaluate_student_answers <student_answer_path>
```

## Pass Criteria

| Dataset | Metric | Threshold |
|---------|--------|-----------|
| Docs | Recall@5 | >= 80% |
| Code | Recall@5 | >= 50% |

## IoU Overlap Threshold

A source is considered "found" if the Intersection over Union (IoU) between the
student's retrieved chunk and the ground-truth source exceeds **5%**. This threshold
is consistent across all commands.

## Build Instructions

To rebuild standalone binaries for distribution:

```bash
./build.sh
```

This produces `moulinette-fedora` and `moulinette-ubuntu` executables via Docker + PyInstaller.

## Input File Formats

### Student Search Results (`student_results_path`)
```json
{
  "search_results": [
    {
      "question_id": "uuid",
      "question_str": "What is the question text?",
      "retrieved_sources": [
        {
          "file_path": "path/to/file",
          "first_character_index": 0,
          "last_character_index": 500
        }
      ]
    }
  ],
  "k": 10
}
```

### Ground Truth Dataset (`dataset_path`)
```json
{
  "rag_questions": [
    {
      "question_id": "uuid",
      "question": "What is...",
      "answer": "The answer is...",
      "sources": [
        {
          "file_path": "path/to/file",
          "first_character_index": 0,
          "last_character_index": 500
        }
      ]
    }
  ]
}
```

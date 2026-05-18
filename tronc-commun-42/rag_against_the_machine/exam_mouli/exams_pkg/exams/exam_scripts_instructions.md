# Exam Scripts Instructions — Corrector Guide

This document explains how to use the exam scripts during correction of
Project 2: RAG Against the Machine. All exam scripts are located in `exams/scripts/`.

---

## Prerequisites

Before running any exam script:

1. **Install student dependencies**:
   ```bash
   cd student && uv sync
   ```

2. **Unzip private datasets** (if not already done):
   ```bash
   unzip data/datasets/datasets_private.zip -d data/datasets/
   ```

3. **Verify student code** does not import moulinette packages:
   ```bash
   grep -rn "moulinette" student/ --include="*.py"
   ```

4. **Set up moulinette** (pick one):
   - **Using the binary**: `moulinette-ubuntu` or `moulinette-fedora` from the moulinette zip
   - **Using the source**: `cd moulinette && uv sync`

---

## Recommended Correction Flow (~35 min)

The scale is designed so the automated retrieval pipeline runs in the background
while you inspect code. Follow this flow:

1. **Q1**: Preliminaries — git repo, uv sync, unzip private datasets
2. **Q2**: Launch `exam_retrieval.sh` in a **background terminal** (~8 min)
3. **Q3**: Code quality & Pydantic models review (while pipeline runs)
4. **Q4**: Chunking strategies — ask student to show 2 strategies
5. **Q5**: Retrieval system — live demo with a search query
6. **Q6**: Answer generation — run a test answer
7. **Q7a-d**: Check retrieval results from `exam_retrieval.sh` (should be done by now)
8. **Q8-Q8b**: Run `exam_answer.sh` — judge 3 answers
9. **Q9**: Student understanding — ask 5 questions
10. **Q10**: README documentation review
11. **Q11**: Run `exam_edge_cases.sh` (~1 min)
12. **Q12**: Bonus features review

---

## Exam Scripts Overview

| Script | Tests | Pass Criteria | Duration |
|--------|-------|---------------|----------|
| `exam_retrieval.sh` | Indexing, throughput, Recall@5 | All 4 tests pass | ~8 min |
| `exam_answer.sh` | Answer quality (semi-automated) | 2/3 answers satisfactory | ~5 min |
| `exam_edge_cases.sh` | Edge case handling | All 4 tests pass | ~1 min |

All scripts are run from the project root directory.
All scripts accept `--module-name NAME` to override the Python module name
(default: `src`). Use this if the student named their module differently.

---

## 1. Retrieval Exam (`exams/scripts/exam_retrieval.sh`)

### What it tests

| Test # | Name | Criterion |
|--------|------|-----------|
| 1 | Indexing | Completes in <= 300s (5 min) |
| 2 | Warm retrieval throughput | 200 questions in <= 90s |
| 3 | Docs Recall@5 | >= 80% |
| 4 | Code Recall@5 | >= 50% |

### How to run

```bash
# Using moulinette source directory
./exams/scripts/exam_retrieval.sh \
    --student-path ./student \
    --moulinette-path ./moulinette

# Using moulinette binary
./exams/scripts/exam_retrieval.sh \
    --student-path ./student \
    --moulinette-path ./moulinette-ubuntu
```

### Output

The script prints exact Recall@5 values and a star rating reference table.
Use these values for Q7b (docs excellence) and Q7d (code excellence) star ratings.

### Results directory

```
evaluations/retrieval/<YYYY-MM-DD_HH-MM-SS>/
  indexing_stdout.log       # Indexing output
  indexing_stderr.log       # Indexing errors
  search_docs_stdout.log    # Docs search output
  search_code_stdout.log    # Code search output
  search_results/           # Student search result files
  docs_eval.log             # Moulinette evaluation (docs)
  code_eval.log             # Moulinette evaluation (code)
  summary.log               # Per-test PASS/FAIL
```

---

## 2. Answer Exam (`exams/scripts/exam_answer.sh`)

### What it tests

Uses `list_valid_questions` to show which questions have their sources correctly
retrieved, then lets you pick 3 questions to test answer generation.

### How to run

```bash
# Interactive mode (pick questions during run)
./exams/scripts/exam_answer.sh \
    --student-path ./student \
    --moulinette-path ./moulinette

# Pre-selected questions
./exams/scripts/exam_answer.sh \
    --student-path ./student \
    --moulinette-path ./moulinette \
    --questions "What is PagedAttention?,How to deploy vLLM?,What models does vLLM support?"
```

### Pass criteria

2 out of 3 answers must be satisfactory. A satisfactory answer:
- Addresses the question asked
- Contains relevant information from the vLLM codebase
- Is coherent and understandable

---

## 3. Edge Cases Exam (`exams/scripts/exam_edge_cases.sh`)

### What it tests

| Test # | Name | Input |
|--------|------|-------|
| 1 | Empty query | `search "" --k 10` |
| 2 | Gibberish query | `search "asdfghjkl" --k 10` |
| 3 | k=0 | `answer "What is vLLM?" --k 0` |
| 4 | Bad dataset path | `search_dataset --dataset_path /nonexistent.json` |

### How to run

```bash
./exams/scripts/exam_edge_cases.sh --student-path ./student
```

### Pass criteria

All 4 tests must complete without Python tracebacks. The program may print
error messages or return empty results — that is acceptable. What is NOT
acceptable is an unhandled exception with a traceback.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `uv sync` fails | Check Python version matches `.python-version` |
| Private datasets missing | Run `unzip data/datasets/datasets_private.zip -d data/datasets/` |
| Moulinette binary not executable | Run `chmod +x moulinette-ubuntu` |
| Search results not found | Check `data/output/search_results/` for output files |
| Indexing too slow | May indicate missing index caching; check with student |
| Edge case test hangs | The student may have an infinite loop; Ctrl+C and mark as FAIL |

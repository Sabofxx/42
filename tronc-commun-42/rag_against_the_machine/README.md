*This project has been created as part of the 42 curriculum by omischle.*

# RAG against the machine

## Description

A Retrieval-Augmented Generation (RAG) system that answers questions about the
[vLLM](https://github.com/vllm-project/vllm) codebase. It ingests the
repository, builds a searchable index, retrieves the most relevant code or
documentation snippets for a given question, and generates a grounded answer
using `Qwen/Qwen3-0.6B`.

The pipeline targets the project requirements:

- Indexing time ≤ 5 minutes
- Cold start latency ≤ 60 s
- Warm retrieval ≤ 90 s for 1000 questions
- Recall@5 ≥ 80% on docs, ≥ 50% on code

## Instructions

```bash
# 1. Install (uv is mandatory)
make install
# or:  uv venv && uv sync
source .venv/bin/activate

# 2. Drop the vLLM zip into data/raw/ and unzip
mkdir -p data/raw && unzip vllm-0.10.1.zip -d data/raw

# 3. Drop the public datasets next to it
unzip datasets_public.zip -d data/

# 4. Index (BM25 only, fast)
uv run python -m student index --max_chunk_size 2000

# 4-bis. Index with bonus hybrid retrieval (BM25 + dense embeddings)
uv run python -m student index --use_embeddings True

# 5. Search a single query
uv run python -m student search "How to configure OpenAI server?" --k 10

# 6. Search a whole dataset
uv run python -m student search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 \
    --save_directory data/output/search_results

# 7. Generate answers from the search results
uv run python -m student answer_dataset \
    --student_search_results_path data/output/search_results/dataset_docs_public.json \
    --save_directory data/output/search_results_and_answer

# 8. Evaluate (recall@k)
uv run python -m student evaluate \
    --student_results_path data/output/search_results/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json
```

The `Makefile` exposes the lint/run/clean rules required by the subject.

## System architecture

```
              ┌────────────────────┐
 raw repo ──▶ │  ingest + chunking │── chunks ──┐
              └────────────────────┘            │
                                                ▼
                                         ┌──────────────┐
                                         │  BM25 index  │
                                         │  (bm25s)     │
                                         └──────────────┘
                                                │
                                  (bonus)       ▼
                                         ┌──────────────┐
                                         │ dense vectors│
                                         │ MiniLM-L6-v2 │
                                         └──────────────┘
                                                │
                            ┌───────────────────┴─────────────────┐
              query ─────▶  │  hybrid retrieval (RRF fusion)      │ ──▶ top-k
                            └───────────────────┬─────────────────┘
                                                │
                                         ┌──────▼──────┐
                            question ──▶ │ Qwen3-0.6B  │ ──▶ grounded answer
                                         └─────────────┘
```

Modules:

- `ingest.py` walks the repo, keeps `.py / .md / .rst / .txt`.
- `chunking.py` AST chunking for Python, header chunking for Markdown, with a
  sliding-window fallback when a chunk exceeds the configured maximum.
- `tokenizer.py` simple identifier-friendly tokenizer (camelCase / snake_case
  splitting, lowercasing, stopword removal).
- `index.py` builds and persists BM25 + optional dense embeddings, exposes
  `search_bm25`, `search_dense`, `search_hybrid`.
- `generator.py` Qwen3-0.6B with a strict context-grounded chat prompt.
- `evaluate.py` recall@k with the official 5% overlap rule.
- `cli.py` Python Fire CLI exposing the six required commands.

## Chunking strategy

- **Python files** are parsed with `ast`. Each top-level function, class, and
  the module-level preamble form an independent chunk so identifiers stay
  packed with their surrounding code. Chunks longer than `max_chunk_size`
  (default 2000 characters) are sub-split with a 10 % sliding overlap.
- **Markdown / docs** are split on ATX headers (`#`, `##`, …). Each section
  becomes a chunk; oversized sections fall back to the same sliding-window
  splitter.
- Every chunk records the *exact* `first_character_index` and
  `last_character_index` of the original file, which is what the recall@k
  overlap check compares against.

## Retrieval method

Two retrievers, plus a fusion mode:

- **BM25** via [`bm25s`](https://github.com/xhluca/bm25s). Identifier-aware
  tokenizer; corpus and query share the same tokenization path.
- **Dense** (bonus): `sentence-transformers/all-MiniLM-L6-v2` embeddings,
  normalized, cosine similarity computed with a single matmul over the
  in-memory matrix.
- **Hybrid** (bonus): Reciprocal Rank Fusion (`1 / (k + rank)`, `k = 60`) of
  the two ranked lists. Hybrid is selected automatically when dense vectors
  are available; otherwise the system falls back to pure BM25.

## Performance analysis

With BM25 only on the public datasets:

| Dataset | Recall@1 | Recall@3 | Recall@5 | Recall@10 |
|---------|---------:|---------:|---------:|----------:|
| docs    | ~0.55    | ~0.74    | ~0.82    | ~0.90     |
| code    | ~0.30    | ~0.45    | ~0.55    | ~0.68     |

Hybrid retrieval typically lifts Recall@5 by 3–6 points on docs and 5–10 on
code questions (where naming variation hurts BM25). Re-run `evaluate` after
indexing to print fresh numbers.

## Design decisions

- **`bm25s` over `rank_bm25`**: 10–100× faster indexing and retrieval, fits the
  5-minute budget on the full vLLM repo.
- **Tokenizer co-designed for code**: splitting camelCase and snake_case makes
  identifiers actually match between query and code.
- **AST chunking** keeps function/class boundaries aligned with the offsets the
  evaluator expects, avoiding chunks that straddle two unrelated symbols.
- **RRF for hybrid fusion**: parameter-free, robust to score-scale differences
  between BM25 and cosine similarity.
- **Singleton answer generator** so we only pay the model load cost once per
  process (`get_generator`).
- **Lazy model loading**: the BM25-only retrieval path never imports `torch`
  or `transformers`.

## Challenges faced

- vLLM contains many large Python files and notebooks. The AST splitter must
  fall back to text chunking when a file isn't parseable.
- The recall@k overlap rule operates on raw character offsets, so chunking and
  offsets must be lossless. The code stores absolute offsets at every step.
- `Qwen3-0.6B` ships with a "thinking" chat template that bloats the prompt;
  we disable it (`enable_thinking=False`) to keep generation deterministic
  and fast.

## Example usage

```bash
uv run python -m student answer "How does vLLM serve OpenAI-compatible APIs?" --k 5
```

Output (truncated):

```
vLLM exposes an OpenAI-compatible HTTP API via `vllm/entrypoints/openai/api_server.py`.
Start it with `python -m vllm.entrypoints.openai.api_server --model <model>`.
The server implements /v1/chat/completions, /v1/completions, and /v1/embeddings ...
```

## Resources

- vLLM project documentation: <https://docs.vllm.ai>
- BM25 reference: Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond* (2009).
- `bm25s`: <https://github.com/xhluca/bm25s>
- Sentence-transformers: <https://www.sbert.net>
- Reciprocal Rank Fusion: Cormack et al., SIGIR 2009.

### AI usage

AI tooling (Claude) was used to scaffold the project skeleton (CLI shape,
pyproject, Makefile) and to review the chunking and retrieval logic. Every
generated line was read, edited, and validated against the project spec; the
evaluation logic, tokenizer, and chunking heuristics were tested locally
against the public datasets.

## Bonus features implemented

- ✅ **Hybrid retrieval** (BM25 + dense, RRF fusion) — `--use_embeddings True` at index time, `--mode hybrid` at search.
- ✅ **Semantic embeddings** (sentence-transformers MiniLM-L6-v2).
- ✅ **Result/index caching** — index persisted to disk; re-loads instantly.
- ✅ **Identifier-aware tokenization** acts as a lightweight query expansion
  for camelCase / snake_case identifiers.

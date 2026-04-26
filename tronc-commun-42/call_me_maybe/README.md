*This project has been created as part of the 42 curriculum by omischle.*

# Call Me Maybe

## Description

**Call Me Maybe** is a function-calling tool that turns natural-language
requests into structured, machine-executable function calls. Given a
prompt such as *"What is the sum of 2 and 3?"*, it does **not** answer
the question directly — instead it picks the right function from a
schema and extracts its arguments with the correct types:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": { "a": 2.0, "b": 3.0 }
}
```

The core challenge is reliability. Small models such as
`Qwen/Qwen3-0.6B` (~600M parameters) only emit valid JSON ~30 % of the
time when prompted naively. This project solves that with **constrained
decoding**: at every generation step, the model's logits are intercepted
and invalid tokens are removed from the candidate set. The output is
syntactically valid JSON *and* schema-compliant **by construction**,
regardless of the model size.

## Instructions

### Prerequisites

- Python **3.10** or later
- [`uv`](https://github.com/astral-sh/uv) package manager

### Setup

```bash
git clone https://github.com/Sabofxx/42.git
cd 42/tronc-commun-42/call_me_maybe

uv sync          # the only command an evaluator needs to run
```

`uv sync` reads `pyproject.toml`, installs `numpy` and `pydantic`, and
pulls the local `llm_sdk` package (which itself brings the Hugging Face
runtime). The `llm_sdk/` directory must sit next to `src/`.

### Running the program

```bash
# Default — reads data/input/, writes data/output/
make run
# or
uv run python -m src

# Custom paths (the three flags described in the subject)
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input                data/input/function_calling_tests.json \
  --output               data/output/function_calling_results.json
```

### Makefile targets

| Command | Description |
|---|---|
| `make install` | Install dependencies via `uv sync` |
| `make run` | Run the main script |
| `make debug` | Run the main script under `pdb` |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, `.pytest_cache` |
| `make lint` | `flake8 .` + `mypy .` with the subject's exact flags |
| `make lint-strict` | `flake8 .` + `mypy . --strict` |
| `make test` | Run the `pytest` test suite |

### Input format

`data/input/function_calling_tests.json` — a JSON array of prompts:
```json
[
  { "prompt": "What is the sum of 2 and 3?" },
  { "prompt": "Greet shrek" },
  { "prompt": "Reverse the string 'hello'" }
]
```

`data/input/functions_definition.json` — a JSON array of function
definitions:
```json
[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": {
      "a": { "type": "number" },
      "b": { "type": "number" }
    },
    "returns": { "type": "number" }
  }
]
```

### Output format

`data/output/function_calling_results.json`:
```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": { "a": 2.0, "b": 3.0 }
  },
  {
    "prompt": "Greet shrek",
    "name": "fn_greet",
    "parameters": { "name": "shrek" }
  }
]
```

The keys are exactly `prompt`, `name`, `parameters` as required by the
subject (Section V.4).

## Algorithm explanation — Constrained Decoding

### The problem

LLMs generate text one token at a time. At each step, the model emits a
**logit vector** of size ≈ 150 000 (one score per vocabulary token).
Picking the highest score yields fluent natural language, but not
necessarily structurally valid JSON.

### The solution — token-level masking

Constrained decoding intervenes **before** token selection. Tokens that
would break the required JSON structure or schema are excluded from the
argmax:

```
1. Model emits logits for all ~150k tokens
2. The decoder asks the state (trie / type) which tokens are valid now
3. argmax is computed over the valid set only
4. The chosen token is appended; repeat from step 1
```

The output is therefore always a parseable JSON object that matches the
declared schema — not a statistical property, but a structural
invariant.

### Two-phase generation

**Phase 1 — Function selection** (`select_function`)
A trie indexed by token IDs is built from the legal function names.
Walking down the trie, only the children of the current node are
allowed at each step. The output is guaranteed to be one of the
declared function names.

**Phase 2 — Argument extraction** (`generate_argument`)
For every parameter declared by the chosen function, the decoder
enforces the expected type:

- `number` — the first token must come from the cached "number-start"
  set (digit or `-`); subsequent tokens are accepted as long as their
  textual form is made of digits, `.` or `-`. The value is rebuilt with
  `float(model.decode(...))`.
- `string` — tokens are accepted until the next argmax contains a
  closing quote or a newline. A hard cap of 64 tokens prevents runaway
  generation.
- `boolean` — only the token IDs of `true` and `false` are allowed.

Each argument is generated in its own constrained pass with a small
dedicated sub-prompt, which keeps selection quality high even on a
0.6 B-parameter model.

## Design decisions

- **Pydantic everywhere** — `FunctionDefinition`, `FunctionCallTest` and
  `FunctionCallResult` validate every input and output, so malformed
  files produce a clear error rather than a silent crash.
- **Vocabulary inversion is computed once** in `VocabularyMapper`, and
  the set "tokens that may start a number" is cached too, so generation
  scales with the size of the valid set, not the size of the
  vocabulary.
- **Trie-based selection** — `O(depth)` per step instead of `O(vocab)`,
  and structurally impossible to emit an unknown function name.
- **Greedy decoding within the valid set** — sampling adds nothing once
  the constraint set has filtered invalid choices; greedy is faster and
  fully deterministic.
- **Argument-by-argument generation** — each argument is produced in a
  fresh constrained pass, which avoids compounding errors on functions
  with multiple parameters (e.g., `fn_substitute_string_with_regex`).
- **Lazy SDK imports** (`TYPE_CHECKING`) — unit tests on the trie /
  models / utils run without pulling the full Hugging Face runtime.
- **No `dspy`, `outlines`, `transformers`, `huggingface_hub` or `torch`
  in `src/`** — only the public methods of the provided `llm_sdk`
  (`encode`, `decode`, `get_logits_from_input_ids`,
  `get_path_to_vocab_file`) are used, as required by the subject.

## Performance analysis

| Metric | Target | Achieved |
|---|---|---|
| JSON syntactic validity | 100 % | **100 %** (by construction) |
| Schema compliance | 100 % | **100 %** (by construction) |
| Function-selection accuracy | 90 %+ | ~95 % |
| Total runtime, 11 prompts (CPU) | < 5 min | ~2-3 min |
| Total runtime, 11 prompts (MPS / CUDA) | < 5 min | ~30-60 s |

JSON validity and schema compliance are not statistical metrics — they
are structural invariants enforced by the decoder. The remaining error
budget is on semantic understanding (which function and which substring
to extract), which is inherent to a 0.6 B model.

## Challenges faced

- **BPE tokenization of function names** — names like
  `fn_substitute_string_with_regex` are split into many sub-tokens.
  The trie operates at the token level, which lets multi-token names
  be reconstructed transparently. Prefix collisions
  (e.g. `fn_get` vs `fn_get_square_root`) are handled by requiring the
  trie path to terminate on a *leaf*, not on any terminal node.
- **Multi-token numeric literals** — a number like `265.0` is split into
  several tokens (`265`, `.`, `0`). The decoder accepts the first
  token from the cached "number-start" set, then keeps going as long as
  the textual form of the argmax token is made of digits, `.` or `-`.
- **String termination** — the decoder stops as soon as the argmax
  token contains a `"` or a newline. A hard cap (64 tokens) protects
  against runaway loops on prompts the model misinterprets.
- **Prompt design for a 0.6 B model** — small models are prompt-
  sensitive. A per-argument sub-prompt (`Extract the value of the
  argument 'X' of type Y. Answer with only the value:`) was the simplest
  way to keep selection quality high without breaking the constrained-
  decoding contract.
- **Performance vs. correctness trade-off** — the first version masked
  the full ~150 k-entry logit vector to `-inf` for every step.
  Replacing that with `_argmax_masked` (iterating over the valid set
  only) makes function-name generation roughly an order of magnitude
  faster on CPU.

## Testing strategy

The `tests/` directory holds pytest unit tests, run with `make test`:

- `test_models.py` — Pydantic validation of every model, including the
  `prompt` / `name` / `parameters` output schema demanded by the
  subject.
- `test_utils.py` — JSON loading & writing: missing file, invalid JSON,
  not-an-array, schema mismatch, nested output directories.
- `test_trie.py` — `FunctionTrie`: insertion, traversal, prefix
  collisions, unknown-token handling.

The trie / models / utils tests do not depend on `torch`, so they run
in milliseconds. The end-to-end pipeline is validated manually by
running `make run` against the provided example inputs and checking
that every prompt produces a JSON object whose structure matches
`{prompt, name, parameters}` with the right value types.

## Example usage

```bash
$ uv run python -m src
Loaded 5 function definitions and 11 prompts.
Initializing LLM...
LLM ready.
Function selected: fn_add_numbers
Function selected: fn_add_numbers
Function selected: fn_greet
...
Total time: 42.13 seconds
Wrote 11 entries to data/output/function_calling_results.json.
```

| Prompt | name | parameters |
|---|---|---|
| `"What is the sum of 2 and 3?"` | `fn_add_numbers` | `{"a": 2.0, "b": 3.0}` |
| `"Greet shrek"` | `fn_greet` | `{"name": "shrek"}` |
| `"Reverse the string 'hello'"` | `fn_reverse_string` | `{"s": "hello"}` |
| `"What is the square root of 16?"` | `fn_get_square_root` | `{"a": 16.0}` |
| `"Replace all vowels in 'Programming is fun' with asterisks"` | `fn_substitute_string_with_regex` | `{"source_string": "Programming is fun", "regex": "[aeiouAEIOU]", "replacement": "*"}` |

## Resources

- [Qwen3-0.6B Model Card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Hugging Face Transformers — Generation strategies](https://huggingface.co/docs/transformers/main/en/generation_strategies)
- [Efficient Guided Generation for LLMs — Willard & Louf, 2023](https://arxiv.org/abs/2307.09702)
- [Byte-Pair Encoding — Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
- [JSON Schema Specification](https://json-schema.org/specification)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [uv — Python package manager](https://github.com/astral-sh/uv)

### AI usage in this project

| Task | Tool | Where |
|---|---|---|
| Brainstorming the constrained-decoding design | Claude / ChatGPT | Research and design phase |
| Reviewing the JSON state-machine logic | Claude | `src/constrained_dec.py` — read, rewritten and validated by hand |
| Drafting README sections | Claude | This file — reviewed and completed manually |

All AI-generated content was reviewed, understood and validated before
inclusion. No code was copied without full comprehension.

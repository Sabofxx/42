*This project has been created as part of the 42 curriculum by omischle, lel-ouaz.*

# Agent Smith

## Description

Agent Smith is a Python 3.10 code-agent framework for the 42 Agent Smith project. It implements a Thought -> Code -> Observation loop where an LLM writes Python code, the code runs inside a constrained sandbox, and sandbox observations are fed back to the model until it calls `final_answer(...)`.

The project targets two evaluation tracks:

- MBPP: generate a Python function and validate it with public tests before submission.
- SWE-bench: inspect and patch a Dockerized repository, then submit `git -c core.fileMode=false diff`.

## System Architecture

The repository is split into small, testable layers:

- `agent_smith/agent.py`: benchmark-agnostic orchestration loop and `SolutionOutput` generation.
- `agent_smith/llm.py`: OpenAI-compatible chat-completions client with token accounting and API-key rotation.
- `agent_smith/extraction.py`: Python code extraction plus XML, JSON/Hermes, and ReAct tool-call conversion.
- `agent_smith/sandbox.py`: process-isolated execution with restricted builtins, import allowlist, path allowlist, timeout, memory limits, and MCP tool proxies.
- `agent_smith/mcp_client.py`: stdio and streamable HTTP MCP client wrapper.
- `mcp_tools_mbpp.py`: MBPP MCP server.
- `mcp_tools_swebench.py`: mandatory SWE-bench MCP server.
- `agent_mbpp.py` and `agent_swebench.py`: moulinette-compatible CLIs.

## Agent Loop

Each step follows the same flow:

1. Send the system prompt, task prompt, and previous observations to the configured model.
2. Extract executable Python from the model response.
3. Execute the code in the sandbox.
4. Capture stdout, stderr, errors, timeout status, truncation status, and `final_answer`.
5. Append a `StepMetrics` entry containing raw LLM output, sandbox input, sandbox output, tokens, latency, retries, API URL, and model name.
6. Stop only when `final_answer(...)` is captured or the iteration limit is reached.

The system prompts explicitly forbid external solution lookup and require tool-based exploration.

## Sandbox Design

The sandbox runs generated code in a child process. The child receives only:

- restricted builtins;
- an allowlisted `__import__`;
- a path-checked `open`;
- dynamically discovered MCP tool wrappers;
- the built-in `final_answer`.

The parent process enforces timeout termination and mediates MCP calls. MCP tools run outside the sandbox boundary, while generated Python stays constrained by `SandboxConfig`.

Default configuration is in `sandbox_template.json`.

## Tool Implementation Details

MBPP tools:

- `describe_task()`
- `public_tests()`
- `run_tests(candidate_code="")`

SWE-bench tools:

- `read_file(filepath, start_line, end_line)`
- `edit_file(filepath, old_str, new_str)`
- `list_files(directory, pattern)`
- `search_code(pattern, file_pattern)`
- `search_function_or_class_definition_in_code(name)`
- `find_references(name, filepath, line)`
- `run_tests()`
- `get_patch()`
- `run_command(command, workdir)`

The SWE-bench server supports host mode through `AGENT_SMITH_TESTBED_PATH` or `/testbed`, and Docker mode through the task JSON `docker_image`.

## Instructions

Install dependencies (run in both the project root and the `moulinette/` subdir):

```bash
uv sync
cd moulinette && uv sync && cd ..
mkdir -p cache
```

If `uv run moulinette_eval` fails with `ModuleNotFoundError: No module named 'moulinette'`, the moulinette wheel did not install the package source. Prefix every `moulinette_eval` invocation with `PYTHONPATH=.` while inside the `moulinette/` directory:

```bash
cd moulinette
PYTHONPATH=. uv run moulinette_eval dump mbpp --output ../cache/mbpp_task.json
```

Configure API keys via environment variables. Supported names include `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `TOGETHER_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `FIREWORKS_API_KEY`, and `AGENT_SMITH_API_KEYS`. Multiple keys may be comma, colon, or newline separated. You can also drop them into a `.env` at the project root.

```bash
export GROQ_API_KEY="gsk_..."
# or
echo 'GROQ_API_KEY=gsk_...' >> .env
```

Run the sandbox:

```bash
uv run sandbox
uv run sandbox sandbox_template.json
uv run sandbox --mcp-stdio "python mcp_tools_mbpp.py" sandbox_template.json
uv run sandbox --mcp-server http://127.0.0.1:8000/mcp
```

### Sandbox smoke tests

Each command below is self-contained and exercises a specific sandbox behavior. Expected outcome is in the comment.

```bash
# 1. Nominal path: prints stdout and captures final_answer
printf 'print("hello")\nfinal_answer("ok")\n' | uv run sandbox sandbox_template.json

# 2. Allowed import (math is in sandbox_template.json::authorized_imports)
printf 'import math\nfinal_answer(str(math.sqrt(144)))\n' | uv run sandbox sandbox_template.json

# 3. Blocked import (os is NOT allowed -> ImportError)
printf 'import os\nprint(os.listdir("/"))\n' | uv run sandbox sandbox_template.json || true

# 4. Path allowlist (open outside allowed_directories -> PermissionError)
echo 'open("/etc/passwd").read()' | uv run sandbox sandbox_template.json || true

# 5. Execution timeout (kills after max_execution_time_seconds, default 30s)
printf 'while True:\n    pass\n' | uv run sandbox sandbox_template.json || true

# 6. Memory guard on bytearray (rejects allocations > max_memory_mb)
echo 'x = bytearray(10**12)' | uv run sandbox sandbox_template.json || true

# 7. Typical Python code with final_answer
printf 'def fib(n):\n    a,b=0,1\n    for _ in range(n): a,b=b,a+b\n    return a\nprint([fib(i) for i in range(10)])\nfinal_answer("done")\n' | uv run sandbox sandbox_template.json

# 8. MCP-backed sandbox (loads MBPP tools — describe_task, public_tests, run_tests)
uv run sandbox --mcp-stdio "python mcp_tools_mbpp.py" sandbox_template.json
```

### Provider/API key sanity check

```bash
# Verify the Groq key works end-to-end with the agent's exact payload shape
curl -s -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' | jq .

# List free OpenRouter models (when picking --model-name)
curl -s https://openrouter.ai/api/v1/models | jq -r '.data[].id' | grep -i free | head -30

# Confirm api_keys_for_provider picks up your env
uv run python -c "from agent_smith.env import api_keys_for_provider; print(len(api_keys_for_provider('https://api.groq.com/openai/v1')), 'key(s)')"
```

### Inspecting a solution

```bash
# Summary view
cat cache/mbpp_solution.json | jq '{success, iterations, total_output_tokens, error, solution}'

# Per-step LLM output and sandbox output
cat cache/mbpp_solution.json | jq '.steps[] | {step, llm_output, sandbox_output}'

# Just the error and model used (useful when the run failed silently)
cat cache/mbpp_solution.json | jq '.error, .steps[0].llm_output, .steps[0].model_name, .steps[0].api_url'
```

Run MBPP (single task):

```bash
cd moulinette
PYTHONPATH=. uv run moulinette_eval dump mbpp --output ../cache/mbpp_task.json

cd ..
uv run python -m agent_mbpp \
  --task-file cache/mbpp_task.json \
  --output cache/mbpp_solution.json \
  --model-name "llama-3.3-70b-versatile" \
  --provider-url "https://api.groq.com/openai/v1"

cd moulinette
PYTHONPATH=. uv run moulinette_eval validate mbpp ../cache/mbpp_task.json ../cache/mbpp_solution.json
```

Run MBPP in a loop (N random tasks, prints PASS/FAIL summary):

```bash
mkdir -p cache/loop
for i in 1 2 3 4 5; do
  (cd moulinette && PYTHONPATH=. uv run moulinette_eval dump mbpp --output ../cache/loop/task_$i.json)
  uv run python -m agent_mbpp \
    --task-file cache/loop/task_$i.json \
    --output cache/loop/sol_$i.json \
    --model-name "llama-3.3-70b-versatile" \
    --provider-url "https://api.groq.com/openai/v1"
  (cd moulinette && PYTHONPATH=. uv run moulinette_eval validate mbpp ../cache/loop/task_$i.json ../cache/loop/sol_$i.json | grep "^Overall:")
done
```

Run SWE-bench (requires Docker running — check with `docker ps`):

```bash
# 1. Dump a random SWE-bench task (downloads the repo Docker image on first run, ~1-3 GB)
cd moulinette
PYTHONPATH=. uv run moulinette_eval dump swebench --output ../cache/swebench_task.json

# 2. Optional: inspect the task
cd ..
cat cache/swebench_task.json | jq '{instance_id, repo, docker_image, problem_statement: (.problem_statement | .[0:300])}'

# 3. Run the agent. --max-retries is important: SWE-bench makes many LLM calls
#    and free-tier rate limits will otherwise kill the run after a few iterations.
uv run python -m agent_swebench \
  --task-file cache/swebench_task.json \
  --output cache/swebench_solution.json \
  --model-name "meta-llama/llama-4-scout-17b-16e-instruct" \
  --provider-url "https://api.groq.com/openai/v1" \
  --max-retries 5

# 4. Validate (spins up the docker container, applies the patch, runs the SWE-bench test suite)
cd moulinette
PYTHONPATH=. uv run moulinette_eval validate swebench ../cache/swebench_task.json ../cache/swebench_solution.json
```

A successful agent run produces a git diff in `cache/swebench_solution.json::solution` (starts with `diff --git ...`). A failed run with `success: false` and empty `solution` usually means the LLM rate-limited (HTTP 429), the prompt grew too big (HTTP 413), or the model didn't emit a code block — check `.error` and `.steps[-1].llm_output`.

### Model choice for SWE-bench

All combos below were executed end-to-end against task `sympy__sympy-19495` (real LLM calls + Docker container + SWE-bench test suite). The framework (`LLM → sandbox → MCP → Docker → tests`) is functional in every row; the variation is in how the model behaves and how the provider rate-limits.

| Provider  | Model                                          | Iters | Patch?   | Result                                                    |
|-----------|------------------------------------------------|-------|----------|-----------------------------------------------------------|
| Groq      | `llama-3.3-70b-versatile`                      | 4     | yes      | Patch produced, tests RESOLVED_NO. TPM 12K → 429 mid-run. |
| Groq      | `meta-llama/llama-4-scout-17b-16e-instruct`    | 18    | yes      | Best free Groq pick. Patch produced, RESOLVED_NO.         |
| Groq      | `meta-llama/llama-4-scout-17b-16e-instruct`    | 21    | no       | Killed by 429 mid-run on a different attempt.             |
| Groq      | `qwen/qwen3-32b`                               | 6     | no       | Reasoning model: wastes budget in `<think>` blocks.       |
| Groq      | `llama-3.1-8b-instant`                         | 5     | no       | HTTP 413 (cumulative prompt too big for 8B context).      |
| Groq      | `openai/gpt-oss-120b`                          | 1     | no       | HTTP 400 (rejected `stop` / `max_tokens` shape).          |
| Cerebras  | `gpt-oss-120b`                                 | 30    | no       | Explored for 9 min without ever editing. 334K input > 300K limit. |
| Cerebras  | `zai-glm-4.7`                                  | 30    | no       | Same pattern: full loop, no edit, no rescue.              |

Take-away: **the pipeline works; small free models do not converge on real SWE-bench bugs**. For the defense, demonstrate the framework on MBPP (5/5 reproducible) and on the verified SWE-bench run that produced a patch (`meta-llama/llama-4-scout-17b-16e-instruct`, 18 iters). For actually resolving SWE-bench tasks, switch to Claude 4 / GPT-4-class models via OpenRouter or direct provider.

### Live provider rate-limit inspection

Provider quotas are by minute (TPM) and by day (RPD). The headers tell you what's left without making a full call:

```bash
# Groq: TPM, RPM and reset windows per model
curl -s -D - -o /dev/null -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"meta-llama/llama-4-scout-17b-16e-instruct","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' \
  | grep -iE "ratelimit|retry-after|HTTP/"

# Cerebras: list models actually available for your account
curl -s "https://api.cerebras.ai/v1/models" -H "Authorization: Bearer $AGENT_SMITH_API_KEYS"

# OpenRouter: list free models
curl -s https://openrouter.ai/api/v1/models | jq -r '.data[].id' | grep -i free | head -30
```

Reduce `sandbox_template.json::max_output_chars` (default `5000`) further if you keep hitting HTTP 413; the SWE-bench `run_tests()` output is the usual culprit. Lower `history_pairs` in `agent_smith/agent.py::run_loop` (default `3`) to trim the cumulative prompt further.

### SWE-bench with Cerebras (free, no Groq rate-limit)

Cerebras Cloud has a generous free tier and the largest TPM/RPM among the free options. Sign up at https://cloud.cerebras.ai (Google login), create a key at https://cloud.cerebras.ai/platform/api-keys, then:

```bash
export AGENT_SMITH_API_KEYS="csk-..."
uv run python -m agent_swebench \
  --task-file cache/swebench_task.json \
  --output cache/swebench_solution.json \
  --model-name "gpt-oss-120b" \
  --provider-url "https://api.cerebras.ai/v1" \
  --max-retries 5
```

Provider URLs:

| Provider     | `--provider-url`                              |
|--------------|-----------------------------------------------|
| OpenRouter   | `https://openrouter.ai/api/v1`                |
| OpenAI       | `https://api.openai.com/v1`                   |
| Together     | `https://api.together.xyz/v1`                 |
| Groq         | `https://api.groq.com/openai/v1`              |
| Mistral      | `https://api.mistral.ai/v1`                   |
| Fireworks    | `https://api.fireworks.ai/inference/v1`       |

## Troubleshooting

- **`HTTP Error 402: Payment Required`**: the chosen model is paid and your account has no credits. Use a `:free` model on OpenRouter or switch to Groq.
- **`HTTP Error 403: Forbidden`** with `error code 1010`: Cloudflare blocking. The bundled client sets a `User-Agent` header to avoid this; if you hit it again, verify your `User-Agent` is not stripped.
- **`HTTP Error 404: Not Found`**: model id no longer exists at that provider. List available models:
  ```bash
  curl -s https://openrouter.ai/api/v1/models | jq -r '.data[].id' | grep -i free
  ```
- **`HTTP Error 429: Too Many Requests`**: rate-limited. Add `--max-retries 5` (the LLM client retries on 429 with backoff), wait for the quota to reset, or switch model/provider.
- **`HTTP Error 413: Payload Too Large`**: the cumulative prompt exceeded the provider's per-request limit. Lower `sandbox_template.json::max_output_chars` (default 5000), or pick a model with a bigger context.
- **`HTTP Error 400: Bad Request`** on Groq with the same payload that works on curl: that model rejected one of `stop` / `max_tokens` / `temperature`. Try another model id from `curl -s https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY" | jq -r '.data[].id'`.
- **Empty solution + `iterations: 1`**: the LLM call failed before any code was produced. Inspect the cause:
  ```bash
  cat cache/mbpp_solution.json | jq '.error, .steps[0].llm_output'
  ```
- **`No valid Python code block ... in the model response`**: the model emitted reasoning (e.g. qwen3 `<think>...</think>`) and never reached a fenced code block. Switch to a non-reasoning model or raise the model's output budget.

## Verified end-to-end runs

The following were executed against the live providers and Docker (not synthetic):

### MBPP — reliable

- **5 random tasks (479, 290, 19, 287, 284), `llama-3.3-70b-versatile` via Groq**: **5/5 PASSED**. Mean ~2 iterations, ~400 output tokens, <2 s each.
- Reproducible — the MBPP MCP tools (`describe_task`, `public_tests`, `run_tests`) give the model a fast feedback loop that small models can close.

### SWE-bench — pipeline verified, resolution depends on the model

Task `sympy__sympy-19495` (sympy `subs` on `ConditionSet`/`ImageSet`):

- **`meta-llama/llama-4-scout-17b-16e-instruct` via Groq, `--max-retries 5`** (one good run): agent produced a real `diff --git` patch in **18 iterations / 259 s**. Validator built the SWE-bench Docker container, applied the patch, ran the test suite (`7 passed, 1 failed`). Final verdict: `Correctness: FAILED` / `Resolution status: RESOLVED_NO` — patch syntactically valid but logically incomplete (expected for a 17B free model).
- Other attempts with the same model hit Groq's 30K TPM ceiling at iterations 4 / 21 / 30 — see the model table above.
- All free Cerebras models (`gpt-oss-120b`, `zai-glm-4.7`) ran the full 30 iterations without ever calling `edit_file`, so the auto-rescue had no patch to recover.

### Sandbox

- All 8 smoke tests in [Sandbox smoke tests](#sandbox-smoke-tests) pass (nominal, allowed import, blocked import, path allowlist, timeout, memory guard, fib loop, MCP-backed).

### What this means for the defense

The pipeline (`LLM → sandbox → MCP tools → Docker → SWE-bench test runner → metrics validator`) is **functional end-to-end**. Demonstrable claims:

1. The sandbox enforces every documented restriction.
2. MBPP is fully validated by moulinette at a high success rate.
3. SWE-bench reaches the validator stage with a real container-applied patch.
4. Higher SWE-bench resolution rate requires Claude/GPT-4-class models, not framework changes.

## Benchmark Results and Analysis

The benchmark report lives in `BENCHMARK_REPORT.md`. It documents the required 5-model x 3-task SWE-bench comparison format, reliability metrics, intermediary metrics, and ablation structure.

Do not fabricate benchmark traces. Generate the backing `solution.json` files by running the agents with real free-tier API keys and Docker, then place the run artifacts under `benchmark_runs/` before final submission.

The helper below runs the default 5-model x 3-task matrix and writes `benchmark_runs/summary.json`:

```bash
uv run python scripts/benchmark_swebench.py --moulinette-path moulinette
```

## Resources

- Model Context Protocol Python SDK documentation: https://modelcontextprotocol.github.io/python-sdk/
- Pydantic documentation: https://docs.pydantic.dev/
- Docker documentation: https://docs.docker.com/
- SWE-bench documentation: https://www.swebench.com/
- OpenAI-compatible chat completions API documentation: https://platform.openai.com/docs/api-reference/chat

AI assistance was used to scaffold the project architecture, implement the sandbox and CLI plumbing, and draft documentation. The implementation still requires human review, real benchmark runs, and project-defense familiarity before submission.

# Docker PC Runbook

This file is the practical checklist for continuing the project on a machine where Docker is installed and running.

## 1. Copy Or Clone The Project

Put the full `agent_smith` directory on the Docker machine. The directory must contain at least:

- `pyproject.toml`
- `agent_smith/`
- `agent_mbpp.py`
- `agent_swebench.py`
- `mcp_tools_mbpp.py`
- `mcp_tools_swebench.py`
- `sandbox_template.json`
- `moulinette.zip`
- `README.md`
- `BENCHMARK_REPORT.md`

Enter the project root:

```bash
cd /path/to/agent_smith
```

## 2. Install Prerequisites

Install and start Docker. Verify it works:

```bash
docker info
docker pull python:3.11-slim
```

Install `uv` if it is not available:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then open a new terminal or reload your shell config so `uv` is in `PATH`.

Verify:

```bash
uv --version
```

## 3. Install The Student Project

From the project root:

```bash
uv sync --python 3.10
```

Basic checks:

```bash
uv run python --version
uv run python -m py_compile agent_smith/*.py agent_mbpp.py agent_swebench.py mcp_tools_mbpp.py mcp_tools_swebench.py scripts/benchmark_swebench.py
printf 'print(2 + 2)\n' | uv run sandbox sandbox_template.json
```

Expected sandbox output:

```text
4
```

## 4. Install The Moulinette

Extract it if the `moulinette/` directory is not already present:

```bash
unzip -q moulinette.zip
```

Install its dependencies:

```bash
cd moulinette
uv sync --python 3.10
cd ..
```

## 5. Verify Sandbox Security

From the project root:

```bash
printf 'import os\nprint(os.getcwd())\n' | uv run sandbox sandbox_template.json
printf 'print(open("/etc/passwd").read())\n' | uv run sandbox sandbox_template.json
printf 'while True:\n    pass\n' | uv run sandbox sandbox_template.json
printf 'x = bytearray(1024 * 1024 * 900)\nprint(len(x))\n' | uv run sandbox sandbox_template.json
```

Expected behavior:

- `import os` is rejected.
- `/etc/passwd` is rejected.
- infinite loop times out after about 30 seconds.
- large memory allocation raises `MemoryError` or is terminated by the sandbox.

## 6. Verify MBPP Tools And Moulinette

Dump a known task:

```bash
mkdir -p cache
cd moulinette
uv run moulinette_eval dump mbpp --task-id 2 --output ../cache/mbpp_task_2.json
cd ..
```

Test the MBPP MCP server:

```bash
printf 'print(describe_task())\n' \
  | AGENT_SMITH_TASK_FILE=cache/mbpp_task_2.json \
    uv run sandbox --mcp-stdio "uv run python mcp_tools_mbpp.py" sandbox_template.json
```

Test `run_tests` through the sandbox:

```bash
printf 'code = """def similar_elements(test_tup1, test_tup2):\n    return tuple(set(test_tup1) & set(test_tup2))\n"""\nprint(run_tests(candidate_code=code))\n' \
  | AGENT_SMITH_TASK_FILE=cache/mbpp_task_2.json \
    uv run sandbox --mcp-stdio "uv run python mcp_tools_mbpp.py" sandbox_template.json
```

Expected result: `exit_code: 0`.

## 7. Run The MBPP Agent

Create a `.env` file or export an API key. Example:

```bash
export OPENROUTER_API_KEY="your_free_tier_key"
```

Run one MBPP task:

```bash
uv run python -m agent_mbpp \
  --task-file cache/mbpp_task_2.json \
  --output cache/mbpp_solution_2.json \
  --model-name "qwen/qwen-2.5-coder-32b-instruct" \
  --provider-url "https://openrouter.ai/api/v1"
```

Validate with the moulinette:

```bash
cd moulinette
uv run moulinette_eval validate mbpp ../cache/mbpp_task_2.json ../cache/mbpp_solution_2.json
cd ..
```

If this fails because of Docker, fix Docker before debugging the agent.

## 8. Run A SWE-bench Task

Start with a known easy pool task:

```bash
mkdir -p cache
cd moulinette
uv run moulinette_eval dump swebench --task-id sympy__sympy-14711 --output ../cache/swebench_task.json
cd ..
```

Run the agent:

```bash
uv run python -m agent_swebench \
  --task-file cache/swebench_task.json \
  --output cache/swebench_solution.json \
  --model-name "qwen/qwen-2.5-coder-32b-instruct" \
  --provider-url "https://openrouter.ai/api/v1"
```

Validate:

```bash
cd moulinette
uv run moulinette_eval validate swebench ../cache/swebench_task.json ../cache/swebench_solution.json
cd ..
```

SWE-bench can take several minutes because Docker images may be pulled and tests run inside containers.

## 9. Run The Required Benchmark Matrix

The subject requires at least 5 models on at least 3 SWE-bench tasks. The helper script uses this default matrix:

- `sympy__sympy-14711`
- `sympy__sympy-13480`
- `pydata__xarray-4629`

Run:

```bash
uv run python scripts/benchmark_swebench.py --moulinette-path moulinette
```

Outputs are written under:

```text
benchmark_runs/
```

After the run, open:

```text
benchmark_runs/summary.json
```

Use those real numbers to replace the `TBD` cells in `BENCHMARK_REPORT.md`.

Do not invent benchmark values. The correction checks traces and `solution.json` files.

## 10. Before Submission

Run:

```bash
uv run python -m py_compile agent_smith/*.py agent_mbpp.py agent_swebench.py mcp_tools_mbpp.py mcp_tools_swebench.py scripts/benchmark_swebench.py
python -m json.tool sandbox_template.json >/dev/null
python -m json.tool config/models.example.json >/dev/null
```

Check that no secrets are committed:

```bash
grep -R "sk-" . --exclude-dir=.venv --exclude-dir=moulinette --exclude-dir=.git
grep -R "OPENROUTER_API_KEY=" . --exclude-dir=.venv --exclude-dir=moulinette --exclude-dir=.git
```

Remove local caches if needed:

```bash
rm -rf __pycache__ agent_smith/__pycache__ scripts/__pycache__ cache/
```

Keep benchmark artifacts only if they are real runs needed for the report.

## Troubleshooting

Docker socket error:

```text
docker.errors.DockerException: Error while fetching server API version
```

Fix:

```bash
docker info
```

If `docker info` fails, Docker is not started or your user cannot access the Docker socket.

No API key:

```text
No API key found
```

Fix:

```bash
export OPENROUTER_API_KEY="..."
```

MCP command not found:

Use `uv run python mcp_tools_mbpp.py` or `uv run python mcp_tools_swebench.py` in `--mcp-stdio`.

SWE-bench image pull is slow:

This is normal on the first run. Re-running is faster after Docker caches the image.


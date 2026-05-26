*This project has been created as part of the 42 curriculum by omischle.*

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

Install dependencies:

```bash
uv sync
```

Run the sandbox:

```bash
uv run sandbox
uv run sandbox sandbox_template.json
uv run sandbox --mcp-stdio "python mcp_tools_mbpp.py" sandbox_template.json
uv run sandbox --mcp-server http://127.0.0.1:8000/mcp
```

Run MBPP:

```bash
cd moulinette
uv run moulinette_eval dump mbpp --output ../cache/mbpp_task.json

cd ..
uv run python -m agent_mbpp \
  --task-file cache/mbpp_task.json \
  --output cache/mbpp_solution.json \
  --model-name "model/name" \
  --provider-url "https://provider.example/v1"

cd moulinette
uv run moulinette_eval validate mbpp ../cache/mbpp_task.json ../cache/mbpp_solution.json
```

Run SWE-bench:

```bash
cd moulinette
uv run moulinette_eval dump swebench --output ../cache/swebench_task.json

cd ..
uv run python -m agent_swebench \
  --task-file cache/swebench_task.json \
  --output cache/swebench_solution.json \
  --model-name "model/name" \
  --provider-url "https://provider.example/v1"

cd moulinette
uv run moulinette_eval validate swebench ../cache/swebench_task.json ../cache/swebench_solution.json
```

API keys are loaded from environment variables. Supported names include `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `TOGETHER_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `FIREWORKS_API_KEY`, and `AGENT_SMITH_API_KEYS`. Multiple keys may be comma, colon, or newline separated.

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

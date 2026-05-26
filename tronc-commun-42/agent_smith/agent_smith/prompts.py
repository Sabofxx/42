"""System prompt builders for MBPP and SWE-bench agents."""

from __future__ import annotations

from agent_smith.models import MBPPTaskInput, SWEBenchTaskInput


def mbpp_system_prompt(sandbox_manual: str) -> str:
    return f"""You are Agent Smith, a code agent solving MBPP Python tasks.

Rules:
- Work through Thought -> Code -> Observation.
- Every assistant turn must contain exactly one executable Python code block.
- Use run_tests(candidate_code=...) to test candidates against public tests.
- When solved, call final_answer(solution_code) where solution_code is the full Python function implementation.
- Do not use external sources, hidden tests, or memorized dataset answers.
- Keep solutions compact and compatible with Python 3.10.

Example first step:
Thought: I will test a direct implementation against the public assertions.
```python
code = \"\"\"def add(a, b):
    return a + b
\"\"\"
print(run_tests(candidate_code=code))
```
<end_code>

Example final step:
```python
final_answer(\"\"\"def add(a, b):
    return a + b
\"\"\")
```
<end_code>

{sandbox_manual}
"""


def mbpp_user_prompt(task: MBPPTaskInput) -> str:
    tests = "\n".join((task.test_imports or []) + (task.test_list or []))
    return f"""Solve this MBPP task.

task_id: {task.task_id}
task_definition:
{task.task_definition}

function_definition:
{task.function_definition}

public_tests:
{tests}
"""


def swebench_system_prompt(sandbox_manual: str) -> str:
    return f"""You are Agent Smith, a code agent fixing a SWE-bench repository.

Rules:
- Work through Thought -> Code -> Observation.
- Every assistant turn must contain exactly one executable Python code block.
- Use search_code/list_files/read_file before editing so the trace shows genuine exploration.
- Make the smallest correct patch. Prefer edit_file for exact replacements.
- Use run_tests() or focused run_command(...) checks after editing.
- When solved, call final_answer(get_patch()).
- Do not use external sources, GitHub issues, pull requests, or memorized patches.
- Do not submit an empty patch.

Example exploration:
```python
print(search_code(pattern="validate", file_pattern="*.py"))
```
<end_code>

Example final step:
```python
print(run_tests())
final_answer(get_patch())
```
<end_code>

{sandbox_manual}
"""


def swebench_user_prompt(task: SWEBenchTaskInput) -> str:
    hints = task.hints_text or "(none)"
    return f"""Fix this SWE-bench task.

instance_id: {task.instance_id}
repo: {task.repo}
docker_image: {task.docker_image}

problem_statement:
{task.problem_statement}

hints:
{hints}
"""


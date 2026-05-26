"""Run the required SWE-bench benchmark matrix and summarize solution metrics."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path


DEFAULT_TASKS = [
    "sympy__sympy-14711",
    "sympy__sympy-13480",
    "pydata__xarray-4629",
]


DEFAULT_MODELS = [
    {
        "label": "gpt-oss-120b",
        "model_name": "openai/gpt-oss-120b:free",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "label": "gpt-oss-20b",
        "model_name": "openai/gpt-oss-20b:free",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "label": "deepseek-v4-flash",
        "model_name": "deepseek/deepseek-v4-flash:free",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "label": "glm-4.5-air",
        "model_name": "z-ai/glm-4.5-air:free",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "label": "qwen3-next-80b",
        "model_name": "qwen/qwen3-next-80b-a3b-instruct:free",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
]


def run(command: list[str], cwd: Path, log_file: Path, timeout: int = 1200) -> int:
    started = time.perf_counter()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(
            command, cwd=str(cwd), text=True, capture_output=True, check=False, timeout=timeout
        )
        stdout, stderr, code = completed.stdout, completed.stderr, completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr if isinstance(exc.stderr, str) else "") + f"\nTIMEOUT after {timeout}s"
        code = -1
    elapsed = time.perf_counter() - started
    log_file.write_text(
        "$ " + " ".join(command)
        + f"\nexit_code: {code}\nelapsed: {elapsed:.2f}s\n"
        + "\nstdout:\n" + stdout
        + "\nstderr:\n" + stderr
    )
    return code


def summarize(solution_file: Path, validate_exit_code: int) -> dict:
    if not solution_file.exists():
        return {"pass": False, "error": "solution file missing"}
    data = json.loads(solution_file.read_text())
    request_times = [step.get("request_time_ms", 0) for step in data.get("steps", [])]
    retries = sum(step.get("retries", 0) for step in data.get("steps", []))
    return {
        "pass": validate_exit_code == 0 and data.get("success", False),
        "agent_success": data.get("success"),
        "iterations": data.get("iterations"),
        "total_input_tokens": data.get("total_input_tokens"),
        "total_output_tokens": data.get("total_output_tokens"),
        "total_time_seconds": data.get("total_time_seconds"),
        "avg_request_time_ms": sum(request_times) / len(request_times) if request_times else 0,
        "retries": retries,
        "solution_file": str(solution_file),
        "validate_exit_code": validate_exit_code,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moulinette-path", default="moulinette")
    parser.add_argument("--output-dir", default="benchmark_runs")
    parser.add_argument("--models-file", default="")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--tasks", nargs="*", default=DEFAULT_TASKS)
    parser.add_argument("--max-iterations", type=int, default=30)
    parser.add_argument("--max-retries", type=int, default=8)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    moulinette = (root / args.moulinette_path).resolve()
    output_dir = (root / args.output_dir).resolve()
    env_file_arg = str((root / args.env_file).resolve()) if args.env_file else ""
    models = DEFAULT_MODELS
    if args.models_file:
        models = json.loads(Path(args.models_file).read_text())

    summary: list[dict] = []
    for task_id in args.tasks:
        for model in models:
            run_dir = output_dir / model["label"] / task_id
            task_file = run_dir / "task.json"
            solution_file = run_dir / "solution.json"

            if args.skip_existing and solution_file.exists():
                row = {
                    "model_label": model["label"],
                    "model_name": model["model_name"],
                    "provider_url": model["provider_url"],
                    "task_id": task_id,
                    "skipped": True,
                }
                row.update(summarize(solution_file, 0))
                summary.append(row)
                continue

            run(
                [
                    "uv", "run", "python", "-m", "moulinette",
                    "dump", "swebench", "--task-id", task_id,
                    "--output", str(task_file),
                ],
                cwd=moulinette,
                log_file=run_dir / "dump.log",
            )
            agent_cmd = [
                "uv", "run", "python", "-m", "agent_swebench",
                "--task-file", str(task_file),
                "--output", str(solution_file),
                "--model-name", model["model_name"],
                "--provider-url", model["provider_url"],
                "--api-key-env", model["api_key_env"],
                "--max-iterations", str(args.max_iterations),
                "--max-retries", str(args.max_retries),
            ]
            if env_file_arg:
                agent_cmd += ["--env-file", env_file_arg]
            run(agent_cmd, cwd=root, log_file=run_dir / "agent.log", timeout=1500)

            validate_exit = run(
                [
                    "uv", "run", "python", "-m", "moulinette",
                    "validate", "swebench", str(task_file), str(solution_file),
                ],
                cwd=moulinette,
                log_file=run_dir / "validate.log",
                timeout=900,
            )
            row = {
                "model_label": model["label"],
                "model_name": model["model_name"],
                "provider_url": model["provider_url"],
                "task_id": task_id,
            }
            row.update(summarize(solution_file, validate_exit))
            summary.append(row)
            (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

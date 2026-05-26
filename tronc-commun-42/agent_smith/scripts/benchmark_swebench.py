"""Run the required SWE-bench benchmark matrix and summarize solution metrics."""

from __future__ import annotations

import argparse
import json
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
        "label": "qwen-coder-openrouter",
        "model_name": "qwen/qwen-2.5-coder-32b-instruct",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "label": "deepseek-openrouter",
        "model_name": "deepseek/deepseek-chat-v3-0324:free",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "label": "llama-openrouter",
        "model_name": "meta-llama/llama-3.3-70b-instruct:free",
        "provider_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    {
        "label": "llama-groq",
        "model_name": "llama-3.3-70b-versatile",
        "provider_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
    },
    {
        "label": "mistral-small",
        "model_name": "mistral-small-latest",
        "provider_url": "https://api.mistral.ai/v1",
        "api_key_env": "MISTRAL_API_KEY",
    },
]


def run(command: list[str], cwd: Path, log_file: Path) -> int:
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, check=False)
    elapsed = time.perf_counter() - started
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(
        "$ "
        + " ".join(command)
        + f"\nexit_code: {completed.returncode}\nelapsed: {elapsed:.2f}s\n"
        + "\nstdout:\n"
        + completed.stdout
        + "\nstderr:\n"
        + completed.stderr
    )
    return completed.returncode


def summarize(solution_file: Path, validate_exit_code: int) -> dict:
    if not solution_file.exists():
        return {"pass": False, "error": "solution file missing"}
    data = json.loads(solution_file.read_text())
    request_times = [step.get("request_time_ms", 0) for step in data.get("steps", [])]
    retries = sum(step.get("retries", 0) for step in data.get("steps", []))
    return {
        "pass": validate_exit_code == 0,
        "iterations": data.get("iterations"),
        "total_input_tokens": data.get("total_input_tokens"),
        "total_output_tokens": data.get("total_output_tokens"),
        "total_time_seconds": data.get("total_time_seconds"),
        "avg_request_time_ms": sum(request_times) / len(request_times) if request_times else 0,
        "retries": retries,
        "solution_file": str(solution_file),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moulinette-path", default="moulinette")
    parser.add_argument("--output-dir", default="benchmark_runs")
    parser.add_argument("--models-file", default="")
    args = parser.parse_args()

    root = Path.cwd()
    moulinette = (root / args.moulinette_path).resolve()
    output_dir = (root / args.output_dir).resolve()
    models = DEFAULT_MODELS
    if args.models_file:
        models = json.loads(Path(args.models_file).read_text())

    summary: list[dict] = []
    for model in models:
        for task_id in DEFAULT_TASKS:
            run_dir = output_dir / model["label"] / task_id
            task_file = run_dir / "task.json"
            solution_file = run_dir / "solution.json"

            run(
                [
                    "uv",
                    "run",
                    "moulinette_eval",
                    "dump",
                    "swebench",
                    "--task-id",
                    task_id,
                    "--output",
                    str(task_file),
                ],
                cwd=moulinette,
                log_file=run_dir / "dump.log",
            )
            run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "agent_swebench",
                    "--task-file",
                    str(task_file),
                    "--output",
                    str(solution_file),
                    "--model-name",
                    model["model_name"],
                    "--provider-url",
                    model["provider_url"],
                    "--api-key-env",
                    model["api_key_env"],
                ],
                cwd=root,
                log_file=run_dir / "agent.log",
            )
            validate_exit = run(
                [
                    "uv",
                    "run",
                    "moulinette_eval",
                    "validate",
                    "swebench",
                    str(task_file),
                    str(solution_file),
                ],
                cwd=moulinette,
                log_file=run_dir / "validate.log",
            )
            row = {
                "model_label": model["label"],
                "model_name": model["model_name"],
                "provider_url": model["provider_url"],
                "task_id": task_id,
            }
            row.update(summarize(solution_file, validate_exit))
            summary.append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()


"""Packaged CLI entrypoint for the SWE-bench agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_smith.agent import run_swebench_agent
from agent_smith.env import load_env_file
from agent_smith.models import SandboxConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--provider-url", required=True)
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--env-file", default=None)
    parser.add_argument("--sandbox-config", default=None)
    parser.add_argument("--max-iterations", type=int, default=30)
    parser.add_argument("--max-retries", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_env_file(args.env_file)
    config = None
    if args.sandbox_config:
        config = SandboxConfig.model_validate_json(Path(args.sandbox_config).read_text())
    solution = run_swebench_agent(
        task_file=Path(args.task_file),
        output_file=Path(args.output),
        model_name=args.model_name,
        provider_url=args.provider_url,
        api_key_env=args.api_key_env,
        max_iterations=args.max_iterations,
        max_retries=args.max_retries,
        sandbox_config=config,
    )
    if not solution.success:
        raise SystemExit(1)


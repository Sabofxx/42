"""Agent loop implementation shared by MBPP and SWE-bench CLIs."""

from __future__ import annotations

import json
import os
import shlex
import sys
import time
from pathlib import Path

from agent_smith.env import api_keys_for_provider
from agent_smith.extraction import extract_executable_code
from agent_smith.llm import LLMClient, LLMConfig, approximate_tokens
from agent_smith.mcp_client import MCPClient
from agent_smith.models import (
    MBPPTaskInput,
    SWEBenchTaskInput,
    SandboxConfig,
    SolutionOutput,
    StepMetrics,
)
from agent_smith.prompts import (
    mbpp_system_prompt,
    mbpp_user_prompt,
    swebench_system_prompt,
    swebench_user_prompt,
)
from agent_smith.sandbox import Sandbox


def _write_solution(path: Path, solution: SolutionOutput) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(solution.model_dump_json(indent=2))


def _module_command(script: str) -> str:
    return " ".join([shlex.quote(sys.executable), shlex.quote(str(Path(script).resolve()))])


def _totals(steps: list[StepMetrics]) -> tuple[int, int, int]:
    return (
        sum(1 + step.retries for step in steps),
        sum(step.input_tokens for step in steps),
        sum(step.output_tokens for step in steps),
    )


def _failure_solution(
    *,
    benchmark: str,
    task_id: str,
    system_prompt: str,
    started: float,
    error: str,
    steps: list[StepMetrics] | None = None,
) -> SolutionOutput:
    steps = steps or []
    total_requests, total_in, total_out = _totals(steps)
    return SolutionOutput(
        task_id=task_id,
        benchmark=benchmark,
        success=False,
        solution="",
        iterations=len(steps),
        total_requests=total_requests,
        total_input_tokens=total_in,
        total_output_tokens=total_out,
        total_time_seconds=time.perf_counter() - started,
        steps=steps,
        system_prompt=system_prompt,
        error=error,
    )


def run_loop(
    *,
    benchmark: str,
    task_id: str,
    system_prompt: str,
    user_prompt: str,
    sandbox: Sandbox,
    llm: LLMClient,
    max_iterations: int,
    started: float,
) -> SolutionOutput:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    steps: list[StepMetrics] = []
    error: str | None = None
    solution = ""
    success = False

    for step_no in range(1, max_iterations + 1):
        try:
            response = llm.complete(messages)
            llm_output = response.text
            input_tokens = response.input_tokens
            output_tokens = response.output_tokens
            request_time_ms = response.latency_ms
            retries = response.retries
        except Exception as exc:
            llm_output = f"LLM request failed: {type(exc).__name__}: {exc}"
            input_tokens = approximate_tokens(json.dumps(messages, ensure_ascii=False))
            output_tokens = approximate_tokens(llm_output)
            request_time_ms = 0.0
            retries = 0
            error = llm_output
            steps.append(
                StepMetrics(
                    step=step_no,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    request_time_ms=request_time_ms,
                    api_url=llm.config.provider_url,
                    model_name=llm.config.model_name,
                    llm_output=llm_output,
                    sandbox_input="",
                    sandbox_output=llm_output,
                    retries=retries,
                )
            )
            break

        extraction = extract_executable_code(llm_output)
        sandbox_input = extraction.code
        if extraction.warning:
            observation_prefix = extraction.warning + "\n"
        else:
            observation_prefix = ""
        result = sandbox.execute(sandbox_input)
        observation = observation_prefix + (result.observation or "(no output)")
        steps.append(
            StepMetrics(
                step=step_no,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                request_time_ms=request_time_ms,
                api_url=llm.config.provider_url,
                model_name=llm.config.model_name,
                llm_output=llm_output,
                sandbox_input=sandbox_input,
                sandbox_output=observation,
                retries=retries,
            )
        )
        messages.append({"role": "assistant", "content": llm_output})
        messages.append({"role": "user", "content": "Observation:\n" + observation})

        if result.final_answer is not None:
            solution = result.final_answer
            success = bool(solution.strip())
            break

    if not success and error is None:
        error = "Agent stopped without calling final_answer."
    total_requests, total_in, total_out = _totals(steps)
    return SolutionOutput(
        task_id=task_id,
        benchmark=benchmark,
        success=success,
        solution=solution,
        iterations=len(steps),
        total_requests=total_requests,
        total_input_tokens=total_in,
        total_output_tokens=total_out,
        total_time_seconds=time.perf_counter() - started,
        steps=steps,
        system_prompt=system_prompt,
        error=error,
    )


def run_mbpp_agent(
    *,
    task_file: Path,
    output_file: Path,
    model_name: str,
    provider_url: str,
    api_key_env: str | None = None,
    max_iterations: int = 10,
    max_retries: int = 0,
    sandbox_config: SandboxConfig | None = None,
) -> SolutionOutput:
    started = time.perf_counter()
    task = MBPPTaskInput.model_validate_json(task_file.read_text())
    env = os.environ.copy()
    env["AGENT_SMITH_TASK_FILE"] = str(task_file.resolve())
    mcp = MCPClient(stdio_command=_module_command("mcp_tools_mbpp.py"), env=env)
    try:
        mcp.start()
        sandbox = Sandbox(config=sandbox_config or SandboxConfig(), tool_client=mcp)
        system_prompt = mbpp_system_prompt(sandbox.manual())
        llm = LLMClient(
            LLMConfig(
                provider_url=provider_url,
                model_name=model_name,
                api_keys=api_keys_for_provider(provider_url, api_key_env),
                max_tokens=900,
                max_retries=max_retries,
            )
        )
        solution = run_loop(
            benchmark="mbpp",
            task_id=str(task.task_id),
            system_prompt=system_prompt,
            user_prompt=mbpp_user_prompt(task),
            sandbox=sandbox,
            llm=llm,
            max_iterations=max_iterations,
            started=started,
        )
    except Exception as exc:
        manual = "Sandbox manual unavailable because MCP startup failed."
        system_prompt = mbpp_system_prompt(manual)
        solution = _failure_solution(
            benchmark="mbpp",
            task_id=str(task.task_id),
            system_prompt=system_prompt,
            started=started,
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        try:
            mcp.close()
        except Exception:
            pass
    _write_solution(output_file, solution)
    return solution


def run_swebench_agent(
    *,
    task_file: Path,
    output_file: Path,
    model_name: str,
    provider_url: str,
    api_key_env: str | None = None,
    max_iterations: int = 30,
    max_retries: int = 0,
    sandbox_config: SandboxConfig | None = None,
) -> SolutionOutput:
    started = time.perf_counter()
    task = SWEBenchTaskInput.model_validate_json(task_file.read_text())
    env = os.environ.copy()
    env["AGENT_SMITH_TASK_FILE"] = str(task_file.resolve())
    mcp = MCPClient(stdio_command=_module_command("mcp_tools_swebench.py"), env=env)
    try:
        mcp.start()
        sandbox = Sandbox(config=sandbox_config or SandboxConfig(), tool_client=mcp)
        system_prompt = swebench_system_prompt(sandbox.manual())
        llm = LLMClient(
            LLMConfig(
                provider_url=provider_url,
                model_name=model_name,
                api_keys=api_keys_for_provider(provider_url, api_key_env),
                max_tokens=900,
                max_retries=max_retries,
            )
        )
        solution = run_loop(
            benchmark="swebench",
            task_id=task.instance_id,
            system_prompt=system_prompt,
            user_prompt=swebench_user_prompt(task),
            sandbox=sandbox,
            llm=llm,
            max_iterations=max_iterations,
            started=started,
        )
    except Exception as exc:
        manual = "Sandbox manual unavailable because MCP startup failed."
        system_prompt = swebench_system_prompt(manual)
        solution = _failure_solution(
            benchmark="swebench",
            task_id=task.instance_id,
            system_prompt=system_prompt,
            started=started,
            error=f"{type(exc).__name__}: {exc}",
        )
    finally:
        try:
            mcp.close()
        except Exception:
            pass
    _write_solution(output_file, solution)
    return solution

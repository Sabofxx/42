"""Pydantic models shared by the agents, sandbox, and CLI output."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SandboxConfig(BaseModel):
    """Sandbox configuration.

    The default policy is an allowlist: imports, direct filesystem access, memory,
    and runtime are all denied or constrained unless explicitly configured.
    """

    authorized_imports: List[str] = Field(
        default_factory=lambda: [
            "math",
            "math.*",
            "collections",
            "collections.*",
            "itertools",
            "re",
            "json",
            "typing",
            "typing.*",
            "functools",
            "operator",
            "heapq",
            "bisect",
            "copy",
            "string",
            "random",
            "datetime",
            "datetime.*",
            "array",
            "cmath",
        ]
    )
    allowed_directories: List[str] = Field(
        default_factory=lambda: ["/testbed", "/tmp/agent"]
    )
    max_execution_time_seconds: int = 30
    max_memory_mb: int = 512
    max_output_chars: int = 20_000


class MBPPTaskInput(BaseModel):
    """Input for an MBPP task provided by the moulinette."""

    task_id: int
    task_definition: str
    function_definition: str
    test_imports: List[str] = Field(default_factory=list)
    test_list: List[str] = Field(default_factory=list)


class SWEBenchTaskInput(BaseModel):
    """Input for a SWE-bench task provided by the moulinette."""

    instance_id: str = Field(..., description="SWE-bench instance identifier")
    problem_statement: str = Field(..., description="Issue or feature request")
    docker_image: str = Field(..., description="Docker image containing the repo")
    eval_script: str = Field(..., description="Evaluation script")
    hints_text: str = Field(default="", description="Optional task hints")
    repo: str = Field(default="", description="Repository name")


class StepMetrics(BaseModel):
    """Metrics and provenance for one Thought -> Code -> Observation step."""

    step: int
    input_tokens: int
    output_tokens: int
    request_time_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    api_url: str = ""
    model_name: str = ""
    llm_output: str = ""
    sandbox_input: str = ""
    sandbox_output: str = ""
    retries: int = 0


class SolutionOutput(BaseModel):
    """Student output format consumed by the moulinette."""

    task_id: str
    benchmark: str
    success: bool
    solution: str
    iterations: int
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_time_seconds: float
    steps: List[StepMetrics] = Field(default_factory=list)
    system_prompt: str = ""
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ToolSpec(BaseModel):
    """Small serializable view of an MCP tool schema."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)


class SandboxResult(BaseModel):
    """Result of executing a code block in the sandbox."""

    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    final_answer: Optional[str] = None
    timed_out: bool = False
    truncated: bool = False

    @property
    def observation(self) -> str:
        parts: list[str] = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append("stderr:\n" + self.stderr)
        if self.error:
            parts.append("error:\n" + self.error)
        if self.timed_out:
            parts.append("Execution hit the configured timeout.")
        if self.truncated:
            parts.append("Tool or sandbox output was truncated due to size limits.")
        if self.final_answer is not None:
            parts.append("final_answer captured.")
        return "\n".join(parts).strip()


class LLMResponse(BaseModel):
    """Normalized LLM API response."""

    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    retries: int = 0

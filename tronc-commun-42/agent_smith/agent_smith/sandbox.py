"""Configurable process-isolated sandbox for LLM-generated Python code."""

from __future__ import annotations

import builtins
import io
import json
import multiprocessing as mp
import pathlib
import signal
import subprocess
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Protocol

from agent_smith.models import SandboxConfig, SandboxResult, ToolSpec


class ToolClient(Protocol):
    """Minimal synchronous tool client interface used by the sandbox parent."""

    def list_tools(self) -> list[ToolSpec]:
        ...

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        ...


class FinalAnswerSignal(Exception):
    """Internal control-flow exception raised inside the child process."""

    def __init__(self, answer: str):
        super().__init__(answer)
        self.answer = answer


def _truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    marker = f"\n... <truncated {len(text) - limit} chars>"
    return text[:limit] + marker, True


def _matches_import(name: str, authorized: list[str]) -> bool:
    for pattern in authorized:
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            if name == prefix or name.startswith(prefix + "."):
                return True
        elif name == pattern:
            return True
    return False


def _safe_open_factory(allowed_directories: list[str]):
    allowed_paths = [
        pathlib.Path(directory).expanduser().resolve(strict=False)
        for directory in allowed_directories
    ]

    def safe_open(file, mode="r", *args, **kwargs):
        path = pathlib.Path(file).expanduser().resolve(strict=False)
        if not any(path == root or root in path.parents for root in allowed_paths):
            raise PermissionError(f"Filesystem access denied by sandbox: {path}")
        return builtins.open(path, mode, *args, **kwargs)

    return safe_open


def _restricted_import_factory(authorized_imports: list[str]):
    real_import = builtins.__import__

    def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level != 0:
            raise ImportError("Relative imports are disabled inside the sandbox")
        if not _matches_import(name, authorized_imports):
            raise ImportError(f"Import blocked by sandbox allowlist: {name}")
        module = real_import(name, globals, locals, fromlist, level)
        # The stdlib random module keeps an internal os module reference. Remove
        # it so allowing random does not accidentally expose process primitives.
        if name == "random" and hasattr(module, "_os"):
            try:
                setattr(module, "_os", None)
            except Exception:
                pass
        return module

    return restricted_import


def _safe_builtins(config: SandboxConfig) -> dict[str, Any]:
    names = [
        "ArithmeticError",
        "AssertionError",
        "AttributeError",
        "BaseException",
        "BlockingIOError",
        "BrokenPipeError",
        "BufferError",
        "BytesWarning",
        "ChildProcessError",
        "ConnectionAbortedError",
        "ConnectionError",
        "ConnectionRefusedError",
        "ConnectionResetError",
        "DeprecationWarning",
        "EOFError",
        "Ellipsis",
        "EnvironmentError",
        "Exception",
        "False",
        "FileExistsError",
        "FileNotFoundError",
        "FloatingPointError",
        "FutureWarning",
        "GeneratorExit",
        "IOError",
        "ImportError",
        "ImportWarning",
        "IndentationError",
        "IndexError",
        "InterruptedError",
        "IsADirectoryError",
        "KeyError",
        "KeyboardInterrupt",
        "LookupError",
        "MemoryError",
        "ModuleNotFoundError",
        "NameError",
        "None",
        "NotADirectoryError",
        "NotImplemented",
        "NotImplementedError",
        "OSError",
        "OverflowError",
        "PendingDeprecationWarning",
        "PermissionError",
        "ProcessLookupError",
        "RecursionError",
        "ReferenceError",
        "ResourceWarning",
        "RuntimeError",
        "RuntimeWarning",
        "StopAsyncIteration",
        "StopIteration",
        "SyntaxError",
        "SyntaxWarning",
        "SystemError",
        "SystemExit",
        "TabError",
        "TimeoutError",
        "True",
        "TypeError",
        "UnboundLocalError",
        "UnicodeDecodeError",
        "UnicodeEncodeError",
        "UnicodeError",
        "UnicodeTranslateError",
        "UnicodeWarning",
        "UserWarning",
        "ValueError",
        "Warning",
        "ZeroDivisionError",
        "__build_class__",
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "callable",
        "chr",
        "classmethod",
        "complex",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "hasattr",
        "hash",
        "hex",
        "id",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "next",
        "object",
        "oct",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "zip",
    ]
    safe = {name: getattr(builtins, name) for name in names}

    def guarded_bytearray(*args, **kwargs):
        if args and isinstance(args[0], int):
            max_bytes = config.max_memory_mb * 1024 * 1024
            if args[0] > max_bytes:
                raise MemoryError(
                    f"bytearray allocation exceeds sandbox memory limit: {args[0]} bytes"
                )
        return builtins.bytearray(*args, **kwargs)

    def guarded_bytes(*args, **kwargs):
        if args and isinstance(args[0], int):
            max_bytes = config.max_memory_mb * 1024 * 1024
            if args[0] > max_bytes:
                raise MemoryError(
                    f"bytes allocation exceeds sandbox memory limit: {args[0]} bytes"
                )
        return builtins.bytes(*args, **kwargs)

    safe["bytearray"] = guarded_bytearray
    safe["bytes"] = guarded_bytes
    safe["__import__"] = _restricted_import_factory(config.authorized_imports)
    safe["open"] = _safe_open_factory(config.allowed_directories)
    return safe


def _apply_resource_limits(config: SandboxConfig) -> None:
    try:
        import resource

        memory_bytes = max(16, config.max_memory_mb) * 1024 * 1024
        for limit_name in ("RLIMIT_AS", "RLIMIT_DATA"):
            limit = getattr(resource, limit_name, None)
            if limit is not None:
                try:
                    resource.setrlimit(limit, (memory_bytes, memory_bytes))
                except (OSError, ValueError):
                    pass
    except ImportError:
        pass

    try:
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
        signal.alarm(max(1, config.max_execution_time_seconds))
    except (AttributeError, ValueError):
        pass


def _make_tool_proxy(name: str, conn):
    def proxy(*args, **kwargs):
        if args:
            raise TypeError(
                f"Tool {name} was called with positional arguments. "
                "Use keyword arguments so MCP schemas remain explicit."
            )
        conn.send({"type": "tool_call", "name": name, "arguments": kwargs})
        response = conn.recv()
        if not response.get("ok"):
            raise RuntimeError(response.get("error", f"Tool {name} failed"))
        return response.get("result", "")

    proxy.__name__ = name
    return proxy


def _rss_kb(pid: int) -> int | None:
    try:
        completed = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(pid)],
            text=True,
            capture_output=True,
            timeout=1,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    text = completed.stdout.strip()
    if not text:
        return None
    try:
        return int(text.splitlines()[-1].strip())
    except ValueError:
        return None


def _sandbox_worker(code: str, config_data: dict[str, Any], tool_names: list[str], conn) -> None:
    config = SandboxConfig.model_validate(config_data)
    _apply_resource_limits(config)

    stdout = io.StringIO()
    stderr = io.StringIO()
    namespace: dict[str, Any] = {
        "__builtins__": _safe_builtins(config),
        "__name__": "__sandbox__",
    }

    def final_answer(answer: Any) -> None:
        raise FinalAnswerSignal(str(answer))

    namespace["final_answer"] = final_answer
    for tool_name in tool_names:
        namespace[tool_name] = _make_tool_proxy(tool_name, conn)

    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exec(compile(code, "<sandbox>", "exec"), namespace, namespace)
        conn.send(
            {
                "type": "done",
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "error": None,
                "final_answer": None,
            }
        )
    except FinalAnswerSignal as exc:
        conn.send(
            {
                "type": "done",
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "error": None,
                "final_answer": exc.answer,
            }
        )
    except (KeyboardInterrupt, SystemExit) as exc:
        conn.send(
            {
                "type": "control_exception",
                "exception": type(exc).__name__,
                "message": str(exc),
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
            }
        )
    except TimeoutError:
        conn.send(
            {
                "type": "done",
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "error": "Execution hit the configured timeout.",
                "final_answer": None,
                "timed_out": True,
            }
        )
    except BaseException:
        conn.send(
            {
                "type": "done",
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
                "error": traceback.format_exc(),
                "final_answer": None,
            }
        )


class Sandbox:
    """Execute LLM-generated code in a child process with MCP tool proxies."""

    def __init__(self, config: SandboxConfig | None = None, tool_client: ToolClient | None = None):
        self.config = config or SandboxConfig()
        self.tool_client = tool_client

    def tool_specs(self) -> list[ToolSpec]:
        if not self.tool_client:
            return []
        return self.tool_client.list_tools()

    def manual(self) -> str:
        """Generate the dynamic manual the LLM receives in the system prompt."""

        lines = [
            "Sandbox execution manual:",
            "- Write exactly one Python code block per step.",
            "- Tool calls are ordinary Python function calls.",
            "- Use final_answer(answer_string) when the task is solved.",
            "- Positional arguments are rejected for MCP tools; use keyword arguments.",
            "",
            "Available tools:",
            "- final_answer(answer: str): terminate the agent loop and return the solution.",
        ]
        for spec in self.tool_specs():
            schema = json.dumps(spec.input_schema or {}, ensure_ascii=False)
            description = spec.description.strip() or "No description provided."
            lines.append(f"- {spec.name}: {description} schema={schema}")
        return "\n".join(lines)

    def execute(self, code: str) -> SandboxResult:
        """Run code and return an explicit observation result."""

        if not code.strip():
            return SandboxResult(
                error="No valid code block was found in the model response."
            )

        try:
            compile(code, "<sandbox-preflight>", "exec")
        except SyntaxError:
            return SandboxResult(
                error="SyntaxError before execution:\n" + traceback.format_exc()
            )

        tool_names = [tool.name for tool in self.tool_specs()]
        ctx = mp.get_context("fork" if "fork" in mp.get_all_start_methods() else "spawn")
        parent_conn, child_conn = ctx.Pipe()
        process = ctx.Process(
            target=_sandbox_worker,
            args=(code, self.config.model_dump(), tool_names, child_conn),
        )
        process.start()
        child_conn.close()

        done_message: dict[str, Any] | None = None
        deadline = time.monotonic() + self.config.max_execution_time_seconds
        try:
            while True:
                rss_kb = _rss_kb(process.pid) if process.pid else None
                if rss_kb is not None and rss_kb > self.config.max_memory_mb * 1024:
                    process.terminate()
                    process.join(timeout=1)
                    return SandboxResult(
                        error=(
                            "Execution exceeded the configured memory limit "
                            f"({rss_kb // 1024} MB > {self.config.max_memory_mb} MB)."
                        )
                    )
                if parent_conn.poll(0.05):
                    message = parent_conn.recv()
                    msg_type = message.get("type")
                    if msg_type == "tool_call":
                        response = self._handle_tool_call(message)
                        parent_conn.send(response)
                    elif msg_type == "done":
                        done_message = message
                        break
                    elif msg_type == "control_exception":
                        process.join(timeout=0.2)
                        exception_name = message.get("exception", "SystemExit")
                        if exception_name == "KeyboardInterrupt":
                            raise KeyboardInterrupt(message.get("message", ""))
                        raise SystemExit(message.get("message", ""))

                process.join(timeout=0)
                if not process.is_alive():
                    if parent_conn.poll(0.01):
                        done_message = parent_conn.recv()
                    break

                if time.monotonic() >= deadline:
                    process.terminate()
                    process.join(timeout=1)
                    return SandboxResult(
                        error=(
                            "Execution hit the timeout and was terminated. "
                            "Partial output is unavailable because the child process "
                            "did not complete a flush."
                        ),
                        timed_out=True,
                    )
        finally:
            if process.is_alive():
                process.terminate()
                process.join(timeout=1)
            parent_conn.close()

        if done_message is None:
            code_info = f" exit code {process.exitcode}" if process.exitcode is not None else ""
            return SandboxResult(error=f"Sandbox process ended without a result{code_info}.")

        stdout, out_truncated = _truncate(
            done_message.get("stdout") or "", self.config.max_output_chars
        )
        stderr, err_truncated = _truncate(
            done_message.get("stderr") or "", self.config.max_output_chars
        )
        error, error_truncated = _truncate(
            done_message.get("error") or "", self.config.max_output_chars
        )
        return SandboxResult(
            stdout=stdout,
            stderr=stderr,
            error=error or None,
            final_answer=done_message.get("final_answer"),
            timed_out=bool(done_message.get("timed_out", False)),
            truncated=out_truncated or err_truncated or error_truncated,
        )

    def _handle_tool_call(self, message: dict[str, Any]) -> dict[str, Any]:
        if not self.tool_client:
            return {"ok": False, "error": "No MCP tool client is connected."}
        name = message.get("name", "")
        arguments = message.get("arguments") or {}
        try:
            result = self.tool_client.call_tool(name, arguments)
            result_text = result if isinstance(result, str) else json.dumps(result)
            result_text, truncated = _truncate(result_text, self.config.max_output_chars)
            if truncated:
                result_text += "\nTool output was truncated due to sandbox size limits."
            return {"ok": True, "result": result_text}
        except Exception as exc:
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

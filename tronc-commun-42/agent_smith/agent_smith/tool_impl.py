"""Tool implementations shared by MCP servers.

The SWE-bench tools support two execution modes:
- host mode, when AGENT_SMITH_TESTBED_PATH or /testbed is available;
- Docker mode, when a SWE-bench task JSON provides a docker_image.
"""

from __future__ import annotations

import atexit
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


def truncate(text: str, limit: int = 20_000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... <truncated {len(text) - limit} chars>"


def run_subprocess(command: list[str], timeout: int = 120, cwd: str | None = None) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return truncate(
            f"exit_code: {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return truncate(
            f"exit_code: timeout\nstdout:\n{stdout}\nstderr:\n{stderr}\n"
            f"Command timed out after {timeout}s"
        )


@dataclass
class MBPPToolContext:
    task_file: Path

    @classmethod
    def from_env(cls) -> "MBPPToolContext":
        task_file = os.environ.get("AGENT_SMITH_TASK_FILE")
        if not task_file:
            raise RuntimeError("AGENT_SMITH_TASK_FILE is required for MBPP tools")
        return cls(Path(task_file))

    def task(self) -> dict:
        return json.loads(self.task_file.read_text())

    def public_tests_source(self) -> str:
        task = self.task()
        imports = "\n".join(task.get("test_imports") or [])
        tests = "\n".join(task.get("test_list") or [])
        return "\n".join(part for part in [imports, tests] if part)

    def run_tests(self, candidate_code: str = "") -> str:
        if not candidate_code:
            candidate_path = Path("/tmp/agent/mbpp_solution.py")
            if candidate_path.exists():
                candidate_code = candidate_path.read_text()
        if not candidate_code.strip():
            return "No candidate code was provided."

        task = self.task()
        test_source = self.public_tests_source()
        full_code = candidate_code + "\n" + test_source + "\n"
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
            handle.write(full_code)
            temp_path = handle.name
        try:
            return run_subprocess([sys.executable, temp_path], timeout=30)
        finally:
            try:
                Path(temp_path).unlink()
            except OSError:
                pass

    def describe_task(self) -> str:
        task = self.task()
        return json.dumps(task, indent=2, ensure_ascii=False)


class WorkspaceBackend:
    """Host or Docker-backed file and command operations."""

    def read_file(self, filepath: str, start_line: int = 1, end_line: int = 200) -> str:
        raise NotImplementedError

    def edit_file(self, filepath: str, old_str: str, new_str: str) -> str:
        raise NotImplementedError

    def list_files(self, directory: str, pattern: str = "*") -> str:
        raise NotImplementedError

    def search_code(self, pattern: str, file_pattern: str = "*.py") -> str:
        raise NotImplementedError

    def run_command(self, command: str, workdir: str = "/testbed", timeout: int = 120) -> str:
        raise NotImplementedError

    def get_patch(self) -> str:
        return self.run_command("git -c core.fileMode=false diff", "/testbed", timeout=60)


class HostBackend(WorkspaceBackend):
    def __init__(self, root: Path):
        self.root = root.resolve(strict=False)

    def _resolve(self, path: str) -> Path:
        candidate = Path(path)
        testbed = Path("/testbed")
        if candidate.is_absolute() and (candidate == testbed or testbed in candidate.parents):
            candidate = self.root / candidate.relative_to("/testbed")
        elif not candidate.is_absolute():
            candidate = self.root / candidate
        resolved = candidate.resolve(strict=False)
        if resolved != self.root and self.root not in resolved.parents:
            raise PermissionError(f"Path outside testbed: {resolved}")
        return resolved

    def read_file(self, filepath: str, start_line: int = 1, end_line: int = 200) -> str:
        path = self._resolve(filepath)
        lines = path.read_text(errors="replace").splitlines()
        start = max(1, int(start_line))
        end = min(len(lines), int(end_line))
        return "\n".join(
            f"{line_no}: {lines[line_no - 1]}" for line_no in range(start, end + 1)
        )

    def edit_file(self, filepath: str, old_str: str, new_str: str) -> str:
        path = self._resolve(filepath)
        content = path.read_text()
        count = content.count(old_str)
        if count != 1:
            return f"edit_file refused: expected exactly one match, found {count}."
        path.write_text(content.replace(old_str, new_str, 1))
        compile_check = run_subprocess(
            [sys.executable, "-m", "py_compile", str(path)], timeout=30
        )
        if "exit_code: 0" not in compile_check and path.suffix == ".py":
            return "Edit applied, but syntax check failed:\n" + compile_check
        return "Edit applied successfully."

    def list_files(self, directory: str, pattern: str = "*") -> str:
        root = self._resolve(directory)
        matches = sorted(
            str(path)
            for path in root.rglob("*")
            if path.is_file() and fnmatch.fnmatch(path.name, pattern)
        )
        return truncate("\n".join(matches))

    def search_code(self, pattern: str, file_pattern: str = "*.py") -> str:
        regex = re.compile(pattern)
        rows: list[str] = []
        for path in self.root.rglob("*"):
            if not path.is_file() or not fnmatch.fnmatch(path.name, file_pattern):
                continue
            try:
                lines = path.read_text(errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                if regex.search(line):
                    rows.append(f"{path}:{line_no} {line}")
        return truncate("\n".join(rows))

    def run_command(self, command: str, workdir: str = "/testbed", timeout: int = 120) -> str:
        cwd = self._resolve(workdir)
        return run_subprocess(["/bin/bash", "-lc", command], cwd=str(cwd), timeout=timeout)

    def get_patch(self) -> str:
        completed = subprocess.run(
            ["git", "-c", "core.fileMode=false", "diff"],
            cwd=str(self.root),
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        if completed.returncode == 0:
            return truncate(completed.stdout)
        return truncate(
            f"exit_code: {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )


class DockerBackend(WorkspaceBackend):
    def __init__(self, image: str, container_id: str | None = None):
        self.image = image
        self.container_id = container_id or os.environ.get("AGENT_SMITH_CONTAINER_ID")
        self._started_by_us = False

    def ensure_container(self) -> str:
        if self.container_id:
            return self.container_id
        if not self.image:
            raise RuntimeError("No docker image configured for SWE-bench tools")
        completed = subprocess.run(
            ["docker", "run", "-d", self.image, "tail", "-f", "/dev/null"],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip())
        self.container_id = completed.stdout.strip()
        self._started_by_us = True
        atexit.register(self.cleanup)
        return self.container_id

    def cleanup(self) -> None:
        if self._started_by_us and self.container_id:
            subprocess.run(
                ["docker", "rm", "-f", self.container_id],
                text=True,
                capture_output=True,
                check=False,
            )

    def _docker_completed(
        self, args: list[str], timeout: int = 120, workdir: str = "/testbed"
    ) -> subprocess.CompletedProcess[str]:
        cid = self.ensure_container()
        command = ["docker", "exec", "-w", workdir, cid] + args
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )

    def _docker_exec(self, args: list[str], timeout: int = 120, workdir: str = "/testbed") -> str:
        try:
            completed = self._docker_completed(args, timeout=timeout, workdir=workdir)
            return truncate(
                f"exit_code: {completed.returncode}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            return truncate(
                f"exit_code: timeout\nstdout:\n{stdout}\nstderr:\n{stderr}\n"
                f"Command timed out after {timeout}s"
            )

    def _docker_stdout(self, args: list[str], timeout: int = 120, workdir: str = "/testbed") -> str:
        try:
            completed = self._docker_completed(args, timeout=timeout, workdir=workdir)
            if completed.returncode == 0:
                return truncate(completed.stdout)
            return truncate(
                f"exit_code: {completed.returncode}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            return truncate(
                f"exit_code: timeout\nstdout:\n{stdout}\nstderr:\n{stderr}\n"
                f"Command timed out after {timeout}s"
            )

    def read_file(self, filepath: str, start_line: int = 1, end_line: int = 200) -> str:
        script = (
            "import pathlib,sys\n"
            "path=pathlib.Path(sys.argv[1])\n"
            "start=int(sys.argv[2]); end=int(sys.argv[3])\n"
            "lines=path.read_text(errors='replace').splitlines()\n"
            "for i in range(max(1,start), min(len(lines),end)+1):\n"
            "    print(f'{i}: {lines[i-1]}')\n"
        )
        return self._docker_stdout(
            ["python", "-c", script, filepath, str(start_line), str(end_line)]
        )

    def edit_file(self, filepath: str, old_str: str, new_str: str) -> str:
        script = (
            "import pathlib, py_compile, sys, traceback\n"
            "path=pathlib.Path(sys.argv[1])\n"
            "old=sys.argv[2]; new=sys.argv[3]\n"
            "content=path.read_text()\n"
            "count=content.count(old)\n"
            "if count != 1:\n"
            "    print(f'edit_file refused: expected exactly one match, found {count}.')\n"
            "    raise SystemExit(2)\n"
            "path.write_text(content.replace(old,new,1))\n"
            "if path.suffix == '.py':\n"
            "    try:\n"
            "        py_compile.compile(str(path), doraise=True)\n"
            "    except Exception:\n"
            "        print('Edit applied, but syntax check failed:')\n"
            "        traceback.print_exc()\n"
            "        raise SystemExit(3)\n"
            "print('Edit applied successfully.')\n"
        )
        return self._docker_exec(
            ["python", "-c", script, filepath, old_str, new_str], timeout=60
        )

    def list_files(self, directory: str, pattern: str = "*") -> str:
        command = f"find {shlex.quote(directory)} -type f -name {shlex.quote(pattern)} | sort | head -500"
        return self._docker_stdout(["/bin/bash", "-lc", command], timeout=60)

    def search_code(self, pattern: str, file_pattern: str = "*.py") -> str:
        script = (
            "import fnmatch, os, re, sys\n"
            "regex = re.compile(sys.argv[1])\n"
            "file_pattern = sys.argv[2]\n"
            "count = 0\n"
            "for root, dirs, files in os.walk('/testbed'):\n"
            "    dirs[:] = [d for d in dirs if d not in {'.git', '.tox', '.venv', '__pycache__'}]\n"
            "    for filename in files:\n"
            "        if not fnmatch.fnmatch(filename, file_pattern):\n"
            "            continue\n"
            "        path = os.path.join(root, filename)\n"
            "        try:\n"
            "            with open(path, errors='replace') as handle:\n"
            "                for line_no, line in enumerate(handle, 1):\n"
            "                    if regex.search(line):\n"
            "                        print(f'{path}:{line_no} {line.rstrip()}')\n"
            "                        count += 1\n"
            "                        if count >= 500:\n"
            "                            raise SystemExit(0)\n"
            "        except OSError:\n"
            "            pass\n"
        )
        return self._docker_stdout(["python", "-c", script, pattern, file_pattern], timeout=90)

    def run_command(self, command: str, workdir: str = "/testbed", timeout: int = 120) -> str:
        return self._docker_exec(["/bin/bash", "-lc", command], workdir=workdir, timeout=timeout)

    def get_patch(self) -> str:
        return self._docker_stdout(
            ["git", "-c", "core.fileMode=false", "diff"], workdir="/testbed", timeout=60
        )


def definition_pattern(name: str) -> str:
    escaped = re.escape(name)
    return rf"^\s*(def|class)\s+{escaped}\b"


def reference_pattern(name: str) -> str:
    escaped = re.escape(name)
    return rf"\b{escaped}\b"


@dataclass
class SWEBenchToolContext:
    task_file: Path | None
    backend: WorkspaceBackend
    eval_script: str = ""

    @classmethod
    def from_env(cls) -> "SWEBenchToolContext":
        task_file_value = os.environ.get("AGENT_SMITH_TASK_FILE")
        task_file = Path(task_file_value) if task_file_value else None
        task: dict = {}
        if task_file and task_file.exists():
            task = json.loads(task_file.read_text())

        root_value = os.environ.get("AGENT_SMITH_TESTBED_PATH")
        if root_value:
            backend: WorkspaceBackend = HostBackend(Path(root_value))
        elif Path("/testbed").exists():
            backend = HostBackend(Path("/testbed"))
        else:
            backend = DockerBackend(
                image=task.get("docker_image", ""),
                container_id=os.environ.get("AGENT_SMITH_CONTAINER_ID"),
            )
        return cls(task_file=task_file, backend=backend, eval_script=task.get("eval_script", ""))

    def read_file(self, filepath: str, start_line: int = 1, end_line: int = 200) -> str:
        return self.backend.read_file(filepath, start_line, end_line)

    def edit_file(self, filepath: str, old_str: str, new_str: str) -> str:
        return self.backend.edit_file(filepath, old_str, new_str)

    def list_files(self, directory: str = "/testbed", pattern: str = "*.py") -> str:
        return self.backend.list_files(directory, pattern)

    def search_code(self, pattern: str, file_pattern: str = "*.py") -> str:
        return self.backend.search_code(pattern, file_pattern)

    def search_definition(self, name: str) -> str:
        return self.backend.search_code(definition_pattern(name), "*.py")

    def find_references(self, name: str, filepath: str = "", line: int = 0) -> str:
        del filepath, line
        return self.backend.search_code(reference_pattern(name), "*.py")

    def run_command(self, command: str, workdir: str = "/testbed") -> str:
        return self.backend.run_command(command, workdir, timeout=180)

    def run_tests(self) -> str:
        if self.eval_script:
            if isinstance(self.backend, HostBackend):
                with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as handle:
                    handle.write(self.eval_script)
                    temp_path = handle.name
                try:
                    return self.backend.run_command(f"bash {shlex.quote(temp_path)}", "/testbed", 900)
                finally:
                    try:
                        Path(temp_path).unlink()
                    except OSError:
                        pass
            script = "cat > /tmp/agent_eval.sh && chmod +x /tmp/agent_eval.sh && /bin/bash /tmp/agent_eval.sh"
            cid = self.backend.ensure_container() if isinstance(self.backend, DockerBackend) else ""
            completed = subprocess.run(
                ["docker", "exec", "-i", "-w", "/testbed", cid, "/bin/bash", "-lc", script],
                input=self.eval_script,
                text=True,
                capture_output=True,
                timeout=900,
                check=False,
            )
            return truncate(
                f"exit_code: {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
            )
        return self.backend.run_command("pytest -q", "/testbed", timeout=900)

    def get_patch(self) -> str:
        return self.backend.get_patch()

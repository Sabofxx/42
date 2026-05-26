"""MCP server exposing mandatory SWE-bench tools."""

from __future__ import annotations

import argparse

from agent_smith.tool_impl import SWEBenchToolContext


ctx: SWEBenchToolContext | None = None


def context() -> SWEBenchToolContext:
    global ctx
    if ctx is None:
        ctx = SWEBenchToolContext.from_env()
    return ctx


def build_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("agent-smith-swebench")

    @mcp.tool()
    def read_file(filepath: str, start_line: int = 1, end_line: int = 200) -> str:
        """Read a file with line numbers, similar to cat -n."""

        return context().read_file(filepath, start_line, end_line)

    @mcp.tool()
    def edit_file(filepath: str, old_str: str, new_str: str) -> str:
        """Replace exactly one old_str occurrence in filepath with new_str."""

        return context().edit_file(filepath, old_str, new_str)

    @mcp.tool()
    def list_files(directory: str = "/testbed", pattern: str = "*.py") -> str:
        """List files in a directory matching a glob pattern."""

        return context().list_files(directory, pattern)

    @mcp.tool()
    def search_code(pattern: str, file_pattern: str = "*.py") -> str:
        """Search code using a grep-like regex pattern."""

        return context().search_code(pattern, file_pattern)

    @mcp.tool()
    def search_function_or_class_definition_in_code(name: str) -> str:
        """Find function or class definitions by name."""

        return context().search_definition(name)

    @mcp.tool()
    def find_references(name: str, filepath: str = "", line: int = 0) -> str:
        """Find references to a symbol name."""

        return context().find_references(name, filepath, line)

    @mcp.tool()
    def run_tests() -> str:
        """Execute the SWE-bench evaluation script or pytest fallback."""

        return context().run_tests()

    @mcp.tool()
    def get_patch() -> str:
        """Return git -c core.fileMode=false diff for current repository changes."""

        return context().get_patch()

    @mcp.tool()
    def run_command(command: str, workdir: str = "/testbed") -> str:
        """Run a shell command in the given workdir and return stdout, stderr, exit code."""

        return context().run_command(command, workdir)

    @mcp.resource("agent://swebench/task")
    def task_resource() -> str:
        task_file = context().task_file
        return task_file.read_text() if task_file and task_file.exists() else "{}"

    @mcp.prompt()
    def swebench_debugger() -> str:
        return (
            "Explore the repository with read_file/search_code, make minimal edits, "
            "run focused tests, then call final_answer(get_patch())."
        )

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true", help="serve streamable HTTP instead of stdio")
    args = parser.parse_args()
    transport = "streamable-http" if args.http else "stdio"
    build_server().run(transport=transport)


if __name__ == "__main__":
    main()


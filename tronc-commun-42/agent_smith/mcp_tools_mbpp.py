"""MCP server exposing MBPP task tools."""

from __future__ import annotations

import argparse

from agent_smith.tool_impl import MBPPToolContext


ctx: MBPPToolContext | None = None


def context() -> MBPPToolContext:
    global ctx
    if ctx is None:
        ctx = MBPPToolContext.from_env()
    return ctx


def build_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("agent-smith-mbpp")

    @mcp.tool()
    def describe_task() -> str:
        """Return the current MBPP task JSON."""

        return context().describe_task()

    @mcp.tool()
    def public_tests() -> str:
        """Return public imports and assertions for the current MBPP task."""

        return context().public_tests_source()

    @mcp.tool()
    def run_tests(candidate_code: str = "") -> str:
        """Run public MBPP tests against candidate_code."""

        return context().run_tests(candidate_code)

    @mcp.resource("agent://mbpp/task")
    def task_resource() -> str:
        return context().describe_task()

    @mcp.prompt()
    def mbpp_solver() -> str:
        return (
            "Solve the MBPP task by writing Python code, testing it with run_tests, "
            "then call final_answer(code)."
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


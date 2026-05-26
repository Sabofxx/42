"""Command-line interface for the sandbox."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent_smith.mcp_client import MCPClient
from agent_smith.models import SandboxConfig
from agent_smith.sandbox import Sandbox


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute Python code in Agent Smith sandbox")
    parser.add_argument("config", nargs="?", help="Sandbox JSON configuration file")
    parser.add_argument("--mcp-stdio", default=None, help="MCP stdio server command")
    parser.add_argument("--mcp-server", default=None, help="MCP streamable HTTP server URL")
    parser.add_argument(
        "--manual",
        action="store_true",
        help="print the generated sandbox manual and exit",
    )
    return parser.parse_args()


def load_config(path: str | None) -> SandboxConfig:
    if not path:
        return SandboxConfig()
    return SandboxConfig.model_validate_json(Path(path).read_text())


def read_code_from_stdin() -> str:
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("Enter sandbox Python code. Finish with Ctrl-D.")
    return sys.stdin.read()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    mcp: MCPClient | None = None
    try:
        if args.mcp_stdio or args.mcp_server:
            mcp = MCPClient(stdio_command=args.mcp_stdio, server_url=args.mcp_server)
            mcp.start()
        sandbox = Sandbox(config=config, tool_client=mcp)
        if args.manual:
            print(sandbox.manual())
            return
        code = read_code_from_stdin()
        result = sandbox.execute(code)
        print(result.observation)
        if result.final_answer is not None:
            print("FINAL_ANSWER:")
            print(result.final_answer)
        if result.error or result.timed_out:
            raise SystemExit(1)
    finally:
        if mcp:
            mcp.close()


if __name__ == "__main__":
    main()


"""Synchronous wrapper around MCP stdio and streamable HTTP clients."""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import threading
from contextlib import AsyncExitStack
from typing import Any

from agent_smith.models import ToolSpec


class MCPClient:
    """Long-lived MCP client session usable from synchronous sandbox code."""

    def __init__(
        self,
        stdio_command: str | None = None,
        server_url: str | None = None,
        env: dict[str, str] | None = None,
    ):
        if not stdio_command and not server_url:
            raise ValueError("Either stdio_command or server_url is required")
        self.stdio_command = stdio_command
        self.server_url = server_url
        self.env = env or os.environ.copy()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()
        self._failed: BaseException | None = None
        self._session = None
        self._shutdown_event: asyncio.Event | None = None
        self._tools: list[ToolSpec] = []

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=30)
        if self._failed:
            raise RuntimeError(f"Failed to start MCP client: {self._failed}") from self._failed
        if not self._ready.is_set():
            raise TimeoutError("Timed out while starting MCP client")

    def close(self) -> None:
        if not self._loop:
            return
        if self._shutdown_event:
            self._loop.call_soon_threadsafe(self._shutdown_event.set)
        if self._thread:
            self._thread.join(timeout=10)

    def __enter__(self) -> "MCPClient":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def list_tools(self) -> list[ToolSpec]:
        return list(self._tools)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        if not self._loop or not self._session:
            raise RuntimeError("MCP client is not started")
        future = asyncio.run_coroutine_threadsafe(
            self._call_tool_async(name, arguments), self._loop
        )
        return future.result()

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._main_async())
        finally:
            self._loop.close()

    async def _main_async(self) -> None:
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            from mcp.client.streamable_http import streamablehttp_client

            self._shutdown_event = asyncio.Event()
            async with AsyncExitStack() as stack:
                if self.stdio_command:
                    argv = shlex.split(self.stdio_command)
                    if not argv:
                        raise ValueError("Empty stdio command")
                    params = StdioServerParameters(
                        command=argv[0],
                        args=argv[1:],
                        env=self.env,
                    )
                    read_stream, write_stream = await stack.enter_async_context(
                        stdio_client(params)
                    )
                else:
                    transport = await stack.enter_async_context(
                        streamablehttp_client(self.server_url)
                    )
                    read_stream, write_stream = transport[0], transport[1]

                self._session = await stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
                await self._session.initialize()
                listed = await self._session.list_tools()
                self._tools = [self._normalize_tool(tool) for tool in listed.tools]
                self._ready.set()
                await self._shutdown_event.wait()
        except BaseException as exc:
            self._failed = exc
            self._ready.set()
        finally:
            self._session = None

    async def _call_tool_async(self, name: str, arguments: dict[str, Any]) -> str:
        result = await self._session.call_tool(name, arguments)
        return self._stringify_result(result)

    @staticmethod
    def _normalize_tool(tool: Any) -> ToolSpec:
        schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None)
        return ToolSpec(
            name=getattr(tool, "name", ""),
            description=getattr(tool, "description", "") or "",
            input_schema=schema or {},
        )

    @staticmethod
    def _stringify_result(result: Any) -> str:
        structured = getattr(result, "structuredContent", None) or getattr(
            result, "structured_content", None
        )
        if structured is not None:
            return json.dumps(structured, ensure_ascii=False, indent=2)
        pieces: list[str] = []
        for content in getattr(result, "content", []) or []:
            text = getattr(content, "text", None)
            if text is not None:
                pieces.append(text)
            else:
                pieces.append(str(content))
        text = "\n".join(pieces)
        if getattr(result, "isError", False) or getattr(result, "is_error", False):
            return "Tool error:\n" + text
        return text

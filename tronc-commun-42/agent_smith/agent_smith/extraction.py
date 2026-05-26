"""Model output extraction and non-Python tool-call normalization."""

from __future__ import annotations

import ast
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any


@dataclass
class ExtractionResult:
    code: str
    warning: str | None = None


_FENCED_RE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
_OPEN_FENCE_RE = re.compile(r"```(?:python|py)?\s*(.*)$", re.DOTALL | re.IGNORECASE)
_TOOL_CALL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_INVOKE_RE = re.compile(r"<invoke\b.*?</invoke>", re.DOTALL)


def _literal(value: Any) -> str:
    return repr(value)


def _call_to_python(name: str, arguments: dict[str, Any] | None = None) -> str:
    arguments = arguments or {}
    args = ", ".join(f"{key}={_literal(value)}" for key, value in arguments.items())
    return f"result = {name}({args})\nprint(result)"


def _extract_json_tool_call(text: str) -> ExtractionResult | None:
    match = _TOOL_CALL_RE.search(text)
    payload = match.group(1) if match else text.strip()
    if not payload.startswith("{"):
        return None
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return None
    name = parsed.get("name") or parsed.get("tool_name")
    arguments = parsed.get("arguments") or parsed.get("args") or {}
    if not name:
        return None
    return ExtractionResult(
        code=_call_to_python(str(name), arguments),
        warning="Converted JSON/Hermes tool call to Python.",
    )


def _extract_xml_tool_call(text: str) -> ExtractionResult | None:
    match = _INVOKE_RE.search(text)
    if not match:
        return None
    try:
        root = ET.fromstring(match.group(0))
    except ET.ParseError:
        return None
    name = root.attrib.get("name")
    if not name:
        return None
    arguments: dict[str, Any] = {}
    for parameter in root.findall(".//parameter"):
        key = parameter.attrib.get("name")
        if not key:
            continue
        value = (parameter.text or "").strip()
        try:
            arguments[key] = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            arguments[key] = value
    return ExtractionResult(
        code=_call_to_python(name, arguments),
        warning="Converted XML invoke tool call to Python.",
    )


def _extract_react_action(text: str) -> ExtractionResult | None:
    action = re.search(r"Action\s*:\s*([A-Za-z_][A-Za-z0-9_]*)", text)
    action_input = re.search(r"Action Input\s*:\s*(.*)", text, re.DOTALL)
    if not action or not action_input:
        return None
    raw_args = action_input.group(1).strip()
    if raw_args.startswith("```"):
        fenced = _FENCED_RE.search(raw_args)
        raw_args = fenced.group(1).strip() if fenced else raw_args.strip("`")
    try:
        parsed = json.loads(raw_args)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(raw_args)
        except (SyntaxError, ValueError):
            parsed = {"input": raw_args}
    if not isinstance(parsed, dict):
        parsed = {"input": parsed}
    return ExtractionResult(
        code=_call_to_python(action.group(1), parsed),
        warning="Converted ReAct Action / Action Input to Python.",
    )


def extract_executable_code(text: str) -> ExtractionResult:
    """Extract Python code from common LLM formats.

    Python code blocks are preferred. A malformed opening fence is interpreted as
    the remainder of the message and reported explicitly to the agent.
    """

    fenced = _FENCED_RE.search(text)
    if fenced:
        return ExtractionResult(code=fenced.group(1).strip())

    open_fence = _OPEN_FENCE_RE.search(text)
    if open_fence:
        return ExtractionResult(
            code=open_fence.group(1).strip(),
            warning="Malformed code block: opening fence had no closing fence; interpreted trailing text as Python.",
        )

    for extractor in (_extract_json_tool_call, _extract_xml_tool_call, _extract_react_action):
        converted = extractor(text)
        if converted is not None:
            return converted

    return ExtractionResult(
        code="",
        warning="No valid Python code block or supported tool-call format was found.",
    )


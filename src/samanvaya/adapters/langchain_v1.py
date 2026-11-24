"""LangChain 1.x sync tool-call middleware, with no dependency at core import time.

This factory depends on `langchain` and `langchain-core` ONLY when called.
It uses the documented wrap_tool_call hook and returns a ToolMessage on denial.

Important: This works on create_agent middleware tool calls, not arbitrary direct
calls to tools/credentials. It is deliberately sync-only; see integration docs.
"""
from __future__ import annotations

from .broker import ConstitutionalToolBroker


def make_langchain_middleware(broker: ConstitutionalToolBroker):
    try:
        from langchain.agents.middleware import wrap_tool_call
        from langchain_core.messages import ToolMessage
    except ImportError as exc:
        raise ImportError("Install `pip install 'samanvaya[langchain]'` first") from exc

    @wrap_tool_call
    def constitutional_tool_hook(request, handler):
        tool_call = request.tool_call
        # request.tool_call is supplied by LangChain. The model cannot provide
        # the BoundTool mapping or trusted plan policy, which are host-owned.
        name = tool_call["name"]
        args = tool_call["args"]
        tool_call_id = tool_call["id"]
        result = broker.invoke(name, args, lambda: handler(request))
        if not result.executed:
            return ToolMessage(content=f"SAMANVAYA_BLOCKED: {result.code}",
                               tool_call_id=tool_call_id, status="error")
        if result.code == "tool_failed":
            return ToolMessage(content="SAMANVAYA_TOOL_FAILED",
                               tool_call_id=tool_call_id, status="error")
        return result.result

    return constitutional_tool_hook

"""Contract-level tests for the documented LangChain v1 tool hook.

These deliberately do NOT pretend to run a real LangChain graph. See
`test_langchain_real.py` (runs in CI with optional LangChain dependencies).
"""
from __future__ import annotations

from datetime import timedelta
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from samanvaya import (ActionIntent, AuditLog, ConstitutionConfig, ConstitutionalGateway,
                       ConstitutionalPolicy, Effect, Mandate, MandateBook)
from samanvaya.adapters import BoundTool, ConstitutionalToolBroker
from samanvaya.adapters.langchain_v1 import make_langchain_middleware
from samanvaya.models import utcnow


class FakeToolMessage:
    def __init__(self, content, tool_call_id, status='success'):
        self.content, self.tool_call_id, self.status = content, tool_call_id, status


class FakeMiddleware:
    def __init__(self, fn):
        self.wrap_tool_call = fn


def wrap_tool_call(fn):
    return FakeMiddleware(fn)


class LangChainContractTests(unittest.TestCase):
    def test_denial_returns_toolmessage_without_calling_handler(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = MandateBook(('human:owner',))
            policy = ConstitutionalPolicy(book, ConstitutionConfig(('human:owner',)))
            broker = ConstitutionalToolBroker(ConstitutionalGateway(policy, AuditLog(Path(tmp)/'audit.jsonl')), ())
            middleware_pkg = types.ModuleType('langchain.agents.middleware')
            middleware_pkg.wrap_tool_call = wrap_tool_call
            mods = {'langchain': types.ModuleType('langchain'),
                    'langchain.agents': types.ModuleType('langchain.agents'),
                    'langchain.agents.middleware': middleware_pkg,
                    'langchain_core': types.ModuleType('langchain_core'),
                    'langchain_core.messages': types.ModuleType('langchain_core.messages')}
            mods['langchain_core.messages'].ToolMessage = FakeToolMessage
            with patch.dict(sys.modules, mods):
                middleware = make_langchain_middleware(broker)
            request = types.SimpleNamespace(tool_call={'name':'delete','args':{},'id':'tool-call-13'})
            result = middleware.wrap_tool_call(request, lambda _: self.fail('Tool executed'))
            self.assertEqual(result.status,'error')
            self.assertEqual(result.tool_call_id,'tool-call-13')
            self.assertIn('tool_not_registered',result.content)

    def test_allow_calls_handler_once_through_gateway(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = MandateBook(('human:owner',))
            book.issue(Mandate('read1','human:owner','agent:a',('read',),('repo:alpha',),
                               ('research',),(Effect.READ,), utcnow()+timedelta(hours=1)))
            policy = ConstitutionalPolicy(book, ConstitutionConfig(('human:owner',)))
            broker = ConstitutionalToolBroker(ConstitutionalGateway(policy, AuditLog(Path(tmp)/'audit.jsonl')),
                                              (BoundTool('read', lambda _: ActionIntent('intent1','agent:a','read1',
                                                          'read','repo:alpha/x','research',Effect.READ)),))
            middleware_pkg = types.ModuleType('langchain.agents.middleware')
            middleware_pkg.wrap_tool_call = wrap_tool_call
            mods = {'langchain': types.ModuleType('langchain'),
                    'langchain.agents': types.ModuleType('langchain.agents'),
                    'langchain.agents.middleware': middleware_pkg,
                    'langchain_core': types.ModuleType('langchain_core'),
                    'langchain_core.messages': types.ModuleType('langchain_core.messages')}
            mods['langchain_core.messages'].ToolMessage = FakeToolMessage
            with patch.dict(sys.modules, mods):
                middleware = make_langchain_middleware(broker)
            invoked=[]
            msg = FakeToolMessage('read success','tool-1')
            result = middleware.wrap_tool_call(types.SimpleNamespace(
                    tool_call={'name':'read','args':{},'id':'tool-1'}),
                    lambda request: invoked.append(1) or msg)
            self.assertIs(result, msg)
            self.assertEqual(invoked, [1])
            self.assertEqual(book.usage('read1'), 1)

if __name__ == '__main__':
    unittest.main()

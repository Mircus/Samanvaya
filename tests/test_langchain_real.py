"""Real installed LangChain v1 create_agent + ToolNode exercise.

Skipped when optional dependencies are missing. GitHub CI installs these in a
separate compatibility job; passing shim tests alone is not sufficient.
"""
from __future__ import annotations

from datetime import timedelta
import os
from pathlib import Path
import tempfile
import unittest

from samanvaya import (ActionIntent, AuditLog, ConstitutionConfig, ConstitutionalGateway,
                       ConstitutionalPolicy, Effect, Mandate, MandateBook)
from samanvaya.adapters import BoundTool, ConstitutionalToolBroker
from samanvaya.adapters.langchain_v1 import make_langchain_middleware
from samanvaya.models import utcnow

try:
    from langchain.agents import create_agent
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage, ToolMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from langchain_core.tools import tool
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

if not HAS_LANGCHAIN and os.environ.get("SAMANVAYA_REQUIRE_LANGCHAIN") == "1":
    raise RuntimeError("LangChain live integration explicitly required but import failed")


if HAS_LANGCHAIN:
    class OneToolModel(BaseChatModel):
        """Fixed, no-network chat model forcing exactly one tool call."""
        requested_tool: str = 'count'

        @property
        def _llm_type(self):
            return 'samanvaya-test-fixed-model'

        def bind_tools(self, tools, **kwargs):
            return self

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            if any(isinstance(m, ToolMessage) for m in messages):
                msg = AIMessage(content='finished')
            else:
                msg = AIMessage(content='', tool_calls=[dict(name=self.requested_tool,
                            args={'item':'x'}, id='call-123', type='tool_call')])
            return ChatResult(generations=[ChatGeneration(message=msg)])


@unittest.skipUnless(HAS_LANGCHAIN, 'LangChain not installed: optional CI job runs this')
class LangChainRealTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.audit = AuditLog(Path(self.temp.name) / 'audit.jsonl')
        self.book = MandateBook(('human:owner',))
        self.book.issue(Mandate('m1', 'human:owner', 'agent:operator', ('read',),
                                ('repo:notes',), ('research',), (Effect.READ,),
                                utcnow()+timedelta(hours=1), max_uses=5))
        self.gateway = ConstitutionalGateway(ConstitutionalPolicy(
            self.book, ConstitutionConfig(('human:owner',))), self.audit)

    def test_agent_executes_authorized_tool(self):
        executed=[]
        @tool
        def count(item: str) -> str:
            """Count one item."""
            executed.append(item)
            return 'counted'

        broker = ConstitutionalToolBroker(self.gateway, (
            BoundTool('count', lambda _: ActionIntent('test-1','agent:operator','m1',
                                                    'read','repo:notes/x','research',Effect.READ)),))
        agent = create_agent(OneToolModel(), tools=[count],
                             middleware=[make_langchain_middleware(broker)])
        result = agent.invoke({'messages': [{'role':'user','content':'Count x'}]})
        self.assertEqual(executed, ['x'])
        self.assertTrue(any(isinstance(m,ToolMessage) for m in result['messages']))
        self.assertEqual(self.book.usage('m1'), 1)

    def test_agent_blocks_unregistered_tool(self):
        executed=[]
        @tool
        def count(item: str) -> str:
            """Count one item."""
            executed.append(item)
            return 'counted'
        broker = ConstitutionalToolBroker(self.gateway, ())
        agent = create_agent(OneToolModel(), tools=[count],
                             middleware=[make_langchain_middleware(broker)])
        result = agent.invoke({'messages': [{'role':'user','content':'Count x'}]})
        self.assertEqual(executed, [])
        messages = [m for m in result['messages'] if isinstance(m,ToolMessage)]
        self.assertTrue(messages)
        self.assertIn('SAMANVAYA_BLOCKED', messages[-1].content)
        self.assertEqual(self.book.usage('m1'), 0)

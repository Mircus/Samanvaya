# Framework portability — LangChain 1.x first

**Verified against published LangChain middleware APIs on 24 Nov 2026.** Local tests do not include an installed LangChain distribution. The optional GitHub Actions job is intended to provide a real-framework proof after push.

## Contract

The trusted host configures:

- `ConstitutionalPolicy` + `MandateBook` (prototype identity semantics; not production authentication);
- a `ConstitutionalPlan` with obligations and facts (the agent must not author its own constitution);
- `BoundTool` mappings from tool names/validated arguments to immutable `ActionIntent` values;
- for a plan-bound tool, an `expected_args_digest` computed over the operator-approved full argument object;
- a `ConstitutionalGateway` that blocks direct access to the host's real tool implementation.

The host continues to own agent memory, orchestration, prompting and the actual tool implementation.

## LangChain v1 integration

Install the optional dependencies:

```bash
python -m pip install -e ".[langchain]"
python -m unittest tests.test_langchain_real -v
```

Typical application code (fill in trusted host construction):

```python
from langchain.agents import create_agent
from langchain_core.tools import tool
from samanvaya.adapters import BoundTool, ConstitutionalToolBroker
from samanvaya.adapters.langchain_v1 import make_langchain_middleware

@tool
def read_report(report_id: str) -> str:
    """Read an authorized report."""
    return trusted_backend.read_report(report_id)

# Build `gateway`, `bindings`, `plan` and `analyzer` in trusted host code.
# For high-consequence actions, real credentials must never be available to
# agent-generated Python or other ungoverned tools.
broker = ConstitutionalToolBroker(gateway, bindings, plan=plan, analyzer=analyzer)
agent = create_agent(
    model=model,
    tools=[read_report],
    middleware=[make_langchain_middleware(broker)],
)
response = agent.invoke({"messages": [{"role": "user", "content": "Read report 123"}]})
```

The LangChain middleware uses the supported `wrap_tool_call` hook, receives `request.tool_call` with `name`, `args`, and `id`, calls the broker once, and yields an error-status `ToolMessage` for any blocked action. Neither prompts nor model-supplied parameters create mandates.

**Unsupported in v0.2:** LangChain async runs, direct `BaseTool.invoke` without agent middleware, other agent graph dispatch paths, injected state modifications after policy evaluation, and raw direct service access. Do not treat the sync middleware as an application-wide sandbox. In a real deployment, enforce credentials and network isolation beyond framework hooks.

### Windows PowerShell

```powershell
py -m pip install -e ".[langchain]"
$env:SAMANVAYA_REQUIRE_LANGCHAIN = "1"
py -m unittest tests.test_langchain_real -v
Remove-Item Env:SAMANVAYA_REQUIRE_LANGCHAIN
```

## What counts as evidence of portability?

1. Baseline `python -m unittest discover -s tests -v`: local unit tests and a double of the documented LangChain request/handler contract.
2. Optional LangChain installation: `test_langchain_real` exercises `create_agent`, a deterministic `BaseChatModel` (no paid LLM calls), and actual LangChain tool handling. It verifies both allowed and blocked calls. A passing CI job is required before claiming end-to-end integration.
3. Production boundary: provision a separate restricted tool service, remove raw service credentials from the agent process, verify the external action against the same immutable intent/parameter digest, and reproduce the denied-bypass test there. **This is not implemented.**

References:
- https://reference.langchain.com/python/langchain/agents/middleware/types/wrap_tool_call
- https://reference.langchain.com/python/langchain/agents/middleware/types/AgentMiddleware/wrap_tool_call
- https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage

## Future adapters — no extra framework invented

- **LangGraph custom ToolNode**: use the same broker behind tool calls, after verified LangChain path; supply separate async gateway / transactional state.
- **Microsoft Agent Governance Toolkit**: prefer integrating Samanvaya's *whole-plan assessments / repair reports* into its existing policy/intervention interfaces, rather than cloning its gates.
- **OpenAI Agents / PydanticAI / Google ADK / CrewAI**: only build thin mapping layers after users demonstrate need. Do not implement generic middleware features already native to their host frameworks.
- **MCP**: consider a remote governed tool gateway only if production isolation demands it; a Python middleware alone is not a non-bypassable boundary.

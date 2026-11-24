# SAMANVAYA v0.2 — differentiation without duplicating governance infrastructure

**Status:** executable research hypothesis, not a proven claim of novelty. Reviewed 24 November 2026.

## What we deliberately do not build

Samanvaya is **not** an identity provider, policy-engine replacement, agent orchestrator, cryptographic ledger, sandbox, observability platform, or LangChain alternative. Existing systems are substantially stronger in those domains:

| Mature or emerging system | Capabilities not to reimplement | Evidence / documentation |
|---|---|---|
| Microsoft Agent Governance Toolkit / ACS | Agent runtime governance, policies, identity, isolation, intervention points, multi-framework adapters | https://github.com/microsoft/agent-governance-toolkit ; https://microsoft.github.io/agent-governance-toolkit/ |
| Open Policy Agent (OPA) | General-purpose Rego policy evaluation and policy distribution | https://www.openpolicyagent.org/docs |
| Cedar | Scoped resource authorization and analysable policies | https://www.cedarpolicy.com/ |
| OpenFGA | Relationship-based authorization | https://openfga.dev/ |
| Agent Governance Protocol (AGP) | Collective voting, quorum, veto and auditable agreement | https://github.com/agpprotocol/agp |
| LangChain / LangGraph | Agent execution, tools, stateful orchestration and `wrap_tool_call` middleware | https://docs.langchain.com/oss/python/langchain/middleware/custom |
| HUAP (original project) | JSONL trace patterns, replay, diff, CI and human review workflow | https://github.com/Mircus/HUAP |

A constitutional check attached to a tool call is **not by itself novel**. Microsoft AGT even has a constitutional-constraint extension design. We cannot claim otherwise: https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/adr/0006-constitutional-constraint-layer-as-community-extension.md

## Narrow research hypothesis

**H1 — Multi-action coherence:** A case may consist of individually authorized actions but remain inadmissible as a *whole* because facts, duties, mutually exclusive actions or prerequisites conflict.

**H2 — Certified finite-catalog repair:** Given a trusted, finite catalog of permissible modifications, we can find least-cost admissible revisions and supply an **explicit, scoped minimality certificate** (only within that catalog). Neither mandates nor facts are created in this process.

**H3 — Portable decision integration:** This analysis can govern an existing tool execution loop through a framework adapter rather than replacing the loop.

These hypotheses are a contribution **only if we can show that existing products cannot obtain the same result comparably through ordinary configuration**. They are currently implementation objectives, not established research firsts.

## What v0.2 implements

1. `CoherenceAnalyzer` checks a typed whole-plan object against the original five-pillar action policy, supported factual obligations, mutually exclusive steps, and ordering constraints.
2. `MinimalRepairExplorer` performs bounded cost-ordered search over a trusted catalog of replace/drop edits. It explores at most `max_variants`; no fabricated new permissions or evidence. The report says whether minimality was proven **within the fully explored catalog**.
3. `ConstitutionalToolBroker` binds a real tool name, an operator-owned intent mapping, a plan step and an exact JSON-argument digest. It rechecks plan coherence and then invokes the existing Samanvaya gateway.
4. `make_langchain_middleware` uses LangChain 1.x `wrap_tool_call`. It blocks denied calls with a `ToolMessage` and never calls the handler on denial.
5. Executable reference scenarios, contract-level integration tests and a real LangChain compatibility test module (CI dependency required).

## What is still missing

- Authentication: actors, approvals, endorsements and witnesses are **assertions**; evidence status is not checked against a third-party authority.
- Action parameters: digest binding is enforced only by the **plan-bound broker**, not for arbitrary direct gateway use.
- External isolation: agent code with raw credentials can bypass the middleware and broker entirely. A hardened deployment requires a trusted tool broker, credential isolation and no alternate egress.
- Atomicity: plan coherence may change between preflight and effect; storage, mandate quotas and case updates are not transactionally bound across processes.
- Fact semantics: obligations are declared by a trusted plan author; changing an action's name can change which obligations apply. Alternatives must be supplied by an accountable operator, not freely invented by a model.
- Global optimality: minimal repair is scoped to supplied edits; it does **not** solve unrestricted normative optimization or guarantee that the plan is ethically adequate.
- Framework validation: the real LangChain test **requires the optional dependency and must pass in CI** before we claim proven live interoperability. We do not substitute mock integration tests for live tests.

## Evaluation design (a falsifiable claim)

Compare Samanvaya, Microsoft AGT/ACS, OPA/Cedar-based policies, and AGP on the **same cases**:

1. individually allowed action, but required environmental fact missing;
2. contradictory verified factual values;
3. individually valid actions that violate a cross-action order or exclusion;
4. fresh fact replaced by expired evidence;
5. finite trusted alternative catalog with cost `1` unauthorized and cost `2` valid;
6. tool call attempted with altered parameters after plan review.

For each solution report: native support, simple policy configuration, custom code required, correctness on negative cases, operational complexity, performance, maintenance, and ability to give a constrained minimality certificate. Publish scripts, exact versions, input facts and logs. **No third-party benchmark has yet been run.** The included `benchmarks/reference_suite.py` establishes only an internal action-only baseline.

## Stop/go criterion

If an established toolkit supplies H1–H3 with less code, equal clarity, equal verification and comparable performance, Samanvaya should become a specification/plugin **on that toolkit**, not compete with it. If a genuine gap survives comparative testing, extend only that gap.

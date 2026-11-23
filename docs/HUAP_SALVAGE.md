# HUAP → Samanvaya: audited salvage decisions

Source: https://github.com/Mircus/HUAP; inspected 2026-11-23, `main` tree `41f8548c9b6c38814bf4634df44b4f92748304b0`.

HUAP's README frames it as trace-first instrumentation: replay, diff, CI/evaluation, model routing, human gates, pods and safe tools. We inspected source files in `packages/hu-core/hu_core/{trace,tools,orchestrator,policy,runtime,contracts}`.

## Salvage ledger

| HUAP subsystem / source | Disposition | Samanvaya equivalent | Reason |
|---|---|---|---|
| `trace/models.py`, `trace/writer.py` | **Preserve design, implement fresh** | `audit.py`, `models.py` | Explicit event envelope and JSONL are valuable; introduce separate constitutional event version and hash chain. |
| `trace/diff.py`, `trace/replay.py` | **Preserve design, narrow scope** | `audit.diff_traces`, `replay.replay_constitution` | Safe policy replay is useful; no external side effects in replay. Full HUAP workflow replay intentionally not ported. |
| `eval/`, `ci/` | **Preserve test-first mindset** | `tests/`, GitHub Actions | Regression gating must cover authority invariants, not just cost/quality. |
| `runtime/human_gate.py` | **Keep concept, replace implementation** | `HumanApproval`, `ESCALATE` | A local JSON decision file is not authentication or an enforceable constitutional grant. |
| `tools/registry.py` | **Keep tool metadata and execution boundary concept; replace permission check** | `ConstitutionalGateway`, `MandateBook` | Existing `check_permissions=False` path and caller-asserted `ExecutionContext` are inappropriate as sole authorization controls. |
| `policy/base.py` | **Do not port as enforcement** | `ConstitutionalPolicy` | Existing pre/post hooks are no-op placeholders. |
| `orchestrator/graph.py` | **Do not duplicate general workflow engine** | Host adapter contract (planned) | HUAP executes node/edge workflows; constitutional governance should remain framework-neutral. |
| `contracts/_base.py` | **Preserve explicit contract discipline** | Immutable dataclasses and schema docs | New constitutional objects should not inherit domain-specific coaching/pod interfaces. |
| `memory/`, `services/model_router.py`, `plugins/` | **Not core** | Optional ports planned | Useful in HUAP, but creating another framework duplicates HYRI/LangGraph. |
| `adapters/{langchain,crewai}.py` | **Defer** | Host tool adapters (v0.2) | Runtime integration should ensure calls cannot skip authorization. |

## What is actually migrated

**A clean reimplementation** of the most valuable instrumentation concepts, including JSONL events, semantic diff, no-side-effect replay, CI-based conformance tests and a minimal CLI. We also supply a **read-only HUAP trace inspector** (`compat/huap_trace.py`). No legacy HUAP Python source files have been directly copied into the baseline. Reusing old HUAP workflow execution without robust authority enforcement would create an unjustified security impression.

## What must remain separate

- HUAP legacy trace data is evidence of recorded actions, not proof that they were authorized.
- New constitutional decisions are emitted under `samanvaya.audit.v0.1` rather than pretending compatibility with HUAP trace schema 0.1.
- Policies are evaluated at the actual entry to a governed tool adapter, not only at workflow-planning time.
- Host integrations with HYRI, LangGraph, CrewAI or a future hypergraph runtime should be plugins or adapters rather than core dependencies.

## Potential future direct-source salvage

If needed, selectively transplant HUAP's mature report HTML renderer and CI diff front end into optional packages after preserving MIT notices and writing tests for new constitutional event envelopes. Do not port the old policy placeholder, unsandboxed executor, or unverified gate decisions unchanged.

# Claude / Codex handoff: Samanvaya v0.2

Do **not** start a new agent platform, add an LLM panel, or rewrite LangChain. Keep the repo's core standard-library-only. The current architecture is: v0.1 action policy + v0.2 whole-plan coherence + bounded repair search + optional host adapters.

## Required first reading

`README.md` → `docs/DIFFERENTIATOR_AND_NON_DUPLICATION.md` → `docs/ARCHITECTURE.md` → `docs/FRAMEWORK_PORTABILITY.md` → `docs/EXPERIMENT_PROTOCOL.md` → `docs/SECURITY.md` → `docs/adr/0005-coherence-repair-not-another-agent-runtime.md`.

## P0 — verify real framework interoperability

1. Install the pinned supported LangChain 1.x range and make `tests/test_langchain_real.py` pass with actual `create_agent` + deterministic fake chat model and tool; do not remove the test if it exposes API mismatches.
2. Verify that blocked calls do not execute **any** side effect, including async paths. Current adapter is sync only: implement an async gateway correctly or reject async tool paths fail-closed.
3. Add an adversarial test in which another middleware mutates tool arguments *after* governance. Ensure final tool boundary sees the exact authorized arguments.
4. Isolate tool credentials behind a separate process/service; prove agent-created arbitrary Python can't call raw tools. Middleware alone is not a security boundary.

## P1 — differentiate responsibly

5. Run cases from `docs/DIFFERENTIATOR_AND_NON_DUPLICATION.md` using upstream Microsoft AGT/ACS and OPA/Cedar/AGP. Publish reproducible configs and results before claiming originality.
6. Replace caller-asserted `verified` facts with signed or independently validated evidence, explicit subject, validity, confidence and provenance. Do not paper over with model judgments.
7. Make the plan and constraint catalog operator-authenticated, versioned and immutable while a run executes. Bind plan digest, mandate state, facts and tool argument digest to an execution receipt.
8. Consider genuinely new repair solvers only once policy-only baselines have been run. Current uniform-cost search is deliberately small and complete only for a finite catalog.

## P2 — engineering refinements

9. Transactional finite-use budgets and atomic check/reserve/effect semantics across processes; test races.
10. Better collective semantics: independently authenticated member endorsements, dissent preservation, overlapping collectives, and responsibilities that cannot be washed away by group votes.
11. Counterfactual multi-stage plans; plan evolution, new facts and automatic invalidation. Begin with deterministic solvers and evidence, not more prompts.
12. Import external policies/decision engines via adapters, **not** copied policy machinery.

## Required reporting per PR

Give exact pinned dependencies, pass/fail counts, evidence of actual framework behavior, new features, security assumptions, upstream work considered, and whether each piece is duplicated elsewhere. No claim of non-bypassability until host isolation proves it.

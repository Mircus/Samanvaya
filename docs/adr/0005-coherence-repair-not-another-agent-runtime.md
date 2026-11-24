# ADR-0005 — Differentiate through whole-plan coherence and scoped minimal repair

**Date:** 2026-11-24
**Status:** Accepted for experimental v0.2; external novelty claims deferred

## Context

Microsoft AGT/ACS, OPA, Cedar, AGP, LangChain and other projects already implement policy, authority, runtime interception, collective governance, tracing or related features. A new generic agent governance platform would duplicate substantial mature work.

## Decision

1. Keep the independent Samanvaya v0.1 decision kernel as an *experimental reference*, not a replacement for production authorization services.
2. Extend it with a typed, whole-plan coherence assessor for evidence, obligations, sequencing and incompatible actions.
3. Add finite-catalog, cost-ordered repair suggestions with explicit minimality scope; do not automatically enact them.
4. Demonstrate portability using a thin LangChain v1 middleware and a framework-neutral broker; no new orchestration engine.
5. Compare with upstream capabilities before building further authorization, audit, broker or identity infrastructure.

## Consequences

- Small dependencies; no LLM required for local proof-of-concept.
- A real differentiator is possible but **not established as unique** without a fair third-party benchmark.
- No production claim: authenticated credentials, evidence attestation, transactional updates, process isolation and live LangChain testing remain distinct gates.
- One known issue: modifying an action may change which obligation triggers; therefore plan and repair catalog authorship must be trusted.

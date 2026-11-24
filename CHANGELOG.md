# Changelog

## 0.1.0 — 2026-11-23 — Foundational baseline

Initial constitutional kernel built as a fresh independent Python package, inspired by selectively retained HUAP design patterns. Includes typed mandates, policy/collective checking, JSONL audits, revocation and quotas, simulated action gateway, safe policy replay, HUAP trace inspection, CLI, tests, CI and architectural documentation.

**Warning:** Caller-supplied identities, evidence-status claims, approvals and endorsements are not verified. Host tool broker enforcement and independent audit trust are not implemented.

## 0.2.0 — 2026-11-24 — Coherence, bounded repair and thin framework bridge

- Added whole-plan `CoherenceAnalyzer` for typed factual, ordering and exclusion obligations.
- Added finite-catalog cost-ordered `MinimalRepairExplorer` with explicit proof scope.
- Added `ConstitutionalToolBroker`, plan-bound argument digests, and optional LangChain v1 middleware.
- Added no-network community land demo, machine-readable internal reference suite and adversarial tests.
- Added non-duplication study, experimental protocol, interoperability guide, ADR-0005 and Claude/Codex handoff.
- Added separate GitHub Actions job to test installed LangChain 1.x integration.

**Still not production-secure.** LangChain has not been installed or executed in the originating local environment. The live interoperability tests are marked/skipped locally and must pass after a CI environment installs the optional dependency.

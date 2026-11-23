# Samanvaya constitutional charter — v0.1

**Status:** architectural baseline. The terms **MUST** and **MUST NOT** here specify design requirements; they are not claims that this prototype enforces them across an operating system.

## Article I — Human primacy and non-sovereignty

Agents have capabilities, not inherent political or legal authority. Every authority grant MUST trace to an identifiable human or institution acting as a principal. A model MUST NOT mint its own authority. Real principal authentication is a v0.2 requirement; the current trusted-root string is a testing stand-in.

## Article II — Grounding (Ṛta)

Consequential actions require evidence with a provenance chain. When relevant evidence is missing, the verdict MUST be `UNKNOWN` and action MUST NOT execute. Contradictory evidence MUST block action. Evaluators MUST distinguish factual evidence from instructions embedded inside untrusted documents.

## Article III — Purpose and obligations (Dharma)

The authorized purpose is part of authority. A permitted action cannot be reused for a non-permitted purpose. Declared harm or unresolved prohibited risk MUST NOT be ignored. False certainty and harmful effects require a repair/escalation path rather than silent override.

## Article IV — Bounded authority (Adhikāra)

Mandates MUST specify holder, issuer, allowed actions, resource scopes, purposes, effects, expiration and quota. Delegations MUST be no broader than their parents and MUST become ineffective when an ancestor expires or is revoked. Unknown authority MUST be denied.

## Article V — Collective organs (Samanvaya)

A collective is a first-class actor with a defined membership, quorum and accountable human principal. Its rights MUST NOT be inferred by pooling private rights of members. Endorsements require integrity, authentication and freshness in hardened versions.

## Article VI — Continuing governability (Punarnavīkaraṇa)

High-impact effects require escalation to an identified human decision-maker. Approval MUST be scoped to a particular proposal and expiry. Revocation MUST interrupt future actions and propagate through delegated descendants. Long-running actions and compensating transactions require additional mechanisms not yet implemented.

## Article VII — Audit and contestability

Actions MUST emit a decision record before an effect. Audits SHOULD support independent verification, policy replay and a trace of responsible principals. No system SHOULD equate a trace hash with trustworthiness without an external integrity anchor.

## Article VIII — Fail-closed execution

`DENY`, `UNKNOWN` and `ESCALATE` all mean **no execution**. An internal logging or policy error MUST NOT default to success. Approval cannot enlarge a mandate or overrule other hard constraints. Direct tool handles must not be exposed to untrusted agents in real deployments.

## Article IX — No hidden redefinition

Changes to constitutional policy MUST be versioned, reviewed, accompanied by migration notes, and tested against a stable conformance suite. Agents MUST NOT silently change the constitution under which they operate.

## Article X — Accountability is not dissolved by collectives

When a group acts, its event provenance must retain the individual contributor identities and the responsible human principal. Collective action can distribute execution, never eliminate accountability.

## Current executable coverage

- **Implemented (prototype):** checks in Articles II–VI at the data-assertion level; fail-closed gateway; JSONL decision audit; finite-use quota; structurally bounded delegation; revocation; collective quorum.
- **Partially implemented:** trace diff and side-effect-free decision replay; local trace hash chain; temporal review.
- **Not implemented:** authentication, signatures, verified data provenance, immutable external audit anchoring, safe host-tool sandbox, exactly-once semantics, distributed revocation and quota consistency, independent human approval UI, compensation for external effects.

Read [SECURITY.md](SECURITY.md) before deploying on real tools.

# Engineering handoff to Claude / Codex

**Read first**: `README.md`, `docs/CONSTITUTION.md`, `docs/SECURITY.md`, `docs/HUAP_SALVAGE.md`, `docs/TWELVE_LAWS_MATRIX.md`.

## Mission

Improve this **small constitutional kernel** into a genuinely enforceable control layer for accountable agent collectives. Preserve the five-pillar design, fail-closed semantics, and concrete evidence of correctness. Do not expand it into an agent platform, HYRI replacement, giant control plane, or prompt-only moral theater.

## Baseline inventory

- Standard library, Python 3.11+, `src/samanvaya/` package.
- `models.py`: immutable typed objects.
- `mandates.py`: scope attenuation, expiry, quota, ancestor revocation.
- `constitution.py`: deterministic policy with four outcomes.
- `gateway.py`: audit before side effect and finite quota reservation.
- `audit.py`, `replay.py`: trace, validate, diff, replay decisions without effects.
- `compat/huap_trace.py`: read-only legacy HUAP trace inspection.
- `tests/`: negative/adversarial policy tests.

## Immediate work, ranked

**P0 — Authenticate and enforce**

1. Introduce a non-forgeable identity/authorization boundary. Current strings can be spoofed; this is not a credible security model. Implement a testable `PrincipalVerifier` with one concrete secure host integration, not just a new interface.
2. Make tools reachable *only* through the governed broker in that demonstration, and prove untrusted actors cannot invoke a raw tool. No flag may disable the authorization check.
3. Redesign `HumanApproval` to bind an authenticated person to an immutable action-intent digest, policy version, expiration and optional reviewer role; the host owns authentication. Prevent replay and cross-intent reuse.
4. Replace `EvidenceStatus.VERIFIED` caller assertion with verifier-produced attestations. Add malicious evidence, expired evidence and contradictory evidence cases.
5. Improve the mandate ledger: durable atomic quotas, authenticated issuance and revocation, signed or tamper-evident authority lineage, consistent concurrency and crash recovery.

**P1 — Strengthen constitutive structure**

6. Add a typed hyperedge protocol for membership roles, accountable owner, distinct signed endorsements, veto and delegated subcollectives. The collective **never** receives the union of member powers by default.
7. Make policy output explainable but not manipulable. Include rule IDs, version IDs and structured evidence references. Add tests for all `ALLOW | DENY | UNKNOWN | ESCALATE` cases.
8. Build a verifiable trace-replay facility that uses fixed constitution version and independently anchored audit checkpoints; preserve the existing HUAP-inspired diff interface.
9. Retrieve and verify *all twelve* original Srinivas Gutta laws. Mark exact titles/phrasing and citations before mapping to the pentad. No fabrication or casual conflation.
10. Add a minimal LangGraph or HYRI adapter demo **only after** P0 tests establish enforcement in a controlled host.

## Required acceptance tests

- A model-generated string cannot grant, sign or widen its own authority.
- Tool calls outside the broker are blocked by host isolation, not simply discouraged.
- Permission to read does not entail permission to publish, send or delete.
- A mandate is invalid after expiry/revocation, including every descendant.
- Two simulated endorsements by one signer do not satisfy a two-person quorum.
- One collective member cannot claim the other members' private privileges.
- A valid human approval does not override contradictory evidence or an out-of-scope action.
- A trace write failure prevents the side effect.
- Parallel quota spending cannot exceed a configured maximum.
- Policy replay never invokes a tool or mutates external state.
- An evidence provider cannot assert trust merely by setting `verified=true` in its own output.
- Every asserted law-to-implementation mapping has a cited text and a negative test.

## Reporting requirements

For each PR, provide: scope, changed source files, tests run and actual output, threat model change, incomplete guarantees, any introduced dependencies and rollback plan. No unverified claims of production readiness. Keep commits small, tests passing, and do not overwrite HUAP. Do not introduce any cloud expense or external effects during the demo.

## Recommended first concrete PR

`P0-identity-and-broker`: authenticated mock principal tokens + a controlled subprocess/tool broker with explicit action scope, negative bypass test, and versioned signed approval protocol. Add `SECURITY.md` updates indicating exactly which guarantees moved from 'No' to 'Demonstrated'.

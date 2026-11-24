> **2026-11-24 note:** v0.2 now contains experimental whole-plan coherence,
> finite-catalog repair, a generic tool broker, and an optional sync LangChain
> middleware. The security milestones below **remain incomplete**; v0.2's
> existence must not be confused with production-grade enforcement. See
> `DIFFERENTIATOR_AND_NON_DUPLICATION.md` and `CLAUDE_CODEX_V02_HANDOFF.md`.

# Roadmap: evidence-driven, bounded engineering

## v0.1 — Baseline (this archive)

- [x] New repository layout and documentation
- [x] Five-pillar constitutional evaluator and typed vocabulary
- [x] Explicit finite-use mandates and structural delegation constraints
- [x] Collective hyperedge membership, quorum and accountable principal checks
- [x] Expiration, ancestor revocation, human escalation, purpose and evidence checks
- [x] JSONL decision audit, semantic trace diff and integrity validation
- [x] Safe policy replay and HUAP v0.1 read-only trace inspection
- [x] Executable simulation + unittest/CI scaffold
- [ ] Production-safe identity or attestation (**not included**)

## v0.2 — Make authorization meaningful at the host boundary

1. Versioned `PrincipalVerifier` interface and authenticated mock provider for tests.
2. Binding principals to actual work identities (not to model-generated strings).
3. Versioned `EvidenceVerifier`: signed source metadata, digest validation, freshness, subject and intended purpose.
4. Authenticated `HumanApprovalPort`, scoped to proposal hash, policy version, expiry and named reviewer.
5. No-bypass `ToolBroker` integration demo with constrained credentials and negative bypass test.
6. Replace in-memory mandate ledger with transactionally consistent storage and atomic quota reservations.
7. Track policy version and input normalization in each `Decision` for deterministic replay.
8. Produce a formal v0.2 JSON Schema for event and mandate envelopes.

**Stop condition:** Until actor, evidence and human review are authenticated, none of the hard guarantees should be represented as fulfilled.

## v0.3 — Collective intelligence and verifiable authority

1. Authenticated endorsements and explicit quorum/role rules; configurable dissent and veto.
2. Group hyperedge as first-class authority principal; multiple overlapping hyperedges.
3. Actor membership leases, dynamic member addition/revocation, separation of duties.
4. Delegation graph with cryptographic parent provenance, attenuation and revocation fan-out.
5. Link accountable principal and responsible contributors to every audit receipt.
6. Counterfactual checks: could action have been safely refused, delayed, or repaired?

## v0.4 — Continuing governability

1. Interrupt/renew lease control for in-flight actions and long campaigns.
2. Compensation protocols for reversible effects; explicit refusal for irreversible ones without higher approval.
3. Remote audit checkpoint or append-only sink.
4. Policy migration governance: signed constitution version, approval workflow and rollback.
5. Adversarial benchmark mapped to **verified** full article texts of Srinivas's twelve laws.
6. Optional HYRI adapter or other host integration, without a new UI/control plane.

## Anti-roadmap — do not build

- No replacement for HYRI Core, LangGraph, CrewAI or existing workflow orchestration.
- No simulated bureaucracy with five LLM role prompts instead of enforced checks.
- No agent-granted policy override.
- No claims of certified Gutta-law conformance until texts and tests are independently verified.
- No large platform rewrite before the v0.2 bypass/identity exercise passes.

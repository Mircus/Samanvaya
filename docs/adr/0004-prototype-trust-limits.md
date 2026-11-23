# ADR-0004: Explicitly label assertion-level checks as non-secure

- **Date:** 2026-11-23
- **Status:** Accepted for baseline

## Decision

The v0.1 identity, approval, evidence and endorsement payloads are **unauthenticated assertions**. This fact must appear in README, code docstrings, SECURITY and handoff. No component may advertise the prototype as production-ready authorization or claim legal compliance with twelve laws.

## Consequences

Identity provider, verifier-issued attestations, immutable proposal hashes, signed human reviews and an isolated tool broker are the first engineering milestones. All future 'guarantee' language must be backed by negative tests and a stated threat model.

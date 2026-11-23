# ADR-0003: Audit before effect; retain four decision states

- **Date:** 2026-11-23
- **Status:** Accepted for baseline

## Decision

Policies yield `ALLOW`, `DENY`, `UNKNOWN`, or `ESCALATE`; only `ALLOW` enters a governed effect adapter. The gateway writes the full proposal and decision before invoking a callable. It records start and completion/failure separately. Missing audit capability prevents execution.

## Consequences

Do not collapse insufficient evidence into `DENY` or `ALLOW`, and do not call a pending review an authorization. A local hash-chain provides consistency, not anti-tampering security. Durable log storage and independent anchoring are later requirements.

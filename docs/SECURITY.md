# Security model, limitations and non-goals

## DO NOT DEPLOY AS A SECURITY ENFORCEMENT PRODUCT (v0.1)

The local prototype demonstrates **structural constitutional checks**, not authentication, a hardened sandbox, or resistance to a compromised hosting process. v0.1 protects only tool calls that cooperate with `ConstitutionalGateway`. The threat model deliberately assumes a trusted single-process host and test-issued identities; this assumption is not acceptable for untrusted deployed agents.

| Claim | v0.1 actual state | Work required |
|---|---|---|
| Identity is authenticated | **No.** Principals are caller-supplied strings. | OIDC/session authentication or signed workload identities verified outside the model. |
| `EvidenceStatus.VERIFIED` means verified | **No.** It is a supplied enum assertion. | Source-specific attestation, freshness, provenance, signer trust roots, content hashes. |
| Endorsements prove consent | **No.** Names are asserted; quorum is structural only. | Per-intent signed attestations with nonce, expiry, role and separation-of-duties policy. |
| Human approval represents a real human | **No.** Reviewer string is asserted. | Authenticated review UI + bound approvals recorded immutably. |
| Agents cannot call tools directly | **No.** The host can bypass this library. | Exclusive tool broker, subprocess isolation, restricted credentials and egress. |
| Mandates survive process crash | **No.** In-memory ledger. | Transactional durable store, atomic reservations, fencing tokens. |
| Logs are tamper-proof | **No.** Local hash chain detects corruption only against trusted anchor. | Signed checkpoints / external append-only store and retention policy. |
| Effects can always be undone | **No.** Synchronous callable with no compensation. | Reversible transaction design / compensating actions / idempotency keys. |
| Revocation interrupts in-flight actions | **No.** Future proposals only. | Cancellation, leases, short-lived credentials, in-flight revocation checkpoints. |
| Zero data leakage in logs | **No.** Intent fields, evidence sources are logged. | Privacy classification, explicit redaction and minimization. |

## Threat cases and desired future tests

1. **Impersonation:** agent submits `actor="human:owner"` or `issuer="human:owner"` → must fail with authenticated principal binding.
2. **Forged quorum:** one agent claims 2 consenting names → must fail without distinct verifiable signatures.
3. **Fake evidence:** agent marks its own text `VERIFIED` → must fail without trusted evidence-provider attestations.
4. **Tool-bypass:** agent obtains raw SDK connection and calls external service → host integration must block via broker and isolated credentials.
5. **Delegation laundering:** holder delegates wider purpose/action/resource than its own → structurally denied already; verify across credentials and concurrent updates.
6. **Quota race:** parallel calls spend the last action allowance twice → needs durable atomic reservation.
7. **Trace substitution:** malicious host replaces audit file → needs external anchored signature or immutable audit sink.
8. **Untrusted prompt instructions:** evidence document instructs model to ignore policy → evidence data must not be executable instructions.
9. **Long-running revoked action:** grant revoked after execution starts → use leases and cancellation checkpoints.
10. **Malformed/unparseable resource:** ambiguous paths, unicode spoofing and percent encodings → validate against canonical resource-adapter representation.

## Hard rules for future contributors

- Never add a `skip_policy`/`check_permissions=False` feature to governed tool execution.
- Never interpret a generated narrative as a principal signature, a verified source, or a legal mandate.
- Approval cannot override a known DENY or convert UNKNOWN evidence into fact.
- Fail closed if audit-before-effect, mandate reservation, or principal verification fails.
- Keep the policy engine deterministic and side-effect-free.
- Require adversarial tests for every security-related change. Prefer a smaller correct kernel to dozens of loosely enforced agent roles.

## Responsible release policy

Do not market this as compliance certification, enterprise-ready policy enforcement or legal accountability. Do not connect to payment, production databases, email, physical devices or privileged clouds without completing security milestones and external review. Report security defects privately to the repository maintainers rather than attaching secrets to public issues.

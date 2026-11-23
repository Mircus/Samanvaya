<p align="center">
  <img src="assets/samanvaya-logo.png" alt="Samanvaya — indigo and emerald emblem" width="560">
</p>

# SAMANVAYA

**An executable constitution for accountable AI agent collectives.**

*Ṛta · Dharma · Adhikāra · Samanvaya · Punarnavīkaraṇa*

> Intelligence may be distributed. Responsibility cannot disappear.

**Status: v0.1 experimental foundation (23 November 2026). Not production-secure.**

Samanvaya is a small, standard-library Python constitutional kernel. It borrows HUAP's useful trace-first philosophy—replay, diff, explicit contracts, evaluation-oriented testing—while placing **legitimate authority** in front of consequential agent actions. Its objective is to become an enforceable, inspectable governance layer for agent systems, not a new LLM framework or another general-purpose UI.

The five Sanskrit-derived architectural principles are design inspirations, **not claims that classical Vedic texts directly specified software requirements**. See [VEDIC_FOUNDATIONS.md](docs/VEDIC_FOUNDATIONS.md).

## What works now

- **Constitutional gateway**: agent requests are checked before the registered callable executes.
- **Ṛta / evidence**: missing evidence becomes `UNKNOWN`; conflicting evidence becomes `DENY`.
- **Dharma / purpose**: actions must match a bounded purpose; declared harm is refused pending repair.
- **Adhikāra / mandates**: explicit issuer, holder, verb, resource scope, purpose, permitted effect, expiration, quota, constrained delegation and revocation.
- **Samanvaya / hyperedges**: explicit agent collectives with unique members, quorum and a named accountable human principal; collectives cannot inherit the union of member permissions.
- **Punarnavīkaraṇa / correction**: expiration, revocation cascades, and intent-scoped human review.
- **Audit + replay**: chain-linked JSONL decision audit, integrity check, semantic diff, and no-side-effect re-evaluation of decisions using a fresh policy.
- **HUAP compatibility**: read-only inspection of existing HUAP JSONL traces. Legacy traces do **not** convey authority.
- **19 unit tests** and GitHub Actions test workflow, with no external runtime dependencies.

## What does **not** work yet

**Do not mistake this for a production security boundary.** Identity strings, evidence `verified` status, human approvals and collective endorsements are **caller assertions**; there are no cryptographic signatures, authenticated human sessions, process sandbox, durable transactional quota ledger, network isolation, or distributed consensus. Agents can bypass the gateway if the host application gives them raw tool access. A local JSONL hash chain does not independently authenticate its own origin.

The first hardening priority is secure, exclusive integration at every tool/side-effect boundary, followed by authenticated principals and attestations. See [SECURITY.md](docs/SECURITY.md), [ROADMAP.md](docs/ROADMAP.md) and [HANDOFF_FOR_CLAUDE_CODEX.md](docs/HANDOFF_FOR_CLAUDE_CODEX.md).

## Install and run (Python 3.11+)

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m samanvaya demo --audit ./demo.jsonl
python -m samanvaya verify-audit ./demo.jsonl
```

The demo simulates three cases without calling external services:

```text
safe-read: ALLOW (...), executed=True
escalate-publish: ESCALATE (human_review_required), executed=False
deny-deletion: DENY (action_out_of_scope), executed=False
```

See [`examples/collective_demo.py`](examples/collective_demo.py) for collective-action quorum and bounded authority, and [`examples/legacy_huap_event.jsonl`](examples/legacy_huap_event.jsonl) for a minimal HUAP trace example.

## Minimal Python API

```python
from datetime import timedelta
from samanvaya import (
    ActionIntent, AuditLog, ConstitutionConfig, ConstitutionalGateway,
    ConstitutionalPolicy, Effect, Mandate, MandateBook,
)
from samanvaya.models import utcnow

mandates = MandateBook(root_issuers=("human:owner",))
mandates.issue(Mandate(
    mandate_id="m1", issuer="human:owner", holder="agent:analyst",
    actions=("read",), resource_scopes=("repo:reports",),
    purposes=("research",), allowed_effects=(Effect.READ,),
    expires_at=utcnow() + timedelta(hours=1), max_uses=10,
))
policy = ConstitutionalPolicy(mandates, ConstitutionConfig(("human:owner",)))
gateway = ConstitutionalGateway(policy, AuditLog("./decisions.jsonl"))
intent = ActionIntent("i1", "agent:analyst", "m1", "read",
                      "repo:reports/notes", "research", Effect.READ)
receipt = gateway.execute(intent, lambda: "simulated read")
assert receipt.executed and receipt.result == "simulated read"
```

This demonstrates policy behavior only; `human:owner` is not authenticated in this example.

## Repository map

```text
src/samanvaya/
  models.py           Typed intentions, mandates, evidence, approvals, collectives
  mandates.py         Bounded issuance, delegation, quota, scope, revocation
  constitution.py     The five-pillar decision engine
  gateway.py          Check + log + reserve + side-effect adapter boundary
  audit.py            Chain-linked JSONL verification and semantic diff
  replay.py           Side-effect-free constitutional decision replay
  compat/huap_trace.py  Read-only legacy HUAP JSONL compatibility
  cli.py              Demo, verify-audit, inspect-huap
examples/             Collective demo, sample HUAP trace
 tests/               Policy, replay, HUAP compatibility and adversarial tests
 docs/                Charter, architecture, 12-law matrix, ADRs, security, migration
```

## Fundamental separation

```mermaid
flowchart TD
    A[Agent or accountable collective] --> B[ActionIntent + evidence + mandate]
    B --> C{Samanvaya Constitutional Policy}
    C -->|ALLOW| D[Audit + reserve quota]
    D --> E[Bounded host tool adapter]
    C -->|DENY / UNKNOWN| F[No execution]
    C -->|ESCALATE| G[Human review via host identity system]
    G -->|Valid approval bound to intent| C
    E --> H[Outcome audit]
```

*The demo uses simulated review and tools. External enforcement and authenticated human identity are future work.*

## Documentation

- [CONSTITUTION.md](docs/CONSTITUTION.md) — normative kernel charter and invariants
- [VEDIC_FOUNDATIONS.md](docs/VEDIC_FOUNDATIONS.md) — why these five organizing principles
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — boundaries, objects, flow and hypergraphs
- [TWELVE_LAWS_MATRIX.md](docs/TWELVE_LAWS_MATRIX.md) — provisional map to Srinivas Gutta's 12-law series, with source-verification flags
- [HUAP_SALVAGE.md](docs/HUAP_SALVAGE.md) — what we retained conceptually and why
- [SECURITY.md](docs/SECURITY.md) — actual guarantees vs threat-model gaps
- [ROADMAP.md](docs/ROADMAP.md) — subsequent engineering milestones
- [HANDOFF_FOR_CLAUDE_CODEX.md](docs/HANDOFF_FOR_CLAUDE_CODEX.md) — task brief and acceptance gates
- [ADRs](docs/adr/README.md) — permanent architecture choices

## Origins, rights and acknowledgements

This codebase is a **clean small kernel with explicit conceptual lineage**, not a byte-for-byte fork of HUAP. The HUAP public repository supplied the tracing, replay, policy hook, pod, human gate and test/CI design patterns; the executable constitution here is newly implemented. HUAP was reviewed on 23 November 2026. Source: https://github.com/Mircus/HUAP. See [NOTICE](NOTICE) and [HUAP_SALVAGE.md](docs/HUAP_SALVAGE.md).

Conceptual dialogue: Srinivas Gutta's **Twelve Laws of Agentic AI**, especially articles 8 (accountability), 10 (non-delegable authority), and 12 (governability). The law matrix is expressly **provisional** pending an article-by-article verified audit and does not claim to reproduce his actual texts.

MIT license. Early baseline maintained as a **starting point for Claude/Codex refinement**, not as a deployed platform.

# Working correspondence to Srinivas Gutta's Twelve Laws of Agentic AI

**PROVISIONAL — do not quote this as the authoritative list of Srinivas's titles or formulations.**

The objective is to make the architecture **testably responsive** to a twelve-article constitutional discussion, not to misattribute new rules to its author. The numbered grouping below is the working pentad mapping agreed during design discussions. As of 2026-11-23, the team has not verified the full source text of all twelve articles. Only articles 8, 10 and 12 have supplied source URLs/titles. Before publishing a scholarly or compliance statement, retrieve and compare all twelve original texts and mark each correspondence verified.

| Law | Working constitutional interpretation **(not a quotation)** | Primary pillar | Kernel object/check | Coverage |
|---|---|---|---|---|
| 01 | Autonomy must begin with an explicit authorization boundary. | Adhikāra | `Mandate` | Prototype |
| 02 | Capability is insufficient without legitimate authority. | Adhikāra | Holder, issuer, actions | Prototype |
| 03 | Authority is scoped to resource, purpose and time. | Adhikāra | Scope, expiry, effect | Prototype |
| 04 | Authority must be constrained and independently checked before effects. | Adhikāra | `ConstitutionalGateway` | Partial |
| 05 | Agents owe obligations beyond completing the requested task. | Dharma | Purpose, harm flags | Partial |
| 06 | High-impact effects need safeguards or human review. | Dharma | Human escalation | Partial |
| 07 | Agents should be bound to evidence and uncertainty. | Ṛta | Evidence / `UNKNOWN` | Partial |
| 08 | **Autonomy without accountability** is unacceptable. | Samanvaya | Responsible principal, trace | Partial |
| 09 | Decisions should remain revisable/correctable. | Punarnavīkaraṇa | Expiry, revocation | Partial |
| 10 | **An agent cannot delegate authority it does not possess.** | Samanvaya + Adhikāra | Subset delegation | Prototype |
| 11 | Collective action carries collective duties, not vanishing responsibility. | Dharma | Group mandate + named principal | Partial |
| 12 | **Autonomous systems must remain governable.** | Punarnavīkaraṇa | Revocation, review, audit, human control | Partial |

Laws 01–07, 09, 11 above are **our interim engineering hypotheses**, not verified wording or faithful summaries of the actual corresponding original articles. Even 08/10/12 here are short themes inferred from linked article titles, not complete textual analyses.

## Confirmed supplied article URLs

- [Article 8 — Autonomy Without Accountability](https://www.linkedin.com/pulse/article-8-autonomy-without-accountability-eighth-law-srinivas-gutta-qf6xc/)
- [Article 10 — An Agent Cannot Delegate Authority It Does Not Possess](https://www.linkedin.com/pulse/article-10-agent-cannot-delegate-authority-does-possess-gutta-ixcac/)
- [Article 12 — Autonomous Systems Must Remain Governable](https://www.linkedin.com/pulse/article-12-autonomous-systems-must-remain-governable-srinivas-gutta-2qgzc/)

## Verification checklist for research handoff

1. Collect all 12 source URLs and article publication dates. Preserve quoted law statements accurately (with permission where needed).
2. Record exact law titles and mechanisms. Distinguish the author's requirements from Samanvaya's extrapolation.
3. Map each law to one or more enforcement points; justify every mapping with source evidence.
4. For each law, create at least one normal and one adversarial conformance test.
5. Publish a separate *interpretive mapping* with version number, not a claim of official certification.

## Multi-axis design point

The five pillars are mutually checking constraints. An admissible action can be coherent but unauthorized, authorized but contrary to purpose, collectively approved but out of scope, or currently valid but later revoked. Nothing in the architecture grants an agent sovereignty to repair those failures by granting itself powers.

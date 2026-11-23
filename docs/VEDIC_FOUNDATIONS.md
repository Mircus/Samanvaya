# The fivefold constitutional frame

**Normative design note, 2026-11-23.** These terms are used as **conceptual inspiration**, not as a claim that ancient texts contain a software architecture. We do not translate metaphysics directly into a Boolean program; we choose precise engineering commitments informed by older ideas about order, duty, authority, harmonious coordination, and renewal.

## Lokasaṃgraha: the enclosing purpose

*Lokasaṃgraha* (लोकसंग्रह) broadly evokes sustaining social/world order and collective welfare. For Samanvaya, it names a guiding objective: **agents are not sovereign units; they operate as accountable parts of a larger human-governed whole**. No single policy rule can prove this objective is achieved. We therefore require multiple independently tested constraints.

## Ṛta — order before assertion

Ṛta (ऋत) evokes order and truth. Here it means a proposed consequential action must have *traceable grounds*: provenance, status, freshness (future work), and explicit uncertainty. A model's persuasive prose is never evidence of authority. `UNKNOWN` is a legitimate answer, not an invitation to guess. v0.1 checks caller-declared evidence status, not genuine verification.

## Dharma — duties and rightful purpose

Dharma (धर्म) here means purpose-bound obligation: even if an agent has the technical means and a limited mandate, it cannot arbitrarily repurpose that mandate. Duties, foreseeable harms, reversibility and externalities belong to decision-making, not merely to post-hoc evaluation. Current harm flags fail closed pending repair; more nuanced risk and remediation policy is future work.

## Adhikāra — qualified authority to act

Adhikāra (अधिकार) concerns entitlement, competence or scope of authority. In this system **capability is not authorization**. An agent may know how to call a tool yet have no valid mandate to do so. Mandates specify issuer, holder, action, resource, purpose, permitted effect, budget and validity. A delegated mandate must be no broader than its parent. Mere claims of identity must eventually be replaced by authenticated principals and attestations.

## Samanvaya — coordinated collective agency

Samanvaya (समन्वय) suggests coordination or harmonization. The central computational object is a **hyperedge**, a designated group that can act as one bounded collective without collapsing member identities. Collective authority must be separately issued; it is **never** the union of all members' individual powers. It requires quorum and a named accountable principal. Endorsement authentication is not implemented in v0.1.

## Punarnavīkaraṇa — continuing repairability

Punarnavīkaraṇa (पुनर्नवीकरण) can express renewal or making new again. The relevant engineering principle is that authorization must remain revocable, reviewable, time-limited and subject to correction. v0.1 includes revocation, expiry and escalation; restoration workflows, reversible execution and governing-policy version migration are planned.

## The five-pillar logical shape

An action is admissible only if all hard requirements pass. Notation:

`Admissible(a) = Ṛta(a) ∧ Dharma(a) ∧ Adhikāra(a) ∧ Samanvaya(a) ∧ Punarnavīkaraṇa(a)`

This is a useful *engineering shorthand*, not a formal axiomatization of Sanskrit philosophical systems. The evaluator returns one of four statuses: `ALLOW`, `DENY`, `UNKNOWN`, `ESCALATE`. Unknown evidence or required human review must not be collapsed into an optimistic `True`.

## Why this differs from guardrails

A post-hoc check may tell you that an autonomous action was problematic. A constitutional kernel instead asks **before the effect**: Is it epistemically grounded? Is the purpose legitimate? Who granted authority? What collective is acting? Can the mandate be revoked or the action corrected? The last question needs real systems integration; v0.1 demonstrates only the beginning.

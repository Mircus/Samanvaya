"""Five-pillar executable constitution. Pure policy: no model calls, no I/O.

Ṛta: evidence; Dharma: permitted purpose & declared harm; Adhikāra: bounded mandate;
Samanvaya: collective quorum/accountability; Punarnavīkaraṇa: expiry/revocation/review.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .mandates import MandateBook, in_scope
from .models import (ActionIntent, Collective, Decision, Effect, EvidenceStatus,
                     HumanApproval, Verdict, utcnow)


@dataclass(frozen=True)
class ConstitutionConfig:
    human_reviewers: tuple[str, ...]
    review_effects: tuple[Effect, ...] = (Effect.EXTERNAL, Effect.IRREVERSIBLE)
    evidence_required_effects: tuple[Effect, ...] = (
        Effect.WRITE, Effect.EXTERNAL, Effect.IRREVERSIBLE
    )


class ConstitutionalPolicy:
    def __init__(self, mandates: MandateBook, config: ConstitutionConfig,
                 collectives: tuple[Collective, ...] = ()):
        self.mandates = mandates
        self.config = config
        self.collectives = {c.collective_id: c for c in collectives}
        for c in collectives:
            if not c.collective_id or not c.accountable_principal or not c.members:
                raise ValueError("Collective requires identity, members and responsible principal")
            if len(set(c.members)) != len(c.members) or c.quorum < 1 or c.quorum > len(c.members):
                raise ValueError("Invalid collective membership or quorum")

    def evaluate(self, intent: ActionIntent, approval: HumanApproval | None = None,
                 at: datetime | None = None) -> Decision:
        at = at or utcnow()

        def decision(verdict: Verdict, *reasons: str) -> Decision:
            return Decision(verdict, tuple(reasons), intent.intent_id, intent.mandate_id, at)

        if not all((intent.intent_id, intent.actor, intent.action, intent.resource, intent.purpose)):
            return decision(Verdict.DENY, "malformed_intent")
        try:
            in_scope(intent.resource, intent.resource)
        except ValueError:
            return decision(Verdict.DENY, "invalid_resource")

        # ADHIKĀRA — no mandate, no action; bounded holder, action, resource and purpose.
        mandate = self.mandates.get(intent.mandate_id)
        if not mandate:
            return decision(Verdict.DENY, "mandate_absent")
        if not self.mandates.active(mandate.mandate_id, at):
            return decision(Verdict.DENY, "mandate_inactive")
        if not self.mandates.quota_available(mandate.mandate_id):
            return decision(Verdict.DENY, "mandate_quota_exhausted")
        if intent.action not in mandate.actions:
            return decision(Verdict.DENY, "action_out_of_scope")
        if intent.effect not in mandate.allowed_effects:
            return decision(Verdict.DENY, "effect_out_of_scope")
        if not any(in_scope(intent.resource, scope) for scope in mandate.resource_scopes):
            return decision(Verdict.DENY, "resource_out_of_scope")

        # DHARMA — an authorized verb is not an authorized purpose.
        if intent.purpose not in mandate.purposes:
            return decision(Verdict.DENY, "purpose_out_of_scope")
        if intent.harm_flags:
            return decision(Verdict.DENY, "declared_harm_requires_repair")

        # SAMANVAYA — a hyperedge is a distinct bounded actor, not a magic union
        # of all member rights. Claimed endorsements are prototype assertions only.
        if intent.collective_id:
            collective = self.collectives.get(intent.collective_id)
            if not collective:
                return decision(Verdict.DENY, "collective_absent")
            if mandate.holder != collective.collective_id:
                return decision(Verdict.DENY, "collective_mandate_mismatch")
            if not mandate.accountable_principal or (
                    mandate.accountable_principal != collective.accountable_principal):
                return decision(Verdict.DENY, "collective_accountability_missing")
            if intent.actor not in collective.members:
                return decision(Verdict.DENY, "actor_not_in_collective")
            if len(set(intent.endorsements)) != len(intent.endorsements):
                return decision(Verdict.DENY, "duplicate_endorsements")
            if not set(intent.endorsements) <= set(collective.members):
                return decision(Verdict.DENY, "unknown_endorser")
            if len(intent.endorsements) < collective.quorum:
                return decision(Verdict.DENY, "collective_quorum_missing")
        else:
            if intent.endorsements:
                return decision(Verdict.DENY, "endorsements_without_collective")
            if mandate.holder != intent.actor:
                return decision(Verdict.DENY, "actor_not_mandate_holder")

        # ṚTA — no blind assertions for consequential operations.
        if any(e.status == EvidenceStatus.CONFLICTING for e in intent.evidence):
            return decision(Verdict.DENY, "conflicting_evidence")
        if intent.effect in self.config.evidence_required_effects:
            if not intent.evidence or not any(e.status == EvidenceStatus.VERIFIED
                                              and e.source and e.digest for e in intent.evidence):
                return decision(Verdict.UNKNOWN, "verified_evidence_unavailable")

        # PUNARNAVĪKARAṆA — approvals have time and intent scope.
        if intent.effect in self.config.review_effects:
            if approval is None:
                return decision(Verdict.ESCALATE, "human_review_required")
            if (approval.intent_id != intent.intent_id
                    or approval.approver not in self.config.human_reviewers
                    or approval.expires_at.tzinfo is None
                    or approval.expires_at <= at):
                return decision(Verdict.DENY, "invalid_human_approval")
        return decision(Verdict.ALLOW, "all_applicable_checks_passed")

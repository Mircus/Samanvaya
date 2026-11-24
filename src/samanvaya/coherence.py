"""Constitutional coherence over entire plans (no execution, no model calls).

Unlike an action-level permission gate, this checks cross-action obligations,
conflicting factual witnesses, and dependency/order constraints. v0.2 witnesses
and principals are caller assertions: see SECURITY.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from .constitution import ConstitutionalPolicy
from .models import ActionIntent, EvidenceStatus, HumanApproval, Verdict, utcnow
from .mandates import normalized_time


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    intent: ActionIntent
    essential: bool = True  # Essential steps cannot be dropped by repair proposals


@dataclass(frozen=True)
class FactWitness:
    proposition: str
    value: str
    source: str
    digest: str
    status: EvidenceStatus
    valid_until: datetime | None = None


@dataclass(frozen=True)
class FactObligation:
    """Before acting, a fact must have a unique supported permitted value.

    trigger_actions are fixed by a trusted plan author, not the model.
    An empty trigger_actions tuple applies to all actions in the step.
    """
    rule_id: str
    step_id: str
    proposition: str
    accepted_values: tuple[str, ...]
    trigger_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class BeforeObligation:
    rule_id: str
    prerequisite_step: str
    dependent_step: str


@dataclass(frozen=True)
class ExclusionObligation:
    rule_id: str
    steps: tuple[str, ...]
    maximum_present: int = 1


Obligation = Union[FactObligation, BeforeObligation, ExclusionObligation]


@dataclass(frozen=True)
class ConstitutionalPlan:
    plan_id: str
    steps: tuple[PlanStep, ...]
    obligations: tuple[Obligation, ...]
    facts: tuple[FactWitness, ...] = ()
    declared_step_ids: tuple[str, ...] = ()  # fixed original universe, surviving repairs


@dataclass(frozen=True)
class Finding:
    rule_id: str
    status: Verdict
    code: str
    explanation: str


@dataclass(frozen=True)
class PlanAssessment:
    plan_id: str
    verdict: Verdict
    findings: tuple[Finding, ...]
    evaluated_steps: int
    evaluated_at: datetime

    @property
    def admissible(self) -> bool:
        return self.verdict is Verdict.ALLOW


_PRIORITY = {Verdict.ALLOW: 0, Verdict.ESCALATE: 1, Verdict.UNKNOWN: 2, Verdict.DENY: 3}


class CoherenceAnalyzer:
    """Pure planning-time evaluator, never authorizes or executes a real effect."""

    def __init__(self, policy: ConstitutionalPolicy):
        self.policy = policy

    def assess(self, plan: ConstitutionalPlan,
               approvals: dict[str, HumanApproval] | None = None,
               at: datetime | None = None) -> PlanAssessment:
        at = normalized_time(at or utcnow())
        approvals = approvals or {}
        if not plan.plan_id:
            raise ValueError("Plan identifier required")
        ids = [s.step_id for s in plan.steps]
        intent_ids = [s.intent.intent_id for s in plan.steps]
        if any(not k for k in ids) or len(set(ids)) != len(ids):
            raise ValueError("Duplicate or missing step identifier")
        if len(set(intent_ids)) != len(intent_ids):
            raise ValueError("Duplicate intent identifier")
        rule_ids = [r.rule_id for r in plan.obligations]
        if any(not rid for rid in rule_ids) or len(set(rule_ids)) != len(rule_ids):
            raise ValueError("Obligation IDs must be distinct and nonempty")
        steps = {s.step_id: s for s in plan.steps}
        declared_ids = set(ids)
        universe = set(plan.declared_step_ids or ids)
        if len(universe) != len(plan.declared_step_ids or ids) or not declared_ids <= universe:
            raise ValueError("Invalid original step universe")
        for rule in plan.obligations:
            refs = ((rule.step_id,) if isinstance(rule, FactObligation) else
                    (rule.prerequisite_step, rule.dependent_step) if isinstance(rule, BeforeObligation)
                    else rule.steps if isinstance(rule, ExclusionObligation) else ())
            if any(ref not in universe for ref in refs):
                raise ValueError("Obligation references undeclared step")
        findings: list[Finding] = []

        for step in plan.steps:
            decision = self.policy.evaluate(step.intent,
                                            approval=approvals.get(step.intent.intent_id), at=at)
            if decision.verdict is not Verdict.ALLOW:
                findings.append(Finding(f"action:{step.step_id}", decision.verdict,
                                        decision.reasons[0], ", ".join(decision.reasons)))

        for rule in plan.obligations:
            if isinstance(rule, FactObligation):
                if rule.step_id not in declared_ids:
                    # A removed optional step does not trigger its fact obligation.
                    continue
                if not rule.accepted_values or not rule.proposition:
                    raise ValueError("Fact obligation missing proposition or accepted values")
                if rule.trigger_actions and steps[rule.step_id].intent.action not in rule.trigger_actions:
                    continue
                witnesses = [w for w in plan.facts if w.proposition == rule.proposition]
                if any(w.status is EvidenceStatus.CONFLICTING for w in witnesses):
                    findings.append(Finding(rule.rule_id, Verdict.DENY, "explicit_fact_conflict",
                                            f"Conflicting witness for {rule.proposition}"))
                    continue
                verified = [w for w in witnesses if w.status is EvidenceStatus.VERIFIED
                            and w.source and w.digest and w.value and
                            (w.valid_until is None or
                             normalized_time(w.valid_until) > at)]
                values = {w.value for w in verified}
                if len(values) > 1:
                    findings.append(Finding(rule.rule_id, Verdict.DENY, "contradictory_verified_facts",
                                            f"Incompatible values for {rule.proposition}"))
                elif not values:
                    findings.append(Finding(rule.rule_id, Verdict.UNKNOWN, "fact_not_established",
                                            f"Fresh evidence required for {rule.proposition}"))
                elif next(iter(values)) not in rule.accepted_values:
                    findings.append(Finding(rule.rule_id, Verdict.DENY, "fact_violates_obligation",
                                            f"Established {rule.proposition} outside allowed values"))
            elif isinstance(rule, BeforeObligation):
                if rule.dependent_step in declared_ids:
                    if rule.prerequisite_step not in declared_ids:
                        findings.append(Finding(rule.rule_id, Verdict.DENY, "missing_prerequisite",
                                                f"{rule.prerequisite_step} absent"))
                    elif ids.index(rule.prerequisite_step) >= ids.index(rule.dependent_step):
                        findings.append(Finding(rule.rule_id, Verdict.DENY, "invalid_sequence",
                                                f"{rule.prerequisite_step} must precede {rule.dependent_step}"))
            elif isinstance(rule, ExclusionObligation):
                if len(set(rule.steps)) != len(rule.steps) or rule.maximum_present < 0:
                    raise ValueError("Invalid exclusion rule")
                if sum(k in declared_ids for k in rule.steps) > rule.maximum_present:
                    findings.append(Finding(rule.rule_id, Verdict.DENY, "incompatible_actions",
                                            f"At most {rule.maximum_present} among {rule.steps}"))
            else:
                raise TypeError("Unknown obligation type")

        verdict = max((f.status for f in findings), key=lambda s: _PRIORITY[s],
                      default=Verdict.ALLOW)
        return PlanAssessment(plan.plan_id, verdict, tuple(findings), len(plan.steps), at)

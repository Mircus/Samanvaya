"""Bounded, certifiable minimal repair over *operator-supplied* alternatives.

Never fabricates evidence, endorsement, mandate or permission. Does not execute
an alternative. Minimality is proved only within an explicit finite edit catalog.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from datetime import datetime
from heapq import heappop, heappush

from .coherence import CoherenceAnalyzer, ConstitutionalPlan, PlanAssessment, PlanStep
from .constitution import ConstitutionalPolicy
from .models import utcnow
from .models import ActionIntent, HumanApproval, Verdict


@dataclass(frozen=True)
class RepairEdit:
    edit_id: str
    step_id: str
    replacement: ActionIntent | None  # None explicitly removes a non-essential step
    cost: int
    rationale: str


@dataclass(frozen=True)
class RepairCandidate:
    edits: tuple[RepairEdit, ...]
    cost: int
    assessment: PlanAssessment
    plan: ConstitutionalPlan


@dataclass(frozen=True)
class RepairSearchResult:
    original: PlanAssessment
    feasible: tuple[RepairCandidate, ...]
    pending: tuple[RepairCandidate, ...]
    explored_variants: int
    catalog_variants: int
    complete: bool
    minimal_proven_within_catalog: bool
    catalog_sha256: str
    evaluated_at: datetime


class MinimalRepairExplorer:
    def __init__(self, analyzer: CoherenceAnalyzer):
        self.analyzer = analyzer

    def explore(self, plan: ConstitutionalPlan, catalog: tuple[RepairEdit, ...],
                approvals: dict[str, HumanApproval] | None = None,
                at: datetime | None = None, max_variants: int = 512,
                max_results: int = 5) -> RepairSearchResult:
        if max_variants <= 0 or max_results <= 0:
            raise ValueError("Positive limits required")
        # Freeze analysis time and mandate state for a meaningful scoped proof.
        # A live gateway *never* uses this snapshot for actual authorization.
        at = at or utcnow()
        policy = self.analyzer.policy
        snapshot_policy = ConstitutionalPolicy(policy.mandates.planning_snapshot(),
                                               policy.config,
                                               tuple(policy.collectives.values()))
        frozen_analyzer = CoherenceAnalyzer(snapshot_policy)
        # Baseline always checked even when search is truncated.
        plan = replace(plan, declared_step_ids=plan.declared_step_ids or
                       tuple(s.step_id for s in plan.steps))
        original = frozen_analyzer.assess(plan, approvals=approvals, at=at)
        originals = {s.step_id: s for s in plan.steps}
        by_step: dict[str, list[RepairEdit]] = {key: [] for key in originals}
        seen_ids: set[str] = set()
        for edit in catalog:
            if not edit.edit_id or edit.edit_id in seen_ids:
                raise ValueError("Edit IDs must be unique and nonempty")
            seen_ids.add(edit.edit_id)
            if edit.step_id not in originals or edit.cost <= 0 or not edit.rationale:
                raise ValueError("Edit must name an existing step, positive cost and rationale")
            step = originals[edit.step_id]
            if edit.replacement is None and step.essential:
                raise ValueError("Cannot drop essential step")
            if edit.replacement is not None and edit.replacement.intent_id == step.intent.intent_id:
                raise ValueError("Changed action requires a fresh intent ID")
            by_step[edit.step_id].append(edit)
        # Uniform-cost search in the finite product space.  Never materialize the
        # product: its cardinality can be exponential in the number of steps.
        slot_ids = sorted(by_step)
        choices = [tuple([None] + sorted(by_step[slot], key=lambda e: (e.cost, e.edit_id)))
                   for slot in slot_ids]
        variant_count = 1
        for c in choices:
            variant_count *= len(c)

        def decode(indices: tuple[int, ...]):
            return tuple(choices[i][idx] for i, idx in enumerate(indices))

        def rank(indices: tuple[int, ...]):
            selected = tuple(e for e in decode(indices) if e is not None)
            return (sum(e.cost for e in selected), tuple(e.edit_id for e in selected))

        start = tuple(0 for _ in choices)
        heap: list[tuple[int, tuple[str, ...], tuple[int, ...]]] = []
        heappush(heap, (*rank(start), start))
        visited = {start}
        feasible: list[RepairCandidate] = []
        pending: list[RepairCandidate] = []
        explored = 0
        while heap and explored < max_variants:
            _, _, indices = heappop(heap)
            explored += 1
            for dimension in range(len(choices)):
                if indices[dimension] + 1 < len(choices[dimension]):
                    nxt = tuple(v + (i == dimension) for i, v in enumerate(indices))
                    if nxt not in visited:
                        visited.add(nxt)
                        heappush(heap, (*rank(nxt), nxt))
            selected = tuple(e for e in decode(indices) if e is not None)
            edits_by_step = {e.step_id: e for e in selected}
            new_steps = []
            for s in plan.steps:
                e = edits_by_step.get(s.step_id)
                if e is None:
                    new_steps.append(s)
                elif e.replacement is not None:
                    new_steps.append(replace(s, intent=e.replacement))
            candidate = replace(plan, steps=tuple(new_steps))
            assessment = frozen_analyzer.assess(candidate, approvals=approvals, at=at)
            result = RepairCandidate(selected, sum(e.cost for e in selected), assessment, candidate)
            if assessment.verdict is Verdict.ALLOW:
                feasible.append(result)
            elif selected and assessment.verdict in (Verdict.UNKNOWN, Verdict.ESCALATE):
                pending.append(result)
        complete = explored == variant_count
        catalog_bytes = json.dumps([asdict(e) for e in catalog], sort_keys=True,
                                   ensure_ascii=False, default=str,
                                   separators=(",", ":")).encode("utf-8")
        catalog_sha = sha256(catalog_bytes).hexdigest()
        return RepairSearchResult(original, tuple(feasible[:max_results]),
                                  tuple(pending[:max_results]), explored,
                                  variant_count, complete, complete and bool(feasible), catalog_sha, at)

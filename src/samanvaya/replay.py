"""Safe, no-side-effect constitutional replay of a verified decision log.

Provide a FRESH policy/mandate ledger configured with the same original mandates.
This rechecks decisions, not the external effects of tools and not HUAP workflow replay.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .audit import verified_events
from .constitution import ConstitutionalPolicy
from .models import ActionIntent, Effect, Evidence, EvidenceStatus, HumanApproval, Verdict


def _intent(raw: dict) -> ActionIntent:
    return ActionIntent(
        intent_id=raw['intent_id'], actor=raw['actor'], mandate_id=raw['mandate_id'],
        action=raw['action'], resource=raw['resource'], purpose=raw['purpose'],
        effect=Effect(raw['effect']),
        evidence=tuple(Evidence(source=e['source'], digest=e['digest'],
                                status=EvidenceStatus(e['status']),
                                description=e.get('description', ''))
                       for e in raw.get('evidence', ())),
        collective_id=raw.get('collective_id'),
        endorsements=tuple(raw.get('endorsements', ())),
        harm_flags=tuple(raw.get('harm_flags', ())),
    )


def _approval(raw: dict | None) -> HumanApproval | None:
    if raw is None:
        return None
    return HumanApproval(intent_id=raw['intent_id'], approver=raw['approver'],
                         expires_at=datetime.fromisoformat(raw['expires_at']))


def replay_constitution(path: str | Path, policy: ConstitutionalPolicy) -> dict:
    """Return divergence report; never call a tool. Does not change source audit."""
    deviations: list[dict] = []
    decisions: dict[str, Verdict] = {}
    seen_decisions = 0
    for event in verified_events(path):
        if event['kind'] == 'constitutional_decision':
            logged = event['data']['decision']
            action = _intent(event['data']['intent'])
            computed = policy.evaluate(
                action, _approval(event['data'].get('approval')),
                at=datetime.fromisoformat(logged['checked_at']))
            expected_verdict = Verdict(logged['verdict'])
            decisions[action.intent_id] = computed.verdict
            seen_decisions += 1
            if (computed.verdict != expected_verdict
                    or list(computed.reasons) != logged['reasons']):
                deviations.append({
                    'seq': event['seq'], 'intent_id': action.intent_id,
                    'expected': logged['verdict'], 'actual': computed.verdict.value,
                    'expected_reasons': logged['reasons'],
                    'actual_reasons': list(computed.reasons),
                })
        elif event['kind'] == 'execution_started':
            intent_id = event['data']['intent_id']
            if decisions.get(intent_id) != Verdict.ALLOW:
                deviations.append({'seq': event['seq'], 'intent_id': intent_id,
                                   'error': 'execution without replayed ALLOW'})
            else:
                try:
                    policy.mandates.reserve(event['data']['mandate_id'],
                                            at=datetime.fromisoformat(event['ts']))
                except PermissionError as exc:
                    deviations.append({'seq': event['seq'], 'intent_id': intent_id,
                                       'error': f'replay reservation denied: {exc}'})
    return {'matched': not deviations, 'decisions_checked': seen_decisions,
            'deviations': deviations, 'side_effects_executed': False}

"""Run from an installed package: python examples/collective_demo.py

Simulated collective endorsements, not cryptographic votes.
"""
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from samanvaya import (ActionIntent, AuditLog, Collective, ConstitutionConfig,
                       ConstitutionalGateway, ConstitutionalPolicy, Effect,
                       Mandate, MandateBook)
from samanvaya.models import utcnow


def main():
    team = Collective('collective:research', ('agent:alice', 'agent:bob', 'agent:critic'),
                      quorum=2, accountable_principal='human:director')
    book = MandateBook(('human:director',))
    book.issue(Mandate(
        mandate_id='mandate:research-team', issuer='human:director', holder=team.collective_id,
        actions=('read',), resource_scopes=('repo:research',), purposes=('scientific-analysis',),
        allowed_effects=(Effect.READ,), expires_at=utcnow() + timedelta(hours=1),
        accountable_principal='human:director', max_uses=2,
    ))
    policy = ConstitutionalPolicy(book, ConstitutionConfig(('human:director',)), (team,))
    with TemporaryDirectory() as temp:
        gateway = ConstitutionalGateway(policy, AuditLog(Path(temp) / 'collective.jsonl'))
        base = dict(
            intent_id='proposal:001', actor='agent:alice',
            mandate_id='mandate:research-team', action='read',
            resource='repo:research/paper', purpose='scientific-analysis',
            effect=Effect.READ, collective_id='collective:research',
        )
        missing_quorum = gateway.execute(ActionIntent(**base, endorsements=('agent:alice',)),
                                         lambda: 'this must not run')
        print('ONE ENDORSEMENT:', missing_quorum.decision.verdict.value,
              missing_quorum.decision.reasons)
        proper_quorum = gateway.execute(ActionIntent(**base, endorsements=('agent:alice', 'agent:bob')),
                                        lambda: 'simulated document read')
        print('TWO ENDORSEMENTS:', proper_quorum.decision.verdict.value,
              proper_quorum.result)
        # Still no right to publish, despite collective quorum.
        forbidden = gateway.execute(ActionIntent(**{**base, 'action': 'publish',
                                                  'endorsements': ('agent:alice', 'agent:bob')}),
                                    lambda: 'this must not run')
        print('PUBLISH REQUEST:', forbidden.decision.verdict.value,
              forbidden.decision.reasons)


if __name__ == '__main__':
    main()

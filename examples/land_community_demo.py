"""No-network Samanvaya v0.2 demo: community land option, factual gap, repair.

No real purchase, survey, payment, or external service is performed.
"""
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from samanvaya import (
    ActionIntent, AuditLog, ConstitutionConfig, ConstitutionalGateway,
    ConstitutionalPolicy, Effect, Evidence, EvidenceStatus, Mandate, MandateBook,
)
from samanvaya.coherence import (
    CoherenceAnalyzer, ConstitutionalPlan, FactObligation, PlanStep,
)
from samanvaya.repair import MinimalRepairExplorer, RepairEdit
from samanvaya.adapters import BoundTool, ConstitutionalToolBroker
from samanvaya.adapters.broker import canonical_args_digest
from samanvaya.models import utcnow


def main():
    with TemporaryDirectory() as directory:
        mandates = MandateBook(('human:trustee',))
        mandates.issue(Mandate(
            'm-land', 'human:trustee', 'agent:scout', ('option', 'survey'),
            ('land:tuscany',), ('community-feasibility',), (Effect.READ, Effect.WRITE),
            utcnow() + timedelta(hours=2), max_uses=4))
        policy = ConstitutionalPolicy(mandates, ConstitutionConfig(('human:trustee',)))
        analyzer = CoherenceAnalyzer(policy)
        audit = AuditLog(Path(directory) / 'decisions.jsonl')
        gateway = ConstitutionalGateway(policy, audit)
        evidence = (Evidence('report:land-registry', 'sha256:registry', EvidenceStatus.VERIFIED),)
        option = ActionIntent('intent:land-option', 'agent:scout', 'm-land', 'option',
                              'land:tuscany/site-a', 'community-feasibility',
                              Effect.WRITE, evidence)
        survey = ActionIntent('intent:survey', 'agent:scout', 'm-land', 'survey',
                              'land:tuscany/site-a', 'community-feasibility', Effect.READ)
        plan = ConstitutionalPlan('plan:community', (PlanStep('decision', option),),
                                  (FactObligation('water', 'decision', 'water_available',
                                                  ('yes',), trigger_actions=('option',)),))
        print('Individually authorized option:', policy.evaluate(option).verdict.value)
        print('Constitutional plan:', analyzer.assess(plan).verdict.value)

        arguments = {'site': 'site-a'}
        original_broker = ConstitutionalToolBroker(gateway, (
            BoundTool('option', lambda _: option, 'decision', canonical_args_digest(arguments)),
        ), plan, analyzer)
        actual_effects = []
        blocked = original_broker.invoke('option', arguments,
                                         lambda: actual_effects.append('NOT EXPECTED'))
        print('Before repair, tool:', blocked.code, '| effects:', len(actual_effects))

        edits = (RepairEdit('water-survey', 'decision', survey, 2,
                            'Commission survey rather than taking a land option'),)
        report = MinimalRepairExplorer(analyzer).explore(plan, edits)
        print('Admissible alternatives:', [(r.edits[0].edit_id, r.cost) for r in report.feasible])
        print('Minimal within catalog:', report.minimal_proven_within_catalog)

        # An operator must choose the alternative and bind new tools themselves.
        chosen = report.feasible[0].plan
        survey_broker = ConstitutionalToolBroker(gateway, (
            BoundTool('survey', lambda _: survey, 'decision', canonical_args_digest(arguments)),
        ), chosen, analyzer)
        allowed = survey_broker.invoke('survey', arguments,
                                        lambda: actual_effects.append('SIMULATED SURVEY') or 'ok')
        print('After operator selects repair, tool:', allowed.code,
              '| effects:', actual_effects)
        print('Real external effects: none (simulated demo)')


if __name__ == '__main__':
    main()

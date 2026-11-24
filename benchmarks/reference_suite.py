"""Reproducible Samanvaya-only reference suite; NOT a competitor benchmark.

Run: python benchmarks/reference_suite.py
The comparison with an action-only baseline illustrates added behavior, but it
cannot establish superiority against third-party governance toolkits.
"""
from datetime import timedelta
import json
from samanvaya import (ActionIntent, ConstitutionConfig, ConstitutionalPolicy,
                       Effect, Evidence, EvidenceStatus, Mandate, MandateBook)
from samanvaya.coherence import (CoherenceAnalyzer, ConstitutionalPlan,
                                 FactObligation, FactWitness, PlanStep)
from samanvaya.models import utcnow


def main():
    book = MandateBook(('human:trustee',))
    book.issue(Mandate('m', 'human:trustee', 'agent:analyst', ('option',),
                       ('land:tuscany',), ('community',), (Effect.WRITE,),
                       utcnow()+timedelta(days=1), max_uses=10))
    policy = ConstitutionalPolicy(book, ConstitutionConfig(('human:trustee',)))
    analyzer = CoherenceAnalyzer(policy)
    intent = ActionIntent('i', 'agent:analyst', 'm', 'option', 'land:tuscany/site-1',
                          'community', Effect.WRITE,
                          (Evidence('land-registry','sha:test',EvidenceStatus.VERIFIED),))
    obligation = (FactObligation('water-required','site','water',('yes',)),)
    scenarios = {
        'missing_fact': (),
        'false_fact': (FactWitness('water','no','surveyor','sha:no',EvidenceStatus.VERIFIED),),
        'fresh_true_fact': (FactWitness('water','yes','surveyor','sha:yes',EvidenceStatus.VERIFIED),),
        'contradiction': (
            FactWitness('water','yes','surveyor-a','sha:yes',EvidenceStatus.VERIFIED),
            FactWitness('water','no','surveyor-b','sha:no',EvidenceStatus.VERIFIED)),
        'expired_fact': (FactWitness('water','yes','surveyor','sha:old',
                                    EvidenceStatus.VERIFIED,utcnow()-timedelta(days=1)),),
    }
    expected = {'missing_fact':'UNKNOWN','false_fact':'DENY','fresh_true_fact':'ALLOW',
                'contradiction':'DENY','expired_fact':'UNKNOWN'}
    rows = []
    for name, facts in scenarios.items():
        plan = ConstitutionalPlan(name,(PlanStep('site',intent),),obligation,facts)
        assessed = analyzer.assess(plan)
        row = {'scenario':name,'action_only':policy.evaluate(intent).verdict.value,
               'whole_plan':assessed.verdict.value,
               'findings':[f.code for f in assessed.findings],
               'expected':expected[name], 'passed':assessed.verdict.value == expected[name]}
        rows.append(row)
    print(json.dumps({'description':'internal action-only baseline vs Samanvaya plan coherence',
                      'note':'No comparison with AGT/OPA/AGP or other products has been performed',
                      'cases':rows, 'all_pass':all(r['passed'] for r in rows)},indent=2))
    if not all(r['passed'] for r in rows):
        raise SystemExit(1)

if __name__ == '__main__':
    main()

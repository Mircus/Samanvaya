"""Adversarial and finite-search properties for constitutional repair."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from itertools import product
import unittest

from samanvaya import (ActionIntent, ConstitutionConfig, ConstitutionalPolicy,
                       Effect, Mandate, MandateBook, Verdict)
from samanvaya.coherence import (CoherenceAnalyzer, ConstitutionalPlan,
                                 ExclusionObligation, PlanStep)
from samanvaya.models import utcnow
from samanvaya.repair import MinimalRepairExplorer, RepairEdit
from samanvaya.adapters.broker import canonical_args_digest


class RepairPropertyTests(unittest.TestCase):
    def setUp(self):
        self.book = MandateBook(('human:owner',))
        self.book.issue(Mandate('m','human:owner','agent:a',('read','delete'),('repo:site',),
                                ('research',),(Effect.READ,),
                                utcnow()+timedelta(days=3),max_uses=100))
        self.analyzer = CoherenceAnalyzer(ConstitutionalPolicy(
            self.book, ConstitutionConfig(('human:owner',))))
        self.explorer = MinimalRepairExplorer(self.analyzer)

    def intent(self, uid, action='read'):
        return ActionIntent(uid,'agent:a','m',action,'repo:site/x','research',Effect.READ)

    def test_cost_ordering_agrees_with_full_bruteforce_for_two_slots(self):
        plan = ConstitutionalPlan('two',
            (PlanStep('a',self.intent('a'),essential=False),
             PlanStep('b',self.intent('b'),essential=False)),
            (ExclusionObligation('must-pick-at-most-one',('a','b'),1),))
        options=(RepairEdit('drop-a','a',None,7,'Remove a'),
                 RepairEdit('drop-b','b',None,2,'Remove b'),
                 RepairEdit('delete-a','a',self.intent('a2','delete'),1,'Invalid action'))
        report=self.explorer.explore(plan,options)
        self.assertTrue(report.complete)
        self.assertTrue(report.minimal_proven_within_catalog)
        self.assertEqual(report.feasible[0].cost,2)
        self.assertEqual(report.feasible[0].edits[0].edit_id,'drop-b')
        self.assertEqual(report.explored_variants,6)
        self.assertEqual(len(report.catalog_sha256),64)
        self.assertEqual(report.original.evaluated_at,report.evaluated_at)
        self.assertTrue(all(c.assessment.evaluated_at==report.evaluated_at
                            for c in report.feasible))

    def test_large_product_search_remains_bounded(self):
        steps=tuple(PlanStep(str(i), self.intent('i'+str(i)), essential=False)
                    for i in range(12))
        edits=tuple(RepairEdit('drop'+str(i),str(i),None,1,'Drop optional')
                    for i in range(12))
        report=self.explorer.explore(ConstitutionalPlan('large', steps,()), edits,
                                     max_variants=4,max_results=4)
        self.assertEqual(report.catalog_variants,4096)
        self.assertEqual(report.explored_variants,4)
        self.assertFalse(report.minimal_proven_within_catalog)

    def test_snapshot_is_independent_of_later_revocation(self):
        copied=self.book.planning_snapshot()
        self.assertTrue(copied.active('m'))
        self.book.revoke('m','human:owner')
        self.assertFalse(self.book.active('m'))
        self.assertTrue(copied.active('m'))
        # Snapshot is for planning only. Any live effect would be blocked.
        self.assertEqual(self.analyzer.assess(ConstitutionalPlan(
            'live',(PlanStep('x',self.intent('x')),),())).verdict,Verdict.DENY)

    def test_json_argument_hash_order_invariance(self):
        a=canonical_args_digest({'resource':'a','count':3,'sub':{'a':1,'b':2}})
        b=canonical_args_digest({'sub':{'b':2,'a':1},'count':3,'resource':'a'})
        c=canonical_args_digest({'resource':'b','count':3,'sub':{'a':1,'b':2}})
        self.assertEqual(a,b)
        self.assertNotEqual(a,c)

    def test_planner_never_enlarges_scope(self):
        plan=ConstitutionalPlan('n',(PlanStep('x',self.intent('a')),),())
        future=ActionIntent('a-new','agent:a','m','read',
                            'repo:secret/other','research',Effect.READ)
        report=self.explorer.explore(plan, (RepairEdit('privilege','x',future,1,'No privilege'),))
        self.assertEqual(report.original.verdict,Verdict.ALLOW)
        self.assertEqual([c.cost for c in report.feasible],[0])
        self.assertNotIn('privilege',[e.edit_id for c in report.feasible for e in c.edits])

if __name__=='__main__':
    unittest.main()

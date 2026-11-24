from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
import tempfile
import unittest
from pathlib import Path

from samanvaya import (ActionIntent, AuditLog, ConstitutionConfig, ConstitutionalGateway,
                       ConstitutionalPolicy, Effect, Evidence, EvidenceStatus,
                       Mandate, MandateBook, Verdict)
from samanvaya.coherence import (BeforeObligation, CoherenceAnalyzer, ConstitutionalPlan,
                                 ExclusionObligation, FactObligation, FactWitness, PlanStep)
from samanvaya.models import utcnow
from samanvaya.repair import MinimalRepairExplorer, RepairEdit
from samanvaya.adapters import BoundTool, ConstitutionalToolBroker
from samanvaya.adapters.broker import canonical_args_digest


class PlanRepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.book = MandateBook(('human:owner',))
        self.end = utcnow() + timedelta(days=4)
        self.book.issue(Mandate('m1', 'human:owner', 'agent:planner',
                                ('check', 'purchase', 'option', 'publish'),
                                ('land:tuscany',), ('sustainable-community',),
                                (Effect.READ, Effect.WRITE, Effect.EXTERNAL),
                                self.end, max_uses=30))
        self.policy = ConstitutionalPolicy(self.book, ConstitutionConfig(('human:owner',)))
        self.analyzer = CoherenceAnalyzer(self.policy)
        self.explorer = MinimalRepairExplorer(self.analyzer)
        self.audit = AuditLog(Path(self.tmp.name) / 'run.jsonl')
        self.gateway = ConstitutionalGateway(self.policy, self.audit)
        self.evidence = (Evidence('review:public', 'sha256:test', EvidenceStatus.VERIFIED),)

    def intent(self, uid='i1', action='purchase', effect=Effect.EXTERNAL,
               resource='land:tuscany/site-a'):
        return ActionIntent(uid, 'agent:planner', 'm1', action, resource,
                            'sustainable-community', effect,
                            evidence=self.evidence)

    def plan(self, witness=(), steps=None):
        return ConstitutionalPlan(
            'land-search', tuple(steps or (PlanStep('land', self.intent()),)),
            (FactObligation('r-water', 'land', 'water_supply', ('adequate',),
                            trigger_actions=('purchase',)),),
            tuple(witness))

    def test_unknown_water_blocks_entire_plan(self):
        a = self.analyzer.assess(self.plan())
        self.assertEqual(a.verdict, Verdict.UNKNOWN)
        self.assertIn('fact_not_established', [f.code for f in a.findings])

    def test_false_water_denied_even_with_other_verified_evidence(self):
        witness = FactWitness('water_supply', 'inadequate', 'survey', 'sha:survey',
                              EvidenceStatus.VERIFIED)
        a = self.analyzer.assess(self.plan((witness,)))
        self.assertEqual(a.verdict, Verdict.DENY)
        self.assertIn('fact_violates_obligation', [f.code for f in a.findings])

    def test_conflicting_witnesses_are_not_vote_counted(self):
        good = FactWitness('water_supply', 'adequate', 'a', 'sha:a', EvidenceStatus.VERIFIED)
        bad = FactWitness('water_supply', 'inadequate', 'b', 'sha:b', EvidenceStatus.VERIFIED)
        a = self.analyzer.assess(self.plan((good, bad)))
        self.assertEqual(a.verdict, Verdict.DENY)
        self.assertIn('contradictory_verified_facts', [f.code for f in a.findings])

    def test_stale_fact_cannot_authorize(self):
        expired = FactWitness('water_supply', 'adequate', 'x', 'sha:x',
                              EvidenceStatus.VERIFIED, utcnow() - timedelta(seconds=1))
        self.assertEqual(self.analyzer.assess(self.plan((expired,))).verdict, Verdict.UNKNOWN)

    def test_exclusion_and_prerequisite_invariants(self):
        a = PlanStep('survey', self.intent('survey-1', 'check', Effect.READ))
        b = PlanStep('land', self.intent('buy-1', 'purchase', Effect.EXTERNAL))
        p = ConstitutionalPlan('p', (b, a),
                              (BeforeObligation('first-survey', 'survey', 'land'),
                               ExclusionObligation('no-two', ('land', 'survey'), 1)))
        assessed = self.analyzer.assess(p)
        self.assertEqual(assessed.verdict, Verdict.DENY)
        self.assertIn('invalid_sequence', [f.code for f in assessed.findings])
        self.assertIn('incompatible_actions', [f.code for f in assessed.findings])

    def test_unknown_step_references_fail_schema(self):
        p = ConstitutionalPlan('p', (PlanStep('land', self.intent()),),
                               (FactObligation('bug', 'missing', 'water', ('yes',)),))
        with self.assertRaises(ValueError):
            self.analyzer.assess(p)

    def test_repair_minimal_among_trusted_catalog_and_never_grants_authority(self):
        # Existing mandate allows an option agreement (WRITE), not a direct purchase
        # without human approval and water evidence. Trusted alternatives only.
        p = self.plan()
        good = RepairEdit('option', 'land', self.intent('i2', 'option', Effect.WRITE),
                          2, 'Buy an option rather than the land; survey water first')
        expensive = RepairEdit('check', 'land', self.intent('i3', 'check', Effect.READ),
                               5, 'Reopen feasibility study')
        unpermitted = RepairEdit('delete', 'land', self.intent('i4', 'delete', Effect.WRITE),
                                 1, 'Cannot self-authorize deletion')
        report = self.explorer.explore(p, (good, expensive, unpermitted))
        self.assertEqual(report.original.verdict, Verdict.UNKNOWN)
        self.assertTrue(report.minimal_proven_within_catalog)
        self.assertEqual(report.catalog_variants, 4)
        self.assertEqual([c.cost for c in report.feasible], [2, 5])
        self.assertEqual(report.feasible[0].edits[0].edit_id, 'option')
        # The repair output did NOT execute the agreement or consume mandate quota.
        self.assertEqual(self.book.usage('m1'), 0)

    def test_bound_search_does_not_make_false_minimality_claim(self):
        p = self.plan()
        many = tuple(RepairEdit('s'+str(i), 'land', self.intent('i'+str(i+2), 'check', Effect.READ),
                                i+1, 'Study instead') for i in range(20))
        report = self.explorer.explore(p, many, max_variants=2)
        self.assertEqual(report.catalog_variants, 21)
        self.assertEqual(report.explored_variants, 2)
        self.assertFalse(report.complete)
        self.assertFalse(report.minimal_proven_within_catalog)

    def test_essential_step_cannot_be_removed(self):
        with self.assertRaises(ValueError):
            self.explorer.explore(self.plan(), (RepairEdit('drop','land',None,1,'Drop'),))

    def test_modified_intent_must_receive_new_id(self):
        with self.assertRaises(ValueError):
            self.explorer.explore(self.plan(), (RepairEdit('same','land',
                                  self.intent(action='check', effect=Effect.READ),1,'Same id'),))

    def test_optional_drop_preserves_known_rule_universe(self):
        p = self.plan(steps=(PlanStep('land', self.intent(), essential=False),))
        report = self.explorer.explore(p, (RepairEdit('defer','land',None,3,'No action now'),))
        self.assertTrue(report.feasible)
        self.assertEqual(report.feasible[0].plan.steps, ())
        self.assertEqual(report.feasible[0].plan.declared_step_ids, ('land',))

    def test_broker_blocks_authorized_action_when_plan_incoherent(self):
        p = ConstitutionalPlan('p', (PlanStep('land', self.intent('i2', 'option', Effect.WRITE)),),
                               (FactObligation('need-water', 'land', 'water_supply', ('adequate',)),))
        call_args = {'plot':'site-a'}
        binding = BoundTool('option', lambda args: self.intent('i2', 'option', Effect.WRITE),
                            'land', canonical_args_digest(call_args))
        broker = ConstitutionalToolBroker(self.gateway, (binding,), p, self.analyzer)
        fired = []
        output = broker.invoke('option', call_args, lambda: fired.append('EFFECT'))
        self.assertFalse(output.executed)
        self.assertEqual(output.code, 'plan_unknown')
        self.assertFalse(fired)

    def test_broker_cannot_override_mandate_from_agent_args(self):
        p = ConstitutionalPlan('p', (PlanStep('land', self.intent('i2', 'option', Effect.WRITE)),), ())
        known_args = {'plot': 'site-a'}
        binding = BoundTool('option', lambda _: self.intent('i2', 'option', Effect.WRITE),
                            'land', canonical_args_digest(known_args))
        broker = ConstitutionalToolBroker(self.gateway, (binding,), p, self.analyzer)
        fired = []
        def handler():
            fired.append('OK')
            return 'done'
        self.assertFalse(broker.invoke('option',
                         {'plot':'site-a', 'mandate_id':'ROOT'}, handler).executed)
        self.assertFalse(fired)
        response = broker.invoke('option', known_args, handler)
        self.assertEqual(response.code, 'completed')
        self.assertEqual(fired, ['OK'])
        self.assertEqual(self.book.usage('m1'), 1)

    def test_broker_unknown_tool_never_dispatches(self):
        broker = ConstitutionalToolBroker(self.gateway, ())
        response = broker.invoke('send_payment', {}, lambda: self.fail('executed'))
        self.assertEqual(response.code, 'tool_not_registered')

    def test_broker_plan_requires_exact_args_digest(self):
        p = ConstitutionalPlan('p', (PlanStep('land', self.intent('i2', 'option', Effect.WRITE)),), ())
        with self.assertRaises(ValueError):
            ConstitutionalToolBroker(self.gateway, (BoundTool('option', lambda _: p.steps[0].intent,
                                                                 'land'),), p, self.analyzer)

    def test_audit_failure_prevents_broker_execution(self):
        class BadAudit:
            def append(self, kind, data):
                raise OSError('disk full')
        broker = ConstitutionalToolBroker(ConstitutionalGateway(self.policy, BadAudit()),
                                         (BoundTool('check', lambda _: self.intent('k','check',Effect.READ)),))
        with self.assertRaises(OSError):
            broker.invoke('unknown', {}, lambda: self.fail('executed'))


if __name__ == '__main__':
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

from samanvaya import (ActionIntent, AuditIntegrityError, AuditLog, Collective, ConstitutionConfig,
                       ConstitutionalGateway, ConstitutionalPolicy, Effect, Evidence, EvidenceStatus,
                       HumanApproval, Mandate, MandateBook, Verdict, verified_events, diff_traces)
from samanvaya.mandates import in_scope, normalized_time
from samanvaya.models import utcnow


class ConstitutionalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.audit = AuditLog(Path(self.temp.name) / 'audit.jsonl')
        self.book = MandateBook(('human:owner',))
        self.exp = utcnow() + timedelta(hours=1)
        self.root = Mandate('mandate:alpha', 'human:owner', 'agent:alice',
                            ('read', 'write', 'publish'), ('repo:project',),
                            ('research',), (Effect.READ, Effect.WRITE, Effect.EXTERNAL),
                            self.exp, max_uses=5, delegable=True,
                            accountable_principal='human:owner')
        self.book.issue(self.root)
        self.policy = ConstitutionalPolicy(self.book, ConstitutionConfig(('human:owner',)))
        self.gateway = ConstitutionalGateway(self.policy, self.audit)

    def intent(self, **changes):
        return replace(ActionIntent('intent:1', 'agent:alice', 'mandate:alpha',
                                    'read', 'repo:project/paper', 'research', Effect.READ), **changes)

    def evidenced(self):
        return (Evidence('artifact:source', 'sha256:ab12', EvidenceStatus.VERIFIED),)

    def test_allowed_read_executes(self):
        called = []
        r = self.gateway.execute(self.intent(), lambda: called.append('ok'))
        self.assertEqual(r.decision.verdict, Verdict.ALLOW)
        self.assertTrue(r.executed)
        self.assertEqual(called, ['ok'])
        self.assertEqual(self.book.usage('mandate:alpha'), 1)

    def test_actor_cannot_borrow_others_mandate(self):
        r = self.gateway.execute(self.intent(actor='agent:bob'), lambda: self.fail('executed'))
        self.assertEqual(r.decision.reasons, ('actor_not_mandate_holder',))
        self.assertFalse(r.executed)

    def test_action_resource_purpose_and_effect_bounds(self):
        for change, reason in [
            ({'action': 'delete'}, 'action_out_of_scope'),
            ({'resource': 'repo:project-evil/file'}, 'resource_out_of_scope'),
            ({'purpose': 'advertising'}, 'purpose_out_of_scope'),
            ({'effect': Effect.IRREVERSIBLE}, 'effect_out_of_scope'),
        ]:
            with self.subTest(reason=reason):
                verdict = self.policy.evaluate(self.intent(**change))
                self.assertEqual(verdict.verdict, Verdict.DENY)
                self.assertEqual(verdict.reasons, (reason,))

    def test_rta_missing_evidence_unknown_never_executes(self):
        intent = self.intent(action='write', effect=Effect.WRITE)
        r = self.gateway.execute(intent, lambda: self.fail('executed'))
        self.assertEqual(r.decision.verdict, Verdict.UNKNOWN)
        self.assertFalse(r.executed)

    def test_verified_evidence_allows_write_but_conflict_denies(self):
        intent = self.intent(action='write', effect=Effect.WRITE, evidence=self.evidenced())
        self.assertEqual(self.policy.evaluate(intent).verdict, Verdict.ALLOW)
        conflict = replace(intent, evidence=(Evidence('x', 'hash', EvidenceStatus.CONFLICTING),))
        self.assertEqual(self.policy.evaluate(conflict).verdict, Verdict.DENY)

    def test_dharma_declared_harm_denied_even_with_approval(self):
        intent = self.intent(harm_flags=('privacy-risk',))
        self.assertEqual(self.policy.evaluate(intent).reasons,
                         ('declared_harm_requires_repair',))

    def test_external_requires_scoped_human_review(self):
        intent = self.intent(action='publish', effect=Effect.EXTERNAL, evidence=self.evidenced())
        self.assertEqual(self.policy.evaluate(intent).verdict, Verdict.ESCALATE)
        fake = HumanApproval('other-intent', 'human:owner', self.exp)
        self.assertEqual(self.policy.evaluate(intent, fake).verdict, Verdict.DENY)
        wrong_reviewer = HumanApproval('intent:1', 'agent:alice', self.exp)
        self.assertEqual(self.policy.evaluate(intent, wrong_reviewer).verdict, Verdict.DENY)
        good = HumanApproval('intent:1', 'human:owner', self.exp)
        self.assertEqual(self.policy.evaluate(intent, good).verdict, Verdict.ALLOW)

    def test_exhausted_quota_denies_sixth_attempt(self):
        for _ in range(5):
            self.assertTrue(self.gateway.execute(self.intent(), lambda: True).executed)
        self.assertEqual(self.policy.evaluate(self.intent()).reasons,
                         ('mandate_quota_exhausted',))

    def test_revoke_blocks_child_and_parent(self):
        child = Mandate('child', 'agent:alice', 'agent:bob', ('read',),
                        ('repo:project/sub',), ('research',), (Effect.READ,),
                        self.exp - timedelta(minutes=1), parent_id='mandate:alpha')
        self.book.issue(child)
        self.assertTrue(self.book.active('child'))
        self.book.revoke('mandate:alpha', 'human:owner')
        self.assertFalse(self.book.active('child'))
        self.assertEqual(self.policy.evaluate(self.intent()).verdict, Verdict.DENY)

    def test_delegation_cannot_expand_scope_or_rights(self):
        child = Mandate('child', 'agent:alice', 'agent:bob', ('delete',),
                        ('repo:project/sub',), ('research',), (Effect.READ,),
                        self.exp - timedelta(minutes=1), parent_id='mandate:alpha')
        with self.assertRaises(PermissionError):
            self.book.issue(child)
        with self.assertRaises(PermissionError):
            self.book.issue(replace(child, actions=('read',), resource_scopes=('repo:project-evil',)))
        with self.assertRaises(PermissionError):
            self.book.issue(replace(child, actions=('read',), expires_at=self.exp + timedelta(days=1)))
        valid = replace(child, actions=('read',))
        self.book.issue(valid)
        self.assertTrue(self.book.active('child'))

    def test_collective_has_distinct_mandate_and_quorum(self):
        c = Collective('squad:alpha', ('agent:alice', 'agent:bob', 'agent:charlie'), 2,
                       'human:owner')
        self.book.issue(Mandate('squad-m', 'human:owner', 'squad:alpha', ('read',),
                                ('repo:project',), ('research',), (Effect.READ,),
                                self.exp, max_uses=3, accountable_principal='human:owner'))
        policy = ConstitutionalPolicy(self.book, ConstitutionConfig(('human:owner',)), (c,))
        intent = self.intent(mandate_id='squad-m', collective_id='squad:alpha',
                             endorsements=('agent:alice', 'agent:bob'))
        self.assertEqual(policy.evaluate(intent).verdict, Verdict.ALLOW)
        self.assertEqual(policy.evaluate(replace(intent, endorsements=('agent:alice',))).verdict,
                         Verdict.DENY)
        self.assertEqual(policy.evaluate(replace(intent, endorsements=('agent:alice', 'agent:alice'))).verdict,
                         Verdict.DENY)
        self.assertEqual(policy.evaluate(replace(intent, endorsements=('agent:alice', 'agent:outsider'))).verdict,
                         Verdict.DENY)
        self.assertEqual(policy.evaluate(replace(intent, actor='agent:outsider')).verdict,
                         Verdict.DENY)
        # A member's personal mandate cannot be laundered through a collective.
        self.assertEqual(policy.evaluate(replace(intent, mandate_id='mandate:alpha')).verdict,
                         Verdict.DENY)

    def test_resource_traversal_rejected(self):
        self.assertFalse(in_scope('repo:project-evil/paper', 'repo:project'))
        for bad in ('repo:project/../secret', 'repo:project//secret',
                    'https://example.test/x', 'repo:project%2Fsecret', 'repo:project\\secret'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                in_scope(bad, 'repo:project')

    def test_audit_chain_and_tampering(self):
        self.gateway.execute(self.intent(), lambda: 'ok')
        events = list(verified_events(self.audit.path))
        self.assertEqual([e['kind'] for e in events],
                         ['constitutional_decision', 'execution_started', 'execution_finished'])
        data = self.audit.path.read_text()
        self.audit.path.write_text(data.replace('completed', 'altered  ', 1))
        with self.assertRaises(AuditIntegrityError):
            list(verified_events(self.audit.path))

    def test_audit_reopen_and_diff(self):
        self.gateway.execute(self.intent(), lambda: 'ok')
        second = AuditLog(self.audit.path)
        second.append('note', {'x': 1})
        self.assertEqual(len(list(verified_events(self.audit.path))), 4)
        self.assertEqual(diff_traces(self.audit.path, self.audit.path), [])

    def test_failed_operation_consumes_one_attempt(self):
        def crash():
            raise RuntimeError('nope')
        receipt = self.gateway.execute(self.intent(), crash)
        self.assertEqual(receipt.outcome, 'failed')
        self.assertEqual(self.book.usage('mandate:alpha'), 1)

    def test_audit_failure_prevents_execution(self):
        class BadAudit:
            def append(self, kind, data):
                raise OSError('disk full')
        gateway = ConstitutionalGateway(self.policy, BadAudit())
        with self.assertRaises(OSError):
            gateway.execute(self.intent(), lambda: self.fail('executed'))
        self.assertEqual(self.book.usage('mandate:alpha'), 0)


if __name__ == '__main__':
    unittest.main()

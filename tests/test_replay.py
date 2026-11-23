import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from samanvaya import (ActionIntent, AuditLog, ConstitutionConfig, ConstitutionalGateway,
                       ConstitutionalPolicy, Effect, Mandate, MandateBook, replay_constitution)
from samanvaya.models import utcnow


class ReplayTests(unittest.TestCase):
    def test_replay_agrees_without_executing_again(self):
        expires = utcnow() + timedelta(hours=1)
        def make_policy():
            book = MandateBook(('human:owner',))
            book.issue(Mandate('m', 'human:owner', 'agent:alice', ('read',),
                               ('repo:project',), ('research',), (Effect.READ,),
                               expires, max_uses=2))
            return ConstitutionalPolicy(book, ConstitutionConfig(('human:owner',)))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'run.jsonl'
            gateway = ConstitutionalGateway(make_policy(), AuditLog(path))
            intent = ActionIntent('i', 'agent:alice', 'm', 'read', 'repo:project/a',
                                  'research', Effect.READ)
            count = []
            gateway.execute(intent, lambda: count.append('run'))
            replay = replay_constitution(path, make_policy())
            self.assertEqual(replay['decisions_checked'], 1)
            self.assertTrue(replay['matched'])
            self.assertFalse(replay['side_effects_executed'])
            self.assertEqual(count, ['run'])

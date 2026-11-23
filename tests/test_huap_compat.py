import json
import tempfile
import unittest
from pathlib import Path

from samanvaya.compat import inspect_huap_trace


class HuapCompatTests(unittest.TestCase):
    def test_import_is_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'legacy.jsonl'
            p.write_text(json.dumps({
                'v': '0.1', 'ts': '2026-01-01T00:00:00Z', 'name': 'tool_call',
                'kind': 'tool', 'run_id': 'x', 'span_id': 'a', 'pod': 'example',
                'data': {'permissions': {'allowed': True}},
            }) + '\n')
            report = inspect_huap_trace(p)
            self.assertEqual(report['events'], 1)
            self.assertFalse(report['confers_authority'])

    def test_bad_legacy_trace_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'legacy.jsonl'
            p.write_text('{"name": "tool_call"}\n')
            with self.assertRaises(ValueError):
                inspect_huap_trace(p)


if __name__ == '__main__':
    unittest.main()

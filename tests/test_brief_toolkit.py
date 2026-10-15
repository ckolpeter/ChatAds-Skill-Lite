import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import brief_toolkit as b
import beginner_toolkit as beginner


class BriefTests(unittest.TestCase):
    def setUp(self):
        self.blank = json.loads((ROOT / 'templates/business-brief.json').read_text())

    def test_templates_valid(self):
        for path in ('templates/business-brief.json', 'examples/brief.synthetic.json'):
            with self.subTest(path=path):
                b.validate(json.loads((ROOT / path).read_text()))

    def test_schema_subset_stays_supported_and_closed(self):
        schema = json.loads(b.SCHEMA.read_text())
        allowed = {'$schema', 'title', 'type', 'const', 'properties', 'required',
                   'additionalProperties', 'items', 'minLength', 'pattern', 'minimum'}
        def check(node):
            self.assertFalse(set(node) - allowed)
            if node.get('type') == 'object':
                self.assertIs(node['additionalProperties'], False)
                self.assertEqual(set(node['required']), set(node['properties']))
                for child in node['properties'].values():
                    check(child)
            if 'items' in node:
                check(node['items'])
        check(schema)

    def test_cli_success_and_conversion(self):
        for command, path in [('validate', 'examples/brief.synthetic.json'),
                              ('from-beginner', 'templates/beginner-onboarding.json')]:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/brief_toolkit.py'), command, str(ROOT / path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            b.validate(json.loads(result.stdout))

    def test_partial_budget_zero_and_evidence(self):
        self.blank['spend_limit']['amount'] = 0
        self.blank['evidence'] = [{'claim': 'Fictional workshop format', 'source': 'Synthetic product sheet'}]
        self.assertEqual(b.validate(self.blank), self.blank)

    def test_negative_matrix(self):
        cases = [('contract_name', 'chatads.plan'), ('contract_version', '2.0'),
                 ('offer', ''), ('customer', []), ('open_questions', [None]),
                 ('landing_url', 'javascript:alert(1)'),
                 ('landing_url', 'https://user:pass@example.com/'),
                 ('landing_url', 'https://example.com/?private=value'),
                 ('landing_url', 'https://example.com/#value'),
                 ('evidence', [{'claim': 'claim', 'source': 'doc', 'account_id': 'synthetic'}]),
                 ('spend_limit', {'currency': 'TWD', 'amount': True, 'period_days': 1}),
                 ('spend_limit', {'currency': 'twd', 'amount': 1, 'period_days': 1}),
                 ('spend_limit', {'currency': None, 'amount': -1, 'period_days': 1}),
                 ('spend_limit', {'currency': None, 'amount': float('nan'), 'period_days': 1}),
                 ('spend_limit', {'currency': None, 'amount': float('inf'), 'period_days': 1}),
                 ('spend_limit', {'currency': None, 'amount': 1, 'period_days': 0}),
                 ('spend_limit', {'currency': None, 'amount': 1, 'period_days': 1.5})]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                data = copy.deepcopy(self.blank)
                data[key] = value
                with self.assertRaises(b.ValidationError):
                    b.validate(data)

    def test_closed_objects(self):
        for target in ('root', 'budget', 'evidence'):
            for field in ('credentials', 'account_id', 'external_writes', 'publish_authorized', 'connector_payload'):
                with self.subTest(target=target, field=field):
                    data = copy.deepcopy(self.blank)
                    node = data
                    if target == 'budget':
                        node = data['spend_limit']
                    elif target == 'evidence':
                        data['evidence'] = [{'claim': 'synthetic', 'source': 'sheet'}]
                        node = data['evidence'][0]
                    node[field] = False
                    with self.assertRaises(b.ValidationError):
                        b.validate(data)

    def test_required_fields(self):
        for key in self.blank:
            data = copy.deepcopy(self.blank)
            del data[key]
            with self.subTest(key=key), self.assertRaises(b.ValidationError):
                b.validate(data)

    def test_sensitive_prose_rejected(self):
        for key in ('business', 'offer', 'goal', 'open_questions', 'evidence'):
            data = copy.deepcopy(self.blank)
            value = 'account_id: synthetic-placeholder'
            data[key] = [value] if key == 'open_questions' else [{'claim': 'test', 'source': value}] if key == 'evidence' else value
            with self.subTest(key=key), self.assertRaises(b.ValidationError):
                b.validate(data)

    def test_legacy_conversion_preserves_unknowns_and_workflow(self):
        legacy = json.loads((ROOT / 'templates/beginner-onboarding.json').read_text())
        before = copy.deepcopy(legacy)
        out = b.from_beginner(legacy)
        self.assertEqual(legacy, before)
        self.assertEqual(beginner.onboarding(legacy)['missing_fields'][0], 'offer')
        self.assertIsNone(out['offer'])
        self.assertIsNone(out['spend_limit']['amount'])
        self.assertNotIn('external_writes', out)
        self.assertTrue(out['open_questions'])
        legacy['offer'] = 'Fictional service'
        self.assertEqual(b.from_beginner(legacy)['offer'], legacy['offer'])

    def test_legacy_rejects_permissions_versions_and_extras(self):
        baseline = json.loads((ROOT / 'templates/beginner-onboarding.json').read_text())
        for key, value in [('external_writes', True), ('external_writes', 0), ('schema_version', '2.0'), ('mode', 'pro'), ('account_id', None)]:
            data = {**baseline, key: value}
            with self.subTest(key=key), self.assertRaises(b.ValidationError):
                b.from_beginner(data)

    def test_cli_rejects_duplicates_and_nonfinite_without_echo(self):
        for text in ('{"private":"DO_NOT_ECHO","private":null}', '{"amount":NaN}', '[]'):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'input.json'
                path.write_text(text)
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/brief_toolkit.py'), 'validate', str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('DO_NOT_ECHO', result.stderr)
                self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()

"""Small adversarial checks for bounded D4 publication eligibility."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).with_name('publish_bounded_d4.py')
spec = importlib.util.spec_from_file_location('publish_bounded_d4', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicationEligibility(unittest.TestCase):
    def fixture(self, root, count=2, codim=7, bound=5):
        attempt = root / 'item' / 'attempt-001'
        attempt.mkdir(parents=True)
        files = {
            'degree4.bin': b'certificate bytes',
            'check4.stdout.txt': f'VALID: 1 is not in W_4(F), and codim W_4(F) >= {codim}\n'.encode(),
            'count.stdout.txt': f'{count}\n'.encode(),
        }
        for name, value in files.items():
            (attempt / name).write_bytes(value)
        sha = lambda value: hashlib.sha256(value).hexdigest()
        result = {'id': 'item', 'status': 'certificate_verified', 'plan_sha256': 'plan',
                  'exact_solutions': count, 'last_fall_degree_lower_bound': bound,
                  'stages': [{'degree': 3, 'certified_codimension': 3},
                             {'degree': 4, 'certified_codimension': codim,
                              'certificate_sha256': sha(files['degree4.bin'])}],
                  'artifacts': {name: {'bytes': len(value), 'sha256': sha(value)}
                                for name, value in files.items()}}
        path = attempt / 'result.json'
        path.write_text(json.dumps(result))
        return path

    def test_accepted_strict_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.fixture(Path(temporary))
            self.assertEqual(module.checked_row(path, 'plan', {'item'})['id'], 'item')

    def test_equal_count_is_publishable_without_degree_five_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.fixture(Path(temporary), count=7, codim=7, bound=4)
            self.assertIsNotNone(module.checked_row(path, 'plan', {'item'}))

    def test_tampered_certificate_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.fixture(Path(temporary))
            (path.parent / 'degree4.bin').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'retained artifact changed'):
                module.checked_row(path, 'plan', {'item'})

    def test_false_lower_bound_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.fixture(Path(temporary), count=7, codim=7, bound=5)
            with self.assertRaisesRegex(ValueError, 'lower-bound inference'):
                module.checked_row(path, 'plan', {'item'})

    def test_existing_evidence_must_match_current_receipts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.fixture(root)
            bundle = root / 'evidence.tar.gz'
            module.pack_evidence(path.parent, bundle)
            module.pack_evidence(path.parent, bundle)
            (path.parent / 'count.stdout.txt').write_text('9\n')
            with self.assertRaisesRegex(ValueError, 'evidence bundle differs'):
                module.pack_evidence(path.parent, bundle)

    def test_previous_readback_skips_only_identical_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.fixture(root)
            archive = root / 'archive'
            archive.mkdir()
            row = json.loads(path.read_text())
            receipt = {'schema': 'semaev.published-bounded-d4/v1',
                       'plan_sha256': 'plan', 'result': row,
                       'compressed_sha256': 'packed', 'compressed_bytes': 42}
            ack = {'schema': 'semaev.bounded-d4-publication-readback/v1',
                   'id': 'item', 'certificate_sha256': row['stages'][1]['certificate_sha256'],
                   'files': [{'name': 'item.D4.cert.gz', 'sha256': 'packed', 'bytes': 42}]}
            (archive / 'item.receipt.json').write_text(json.dumps(receipt))
            (archive / 'item.publication.json').write_text(json.dumps(ack))
            self.assertTrue(module.already_published(path, archive, 'plan', {'item'}))
            row['exact_solutions'] = 3
            path.write_text(json.dumps(row))
            with self.assertRaisesRegex(ValueError, 'identity differs'):
                module.already_published(path, archive, 'plan', {'item'})


if __name__ == '__main__':
    unittest.main()

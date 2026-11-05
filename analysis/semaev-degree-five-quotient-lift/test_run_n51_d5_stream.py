"""Small admission and custody controls before any high-memory D5 trial."""
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).with_name('run_n51_d5_stream.py')
sys.path.insert(0, str(SOURCE.parent))
spec = importlib.util.spec_from_file_location('run_n51_d5_stream', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TrialAdmission(unittest.TestCase):
    def fixture(self, root):
        bundle = root / 'bundle'
        bundle.mkdir()
        names = ('quotient_lift_bounded_stream', 'cert_check.py', 'count_by_sum',
                 'stream_certificate_custody.py')
        digests = {}
        for name in names:
            path = bundle / name
            path.write_bytes(name.encode())
            digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        record = dict(n=51, V_basis_hex=['1'] * 26)
        panel = dict(items=[dict(id='prior', record=record)])
        (bundle/'panel-plan.json').write_text(json.dumps(panel))
        panel_sha = module.sha(bundle/'panel-plan.json')
        prior = dict(id='prior', status='certificate_verified', plan_sha256=panel_sha,
                     exact_solutions=0, stages=[dict(degree=3),
                         dict(degree=4, certificate_sha256='raw', certified_codimension=5)])
        (bundle/'prior-result.json').write_text(json.dumps(prior))
        ack = dict(id='prior', certificate_sha256='raw', files=[
            dict(name='prior.D4.cert.gz', sha256='packed', bytes=7,
                 store_uri='s3://bucket/pinned', anonymous_url='file:///pinned')])
        (bundle/'publication-ack.json').write_text(json.dumps(ack))
        profile = dict(working_coordinates=100, next_degree_columns=10,
                       native_envelopes={'60000':dict(envelope_bytes=1000)})
        (bundle/'profile.json').write_text(json.dumps(profile))
        request = dict(schema='semaev.streamed-d5-trial-request/v1', status='frozen',
                       record=record,
                       expected_exact_solutions=0,
                       seed=dict(prior_result_sha256=module.sha(bundle/'prior-result.json'),
                                 publication_ack_sha256=module.sha(bundle/'publication-ack.json'),
                                 source_panel_plan_sha256=panel_sha, raw_sha256='raw',
                                 compressed_sha256='packed', compressed_bytes=7,
                                 compressed_uri='s3://bucket/pinned', compressed_url='file:///pinned'),
                       seed_codimension=5,
                       profile=dict(next_degree_columns=10, working_coordinates=100,
                                    bounded_native_envelope_bytes=1000,
                                    sha256=module.sha(bundle/'profile.json')),
                       limits=dict(certificate_max_bytes=32 + 8 * 10 * (1 + 2),
                                   producer_memory_bytes=10, pod_memory_bytes=20),
                       instruments=dict(producer_binary_sha256=digests['quotient_lift_bounded_stream'],
                           checker_sha256=digests['cert_check.py'],
                           counter_sha256=digests['count_by_sum'],
                           transport_sha256=digests['stream_certificate_custody.py'],
                           runner_sha256=module.sha(SOURCE)))
        return request, bundle

    def test_frozen_request_and_ceiling_are_required(self):
        with tempfile.TemporaryDirectory() as temporary:
            request, bundle = self.fixture(Path(temporary))
            module.validate_request(request, bundle, SOURCE)
            request['status'] = 'draft'
            with self.assertRaisesRegex(ValueError, 'frozen'):
                module.validate_request(request, bundle, SOURCE)
            request['status'] = 'frozen'
            request['limits']['certificate_max_bytes'] += 1
            with self.assertRaisesRegex(ValueError, 'ceiling'):
                module.validate_request(request, bundle, SOURCE)

    def test_changed_binary_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            request, bundle = self.fixture(Path(temporary))
            (bundle / 'quotient_lift_bounded_stream').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'instrument identity mismatch'):
                module.validate_request(request, bundle, SOURCE)

    def test_changed_published_predecessor_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            request, bundle = self.fixture(Path(temporary))
            prior = bundle / 'prior-result.json'
            row = json.loads(prior.read_text())
            row['exact_solutions'] = 1
            prior.write_text(json.dumps(row))
            with self.assertRaisesRegex(ValueError, 'predecessor'):
                module.validate_request(request, bundle, SOURCE)

    def test_seed_hash_and_size_are_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = b'frozen D4 seed' * 100
            packed = root / 'seed.gz'
            with gzip.open(packed, 'wb') as output:
                output.write(payload)
            request = dict(seed=dict(compressed_uri='s3://bucket/pinned',
                           compressed_url=packed.as_uri(),
                           compressed_bytes=packed.stat().st_size,
                           compressed_sha256=module.sha(packed),
                           raw_bytes=len(payload),
                           raw_sha256=hashlib.sha256(payload).hexdigest()),
                           limits=dict(seed_transfer_timeout_seconds=10))
            out = root / 'out'
            out.mkdir()
            raw = module.receive_seed(request, out, None)
            self.assertEqual(raw.read_bytes(), payload)
            request['seed']['raw_sha256'] = '0' * 64
            next_out = root / 'changed'
            next_out.mkdir()
            with self.assertRaisesRegex(ValueError, 'raw D4 seed identity mismatch'):
                module.receive_seed(request, next_out, None)

    def test_timeout_keeps_stage_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                module.stage('slow', [sys.executable, '-c', 'import time; time.sleep(2)'],
                             root, None, 0.05, 1 << 30)
            self.assertTrue(json.loads((root / 'slow.json').read_text())['timed_out'])


if __name__ == '__main__':
    unittest.main()

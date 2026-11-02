#!/usr/bin/env python3
"""Exercise publication selection without starting a native closure run."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import checkpoint_cadence_hook as hook


class CadenceHookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.snapshots = self.root / 'snapshots'
        self.snapshots.mkdir()
        self.request = self.root / 'request.json'
        self.context = self.root / 'context.json'
        self.seed = 'ab' * 32
        self.binary = 'cd' * 32

    def environment(self, cadence=3):
        data = (json.dumps({'checkpoint_publish_every': cadence}) + '\n').encode()
        self.request.write_bytes(data)
        self.context.write_text(json.dumps({
            'request_sha256': hashlib.sha256(data).hexdigest(),
            'seed_sha256': self.seed, 'binary_sha256': self.binary,
        }))
        return patch.dict(os.environ, {
            'SEMAEV_CHECKPOINT_DIR': str(self.snapshots),
            'SEMAEV_CHECKPOINT_REQUEST': str(self.request),
            'SEMAEV_CHECKPOINT_CONTEXT': str(self.context),
            'SEMAEV_CHECKPOINT_PRUNE_LOCAL': '1',
        })

    def snapshot(self, sequence, phase=0, seed=None):
        path = self.snapshots / f'checkpoint-{sequence}.bin'
        words = [hook.MAGIC, 1, 6, 5, 8, 1, 7, 2,
                 phase, 0, 0, 0, 0, sequence]
        path.write_bytes(struct.pack('<14Q', *words) +
                         bytes.fromhex(seed or self.seed) +
                         bytes.fromhex(self.binary) + bytes(32))
        return path

    def integration_environment(self):
        work = self.root / 'work'
        work.mkdir()
        request = {
            'checkpoint_publish_every': 3,
            'disk_policy': {
                'N': 6, 'degree': 5, 'working_coordinates': 8,
                'capacity_bytes': 1 << 30, 'reserve_bytes': 16 << 20,
                'work_root': str(self.root),
                'certificate_relative_path': 'work/certificate.bin',
            },
        }
        data = (json.dumps(request) + '\n').encode()
        self.request.write_bytes(data)
        self.context.write_text(json.dumps({
            'request_sha256': hashlib.sha256(data).hexdigest(),
            'protocol_sha256': 'ef' * 32,
            'seed_sha256': self.seed, 'binary_sha256': self.binary,
        }))
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        aws = bin_dir / 'aws'
        shutil.copy2(Path(__file__).with_name('fake_checkpoint_aws.py'), aws)
        aws.chmod(0o755)
        return patch.dict(os.environ, {
            'SEMAEV_CHECKPOINT_DIR': str(self.snapshots),
            'SEMAEV_CHECKPOINT_REQUEST': str(self.request),
            'SEMAEV_CHECKPOINT_CONTEXT': str(self.context),
            'SEMAEV_CHECKPOINT_PRUNE_LOCAL': '1',
            'SEMAEV_CHECKPOINT_S3_PREFIX': 's3://fake-bucket/cadence',
            'FAKE_CHECKPOINT_STORE': str(self.root / 'store'),
            'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'],
        })

    def test_skipped_seed_snapshot_is_removed(self):
        snapshot = self.snapshot(2)
        with self.environment(), patch.object(hook.subprocess, 'run') as publish:
            hook.run(snapshot)
        self.assertFalse(snapshot.exists())
        publish.assert_not_called()

    def test_due_seed_snapshot_uses_verified_guard(self):
        snapshot = self.snapshot(3)
        with self.environment(), patch.object(hook.subprocess, 'run') as publish:
            hook.run(snapshot)
        self.assertTrue(snapshot.exists())
        publish.assert_called_once()
        self.assertEqual(publish.call_args.args[0][-1], str(snapshot))

    def test_phase_transition_is_always_published(self):
        snapshot = self.snapshot(2, phase=1)
        with self.environment(), patch.object(hook.subprocess, 'run') as publish:
            hook.run(snapshot)
        publish.assert_called_once()

    def test_bad_context_is_rejected_before_pruning(self):
        snapshot = self.snapshot(2, seed='ef' * 32)
        with self.environment(), patch.object(hook.subprocess, 'run') as publish:
            with self.assertRaisesRegex(ValueError, 'identity/context mismatch'):
                hook.run(snapshot)
        self.assertTrue(snapshot.exists())
        publish.assert_not_called()

    def test_boolean_cadence_is_not_an_integer_policy(self):
        snapshot = self.snapshot(2)
        with self.environment(True):
            with self.assertRaisesRegex(ValueError, 'invalid checkpoint publication cadence'):
                hook.run(snapshot)
        self.assertTrue(snapshot.exists())

    def test_due_snapshot_uses_real_guard_and_fake_store(self):
        snapshot = self.snapshot(3)
        body = snapshot.read_bytes()[:-32]
        snapshot.write_bytes(body + hashlib.sha256(body).digest())
        with self.integration_environment():
            hook.run(snapshot)
            for sequence in (4, 5):
                skipped = self.snapshot(sequence)
                hook.run(skipped)
                self.assertFalse(skipped.exists())
            later = self.snapshot(6)
            body = later.read_bytes()[:-32]
            later.write_bytes(body + hashlib.sha256(body).digest())
            hook.run(later)
            restored = self.root / 'restored'
            receipt = self.root / 'restore.json'
            subprocess.run([
                sys.executable, str(Path(__file__).with_name('restore_lift_checkpoint.py')),
                '--prefix', 's3://fake-bucket/cadence', '--context', str(self.context),
                '--out', str(restored), '--receipt', str(receipt),
            ], check=True, stdout=subprocess.PIPE)
        self.assertFalse(snapshot.exists())
        ack = json.loads((self.snapshots / 'checkpoint-3.publication.json').read_text())
        self.assertEqual(ack['snapshot']['sequence'], 3)
        objects = list((self.root / 'store' / 'fake-bucket' / 'cadence' / 'objects').glob('*.bin'))
        manifests = list((self.root / 'store' / 'fake-bucket' / 'cadence' / 'manifests').glob('*.json'))
        self.assertEqual((len(objects), len(manifests)), (2, 2))
        restored_result = json.loads(receipt.read_text())
        self.assertEqual(restored_result['status'], 'checkpoint_restored')
        self.assertEqual(restored_result['snapshot']['sequence'], 6)


if __name__ == '__main__':
    unittest.main()

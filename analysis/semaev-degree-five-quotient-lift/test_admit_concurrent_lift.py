import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import admit_concurrent_lift as gate


class ConcurrentGateTests(unittest.TestCase):
    def test_future_growth_is_reserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            owner_plan = base / 'owner.json'
            owner_plan.write_text(json.dumps({'memory_bytes': 1_000}))
            plan = {
                'concurrent_owners': [{
                    'pid': 10, 'command_contains': 'existing-owner',
                    'plan': str(owner_plan), 'plan_sha256': gate.sha(owner_plan),
                    'memory_bytes': 1_000,
                }],
                'memory_bytes': 500, 'reserve_bytes': 100,
                'output_root': str(base / 'absent'),
                'checkpoint_prefix': 's3://example/checkpoints/new',
            }
            rows = {10: (1, 50, 'existing-owner'), 11: (10, 150, 'native-child')}
            clear = type('Result', (), {'stdout': '{}'})()
            with patch.object(gate, 'proc_table', return_value=rows), \
                 patch.object(gate, 'total_bytes', return_value=4_000), \
                 patch.object(gate, 'available_bytes', return_value=1_400), \
                 patch.object(gate.subprocess, 'run', return_value=clear):
                accepted = gate.gate(plan)
            self.assertEqual(accepted['required_available_bytes'], 1_400)
            self.assertEqual(accepted['owners'][0]['pids'], [10, 11])
            with patch.object(gate, 'proc_table', return_value=rows), \
                 patch.object(gate, 'total_bytes', return_value=4_000), \
                 patch.object(gate, 'available_bytes', return_value=1_399):
                with self.assertRaisesRegex(ValueError, 'future-growth headroom'):
                    gate.gate(plan)

    def test_owner_identity_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            owner_plan = Path(tmp) / 'owner.json'
            owner_plan.write_text(json.dumps({'memory_bytes': 1_000}))
            plan = {'concurrent_owners': [{'pid': 10, 'command_contains': 'expected',
                     'plan': str(owner_plan), 'plan_sha256': gate.sha(owner_plan),
                     'memory_bytes': 1_000}], 'memory_bytes': 500, 'reserve_bytes': 100}
            with patch.object(gate, 'proc_table', return_value={10: (1, 50, 'different')}):
                with self.assertRaisesRegex(ValueError, 'named owner not live'):
                    gate.gate(plan)


if __name__ == '__main__':
    unittest.main()

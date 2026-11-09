import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_finite_selector import fixture


class RetainedExactTests(unittest.TestCase):
    def run_cli(self, limit=1000000, corrupt=False):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        p=Path(folder.name);s,a=fixture()
        if corrupt:a['equations'][0]['monomial_masks_hex']=[]
        (p/'parameters.json').write_text(json.dumps(s));(p/'system.json').write_text(json.dumps(a))
        cmd=[sys.executable,str(Path(__file__).with_name('inspect_retained_lfd.py')),str(p/'parameters.json'),str(p/'system.json'),'--operation-limit',str(limit),'--output',str(p/'result.json')]
        run=subprocess.run(cmd,capture_output=True,text=True)
        return p,cmd,run
    def test_complete_binds_original_and_preserves_scope(self):
        p,cmd,r=self.run_cli();self.assertEqual(r.returncode,0,r.stderr)
        data=json.loads((p/'result.json').read_text())
        self.assertEqual(data['analysis']['status'],'complete')
        # Only pairs (0,1),(1,0); zero has two selector codes, hence four code solutions.
        self.assertEqual(data['analysis']['zero_count'],4)
        self.assertIsInstance(data['analysis']['exact_lfd'],int)
        self.assertEqual(len(data['analysis']['caps']),6)
        self.assertFalse(data['dataset_admission'])
        self.assertFalse(data['analysis']['independently_checked_certificate'])
        before=(p/'result.json').read_bytes()
        rerun=subprocess.run(cmd,capture_output=True,text=True)
        self.assertNotEqual(rerun.returncode,0);self.assertEqual((p/'result.json').read_bytes(),before)
    def test_exhaustion_never_exact(self):
        p,_,r=self.run_cli(limit=1);self.assertEqual(r.returncode,0,r.stderr)
        data=json.loads((p/'result.json').read_text())
        self.assertEqual(data['analysis']['status'],'budget_exhausted')
        self.assertIsNone(data['analysis']['exact_lfd'])
        self.assertLessEqual(data['analysis']['operations_used'],1)
    def test_corruption_never_admitted(self):
        p,_,r=self.run_cli(corrupt=True)
        self.assertNotEqual(r.returncode,0);self.assertFalse((p/'result.json').exists())


if __name__=='__main__':unittest.main()

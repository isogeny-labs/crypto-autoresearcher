import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from attach_verified_lfd import attach, read_certificate
from exact_boolean_lfd import analyze
from test_finite_selector import fixture
from join_retained_weil import polys


class AttachedCertificateTests(unittest.TestCase):
    def inputs(self):
        s,a=fixture();rows=polys(a['equations'],3,4)
        c=analyze(4,rows,1000000,include_certificate=True)['certificate']
        return s,a,c
    def test_exact_label_after_fresh_verification(self):
        s,a,c=self.inputs();r=attach(s,a,c)
        self.assertTrue(r['certificate_verified']);self.assertTrue(r['bound_labels_admission'])
        self.assertEqual(r['last_fall_degree'],{'exact':4,'lower_bound':4,'upper_bound':4})
        self.assertFalse(r['dataset_admission']);self.assertIsNone(r['native_instruction_count'])
    def test_valid_certificate_for_other_system_rejected(self):
        s,a,c=self.inputs()
        other=analyze(4,[[]],1000000,include_certificate=True)['certificate']
        with self.assertRaises(ValueError):attach(s,a,other)
    def test_matching_equations_with_corrupted_proof_rejected(self):
        s,a,c=self.inputs()
        for cap in c['caps']:
            if cap['basis']:
                cap['basis'][0]['source']={'parent':0,'variable':0};break
        with self.assertRaises(ValueError):attach(s,a,c)
    def test_exhaustion_not_admitted(self):
        s,a,c=self.inputs();r=attach(s,a,c,1)
        self.assertFalse(r['certificate_verified']);self.assertFalse(r['bound_labels_admission'])
        self.assertIsNone(r['last_fall_degree']['exact']);self.assertEqual(r['last_fall_degree']['upper_bound'],5)
    def test_different_original_artifact_rejected(self):
        s,a,c=self.inputs();a['coordinate_maps'][0][0]['monomial_masks_hex']=[]
        with self.assertRaises(ValueError):attach(s,a,c)
    def test_cli_roundtrip_and_exclusive_output(self):
        s,a,c=self.inputs()
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for name,obj in [('p',s),('a',a),('c',c)]: (p/name).write_text(json.dumps(obj))
            cmd=[sys.executable,str(Path(__file__).with_name('attach_verified_lfd.py')),str(p/'p'),str(p/'a'),str(p/'c'),'--output',str(p/'out')]
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
            out=json.loads((p/'out').read_text());self.assertTrue(out['certificate_verified'])
            self.assertEqual(out['certificate_file_sha256'],read_certificate(p/'c')[1])
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(r.returncode,0)
            (p/'dup').write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError):read_certificate(p/'dup')


if __name__=='__main__':unittest.main()

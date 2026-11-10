import unittest
import json
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
import check_candidate as direct
from inspect_bounds import inspect

def candidate():
    return {'schema':direct.SCHEMA,'input':{'schema':'semaev.normalized-binary-m2-input/v1','n':3,'modulus':11,'basis':[1],'a2':0,'a6':1,'z':1,'require_rational_target':False},'degree_cap':2,'quotient_dimension':2,'columns':[1,2,3,0]}

class DirectControls(unittest.TestCase):
    def test_rank_two_full_kernel(self):
        c=candidate();r=direct.check(c)
        self.assertEqual(r['low_degree_rank'],2)
        self.assertEqual(r['low_degree_kernel_dimension'],1)
        self.assertEqual(r['kernel_products_checked'],2)
        self.assertEqual(r['codimension_lower_bound'],2)
        self.assertIsNone(r['lfd_lower_bound'])
        self.assertEqual(r['bridge_status'],'not_supplied')
        self.assertFalse(r['dataset_admission'])
        self.assertEqual(r['equation_binding_sha256'],inspect(c['input'])['equation_binding_sha256'])
    def test_arbitrary_quotient_basis(self):
        c=candidate();c['columns']=[2,1,3,0]
        self.assertTrue(direct.check(c)['constant_nonmembership_checked'])
    def test_rank_one_evaluation(self):
        c=candidate();c.update(quotient_dimension=1,columns=[1,0,1,0])
        self.assertEqual(direct.check(c)['low_degree_kernel_dimension'],2)
    def test_initial_annihilation_does_not_imply_closure(self):
        c=candidate();c['columns']=[1,2,3,1]
        with self.assertRaisesRegex(direct.Invalid,'not closed'):direct.check(c)
    def test_generator_rank_and_constant_rejections(self):
        for columns,reason in [([1,2,2,0],'generator'),([1,1,0,0],'rank'),([0,1,2,0],'constant')]:
            c=candidate();c['columns']=columns
            with self.assertRaisesRegex(direct.Invalid,reason):direct.check(c)
    def test_does_not_use_reconstructed_validator_equations(self):
        c=candidate();original=inspect(c['input'])
        original['equation_binding']['equations']=[[0]]
        original['equation_binding_sha256']='incorrect deliberately'
        with patch.object(direct,'inspect',return_value=original):
            self.assertNotEqual(direct.check(c)['equation_binding_sha256'],'incorrect deliberately')
    def test_shape_and_caps(self):
        for update in [dict(degree_cap=True),dict(quotient_dimension=65),dict(columns=[1]),dict(columns=[1,2,3,-1]),dict(extra='T')]:
            c=candidate();c.update(update)
            with self.assertRaises(direct.Invalid):direct.check(c)
        c=candidate();c['input']['basis']=[1<<i for i in range(9)]
        with self.assertRaisesRegex(direct.Capacity,'variable cap'):direct.check(c)
        c=candidate();c['input']['basis']=[1<<i for i in range(8)];c['degree_cap']=8
        with self.assertRaisesRegex(direct.Capacity,'monomial'):direct.check(c)

    def test_cli_refusal_statuses(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            cases=[]
            c=candidate();c['columns']=[1,2,3,1];cases.append((c,'rejected_input_or_predicate'))
            c=candidate();c['input']['basis']=[1<<i for i in range(9)];cases.append((c,'not_checked_capacity'))
            cases.append((candidate(),'checked'))
            for i,(c,status) in enumerate(cases):
                source=root/('input%d.json'%i);out=root/('out%d.json'%i)
                source.write_text(json.dumps(c))
                command=[sys.executable,str(Path(__file__).with_name('check_candidate.py')),str(source),'--output',str(out)]
                result=subprocess.run(command,capture_output=True,timeout=5)
                self.assertEqual(result.returncode,0 if status=='checked' else 2,result.stderr)
                record=json.loads(out.read_text());self.assertEqual(record['status'],status)
                self.assertIsNone(record['lfd_lower_bound'])
                original=out.read_bytes()
                self.assertNotEqual(subprocess.run(command,capture_output=True,timeout=5).returncode,0)
                self.assertEqual(out.read_bytes(),original)

if __name__=='__main__':unittest.main()

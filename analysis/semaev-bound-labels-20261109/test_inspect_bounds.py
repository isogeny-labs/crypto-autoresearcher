import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from inspect_bounds import Field, inspect, SCHEMA

class Controls(unittest.TestCase):
    def fixture(self):
        return dict(schema=SCHEMA,n=4,modulus=19,basis=[1,6],a2=8,a6=1,z=2,require_rational_target=True)
    def test_subfield(self):
        r=inspect(self.fixture(),4)
        self.assertTrue(r['quadratic_subfield_basis'])
        self.assertEqual(r['written_lfd_upper_bound'],2) # constant trace refutation
        self.assertIsNone(r['exact_lfd'])
        self.assertIsNone(r['lfd_lower_bound'])
        self.assertEqual(r['product_profile']['distinct_pair_count'],0)
        self.assertFalse(r['solver_executed'])
        self.assertFalse(r['dataset_admission'])
        self.assertEqual(r['original_dataset_equations_match'],'not_checked')
        self.assertFalse(r['theorem_sources_runtime_verified'])
    def test_unknown(self):
        for limit,status in [(0,'not_checked'),(2,'not_checked_capacity')]:
            r=inspect(self.fixture(),limit)['product_profile']
            self.assertEqual(r['status'],status)
            self.assertIsNone(r['distinct_product_member'])
    def test_rejections(self):
        for update in [dict(modulus=-19),dict(modulus=21),dict(basis=[1,1]),dict(a6=0),dict(z=0),dict(a2=0),dict(n=True),dict(extra=True)]:
            s=self.fixture();s.update(update)
            with self.assertRaises(ValueError):inspect(s)
    def test_equation_values(self):
        s=self.fixture();r=inspect(s);f=Field(4,19)
        for bits in range(16):
            x=(bits&1)^ (6 if bits&2 else 0)
            y=((bits>>2)&1)^ (6 if bits&8 else 0)
            p=f.mul(x,y)
            expected=f.mul(p,p)^f.mul(2,p)^f.mul(4,f.mul(x^y,x^y))^1
            actual=0
            for b,row in enumerate(r['equation_binding']['equations']):
                actual |= (sum((bits&m)==m for m in row)%2)<<b
            self.assertEqual(actual,expected)
    def test_input_binding(self):
        a=self.fixture();b=self.fixture();b['basis']=[6,1]
        self.assertNotEqual(inspect(a)['input_sha256'],inspect(b)['input_sha256'])
        self.assertNotEqual(inspect(a)['equation_binding_sha256'],inspect(b)['equation_binding_sha256'])

    def test_cli_no_clobber_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'input.json'; out=root/'output.json'
            source.write_text(json.dumps(self.fixture()))
            command=[sys.executable,str(Path(__file__).with_name('inspect_bounds.py')),str(source),'--output',str(out)]
            first=subprocess.run(command,capture_output=True,timeout=5)
            self.assertEqual(first.returncode,0,first.stderr)
            result=json.loads(out.read_text())
            self.assertEqual(len(result['inspector_sha256']),64)
            self.assertTrue(result['theorem_source_sha256'])
            original=out.read_bytes()
            self.assertNotEqual(subprocess.run(command,capture_output=True,timeout=5).returncode,0)
            self.assertEqual(out.read_bytes(),original)
            out.unlink()
            source.write_text('{"n":4,"n":5}')
            self.assertNotEqual(subprocess.run(command,capture_output=True,timeout=5).returncode,0)
            self.assertFalse(out.exists())

    def test_negative_modulus_cli_terminates(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); source=root/'input.json'; out=root/'output.json'
            spec=self.fixture();spec['modulus']=-19;source.write_text(json.dumps(spec))
            command=[sys.executable,str(Path(__file__).with_name('inspect_bounds.py')),str(source),'--output',str(out)]
            result=subprocess.run(command,capture_output=True,timeout=5)
            self.assertNotEqual(result.returncode,0)
            self.assertIn(b'monic odd degree-n modulus required',result.stderr)
            self.assertFalse(out.exists())

if __name__=='__main__':unittest.main()

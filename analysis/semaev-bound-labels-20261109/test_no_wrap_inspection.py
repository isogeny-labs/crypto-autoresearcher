import unittest
from inspect_bounds import inspect,SCHEMA

class NoWrapControls(unittest.TestCase):
    def fixture(self,r=6):
        return dict(schema=SCHEMA,n=25,modulus=(1<<25)|(1<<3)|1,basis=[1<<i for i in range(r+1)],a2=0,a6=1,z=1,require_rational_target=True)
    def test_exact_and_changed_input_basis(self):
        a=self.fixture();b=self.fixture();b['basis'][0]^=b['basis'][1];b['basis'].reverse()
        for s in (a,b):
            v=inspect(s);self.assertTrue(v['no_wrap_family']['recognized']);self.assertEqual(v['exact_lfd'],3);self.assertEqual(v['lfd_lower_bound'],3);self.assertEqual(v['written_lfd_upper_bound'],3);self.assertEqual(v['ffd']['exact_value'],2);self.assertEqual(v['written_solution_count'],2);self.assertFalse(v['dataset_admission'])
        self.assertNotEqual(inspect(a)['equation_binding_sha256'],inspect(b)['equation_binding_sha256'])
    def test_small_family(self):
        for r in (1,5):
            v=inspect(self.fixture(r));self.assertEqual(v['exact_lfd'],2);self.assertEqual(v['written_lfd_upper_bound'],2)
    def test_boundary_and_wrong_subspace(self):
        for update in [dict(basis=[1,2,4,8,16,32,128]),dict(basis=[1<<i for i in range(8)]),dict(z=2,require_rational_target=False),dict(a6=2,require_rational_target=False),dict(basis=[1])]:
            s=self.fixture();s.update(update);v=inspect(s);self.assertFalse(v['no_wrap_family']['recognized']);self.assertIsNone(v['exact_lfd']);self.assertIsNone(v['written_solution_count'])
    def test_larger_member_has_interval_not_exact_label(self):
        s=self.fixture(7);s.update(n=31,modulus=(1<<31)|(1<<3)|1)
        v=inspect(s);self.assertTrue(v['no_wrap_family']['recognized']);self.assertEqual(v['lfd_lower_bound'],3);self.assertEqual(v['written_lfd_upper_bound'],4);self.assertIsNone(v['exact_lfd'])
    def test_independence_cannot_be_skipped(self):
        s=self.fixture();s['basis'][-1]=s['basis'][0]
        with self.assertRaises(ValueError):inspect(s)
    def test_original_row_witness(self):
        s=self.fixture();s['basis'][0]^=s['basis'][2];v=inspect(s);rows=v['equation_binding']['equations'];out=set()
        for row in rows[1:]:out.symmetric_difference_update(row)
        self.assertTrue(out);self.assertTrue(all(m.bit_count()<=1 for m in out));self.assertNotEqual(out,set(rows[0]));self.assertTrue(all(any(m.bit_count()==2 for m in row) for row in rows[1:] if row))

if __name__=='__main__':unittest.main()

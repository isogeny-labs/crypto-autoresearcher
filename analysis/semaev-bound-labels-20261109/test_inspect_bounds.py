import unittest
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
    def test_unknown(self):
        for limit,status in [(0,'not_checked'),(2,'not_checked_capacity')]:
            r=inspect(self.fixture(),limit)['product_profile']
            self.assertEqual(r['status'],status)
            self.assertIsNone(r['distinct_product_member'])
    def test_rejections(self):
        for update in [dict(modulus=21),dict(basis=[1,1]),dict(a6=0),dict(z=0),dict(a2=0),dict(n=True),dict(extra=True)]:
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

if __name__=='__main__':unittest.main()

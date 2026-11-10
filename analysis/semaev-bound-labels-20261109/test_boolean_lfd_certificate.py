import copy
import unittest
from exact_boolean_lfd import analyze
from verify_boolean_lfd_certificate import verify


class CertificateTests(unittest.TestCase):
    def certificate(self):return analyze(2,[[3],[0,3]],1000000,include_certificate=True)['certificate']
    def test_independent_verification(self):
        c=self.certificate();r=verify(c)
        self.assertTrue(r['verified']);self.assertEqual(r['exact_lfd'],2);self.assertEqual(r['zero_count'],0)
    def test_missing_caps(self):
        c=self.certificate();c['caps'].pop()
        with self.assertRaises(ValueError):verify(c)
    def test_forward_reference(self):
        c=self.certificate();c['caps'][2]['basis'][0]['source']={'parent':0,'variable':0}
        with self.assertRaises(ValueError):verify(c)
    def test_changed_row(self):
        c=self.certificate();c['caps'][2]['basis'][0]['row']=[1]
        with self.assertRaises(ValueError):verify(c)
    def test_missing_input_and_unsaturated_basis(self):
        c=self.certificate();c['caps'][2]['basis']=[]
        with self.assertRaises(ValueError):verify(c)
        c=analyze(2,[[1]],1000000,include_certificate=True)['certificate']
        c['caps'][2]['basis']=c['caps'][2]['basis'][:1]
        with self.assertRaises(ValueError):verify(c)
    def test_budget_cannot_verify(self):
        r=verify(self.certificate(),1)
        self.assertFalse(r['verified']);self.assertIsNone(r['exact_lfd'])
    def test_invalid_domains(self):
        c=self.certificate();c['n_vars']=True
        with self.assertRaises(ValueError):verify(c)
        c=self.certificate();c['equations'][0]=[4]
        with self.assertRaises(ValueError):verify(c)
    def test_affine_and_constants(self):
        for n,rows,degree in [(0,[],0),(0,[[0]],0),(2,[[1]],0),(1,[[1],[0,1]],1)]:
            c=analyze(n,rows,1000000,include_certificate=True)['certificate'];r=verify(c)
            self.assertTrue(r['verified']);self.assertEqual(r['exact_lfd'],degree)


if __name__=='__main__':unittest.main()

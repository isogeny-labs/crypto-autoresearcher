import unittest
from fractions import Fraction
from proof_reference import sum_fibres, collection_floor


class ProofCountercontrols(unittest.TestCase):
    def test_mass_counts_ordered_tuples_with_repetitions(self):
        for r in range(2,10):
            for base in ([],[0],[0,1],list(range(r))):
                for m in (1,2,3):
                    counts=sum_fibres(r,base,m)
                    self.assertEqual(sum(counts),len(base)**m)
                    self.assertLessEqual(sum(c>0 for c in counts),min(r,len(base)**m))

    def test_mean_is_not_success_probability(self):
        counts=sum_fibres(5,[0,1],2)
        self.assertEqual(sum(counts),4)
        self.assertEqual(sum(c>0 for c in counts),3)

    def test_iid_assumption_is_necessary(self):
        counts=sum_fibres(7,[0],2)
        uniform=Fraction(sum(c>0 for c in counts),7)
        adaptive=counts[0]>0
        self.assertEqual(uniform,Fraction(1,7))
        self.assertTrue(adaptive)

    def test_boundary_and_restricted_enumeration_floor(self):
        self.assertEqual(collection_floor(7,0,2,0),0)
        with self.assertRaises(ValueError):collection_floor(7,0,2,1)
        # Conditional model K=B and c0=B: its m2 floor is >=r.
        for r in range(2,30):
            for b in range(1,r+1):
                self.assertGreaterEqual(collection_floor(r,b,2,b,b),r)


if __name__=='__main__':unittest.main()

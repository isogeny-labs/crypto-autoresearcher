import copy
import unittest
from attach_capacity_bound import attach, capacity_profile
from check_candidate import Invalid
from test_check_candidate import candidate

class CapacityControls(unittest.TestCase):
    def test_rank_equal_capacity_is_not_a_lower_bound(self):
        result=attach(candidate(),2)
        self.assertEqual(result['capacity_profile']['ordered_solution_upper_bound'],2)
        self.assertEqual(result['direct_check']['quotient_dimension'],2)
        self.assertEqual(result['status'],'inconclusive_capacity')
        self.assertIsNone(result['lfd_lower_bound'])
        self.assertFalse(result['dataset_admission'])
    def test_invalid_closure_never_reaches_capacity_admission(self):
        c=candidate();c['columns']=[1,2,3,1]
        with self.assertRaisesRegex(Invalid,'not closed'):attach(c,2)
    def test_known_F16_trace_refutation_has_zero_capacity(self):
        spec=dict(schema='semaev.normalized-binary-m2-input/v1',n=4,modulus=19,basis=[1,6],a2=8,a6=1,z=2,require_rational_target=True)
        for cap in [0,2,4]:
            result=capacity_profile(spec,cap)
            self.assertEqual(result['ordered_solution_upper_bound'],0)
            self.assertEqual(result['admissible_selector_count'],0)
            self.assertFalse(result['affine_fibre_consistency_checked'])
            self.assertIsNone(result['exact_solution_count'])
    def test_missing_profile_is_unknown_not_exclusion(self):
        spec=candidate()['input']
        for limit,status in [(0,'not_checked'),(1,'not_checked_capacity')]:
            result=capacity_profile(spec,limit)
            self.assertEqual(result['profile_status'],status)
            self.assertTrue(result['square_member'])
            self.assertEqual(result['square_membership_method'],'linear_span_rank')
            self.assertIsNone(result['admissible_distinct_product_pairs'])
    def test_involution_and_selector_capacity_for_known_two_points(self):
        result=capacity_profile(candidate()['input'],2)
        self.assertEqual(result['product_preimages'],1)
        self.assertEqual(result['total_distinct_product_pairs'],0)
        self.assertTrue(result['square_member'])
        self.assertFalse(result['zero_selector_admissible'])
        self.assertEqual(result['admissible_selector_count'],1)
        self.assertEqual(result['ordered_solution_upper_bound'],2)
    def test_caller_bound_or_verdict_cannot_be_injected(self):
        for key,value in [('solution_count',0),('checked',True),('codimension_lower_bound',100)]:
            c=candidate();c[key]=value
            with self.assertRaises(Invalid):attach(c)
        for limit in [-1,True,257]:
            with self.assertRaises(ValueError):capacity_profile(candidate()['input'],limit)

if __name__=='__main__':unittest.main()

import json
from pathlib import Path
import unittest
from verify_degree_three_control import verify

class FixedControl(unittest.TestCase):
    def candidate(self):
        return json.loads(Path(__file__).with_name('degree-three-control').joinpath('candidate.json').read_text())
    def test_matching_lower_and_upper_witnesses(self):
        result=verify(self.candidate())
        self.assertEqual((result['lfd_lower_bound'],result['lfd_upper_bound'],result['exact_lfd']),(3,3,3))
        self.assertEqual(result['ordered_solution_count'],2)
        self.assertFalse(result['dataset_admission'])
    def test_wrong_system_refused(self):
        c=self.candidate();c['input']['basis']=[1,3]
        with self.assertRaisesRegex(ValueError,'fixed normalized'):verify(c)
    def test_bad_quotient_refused(self):
        c=self.candidate();c['columns'][6]=1 # ac should vanish.
        with self.assertRaises(ValueError):verify(c)

if __name__=='__main__':unittest.main()

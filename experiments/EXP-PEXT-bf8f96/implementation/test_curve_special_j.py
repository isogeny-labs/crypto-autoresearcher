"""Exact special-j classification in ordinary and characteristic-three fields."""

import json
from pathlib import Path
import unittest

from check_quotient_certificate import Field
from curve_special_j import special_j


class SpecialJTests(unittest.TestCase):
    def field(self, cohort):
        path = Path(__file__).parent.parent / "inputs/join-plans-20261103" / f"{cohort}.json"
        return Field(json.loads(path.read_text())["field"])

    def test_q5_ordinary_special_values_and_nonspecial(self):
        f = self.field("q5-n3")
        self.assertTrue(special_j(f, [0, 0, 1]))  # j=0
        self.assertTrue(special_j(f, [0, 1, 0]))  # j=1728 mod 5 = 3
        self.assertFalse(special_j(f, [0, 1, 1]))  # j=2
        with self.assertRaisesRegex(ValueError, "singular"):
            special_j(f, [0, 0, 0])

    def test_q3_collapsed_special_values(self):
        f = self.field("q3-n5")
        self.assertTrue(special_j(f, [0, 1, 0]))  # 1728=0 in char 3
        self.assertFalse(special_j(f, [1, 0, 1]))

    def test_all_published_models_against_cubic_discriminant_formula(self):
        counts = {}
        for cohort in ("q5-n3", "q7-n3", "q11-n3", "q3-n5"):
            path = Path(__file__).parent.parent / "inputs/join-plans-20261103" / f"{cohort}.json"
            plan = json.loads(path.read_text())
            f = Field(plan["field"])
            flags = []
            for curve in plan["classes"]:
                a, b, c = curve["model"]
                mul, add, sub = f.mul, f.add, f.sub
                k = lambda value: value % f.p
                c4 = sub(mul(k(16), mul(a, a)), mul(k(48), b))
                discriminant = add(
                    sub(mul(mul(a, a), mul(b, b)), mul(k(4), f.power(b, 3))),
                    add(sub(0, mul(k(4), mul(f.power(a, 3), c))),
                        add(sub(0, mul(k(27), mul(c, c))),
                            mul(k(18), mul(mul(a, b), c)))))
                delta = mul(k(16), discriminant)
                self.assertNotEqual(delta, 0)
                independent = f.div(f.power(c4, 3), delta) in {0, k(1728)}
                actual = special_j(f, curve["model"])
                self.assertEqual(actual, independent)
                flags.append(actual)
            counts[cohort] = sum(flags)
        self.assertEqual(counts, {"q5-n3": 6, "q7-n3": 8,
                                  "q11-n3": 4, "q3-n5": 4})


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Fixed F27 software checks for the prospective C7 instrument control."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from check_all_degree_collision_certificate import FIXED_FORMS, PATTERNS
from check_quotient_certificate import Field, trim
from c7_matched_random import (check_form, direct_incidence, factor_pattern,
                               sample_stratum, weighted_relations)
from c7_seed_replay import replay
from c7_seed_replay import _draw as independent_draw
from c7_matched_random import _coefficient as producer_draw
from independent_component_geometry import assess as assess_independent_geometry
from squareclass_relations import coefficient_bit


class C7MatchedRandomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-c7-fixture-")
        source = Path(__file__).with_name("join_certificate.rs")
        binary = Path(cls.scratch.name) / "join_certificate"
        subprocess.run(["rustc", "--edition=2021", str(source), "-o", str(binary)],
                       check=True, capture_output=True)
        cls.field_record = json.loads(subprocess.check_output(
            [str(binary), "f27-char3"]))["field"]
        cls.field = Field(cls.field_record)

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_all_fixed_branch_patterns_and_rank_instruments(self):
        for form, pattern in zip(FIXED_FORMS, PATTERNS):
            with self.subTest(pattern=pattern):
                self.assertEqual(factor_pattern(self.field, form), tuple(pattern))
                checked = check_form(self.field, form, self.field_record)
                self.assertEqual(checked["pattern"], pattern)
                self.assertEqual(checked["scalar_class"],
                                 coefficient_bit(self.field, trim(form)[-1]))
                forms = [form]
                for _ in range(1, self.field.n):
                    forms.append([self.field.power(v, self.field.p)
                                  for v in forms[-1]])
                weighted = weighted_relations(self.field, forms)
                incidence = direct_incidence(self.field, forms)
                self.assertEqual([weighted["geometric_rank"],
                                  weighted["arithmetic_rank"]], checked["rank_pair"])
                self.assertEqual(weighted["constant_nonsquare_relation"],
                                 incidence["constant_nonsquare_relation"])

    def test_fixture_only_sampling_path_and_instrument_discrepancy(self):
        form = FIXED_FORMS[4]
        scalar = coefficient_bit(self.field, trim(form)[-1])
        with patch("c7_matched_random._coefficient",
                   side_effect=lambda field, label, attempt, position: form[position]):
            record = sample_stratum(self.field_record, [4], scalar, count=1)
        self.assertEqual(record["status"], "control_complete")
        self.assertEqual(record["requested"], 1)
        self.assertEqual(record["attempted"], 1)
        self.assertEqual(record["selected"][0]["form"], form)
        with patch("c7_matched_random._coefficient",
                   side_effect=lambda field, label, attempt, position: form[position]):
            flipped = sample_stratum(self.field_record, [4], 1 - scalar, count=1)
        self.assertEqual(flipped["status"], "control_complete")
        self.assertEqual(flipped["scalar_flips"], 1)
        self.assertEqual(flipped["selected"][0]["check"]["scalar_class"], 1 - scalar)
        self.assertEqual(flipped["selected"][0]["check"]["pattern"], [4])
        original = weighted_relations
        def wrong(field, forms):
            result = original(field, forms)
            result["geometric_rank"] += 1
            return result
        with patch("c7_matched_random.weighted_relations", side_effect=wrong):
            with self.assertRaisesRegex(ValueError, "weighted-factor/incidence discrepancy"):
                check_form(self.field, form, self.field_record)
        def wrong_genus(record, forms):
            result = assess_independent_geometry(record, forms)
            result["geometric_component_genus"] += 1
            return result
        with patch("c7_matched_random.assess_independent_geometry",
                   side_effect=wrong_genus):
            with self.assertRaisesRegex(ValueError, "independent character-geometry discrepancy"):
                check_form(self.field, form, self.field_record)

    def test_malformed_quartic_rejected(self):
        with self.assertRaises(ValueError):
            factor_pattern(self.field, [1, 0, 0, 0, 0])
        with self.assertRaises(ValueError):
            check_form(self.field, [0, 0, 0, 0, 0], self.field_record)

    def test_independent_retained_seed_replay_and_tamper(self):
        # Both streams are held to a fixed existing software form; this test
        # does not take a randomized control sample before admission.
        form = FIXED_FORMS[4]
        scalar = coefficient_bit(self.field, trim(form)[-1])
        fixed = lambda field, label, attempt, position: form[position]
        with patch("c7_matched_random._coefficient", side_effect=fixed):
            record = sample_stratum(self.field_record, [4], scalar, count=1)
        with patch("c7_seed_replay._draw", side_effect=fixed):
            checked = replay(self.field_record, record)
            self.assertTrue(checked["valid"])
            self.assertEqual(checked["selected"], 1)
            for key, changed in (("seed", 0), ("attempted", 2),
                                 ("scalar_flips", 1)):
                tampered = dict(record)
                tampered[key] = changed
                with self.assertRaisesRegex(ValueError, "retained record differs"):
                    replay(self.field_record, tampered)
            tampered = json.loads(json.dumps(record))
            tampered["selected"][0]["form"][0] ^= 1
            with self.assertRaisesRegex(ValueError, "retained record differs"):
                replay(self.field_record, tampered)

    def test_counter_word_parity_without_control_sampling(self):
        label = ["fixed-prng-fixture", [4], 0]
        for attempt, position in ((0, 0), (1, 4), (4095, 2)):
            self.assertEqual(independent_draw(self.field, label, attempt, position),
                             producer_draw(self.field, label, attempt, position))


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Actual F27 source maps into checked conjugate radical generators."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from candidate_binding import CandidateBinder
from candidate_stage import join_path
from source_radical_binding import certify, certify_bound


class SourceRadicalBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-source-radical-")
        binary = Path(cls.scratch.name) / "join"
        subprocess.run(["rustc", "--edition=2021", str(Path(__file__).with_name(
            "join_certificate.rs")), "-o", str(binary)], check=True, capture_output=True)
        cls.joined = json.loads(subprocess.check_output(
            [binary, "f27-char3", "0", "6"]))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_source_generator_and_order_three_action(self):
        for row in self.joined["rows"]:
            result = certify(self.joined["field"], row["model"], row["target"],
                             row["matrix"], row["conjugates"])
            self.assertEqual(result["source_generator_square"], row["transformed_form"])
            self.assertEqual(result["source_map"]["source_form"], row["original_form"])
            self.assertEqual(result["status"],
                             "source_generator_and_order_n_action_checked; fixed_field_model_pending")
            self.assertEqual([entry["to"] for entry in result["action_on_generators"]],
                             [1, 2, 0])
            self.assertEqual(sum(entry["sign"] for entry in
                                 result["action_on_generators"]) % 2, 0)

    def test_wrong_source_or_conjugate_refused(self):
        row = self.joined["rows"][0]
        forms = copy.deepcopy(row["conjugates"])
        forms[0][0] = (forms[0][0]+1) % 27
        with self.assertRaisesRegex(ValueError, "conjugate 0 differs"):
            certify(self.joined["field"], row["model"], row["target"],
                    row["matrix"], forms)
        forms = copy.deepcopy(row["conjugates"])
        forms[1][0] = (forms[1][0]+1) % 27
        with self.assertRaisesRegex(ValueError, "conjugate 1 differs"):
            certify(self.joined["field"], row["model"], row["target"],
                    row["matrix"], forms)
        wrong_model = list(row["model"])
        wrong_model[-1] = (wrong_model[-1]+1) % 27
        with self.assertRaises(ValueError):
            certify(self.joined["field"], wrong_model, row["target"],
                    row["matrix"], row["conjugates"])

    def test_published_curve_t_ordinal_binding(self):
        binder = CandidateBinder("q5-n3", plan_path=join_path("q5-n3"))
        binding = binder.bind(0, 0)
        field = binder.field
        form = binding["quotient_form"]
        forms = [form]
        for _ in range(2):
            forms.append([field.power(value, field.p) for value in forms[-1]])
        result = certify_bound(binder, 0, 0, 0, [1, 0, 0, 1], forms)
        self.assertEqual(result["source_map"]["join_plan_sha256"], binder.plan_sha256)
        self.assertEqual(result["source_map"]["structure_ordinal"], 0)

    def test_non_exhibiting_solver_cannot_certify_inadmissibility(self):
        row = self.joined["rows"][0]
        with mock.patch("source_radical_binding.candidate_lift", return_value={
                "schema": "pext.radical-frobenius/v1",
                "status": "no_order_n_lift_for_coherent_relation_algebra"}):
            with self.assertRaisesRegex(ValueError, "source radical action absent"):
                certify(self.joined["field"], row["model"], row["target"],
                        row["matrix"], row["conjugates"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

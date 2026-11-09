"""Fixed published-source C6 transport and twisted-action software checks."""

import copy
import hashlib
import json
import unittest

from c6_coordinate_control import (check_all_slots, check_seeded, check_transport,
                                   seeded_matrix)
from candidate_binding import CandidateBinder
from candidate_stage import join_path
from check_quotient_certificate import Field
from check_structure_certificate import transform
from independent_component_geometry import assess


class C6CoordinateControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binder = CandidateBinder("q5-n3", plan_path=join_path("q5-n3"))
        cls.binding = cls.binder.bind(0, 0)

    def test_seeded_actual_curve_and_two_canonical_t_units(self):
        first = None
        for t_index in (0, 1):
            with self.subTest(t_index=t_index):
                result = check_seeded(self.binder, 0, t_index, 0, 0)
                self.assertEqual(result["seed"], 20261102)
                self.assertEqual(result["slot"], 0)
                self.assertEqual(result["sha256_blocks"],
                                 result["draw_index"] + 1)
                self.assertEqual(result["sha256_bytes_generated"],
                                 32 * result["sha256_blocks"])
                self.assertEqual(result["sample_bytes_examined"],
                                 8 * result["sha256_blocks"])
                self.assertTrue(result["invariant_equality"])
                self.assertEqual(result["base_invariants"],
                                 result["common_transport_invariants"])
                self.assertNotEqual(result["transport_matrix"][2], 0)
                field = Field(self.binding["field"])
                self.assertTrue(any(field.power(value, field.p) != value
                                    for value in result["transport_matrix"]))
                if t_index == 0:
                    first = result
        binding = self.binder.bind(0, 0)
        draw = seeded_matrix(binding["field"], binding, 0, 0)
        self.assertEqual(draw["matrix"], first["transport_matrix"])
        identity = {key: binding[key] for key in (
            "cohort", "class_index", "T_index", "join_plan_sha256",
            "input_sha256", "manifest_sha256", "structure_offset")}
        payload = json.dumps(["pext-c6-coordinate/v1", 20261102, identity,
                              0, 0, draw["draw_index"]], sort_keys=True,
                             separators=(",", ":")).encode()
        self.assertEqual(draw["counter_sha256"],
                         hashlib.sha256(payload).hexdigest())
        words = [int.from_bytes(bytes.fromhex(draw["counter_sha256"])[2*i:2*(i+1)],
                                "little") for i in range(4)]
        size = Field(binding["field"]).size
        self.assertTrue(all(word < 65536 - (65536 % size)
                            for word in words))

    def test_common_transport_invariant_and_naive_orbit_counterexample(self):
        matrix = [1, 0, 5, 1]
        result = check_transport(self.binder, 0, 0, 0, matrix)
        self.assertEqual(result["base_invariants"],
                         result["common_transport_invariants"])
        field = Field(self.binding["field"])
        moved = transform(field, self.binding["quotient_form"], matrix)
        naive = [moved]
        for _ in range(field.n - 1):
            naive.append([field.power(value, field.p) for value in naive[-1]])
        naive_geometry = assess(self.binding["field"], naive)
        self.assertEqual((result["base_invariants"]["geometric_rank"],
                          result["base_invariants"]["geometric_component_genus"]),
                         (1, 1))
        self.assertEqual((naive_geometry["geometric_rank"],
                          naive_geometry["geometric_component_genus"]),
                         (3, 17))

    def test_all_sixteen_frozen_slots_on_one_published_unit(self):
        batch = check_all_slots(self.binder, 0, 0, 0)
        self.assertEqual(batch["slot_count"], 16)
        self.assertEqual([row["slot"] for row in batch["rows"]],
                         list(range(16)))
        self.assertEqual(len({tuple(row["transport_matrix"])
                              for row in batch["rows"]}), 16)
        self.assertTrue(all(row["base_invariants"]
                            == row["common_transport_invariants"]
                            for row in batch["rows"]))

    def test_full_scalar_composition_and_twist_tampering(self):
        result = check_transport(self.binder, 0, 0, 1000, [1, 1, 5, 1])
        self.assertEqual(result["binary_form_scalar_factor"], 6)
        self.assertEqual(result["ordinate_scalar_factor"], 51)
        self.assertEqual(result["base_invariants"],
                         result["common_transport_invariants"])
        field = Field(self.binding["field"])
        form = transform(field, self.binding["quotient_form"],
                         result["base_matrix"])
        base = [form]
        for _ in range(field.n - 1):
            base.append([field.power(value, field.p) for value in base[-1]])
        common = [transform(field, item, result["transport_matrix"])
                  for item in base]
        bad_twist = copy.deepcopy(result["twisted_frobenius_matrix"])
        bad_twist[2] = field.add(bad_twist[2], 1)
        with self.assertRaisesRegex(ValueError, "invalid twisted"):
            assess(self.binding["field"], common,
                   twisted_frobenius_matrix=bad_twist)
        with self.assertRaisesRegex(ValueError, "invalid twisted"):
            changed = copy.deepcopy(common)
            changed[1][0] = field.add(changed[1][0], 1)
            assess(self.binding["field"], changed,
                   twisted_frobenius_matrix=result[
                       "twisted_frobenius_matrix"])
        with self.assertRaisesRegex(ValueError, "singular"):
            check_transport(self.binder, 0, 0, 0, [1, 0, 0, 0])


if __name__ == "__main__":
    unittest.main(verbosity=2)

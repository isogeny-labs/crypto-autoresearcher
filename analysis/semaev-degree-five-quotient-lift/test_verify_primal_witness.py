#!/usr/bin/env python3
"""Independent checker controls: legal closure, degree refusal and tampering."""

import copy
import hashlib
import struct
import tempfile
import unittest
from pathlib import Path

from seed_kernel import SeedKernel
from verify_primal_witness import check, named_system, system_digest


SYSTEM = [[1, 2], [1], [0, 3]]  # x0+x1, x0, 1+x0*x1: no Boolean zero
DIGEST = system_digest(2, SYSTEM)
WITNESS = {
    "schema": "semaev.boolean-primal-witness/v1",
    "variables": 2,
    "degree": 2,
    "generators": SYSTEM,
    "steps": [
        {"op": "input", "index": 0},
        {"op": "input", "index": 1},
        {"op": "xor", "refs": [0, 1]},  # x1
        {"op": "mul", "ref": 2, "variable": 0},  # x0*x1
        {"op": "input", "index": 2},
        {"op": "xor", "refs": [3, 4]},  # 1
    ],
    "terminal": 5,
}


class WitnessChecks(unittest.TestCase):
    def test_named_n47_input_binding(self):
        plan = Path(__file__).resolve().parent / "rank-check/n47-rand00-plan-002.json"
        nvars, generators = named_system(
            plan,
            "178bec5c09a4645274d8ef5806a3ebdd5681827e14258dd07cfc2b84fc331abd",
            "b6e28168091986b3cb04790f51889723db0ec5838633767bb80a6dc4ac97bd70")
        self.assertEqual((nvars, len(generators), sum(map(len, generators))), (48, 47, 14443))
        self.assertEqual(system_digest(nvars, generators),
                         "f9ab99aa260c60f4a28758488e363d7d400f4a9c7f2e8537fd572a974f2d5084")
        with self.assertRaisesRegex(ValueError, "descent-source digest mismatch"):
            named_system(plan,
                         "178bec5c09a4645274d8ef5806a3ebdd5681827e14258dd07cfc2b84fc331abd",
                         "0" * 64)

    def test_legal_refutation(self):
        result = check(WITNESS, DIGEST)
        self.assertEqual((result["status"], result["degree"], result["steps"]),
                         ("valid_primal_refutation", 2, 6))

    def test_wrong_system_rejected(self):
        mutated = copy.deepcopy(WITNESS)
        mutated["generators"][1] = [2]
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            check(mutated, DIGEST)

    def test_illegal_degree_rejected(self):
        mutated = copy.deepcopy(WITNESS)
        mutated["degree"] = 1
        with self.assertRaisesRegex(ValueError, "degree bound"):
            check(mutated, DIGEST)

    def test_illegal_multiplication_rejected(self):
        mutated = copy.deepcopy(WITNESS)
        mutated["steps"] = [
            {"op": "input", "index": 2},
            {"op": "mul", "ref": 0, "variable": 0},
        ]
        mutated["terminal"] = 1
        with self.assertRaisesRegex(ValueError, "degree minus one"):
            check(mutated, DIGEST)

    def test_wrong_terminal_rejected(self):
        mutated = copy.deepcopy(WITNESS)
        mutated["steps"][-1]["refs"] = [2, 4]
        with self.assertRaisesRegex(ValueError, "not the constant one"):
            check(mutated, DIGEST)

    def test_forward_reference_rejected(self):
        mutated = copy.deepcopy(WITNESS)
        mutated["steps"][2]["refs"] = [0, 3]
        with self.assertRaisesRegex(ValueError, "invalid xor reference"):
            check(mutated, DIGEST)

    def test_boolean_product_cancellation(self):
        mutated = copy.deepcopy(WITNESS)
        mutated["variables"] = 3
        mutated["degree"] = 3
        mutated["generators"].append([1, 3])
        mutated["steps"][0] = {"op": "input", "index": 3}
        mutated["steps"][1] = {"op": "mul", "ref": 0, "variable": 1}
        mutated["steps"] = mutated["steps"][:2]
        mutated["terminal"] = 1
        with self.assertRaisesRegex(ValueError, "not the constant one"):
            check(mutated, system_digest(3, mutated["generators"]))

    def test_checked_kernel_premise(self):
        # B_1 monomials x0,x1,1; pi(x0)=pi(x1)=0, pi(1)=1.
        seed_bytes = struct.pack("<4q", 2, 1, 3, 1)
        seed_bytes += struct.pack("<3Q", 1, 2, 0)
        seed_bytes += struct.pack("<3Q", 0, 0, 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "seed.bin"
            path.write_bytes(seed_bytes)
            digest = hashlib.sha256(seed_bytes).hexdigest()
            witness = copy.deepcopy(WITNESS)
            witness["steps"] = [
                {"op": "kernel", "terms": [2]},
                {"op": "mul", "ref": 0, "variable": 0},
                {"op": "input", "index": 2},
                {"op": "xor", "refs": [1, 2]},
            ]
            witness["terminal"] = 3
            with self.assertRaisesRegex(ValueError, "requires a checked D4 seed"):
                check(witness, DIGEST)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                SeedKernel(path, "0" * 64)
            seed = SeedKernel(path, digest)
            try:
                result = check(witness, DIGEST, seed)
                self.assertEqual((result["status"], result["kernel_leaves"]),
                                 ("valid_given_accepted_seed_and_kernel_equality", 1))
                witness["steps"][0]["terms"] = [0]
                with self.assertRaisesRegex(ValueError, "not in the D4 quotient kernel"):
                    check(witness, DIGEST, seed)
            finally:
                seed.close()


if __name__ == "__main__":
    unittest.main()

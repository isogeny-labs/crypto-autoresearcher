"""Fixed F27 per-form unit replay and mutation rejection."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_candidate_unit import verify


class CheckedCandidateUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-candidate-unit-")
        base = Path(__file__).parent
        binaries = []
        for source in ("candidate_unit.rs", "join_certificate.rs"):
            binary = Path(cls.scratch.name) / source.removesuffix(".rs")
            subprocess.run(["rustc", "--edition=2021", str(base / source), "-o", str(binary)],
                           check=True, capture_output=True)
            binaries.append(binary)
        cls.binary = binaries[0]
        cls.joined = json.loads(subprocess.check_output([binaries[1], "f27-char3"]))
        cls.forms = [[1, 0, 1, 1, 0], [1, 1, 1, 0, 1]]
        cls.units = []
        for form in cls.forms:
            args = [str(cls.binary), "3", "3", ",".join(map(str, form)),
                    "27", "819", "3276", "1000", "1000", "819"]
            cls.units.append(json.loads(subprocess.check_output(args)))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_fixed_units_and_mutations(self):
        results = [verify(unit, self.joined, form)
                   for unit, form in zip(self.units, self.forms)]
        self.assertEqual([result["exceptional"] for result in results], [279, 1])
        self.assertEqual([result["generic_intervals"] for result in results], [109, 1])
        self.assertTrue(all(unit["candidate_order_aa"] ==
                            "reverse-cocycle-build-representatives-buckets-and-roots/v1"
                            for unit in self.units))
        missing_aa = copy.deepcopy(self.units[1])
        missing_aa.pop("candidate_order_aa")
        with self.assertRaisesRegex(ValueError, "candidate unit schema or order"):
            verify(missing_aa, self.joined, self.forms[1])
        missing = copy.deepcopy(self.units[0])
        missing["rows"].pop()
        with self.assertRaisesRegex(ValueError, "row cardinality"):
            verify(missing, self.joined, self.forms[0])
        wrong_matrix = copy.deepcopy(self.units[0])
        other = (wrong_matrix["rows"][0][0] + 1) % 819
        wrong_matrix["rows"][0][1] = self.joined["rows"][other]["matrix"]
        with self.assertRaisesRegex(ValueError, "matrix ordinal mismatch"):
            verify(wrong_matrix, self.joined, self.forms[0])
        broken_interval = copy.deepcopy(self.units[0])
        broken_interval["generic_intervals"][0][1] += 1
        with self.assertRaisesRegex(ValueError, "generic complement coverage"):
            verify(broken_interval, self.joined, self.forms[0])
        wrong_genus = copy.deepcopy(self.units[0])
        wrong_genus["rows"][0][4] += 1
        with self.assertRaisesRegex(ValueError, "candidate geometry mismatch"):
            verify(wrong_genus, self.joined, self.forms[0])
        wrong_field = copy.deepcopy(self.units[0])
        wrong_field["field"]["modulus"][0] ^= 1
        with self.assertRaisesRegex(ValueError, "candidate field identity"):
            verify(wrong_field, self.joined, self.forms[0])
        with self.assertRaisesRegex(ValueError, "candidate expected form"):
            verify(self.units[0], self.joined, self.forms[1])
        rejected = subprocess.run([str(self.binary), "3", "3", "1,0,1,1,0",
                                   "27", "819", "3276", "1000", "1000", "0"],
                                  capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("candidate limit exceeded", rejected.stderr)
        print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)

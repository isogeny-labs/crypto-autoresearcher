"""Fixed software replay and omission/extra-index rejection."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_rational_collision_certificate import verify
from check_compact_class_inputs import BasisField
from generic_disjoint import classify


class RationalCollisionCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-rational-collision-")
        base = Path(__file__).parent
        binaries = []
        for source in ("rational_collision_certificate.rs", "join_certificate.rs"):
            binary = Path(cls.scratch.name) / source.removesuffix(".rs")
            subprocess.run(["rustc", "--edition=2021", str(base / source), "-o", str(binary)],
                           check=True, capture_output=True)
            binaries.append(binary)
        cls.certificate = json.loads(subprocess.check_output([binaries[0]]))
        cls.joined = json.loads(subprocess.check_output([binaries[1], "f27-char3"]))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_full_fixed_fixture_and_mutations(self):
        result = verify(self.certificate, self.joined)
        self.assertEqual(result["targets"],
                         [{"coset_index": 0, "rational_roots": 2, "candidate_indices": 273},
                          {"coset_index": 1, "rational_roots": 0, "candidate_indices": 0}])
        field = BasisField(self.joined["field"])
        residual = []
        for target in self.certificate["rows"]:
            coset_index = target["coset_index"]
            generated = set(target["structure_indices"])
            exceptional = {row["structure_index"] for row in self.joined["rows"]
                           if row["coset_index"] == coset_index
                           and classify(field, row["conjugates"])["classification"] == "exceptional"}
            self.assertLessEqual(generated, exceptional)
            residual.append(len(exceptional-generated))
        self.assertEqual(residual, [6, 1])
        missing = json.loads(json.dumps(self.certificate))
        missing["rows"][0]["structure_indices"].pop()
        with self.assertRaisesRegex(ValueError, "candidate set mismatch"):
            verify(missing, self.joined)
        extra = json.loads(json.dumps(self.certificate))
        unused = next(i for i in range(819) if i not in extra["rows"][0]["structure_indices"])
        extra["rows"][0]["structure_indices"].append(unused)
        extra["rows"][0]["structure_indices"].sort()
        with self.assertRaisesRegex(ValueError, "candidate set mismatch"):
            verify(extra, self.joined)
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)

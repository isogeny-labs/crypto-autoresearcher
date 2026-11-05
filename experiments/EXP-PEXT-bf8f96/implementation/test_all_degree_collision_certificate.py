"""Independent all-pattern F27 replay with omission and malformed-root controls."""

import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_all_degree_collision_certificate import verify


class AllDegreeCollisionCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-all-degree-")
        base = Path(__file__).parent
        binaries = []
        for source in ("all_degree_collision_certificate.rs", "join_certificate.rs"):
            binary = Path(cls.scratch.name) / source.removesuffix(".rs")
            subprocess.run(["rustc", "--edition=2021", str(base / source), "-o", str(binary)],
                           check=True, capture_output=True)
            binaries.append(binary)
        cls.certificate = json.loads(subprocess.check_output([binaries[0]]))
        cls.joined = json.loads(subprocess.check_output([binaries[1], "f27-char3"]))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_full_fixture_and_mutations(self):
        result = verify(self.certificate, self.joined)
        self.assertEqual([row["exceptional"] for row in result["targets"]],
                         [590, 279, 117, 20, 1, 279, 1])
        self.assertEqual([row["pattern"] for row in result["targets"][:5]],
                         [[1, 1, 1, 1], [1, 1, 2], [1, 3], [2, 2], [4]])
        missing = copy.deepcopy(self.certificate)
        missing["rows"][3]["nonrational_indices"].pop()
        with self.assertRaisesRegex(ValueError, "nonrational_indices candidate set mismatch"):
            verify(missing, self.joined)
        extra = copy.deepcopy(self.certificate)
        unused = next(i for i in range(819) if i not in extra["rows"][4]["union_indices"])
        extra["rows"][4]["union_indices"].append(unused)
        extra["rows"][4]["union_indices"].sort()
        with self.assertRaisesRegex(ValueError, "union_indices candidate set mismatch"):
            verify(extra, self.joined)
        broken_root = copy.deepcopy(self.certificate)
        broken_root["rows"][4]["roots"][0] = [0] * 4
        with self.assertRaisesRegex(ValueError, "root off quartic"):
            verify(broken_root, self.joined)
        broken_factor = copy.deepcopy(self.certificate)
        broken_factor["rows"][3]["factors"][0][0] = 0
        with self.assertRaisesRegex(ValueError, "factor"):
            verify(broken_factor, self.joined)
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)

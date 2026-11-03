"""Fixed F27 generic-support decomposition against full square relations."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_compact_class_inputs import BasisField
from check_quotient_certificate import square_relations
from generic_disjoint import classify


class GenericDisjointTests(unittest.TestCase):
    def test_f27_complete_fixed_structure_control(self):
        with tempfile.TemporaryDirectory(prefix="pext-disjoint-control-") as scratch:
            binary = str(Path(scratch) / "join")
            subprocess.run(["rustc", "--edition=2021", "-O",
                            str(Path(__file__).with_name("join_certificate.rs")),
                            "-o", binary], check=True)
            record = json.loads(subprocess.check_output([binary, "f27-char3"]))
        field = BasisField(record["field"])
        counts = {"generic-disjoint": 0, "exceptional": 0}
        for row in record["rows"]:
            forms = row["conjugates"]
            result = classify(field, forms)
            counts[result["classification"]] += 1
            if result["classification"] == "generic-disjoint":
                self.assertEqual(square_relations(field, forms), [[0, True]])
                self.assertEqual(result["geometric_genus"], 17)
            else:
                self.assertTrue(result["overlaps"])
        self.assertEqual(sum(counts.values()), record["total"])
        self.assertGreater(counts["generic-disjoint"], 0)
        self.assertGreater(counts["exceptional"], 0)
        print(json.dumps(counts, sort_keys=True))

    def test_repeated_and_infinity_cases(self):
        with tempfile.TemporaryDirectory(prefix="pext-disjoint-control-") as scratch:
            binary = str(Path(scratch) / "join")
            subprocess.run(["rustc", "--edition=2021", "-O",
                            str(Path(__file__).with_name("join_certificate.rs")),
                            "-o", binary], check=True)
            record = json.loads(subprocess.check_output([binary, "f27-char3", "0", "1"]))
        field = BasisField(record["field"])
        form = record["rows"][0]["original_form"]
        self.assertEqual(classify(field, [form]*3)["classification"], "exceptional")
        with self.assertRaises(ValueError):
            classify(field, [[0, 0, 1, 0, 1]]*3)
        broken = [list(item) for item in record["rows"][0]["conjugates"]]
        broken[1][0] = field.add(broken[1][0], 1)
        with self.assertRaises(ValueError):
            classify(field, broken)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Cross-check Python production plan indexing against the Rust join producer."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from join_plan import plan_for_models


class JoinPlanTests(unittest.TestCase):
    def test_fixed_control_offsets_match_rust(self):
        with tempfile.TemporaryDirectory(prefix="pext-plan-control-") as scratch:
            binary = str(Path(scratch) / "join")
            subprocess.run(["rustc", "--edition=2021", "-O",
                            str(Path(__file__).with_name("join_certificate.rs")),
                            "-o", binary], check=True)
            for fixture in ("f3-classes", "f5-classes", "f27-char3"):
                with self.subTest(fixture=fixture):
                    rust = json.loads(subprocess.check_output([binary, fixture]))
                    models = [entry["model"] for entry in rust["classes"]]
                    f = rust["field"]
                    plan = plan_for_models(f, models, fixture, "fixed-control", "fixed-control",
                                           f["prime"], f["degree"], len(models))
                    self.assertEqual(plan["classes"], rust["classes"])
                    self.assertEqual(plan["structures_per_T"], rust["structures"])
                    self.assertEqual(plan["total_rows"], rust["total"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

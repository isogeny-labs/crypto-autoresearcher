"""Exercise real supervisor admission against the preserved PFDR failed envelope.

No scientific execution; fixtures are copied into temporary directories. Requires
materializing EXP-PFDR-7c7c95 and RUN-PFDR-1e5d2b in sparse checkouts.
"""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml
import experiment_execution as execution

ROOT = Path(__file__).resolve().parents[1]
PLAN = "experiments/EXP-PFDR-7c7c95/trial-plan.json"
RUN = ROOT / "experiments/EXP-PFDR-7c7c95/runs/RUN-PFDR-1e5d2b"


class PreservedPFDRAdmission(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        for name in ("manifest.yaml", "environment.json", "raw-result.json", "command.txt", "stdout.log", "stderr.log",
                     "check.stdout.log", "check.stderr.log"):
            shutil.copyfile(RUN / name, self.directory / name)
        self.plan = json.loads((ROOT / PLAN).read_text())
        self.launch = json.loads((RUN / "launch.json").read_text())
        self.receipt = json.loads((RUN / "execution-receipt.json").read_text())
        self.trial = next(t for t in self.plan["trials"] if t["id"] == "pilot")
        self.document = yaml.safe_load((self.directory / "manifest.yaml").read_text())
        # Replay admission in another Python environment. The historical driver
        # named its ephemeral uv interpreter; use the equivalent frozen argv in
        # this temporary fixture so current sys.executable is not a false defect.
        self.document["run"]["code"]["command"] = self.launch["argv"]

    def admit(self):
        (self.directory / "manifest.yaml").write_text(yaml.safe_dump(self.document))
        return execution.complete_manifest(
            self.directory, self.plan, PLAN, self.launch["plan_sha256"], self.trial,
            self.launch["authority"], self.launch["argv"], self.launch["check_argv"],
            self.receipt["started_at"], self.receipt["finished_at"])

    def corrected_fixture(self):
        # A prospective correction in memory only: historical records stay sealed.
        self.plan["hypothesis_id"] = self.document["run"]["hypothesis_id"]
        old = self.document["run"]["inputs"]
        self.document["run"]["inputs"] = {"derived": old["parameters"]}

    def test_original_failure_is_reproduced(self):
        with self.assertRaisesRegex(execution.EnvelopeRefused, "names no hypothesis"):
            self.admit()

    def test_hypothesis_only_fix_is_insufficient(self):
        self.plan["hypothesis_id"] = self.document["run"]["hypothesis_id"]
        with self.assertRaisesRegex(execution.EnvelopeRefused, "declares no (curve_id|seed|parameters)"):
            self.admit()

    def test_null_inputs_removal_still_leaves_undeclared_parameters(self):
        self.plan["hypothesis_id"] = self.document["run"]["hypothesis_id"]
        for key in ("curve_id", "seed"):
            del self.document["run"]["inputs"][key]
        with self.assertRaisesRegex(execution.EnvelopeRefused, "declares no parameters"):
            self.admit()

    def test_prospective_envelope_passes_actual_schema_and_fact_checks(self):
        self.corrected_fixture()
        self.admit()
        self.assertEqual(execution.manifest_schema_errors(self.directory / "manifest.yaml"), [])

    def test_mutations_are_refused_before_publication(self):
        self.corrected_fixture()
        base = copy.deepcopy(self.document)
        mutations = [
            (("id",), "RUN-PFDR-ffffff"),
            (("run_id",), "RUN-PFDR-ffffff"),
            (("experiment_id",), "EXP-PFDR-ffffff"),
            (("hypothesis_id",), "H-PFDR-ffffff"),
            (("task_id",), "TASK-20261109-ffffff"),
            (("trial_id",), "other"),
            (("approved_by",), "DEC-20261109-ffffff"),
            (("code", "commit"), "f" * 40),
            (("code", "command"), ["false"]),
            (("code", "check_command"), ["false"]),
            (("inputs", "seed"), None),
            (("inputs", "curve_id"), None),
            (("inputs", "parameters"), {"unexpected": 1}),
            (("inputs", "trial_plan"), "other.json"),
            (("inputs", "plan_sha256"), "f" * 64),
            (("inputs", "specification_sha256"), "f" * 64),
            (("environment", "source_sha256"), {
                "experiments/EXP-PFDR-7c7c95/implementation/run.py": "f" * 64}),
            (("timing", "started_at"), "2000-01-01T00:00:00Z"),
            (("timing", "wall_seconds"), 100000),
        ]
        for keys, value in mutations:
            with self.subTest(field=".".join(keys)):
                self.document = copy.deepcopy(base)
                block = self.document["run"]
                for key in keys[:-1]:
                    block = block.setdefault(key, {})
                block[keys[-1]] = value
                before = yaml.safe_dump(self.document)
                with self.assertRaises(execution.EnvelopeRefused):
                    self.admit()
                self.assertEqual((self.directory / "manifest.yaml").read_text(), before)


if __name__ == "__main__":
    unittest.main()

"""Retained synthetic C2 fixture and independent analyze-stage readback."""

import json
from pathlib import Path
import tempfile
import unittest

from c2_control_stage import (ARTIFACTS, SOURCES, check_control,
                              run_control, sha256)
from input_manifest import ROOT


class C2ControlStageTests(unittest.TestCase):
    def test_write_once_raw_replay_and_tamper_refusal(self):
        sources = {relative: sha256(ROOT / relative) for relative in SOURCES}
        with tempfile.TemporaryDirectory(prefix="pext-c2-stage-") as scratch:
            run_dir = Path(scratch)
            result = run_control(run_dir, sources, "a" * 64, "RUN-C2-software")
            self.assertEqual(result["status"], "fixed_software_fixture_checked")
            self.assertEqual(set(ARTIFACTS), {path.name for path in run_dir.iterdir()})
            self.assertTrue(check_control(run_dir, sources, "a" * 64,
                                          "RUN-C2-software")["valid"])
            with self.assertRaises(FileExistsError):
                run_control(run_dir, sources, "a" * 64, "RUN-C2-software")
            with self.assertRaisesRegex(ValueError, "summary differs"):
                check_control(run_dir, sources, "a" * 64, "RUN-wrong")
            changed_sources = dict(sources)
            changed_sources[next(iter(SOURCES))] = "0" * 64
            with self.assertRaisesRegex(ValueError, "source differs"):
                check_control(run_dir, changed_sources, "a" * 64,
                              "RUN-C2-software")
            summary = run_dir / "c2-control.json"
            saved_summary = summary.read_bytes()
            wrong_compiler = json.loads(saved_summary)
            wrong_compiler["compiler"] = "/bin/true"
            summary.write_text(json.dumps(wrong_compiler))
            with self.assertRaisesRegex(ValueError, "compiler differs"):
                check_control(run_dir, sources, "a" * 64,
                              "RUN-C2-software")
            summary.write_bytes(saved_summary)
            partial = run_dir / "c2-join.partial"
            partial.symlink_to(run_dir / "missing")
            with self.assertRaisesRegex(ValueError, "incomplete build"):
                check_control(run_dir, sources, "a" * 64,
                              "RUN-C2-software")
            partial.unlink()
            raw = run_dir / "c2-all-degree.json"
            certificate = json.loads(raw.read_bytes())
            certificate["rows"][3]["cross_ratio_orbit"][0][0] = 4
            raw.write_text(json.dumps(certificate))
            with self.assertRaisesRegex(ValueError, "cross-ratio orbit"):
                check_control(run_dir, sources, "a" * 64, "RUN-C2-software")


if __name__ == "__main__":
    unittest.main(verbosity=2)

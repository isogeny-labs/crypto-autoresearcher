"""Fixed wiring tests; C6/C7 engines are mocked and no control is sampled."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import c67_control_producer as producer
import c67_run_custody as custody
from test_c67_run_custody import fixture_admission


class BinderFixture:
    def __init__(self, cohort, plan_path):
        self.plan_sha256 = next(row["join_plan_sha256"] for row in
                                fixture_admission()["records"] if row["cohort"] == cohort)
        self.plan = {"field": {"fixed": "software-fixture"}}


class C67ProducerTests(unittest.TestCase):
    def test_exact_order_existing_stage_and_independent_check(self):
        admission = fixture_admission()
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            calls = []
            def write(plan, directory, stage, path, payload):
                calls.append(path)
                return {"path": path, "sha256": "fixed"}
            sealed = {"coverage_complete": True}
            checked = {"status": "checked_all_controls", "coverage_complete": True}
            with patch.object(producer, "_preflight", return_value=(root, admission)), \
                 patch.object(custody, "prepare", return_value=admission), \
                 patch.object(producer, "CandidateBinder", side_effect=BinderFixture), \
                 patch.object(producer, "check_all_slots", return_value={"fixed": "C6"}) as c6, \
                 patch.object(producer, "sample_stratum", return_value={"fixed": "C7"}) as c7, \
                 patch.object(custody, "write_result", side_effect=write), \
                 patch.object(custody, "readback", return_value=sealed), \
                 patch.object(producer.independent, "check", return_value=checked) as replay:
                result = producer.run_controls("fixture-plan", root, "n3ext")
            self.assertEqual(calls, [row["path"] for row in admission["records"]])
            self.assertEqual(c6.call_count, 1)
            self.assertEqual(c7.call_count, 2)
            replay.assert_called_once_with("fixture-plan", root, "n3ext")
            self.assertEqual(result["status"], "checked_all_controls")
            self.assertEqual(len(result["written"]), 3)

    def test_refuses_changed_admission_and_preserves_partial_failure(self):
        admission = fixture_admission()
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            with patch.object(producer, "_preflight", return_value=(root, admission)), \
                 patch.object(custody, "prepare", return_value={**admission, "run_id": "other"}), \
                 patch.object(custody, "write_result") as writer:
                with self.assertRaisesRegex(ValueError, "admission changed"):
                    producer.run_controls("fixture-plan", root, "n3ext")
                writer.assert_not_called()
            writes = []
            def fail_second(plan, directory, stage, path, payload):
                writes.append(path)
                if len(writes) == 2:
                    raise ValueError("fixed second write failure")
                return {"path": path}
            with patch.object(producer, "_preflight", return_value=(root, admission)), \
                 patch.object(custody, "prepare", return_value=admission), \
                 patch.object(producer, "CandidateBinder", side_effect=BinderFixture), \
                 patch.object(producer, "check_all_slots", return_value={"fixed": "C6"}), \
                 patch.object(producer, "sample_stratum", return_value={"fixed": "C7"}), \
                 patch.object(custody, "write_result", side_effect=fail_second), \
                 patch.object(custody, "readback") as seal:
                with self.assertRaisesRegex(ValueError, "fixed second write failure"):
                    producer.run_controls("fixture-plan", root, "n3ext")
                seal.assert_not_called()
            self.assertEqual(writes, [row["path"] for row in admission["records"][:2]])

    def test_future_plan_binds_producer_and_replay_sources(self):
        admission = fixture_admission()
        hashes = {relative: custody.digest(custody._regular(producer.ROOT / relative))
                  for relative in producer.independent.SOURCES}
        hashes[producer.SOURCE] = custody.digest(custody._regular(producer.ROOT / producer.SOURCE))
        producer_hash = hashes[producer.SOURCE]
        plan = {"source_sha256": hashes,
                "trials": [{"id": "n3ext", "artifacts": [producer.independent.CHECK]}]}
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            with patch.object(custody, "_preflight", return_value=(root, admission)), \
                 patch("experiment_execution.load_plan", return_value=plan):
                producer._preflight("fixture-plan", root, "n3ext")
                plan["source_sha256"][producer.SOURCE] = "0" * 64
                with self.assertRaisesRegex(ValueError, "producer source differs"):
                    producer._preflight("fixture-plan", root, "n3ext")
                plan["source_sha256"][producer.SOURCE] = producer_hash
                plan["trials"][0]["artifacts"] = []
                with self.assertRaisesRegex(ValueError, "independent check absent"):
                    producer._preflight("fixture-plan", root, "n3ext")


if __name__ == "__main__":
    unittest.main(verbosity=2)

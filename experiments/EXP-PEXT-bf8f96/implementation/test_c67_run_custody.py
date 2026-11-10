"""Fixed custody fixtures only: no C6 computation, C7 draws or cohort trials."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import c67_run_custody as custody

sys.path.insert(0, str(custody.ROOT / "tools"))
import experiment_execution


def fixture_admission():
    schedule = json.loads((custody.ROOT / custody.SCHEDULE).read_bytes())
    # Use one real published stratum only as a software fixture.
    record = custody.expected_records(schedule, "n3ext")[:3]
    return {"schema": "pext.c67-run-custody/v1", "experiment": custody.EXP,
            "status": "prospective_custody_only; control_execution_pending",
            "stage": "n3ext", "run_id": "RUN-fixed-fixture", "plan_sha256": "a" * 64,
            "schedule_sha256": "b" * 64, "records": record}


def fixture_payload(record):
    selection = record["selection"]
    if record["control"] == "C6":
        identity = {key: selection[key] for key in (
            "class_index", "T_index", "structure_ordinal", "seed")}
        identity.update({"cohort": record["cohort"],
                         "join_plan_sha256": record["join_plan_sha256"]})
        return {"schema": "pext.c6-coordinate-control-batch/v1", **identity,
                "draw_cap": 4096, "slot_count": 16,
                "rows": [{**identity, "slot": slot,
                          "schema": "pext.c6-coordinate-control/v1",
                          "transport_matrix": [1, slot, 1, 0],
                          "base_invariants": {"fixture_only": True},
                          "common_transport_invariants": {"fixture_only": True},
                          "binding_sha256": selection["binding_sha256"]} for slot in range(16)]}
    return {"schema": "pext.c7-matched-random/v1", "seed": selection["seed"],
            "field_sha256": record["field_sha256"], "pattern": record["pattern"],
            "scalar_class": selection["scalar_class"], "requested": 16, "draw_cap": 4096,
            "attempted": 16, "selected": [{"draw": draw, "form": [draw, 0, 0, 0, 1],
                                           "check": {"pattern": record["pattern"],
                                                     "scalar_class": selection["scalar_class"]}}
                                          for draw in range(16)],
            "status": "control_complete"}


def fixture_results(root, admission):
    (root / custody.ADMISSION).write_bytes(custody.canonical(admission))
    (root / "c67-results").mkdir()
    for record in admission["records"]:
        envelope = {"schema": "pext.c67-run-result/v1",
                    **{key: admission[key] for key in (
                        "experiment", "stage", "run_id", "plan_sha256", "schedule_sha256")},
                    "admission_sha256": custody.digest(custody.canonical(admission)),
                    "record": record, "payload": fixture_payload(record)}
        (root / record["path"]).write_bytes(custody.canonical(envelope))


class C67RunCustodyTests(unittest.TestCase):
    def test_retained_byte_cap_refuses_oversized_input_and_output(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "oversized.json"
            with patch.object(custody, "MAX_CONTROL_BYTES", 4):
                with self.assertRaisesRegex(ValueError, "output exceeds byte cap"):
                    custody._write_once(path, b"12345")
                self.assertFalse(path.exists())
                path.write_bytes(b"12345")
                with self.assertRaisesRegex(ValueError, "retained file exceeds byte cap"):
                    custody._regular(path)

    def test_published_coverage_stays_within_existing_three_census_runs(self):
        schedule = json.loads((custody.ROOT / custody.SCHEDULE).read_bytes())
        records = [custody.expected_records(schedule, stage) for stage in custody.COHORTS]
        self.assertEqual([len(rows) for rows in records], [30, 15, 15])
        self.assertEqual(sum(r["control"] == "C6" for rows in records for r in rows), 20)
        self.assertEqual(sum(r["control"] == "C7" for rows in records for r in rows), 40)
        for stage in ("regression", "orbits", "analyze", "seventh-run"):
            with self.assertRaisesRegex(ValueError, "existing census"):
                custody.expected_records(schedule, stage)
        for mutate in (lambda s: s.update(C7_requested_forms=639),
                       lambda s: s["cohorts"][0]["strata"][0]["C7"][0].update(samples=15),
                       lambda s: s["cohorts"][0]["strata"].append(s["cohorts"][0]["strata"][0])):
            changed = copy.deepcopy(schedule)
            mutate(changed)
            with self.assertRaises(ValueError):
                custody.expected_records(changed, "n3core")

    def test_prospective_prepare_is_exclusive_and_rejects_existing_data(self):
        admission = fixture_admission()
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            with patch.object(custody, "_preflight", return_value=(root, admission)):
                custody.prepare("fixture-plan", root, "n3ext")
                self.assertTrue((root / "c67-results").is_dir())
                with self.assertRaises((FileExistsError, ValueError)):
                    custody.prepare("fixture-plan", root, "n3ext")
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            (root / "c67-results").mkdir()
            with patch.object(custody, "_preflight", return_value=(root, admission)):
                with self.assertRaisesRegex(ValueError, "before prospective custody"):
                    custody.prepare("fixture-plan", root, "n3ext")
                self.assertFalse((root / custody.ADMISSION).exists())

    def test_exclusive_guarded_result_writes_bind_identity_and_reject_extra_paths(self):
        admission = fixture_admission()
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            with patch.object(custody, "_preflight", return_value=(root, admission)):
                custody.prepare("fixture-plan", root, "n3ext")
                record = admission["records"][0]
                payload = fixture_payload(record)
                result = custody.write_result("fixture-plan", root, "n3ext", record["path"], payload)
                wrapped = json.loads((root / record["path"]).read_bytes())
                self.assertEqual(wrapped["run_id"], admission["run_id"])
                self.assertEqual(wrapped["record"], record)
                self.assertEqual(wrapped["admission_sha256"], custody.digest(custody.canonical(admission)))
                self.assertEqual(result["sha256"], custody.digest((root / record["path"]).read_bytes()))
                with self.assertRaises(FileExistsError):
                    custody.write_result("fixture-plan", root, "n3ext", record["path"], payload)
                for path in ("c67-results/extra.json", "../escape.json", str(root / "absolute.json")):
                    with self.assertRaisesRegex(ValueError, "outside prospective schedule"):
                        custody.write_result("fixture-plan", root, "n3ext", path, payload)
                self.assertEqual(len(list((root / "c67-results").iterdir())), 1)

    def test_exact_readback_and_same_count_byte_tamper(self):
        admission = fixture_admission()
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            fixture_results(root, admission)
            with patch.object(custody, "_preflight", return_value=(root, admission)):
                first = custody.readback("fixture-plan", root, "n3ext")
                self.assertTrue(first["coverage_complete"])
                self.assertEqual(custody.readback("fixture-plan", root, "n3ext"), first)
                path = root / admission["records"][1]["path"]
                # Unexamined arithmetic bytes are still bound by the sealed digest.
                value = json.loads(path.read_bytes())
                value["payload"]["fixed_fixture_marker"] = True
                path.write_bytes(custody.canonical(value))
                with self.assertRaisesRegex(ValueError, "bytes differ"):
                    custody.readback("fixture-plan", root, "n3ext")

    def test_missing_extra_and_symlink_results_refused(self):
        admission = fixture_admission()
        for failure in ("missing", "extra", "symlink"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as scratch:
                root = Path(scratch)
                fixture_results(root, admission)
                path = root / admission["records"][0]["path"]
                if failure == "extra":
                    (path.parent / "extra.json").write_text("{}")
                else:
                    saved = path.read_bytes()
                    path.unlink()
                    if failure == "symlink":
                        external = root / "external.json"
                        external.write_bytes(saved)
                        path.symlink_to(external)
                with self.assertRaises(ValueError):
                    custody.compare_results(root, admission)

    def test_result_cannot_move_between_run_plan_schedule_or_selection(self):
        admission = fixture_admission()
        for key in ("run_id", "plan_sha256", "schedule_sha256", "admission_sha256", "record"):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as scratch:
                root = Path(scratch)
                fixture_results(root, admission)
                path = root / admission["records"][0]["path"]
                value = json.loads(path.read_bytes())
                value[key] = "wrong"
                path.write_bytes(custody.canonical(value))
                with self.assertRaisesRegex(ValueError, "custody binding"):
                    custody.compare_results(root, admission)

    def test_duplicate_c6_slots_and_c7_draws_refused(self):
        admission = fixture_admission()
        c6, c7 = admission["records"][:2]
        payload = fixture_payload(c6)
        payload["rows"][1]["slot"] = 0
        with self.assertRaisesRegex(ValueError, "slot coverage"):
            custody._payload_coverage(payload, c6)
        payload = fixture_payload(c7)
        payload["selected"][1]["draw"] = 0
        with self.assertRaisesRegex(ValueError, "draw coverage"):
            custody._payload_coverage(payload, c7)
        payload = fixture_payload(c7)
        payload["requested"] = 15
        with self.assertRaisesRegex(ValueError, "frozen count"):
            custody._payload_coverage(payload, c7)

    def test_draw_cap_exhaustion_keeps_requested_coverage_unmet(self):
        admission = fixture_admission()
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            fixture_results(root, admission)
            path = root / admission["records"][1]["path"]
            value = json.loads(path.read_bytes())
            value["payload"].update(attempted=4096, selected=[],
                                    status="inconclusive_draw_cap_exhausted")
            path.write_bytes(custody.canonical(value))
            checked = custody.compare_results(root, admission)
            self.assertFalse(checked["coverage_complete"])
            self.assertEqual(checked["records"][1]["retained"], 0)
            self.assertEqual(checked["records"][1]["requested"], 16)

    def test_preflight_uses_supervisor_authority_and_exact_input_source_hashes(self):
        schedule = json.loads((custody.ROOT / custody.SCHEDULE).read_bytes())
        hashes = {custody.SCHEDULE: custody.digest((custody.ROOT / custody.SCHEDULE).read_bytes())}
        for cohort in custody.COHORTS["n3ext"]:
            path = custody.PREFIX + f"inputs/join-plans-20261103/{cohort}.json"
            hashes[path] = custody.digest((custody.ROOT / path).read_bytes())
        plan = {"experiment_id": custody.EXP, "input_sha256": hashes,
                "source_sha256": {custody.SELF: custody.digest((custody.ROOT / custody.SELF).read_bytes())},
                "trials": [{"id": stage, "stage": stage, "run_id": f"RUN-fixture-{stage}",
                            "watchdog_seconds": seconds, "memory_mb": 4096,
                            "artifacts": custody.expected_artifacts(schedule, stage) if stage in custody.COHORTS else []}
                           for stage, seconds in zip(custody.STAGES, custody.WATCHDOGS)]}
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            plan_path = root / "fixture-plan.json"
            plan_path.write_text("fixed fixture plan bytes")
            authority = {"owner": "fixed-fixture", "epoch": 1}
            launch = {"trial_id": "n3ext", "run_id": "RUN-fixture-n3ext",
                      "plan_sha256": custody.digest(plan_path.read_bytes()), "authority": authority}
            (root / "launch.json").write_bytes(custody.canonical(launch))
            with patch.object(experiment_execution, "load_plan", return_value=plan), \
                 patch.object(experiment_execution, "authorize", return_value=authority) as authorize, \
                 patch.object(experiment_execution, "run_root", return_value=root):
                _, bound = custody._preflight(plan_path, root, "n3ext")
                self.assertEqual(len(bound["records"]), 15)
                authorize.assert_called_once()
                plan["input_sha256"][custody.SCHEDULE] = "0" * 64
                with self.assertRaisesRegex(ValueError, "schedule not bound"):
                    custody._preflight(plan_path, root, "n3ext")
                plan["input_sha256"] = hashes.copy()
                # Restore the fixture's schedule hash after the intentional mutation.
                plan["input_sha256"][custody.SCHEDULE] = custody.digest((custody.ROOT / custody.SCHEDULE).read_bytes())
                plan["source_sha256"][custody.SELF] = "0" * 64
                with self.assertRaisesRegex(ValueError, "source not bound"):
                    custody._preflight(plan_path, root, "n3ext")


if __name__ == "__main__":
    unittest.main(verbosity=2)

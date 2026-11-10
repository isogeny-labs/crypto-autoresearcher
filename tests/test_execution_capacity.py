import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import execution_capacity as ec  # noqa: E402


def _spec(root: Path, exp_id: str, status: str, budget: str, runs: bool = False):
    d = root / "experiments" / exp_id
    d.mkdir(parents=True)
    (d / "specification.yaml").write_text(
        f"experiment:\n  id: {exp_id}\n  status: {status}\n  goal_id: GOAL-X\n{budget}")
    if runs:
        (d / "runs" / "RUN-1").mkdir(parents=True)
        (d / "runs" / "RUN-1" / "manifest.yaml").write_text("run: {status: ok}\n")


class ExecutionCapacityTest(unittest.TestCase):
    def test_declared_hours(self):
        self.assertEqual(ec.declared_hours({"total_cpu_hours": 3}), 3.0)
        self.assertEqual(ec.declared_hours(
            {"wall_clock_seconds_per_run": 900, "maximum_runs": 20}), 5.0)
        self.assertIsNone(ec.declared_hours({"maximum_runs": 2}))
        self.assertIsNone(ec.declared_hours(None))

    def test_compute(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "orchestration").mkdir()
            (root / "orchestration" / "execution-capacity.yaml").write_text(
                "routes:\n- {name: a, cpu_hours_per_week: 100, number_status: unverified}\n"
                "- {name: b, cpu_hours_per_week: 0}\n"
                "default_contract_cpu_hours: 0.5\n")
            _spec(root, "EXP-X-000001", "approved", "  plan:\n    budget:\n      total_cpu_hours: 3.0\n")
            _spec(root, "EXP-X-000002", "approved", "")
            _spec(root, "EXP-X-000003", "approved", "  budget: {total_cpu_hours: 9}\n", runs=True)
            _spec(root, "EXP-X-000004", "draft", "  budget: {total_cpu_hours: 9}\n")
            r = ec.compute(root, dispatching=2)
        self.assertEqual(r["approved_unrun_contracts"], 2)
        self.assertEqual(r["contracts_with_declared_budget"], 1)
        self.assertAlmostEqual(r["demand_hours"], 3.5)
        self.assertEqual(r["capacity_hours_per_week"], 100)
        self.assertAlmostEqual(r["utilisation"], 0.035)
        self.assertEqual(r["sentence"],
                         "capacity 100 h, demand 3.5 h, dispatching 2 / recording why not")

    def test_seed_file_all_unverified(self):
        cap = ec.load_capacity(ec.CAPACITY_FILE)
        self.assertEqual({r["name"] for r in cap["routes"]},
                         {"isolab-eks cpu-spot", "runpod", "local"})
        self.assertTrue(all(r["number_status"] == "unverified" for r in cap["routes"]))


if __name__ == "__main__":
    unittest.main()

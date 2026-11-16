import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import mechanism_review as mr  # noqa: E402

TODAY = dt.date(2026, 12, 20)


def mech(id, status, review_by="2026-12-10", cmd="echo 3"):
    return {"id": id, "name": id, "owner_doc": "x.md", "use_metric": cmd,
            "added_on": "2026-11-10", "review_by": review_by, "status": status}


class MechanismReviewTest(unittest.TestCase):
    def test_run_metric(self):
        self.assertEqual(mr.run_metric("echo 7"), 7.0)
        self.assertEqual(mr.run_metric("echo noise; echo 2.5"), 2.5)
        self.assertIsNone(mr.run_metric("echo hello"))
        self.assertIsNone(mr.run_metric("exit 3"))
        self.assertIsNone(mr.run_metric("sleep 5", timeout=1))

    def test_overdue_rules(self):
        rows = mr.review([
            mech("measured-used", "measured"),
            mech("measured-zero", "measured", cmd="echo 0"),
            mech("unmeasured-overdue", "unmeasured"),
            mech("broken", "measured", cmd="exit 1"),
            mech("not-yet", "unmeasured", review_by="2027-01-01"),
            mech("retired", "retired", cmd="echo 0"),
        ], TODAY)
        over = {r["id"] for r in rows if r["overdue"]}
        self.assertEqual(over, {"measured-zero", "unmeasured-overdue", "broken"})
        by = {r["id"]: r for r in rows}
        self.assertEqual(by["broken"]["value"], "unavailable")
        self.assertEqual(by["not-yet"]["days_to_review"], 12)
        self.assertIn("make optional", mr.render_overdue(rows))

    def test_registry_shape(self):
        mechs = mr.load_registry()
        ids = [m["id"] for m in mechs]
        self.assertEqual(len(ids), len(set(ids)))
        for m in mechs:
            self.assertIn(m["status"], mr.STATUSES)
            added, rb = mr._date(m["added_on"]), mr._date(m["review_by"])
            self.assertEqual((rb - added).days, 30, m["id"])
            self.assertTrue(m["use_metric"] and m["owner_doc"])
        agents = Path(mr.REPO, "AGENTS.md")
        if agents.exists():
            h2 = [l for l in agents.read_text().splitlines() if l.startswith("## ")]
            self.assertEqual(sum(i.startswith("agents-md:") for i in ids), len(h2))


if __name__ == "__main__":
    unittest.main()

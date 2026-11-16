import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import check_handoff_expiry as che  # noqa: E402
import expire_handoffs as eh  # noqa: E402
import validate_ledger as vl  # noqa: E402

TODAY = dt.date(2026, 11, 10)


def make_ctx(handoffs, decisions=()):
    ctx = vl.Ctx(set())
    for rid, body in handoffs.items():
        ctx.register(rid, f"/x/ledger/handoffs/{rid}.yaml", body, "handoff")
    for rid, body in decisions:
        ctx.register(rid, f"/x/ledger/decisions/{rid}.yaml", body, "coordinator_decision")
    return ctx


def h(role="validator", **kw):
    return {"from": "coordinator", "to": role, "objective": "o", "budget": {}, **kw}


class CheckTest(unittest.TestCase):
    def test_candidate_advisory(self):
        ctx = make_ctx({
            "TASK-20261001-aaaaaa": h(),                              # 40 d, open
            "TASK-20261001-bbbbbb": h(archived_by="TASK-20261002-x"),  # returned
            "TASK-20261105-cccccc": h(),                              # 5 d
            "TASK-20261001-dddddd": h(status="expired"),               # already
            "TASK-20261027-eeeeee": h(),                              # exactly 14 d
        })
        che.check_handoff_expiry(ctx, today=TODAY)
        self.assertEqual(len(ctx.advisories), 1)
        self.assertIn("expired candidate", ctx.advisories[0])
        self.assertIn("TASK-20261001-aaaaaa", ctx.advisories[0])
        self.assertEqual(ctx.errors, [])

    def test_today_accepts_string_forms(self):
        ctx = make_ctx({"TASK-20261001-aaaaaa": h()})
        che.check_handoff_expiry(ctx, today="20261110")
        che.check_handoff_expiry(ctx, today="2026-11-10")
        self.assertEqual(len(ctx.advisories), 2)

    def _six_expired(self):
        recs = {f"TASK-2026100{i}-e0000{i}": h(status="expired", expired_on="2026-11-01")
                for i in range(1, 7)}
        recs["TASK-20261105-newnew"] = h()
        recs["TASK-20261105-othrol"] = h("executor")
        recs["TASK-20260901-oldold"] = h()   # older than the expired ones
        return recs

    def test_role_limit_error_and_clearing(self):
        recs = self._six_expired()
        ctx = make_ctx(recs)
        che.check_handoff_expiry(ctx, today=TODAY)
        self.assertEqual(len(ctx.errors), 1)
        self.assertIn("TASK-20261105-newnew", ctx.errors[0])
        self.assertIn("clears_expired", ctx.errors[0])
        ids = [f"TASK-2026100{i}-e0000{i}" for i in range(1, 3)]
        ctx = make_ctx(recs, [("DEC-20261110-abcdef", {"clears_expired": ids})])
        che.check_handoff_expiry(ctx, today=TODAY)   # 4 left uncleared
        self.assertEqual(ctx.errors, [])

    def test_five_expired_is_allowed(self):
        recs = {k: v for k, v in list(self._six_expired().items())[:5]}
        recs["TASK-20261105-newnew"] = h()
        ctx = make_ctx(recs)
        che.check_handoff_expiry(ctx, today=TODAY)
        self.assertEqual(ctx.errors, [])


class ExpireTest(unittest.TestCase):
    def test_apply_write_once_never_deletes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "ledger" / "handoffs"
            d.mkdir(parents=True)
            a = d / "TASK-20261001-aaaaaa.yaml"
            a.write_text("handoff:\n  id: TASK-20261001-aaaaaa\n  to: validator\n  budget: {}\n")
            b = d / "TASK-20261001-bbbbbb.yaml"
            b.write_text("handoff:\n  id: TASK-20261001-bbbbbb\n  to: executor\n  status: assigned\n  budget: {}\n")
            c = d / "TASK-20261001-cccccc.yaml"
            c.write_text("handoff:\n  id: TASK-20261001-cccccc\n  to: executor\n  archived_by: TASK-20261002-zzzzzz\n")
            before_c = c.read_text()
            self.assertEqual(eh.main(["--repo-root", str(root), "--today", "2026-11-10"]), 0)
            self.assertNotIn("expired", a.read_text())          # dry run
            eh.main(["--repo-root", str(root), "--today", "2026-11-10", "--apply"])
            ba = eh._body(a)
            self.assertEqual((ba["status"], str(ba["expired_on"])), ("expired", "2026-11-10"))
            bb = eh._body(b)
            self.assertEqual((bb["status"], bb["status_before_expiry"]), ("expired", "assigned"))
            self.assertEqual(c.read_text(), before_c)
            first = a.read_text()
            eh.main(["--repo-root", str(root), "--today", "2026-12-25", "--apply"])
            self.assertEqual(a.read_text(), first)               # write-once
            self.assertEqual(len(list(d.glob("*.yaml"))), 3)

    def test_role_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d = root / "ledger" / "handoffs"
            d.mkdir(parents=True)
            for i in range(7):
                (d / f"TASK-2026100{i}-e0000{i}.yaml").write_text(
                    f"handoff:\n  id: TASK-2026100{i}-e0000{i}\n  to: red-team\n  status: expired\n")
            over = eh.role_report(eh.scan(root), [], None)
            self.assertEqual(list(over), ["red-team"])
            self.assertEqual(len(over["red-team"]), 7)
            cleared = [{"clears_expired": list(over["red-team"][:3])}]
            self.assertEqual(eh.role_report(eh.scan(root), cleared, "red-team"), {})


if __name__ == "__main__":
    unittest.main()

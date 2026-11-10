"""Per-area approval capacity (harness review I2; docs/execution-capacity-cap.md)."""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_approval_capacity as cap_rule  # noqa: E402
import portfolio_kpis  # noqa: E402


class FakeCtx:
    """The subset of validate_ledger.Ctx the rule reads."""

    def __init__(self) -> None:
        self.ids: dict[str, str] = {}
        self.records: dict[str, dict] = {}
        self.record_types: dict[str, str] = {}
        self.errors: list[str] = []
        self.advisories: list[str] = []

    def err(self, path: str, msg: str) -> None:
        self.errors.append(f"{path}: {msg}")

    def advise(self, path: str, msg: str) -> None:
        self.advisories.append(f"{path}: {msg}")


class ApprovalCapacity(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.policy = self.root / "research-priority.yaml"
        self.policy.write_text("ecc_areas: [ECDLP]\napproved_unrun_cap_per_area: 3\n")
        self.ctx = FakeCtx()

    def exp(self, exp_id: str, *, status: str = "approved", approved_by: str = "legacy",
            ran: bool = False, supersedes: str | None = None) -> None:
        d = self.root / "experiments" / exp_id
        (d / "runs").mkdir(parents=True)
        if ran:
            (d / "runs" / "RUN-X-000001").mkdir()
        spec = d / "specification.yaml"
        spec.write_text("")
        self.ctx.ids[exp_id] = str(spec)
        self.ctx.records[exp_id] = {"id": exp_id, "status": status, "approved_by": approved_by,
                                    "supersedes": supersedes}
        self.ctx.record_types[exp_id] = "experiment"

    def dec(self, dec_id: str, targets: list[str], **extra) -> None:
        self.ctx.ids[dec_id] = f"ledger/decisions/{dec_id}.yaml"
        self.ctx.records[dec_id] = {"id": dec_id, "decision": "approve", "target_ids": targets,
                                    **extra}
        self.ctx.record_types[dec_id] = "coordinator_decision"

    def run_rule(self) -> None:
        cap_rule.check_approval_capacity(self.ctx, policy_file=self.policy)

    def three_standing(self) -> None:
        for i in range(3):
            self.exp(f"EXP-ECDLP-00000{i}")

    def test_new_approval_over_cap_is_an_error_after_enforcement(self):
        self.three_standing()
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261112-aaaaaa")
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-aaaaaa"])
        self.run_rule()
        self.assertEqual(len(self.ctx.errors), 1, self.ctx.errors)
        self.assertIn("area:ECDLP would hold 4", self.ctx.errors[0])
        self.assertIn("supersedes:", self.ctx.errors[0])
        self.assertEqual(self.ctx.advisories, [])

    def test_same_approval_before_enforcement_is_advisory(self):
        self.three_standing()
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261110-aaaaaa")
        self.dec("DEC-20261110-aaaaaa", ["EXP-ECDLP-aaaaaa"])
        self.run_rule()
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(len(self.ctx.advisories), 1)
        self.dec("DEC-20261001-bbbbbb", ["EXP-ECDLP-000001"])  # before the advisory window
        self.ctx.advisories.clear()
        self.run_rule()
        self.assertEqual(len(self.ctx.advisories), 1)

    def test_within_cap_passes(self):
        self.exp("EXP-ECDLP-000000")
        self.exp("EXP-ECDLP-000001")
        self.exp("EXP-ECDLP-000002", ran=True)  # ran: not in the backlog
        self.exp("EXP-SSI-000003")              # another area does not count
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261112-aaaaaa")
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-aaaaaa"])
        self.run_rule()
        self.assertEqual(self.ctx.errors, [])

    def test_naming_a_retired_same_area_contract_passes(self):
        self.three_standing()
        self.exp("EXP-ECDLP-dddddd", status="superseded")
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261112-aaaaaa")
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-aaaaaa"], supersedes="EXP-ECDLP-dddddd")
        self.run_rule()
        self.assertEqual(self.ctx.errors, [])

    def test_naming_an_unretired_or_other_area_contract_does_not_pass(self):
        self.three_standing()
        self.exp("EXP-SSI-dddddd", status="superseded")
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261112-aaaaaa")
        # EXP-ECDLP-000000 is still approved-unrun; EXP-SSI-dddddd is another area.
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-aaaaaa"],
                 supersedes=["EXP-ECDLP-000000", "EXP-SSI-dddddd"])
        self.run_rule()
        self.assertEqual(len(self.ctx.errors), 1)

    def test_spec_level_supersession_retires_an_approved_contract(self):
        self.three_standing()
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261112-aaaaaa",
                 supersedes="EXP-ECDLP-000000")
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-aaaaaa"], supersedes=["EXP-ECDLP-000000"])
        self.run_rule()
        self.assertEqual(self.ctx.errors, [])

    def test_later_approvals_do_not_fail_an_earlier_lawful_decision(self):
        self.exp("EXP-ECDLP-000000")
        self.exp("EXP-ECDLP-000001")
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261112-aaaaaa")
        self.exp("EXP-ECDLP-bbbbbb", approved_by="DEC-20261113-bbbbbb")
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-aaaaaa"])
        self.dec("DEC-20261113-bbbbbb", ["EXP-ECDLP-bbbbbb"])
        self.run_rule()
        self.assertEqual(len(self.ctx.errors), 1)
        self.assertIn("DEC-20261113-bbbbbb", self.ctx.errors[0])

    def test_non_approve_decisions_and_continuations_are_ignored(self):
        self.three_standing()
        self.exp("EXP-ECDLP-cccccc", ran=True)
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-cccccc"])  # continuation of a run contract
        self.dec("DEC-20261112-bbbbbb", ["EXP-ECDLP-000000"], decision="revise")
        self.run_rule()
        self.assertEqual(self.ctx.errors, [])

    def test_absent_field_disables_the_rule(self):
        self.policy.write_text("ecc_areas: [ECDLP]\n")
        self.three_standing()
        self.exp("EXP-ECDLP-aaaaaa", approved_by="DEC-20261112-aaaaaa")
        self.dec("DEC-20261112-aaaaaa", ["EXP-ECDLP-aaaaaa"])
        self.run_rule()
        self.assertEqual(self.ctx.errors, [])

    def test_invalid_cap_is_refused(self):
        self.policy.write_text("approved_unrun_cap_per_area: 0\n")
        with self.assertRaises(ValueError):
            portfolio_kpis.approved_unrun_cap(self.policy)

    def test_repository_policy_declares_three(self):
        self.assertEqual(portfolio_kpis.approved_unrun_cap(), 3)


class KpiCapacityFlag(unittest.TestCase):
    def kpis(self, root: Path, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with redirect_stdout(out):
            code = portfolio_kpis.main(["--repo-root", str(root), *argv])
        return code, out.getvalue()

    def test_area_capacity_reads_the_policy_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "orchestration").mkdir()
            policy = root / "orchestration" / "research-priority.yaml"
            policy.write_text("approved_unrun_cap_per_area: 3\n")
            for i in range(2):
                exp_id = f"EXP-T-00000{i}"
                d = root / "experiments" / exp_id
                d.mkdir(parents=True)
                (d / "specification.yaml").write_text(
                    f"experiment:\n  id: {exp_id}\n  status: approved\n  goal_id: GOAL-T-000001\n")
            code, out = self.kpis(root, "--capacity", "area:T")
            self.assertEqual(code, 0)
            self.assertIn("area:T\tapproved_unrun=2\tcap=3\theadroom=1", out)
            policy.write_text("approved_unrun_cap_per_area: 2\n")
            code, out = self.kpis(root, "--capacity", "area:T")
            self.assertEqual(code, 1)
            self.assertIn("cap=2\theadroom=0", out)
            code, out = self.kpis(root, "--capacity", "GOAL-T-000001")  # legacy goal view
            self.assertEqual(code, 0)
            self.assertIn("approved_unrun=2\tcap=none", out)


if __name__ == "__main__":
    unittest.main()

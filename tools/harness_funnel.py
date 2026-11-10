#!/usr/bin/env python3
"""Count how work moves through the research harness, stage by stage.

The funnel is: proposals and ideas, hypotheses, experiment specifications,
approved contracts, runs, evidence, decisions.  The tool is a read-only
operational measurement of the ledger.  It is not research evidence and it
never writes to the repository.

Approval date rule (first match wins, see ``approval_date``):

1. ``approved_at`` on the specification.
2. The date of the decision named by ``approval_decision``
   (``decided_at``, then ``recorded_at``, then ``date``), then the date inside
   that decision id (``DEC-YYYYMMDD-...``).
3. The same lookup for ``execution_authorized_decision``.
4. ``frozen_at``.
5. ``specified_at``.
6. ``updated``.
7. The date of the earliest ``approve`` decision whose ``target_ids`` name the
   experiment.
8. Unknown.  Unknown ages are reported in their own bucket and are never
   counted as overdue.

Runs are counted as entries under ``experiments/<id>/runs/``.  In a sparse
checkout the run entries may be absent from the working tree, so ``--runs-source
git`` (or ``auto``, which falls back to it) lists them with ``git ls-tree``,
which needs tree objects only and fetches no blobs.  Run manifest status needs
the manifest blobs and is reported as ``not_fetched`` in that mode.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required")

_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
SCHEMA = "lab.harness-funnel/v1"
AGE_BUCKETS = ("0-7d", "8-14d", "15-30d", "31-60d", "61-90d", "91d+", "unknown")
NO_GOAL = "(no goal)"


def load_yaml(path: Path):
    """Return the parsed document, or None when the file cannot be parsed."""
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.load(fh, Loader=_LOADER)
    except Exception:
        return None


def unwrap(doc, key: str):
    """Return the record body, nested under ``key`` or flat; None otherwise."""
    if not isinstance(doc, dict):
        return None
    inner = doc.get(key)
    if isinstance(inner, dict):
        return inner
    return doc


def to_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        m = re.match(r"\s*(\d{4})-(\d{2})-(\d{2})", value)
        if m:
            try:
                return dt.date(int(m[1]), int(m[2]), int(m[3]))
            except ValueError:
                return None
    return None


def id_date(ident) -> dt.date | None:
    if isinstance(ident, str):
        m = re.match(r"[A-Z]+-(\d{4})(\d{2})(\d{2})-", ident)
        if m:
            try:
                return dt.date(int(m[1]), int(m[2]), int(m[3]))
            except ValueError:
                return None
    return None


def _load_dir(root: Path, patterns, key: str):
    """Load records matching the glob patterns.  Returns (records, skipped)."""
    seen = []
    for pat in patterns:
        seen.extend(sorted(root.glob(pat)))
    records, skipped = [], 0
    for path in seen:
        if not path.is_file():
            continue
        body = unwrap(load_yaml(path), key)
        if body is None:
            skipped += 1
            continue
        records.append((path, body))
    return records, skipped


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _git_run_entries(root: Path) -> dict[str, set[str]] | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "HEAD", "--", "experiments"],
            capture_output=True, text=True, check=False)
    except OSError:
        return None
    if out.returncode:
        return None
    runs: dict[str, set[str]] = {}
    for line in out.stdout.splitlines():
        parts = line.split("/")
        if len(parts) >= 4 and parts[0] == "experiments" and parts[2] == "runs":
            if not parts[3].startswith("."):
                runs.setdefault(parts[1], set()).add(parts[3])
    return runs


def _fs_run_entries(root: Path) -> dict[str, set[str]]:
    runs: dict[str, set[str]] = {}
    exp_root = root / "experiments"
    if not exp_root.is_dir():
        return runs
    for exp in sorted(exp_root.iterdir()):
        rd = exp / "runs"
        if rd.is_dir():
            names = {p.name for p in rd.iterdir() if not p.name.startswith(".")}
            if names:
                runs[exp.name] = names
    return runs


def run_entries(root: Path, source: str) -> tuple[dict[str, set[str]], str]:
    if source == "fs":
        return _fs_run_entries(root), "fs"
    if source == "git":
        got = _git_run_entries(root)
        return (got if got is not None else {}), "git"
    fs = _fs_run_entries(root)
    if fs:
        return fs, "fs"
    got = _git_run_entries(root)
    if got:
        return got, "git"
    return fs, "fs"


def run_status(root: Path, exp_id: str, run_id: str) -> str:
    rdir = root / "experiments" / exp_id / "runs" / run_id
    for name in ("manifest.json", "manifest.yaml"):
        p = rdir / name
        if p.is_file():
            if name.endswith(".json"):
                try:
                    body = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    return "unparsable"
            else:
                body = load_yaml(p)
            body = unwrap(body, "run") if isinstance(body, dict) else None
            if isinstance(body, dict):
                return str(body.get("status"))
            return "unparsable"
    return "no_manifest"


class Funnel:
    """Everything the stages and the WIP policy need, scanned once."""

    def __init__(self, root: Path, runs_source: str = "auto"):
        self.root = Path(root)
        r = self.root
        self.skipped: Counter = Counter()
        self.proposals = sorted((r / "ledger/proposals").glob("*.yaml")) if (r / "ledger/proposals").is_dir() else []
        self.ideas = sorted((r / "ledger/ideas").glob("*.yaml")) if (r / "ledger/ideas").is_dir() else []

        hyp, s = _load_dir(r, ["ledger/hypotheses/*.yaml"], "hypothesis")
        self.hypotheses = [b for _, b in hyp]
        self.skipped["hypotheses"] = s
        self.hyp_goal = {}
        for h in self.hypotheses:
            if isinstance(h.get("id"), str):
                self.hyp_goal[h["id"]] = self._goal_of(h)

        dec, s = _load_dir(r, ["ledger/decisions/*.yaml"], "coordinator_decision")
        self.decisions = [b for _, b in dec]
        self.skipped["decisions"] = s
        self.decision_date = {}
        self.approve_date_by_target: dict[str, dt.date] = {}
        for d in self.decisions:
            when = to_date(d.get("decided_at")) or to_date(d.get("recorded_at")) or to_date(d.get("date")) or id_date(d.get("id"))
            if isinstance(d.get("id"), str):
                self.decision_date[d["id"]] = when
            if when and str(d.get("decision")) == "approve":
                for t in _as_list(d.get("target_ids")):
                    if isinstance(t, str) and (t not in self.approve_date_by_target or when < self.approve_date_by_target[t]):
                        self.approve_date_by_target[t] = when

        ev, s = _load_dir(r, ["ledger/evidence/*.yaml", "ledger/EV-*.yaml"], "evidence")
        self.evidence = [b for _, b in ev]
        self.skipped["evidence"] = s
        self.evidence_cited: Counter = Counter()
        for e in self.evidence:
            for key in ("experiment_ids", "experiment_id"):
                for x in _as_list(e.get(key)):
                    if isinstance(x, str):
                        self.evidence_cited[x] += 1

        goals, s = _load_dir(r, ["ledger/goals/*.yaml", "ledger/goals/*/goal.yaml"], "research_goal")
        self.goals = [b for _, b in goals]
        self.skipped["goals"] = s

        self.runs, self.runs_source = run_entries(r, runs_source)

        self.contracts = []
        exp_root = r / "experiments"
        specs = sorted(exp_root.glob("*/specification.yaml")) if exp_root.is_dir() else []
        self.spec_files = len(specs)
        for path in specs:
            body = unwrap(load_yaml(path), "experiment")
            if body is None:
                self.skipped["specifications"] += 1
                continue
            exp_id = path.parent.name
            when, src = self.approval_date(exp_id, body)
            self.contracts.append({
                "id": exp_id,
                "path": path,
                "spec": body,
                "status": str(body.get("status")),
                "goal": self._goal_of(body) or self.hyp_goal.get(body.get("hypothesis_id")) or NO_GOAL,
                "approval_date": when,
                "approval_source": src,
                "has_run": bool(self.runs.get(exp_id)),
                "has_evidence": self.evidence_cited[exp_id] > 0,
            })
        for c in self.contracts:
            c["approved_unrun"] = c["status"] == "approved" and not c["has_run"] and not c["has_evidence"]

    @staticmethod
    def _goal_of(rec: dict):
        g = rec.get("goal_id")
        if isinstance(g, str) and g:
            return g
        gs = rec.get("goal_ids")
        if isinstance(gs, list):
            for x in gs:
                if isinstance(x, str) and x:
                    return x
        return None

    def approval_date(self, exp_id: str, spec: dict):
        d = to_date(spec.get("approved_at"))
        if d:
            return d, "approved_at"
        for key in ("approval_decision", "execution_authorized_decision"):
            ref = spec.get(key)
            if isinstance(ref, str):
                d = self.decision_date.get(ref) or id_date(ref)
                if d:
                    return d, key
        for key in ("frozen_at", "specified_at", "updated"):
            d = to_date(spec.get(key))
            if d:
                return d, key
        d = self.approve_date_by_target.get(exp_id)
        if d:
            return d, "approve_decision_target"
        return None, "unknown"


def age_bucket(age: int | None) -> str:
    if age is None:
        return "unknown"
    for limit, name in ((7, "0-7d"), (14, "8-14d"), (30, "15-30d"), (60, "31-60d"), (90, "61-90d")):
        if age <= limit:
            return name
    return "91d+"


def age_days(contract: dict, as_of: dt.date) -> int | None:
    d = contract["approval_date"]
    return None if d is None else max(0, (as_of - d).days)


def _hist(values) -> dict:
    return dict(sorted(Counter(str(v) for v in values).items(), key=lambda kv: (-kv[1], kv[0])))


def summarize(f: Funnel, as_of: dt.date) -> dict:
    approved = [c for c in f.contracts if c["status"] == "approved"]
    unrun = [c for c in approved if c["approved_unrun"]]
    aging = {b: 0 for b in AGE_BUCKETS}
    sources = Counter()
    for c in unrun:
        aging[age_bucket(age_days(c, as_of))] += 1
        sources[c["approval_source"]] += 1
    per_goal: dict[str, dict] = {}
    for c in approved:
        row = per_goal.setdefault(c["goal"], {"approved": 0, "approved_unrun": 0})
        row["approved"] += 1
        row["approved_unrun"] += 1 if c["approved_unrun"] else 0
    per_goal = dict(sorted(per_goal.items(), key=lambda kv: (-kv[1]["approved_unrun"], kv[0])))

    if f.runs_source == "fs":
        run_hist = Counter()
        for exp_id, names in sorted(f.runs.items()):
            for n in sorted(names):
                run_hist[run_status(f.root, exp_id, n)] += 1
        runs_by_status = _hist(run_hist.elements())
    else:
        runs_by_status = {"not_fetched": sum(len(v) for v in f.runs.values())}
    run_total = sum(len(v) for v in f.runs.values())

    certs = sum(1 for e in f.evidence
                if isinstance(e.get("certificate"), dict) and e["certificate"].get("verified") is True)
    ndec, nev = len(f.decisions), len(f.evidence)
    return {
        "schema": SCHEMA,
        "as_of": as_of.isoformat(),
        "runs_source": f.runs_source,
        "proposals": {"proposals": len(f.proposals), "ideas": len(f.ideas), "total": len(f.proposals) + len(f.ideas)},
        "hypotheses": {"total": len(f.hypotheses), "by_status": _hist(h.get("status") for h in f.hypotheses)},
        "specifications": {"total": len(f.contracts), "by_status": _hist(c["status"] for c in f.contracts)},
        "approved": {
            "total": len(approved),
            "with_approved_by": sum(1 for c in approved if c["spec"].get("approved_by")),
            "with_run": sum(1 for c in approved if c["has_run"]),
            "with_evidence": sum(1 for c in approved if c["has_evidence"]),
        },
        "approved_unrun": {
            "total": len(unrun),
            "share_of_approved": round(len(unrun) / len(approved), 4) if approved else None,
            "aging_days": aging,
            "approval_date_source": dict(sorted(sources.items())),
        },
        "runs": {"total": run_total, "experiments_with_runs": len(f.runs), "by_manifest_status": runs_by_status},
        "evidence": {
            "total": nev,
            "by_claim_tier": _hist(e.get("claim_tier") for e in f.evidence),
            "by_direction": _hist(e.get("direction") for e in f.evidence),
            "certificate_verified": certs,
        },
        "decisions": {"total": ndec, "by_decision": _hist(d.get("decision") for d in f.decisions)},
        "goals": {"total": len(f.goals), "by_status": _hist(g.get("status") for g in f.goals)},
        "per_goal": per_goal,
        "ratios": {
            "decisions_per_evidence": round(ndec / nev, 3) if nev else None,
            "evidence_per_approved_contract": round(nev / len(approved), 3) if approved else None,
        },
        "unreadable_records": dict(sorted((k, v) for k, v in f.skipped.items() if v)),
    }


def headline(s: dict) -> list[str]:
    r = s["ratios"]
    return [
        f"proposals+ideas {s['proposals']['total']}  hypotheses {s['hypotheses']['total']}  "
        f"specifications {s['specifications']['total']}  approved {s['approved']['total']}",
        f"approved_unrun {s['approved_unrun']['total']} "
        f"({_pct(s['approved_unrun']['share_of_approved'])} of approved)",
        f"runs {s['runs']['total']}  evidence {s['evidence']['total']}  decisions {s['decisions']['total']}  "
        f"certificate_verified {s['evidence']['certificate_verified']}",
        f"decisions per evidence {r['decisions_per_evidence']}  evidence per approved contract "
        f"{r['evidence_per_approved_contract']}",
    ]


def _pct(x) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def render_text(s: dict) -> str:
    out = [f"Harness funnel as of {s['as_of']} (runs source: {s['runs_source']})", ""]

    def hist(title, h):
        out.append(f"{title}")
        items = list(h.items())
        for k, v in items[:12]:
            out.append(f"    {k[:44]:<44} {v:>6}")
        if len(items) > 12:
            rest = items[12:]
            out.append(f"    {'other (' + str(len(rest)) + ' distinct values)':<44} {sum(v for _, v in rest):>6}")

    out.append(f"{'proposals':<20}{s['proposals']['proposals']:>7}   ideas {s['proposals']['ideas']}")
    out.append(f"{'hypotheses':<20}{s['hypotheses']['total']:>7}")
    hist("  by status", s["hypotheses"]["by_status"])
    out.append(f"{'specifications':<20}{s['specifications']['total']:>7}")
    hist("  by status", s["specifications"]["by_status"])
    a = s["approved"]
    out.append(f"{'approved':<20}{a['total']:>7}   with approved_by {a['with_approved_by']}, "
               f"with run {a['with_run']}, with evidence {a['with_evidence']}")
    u = s["approved_unrun"]
    out.append(f"{'approved_unrun':<20}{u['total']:>7}   {_pct(u['share_of_approved'])} of approved")
    for b, n in u["aging_days"].items():
        out.append(f"    age {b:<35} {n:>6}")
    out.append(f"    approval date source: {u['approval_date_source']}")
    out.append(f"{'runs':<20}{s['runs']['total']:>7}   in {s['runs']['experiments_with_runs']} experiments")
    hist("  by manifest status", s["runs"]["by_manifest_status"])
    out.append(f"{'evidence':<20}{s['evidence']['total']:>7}   certificate.verified {s['evidence']['certificate_verified']}")
    hist("  by claim_tier", s["evidence"]["by_claim_tier"])
    hist("  by direction", s["evidence"]["by_direction"])
    out.append(f"{'decisions':<20}{s['decisions']['total']:>7}")
    hist("  by decision", s["decisions"]["by_decision"])
    out.append(f"{'goals':<20}{s['goals']['total']:>7}")
    hist("  by status", s["goals"]["by_status"])
    out.append("per goal (approved / approved_unrun), top 15 by approved_unrun")
    for g, row in list(s["per_goal"].items())[:15]:
        out.append(f"    {g:<40} {row['approved']:>6} {row['approved_unrun']:>6}")
    out.append("ratios")
    for k, v in s["ratios"].items():
        out.append(f"    {k:<40} {v}")
    if s["unreadable_records"]:
        out.append(f"unreadable records skipped: {s['unreadable_records']}")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="repository root")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--check", action="store_true", help="print the headline lines and exit 0 (for CI artifacts)")
    ap.add_argument("--as-of", help="YYYY-MM-DD used for aging (default: today)")
    ap.add_argument("--runs-source", choices=("auto", "fs", "git"), default="auto")
    args = ap.parse_args(argv)
    as_of = to_date(args.as_of) if args.as_of else dt.date.today()
    if as_of is None:
        ap.error("--as-of must be YYYY-MM-DD")
    s = summarize(Funnel(Path(args.root), args.runs_source), as_of)
    if args.check:
        print("\n".join(headline(s)))
        return 0
    print(json.dumps(s, indent=2, sort_keys=False) if args.json else render_text(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())

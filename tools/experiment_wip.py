#!/usr/bin/env python3
"""Limit approved-but-unrun experiment contracts per goal.

Policy file: coordination/experiment_wip_policy.json (schema
lab.experiment-wip/v1, modes off|advisory|enforce).  The count of approved
contracts that have no run and no citing evidence comes from
tools/harness_funnel.py.  This is an operational admission signal, not
research evidence.

--report   per-goal approved-unrun counts against the cap, and overdue contracts.
--check    list contracts approved on or after the cutoff that break the cap or
           lack a first_measurement block.  Exit 1 only in enforce mode.
--expire   dry-run list of overdue contracts with the exact change to make.
           Writes nothing unless --apply is also given.  --apply is a
           Coordinator action and must be logged by a decision record.

Cap rule.  For each goal, the currently approved-unrun contracts are ordered by
approval date, then id.  Contracts with an unknown approval date sort first.
The n-th contract in that order was the n-th open contract of the goal when it
was approved, so it breaks the cap when n is above the cap and its approval
date is on or after the cutoff.  Contracts that were run after approval are not
in the list, which can only make this check lenient for older history.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_funnel as hf  # noqa: E402

SCHEMA = "lab.experiment-wip/v1"
MODES = ("off", "advisory", "enforce")
POLICY_PATH = Path("coordination/experiment_wip_policy.json")


class PolicyError(ValueError):
    """The committed WIP policy is malformed."""


def _pos_int(policy: dict, key: str) -> int:
    v = policy.get(key)
    if not isinstance(v, int) or isinstance(v, bool) or v < 1:
        raise PolicyError(f"{key} must be a positive integer")
    return v


def load_policy(path: Path) -> dict:
    try:
        policy = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read experiment WIP policy {path}: {exc}") from exc
    if not isinstance(policy, dict) or policy.get("schema") != SCHEMA:
        raise PolicyError(f"experiment WIP policy schema must be {SCHEMA}")
    if policy.get("mode") not in MODES:
        raise PolicyError(f"mode must be one of {', '.join(MODES)}")
    cutoff = policy.get("cutoff")
    if not isinstance(cutoff, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cutoff) or hf.to_date(cutoff) is None:
        raise PolicyError("cutoff must be an ISO date YYYY-MM-DD")
    for key in ("approved_unrun_cap_per_goal", "approved_unrun_expiry_days", "first_measurement_max_seconds"):
        _pos_int(policy, key)
    if not isinstance(policy.get("notes"), str):
        raise PolicyError("notes must be a string")
    return policy


def _sort_key(c: dict):
    d = c["approval_date"]
    return (d is not None, d or dt.date.min, c["id"])


def unrun_by_goal(funnel: hf.Funnel) -> dict[str, list[dict]]:
    goals: dict[str, list[dict]] = {}
    for c in funnel.contracts:
        if c["approved_unrun"]:
            goals.setdefault(c["goal"], []).append(c)
    for rows in goals.values():
        rows.sort(key=_sort_key)
    return goals


def first_measurement_problems(spec: dict, max_seconds: int) -> list[str]:
    fm = spec.get("first_measurement")
    if not isinstance(fm, dict):
        return ["missing first_measurement block"]
    problems = []
    cmd = fm.get("command")
    if not ((isinstance(cmd, str) and cmd.strip()) or (isinstance(cmd, list) and cmd and all(isinstance(x, str) for x in cmd))):
        problems.append("first_measurement.command must be a non-empty string or list of strings")
    ms = fm.get("max_seconds")
    if isinstance(ms, bool) or not isinstance(ms, (int, float)) or ms <= 0:
        problems.append("first_measurement.max_seconds must be a positive number")
    elif ms > max_seconds:
        problems.append(f"first_measurement.max_seconds {ms} exceeds policy {max_seconds}")
    no = fm.get("null_object")
    if no is None or (isinstance(no, (str, list, dict)) and not no):
        problems.append("first_measurement.null_object must be set")
    return problems


def check(funnel: hf.Funnel, policy: dict) -> list[dict]:
    cutoff = hf.to_date(policy["cutoff"])
    cap = policy["approved_unrun_cap_per_goal"]
    out = []
    for goal, rows in sorted(unrun_by_goal(funnel).items()):
        for n, c in enumerate(rows, start=1):
            d = c["approval_date"]
            if d is not None and d >= cutoff and n > cap:
                out.append({"id": c["id"], "goal": goal, "approved": d.isoformat(),
                            "problem": f"open contract {n} of goal when approved, cap {cap}"})
    for c in funnel.contracts:
        d = c["approval_date"]
        if c["status"] == "approved" and d is not None and d >= cutoff:
            for p in first_measurement_problems(c["spec"], policy["first_measurement_max_seconds"]):
                out.append({"id": c["id"], "goal": c["goal"], "approved": d.isoformat(), "problem": p})
    return sorted(out, key=lambda r: (r["id"], r["problem"]))


def overdue(funnel: hf.Funnel, policy: dict, as_of: dt.date) -> list[dict]:
    limit = policy["approved_unrun_expiry_days"]
    rows = []
    for c in funnel.contracts:
        if c["approved_unrun"]:
            age = hf.age_days(c, as_of)
            if age is not None and age > limit:
                rows.append({**c, "age_days": age})
    return sorted(rows, key=lambda c: (-c["age_days"], c["id"]))


# ---- expiry -----------------------------------------------------------------

_STATUS = re.compile(r"^( *)status:[ \t]*(['\"]?)approved\2[ \t]*(#.*)?$")


def plan_expiry(text: str, as_of: dt.date, age_days: int) -> tuple[str, list[str]]:
    """Return (new_text, change_lines).  Raises ValueError when not editable.

    The edit is textual so comments and key order survive.  It targets the
    shallowest ``status: approved`` line, which is the contract's own status.
    """
    lines = text.split("\n")
    hits = [(len(m[1]), i) for i, ln in enumerate(lines) if (m := _STATUS.match(ln))]
    if not hits:
        raise ValueError("no 'status: approved' line found")
    indent, idx = min(hits)
    pad = " " * indent
    if any(re.match(rf"^{pad}expired_from_approved:", ln) for ln in lines):
        raise ValueError("expired_from_approved already present")
    changes = [f"status: approved -> draft"]
    lines[idx] = re.sub(r"approved", "draft", lines[idx], count=1)
    for i, ln in enumerate(lines):
        m = re.match(rf"^{pad}execution_state:[ \t]*(.*)$", ln)
        if m:
            changes.append(f"execution_state: {m[1].strip() or '(empty)'} -> draft")
            lines[i] = f"{pad}execution_state: draft"
            break
    block = [f"{pad}expired_from_approved:",
             f"{pad}  at: '{as_of.isoformat()}'",
             f"{pad}  age_days: {age_days}",
             f"{pad}  policy: {SCHEMA}"]
    lines[idx + 1:idx + 1] = block
    changes.append("add " + " ".join(b.strip() for b in block))
    return "\n".join(lines), changes


def expire(funnel: hf.Funnel, policy: dict, as_of: dt.date, apply: bool) -> list[dict]:
    results = []
    for c in overdue(funnel, policy, as_of):
        path: Path = c["path"]
        row = {"id": c["id"], "goal": c["goal"], "age_days": c["age_days"], "path": str(path)}
        try:
            new_text, changes = plan_expiry(path.read_text(encoding="utf-8"), as_of, c["age_days"])
            parsed = hf.unwrap(yaml_load_text(new_text), "experiment")
            if not isinstance(parsed, dict) or parsed.get("status") != "draft" \
                    or parsed.get("expired_from_approved", {}).get("age_days") != c["age_days"]:
                raise ValueError("edited text did not reparse to the intended change")
        except (ValueError, OSError) as exc:
            row.update(changes=[], error=str(exc), applied=False)
            results.append(row)
            continue
        row.update(changes=changes, applied=False)
        if apply:
            path.write_text(new_text, encoding="utf-8")
            row["applied"] = True
        results.append(row)
    return results


def yaml_load_text(text: str):
    return hf.yaml.load(text, Loader=hf._LOADER)


# ---- cli --------------------------------------------------------------------

def report_lines(funnel: hf.Funnel, policy: dict, as_of: dt.date) -> list[str]:
    cap, limit = policy["approved_unrun_cap_per_goal"], policy["approved_unrun_expiry_days"]
    goals = unrun_by_goal(funnel)
    out = [f"Experiment WIP report as of {as_of} (mode {policy['mode']}, cutoff {policy['cutoff']}, "
           f"cap {cap} per goal, expiry {limit} days)",
           "", f"{'goal':<42}{'unrun':>7}{'cap':>5}{'over':>6}"]
    for goal, rows in sorted(goals.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        out.append(f"{goal:<42}{len(rows):>7}{cap:>5}{max(0, len(rows) - cap):>6}")
    total = sum(len(v) for v in goals.values())
    over = sum(1 for v in goals.values() if len(v) > cap)
    out += ["", f"approved_unrun total {total} in {len(goals)} goals, {over} goals over cap"]
    late = overdue(funnel, policy, as_of)
    unknown = sum(1 for rows in goals.values() for c in rows if c["approval_date"] is None)
    out += ["", f"overdue approved-unrun contracts (older than {limit} days): {len(late)}"
                f"  (age unknown, not counted: {unknown})"]
    for c in late[:50]:
        out.append(f"    {c['id']:<28}{c['goal']:<28}{c['age_days']:>5} days")
    if len(late) > 50:
        out.append(f"    ... {len(late) - 50} more")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--policy", help="policy file (default: coordination/experiment_wip_policy.json under --root)")
    ap.add_argument("--mode", choices=MODES, help="override the policy mode")
    ap.add_argument("--as-of", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--runs-source", choices=("auto", "fs", "git"), default="auto")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--report", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--expire", action="store_true")
    ap.add_argument("--apply", action="store_true", help="with --expire: write the changes (Coordinator action)")
    args = ap.parse_args(argv)
    if args.apply and not args.expire:
        ap.error("--apply only makes sense with --expire")
    as_of = hf.to_date(args.as_of) if args.as_of else dt.date.today()
    if as_of is None:
        ap.error("--as-of must be YYYY-MM-DD")
    root = Path(args.root)
    try:
        policy = load_policy(Path(args.policy) if args.policy else root / POLICY_PATH)
    except PolicyError as exc:
        print(f"policy error: {exc}", file=sys.stderr)
        return 2
    mode = args.mode or policy["mode"]
    funnel = hf.Funnel(root, args.runs_source)

    if args.report:
        print("\n".join(report_lines(funnel, policy, as_of)))
        return 0
    if args.check:
        if mode == "off":
            print("experiment WIP check: mode off, nothing checked")
            return 0
        problems = check(funnel, policy)
        for p in problems:
            print(f"{p['id']}  goal {p['goal']}  approved {p['approved']}  {p['problem']}")
        print(f"experiment WIP check: {len(problems)} problem(s) in contracts approved on or after "
              f"{policy['cutoff']} (mode {mode})")
        return 1 if problems and mode == "enforce" else 0
    rows = expire(funnel, policy, as_of, args.apply and mode != "off")
    for r in rows:
        print(f"{r['id']}  goal {r['goal']}  age {r['age_days']} days  {r['path']}")
        for ch in r["changes"]:
            print(f"    {ch}")
        if r.get("error"):
            print(f"    cannot edit: {r['error']}")
    verb = "applied" if args.apply else "dry run, nothing written"
    print(f"expire: {len(rows)} overdue contract(s), {sum(1 for r in rows if r['applied'])} changed ({verb})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

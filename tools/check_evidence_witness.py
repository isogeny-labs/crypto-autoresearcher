#!/usr/bin/env python3
"""Witness rule for measurement evidence (review 2026-11-10, I6b).

docs/subversion-resistance-20261010.md section 5 proposed that a measurement
run may be cited only if a witness the driver did not write backs it. This
check binds that rule to evidence records (EV-*).

Applies to an evidence record that
  * is dated on or after RULE_FROM (2026-11-11), by `recorded_at`,
    `created_at` or the YYYYMMDD in its id; a record with no date is exempt
    (it cannot be placed after the rule), and
  * makes a measurement claim: it carries a run reference (non-empty
    `run_ids` / `runs`, or a `metrics` / `measured` field, at the top level
    or in an entry of `claims`) and its `type` is a measurement type or it
    states the reference in `claims`.

Such a record needs a `witness:` block:

  kind: sampled_replay
    checker_path, shares_code_with_driver: false, fraction (0 < f <= 1),
    miss_probability (0 <= p <= 1)
  kind: independent_reexecution
    second_implementation_path, metric_agreement (true, or a mapping with
    `agreed: true`)
  kind: certificate
    verifier, certificate_path

Findings are advisories until ADVISORY_UNTIL (2026-12-11) and errors from that
day. Paths named in a witness must exist under the repository root when one is
given. Not enforced: that the checker is in fact independent of the driver,
that the fraction was really replayed, and records with no date.

    python3 tools/check_evidence_witness.py ledger/evidence/EV-X-001.yaml [--today YYYY-MM-DD]

Exit 1 when the file has a finding that is an error on `--today`, else 0.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys

RULE_FROM = "2026-11-11"
ADVISORY_UNTIL = "2026-12-11"
WITNESS_KINDS = ("sampled_replay", "independent_reexecution", "certificate")
MEASUREMENT_TYPES = {
    "empirical", "measurement", "computational", "experimental", "empirical_reanalysis",
    "experiment_results", "derivation_plus_measurement", "mixed", "mixed_exact_derivation_and_finite_controls",
}
RUN_FIELDS = ("run_ids", "runs", "metrics", "measured")
_ID_DATE = re.compile(r"-(\d{8})-")


def _present(value) -> bool:
    return value not in (None, "", [], {}, False)


def _has_run_reference(entry: dict) -> bool:
    return any(_present(entry.get(f)) for f in RUN_FIELDS)


def is_measurement_claim(body: dict) -> bool:
    claims = body.get("claims")
    if isinstance(claims, list) and any(isinstance(c, dict) and _has_run_reference(c) for c in claims):
        return True
    return _has_run_reference(body) and str(body.get("type", "")) in MEASUREMENT_TYPES


def record_date(rec_id: str, body: dict) -> str | None:
    for key in ("recorded_at", "created_at"):
        v = body.get(key)
        if _present(v):
            s = str(v)[:10]
            if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
                return s
    m = _ID_DATE.search(str(rec_id))
    if m:
        d = m.group(1)
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return None


def _path_ok(value, repo_root: str | None) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    return repo_root is None or os.path.exists(os.path.join(repo_root, value))


def witness_problems(body: dict, repo_root: str | None = None) -> list[str]:
    w = body.get("witness")
    if not isinstance(w, dict):
        return ["measurement claim has no `witness:` block (kind: "
                + " | ".join(WITNESS_KINDS) + ")"]
    kind = w.get("kind")
    if kind not in WITNESS_KINDS:
        return [f"witness.kind must be one of {list(WITNESS_KINDS)}, not {kind!r}"]
    out: list[str] = []

    def need_path(field: str):
        if not _path_ok(w.get(field), repo_root):
            out.append(f"witness.{field} must name an existing file" if repo_root
                       else f"witness.{field} must be a non-empty path")

    if kind == "sampled_replay":
        need_path("checker_path")
        if w.get("shares_code_with_driver") is not False:
            out.append("witness.shares_code_with_driver must be false")
        f = w.get("fraction")
        if isinstance(f, bool) or not isinstance(f, (int, float)) or not 0 < f <= 1:
            out.append("witness.fraction must be a number with 0 < fraction <= 1")
        p = w.get("miss_probability")
        if isinstance(p, bool) or not isinstance(p, (int, float)) or not 0 <= p <= 1:
            out.append("witness.miss_probability must be a number in [0, 1]")
    elif kind == "independent_reexecution":
        need_path("second_implementation_path")
        a = w.get("metric_agreement")
        if not (a is True or (isinstance(a, dict) and a.get("agreed") is True)):
            out.append("witness.metric_agreement must be true or a mapping with agreed: true")
    else:
        if not isinstance(w.get("verifier"), str) or not w["verifier"].strip():
            out.append("witness.verifier must name the verifier")
        need_path("certificate_path")
    return out


def check_evidence_witness(ctx, today: str | None = None, repo_root: str | None = None) -> None:
    """validate_ledger check: `today` is YYYY-MM-DD (or YYYYMMDD); default is today's date."""
    if today:
        t = today if "-" in today else f"{today[:4]}-{today[4:6]}-{today[6:]}"
    else:
        t = _dt.date.today().isoformat()
    enforce = t >= ADVISORY_UNTIL
    for rec_id, kind in ctx.record_types.items():
        if kind != "evidence":
            continue
        body = ctx.records[rec_id]
        when = record_date(rec_id, body)
        if when is None or when < RULE_FROM or not is_measurement_claim(body):
            continue
        for problem in witness_problems(body, repo_root):
            msg = f"{rec_id}: {problem} (witness rule, from {RULE_FROM}; error from {ADVISORY_UNTIL})"
            (ctx.err if enforce else ctx.advise)(ctx.ids[rec_id], msg)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--today", default=None, help="YYYY-MM-DD (default: the current date)")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args(argv)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import yaml  # noqa: PLC0415
    with open(a.file, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    body = doc.get("evidence", doc) if isinstance(doc, dict) else None
    if not isinstance(body, dict):
        print(f"{a.file}: not an evidence record", file=sys.stderr)
        return 3

    class _Ctx:
        def __init__(self):
            self.errors, self.advisories = [], []
            rid = str(body.get("id", os.path.basename(a.file)))
            self.record_types, self.records, self.ids = {rid: "evidence"}, {rid: body}, {rid: a.file}

        def err(self, path, msg): self.errors.append(msg)
        def advise(self, path, msg): self.advisories.append(msg)

    ctx = _Ctx()
    check_evidence_witness(ctx, a.today, a.root)
    for m in ctx.advisories:
        print(f"advisory: {m}")
    for m in ctx.errors:
        print(f"error: {m}")
    print(f"evidence-witness: {len(ctx.errors)} error(s), {len(ctx.advisories)} advisory(ies)")
    return 1 if ctx.errors else 0


if __name__ == "__main__":
    sys.exit(main())

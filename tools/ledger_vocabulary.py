#!/usr/bin/env python3
"""Controlled vocabularies for ledger records: one source of truth.

Every enumerated field the validator enforces is defined here:

  hypothesis_status     schemas/hypothesis.schema.json (status enum), which
                        equals the hypothesis state list in AGENTS.md
                        "Research states" plus `rejected_scoped`
  experiment_status     AGENTS.md "Research states" (experiment states) plus
                        the two extra values of schemas/experiment.schema.json
                        (`amended`, `cancelled`)
  evidence_direction    schemas/evidence.schema.json (direction enum)
  evidence_strength     schemas/evidence.schema.json (strength enum)
  claim_tier            docs/claims-and-verification.md tiers plus `theory`
                        and `not_applicable` (see CLAIM_TIERS)
  proof_status          the set tools/validate_ledger.py has always accepted

The schema files are read when present; the constants below are the fallback
for a standalone copy of the validator and must equal the schema enums (a test
checks that they do).

From VOCABULARY_CUTOFF on, a record whose own date falls on or after the
cutoff must use a canonical value (tools/validate_ledger.py,
check_vocabulary). Older records are tallied as advisories, never failures.
`normalize` maps a value to its canonical form: a canonical value maps to
itself, a frequent legacy variant whose meaning is unambiguous maps through
LEGACY, and anything else returns None.

    python3 tools/ledger_vocabulary.py          # print the histogram
    python3 tools/ledger_vocabulary.py --json   # the same, as JSON
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO, "schemas")

VOCABULARY_CUTOFF = "2026-11-08"

# AGENTS.md "Research states". Hypotheses:
#   proposed -> specified -> approved -> running -> analyzed -> replicated ->
#   supported | weakened | rejected | inconclusive | superseded
# `rejected_scoped` is added because the coordinator decision vocabulary
# records `reject_scoped` outcomes, and three hypotheses already carry it.
HYPOTHESIS_STATES = (
    "proposed", "specified", "approved", "running", "analyzed", "replicated",
    "supported", "weakened", "rejected", "inconclusive", "superseded",
)
HYPOTHESIS_STATUSES_FALLBACK = frozenset(HYPOTHESIS_STATES + ("rejected_scoped",))

# Experiments:
#   draft -> review_required -> approved -> running -> completed |
#   failed_infrastructure | invalid -> analyzed -> archived
EXPERIMENT_STATES = (
    "draft", "review_required", "approved", "running", "completed",
    "failed_infrastructure", "invalid", "analyzed", "archived",
)
# schemas/experiment.schema.json also admits these two terminal states.
EXPERIMENT_SCHEMA_EXTRA = ("amended", "cancelled")
EXPERIMENT_STATUSES = frozenset(EXPERIMENT_STATES + EXPERIMENT_SCHEMA_EXTRA)

EVIDENCE_DIRECTIONS_FALLBACK = frozenset(
    {"supports", "weakens", "contradicts", "neutral"})
EVIDENCE_STRENGTHS_FALLBACK = frozenset(
    {"anecdotal", "preliminary", "replicated", "strong", "inconclusive",
     "contradictory"})

# toy | medium | crypto are the scale tiers of docs/claims-and-verification.md
# and templates/research-records.md (tools/validate_ledger.py TIER_ORDER).
# `theory` labels evidence with no measured scale (a derivation or a design
# review; 50 records). `not_applicable` labels coordination and protocol
# evidence that asserts nothing at any scale (86 records), and mirrors
# proof_status `not_applicable`.
CLAIM_TIERS = frozenset({"toy", "theory", "medium", "crypto", "not_applicable"})

# Accepted by tools/validate_ledger.py since proof fields became mandatory.
PROOF_STATUSES = frozenset(
    {"certificate", "derivation", "empirical_only", "not_applicable"})

# Tiers at which supporting evidence must name a positive control.
CALIBRATED_TIERS = frozenset({"medium", "crypto"})

# Frequent legacy variants whose meaning is unambiguous. Values left out
# (e.g. direction `mixed`, strength `moderate`, `n/a` or `single_run`, tier
# `measured-single-host`) have no single canonical reading: `mixed` is not one
# direction, `moderate` sits between two strengths, and `measured-single-host`
# names where the instrument ran, not the scale tested, so the tier must be
# restated, not guessed.
LEGACY: dict[str, dict[str, str]] = {
    "hypothesis_status": {
        "supported_scoped": "supported",
    },
    "experiment_status": {
        "executed": "completed",
        "external_completed": "completed",
        "proposed": "draft",
    },
    "evidence_direction": {
        "refutes": "contradicts",
        "confirms": "supports",
        "corroborating": "supports",
        "supports_strongly": "supports",
        "supporting_scoped": "supports",
        "supportive_scoped": "supports",
        "weakening_scoped": "weakens",
        "none": "neutral",
    },
    "claim_tier": {
        "toy_measurement": "toy",
        "toy_scale": "toy",
        "measurement_toy_scale": "toy",
        "toy_design_only": "toy",
        "theoretical": "theory",
        "theoretical_analysis": "theory",
    },
    "proof_status": {
        "derivation_repaired": "derivation",
        "derived_and_independently_reworked": "derivation",
    },
}

# (record type, field) -> vocabulary kind.
FIELDS: dict[tuple[str, str], str] = {
    ("hypothesis", "status"): "hypothesis_status",
    ("experiment", "status"): "experiment_status",
    ("evidence", "direction"): "evidence_direction",
    ("evidence", "strength"): "evidence_strength",
    ("evidence", "claim_tier"): "claim_tier",
    ("evidence", "proof_status"): "proof_status",
}

# Date fields, in precedence order, that date a record for the cutoff. The
# id's embedded YYYYMMDD is the last resort.
DATE_FIELDS = ("updated", "created", "specified_at", "recorded_at", "added",
               "approved_at")


def _schema_enum(name: str, record_key: str, field: str):
    try:
        with open(os.path.join(SCHEMA_DIR, name), encoding="utf-8") as fh:
            schema = json.load(fh)
        enum = schema["properties"][record_key]["properties"][field]["enum"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if isinstance(enum, list) and all(isinstance(v, str) for v in enum):
        return frozenset(enum)
    return None


def _load() -> dict[str, frozenset]:
    return {
        "hypothesis_status": _schema_enum("hypothesis.schema.json",
                                          "hypothesis", "status")
        or HYPOTHESIS_STATUSES_FALLBACK,
        "experiment_status": EXPERIMENT_STATUSES,
        "evidence_direction": _schema_enum("evidence.schema.json",
                                           "evidence", "direction")
        or EVIDENCE_DIRECTIONS_FALLBACK,
        "evidence_strength": _schema_enum("evidence.schema.json",
                                          "evidence", "strength")
        or EVIDENCE_STRENGTHS_FALLBACK,
        "claim_tier": CLAIM_TIERS,
        "proof_status": PROOF_STATUSES,
    }


_CANONICAL = _load()


def kinds() -> tuple[str, ...]:
    return tuple(_CANONICAL)


def canonical(kind: str) -> frozenset:
    """The canonical value set of a vocabulary kind (KeyError if unknown)."""
    return _CANONICAL[kind]


def normalize(kind: str, value) -> str | None:
    """Canonical form of `value`, or None when it has no unambiguous one."""
    if not isinstance(value, str):
        return None
    allowed = _CANONICAL[kind]
    if value in allowed:
        return value
    key = value.strip().lower()
    if key in allowed:
        return key
    mapped = LEGACY.get(kind, {}).get(key)
    return mapped if mapped in allowed else None


def _date_text(value) -> str | None:
    """YYYY-MM-DD from a date, datetime or ISO-ish string, else None."""
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        value = value.isoformat()
    text = str(value).strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-" \
            and text[:4].isdigit() and text[5:7].isdigit() and text[8:10].isdigit():
        return text[:10]
    return None


def record_date(body: dict, id_date=None) -> str | None:
    """The record's own date as YYYY-MM-DD (first DATE_FIELDS, then id)."""
    for field in DATE_FIELDS:
        found = _date_text(body.get(field))
        if found:
            return found
    if id_date is not None:
        compact = id_date(str(body.get("id") or ""))
        if compact:
            return f"{compact[:4]}-{compact[4:6]}-{compact[6:8]}"
    return None


def is_gated(body: dict, id_date=None) -> bool:
    found = record_date(body, id_date)
    return bool(found) and found >= VOCABULARY_CUTOFF


def names_positive_control(body: dict) -> bool:
    """True when the record names a positive control or calibration."""
    controls = body.get("controls")
    if isinstance(controls, dict) and controls.get("positive") not in (None, "", [], {}):
        return True
    for key in ("positive_control", "instrument_calibration"):
        if body.get(key) not in (None, "", [], {}):
            return True
    return False


# ---- histogram over the ledger ---------------------------------------------

_SOURCES = (
    ("hypothesis", os.path.join("ledger", "hypotheses", "*.yaml")),
    ("evidence", os.path.join("ledger", "evidence", "*.yaml")),
    ("experiment", os.path.join("experiments", "*", "specification.yaml")),
)


def _safe_load(path: str):
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.load(fh, Loader=loader)
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None


def record_body(doc, rec_type: str) -> dict | None:
    """The record mapping: nested under the type key, or flat; else None."""
    if not isinstance(doc, dict):
        return None  # a bare string, a list, an empty file
    nested = doc.get(rec_type)
    if isinstance(nested, dict):
        return nested
    return doc


def _label(value) -> str:
    if value is None:
        return "<missing>"
    if isinstance(value, str):
        return value
    return f"<{type(value).__name__}>"


def histogram(repo: str = REPO) -> dict:
    """{(type, field): Counter(value -> count)} plus per-type file counts."""
    counts: dict[tuple[str, str], collections.Counter] = {
        key: collections.Counter() for key in FIELDS}
    files: dict[str, collections.Counter] = {}
    for rec_type, pattern in _SOURCES:
        tally = files.setdefault(rec_type, collections.Counter())
        for path in sorted(glob.glob(os.path.join(repo, pattern))):
            body = record_body(_safe_load(path), rec_type)
            if body is None:
                tally["skipped"] += 1
                continue
            tally["read"] += 1
            for (kind_type, field) in FIELDS:
                if kind_type == rec_type:
                    counts[(kind_type, field)][_label(body.get(field))] += 1
    return {"counts": counts, "files": files}


def format_histogram(result: dict, width: int = 100) -> list[str]:
    lines = []
    for rec_type, tally in result["files"].items():
        lines.append(f"{rec_type}: {tally.get('read', 0)} record(s) read, "
                     f"{tally.get('skipped', 0)} skipped (unparsable or not "
                     "a mapping)")
    for (rec_type, field), counter in result["counts"].items():
        kind = FIELDS[(rec_type, field)]
        total = sum(counter.values())
        canon = sum(n for v, n in counter.items() if v in canonical(kind))
        lines.append("")
        lines.append(f"{rec_type}.{field} ({kind}): {total} record(s), "
                     f"{len(counter)} distinct, {canon} canonical; canonical "
                     f"set {'|'.join(sorted(canonical(kind)))}")
        for value, n in counter.most_common():
            if value in canonical(kind):
                mark = "ok"
            elif normalize(kind, value):
                mark = f"-> {normalize(kind, value)}"
            else:
                mark = "??"
            shown = value if len(value) <= width else value[:width - 3] + "..."
            lines.append(f"  {n:6d}  {mark:16s} {shown}")
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    result = histogram()
    if args.json:
        print(json.dumps({
            "cutoff": VOCABULARY_CUTOFF,
            "canonical": {k: sorted(canonical(k)) for k in kinds()},
            "files": {k: dict(v) for k, v in result["files"].items()},
            "counts": {f"{t}.{f}": dict(c.most_common())
                       for (t, f), c in result["counts"].items()},
        }, indent=2))
    else:
        print("\n".join(format_histogram(result)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Compose findings.yaml (sheriff.case/v1) for SHF-20261106-a114e7.

Reader claims and findings are imported verbatim from readers/*.yaml, with claim
ids namespaced by reader (<reader>/<id>) so ids from different readers cannot
collide. The composing session's own claims and findings come from session.yaml.
Normalisation, all recorded in each claim's `composition_note`:
  * a beat state outside {pass, fail, not_covered, n/a} becomes not_covered;
  * `upheld` with any not_covered beat becomes `upheld_scoped` (never a pass);
  * an upheld* claim with a failed beat becomes `overclaimed` (a failed beat
    forbids upheld) - the composer never rounds up.
Writes only inside the case directory.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

CASE = Path(__file__).resolve().parents[1]
REL = "research/sheriff/" + CASE.name
STATES = {"pass", "fail", "not_covered", "n/a"}
VERDICTS = {"upheld", "upheld_scoped", "overclaimed", "unsupported", "broken", "not_covered"}
BEATS = {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"}


def norm_beats(beats):
    out, notes = {}, []
    for b, s in (beats or {}).items():
        b = str(b).split()[0].rstrip(":")
        if b not in BEATS:
            notes.append(f"dropped unknown beat key {b!r}")
            continue
        s = str(s).split()[0].rstrip(",;:") if s is not None else "not_covered"
        if s not in STATES:
            notes.append(f"{b}: {s!r} -> not_covered")
            s = "not_covered"
        out[b] = s
    return out, notes


def main() -> int:
    claims, findings, prior, readers = [], [], [], []
    for path in sorted((CASE / "readers").glob("*.yaml")):
        name = path.stem
        doc = yaml.safe_load(path.read_text())
        rd = doc.get("reader") or {}
        readers.append({"role": rd.get("role"), "model": rd.get("model"), "joint": doc.get("joint"),
                        "report": f"readers/{path.name}"})
        ids = {str(c.get("id")) for c in doc.get("claims") or []}
        fids = set()
        for f in doc.get("findings") or []:
            f = dict(f)
            f["reader"] = f"readers/{path.name}"
            f["claim_ids"] = [f"{name}/{x}" for x in f.get("claim_ids") or [] if str(x) in ids]
            beat = str(f.get("beat", "")).split()[0]
            f["beat"] = beat if beat in BEATS else "B9"
            fids.add(f["id"])
            findings.append(f)
        for c in doc.get("claims") or []:
            cid = f"{name}/{c.get('id')}"
            verdict = c.get("suggested_verdict") or c.get("verdict")
            beats, notes = norm_beats(c.get("beats"))
            if verdict not in VERDICTS:
                notes.append(f"verdict {verdict!r} -> not_covered")
                verdict = "not_covered"
            if verdict == "upheld" and any(s == "not_covered" for s in beats.values()):
                verdict = "upheld_scoped"
                notes.append("upheld -> upheld_scoped: a not_covered beat is never a pass")
            if verdict in ("upheld", "upheld_scoped") and any(s == "fail" for s in beats.values()):
                verdict = "overclaimed"
                notes.append("upheld* with a failed beat -> overclaimed")
            linked = [x for x in (c.get("findings") or []) if x in fids]
            linked += [f["id"] for f in findings if cid in f["claim_ids"] and f["id"] not in linked]
            scoped = c.get("scoped_to")
            if verdict in ("upheld_scoped", "overclaimed") and not scoped:
                scoped = f"As stated in {path.name} for this claim; see the reader's checks."
                notes.append("scoped_to supplied by composer from the reader file")
            entry = {"id": cid, "text": str(c.get("text") or "").strip(),
                     "location": str(c.get("location") or "").strip() or f"see readers/{path.name}",
                     "verdict": verdict, "beats": beats or {"B9": "not_covered"},
                     "evidence": [f"{REL}/readers/{path.name}"], "findings": linked, "reader": f"readers/{path.name}"}
            sdir = CASE / "scripts" / "readers" / name
            if sdir.is_dir():
                entry["evidence"].append(f"{REL}/scripts/readers/{name}")
            if scoped:
                entry["scoped_to"] = scoped
            if verdict in ("overclaimed", "unsupported", "broken") and not linked:
                notes.append("no reader finding linked; linked to composer finding SES-UNLINKED")
                entry["findings"] = ["SES-UNLINKED"]
            if notes:
                entry["composition_note"] = notes
            claims.append(entry)
        for p in doc.get("prior_finding_verdicts") or []:
            prior.append({**p, "reader": f"readers/{path.name}"})

    session = yaml.safe_load((CASE / "scripts" / "session.yaml").read_text())
    findings.extend(session["findings"])
    claims.extend(session["claims"])
    prior.extend(session.get("prior_finding_verdicts") or [])
    readers.append(session["reader"])
    if not any(c.get("findings") == ["SES-UNLINKED"] for c in claims):
        findings = [f for f in findings if f["id"] != "SES-UNLINKED"]

    body = {"schema": "sheriff.case/v1", "id": CASE.name, **session["header"],
            "readers": readers, "prior_finding_verdicts": prior, "claims": claims,
            "findings": findings, "lead_dispositions": session["lead_dispositions"]}
    (CASE / "findings.yaml").write_text(yaml.safe_dump({"sheriff_case": body}, sort_keys=False,
                                                        allow_unicode=True, width=100))
    from collections import Counter
    print("claims", len(claims), dict(Counter(c["verdict"] for c in claims)))
    print("findings", len(findings), dict(Counter(f["severity"] for f in findings)))
    print("prior", len(prior), dict(Counter(p["verdict"] for p in prior)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

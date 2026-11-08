#!/usr/bin/env python3
"""Replay the syntax-only 2026-11-08 legacy corrections against frozen sources."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = "ledger/corrections/schema-supersessions/20261108"
H_IDS = (
    "H-BKKMV-001", "H-DREG-001", "H-EQJ-001", "H-FB3-001",
    "H-ICI-001", "H-R6-001", "H-REP-001", "H-SIG-001",
)
RQ_IDS = (
    "RQ-DREG-001", "RQ-FB3-001", "RQ-ISO-001", "RQ-R6-001",
    "RQ-SIG-001", "RQ-TTN-001",
)
CORR_ID = "CORR-20260727-004"


def source(path: str) -> str:
    file = ROOT / path
    if file.is_file():
        return file.read_text(encoding="utf-8")
    # Sparse worktrees omit the archived source. The exact commit blob is still
    # available; the registry hash below prevents a different blob being used.
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", "HEAD:" + path], text=True)


def split_flow(text: str) -> list[str]:
    pieces: list[str] = []
    start = depth = 0
    quote = None
    for index, char in enumerate(text):
        if char in "\"'":
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
        elif quote is None:
            if char in "({[":
                depth += 1
            elif char in ")}]":
                depth -= 1
            elif char == "," and depth == 0:
                pieces.append(text[start:index].strip())
                start = index + 1
    pieces.append(text[start:].strip())
    return [item[1:-1] if len(item) >= 2 and item[0] == item[-1]
            and item[0] in "\"'" else item for item in pieces]


def repair(rid: str, raw: str) -> str:
    if rid == "RQ-DREG-001":
        raw = raw.replace(
            "    - Subset-column rank is INVALID for the sem arm (h012 finding iv): only\n"
            "      full-column exact ranks are evidence.",
            "    - >-\n"
            "      Subset-column rank is INVALID for the sem arm (h012 finding iv): only\n"
            "      full-column exact ranks are evidence.")
    if rid == "H-DREG-001":
        raw = raw.replace(
            "    - The block-m4ri instrument computes exact full-column rank over GF(2);\n"
            "      validated",
            "    - >-\n"
            "      The block-m4ri instrument computes exact full-column rank over GF(2);\n"
            "      validated")
    if rid == "H-ICI-001":
        raw = raw.replace(
            "    - Both paths' CI lower bounds > 0.5 at the extended ladder: quantified KILL;\n",
            "    - >-\n"
            "      Both paths' CI lower bounds > 0.5 at the extended ladder: quantified KILL;\n")
    if rid == "H-FB3-001":
        raw = raw.replace("      with bootstrap CI and permutation-null band",
                          "        with bootstrap CI and permutation-null band")
    if rid == "H-R6-001":
        raw = raw.replace("      unconstrained ladder", "        unconstrained ladder")
    if rid == "H-SIG-001":
        raw = raw.replace("      per n, per panel family", "        per n, per panel family")
    if rid in {"H-DREG-001", "H-FB3-001", "H-R6-001", "H-SIG-001"}:
        lines = []
        in_list = False
        for line in raw.splitlines():
            if line == "  falsification_conditions:" or (
                    rid == "H-SIG-001" and line == "  interpretation_limits:"):
                in_list = True
            elif in_list and line.startswith("  ") and not line.startswith("    "):
                in_list = False
            if in_list and line.startswith("    - "):
                lines.extend(("    - >-", "      " + line[6:]))
            else:
                lines.append(line)
        raw = "\n".join(lines) + "\n"
    if rid == CORR_ID:
        return raw.replace(
            '      - "snapshot before review" (unearned; no dispatcher receipt exists under INT-BATCH007-T / INT-BATCH008-C)',
            '      - >-\n'
            '        "snapshot before review" (unearned; no dispatcher receipt exists under INT-BATCH007-T / INT-BATCH008-C)')
    lines = []
    for line in raw.splitlines():
        match = re.match(r"^(\s+)([a-z_]+): \[(.*)\]$", line)
        if match:
            # Keep valid YAML flow lists byte-for-byte, especially numeric
            # seeds and exponents. Only malformed flow syntax is rewritten.
            try:
                yaml.safe_load(line.strip())
            except yaml.YAMLError:
                indent, key, content = match.groups()
                lines.append(f"{indent}{key}:")
                lines.extend(f"{indent}  - {json.dumps(item, ensure_ascii=False)}"
                             for item in split_flow(content))
            else:
                lines.append(line)
        elif rid == "RQ-TTN-001" and line.startswith("  motivation: Candidate C2 "):
            lines.extend(("  motivation: >-", "    " + line[len("  motivation: "):]))
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def main() -> None:
    registry = yaml.safe_load((ROOT / "tools/schema_supersession_registry.yaml").read_text())
    rows = {row["superseded_path"]: row for row in registry["records"]}
    for rid in (*H_IDS, *RQ_IDS, CORR_ID):
        path = (f"ledger/corrections/{rid}.yaml" if rid == CORR_ID
                else f"ledger/{rid}.yaml")
        suffix = (f"ledger__corrections__{rid}.v2.yaml" if rid == CORR_ID
                  else f"ledger__{rid}.v2.yaml")
        replacement = f"{OUT}/{suffix}"
        row = rows[path]
        original = source(path).encode()
        expected = repair(rid, original.decode()).encode()
        actual = (ROOT / replacement).read_bytes()
        assert row["superseding_path"] == replacement
        assert hashlib.sha256(original).hexdigest() == row["superseded_sha256"]
        assert hashlib.sha256(actual).hexdigest() == row["superseding_sha256"]
        assert actual == expected, f"syntax replay changed: {replacement}"
        doc = yaml.safe_load(actual)
        key = ("correction" if rid == CORR_ID else "hypothesis" if rid in H_IDS
               else "research_question")
        assert doc[key]["id"] == rid
    print(f"replayed {len(H_IDS) + len(RQ_IDS) + 1} hash-bound corrections")


if __name__ == "__main__":
    main()

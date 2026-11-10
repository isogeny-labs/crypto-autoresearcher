#!/usr/bin/env python3
"""wdag selection pass for cells with 21 <= N <= 26 (DR-8).

Rule (pre-registered, a function of N and a nonce, never of an outcome other
than "contained"): among the contained decisive instances of the cell (arms
EQS4 and EQS4-U, distinct instances, sorted by key), take
    i = int(sha256(protocol_sha256 + "\nWDAG\n" + cell_id)) mod n,
the instance at index i and the one at (i + 1) mod n; if n < 2 take them all.
Each selected instance gets one wdag certificate in a child process (wall cap
900 s, JSON cap 400 MB, 10 GB RSS watchdog); a guard trip records not_emitted
and never touches M-1.

    python3 certify.py --run-dir DIR --cell m3n13 --protocol-sha256 HEX [--no-isolate]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os

import cells as CE
import enumz
import run as RUN
from analyze import read_gz_jsonl


def select_keys(protocol_sha256: str, cell_id: str, contained_keys: list) -> list:
    keys = sorted(contained_keys)
    if len(keys) <= 2:
        return keys
    i = int(hashlib.sha256((protocol_sha256 + "\nWDAG\n" + cell_id).encode()).hexdigest(), 16) % len(keys)
    return [keys[i], keys[(i + 1) % len(keys)]]


def contained_decisive(run_dir, cell_id):
    inst = {d["key"]: d for d in read_gz_jsonl(os.path.join(run_dir, "instances.jsonl.gz")) if "N" in d}
    out = {}
    for d in read_gz_jsonl(os.path.join(run_dir, "closures.jsonl.gz")):
        k = d.get("key", "")
        if d.get("D") == 4 and d.get("status") == "ok" and k in inst and inst[k]["cell"] == cell_id \
                and inst[k]["arm"] in ("EQS4", "EQS4-U") and (d.get("M1") or {}).get("contained") is True:
            out[k] = d["engine"]["final_dim"]
    return inst, out


def run_selection(run_dir, cell, protocol_sha256, isolate=True, enforce_range=True):
    class a:      # noqa: N801  (argument bag)
        pass
    a.run_dir, a.cell, a.protocol_sha256, a.no_isolate = run_dir, cell, protocol_sha256, not isolate
    N = CE.CELLS[a.cell]["N"]
    if enforce_range and not 21 <= N <= 26:
        raise SystemExit(f"selection pass applies to 21 <= N <= 26 (N = {N})")
    inst, contained = contained_decisive(a.run_dir, a.cell)
    chosen = select_keys(a.protocol_sha256, a.cell, list(contained))
    cfile = os.path.join(a.run_dir, "closures.jsonl.gz")
    costfile = os.path.join(a.run_dir, "cost.jsonl")
    done = {d["key"] for d in read_gz_jsonl(cfile) if d.get("kind") == "certificate" and d.get("cert_kind") == "wdag"
            and d["M8"]["status"] in ("pending_checker", "accepted", "rejected", "not_emitted")}
    res = []
    for key in chosen:
        if key in done:
            res.append({"key": key, "skipped": "already has a wdag record"})
            continue
        rec = inst[key]
        sysb = gzip.decompress(open(os.path.join(a.run_dir, rec["system_file"]["path"]), "rb").read())
        obj = json.loads(sysb)
        eqs = [sorted(sum(1 << i for i in mono) for mono in e) for e in obj["eqs"]]
        Z = sorted(int(h, 16) for h in rec["Z_hex"])
        gens = enumz.gb_polys(enumz.groebner_from_Z(Z, rec["N"]))
        info = RUN.emit_certificate(a.run_dir, cfile, costfile, key, a.cell, "wdag", 4, rec["N"], eqs, Z, gens,
                                    rec["meta"], contained[key], isolate=not a.no_isolate)
        res.append({"key": key, "status": info["status"]})
    return {"cell": a.cell, "contained_decisive": len(contained), "selected": chosen, "results": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--cell", required=True)
    ap.add_argument("--protocol-sha256", required=True)
    ap.add_argument("--no-isolate", action="store_true")
    a = ap.parse_args()
    print(json.dumps(run_selection(a.run_dir, a.cell, a.protocol_sha256, isolate=not a.no_isolate)))


if __name__ == "__main__":
    main()

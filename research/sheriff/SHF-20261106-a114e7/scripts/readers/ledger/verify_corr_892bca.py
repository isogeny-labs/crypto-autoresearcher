#!/usr/bin/env python3
"""Re-check every git fact CORR-20261029-892bca states about the splice of
RBS-ICPERF-b7e41c, from git objects only (read-only).

Sheriff case SHF-20261106-a114e7, ledger reader (joint LGX).
"""
import hashlib
import json
import subprocess

REPO = "/home/user/crypto-autoresearcher"
S = "experiments/EXP-ICPERF-e467a5/runbook-sessions/RBS-ICPERF-b7e41c"
ERR = f"{S}/steps/S02-trials.attempt-1.supervisor.stderr"
J = f"{S}/journal.jsonl"
MAIN = "da442739db"


def git(*a, binary=False):
    out = subprocess.run(["git", "-C", REPO, *a], capture_output=True, check=False).stdout
    return out if binary else out.decode().strip()


def blob(rev, path):
    return git("rev-parse", "--verify", "--quiet", f"{rev}:{path}") or None


def entries(blob_id):
    return [json.loads(line) for line in git("cat-file", "blob", blob_id, binary=True).decode().splitlines() if line.strip()]


def bound(es):
    out = {}
    for e in es:
        if e.get("type") in ("step_finished", "step_interrupted"):
            for item in (e.get("outputs") or []) + (e.get("logs") or []):
                out[item["path"]] = item.get("sha256")
    return out


R = {}
for rev in ("93b87120f6", "2d3948be7f", "0186e97db6", MAIN):
    R[f"stderr blob at {rev}"] = (blob(rev, ERR) or "absent")[:10]
    R[f"journal blob at {rev}"] = (blob(rev, J) or "absent")[:10]
data = git("cat-file", "blob", blob(MAIN, ERR), binary=True)
R["stderr at main: sha256, bytes"] = [hashlib.sha256(data).hexdigest(), len(data)]
R["stderr at main: text"] = data.decode(errors="replace")
jb_B, jb_A = blob(MAIN, J), blob("93b87120f6", J)
eB, eA = entries(jb_B), entries(jb_A)
R["journal B (main): tip hash, started, owner"] = [eB[-1].get("hash"), eB[0].get("time"), eB[0].get("owner")]
R["journal A (93b87120f6): tip hash, started, owner"] = [eA[-1].get("hash"), eA[0].get("time"), eA[0].get("owner")]
bB, bA = bound(eB), bound(eA)
R["B records for stderr"] = bB.get(ERR)
R["A records for stderr"] = bA.get(ERR)
# Files B binds that sit in the session dir, and how many match main's bytes.
match = {}
for path, digest in bB.items():
    b = blob(MAIN, path)
    actual = hashlib.sha256(git("cat-file", "blob", b, binary=True)).hexdigest() if b else None
    match[path.replace(S + "/", "")] = actual == digest
R["B-bound files: matches at main"] = match
R["B-bound count / matching"] = [len(match), sum(match.values())]
R["merge 0186e97db6 parents"] = git("log", "-1", "--format=%P", "0186e97db6")
R["merge 0186e97db6 subject"] = git("log", "-1", "--format=%s", "0186e97db6")
p1, p2 = R["merge 0186e97db6 parents"].split()
mb = git("merge-base", p1, p2)
R["merge base"] = mb[:10]
R["session dir at merge base"] = git("ls-tree", "--name-only", mb, S + "/") or "absent"
for name in ("journal.jsonl", "environment.json", "steps/S02-trials.attempt-1.claim.stdout",
             "steps/S02-trials.attempt-1.release.stdout", "steps/S02-trials.attempt-1.supervisor.stderr"):
    path = f"{S}/{name}"
    m, a, b = blob("0186e97db6", path), blob(p1, path), blob(p2, path)
    R[f"merge result for {name}"] = ("= parent2 (B side)" if m == b and m != a else
                                     "= parent1 (A side)" if m == a and m != b else
                                     "both equal" if m == a == b else f"other {m} {a} {b}")
R["stderr at parent2 (B side)"] = (blob(p2, ERR) or "absent")[:10]
# First first-parent commit of main that contains the splice merge.
fp = git("rev-list", "--first-parent", "--reverse", f"0186e97db6~1..{MAIN}").split()
for c in fp:
    if subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", "0186e97db6", c]).returncode == 0:
        R["first main first-parent commit containing 0186e97db6"] = [c[:10], git("log", "-1", "--format=%s", c)]
        break
# RUN-ICPERF-943efa: four bound digests vs journal unit (seq 4) and receipt.
units = [e for e in eB if e.get("type") == "unit_recorded"]
R["B unit_recorded seqs"] = [u.get("seq") for u in units]
u = units[-1]
rd = u["run_dir"]
arts = u.get("artifacts") or {}
cmp_ = {}
for name, digest in arts.items():
    b = blob(MAIN, f"{rd}/{name}")
    actual = hashlib.sha256(git("cat-file", "blob", b, binary=True)).hexdigest() if b else None
    cmp_[name] = actual == digest
R["943efa artifacts bound by journal unit (name: equal at main)"] = cmp_
rb = blob(MAIN, f"{rd}/execution-receipt.json")
receipt = json.loads(git("cat-file", "blob", rb, binary=True))
rec_art = receipt.get("artifact_sha256") or {}
R["943efa receipt artifact_sha256 vs journal unit"] = {k: rec_art.get(k) == v for k, v in arts.items()}
R["943efa receipt sha256 vs journal receipt_sha256"] = (
    hashlib.sha256(git("cat-file", "blob", rb, binary=True)).hexdigest() == u.get("receipt_sha256"))
print(json.dumps(R, indent=1))

#!/usr/bin/env python3
"""Blind re-derivation of `tools/runbook.py pending-audits` from its statement
alone (docs/runbook-execution.md: "lists finished sessions whose current
journal tip has no audit"), without reading the tool's implementation.

Reads git objects of one commit only. A session is any */runbook-sessions/*/
journal.jsonl; it is finished when its journal has a session_finished entry;
its tip is the `hash` of its last entry. An audit is any audit.json in the tree
with a runbook_audit schema whose session_dir names the session and whose
journal_tip equals the tip. Prints JSON: sessions, audits and the pending set,
plus a proves-too-much control (dropping each session's audits must make every
finished session pending).

Sheriff case SHF-20261106-a114e7, ledger reader (joint LGX).
"""
import json
import subprocess
import sys

REPO, REV = sys.argv[1], sys.argv[2]


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, check=True).stdout


paths = git("ls-tree", "-r", "-z", "--name-only", REV).decode().split("\0")
journals = [p for p in paths if "/runbook-sessions/" in p and p.endswith("/journal.jsonl")
            and p.count("/runbook-sessions/") == 1 and p.split("/runbook-sessions/")[1].count("/") == 1]
audit_files = [p for p in paths if p.endswith("/audit.json")]
sessions = {}
for j in journals:
    lines = [json.loads(x) for x in git("cat-file", "blob", f"{REV}:{j}").decode().splitlines() if x.strip()]
    sdir = j.rsplit("/", 1)[0]
    sessions[sdir] = {"entries": len(lines),
                      "finished": any(e.get("type") == "session_finished" for e in lines),
                      "tip": lines[-1].get("hash") if lines else None,
                      "status": next((e.get("status") for e in lines if e.get("type") == "session_finished"), None),
                      "audits_of_tip": [], "audits_of_other_tips": []}
audits = []
for a in audit_files:
    try:
        doc = json.loads(git("cat-file", "blob", f"{REV}:{a}"))
    except ValueError:
        continue
    if not isinstance(doc, dict) or "runbook_audit" not in str(doc.get("schema")):
        continue
    audits.append(a)
    s = sessions.get(doc.get("session_dir"))
    if s is None:
        continue
    (s["audits_of_tip"] if doc.get("journal_tip") == s["tip"] else s["audits_of_other_tips"]).append(a)
pending = sorted(d for d, s in sessions.items() if s["finished"] and not s["audits_of_tip"])
control = sorted(d for d, s in sessions.items() if s["finished"])  # with every audit dropped
print(json.dumps({"rev": REV, "sessions": sessions, "runbook_audits_found": len(audits),
                  "pending": pending,
                  "control_all_audits_dropped_pending": control,
                  "control_passes": set(control) >= set(pending) and len(control) == sum(
                      s["finished"] for s in sessions.values())}, indent=1))

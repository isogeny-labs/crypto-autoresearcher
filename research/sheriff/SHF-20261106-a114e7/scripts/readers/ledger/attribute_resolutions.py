#!/usr/bin/env python3
"""For each path carrying one of the 67 validate_ledger errors at b7d5e65b9f,
say how it stopped erroring at da442739db: whether the path's bytes changed
(an in-place edit of a sealed record), whether a run- or schema-supersession
registry entry naming it was added, and which first-parent merge on main
introduced that entry. Read-only git queries; prints JSON.

Sheriff case SHF-20261106-a114e7, ledger reader.
"""
import json
import subprocess
import sys

REPO = "/home/user/crypto-autoresearcher"
OLD, NEW = "b7d5e65b9f", "da442739db"
REGISTRIES = ("tools/run_supersession_registry.yaml",
              "tools/schema_supersession_registry.yaml")


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                          text=True, check=False).stdout


def blob(rev, path):
    return git("rev-parse", "--verify", "--quiet", f"{rev}:{path}").strip() or None


def first_main_merge(commit):
    """First first-parent commit of NEW that contains `commit`."""
    chain = git("rev-list", "--first-parent", "--ancestry-path",
                f"{commit}..{NEW}").split()
    if not chain:
        return commit, git("log", "-1", "--format=%s", commit).strip()
    top = chain[-1]
    return top, git("log", "-1", "--format=%s", top).strip()


def main():
    errors = [line.rstrip("\n") for line in open(sys.argv[1]) if line.strip()]
    main_left = {line.rstrip("\n") for line in open(sys.argv[2]) if line.strip()}
    paths = {}
    for line in errors:
        path, msg = line.split(": ", 1)
        paths.setdefault(path, []).append(msg)
    report = []
    for path, msgs in sorted(paths.items()):
        old_b, new_b = blob(OLD, path), blob(NEW, path)
        row = {"path": path, "errors_at_prior": len(msgs),
               "errors_still_on_main": sum(1 for m in msgs if f"{path}: {m}" in main_left),
               "bytes_changed_prior_to_main": old_b != new_b,
               "blob_prior": old_b, "blob_main": new_b, "registry_routes_added": []}
        for reg in REGISTRIES:
            old_text = git("show", f"{OLD}:{reg}")
            new_text = git("show", f"{NEW}:{reg}")
            if path in new_text and path not in old_text:
                commits = git("log", "--format=%H", f"-S{path}", f"{OLD}..{NEW}", "--", reg).split()
                adds = []
                for c in commits:
                    merge, subject = first_main_merge(c)
                    adds.append({"commit": c[:10], "main_merge": merge[:10],
                                 "main_merge_subject": subject})
                row["registry_routes_added"].append({"registry": reg, "by": adds})
            elif path in new_text:
                row.setdefault("registry_already_named_at_prior", []).append(reg)
        if not row["registry_routes_added"] and not row["bytes_changed_prior_to_main"]:
            # Look for any later record naming the path or its id.
            row["note"] = "no registry route and no byte change: resolved elsewhere (see manual check)"
        report.append(row)
    json.dump(report, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()

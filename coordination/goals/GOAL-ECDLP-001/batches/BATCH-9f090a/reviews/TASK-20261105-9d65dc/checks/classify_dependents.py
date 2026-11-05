#!/usr/bin/env python3
"""Classify every committed citation of KN-FIND-002 / KN-FIND-b7e091 by which
affected sentence it leans on.  Reads the HEAD tree via `git grep` (the local
checkout is sparse), writes dependents_classified.tsv and prints a summary.

Topic tags are keyword heuristics over a +-4 line window; they are a triage aid
for the J4 dependent list, not a judgement.  Impact classes:
  JET    cites jet O(1)/closure                 -> sentence withdrawn
  ENDO   cites endomorphism closure / End=Z      -> conclusion survives, premise/overhead erratum
  INC    cites incidence closure                 -> survives for CHECK over label FB only
  NET    cites net O(log N)                      -> survives for label-valued reading only
  CLOSE  cites generic 'closed at 1/2' / binding  -> survives only per-oracle as above
  META   process / provenance mention only       -> no change needed
"""
import collections
import re
import subprocess
import sys

IDS = ("KN-FIND-002", "KN-FIND-b7e091")
SELF = "BATCH-9f090a/reviews/TASK-20261105-9d65dc"
TOPICS = collections.OrderedDict([
    ("JET", re.compile(r"\bjet|dual-number|first-jet|eps", re.I)),
    ("ENDO", re.compile(r"endomorph|End_\{?F_p|End\(E\)|eigenvalue|\[m\]Q|phi", re.I)),
    ("INC", re.compile(r"incidence|factor-base subset|O\(m\)|CHECK|SEARCH|B\^m|B to the m", re.I)),
    ("NET", re.compile(r"elliptic.net|Somos|net oracle|O\(log N\)", re.I)),
    ("CLOSE", re.compile(r"closed|closure|exponent 1/2|binding|Shoup|simulab", re.I)),
])
META = re.compile(r"schema|type: finding|internal_finding|INDEX|conflict marker|"
                  r"renumber|identifier|front matter|archive|receipt|retier|routed|"
                  r"unopened|not acted on|stand", re.I)


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def main(out):
    hits = git("grep", "-n", "-e", IDS[0], "-e", IDS[1], "HEAD").splitlines()
    files = collections.defaultdict(list)
    for h in hits:
        _, path, ln, _txt = h.split(":", 3)
        if SELF in path:
            continue
        files[path].append(int(ln))
    rows = []
    for path, lns in sorted(files.items()):
        text = git("show", f"HEAD:{path}").splitlines()
        for ln in lns:
            win = " ".join(text[max(0, ln - 5): ln + 4])
            line = text[ln - 1]
            ids = ",".join(i for i in IDS if i in line)
            tags = [t for t, rx in TOPICS.items() if rx.search(win)]
            if not tags or (META.search(line) and "CLOSE" not in tags and len(tags) <= 1):
                tags = tags or ["META"]
            area = "/".join(path.split("/")[:2])
            rows.append((path, ln, area, ids, "+".join(tags), line.strip()[:160]))
    with open(out, "w") as f:
        f.write("path\tline\tarea\tcites\ttopics\ttext\n")
        for r in rows:
            f.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
    by_area = collections.Counter(r[2] for r in rows)
    by_tag = collections.Counter(t for r in rows for t in r[4].split("+"))
    print(f"citing lines: {len(rows)} in {len(files)} files (HEAD {git('rev-parse','HEAD').strip()})")
    print("by area:", dict(by_area.most_common()))
    print("by topic tag:", dict(by_tag.most_common()))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dependents_classified.tsv")

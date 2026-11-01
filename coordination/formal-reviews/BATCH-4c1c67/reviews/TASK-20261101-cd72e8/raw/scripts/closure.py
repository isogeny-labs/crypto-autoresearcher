import re, sys, pathlib
ws = pathlib.Path("/dev/shm/j3/ws")
roots = {"Mathlib": ws/".lake/packages/mathlib", "Batteries": ws/".lake/packages/batteries",
         "Aesop": ws/".lake/packages/aesop", "Qq": ws/".lake/packages/Qq",
         "Plausible": ws/".lake/packages/plausible", "ProofWidgets": ws/".lake/packages/proofwidgets",
         "LeanSearchClient": ws/".lake/packages/LeanSearchClient", "ImportGraph": ws/".lake/packages/importGraph",
         "CryptoResearch": ws}
pat = re.compile(r'^\s*(?:public\s+|private\s+)?(?:meta\s+)?import\s+(?:all\s+)?(.*)$')
def src(mod):
    top = mod.split(".")[0]
    r = roots.get(top)
    if r is None: return None
    p = r / (mod.replace(".", "/") + ".lean")
    return p if p.exists() else None
seen, stack, unresolved = set(), list(sys.argv[1:]), set()
while stack:
    m = stack.pop()
    if m in seen: continue
    seen.add(m)
    p = src(m)
    if p is None:
        unresolved.add(m.split(".")[0]); continue
    txt = re.sub(r'/-.*?-/', '', p.read_text(), flags=re.S)
    for line in txt.splitlines():
        mm = pat.match(line)
        if mm:
            for tok in mm.group(1).split("--")[0].split():
                stack.append(tok)
mathlib = sorted(x for x in seen if x.startswith("Mathlib"))
print("\n".join(mathlib))
print(f"# total {len(seen)}, mathlib {len(mathlib)}, unresolved tops {sorted(unresolved)}", file=sys.stderr)

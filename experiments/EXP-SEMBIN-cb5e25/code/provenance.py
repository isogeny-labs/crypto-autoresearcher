"""Code/engine provenance: sha256 of every code file that can run (IR-5), the
git commit and dirty state, and the CODE_SHA256.json generator.

    python3 provenance.py            # (re)writes code/CODE_SHA256.json
    python3 provenance.py --check    # exit 1 if the file is stale
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys

import _paths

REF_FILES = [
    "src/crypto_autoresearcher/gf2/__init__.py", "src/crypto_autoresearcher/gf2/closure.py",
    "src/crypto_autoresearcher/gf2/kernels.py", "src/crypto_autoresearcher/gf2/_native.py",
    "src/crypto_autoresearcher/gf2/_kernels.c", "src/crypto_autoresearcher/gf2/rankprofile.py",
    "src/crypto_autoresearcher/gf2/rank_only.py", "src/crypto_autoresearcher/gf2/reference.py",
    "tools/artifact_store.py", "tools/lemma4_inside_form.py",
    "experiments/EXP-ECTD-9e4248/driver/reused/macaulay.py", "src/semaev_tree.py",
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def code_files():
    out = []
    for root, dirs, files in os.walk(_paths.CODE_DIR):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
        for fn in files:
            if fn.endswith((".py", ".md", ".json")) and fn != "CODE_SHA256.json":
                out.append(os.path.relpath(os.path.join(root, fn), _paths.REPO))
    return sorted(out)


def compute():
    files = {}
    for rel in code_files() + REF_FILES:
        p = os.path.join(_paths.REPO, rel)
        if os.path.exists(p):
            files[rel] = sha256_file(p)
    return {"schema": "sembin-code-sha256-v1", "files": files,
            "note": "code/ files plus the imported or oracle files named in the specification"}


def git_state():
    def run(*a):
        return subprocess.run(["git", "-C", _paths.REPO, *a], capture_output=True, text=True).stdout.strip()
    status = run("status", "--porcelain")
    return {"commit": run("rev-parse", "HEAD"), "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(status), "dirty_files": status.splitlines()[:200]}


def loaded_code_hashes():
    """sha256 of every module file currently loaded from code/ or the gf2 package."""
    out = {}
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        f = os.path.abspath(f)
        if f.startswith(_paths.CODE_DIR) or f.startswith(_paths.GF2_DIR) or f.startswith(_paths.TOOLS):
            out[os.path.relpath(f, _paths.REPO)] = sha256_file(f)
    return dict(sorted(out.items()))


def environment():
    import numpy
    env = {"python": sys.version, "platform": platform.platform(), "numpy": numpy.__version__,
           "cpu_count": os.cpu_count(), "load_avg_1min": os.getloadavg()[0]}
    try:
        with open("/proc/meminfo") as f:
            env["mem_total_kb"] = int(f.readline().split()[1])
    except OSError:
        pass
    from crypto_autoresearcher.gf2 import _native, kernels
    kernels.backend()
    env["gf2_backend"] = kernels.backend()
    env["gf2_build_info"] = dict(_native.build_info)
    return env


if __name__ == "__main__":
    path = os.path.join(_paths.CODE_DIR, "CODE_SHA256.json")
    cur = compute()
    if "--check" in sys.argv:
        old = json.load(open(path)) if os.path.exists(path) else {}
        sys.exit(0 if old.get("files") == cur["files"] else 1)
    with open(path, "w") as f:
        json.dump(cur, f, indent=1, sort_keys=True)
    print("wrote", path, len(cur["files"]), "files")

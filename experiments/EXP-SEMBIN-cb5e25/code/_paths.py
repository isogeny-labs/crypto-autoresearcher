"""Repository paths and sys.path set-up shared by every module under code/.

Nothing here is scientific: it locates the repo root, puts src/ (the gf2
engine), tools/ and code/ itself on sys.path.
"""
from __future__ import annotations

import os
import sys

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(CODE_DIR)
REPO = os.path.dirname(os.path.dirname(EXP_DIR))
SRC = os.path.join(REPO, "src")
TOOLS = os.path.join(REPO, "tools")
GF2_DIR = os.path.join(SRC, "crypto_autoresearcher", "gf2")
for _p in (CODE_DIR, SRC, TOOLS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

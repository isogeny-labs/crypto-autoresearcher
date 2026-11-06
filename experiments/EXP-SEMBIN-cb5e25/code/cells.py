"""The frozen parameter grid (specification parameter_grid.cells) and the
arms-per-tier table. Values are copied verbatim from the specification and
re-derived by check_cell() (N = m*k+(m-2)*n, M = (m-1)*n, C4, D_max)."""
from __future__ import annotations

from math import comb

_RAW = [
    ("m3n03", 3, 3, 1, 6, 6, 57, 6, "T1"),
    ("m3n04", 3, 4, 1, 7, 8, 99, 6, "T1"),
    ("m3n05", 3, 5, 1, 8, 10, 163, 6, "T1"),
    ("m3n06", 3, 6, 2, 12, 12, 794, 6, "T1"),
    ("m3n07", 3, 7, 2, 13, 14, 1093, 6, "T1"),
    ("m3n08", 3, 8, 2, 14, 16, 1471, 6, "T1"),
    ("m3n09", 3, 9, 3, 18, 18, 4048, 6, "T1"),
    ("m3n10", 3, 10, 3, 19, 20, 5036, 6, "T1"),
    ("m3n11", 3, 11, 3, 20, 22, 6196, 5, "T1"),
    ("m3n12", 3, 12, 4, 24, 24, 12951, 4, "T1"),
    ("m3n13", 3, 13, 4, 25, 26, 15276, 4, "T1"),
    ("m3n14", 3, 14, 4, 26, 28, 17902, 4, "T1"),
    ("m4n08", 4, 8, 2, 24, 24, 12951, 4, "T1"),
    ("m4n09", 4, 9, 2, 26, 27, 17902, 4, "T1"),
    ("m4n10", 4, 10, 2, 28, 30, 24158, 4, "T1"),
    ("m3n15", 3, 15, 5, 30, 30, 31931, 4, "T2"),
    ("m3n16", 3, 16, 5, 31, 32, 36457, 4, "T2"),
    ("m3n17", 3, 17, 5, 32, 34, 41449, 4, "T2"),
    ("m3n19k7", 3, 19, 7, 40, 38, 102091, 4, "T3"),
]
CELLS = {r[0]: dict(id=r[0], m=r[1], n=r[2], k=r[3], N=r[4], M=r[5], C4=r[6], D_max=r[7], tier=r[8])
         for r in _RAW}
EXECUTION_ORDER = (
    sorted([c for c in CELLS if CELLS[c]["tier"] == "T1"], key=lambda c: CELLS[c]["N"])
    + [c for c in CELLS if CELLS[c]["tier"] == "T3"]
    + sorted([c for c in CELLS if CELLS[c]["tier"] == "T2"], key=lambda c: CELLS[c]["N"])
)

ARMS_PER_TIER = {
    "T1": {"EQS4": 5, "EQS4-U": 5, "EQS2": 5, "NULL-PROF": 5, "NULL-SHUF": 5, "PC-TRI": 5,
           "EQS4-AA": 2, "EQS4-FULLFE": 2, "EQS4-NOFE": 2},
    "T2": {"EQS4": 5, "EQS4-U": 5, "EQS2": 5, "NULL-PROF": 3, "PC-TRI": 2, "EQS4-AA": 1},
    "T3": {"EQS4": 5, "PC-TRI": 1, "NULL-PROF": 1, "EQS4-AA": 1},
}
ARMS = ["EQS4", "EQS2", "NULL-PROF", "NULL-SHUF", "PC-TRI", "EQS4-AA", "EQS4-U",
        "EQS4-FULLFE", "EQS4-NOFE"]
TARGET_ARMS = ("EQS4", "EQS4-U", "EQS2")
NULL_ARMS = ("NULL-PROF", "NULL-SHUF")


def C_le(N, D):
    return sum(comb(N, d) for d in range(D + 1))


def d_max(N):
    best = 4
    for D in (4, 5, 6):
        if C_le(N, D) <= 45000:
            best = D
    return best


def dims_of(m, n, k):
    return m * k + (m - 2) * n, (m - 1) * n


def check_cell(c):
    N, M = dims_of(c["m"], c["n"], c["k"])
    assert (N, M) == (c["N"], c["M"]), c["id"]
    assert C_le(N, 4) == c["C4"], c["id"]
    assert d_max(N) == c["D_max"], c["id"]
    assert (1 << (c["n"] - c["k"])) - 1 >= c["m"], c["id"]
    return True

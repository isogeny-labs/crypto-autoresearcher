"""Enumerate abstract branch placements and cross-check their F2[x] ranks.

This is a design component for the unapproved orbits stage. It takes no
curve-census data and does not establish realizability of a placement.
"""

import hashlib
import itertools
import json
import math
import os
from pathlib import Path


TYPES = {"split": (1, 1, 1, 1), "Z2": (1, 1, 2), "odd": (1, 3)}


def remainder(a, b):
    if b == 0:
        raise ZeroDivisionError
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def gcd(a, b):
    while b:
        a, b = b, remainder(a, b)
    return a


def polynomial_rank(n, vectors):
    """Ideal dimension in F2[x]/(x^n-1)."""
    common = (1 << n) | 1
    for vector in vectors:
        common = gcd(common, vector)
    return n - (common.bit_length() - 1)


def shift_rank(n, vectors):
    """Independent binary elimination on all cyclic shifts."""
    mask = (1 << n) - 1
    pivots = {}
    for vector in vectors:
        for offset in range(n):
            row = ((vector << offset) | (vector >> (n - offset))) & mask
            while row:
                bit = row.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = row
                    break
                row ^= pivots[bit]
    return len(pivots)


def placements(n, degrees):
    """Canonical labeled set partitions; each free orbit has distinct slots."""
    count = len(degrees)
    for labels in itertools.product(range(-1, count), repeat=count):
        seen = []
        valid = True
        for index, label in enumerate(labels):
            if label < 0:
                if math.gcd(degrees[index], n) != 1:
                    valid = False
                    break
            elif label not in seen:
                if label != len(seen):
                    valid = False
                    break
                seen.append(label)
        if not valid:
            continue
        members = {label: [i for i, value in enumerate(labels) if value == label]
                   for label in seen}
        if any(len({degrees[i] for i in indices}) != 1
               for indices in members.values()):
            continue
        for slots in itertools.product(range(n), repeat=sum(map(len, members.values()))):
            offset = 0
            positions = {}
            for label, indices in members.items():
                positions[label] = slots[offset:offset + len(indices)]
                offset += len(indices)
            if any(len(set(values)) != len(values)
                   for values in positions.values()):
                continue
            vectors = [((1 << n) - 1) for label in labels if label < 0]
            branch_count = sum(degrees[i] for i, label in enumerate(labels)
                               if label < 0)
            for label, values in positions.items():
                vectors.append(sum(1 << value for value in values))
                branch_count += n * degrees[members[label][0]]
            yield labels, positions, vectors, branch_count


def enumerate_spectrum(degrees=(3, 5, 7)):
    """Check every placement, retain exact counts and one canonical witness."""
    result = {"schema": "pext.orbit-spectrum/v1",
              "status": "abstract_placements_checked; realization_unasserted",
              "degrees": list(degrees), "cases": []}
    for n in degrees:
        if n not in (3, 5, 7):
            raise ValueError("only frozen n=3,5,7 allowed")
        for name, branch_degrees in TYPES.items():
            rows = {}
            total = 0
            digest = hashlib.sha256()
            for labels, positions, vectors, r in placements(n, branch_degrees):
                m = polynomial_rank(n, vectors)
                if shift_rank(n, vectors) != m:
                    raise ValueError("polynomial and binary rank disagree")
                witness = {"labels": labels, "positions": positions,
                           "vectors": vectors, "m": m, "r": r}
                encoded = json.dumps(witness, sort_keys=True,
                                     separators=(",", ":")).encode() + b"\n"
                digest.update(encoded)
                key = (m, r)
                if key not in rows:
                    rows[key] = {"m": m, "r": r, "count": 0,
                                 "first_witness": witness}
                rows[key]["count"] += 1
                total += 1
            result["cases"].append({"n": n, "type": name,
                                    "placement_count": total,
                                    "placement_stream_sha256": digest.hexdigest(),
                                    "m_r": [rows[key] for key in sorted(rows)]})
    return result


def write_once(path, value):
    path = Path(path)
    if path.exists() or path.is_symlink() or path.with_suffix(path.suffix + ".partial").exists():
        raise FileExistsError("orbit spectrum attempt already exists")
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    partial = path.with_suffix(path.suffix + ".partial")
    with partial.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(partial, path)
    return hashlib.sha256(data).hexdigest()


def compare_exact(path, degrees=(3, 5, 7)):
    """Recompute all placements and compare canonical bytes with saved output."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("orbit output missing or symlinked")
    expected = (json.dumps(enumerate_spectrum(degrees), sort_keys=True,
                           separators=(",", ":")).encode() + b"\n")
    if path.read_bytes() != expected:
        raise ValueError("orbit output differs from exact recomputation")
    return hashlib.sha256(expected).hexdigest()

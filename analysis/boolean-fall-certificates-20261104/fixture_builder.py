"""Small deterministic certificate producer. Not an experiment launcher.

Separate from certificate.py's RREF/closure verification. Every eliminated
row retains a finite primitive derivation; no seed-kernel oracle is used.
"""
from certificate import combine, degree, digest, multiply, read_system


def build(system, cap):
    p, n, generators = read_system(system)
    order = sorted(range(1 << n), key=lambda m: (-m.bit_count(), -m))
    pivots, rows, steps = {}, [], []

    def emit(step, row):
        steps.append(step)
        rows.append(row)
        return len(rows) - 1

    def insert(index):
        for col in order:
            value = rows[index].get(col, 0)
            if not value:
                continue
            if col in pivots:
                old = pivots[col]
                c = (-value) % p
                index = emit({"op": "add", "left": index, "right": old, "coefficient": c},
                             combine(rows[index], rows[old], c, p))
            else:
                inv = pow(value, -1, p)
                if inv != 1:
                    index = emit({"op": "add", "left": index, "right": index,
                                  "coefficient": (inv - 1) % p},
                                 combine(rows[index], rows[index], inv - 1, p))
                pivots[col] = index
                return True
        return False

    for j, row in enumerate(generators):
        if degree(row) <= cap:
            insert(emit({"op": "input", "index": j}, row))
    seen = set()
    while True:
        changed = False
        for col, index in list(pivots.items()):
            if col.bit_count() >= cap:
                continue
            for v in range(n):
                if (index, v) in seen:
                    continue
                seen.add((index, v))
                new = emit({"op": "mul", "ref": index, "variable": v},
                           multiply(rows[index], 1 << v, p))
                changed |= insert(new)
        if not changed:
            break
    return {"schema": "boolean.closed-space-certificate/v1", "system": system,
            "degree": cap, "steps": steps, "basis": list(pivots.values())}

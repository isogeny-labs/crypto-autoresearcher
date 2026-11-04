"""Exact finite closure certificates over F_p[b]/(b_i^2-b_i).

This checker never accepts an unproved seed-kernel row. Primal derivations
prove U <= W_D; containment of eligible inputs and multiplication closure
prove W_D <= U. It returns equality only when both directions were checked.
This is a bounded software instrument, not a generic descent theorem.
"""
import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(system):
    return hashlib.sha256(json.dumps(system, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def degree(row):
    return max((mask.bit_count() for mask in row), default=0)


def combine(a, b, c, p):
    out = dict(a)
    for m, v in b.items():
        out[m] = (out.get(m, 0) + c * v) % p
        if not out[m]:
            del out[m]
    return out


def multiply(row, bit, p):
    out = {}
    for m, c in row.items():
        key = m | bit
        out[key] = (out.get(key, 0) + c) % p
        if not out[key]:
            del out[key]
    return out


def echelon(rows, p, order):
    """Return full reduced basis, independent of producer's insertion order."""
    work = [dict(r) for r in rows if r]
    rank = 0
    for col in order:
        pivot = next((j for j in range(rank, len(work)) if work[j].get(col, 0)), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inv = pow(work[rank][col], -1, p)
        work[rank] = {m: (v * inv) % p for m, v in work[rank].items()}
        for j in range(len(work)):
            if j != rank and work[j].get(col, 0):
                work[j] = combine(work[j], work[rank], -work[j][col], p)
        rank += 1
    require(all(not r for r in work[rank:]), "incomplete monomial universe")
    return work[:rank]


def contained(row, basis, p, order):
    out = dict(row)
    for r in basis:
        pivot = next(m for m in order if m in r)
        if out.get(pivot, 0):
            out = combine(out, r, -out[pivot], p)
    return not out


def read_system(system):
    require(set(system) == {"prime", "variables", "generators"}, "wrong system keys")
    p, n = system["prime"], system["variables"]
    require(type(p) is int and 2 <= p <= 65537 and
            all(p % d for d in range(2, isqrt(p) + 1)), "prime not in admitted range")
    require(type(n) is int and 1 <= n <= 12, "variable count outside finite-checker limit")
    def row(terms):
        require(isinstance(terms, list), "terms must be a list")
        result = {}
        for term in terms:
            require(isinstance(term, list) and len(term) == 2, "bad term")
            m, c = term
            require(type(m) is int and 0 <= m < 1 << n and type(c) is int and 0 < c < p,
                    "noncanonical coefficient or monomial")
            require(m not in result, "duplicate monomial")
            result[m] = c
        require(list(result) == sorted(result), "unsorted monomials")
        return result
    require(isinstance(system["generators"], list) and system["generators"], "no generators")
    return p, n, [row(g) for g in system["generators"]]


def check(document, expected_system_sha256):
    require(set(document) == {"schema", "system", "degree", "steps", "basis"}, "wrong document keys")
    require(document["schema"] == "boolean.closed-space-certificate/v1", "wrong schema")
    system = document["system"]
    require(digest(system) == expected_system_sha256, "system hash mismatch")
    p, n, generators = read_system(system)
    d = document["degree"]
    require(type(d) is int and 0 <= d <= n + 1, "invalid degree")
    steps = document["steps"]
    require(isinstance(steps, list) and len(steps) <= 200000, "step limit")
    rows = []
    for step in steps:
        require(isinstance(step, dict), "step must be an object")
        def ref(index):
            require(type(index) is int and 0 <= index < len(rows), "invalid or forward reference")
            return rows[index]
        if set(step) == {"op", "index"} and step["op"] == "input":
            j = step["index"]
            require(type(j) is int and 0 <= j < len(generators), "invalid input")
            r = generators[j]
        elif set(step) == {"op", "left", "right", "coefficient"} and step["op"] == "add":
            c = step["coefficient"]
            require(type(c) is int and 0 <= c < p, "noncanonical scalar")
            r = combine(ref(step["left"]), ref(step["right"]), c, p)
        elif set(step) == {"op", "ref", "variable"} and step["op"] == "mul":
            v = step["variable"]
            require(type(v) is int and 0 <= v < n, "invalid variable")
            source = ref(step["ref"])
            require(not source or degree(source) + 1 <= d, "illegal multiplication budget")
            r = multiply(source, 1 << v, p)
        else:
            raise ValueError("unknown rule; kernel premises are forbidden")
        require(degree(r) <= d, "row exceeds degree cap")
        rows.append(r)
    indices = document["basis"]
    require(isinstance(indices, list) and len(indices) == len(set(indices)) and
            all(type(j) is int and 0 <= j < len(rows) for j in indices), "invalid basis references")
    order = sorted((m for m in range(1 << n) if m.bit_count() <= d),
                   key=lambda m: (-m.bit_count(), -m))
    basis = echelon([rows[j] for j in indices], p, order)
    # Descending-degree RREF isolates the entire low-degree intersection,
    # including combinations that cancel every degree-d coefficient.
    low = [r for r in basis if degree(r) < d]
    for g in generators:
        if degree(g) <= d:
            require(contained(g, basis, p, order), "eligible input absent")
    for r in low:
        for v in range(n):
            require(contained(multiply(r, 1 << v, p), basis, p, order), "space is not closed")
    solutions = 0
    evaluations = []
    for assignment in range(1 << n):
        if all(sum(c for m, c in g.items() if m & assignment == m) % p == 0 for g in generators):
            solutions += 1
            evaluations.append({m: 1 for m in order if m & assignment == m})
    evaluation_basis = echelon(evaluations, p, order)
    evaluation_rank = len(evaluation_basis)
    codimension = len(order) - len(basis)
    one = contained({0: 1}, basis, p, order)
    result = {"status": "exact_closed_space", "system_sha256": expected_system_sha256,
              "prime": p, "variables": n, "degree": d, "rank": len(basis),
              "codimension": codimension, "solutions": solutions, "contains_one": one,
              "primal_steps": len(rows), "kernel_premises": 0}
    # With explicit Boolean equations the ideal is the vanishing ideal of
    # the Boolean zero set. This is the finite witness criterion, not a fit.
    result["evaluation_rank"] = evaluation_rank
    result["lfd_lower_bound"] = d + 1 if codimension > evaluation_rank else None
    result["missing_consequence"] = None
    if codimension > evaluation_rank:
        pivot_columns = [next(m for m in order if m in r) for r in evaluation_basis]
        for free in order:
            if free in pivot_columns:
                continue
            witness = {free: 1}
            for pivot, row in zip(pivot_columns, evaluation_basis):
                if row.get(free, 0):
                    witness[pivot] = (-row[free]) % p
            if not contained(witness, basis, p, order):
                result["missing_consequence"] = [[m, c] for m, c in sorted(witness.items())]
                break
        require(result["missing_consequence"] is not None, "rank criterion lacks witness")
    result["lfd_upper_bound"] = d if one else None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--system-sha256", required=True)
    args = parser.parse_args()
    print(json.dumps(check(json.loads(args.certificate.read_text()), args.system_sha256), sort_keys=True))


if __name__ == "__main__":
    main()

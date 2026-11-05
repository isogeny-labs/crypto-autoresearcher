#!/usr/bin/env python3
"""Exact finite controls for J2, independent of all producer implementation.

This is a bounded mathematical check, not Lean replay, a scientific trial,
or a benchmark. All coefficients are Python integers. Permutations are
tuples of their images; group multiplication is function composition.
"""
import json
from collections import defaultdict


def compose(f, g):
    return tuple(f[g[x]] for x in range(len(g)))


def add(p, q, scale=1):
    out = defaultdict(int, p)
    for word, coefficient in q.items():
        out[word] += scale * coefficient
    return {word: coefficient for word, coefficient in out.items() if coefficient}


def multiply(p, q, op):
    out = defaultdict(int)
    for a, ca in p.items():
        for b, cb in q.items():
            out[op(a, b)] += ca * cb
    return {a: c for a, c in out.items() if c}


def scalar_eval(poly, images):
    value = 0
    for word, coefficient in poly.items():
        term = coefficient
        for letter in word:
            term *= images[letter]
        value += term
    return value


def algebra_eval(poly, images, n):
    out = {}
    identity = tuple(range(n))
    for word, coefficient in poly.items():
        perm = identity
        for letter in word:
            perm = compose(perm, images[letter])
        out = add(out, {perm: coefficient})
    return out


def rows(poly):
    return [{"basis_permutation": list(g), "coefficient": c}
            for g, c in sorted(poly.items())]


def main():
    one, nu, trans = {(): 1}, {("nu",): 1}, {("t",): 1}
    nt = multiply(nu, trans, lambda a, b: a + b)
    witness = add(multiply(nt, nt, lambda a, b: a + b), one, -1)
    aug = scalar_eval(witness, {"nu": 0, "t": 0})
    assert aug == -1
    assert scalar_eval(witness, {"nu": 1, "t": 1}) == 0

    positive = []
    for n in range(1, 6):
        for s in range(n):
            identity = tuple(range(n))
            neg = tuple((-x) % n for x in range(n))
            tr = tuple((x + s) % n for x in range(n))
            reflection = compose(neg, tr)
            square = compose(reflection, reflection)
            image = algebra_eval(witness, {"nu": neg, "t": tr}, n)
            assert square == identity and image == {}
            positive.append({"B": 1, "n": n, "s": s,
                             "nu": list(neg), "t": list(tr),
                             "nu_t": list(reflection), "nu_t_squared": list(square),
                             "augmentation": aug, "group_algebra_image": rows(image)})

    # Known-false mutation: omit the square, on Z/2 with s=1.
    bad = add(nt, one, -1)
    bad_image = algebra_eval(bad, {"nu": (0, 1), "t": (1, 0)}, 2)
    assert bad_image != {}

    # Historical J at n=2: t=1, nu=-1 is a scalar character killing J.
    character = {"nu": -1, "t": 1}
    nu_square = add(multiply(nu, nu, lambda a, b: a + b), one, -1)
    lattice_rows = []
    for u in range(7):
        for v in range(7):
            if (u - v) % 2 == 0:
                binomial = add({("t",) * u: 1}, {("t",) * v: 1}, -1)
                chi = scalar_eval(binomial, character)
                assert chi == 0
                lattice_rows.append({"u": u, "v": v, "character": chi})
    nu_minus_one = add(nu, one, -1)
    assert scalar_eval(nu_square, character) == 0
    assert scalar_eval(witness, character) == 0
    assert scalar_eval(nu_minus_one, character) == -2
    assert algebra_eval(nu_minus_one, {"nu": (0, 1), "t": (1, 0)}, 2) == {}

    # C is not generally a subset of ker rho: [nu,t] survives at n=3,s=1.
    commutator = add(nt, multiply(trans, nu, lambda a, b: a + b), -1)
    maps3 = {"nu": (0, 2, 1), "t": (1, 2, 0)}
    comm_image = algebra_eval(commutator, maps3, 3)
    assert comm_image != {}
    assert scalar_eval(commutator, {"nu": 0, "t": 0}) == 0

    # Group algebra != image algebra of the permutation representation.
    relation = {}
    for k in range(3):
        relation = add(relation, {("t",) * k: 1})
        relation = add(relation, {("t",) * k + ("nu",): 1}, -1)
    rho = algebra_eval(relation, maps3, 3)
    assert len(rho) == 6
    matrix = [[0] * 3 for _ in range(3)]
    for perm, coefficient in rho.items():
        for x, y in enumerate(perm):
            matrix[y][x] += coefficient
    assert matrix == [[0] * 3 for _ in range(3)]

    # n=0 means ZMod 0 = Z: exact integer spot controls, not exhaustive.
    integers = []
    for s, x in [(-3, -7), (0, 0), (2, 9)]:
        first = -(x + s)
        second = -(first + s)
        assert second == x
        integers.append({"s": s, "x": x, "nu_t_x": first, "square_x": second})

    print(json.dumps({
        "task_id": "TASK-20261031-8a54e2", "joint": "J2_commutator_witness",
        "status": "passed", "arithmetic": "exact integers and finite permutations",
        "lean_checked": False, "scientific_runs": 0,
        "zero_generator_augmentation": aug,
        "one_generator_specialization": 0,
        "positive_cases": positive,
        "positive_case_count": len(positive),
        "positive_point_count": sum(row["n"] for row in positive),
        "unsquared_mutation": {"B": 1, "n": 2, "s": 1,
                               "group_algebra_image": rows(bad_image), "is_zero": False},
        "historical_J_n2": {"character": character,
                            "nu_square_minus_one": 0, "nu_t_square_minus_one": 0,
                            "all_lattice_binomials_argument": "1**u - 1**v = 0 for every u,v >= 0",
                            "sample_lattice_binomials": lattice_rows,
                            "nu_minus_one_character": -2, "nu_minus_one_action_image": []},
        "all_commutators_in_kernel_mutation": {"n": 3, "s": 1,
                                               "commutator_image": rows(comm_image), "is_zero": False},
        "operator_target_control": {"n": 3, "polynomial": "sum(t**k,k=0..2)-sum(t**k*nu,k=0..2)",
                                    "group_algebra_image": rows(rho), "operator_matrix": matrix,
                                    "group_algebra_image_is_zero": False, "operator_is_zero": True},
        "integer_modulus_zero_spots": integers,
        "B_zero_boundary": "No i:Fin 0 exists; companion witness needs B>0. The nu**2-1 witness has no i."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

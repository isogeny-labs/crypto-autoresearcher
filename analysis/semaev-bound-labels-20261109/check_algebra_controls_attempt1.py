#!/usr/bin/env python3
"""Fixed exact algebra controls; no random draws, closure engine, or CLI solver.

The F16 engine uses F2[t]/(t^4+t+1), independently of the note's tower
presentation. Sparse ordinary characteristic-two polynomials test the
factorization as a formal identity. Squarefree F16-coefficient polynomials
then compute the coordinate descent. Passing does not verify a general LFD
or unboundedness theorem.
"""
import hashlib
import json
from pathlib import Path
import sys

CHECKS = []

def require(condition, label):
    if not condition:
        raise ValueError(label)
    CHECKS.append(label)

# Ordinary F2 polynomials in X,s,z: sets of exponent triples, no idempotence.
def add(*polys):
    out = set()
    for poly in polys:
        out.symmetric_difference_update(poly)
    return out

def mul(poly, other):
    out = set()
    for a in poly:
        for b in other:
            m = tuple(a[i] + b[i] for i in range(3))
            if m in out:
                out.remove(m)
            else:
                out.add(m)
    return out

def square(poly):
    return mul(poly, poly)

# F16 in polynomial basis 1,t,t^2,t^3, modulus t^4+t+1.
def fm(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 16:
            a ^= 0b10011
    return out

def fp(a, n):
    out = 1
    while n:
        if n & 1:
            out = fm(out, a)
        a = fm(a, a)
        n >>= 1
    return out

def tr(a):
    return a ^ fp(a, 2) ^ fp(a, 4) ^ fp(a, 8)

# Squarefree F16 coefficient polynomials in x0,x1,y0,y1.
def ba(*polys):
    out = {}
    for poly in polys:
        for mask, value in poly.items():
            out[mask] = out.get(mask, 0) ^ value
    return {m: c for m, c in out.items() if c}

def bm(poly, other):
    out = {}
    for m, c in poly.items():
        for n, d in other.items():
            mask = m | n
            out[mask] = out.get(mask, 0) ^ fm(c, d)
    return {m: c for m, c in out.items() if c}

def bv(poly, point):
    out = 0
    for mask, coefficient in poly.items():
        if point & mask == mask:
            out ^= coefficient
    return out

def row(*monomials):
    out = 0
    for mask in monomials:
        out ^= 1 << mask
    return out

def degree(p):
    return max((m.bit_count() for m in range(16) if (p >> m) & 1), default=-1)

def row_rank(rows):
    pivots = {}
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in pivots:
                v ^= pivots[h]
            else:
                pivots[h] = v
                break
    return len(pivots)

def main():
    X, S, Z = {(1, 0, 0)}, {(0, 1, 0)}, {(0, 0, 1)}
    factor = mul(mul(X, add(X, S)), add(square(X), mul(S, X), Z))
    expected = {(4, 0, 0), (2, 2, 0), (2, 0, 1), (1, 1, 1)}
    require(factor == expected, 'formal_characteristic_two_fibre_factorization')
    Y = add(X, S)
    semaev_without_a6 = add(square(add(mul(X, Y), mul(Z, X), mul(Z, Y))), mul(mul(Z, X), Y))
    require(semaev_without_a6 == add(expected, {(0, 2, 2)}), 'formal_S3_substitution_X_plus_s')

    require(all(fp(a, 15) == 1 and fm(a, fp(a, 14)) == 1 for a in range(1, 16)), 'F16_all_nonzero_elements_have_inverses')
    z = 2  # t
    w = fp(z, 2) ^ z
    require(w == 6 and fp(w, 2) == (w ^ 1), 'tower_w_squared_equals_w_plus_one')
    require(fp(z, 2) == (z ^ w), 'tower_z_squared_equals_z_plus_w')
    basis = [1, w, z, fm(w, z)]
    require(row_rank(basis) == 4, 'F16_coordinate_basis_invertible')
    coordinates = {}
    for mask in range(16):
        value = 0
        for i in range(4):
            if mask >> i & 1:
                value ^= basis[i]
        coordinates[value] = mask
    require(len(coordinates) == 16, 'F16_coordinate_lookup_bijective')
    H = [0, 1, w, 1 ^ w]
    require(all(tr(a) == 0 for a in H), 'subfield_has_zero_absolute_trace')
    require(tr(z) == 0 and tr(fp(fp(z, 2), 14)) == 1, 'target_and_inverse_square_traces')

    bx, by, bz = {1: 1, 2: w}, {4: 1, 8: w}, {0: z}
    p = bm(bx, by)
    inner = ba(p, bm(bz, bx), bm(bz, by))
    descended = ba(bm(inner, inner), bm(bz, p), {0: 1})
    rows = [0, 0, 0, 0]
    for monomial, value in descended.items():
        for i in range(4):
            if coordinates[value] >> i & 1:
                rows[i] ^= 1 << monomial
    # P0=x0*y0+x1*y1; P1=x0*y1+x1*y0+x1*y1.
    p0, p1, s0, s1 = row(5, 10), row(9, 6, 10), row(1, 4), row(2, 8)
    expected_rows = [p0 ^ p1 ^ s1 ^ row(0), p1 ^ s0, p0 ^ s0 ^ s1, p1 ^ s1]
    require(rows == expected_rows, 'four_claimed_descent_coordinate_polynomials')
    # Only the 16 fixed assignments of this hand-written finite fixture.
    for point in range(16):
        x, y = bv(bx, point), bv(by, point)
        t = fm(x, y) ^ fm(z, x) ^ fm(z, y)
        direct = fp(t, 2) ^ fm(fm(z, x), y) ^ 1
        require(bv(descended, point) == direct, 'fixture_evaluation_' + str(point))

    require([degree(p) for p in rows] == [2, 2, 2, 2], 'original_rows_all_genuinely_quadratic')
    require(rows[0] ^ rows[2] ^ rows[1] == row(0), 'original_degree_two_constant_fall_identity')
    # Row masks refer to original ordered rows (f00,f01,f10,f11).
    change = [0b0100, 0b1000, 0b1010, 0b1101]
    require(row_rank(change) == 4, 'four_by_four_row_change_invertible')
    changed = []
    for mask in change:
        value = 0
        for i, poly in enumerate(rows):
            if mask >> i & 1:
                value ^= poly
        changed.append(value)
    ell = s0 ^ s1
    require(changed == [rows[2], rows[3], ell, ell ^ row(0)], 'changed_rows_match_claimed_affine_pair')
    require([degree(p) for p in changed] == [2, 2, 1, 1], 'changed_rows_have_degrees_two_two_one_one')
    require(changed[2] ^ changed[3] == row(0), 'changed_degree_one_constant_fall_identity')
    require(all(degree(p) > 0 for p in changed), 'no_literal_constant_generator')
    # A concrete point on the ordinary curve: choose a2 with trace 1.
    a2 = next(a for a in range(16) if tr(a) == 1)
    curve_rhs = fp(z, 3) ^ fm(a2, fp(z, 2)) ^ 1
    ys = [y for y in range(16) if fp(y, 2) ^ fm(z, y) == curve_rhs]
    require(len(ys) == 2, 'target_lifts_to_two_curve_points_with_selected_a2')
    return {
        'schema': 'lfd.fixed-algebra-controls/v1',
        'passed': True,
        'checks': CHECKS,
        'fixture': {'n': 4, 'k': 2, 'modulus': '0x13', 'basis': basis, 'w': w, 'z': z, 'a6': 1, 'a2_for_rational_target': a2, 'target_y_values': ys, 'rows_as_monomial_bitsets': rows, 'row_change_masks': change, 'changed_rows_as_monomial_bitsets': changed},
        'scope': 'Formal sparse polynomial identities and one fixed F16 coordinate fixture; no closure engine and no general LFD or unboundedness verification.',
        'ffd_inference': 'Literal PQ convention: original FFD=2 because all rows have degree2 and a degree2 combination equals1; changed FFD=1 because two genuine affine rows sum to1 and no degree0 row exists. Common degree2 field equations do not affect those lower-cap arguments.',
        'random_draws': 0,
        'native_builds': 0,
        'closure_runs': 0,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command': 'python3 /home/ec2-user/lfd-unbounded-proof-20261109/check_algebra_controls.py',
    }

if __name__ == '__main__':
    try:
        result = main()
    except Exception as exc:
        print(json.dumps({'passed': False, 'error': type(exc).__name__ + ': ' + str(exc), 'completed_checks': CHECKS}, indent=2))
        sys.exit(1)
    print(json.dumps(result, indent=2))

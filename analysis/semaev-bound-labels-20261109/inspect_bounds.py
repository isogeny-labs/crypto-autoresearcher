#!/usr/bin/env python3
"""Bounded, exact-input S3 bound inspector; not an LFD or native solver."""
import argparse
import hashlib
import json
from pathlib import Path

THEOREM_SOURCES = {'docs/reports/2026-11-09-fixed-m2-lfd-upper-time/general-m2-time-bound.md': 'de7f146614dd27be7b60bd5228cce4e07dc5a0f2d4796c5b7873a90f59ed2719', 'docs/reports/2026-11-09-fixed-m2-lfd-upper-time/general-m2-bound-audit.md': '69a16b6ba57ca3b10d0b23333ec11f819bafc393ff96795dc8ff67e5ca6f8360', 'docs/reports/2026-11-09-fixed-m2-lfd-upper-time/subfield-sat-time.md': '4a059e5f068facd350c62aa411c011962cd2b067ecb4f6dd7ff41c898648dc75', 'docs/reports/2026-11-09-fixed-m2-fibre-ffd/fibre-refinement.md': '98962a0b18744abdd7a17d9922617421b99145fb21a1a9ea4839b715c261c052', 'docs/reports/2026-11-09-fixed-m2-fibre-ffd/trace-refinement-audit.md': '28c9d6bdc8bd19be80761c61c912208c95866769b7ff53d08b15e5b910740a9d', 'docs/reports/2026-11-09-fixed-m2-fibre-ffd/ffd-qualified-statement.md': '2f9eced92202f3c65dc6f1a9b42cf68d45616eb9c7a5b16f6d52f429f21a2f6d', 'docs/reports/2026-11-09-fixed-m2-fibre-ffd/corrections.md': '6607dca77ea1b4464745cf72793f1d8cd4a71ceaa1435056abac463d2168da78'}

SCHEMA = 'semaev.normalized-binary-m2-input/v1'

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)

def rem(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a

def gcd(a, b):
    while b:
        a, b = b, rem(a, b)
    return a

class Field:
    def __init__(self, n, modulus):
        if type(n) is not int or not 3 <= n <= 64:
            raise ValueError('n must be an integer in [3,64]')
        if type(modulus) is not int or modulus.bit_length() != n + 1 or not modulus & 1:
            raise ValueError('monic odd degree-n modulus required')
        self.n, self.modulus = n, modulus
        # Rabin irreducibility test over F2, with all prime divisors of n.
        factors = {d for d in range(2, n + 1) if n % d == 0 and all(d % q for q in range(2, int(d ** .5) + 1))}
        x, y = 2, 2
        for i in range(1, n + 1):
            y = self.mul(y, y)
            if any(i == n // q for q in factors) and gcd(y ^ x, modulus) != 1:
                raise ValueError('reducible modulus')
        if y != x:
            raise ValueError('reducible modulus')

    def mul(self, a, b):
        out = 0
        for _ in range(self.n):
            if b & 1:
                out ^= a
            b >>= 1
            a <<= 1
            if a >> self.n:
                a ^= self.modulus
        return out

    def power(self, a, e):
        out = 1
        while e:
            if e & 1:
                out = self.mul(out, a)
            a = self.mul(a, a)
            e >>= 1
        return out

    def trace(self, a):
        out = 0
        for _ in range(self.n):
            out ^= a
            a = self.mul(a, a)
        assert out in (0, 1)
        return out

    def inverse(self, a):
        if not a:
            raise ValueError('inverse of zero')
        return self.power(a, (1 << self.n) - 2)


def inspect(spec, product_limit=0):
    required = {'schema', 'n', 'modulus', 'basis', 'a2', 'a6', 'z', 'require_rational_target'}
    if not isinstance(spec, dict) or set(spec) != required or spec['schema'] != SCHEMA:
        raise ValueError('exact normalized input schema required; raw/extra fields refused')
    if type(product_limit) is not int or not 0 <= product_limit <= 4096:
        raise ValueError('product_limit must be an integer in [0,4096]')
    f = Field(spec['n'], spec['modulus'])
    basis = spec['basis']
    if not isinstance(basis, list) or not 1 <= len(basis) <= f.n:
        raise ValueError('basis size must be in [1,n]')
    for a in basis + [spec['a2'], spec['a6'], spec['z']]:
        if type(a) is not int or not 0 <= a < (1 << f.n):
            raise ValueError('field elements must be canonical nonnegative n-bit integers')
    if rank(basis) != len(basis) or not spec['a6'] or not spec['z']:
        raise ValueError('independent basis and nonzero a6,z required')
    if type(spec['require_rational_target']) is not bool:
        raise ValueError('require_rational_target must be boolean')
    k, z, a6 = len(basis), spec['z'], spec['a6']
    z2 = f.mul(z, z)
    trace_constant = f.trace(f.mul(a6, f.inverse(z2)))
    rational = f.trace(z ^ spec['a2'] ^ f.mul(a6, f.inverse(z2))) == 0
    if spec['require_rational_target'] and not rational:
        raise ValueError('target has no rational curve lift')
    # Coefficient polynomial in K, then canonical polynomial-basis F2 descent.
    coefficients = {0: a6}
    for i, v in enumerate(basis):
        c = f.mul(z2, f.mul(v, v))
        coefficients[1 << i] = c
        coefficients[1 << (k + i)] = c
        for j, w in enumerate(basis):
            vw = f.mul(v, w)
            coefficients[(1 << i) | (1 << (k + j))] = f.mul(vw, vw) ^ f.mul(z, vw)
    equations = [[m for m, c in sorted(coefficients.items()) if (c >> b) & 1] for b in range(f.n)]
    binding = {'schema': 'semaev.canonical-quadratic-coordinate-list/v1', 'variables': 2*k,
               'equations': equations, 'explicit_field_equations': 'x_i^2+x_i for every variable',
               'coefficient_basis': '1,t,...,t^(n-1)', 'normalization': 'multilinear Boolean'}
    trace_values = [f.trace(v) for v in basis]
    trace_active = any(trace_values)
    candidates = [{'bound': k+3, 'theorem': 'arbitrary-subspace-all-instance'}]
    if trace_active:
        candidates.append({'bound': k+2, 'theorem': 'nonconstant-trace-selector'})
    elif trace_constant:
        candidates.append({'bound': 2, 'theorem': 'constant-trace-refutation'})
    subfield = f.n == 2*k and all(f.power(v, 1 << k) == v for v in basis)
    if subfield and f.power(z, 1 << k) != z:
        candidates.append({'bound': 3, 'theorem': 'outside-target-quadratic-subfield'})
    product = {'status': 'not_checked', 'scanned_elements': 0, 'distinct_pair_count': None,
               'distinct_product_member': None, 'square_member': None}
    if product_limit and (1 << k) <= product_limit:
        values = {0}
        for v in basis:
            values |= {x ^ v for x in tuple(values)}
        tz = [u for u in values if u and f.mul(z, f.inverse(u)) in values]
        delta = int(f.power(z, 1 << (f.n-1)) in values)
        assert (len(tz)-delta) % 2 == 0
        pairs = (len(tz)-delta)//2
        product = {'status': 'exhaustively_checked', 'scanned_elements': len(values),
                   'distinct_pair_count': pairs, 'distinct_product_member': bool(pairs),
                   'square_member': bool(delta), 'ordered_solution_capacity': (1 << (k+1))-1+len(tz)}
        if not pairs:
            candidates.append({'bound': k+1 if trace_active else k+2,
                               'theorem': 'distinct-product-exclusion-with-trace' if trace_active else 'distinct-product-exclusion'})
    elif product_limit:
        product['status'] = 'not_checked_capacity'
    monomials = sorted({m for eq in equations for m in eq})
    cols = {m:i for i,m in enumerate(monomials)}
    full_rows = [sum(1 << cols[m] for m in eq) for eq in equations if eq]
    top_rows = [sum(1 << cols[m] for m in eq if bin(m).count('1') == 2) for eq in equations if eq]
    all_quadratic = all(any(bin(m).count('1') == 2 for m in eq) for eq in equations if eq) and bool(full_rows)
    pr, qr = rank(full_rows), rank(top_rows)
    ffd = {'definition': 'literal nonzero Petit-Quisquater fall of normalized coordinate list; zero rows omitted',
           'all_nonzero_rows_genuinely_quadratic': all_quadratic, 'full_row_rank': pr, 'quadratic_row_rank': qr,
           'exact_value': 2 if all_quadratic and pr > qr else None,
           'status': 'qualified_degree_two_witness' if all_quadratic and pr > qr else 'not_established'}
    return {'schema': 'semaev.written-bound-inspection/v1', 'input_sha256': digest(spec),
            'equation_binding_sha256': digest(binding), 'equation_binding': binding,
            'n': f.n, 'k': k, 'm': 2, 'target_has_rational_lift': rational,
            'trace_on_basis': trace_values, 'trace_constant': trace_constant,
            'quadratic_subfield_basis': subfield, 'product_profile': product,
            'written_lfd_upper_bound': min(c['bound'] for c in candidates), 'applicable_bounds': candidates,
            'exact_lfd': None, 'lfd_lower_bound': None, 'ffd': ffd,
            'theorem_source_sha256': THEOREM_SOURCES,
            'proof_status': 'application of independently reviewed written arguments; not formal-kernel certification',
            'solver_executed': False, 'native_instruction_count': None}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--product-limit', type=int, default=0)
    args = ap.parse_args()
    if args.input.stat().st_size > 65536:
        raise ValueError('input exceeds 64 KiB')
    raw = args.input.read_bytes()
    if len(raw) > 65536:
        raise ValueError('input exceeds 64 KiB')
    def unique(pairs):
        d = {}
        for k,v in pairs:
            if k in d:
                raise ValueError('duplicate JSON key')
            d[k] = v
        return d
    result = inspect(json.loads(raw, object_pairs_hook=unique), args.product_limit)
    result['input_file_sha256'] = hashlib.sha256(raw).hexdigest()
    result['inspector_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with args.output.open('x') as out:
        json.dump(result, out, sort_keys=True, indent=2)
        out.write('\n')

if __name__ == '__main__':
    main()

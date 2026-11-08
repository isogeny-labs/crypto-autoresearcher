#!/usr/bin/env python3
"""Independent F_5 controls, constructed solely from the blind card.

This program enumerates only the requested tuple lengths zero and one. It is
not a general group implementation or an inspection of producer code.
"""
import hashlib
import itertools
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
MOD = 5
O = None
A = (0, 1)
B = (2, 1)


def equation(p):
    x, y = p
    return (y*y - x*x*x - x - 1) % MOD == 0


def nonsingular(p):
    x, y = p
    return (-3*x*x - 1) % MOD != 0 or (2*y) % MOD != 0


def span(family):
    return sorted({sum(c*x for c, x in zip(cs, family)) % MOD
                   for cs in itertools.product(range(MOD), repeat=len(family))})


def short_sum(points):
    if len(points) == 0:
        return O
    if len(points) == 1:
        return points[0]
    raise ValueError('Only the requested zero/singleton controls are implemented')


def typed_decide(points, target, family):
    assert all(p is O or (equation(p) and nonsingular(p)) for p in points)
    return (all(p is not O and p[0] in span(family) for p in points)
            and short_sum(points) == target)


def raw_decide(points, target, family):
    if not all(equation(p) and nonsingular(p) for p in points):
        return False
    return typed_decide(points, target, family)


def main():
    families = [('empty', ()), ('zero', (0,)), ('unit', (1,))]
    targets = [('O', O), ('A', A), ('B', B)]
    raw_inputs = [('empty', ()), ('off_curve', ((0, 0),)), ('A', (A,)), ('B', (B,))]
    typed_inputs = [('empty', ()), ('identity', (O,)), ('A', (A,)), ('B', (B,))]
    points = [(x, y) for x in range(MOD) for y in range(MOD) if equation((x, y))]
    assert points == [(0, 1), (0, 4), (2, 1), (2, 4), (3, 1), (3, 4), (4, 2), (4, 3)]
    assert all(nonsingular(p) for p in points)
    assert [span(f) for _, f in families] == [[0], [0], [0, 1, 2, 3, 4]]
    assert (-16*(4 + 27)) % MOD == 4
    rows = []
    for kind, inputs, decide in [('raw', raw_inputs, raw_decide), ('typed', typed_inputs, typed_decide)]:
        for family_name, family in families:
            for input_name, inputs_value in inputs:
                for target_name, target in targets:
                    accepted = decide(inputs_value, target, family)
                    expected = ((input_name == 'empty' and target_name == 'O')
                                or (input_name == 'A' and target_name == 'A')
                                or (input_name == 'B' and target_name == 'B' and family_name == 'unit'))
                    assert accepted == expected, (kind, family_name, input_name, target_name)
                    rows.append(dict(kind=kind, family=family_name, input=input_name,
                                     target=target_name, accepted=accepted))
    result = dict(modulus=MOD, curve='y^2=x^3+x+1', discriminant_mod_5=4,
                  affine_points=points, point_count_including_identity=len(points)+1,
                  spans={name: span(f) for name, f in families},
                  controls=rows, control_count=len(rows),
                  accepted_count=sum(r['accepted'] for r in rows), mismatches=0,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'controls.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['control_count', 'accepted_count', 'mismatches', 'script_sha256']}))


if __name__ == '__main__':
    main()

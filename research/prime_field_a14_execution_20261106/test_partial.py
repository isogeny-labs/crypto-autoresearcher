"""Small finite-field software controls only; no fresh A14 curves or targets."""
from copy import deepcopy
from pathlib import Path
import random
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import solver, known_solver
import partial_solver
from check_partial import check


def fixture():
    return dict(p=101, r=101, a=2, b=3, software_control=True)


def case(width, nt, known, M, B, U, z, q):
    def rhs(v, u):
        return (sum(a*b for a, b in zip(v, z, strict=True))+sum(a*b for a, b in zip(u, q, strict=True))) % 101
    units = [([int(k == j) for k in range(width)], value) for j, value in known]
    return dict(width=width, target_count=nt, modulus=101, targets=[],
        source=units+[(v, rhs(v, [0]*nt)) for v in M],
        target=[dict(vector=v, outside=u, rhs=rhs(v, u)) for v, u in zip(B, U, strict=True)])


def solve_control(c, known, basis):
    out = partial_solver.solve(c, known, basis, solver.Meter(fixture()))
    assert check(c, known, basis, out)['checked']
    native = solver.solve(c, 'sparse_joint', solver.Meter(fixture()))
    assert [(v['identifiable'], v['scalar']) for v in out['recoveries']] == [(v['identifiable'], v['scalar']) for v in native['recoveries']]
    return out


def test_supplied_helpers_and_signed_old_basis_lift_to_original_units():
    z, q, known = [3, 8, 11, 19], [7, 13, 17], [(0, 3), (3, 19)]
    c = case(4, 3, known, [[1, 1, 1, 0]],
             [[1, 0, 0, 1], [0, 0, 0, 1]], [[98, 0, 0], [1, 1, 0]], z, q)
    result = solve_control(c, known, [(2, -1), (1, 1)])
    assert [v['identifiable'] for v in result['recoveries']] == [True, True, False]
    assert result['system']['nullity'] > 0
    assert all(len(v['original_row_weights']) == len(c['source'])+len(c['target'])
               for v in result['recoveries'] if v['identifiable'])


def test_native48_helper16_keeps_old_coordinates_even_when_one_is_revealed():
    z, q = list(range(1, 49)), list(range(51, 59))
    known = [(0, z[0])]+[(j, z[j]) for j in range(32, 48)]
    # Supplied helper coincidence reveals native column5 through an explicit
    # equation.  Column5 stays in the unchanged old-unknown basis.
    revealed = [int(j == 5) for j in range(48)]
    target = [int(j == 33) for j in range(48)]
    c = case(48, 8, known, [revealed], [target], [[98]+[0]*7], z, q)
    basis = [(j, 1 if j % 2 else -1) for j in range(1, 32)]
    result = solve_control(c, known, basis)
    assert len(result['unknown_basis']) == 31 and [5, 1] in result['unknown_basis']
    assert result['recoveries'][0]['scalar'] == q[0]
    assert sum(v['identifiable'] for v in result['recoveries']) == 1
    assert check(c, known, basis, result)['delta'] == 0


def test_all_known_matches_executed_a13_direct_field_counts():
    z, q = [3, 8, 11], [7, 13]
    known = list(enumerate(z))
    c = case(3, 2, known, [], [[1, 0, 100], [0, 1, 1]], [[98, 0], [1, 1]], z, q)
    new = solve_control(c, known, [])
    old = known_solver.solve(c, z, solver.Meter(fixture()))
    assert [v['original_row_weights'] for v in new['recoveries']] == [v['original_row_weights'] for v in old['recoveries']]
    for operation in ('add', 'sub', 'mul', 'inv'):
        key = 'Fr.field_'+operation
        assert new['counters'].get(key, 0) == old['counters'].get(key, 0)


def test_no_known_columns_and_zero_width():
    solve_control(case(2, 2, [], [[1, 0]], [[0, 1]], [[100, 0]], [3, 8], [7, 13]), [], [(1, -1), (0, 1)])
    solve_control(case(0, 2, [], [], [[], []], [[2, 0], [1, 1]], [], [7, 13]), [], [])
    solve_control(case(0, 0, [], [], [], [], [], []), [], [])


def test_random_partial_systems_and_signed_permutations_against_native_joint():
    rng = random.Random(714)
    for _ in range(40):
        width, nt, n = rng.randrange(7), rng.randrange(5), rng.randrange(9)
        z, q = [rng.randrange(101) for _ in range(width)], [rng.randrange(101) for _ in range(nt)]
        columns = list(range(width))
        rng.shuffle(columns)
        count = rng.randrange(width+1)
        known = [(j, z[j]) for j in columns[:count]]
        basis = [(j, rng.choice((1, -1))) for j in columns[count:]]
        M = [[rng.randrange(101) for _ in range(width)] for _ in range(n//2)]
        B = [[rng.randrange(101) for _ in range(width)] for _ in range(n)]
        U = [[rng.randrange(101) for _ in range(nt)] for _ in range(n)]
        solve_control(case(width, nt, known, M, B, U, z, q), known, basis)


@pytest.mark.parametrize('corruption', ['known_value', 'unit', 'duplicate', 'basis_duplicate', 'basis_sign', 'basis_known', 'basis_missing'])
def test_invalid_supplied_information_and_basis_refuse(corruption):
    c = case(3, 2, [(0, 3)], [], [[1, 0, 0]], [[100, 0]], [3, 8, 11], [7, 13])
    known, basis = [(0, 3)], [(1, 1), (2, -1)]
    if corruption == 'known_value': known[0] = (0, 4)
    elif corruption == 'unit': c['source'][0][0][0] = 2
    elif corruption == 'duplicate': known.append((0, 3))
    elif corruption == 'basis_duplicate': basis[1] = (1, 1)
    elif corruption == 'basis_sign': basis[0] = (1, 2)
    elif corruption == 'basis_known': basis[0] = (0, 1)
    elif corruption == 'basis_missing': basis.pop()
    with pytest.raises(ValueError):
        partial_solver.solve(c, known, basis, solver.Meter(fixture()))


@pytest.mark.parametrize('corruption', ['lift', 'reduced_weights', 'known', 'basis', 'rank', 'negative', 'residual', 'counter'])
def test_independent_checker_refuses_corrupted_native_certificates(corruption):
    known, basis = [(0, 3)], [(1, -1)]
    c = case(2, 2, known, [], [[1, 0]], [[100, 0]], [3, 8], [7, 13])
    out = solve_control(c, known, basis)
    if corruption == 'lift': out['recoveries'][0]['original_row_weights'][0] += 1
    elif corruption == 'reduced_weights': out['recoveries'][0]['row_weights'][0] += 1
    elif corruption == 'known': out['known_columns'][0][1] += 1
    elif corruption == 'basis': out['unknown_basis'][0][1] *= -1
    elif corruption == 'rank': out['system']['rank'] += 1
    elif corruption == 'negative': out['recoveries'][1]['identifiable'] = True
    elif corruption == 'residual': out['recoveries'][1]['residual'][-1] = 0
    elif corruption == 'counter': out['counters']['Fr.field_sub'] += 1
    with pytest.raises(ValueError):
        check(c, known, basis, out)

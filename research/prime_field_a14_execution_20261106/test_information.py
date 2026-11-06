"""Outside-corrected information, attribution and native lifting controls."""
from copy import deepcopy
from pathlib import Path
import random
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared import solver
import information, check_information


def example(M, H, C, B, U):
    r, w, nt = 101, 2, 1
    z, q = [5, 7]+list(range(19, 35)), [11]
    f = dict(p=101, r=r, a=2, b=3, software_control=True)
    norm_prepared = dict(known=[], basis=[[1, -1], [0, 1]],
        cell=dict(fixture=dict(factor_base=[dict(point=[j, j+1]) for j in range(w)])))
    hybrid_prepared = dict(known=[[j, z[j]] for j in range(w, w+16)],
        basis=norm_prepared['basis'], cell=dict(fixture=dict(factor_base=
            norm_prepared['cell']['fixture']['factor_base']+[dict(point=[j, j+1]) for j in range(w, w+16)])))
    def rhs(v, u): return (sum(a*b for a, b in zip(v, z, strict=False))+sum(a*b for a, b in zip(u, q, strict=True))) % r
    norm = dict(width=w, target_count=nt, modulus=r, targets=[dict(index=0, point=[2, 3])],
        source=[(v, rhs(v, [0])) for v in M], target=[])
    units = [([int(k == j) for k in range(w+16)], value) for j, value in hybrid_prepared['known']]
    source = units+[(v+[0]*16, rhs(v, [0])) for v in H+C]
    origins = [dict(kind='supplied_native_unit') for _ in units]+[dict(kind='supplied_owned_cache_match') for _ in H]+[dict(kind='collected_source') for _ in C]
    hybrid = dict(width=w+16, target_count=nt, modulus=r, targets=norm['targets'], source=source,
        source_origins=origins, target=[dict(vector=v, rhs=rhs(v, u), outside=u) for v, u in zip(B, U, strict=True)])
    result = information.compare(norm, norm_prepared, hybrid, hybrid_prepared, solver.Meter(f))
    return norm, norm_prepared, hybrid, hybrid_prepared, result


def check(value):
    return check_information.check(*value)


def test_outside_columns_do_not_inflate_new_base_information_and_native_units_lift():
    # Two independent joint equations have one cancelled base direction.
    a, b = [1, 0]+[0]*16, [0, 1]+[0]*16
    a[2], b[3] = 3, 4
    value = example([], [], [], [a, b], [[100], [100]])
    result = check(value)
    assert result['delta_vs_old'] == 1 and result['outside_rank'] == 1
    assert result['increments'] == dict(supplied=0, collected_after_supplied=0, targets_after_cancellation=1)
    assert len(value[-1]['cancellations']) == 1
    assert any(value[-1]['cancellations'][0]['supplied_unit_weights'])


def test_paid_knowledge_is_attributed_before_new_collected_rows():
    value = example([[1, 0]], [[0, 1]], [[0, 1]], [], [])
    result = check(value)
    assert result['delta_vs_old'] == 1
    assert result['increments'] == dict(supplied=1, collected_after_supplied=0, targets_after_cancellation=0)
    assert len(result['old_kernel']) == 1


@pytest.mark.parametrize('seed', range(8))
def test_random_affine_partial_rows_match_dense_block_rank_and_kernel_action(seed):
    rng = random.Random(seed)
    M = [[rng.randrange(101) for _ in range(2)] for _ in range(seed % 3)]
    H = [[0, 1]] if seed % 2 else []
    C = [[rng.randrange(101) for _ in range(2)] for _ in range(seed % 2)]
    B = [[rng.randrange(101) for _ in range(18)] for _ in range(6)]
    U = [[rng.randrange(101)] for _ in B]
    assert check(example(M, H, C, B, U))['checked']


@pytest.mark.parametrize('change', ['delta', 'supply', 'kernel_residual', 'outside', 'lift', 'rhs', 'missing'])
def test_information_checker_refuses_false_attribution_or_original_certificates(change):
    value = deepcopy(example([], [[1, 0]], [], [[1, 0]+[3]+[0]*15, [0, 1]+[0, 4]+[0]*14], [[1], [1]]))
    actual = value[-1]
    if change == 'delta': actual['delta_vs_old'] += 1
    elif change == 'supply': actual['groups']['collected'] = actual['groups'].pop('supplied')
    elif change == 'kernel_residual': actual['cancellations'][0]['old_rowspace']['residual'][0] += 1
    elif change == 'outside': actual['cancellations'][0]['original_target_weights'][0][1] = 1
    elif change == 'lift': actual['cancellations'][0]['supplied_unit_weights'][0] += 1
    elif change == 'rhs': actual['cancellations'][0]['rhs'] += 1
    elif change == 'missing': actual['cancellations'].pop()
    with pytest.raises((ValueError, KeyError)):
        check(value)


def test_cross_base_or_reordered_original_unknowns_cannot_be_scored():
    norm, p, hybrid, h, _ = example([], [], [], [], [])
    h = deepcopy(h)
    h['basis'].reverse()
    with pytest.raises(ValueError, match='matched norm/hybrid'):
        information.compare(norm, p, hybrid, h, solver.Meter(dict(p=101, r=101, a=2, b=3)))

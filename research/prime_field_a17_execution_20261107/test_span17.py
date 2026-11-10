"""Actual tiny paired runs and complete native-row containment witnesses."""
from copy import deepcopy
import pytest
import check_span17
from test_preconstruct17 import toy,fresh
from test_query17 import completed,special_fixture


def test_every_full_reference_row_has_a_candidate_native_consequence(toy):
    results={};fixture=None
    for arm in ('suppress','full'):
        prep,col,recipe,r,_=special_fixture(toy,arm);fixture=prep['cell']['fixture']
        results[arm]=completed(prep,col,recipe,r,arm)[0]
    proof=check_span17.check(results['full'],results['suppress'],fixture)
    assert proof['checked'] and len(proof['witnesses'])==len(results['full']['case']['target'])
    assert proof['omitted_reference_rows']>=1
    bad=deepcopy(results['full']);bad['case']['target'][-1]['rhs']=(bad['case']['target'][-1]['rhs']+1)%fixture['r']
    with pytest.raises(ValueError):check_span17.check(bad,results['suppress'],fixture)
    bad=deepcopy(results['suppress']);bad['case']['source'].pop()
    with pytest.raises(ValueError):check_span17.check(results['full'],bad,fixture)

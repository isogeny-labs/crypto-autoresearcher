"""Actual p211 causal prefixes and counter-binding mutation controls."""
from copy import deepcopy
import pytest
from deps17 import checks16,commitment
import check_query17
from test_preconstruct17 import toy,fresh
from test_query17 import completed,special_fixture


def test_both_actual_tiny_programs_have_causal_prefix_proofs(toy):
    for arm in ('suppress','full'):
        prep,col,recipe,r=fresh(toy,arm);result,cloud,cache,events=completed(prep,col,recipe,r,arm)
        _,oracle=checks16.collection(prep,r,col)
        proof=check_query17.check(prep,col,cloud,cache,result,events,r,arm,oracle)
        assert proof['checked'] and proof['executed_extra_slots']+proof['skipped_slots']==46


def test_actual_extra_query_and_skip_causal_tampering(toy):
    prep,col,recipe,r,_=special_fixture(toy,'suppress');result,cloud,cache,events=completed(prep,col,recipe,r,'suppress')
    _,oracle=checks16.collection(prep,r,col)
    proof=check_query17.check(prep,col,cloud,cache,result,events,r,'suppress',oracle)
    assert proof['skipped_slots']>0 and proof['executed_extra_slots']>0 and proof['own_prefix_certificates']==1
    def check(ev,res=None):return check_query17.check(prep,col,cloud,cache,result if res is None else res,ev,r,'suppress',oracle)
    def remove_cert(ev):ev[:]=[v for v in ev if v['kind']!='online_target_certified']
    def later_cert(ev):
        index=next(i for i,v in enumerate(ev) if v['kind']=='online_target_certified');cert=ev.pop(index)
        skip=next(i for i,v in enumerate(ev) if v['kind']=='slot_skipped');ev.insert(skip+1,cert)
    def wrong_skip(ev):next(v for v in ev if v['kind']=='slot_skipped')['certificate_id']='0'*64
    def no_public_check(ev):
        v=next(v for v in ev if v['kind']=='affine_phase' and v['phase']['phase'].startswith('online_public_certificate_'))
        v['phase']['counters']['public_target_certificates_verified']=0
    def early_start(ev):
        index=next(i for i,v in enumerate(ev) if v['kind']=='full_preconstruction_complete');v=ev.pop(index)
        start=next(i for i,v in enumerate(ev) if v['kind']=='online_start');ev.insert(start+1,v)
    def missing_row(ev):
        index=next(i for i,v in enumerate(ev) if v['kind']=='online_native_row');ev.pop(index)
    for mutation in (remove_cert,later_cert,wrong_skip,no_public_check,early_start,missing_row):
        changed=deepcopy(events);mutation(changed)
        with pytest.raises(ValueError):check(changed)
    # Keep producer result, journal phases and completion digest mutually
    # consistent. An independent schedule must still reject invented Fr work.
    changed=deepcopy(events);res=deepcopy(result)
    res['scheduling_counters']['Fr.field_mul']=1;res['scheduling_phases'][0]['counters']['Fr.field_mul']=1
    phase=next(v for v in changed if v['kind']=='affine_phase' and v['context'].get('kind')=='query_scheduling')
    phase['phase']['counters']['Fr.field_mul']=1
    next(v for v in changed if v['kind']=='query_program_complete')['producer_output_sha256']=commitment(res)
    with pytest.raises(ValueError,match='independent scheduling'):check(changed,res)

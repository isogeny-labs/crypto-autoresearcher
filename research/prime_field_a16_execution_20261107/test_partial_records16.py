"""Actual p211 norm-program records + explicitly mocked I/O admission metadata.

This is a partial software fixture, not a native run or an S3 checkpoint. It
checks that missing other programs do not erase independently checked earlier
programs, and that full cost commitments reject later record tampering.
"""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from test_horizons16 import rules
from deps16 import core,Meter,check_source,checker,commitment,old_check,solver,partial_solver,check_partial,known_checks,native_case
from driver14 import public_verify
from programs16 import rules_for,descriptors,recipe_prefix
from streams16 import append
from ownership16 import OwnedTargetCache
import collection16,branch16,checks16,analyze16


def put(path,value):path.write_text(json.dumps(value,sort_keys=True)+'\n')
def checked(value):return dict(verification=value,wall_valid=False)


@pytest.fixture(scope='module')
def partial_fixture(tmp_path_factory):
    run=tmp_path_factory.mktemp('a16-software-partial');raw=run/'raw';raw.mkdir()
    r=rules();r.update(closed_curve_checkpoint=False,information_audits=48)
    rr=rules_for(r,'norm8');generated=core.generate(r,lambda v:None);original=generated['cells'][0];cid=original['id']
    put(raw/'generated.json',generated);g=check_source.check_generation(r,generated);g['producer_output_sha256']=commitment(generated)
    put(raw/'generation-check.json',checked(g))
    # Deliberately mocked only for this marked p211 fixture; no network or gate.
    put(raw/'admission.json',dict(software_control=True,returncode=0,command=['bash','scripts/checkpoint.sh','gate'],last_push='SOFTWARE_FIXTURE_NO_UPLOAD'))
    put(run/'child.json',dict(software_control=True,child_pid=1,supervisor_pid=2,child_process_group=1))
    put(run/'checkpoint-admitted-start.json',dict(software_control=True,returncode=0,native_curves_generated=0,
        command=['bash','scripts/checkpoint.sh','push'],admission_last_push='SOFTWARE_FIXTURE_NO_UPLOAD',child_pid=1,supervisor_pid=2,child_process_group=1))
    names=('events','branches','case-inputs','solver-outputs','case-checks')
    streams={name:(raw/(cid+'.'+name+'.jsonl')).open('w') for name in names}
    event=lambda v:append(streams['events'],v)
    emit=lambda v:event(dict(program='norm8',base_arm='norm',**v))
    try:
        prep=collection16.prepare(original,rr,None,emit)
        put(raw/(cid+'.norm8.prelude.json'),prep)
        old_check.preparation(original,rr,None,prep)
        put(raw/(cid+'.norm8.prelude-check.json'),checked(dict(checked=True,producer_output_sha256=commitment(prep))))
        meter=core.ProgressMeter(original['fixture'],event,dict(kind='shared_public_targets'))
        targets=meter.stage('target_generation',lambda:core.old.targets(original,r,meter,event))
        payload=dict(generation=targets,phases=meter.phases,counters=meter.counters());put(raw/(cid+'.targets.json'),payload)
        old_check.targets(original,r,targets);put(raw/(cid+'.targets-check.json'),checked(dict(checked=True,producer_output_sha256=commitment(payload))))
        recipes={}
        for h,name in ((8,'norm8'),(24,'known48_24')):
            hr=rules_for(r,name);e=lambda v,h=h:event(dict(target_recipe_horizon=h,**v))
            m=core.ProgressMeter(original['fixture'],e,dict(kind='target_recipes',target_horizon=h))
            v=m.stage('target_recipes',lambda:core.recipes(original,{},hr,m,e));checker.recipes(original,hr,v);recipes[h]=v
            payload=dict(selection=v,phases=m.phases,counters=m.counters());put(raw/(cid+'.target-recipes-h'+str(h)+'.json'),payload)
            put(raw/(cid+'.target-recipes-h'+str(h)+'-check.json'),checked(dict(checked=True,producer_output_sha256=commitment(payload),
                independent_hashes=sum(1 if x['policy']=='hash_offset' else 2 for x in v['trace']))))
        put(raw/(cid+'.target-recipe-prefix-check.json'),checked(dict(checked=recipe_prefix(recipes[8],recipes[24],r['targets'],r['target_policies']))))
        c=collection16.collect(prep,targets,rr,emit);put(raw/(cid+'.norm8.source.json'),dict(cell=prep['cell'],collection=c))
        verify,oracle=checks16.collection(prep,rr,c);put(raw/(cid+'.norm8.source-check.json'),checked(verify))
        cache=OwnedTargetCache(c.query_index,c['natural_records'],rr,emit)
        group=checker.GroupOracle(prep['cell']['fixture'],targets['targets']);plans=dict(descriptors(r))
        index=0
        for schedule in ('ap0','hash0'):
            for policy in r['target_policies']:
                context=dict(source_schedule=schedule,source_prefix=r['sources'],target_policy=policy)
                recipe=recipes[8]['policies'][policy]
                b=branch16.build(prep['cell'],c,rr,recipe,schedule,r['sources'],policy,cache,emit)
                ref=append(streams['branches'],dict(program='norm8',base_arm='norm',context=context,branch=b));emit(dict(kind='branch_output',context=context,record=ref))
                verify=checks16.branch(prep['cell'],c,rr,recipe,b,cache,group);emit(dict(kind='branch_checked',context=context,verification=verify))
                for budget in rr['target_prefixes']:
                    for scope in rr['norm_scopes']:
                        desc=plans[index];m=core.ProgressMeter(prep['cell']['fixture'],emit,dict(kind='native_matrix_assembly',case_id=index))
                        case=m.stage('native_matrix_assembly',lambda:native_case.build(prep,c,b,cache,budget,scope,m))
                        item=dict(case_id=index,descriptor=desc,case=case,shared_phases=m.phases)
                        ref=append(streams['case-inputs'],item);emit(dict(kind='case_input',case_id=index,descriptor=desc,record=ref))
                        outputs=[]
                        for method in ('partial_joint','sparse_joint'):
                            mm=Meter(prep['cell']['fixture'])
                            result=partial_solver.solve(case,prep['known'],prep['basis'],mm) if method=='partial_joint' else solver.solve(case,method,mm)
                            public_verify(result,case,prep['cell']['fixture'],mm)
                            ref=append(streams['solver-outputs'],dict(case_id=index,arm=method,result=result))
                            emit(dict(kind='solver_complete',case_id=index,descriptor=desc,arm=method,record=ref,counters=result['counters']));outputs.append(result)
                        verify=dict(checked=True,partial=check_partial.check(case,prep['known'],prep['basis'],outputs[0],prep['cell']['fixture']),
                            joint=known_checks.joint_case(case,outputs[1],prep['cell']['fixture']),case_sha256=commitment(case),
                            solver_output_sha256={name:commitment(value) for name,value in zip(('partial_joint','sparse_joint'),outputs,strict=True)})
                        ref=append(streams['case-checks'],dict(case_id=index,descriptor=desc,verification=verify))
                        emit(dict(kind='case_checked',case_id=index,descriptor=desc,record=ref));index+=1
        put(raw/(cid+'.norm8.query-cache.json'),checks16.cache_payload(cache))
        put(raw/(cid+'.norm8.query-check.json'),checked(checks16.target_cache(prep,c,cache,oracle,rr)))
    finally:
        for stream in streams.values():stream.close()
    return run,r,cid,index


def test_partial_program_keeps_actual_algebra_and_cost_records(partial_fixture):
    run,r,cid,number=partial_fixture
    result=analyze16.summarize(run,r,dict(returncode=1,timeout=False,exception=None,source_unchanged_after=True))
    assert result['panel_complete']is False
    assert sum(v['verified'] for v in result['cells'])==number==48
    assert len(result['cold_views'])==48 and result['observed_completed_solver_calls']==96
    assert all(not v['verified'] for v in result['cells'] if v['program']!='norm8')


def test_independent_pair_cost_rejects_forged_payload_hash(partial_fixture):
    run,r,cid,_=partial_fixture
    source=json.loads((run/'raw'/(cid+'.norm8.source.json')).read_text())['collection']
    proof=json.loads((run/'raw'/(cid+'.norm8.source-check.json')).read_text())['verification']['pair_construction']
    assert analyze16.pair_cost_binding(source,proof)
    mutated=deepcopy(source)
    phase=next(p for p in mutated['collection_phases'] if p['phase']=='pair_shared_formulas')
    phase['counters']['Fp.field_mul']+=1;mutated['collection_counters']['Fp.field_mul']+=1
    assert analyze16.phase_binding(mutated,'collection_phases','collection_counters')
    with pytest.raises(ValueError):analyze16.pair_cost_binding(mutated,proof)
    forged=deepcopy(proof);forged['construction_counters']['Fp.field_mul']+=1;forged['pair_stage_counters']['Fp.field_mul']+=1
    with pytest.raises(ValueError,match='arithmetic'):analyze16.pair_cost_binding(mutated,forged)

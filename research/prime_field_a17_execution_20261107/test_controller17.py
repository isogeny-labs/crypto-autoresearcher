"""Software-only p211 controller/cost fixtures; no native48 or fresh-field trials.

The archive fixture supplies explicitly synthetic generation/base/prelude checker
receipts to exercise metadata I/O only. Query/constructor/causal/native algebra
and row-consequence work is real on the fixed three-atom p211 control. These
receipts are never an admissible scientific archive or root release.
"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from collections import Counter
import json
import pytest
from deps17 import commitment,Meter,partial_solver,solver,public_verify,check_partial,known_checks,checks16
from test_preconstruct17 import toy
from test_query17 import special_fixture,completed
from cost17 import cache_payload,cold
import analyze17,check_query17,check_construct17,check_span17,prepare17,custody17,driver17


def write(path,value):path.write_text(json.dumps(value,sort_keys=True)+'\n')
def receipt(value,**extra):return dict(verification=dict(checked=True,producer_output_sha256=commitment(value),**extra))


@pytest.fixture(scope='module')
def software_archive(tmp_path_factory,toy):
    run=tmp_path_factory.mktemp('a17-explicit-software-io');raw=run/'raw';raw.mkdir()
    rules=dict(software_control=True,fields=[dict(p=211)],curves_per_field=4,targets=1)
    generated=dict(cells=[dict(id='p211-i'+str(i)) for i in range(4)])
    write(raw/'generated.json',generated);write(raw/'generation-check.json',receipt(generated,curves=4))
    child=dict(child_pid=12,child_process_group=12,supervisor_pid=11);write(run/'child.json',child)
    write(raw/'admission.json',dict(returncode=0,command=['bash','scripts/checkpoint.sh','gate'],last_push='software-only'))
    write(run/'checkpoint-admitted-start.json',dict(returncode=0,command=['bash','scripts/checkpoint.sh','push'],native_curves_generated=0,admission_last_push='software-only',**child))
    for ci in range(4):
        cid='p211-i'+str(ci);vals={};shared=[];masks={}
        for ai,arm in enumerate(('suppress','full')):
            prep,col,recipe,r,_=special_fixture(toy,arm);prep['cell']['id']=cid
            # collection is real tiny geometry, but its creation predates the
            # buffered constructor in this helper; restore its exact phases.
            col_events=[dict(kind='affine_phase',context=dict(kind='software_fixture_collection'),phase=p) for p in col['collection_phases']]
            result,cloud,cache,evs=completed(prep,col,recipe,r,arm);evs=col_events+evs
            coll_proof,oracle=checks16.collection(prep,r,col)
            qp=check_query17.check(prep,col,cloud,cache,result,evs,r,arm,oracle)
            built=dict(cell=prep['cell'],knowledge=prep['initial'],arm_owner=arm,counters={},phases=[])
            rec=dict(selection=dict(policies=dict(general=recipe),trace=[]),arm_owner=arm,counters={},phases=[])
            targets=dict(generation=col['target_generation'],counters={},phases=[])
            values=dict(base=built,prelude=prep,recipe=rec,collection=dict(cell=prep['cell'],collection=col),construction=cloud,query=result,cache=cache_payload(cache))
            proofs={name:receipt(values[name]) for name in ('base','prelude')}
            proofs['recipe']=receipt(rec,independent_hashes=0);proofs['collection']=dict(verification=coll_proof)
            proofs['construction']=dict(verification=check_construct17.check(prep['cell'],col,r,recipe,cloud,arm))
            proofs['query']=dict(verification=qp)
            primary=result.get('online')
            if arm=='full':
                evs.append(dict(kind='batch_solver_start',execution_arm=arm,method='partial_joint'))
                m=Meter(prep['cell']['fixture']);primary=partial_solver.solve(result['case'],prep['known'],[],m);public_verify(primary,result['case'],prep['cell']['fixture'],m)
                check_partial.check(result['case'],prep['known'],[],primary,prep['cell']['fixture'])
                evs.append(dict(kind='batch_solver_complete',execution_arm=arm,method='partial_joint',counters=primary['counters']))
            values['primary']=primary;proofs['primary']=receipt(primary)
            m=Meter(prep['cell']['fixture']);joint=solver.solve(result['case'],'sparse_joint',m);public_verify(joint,result['case'],prep['cell']['fixture'],m)
            known_checks.joint_case(result['case'],joint,prep['cell']['fixture']);values['joint']=joint
            evs.extend([dict(kind='batch_solver_start',execution_arm='joint_on_'+arm,method='sparse_joint'),dict(kind='batch_solver_complete',execution_arm='joint_on_'+arm,method='sparse_joint',counters=joint['counters'])])
            proofs['joint']=receipt(joint,primary_output_sha256=commitment(primary))
            values['cold']=cold(arm,built,prep,col,rec,targets,cloud,result,values['cache'],primary)
            idx=2*ci+ai;desc=dict(custody17.descriptors(rules))[idx]
            values['complete']=dict(complete=True,case_id=idx,descriptor=desc,**{k+'_output_sha256':commitment(values[k]) for k in ('query','primary','joint','cold')})
            for key,value in values.items():write(raw/(cid+'.'+arm+'.'+key+'.json'),value)
            for key,value in proofs.items():write(raw/(cid+'.'+arm+'.'+key+'-check.json'),value)
            (raw/(cid+'.'+arm+'.events.jsonl')).write_text(''.join(json.dumps(ev)+'\n' for ev in evs))
            vals[arm]=values;masks[arm]=sum(1<<v['target_index'] for v in primary['recoveries'] if v['identifiable'])
        write(raw/(cid+'.targets.json'),targets);write(raw/(cid+'.targets-check.json'),receipt(targets))
        span=check_span17.check(vals['full']['query'],vals['suppress']['query'],prep['cell']['fixture'],shared.append)
        write(raw/(cid+'.row-consequences.json'),span)
        (raw/(cid+'.shared.events.jsonl')).write_text(''.join(json.dumps(ev)+'\n' for ev in shared))
        write(raw/(cid+'.complete.json'),dict(complete=True,curve_index=ci,checked_case_systems=2*(ci+1),completed_batch_solver_calls=3*(ci+1),
            completed_online_engines=ci+1,verified_execution_rows=4*(ci+1),row_consequences_sha256=commitment(span),full_construction_equal=True,identified_mask=masks['full']))
        write(run/('checkpoint-'+cid+'.json'),dict(returncode=0,command=['bash','scripts/checkpoint.sh','push'],closed_curve=cid,completed_curves=ci+1,
            checked_cases=2*(ci+1),checked_batch_solver_calls=3*(ci+1),completed_online_engines=ci+1,stdout='software-mocked s3://setec-astronomy-artifacts/checkpoints/fixture/'))
    execution=dict(returncode=0,timeout=False,exception=None,source_unchanged_after=True)
    return run,rules,execution


def test_complete_software_io_census_and_costs(software_archive):
    run,rules,execution=software_archive;data=analyze17.summarize(run,rules,execution)
    assert data['panel_complete'] and len(data['cells'])==8 and len(data['cold_views'])==8
    assert data['observed_completed_batch_solver_calls']==12 and data['observed_completed_online_engines']==4
    assert sum(v['verified'] for v in data['cells'])==8 and len(data['row_consequences'])==4
    assert all(v['proof']['omitted_reference_rows']>=1 for v in data['row_consequences'])


def test_missing_and_failed_prefix_remain_unknown(tmp_path,software_archive):
    _,rules,execution=software_archive;data=analyze17.summarize(tmp_path,rules,dict(execution,returncode=1))
    assert not data['panel_complete'] and len(data['cells'])==8 and all(not v['verified'] for v in data['cells'])
    raw=tmp_path/'raw';raw.mkdir();(raw/'p211-i0.suppress.events.jsonl').write_text(json.dumps(dict(kind='affine_phase',context=dict(kind='query_scheduling'),phase=dict(counters={'paid_prefix':7})))+'\n'+json.dumps(dict(kind='query_program_failed',error='software_fixture'))+'\n')
    data=analyze17.summarize(tmp_path,rules,dict(execution,returncode=1))
    assert data['physical_counters']['p211-i0.suppress.query_scheduling']['paid_prefix']==7 and data['errors']


def test_cold_cost_or_phase_forgery_rejected(tmp_path,software_archive):
    import shutil
    source,rules,execution=software_archive;run=tmp_path/'copy';shutil.copytree(source,run)
    path=run/'raw/p211-i0.suppress.cold.json';value=json.loads(path.read_text());value['physical_engine_counters']['Fr.field_mul']=0;write(path,value)
    with pytest.raises(ValueError,match='cold vector'):analyze17.summarize(run,rules,execution)


def test_independent_budget_preserves_deadline_and_reserves_prior_cpu():
    original=custody17.load(custody17.BUDGET_INPUTS[0]);issued=datetime.fromisoformat(original['issued_utc'])
    budget=prepare17.remaining_budget(issued+timedelta(seconds=3600))
    assert budget['absolute_deadline']==original['absolute_deadline'] and budget['known_prior_cpu_seconds']>578
    assert budget['watchdog_seconds']<18000 and budget['elapsed_window_reservation_seconds']==3600
    with pytest.raises(ValueError,match='exhausted'):prepare17.remaining_budget(datetime.fromisoformat(original['absolute_deadline']))


def test_driver_refusal_happens_before_generation(tmp_path,monkeypatch):
    import sys
    monkeypatch.setattr(sys,'argv',['driver17','--inputs',str(tmp_path/'absent'),'--protocol',str(tmp_path/'absentp'),'--release',str(tmp_path/'absentr'),'--out',str(tmp_path/'raw')])
    def refused(*args):raise ValueError('explicit software admission refusal')
    monkeypatch.setattr(driver17,'admit',refused)
    def forbidden(*args):raise AssertionError('generation before admission')
    monkeypatch.setattr(driver17.core,'generate',forbidden)
    with pytest.raises(ValueError,match='admission refusal'):driver17.main()
    assert not (tmp_path/'raw').exists()


def test_supervisor_refuses_resource_change_before_output(tmp_path,monkeypatch):
    import sys,supervise17
    release=dict(owner='software-owner',parameters=custody17.PARAMETERS,execution_authorized=True,source_commit='software-only',package_versions={},numpy_runtime={},max_attempts=1,memory_bytes=4294967296)
    path=tmp_path/'software-release.json';write(path,release)
    monkeypatch.setattr(sys,'argv',['supervise17','--protocol',str(tmp_path/'p'),'--release',str(path),'--out',str(tmp_path/'run'),'--owner','software-owner'])
    monkeypatch.setattr(supervise17,'bindings',lambda commit:({},{}))
    monkeypatch.setattr(supervise17.runtime_numpy,'snapshot',lambda:{})
    monkeypatch.setenv('GIT_CONFIG_COUNT','1');monkeypatch.setenv('GIT_CONFIG_KEY_0','test.inherited');monkeypatch.setenv('GIT_CONFIG_VALUE_0','preserved')
    with pytest.raises(ValueError,match='two-GiB'):supervise17.main()
    import os
    assert os.environ['GIT_CONFIG_VALUE_0']=='preserved' and os.environ['GIT_CONFIG_KEY_1']=='core.packedGitWindowSize'
    assert os.environ['GIT_CONFIG_COUNT']=='3' and not(tmp_path/'run').exists()


def test_protocol_preview_is_schema_valid_and_distinguishes_actual_engines():
    p=prepare17.make_protocol('0'*40);t=custody17.tools()
    assert not t.schema_errors(p,'experiment.protocol/v1') and not t.lint_protocol(p,custody17.HERE)
    assert len(p['randomization']['seed_derivation']['seeds'])==16
    assert p['arms'][0]['parameters']['batch_solver_calls']==12 and p['arms'][0]['parameters']['online_engine_executions']==4
    assert p['freeze']['status']=='draft' and p['sample_size']['instances']==8

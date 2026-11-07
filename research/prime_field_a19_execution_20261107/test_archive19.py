"""Software-only p211 archive plumbing; generation/S3 receipts explicitly mocked.

Four archive IDs repeat the SAME tiny mathematical fixture. They test schema,
custody and census only and are never scientific replicates or real S3 claims.
All pool/helper/query/constructor/algebra work uses marked p211 rules, norm3,
pool2, two targets and horizon2; no native pool/field pilot runs here.
"""
from copy import deepcopy
from pathlib import Path
import json,sys,shutil
import pytest
from deps19 import core,solver,public_base,check_base,check_pairs,checker,native_case,public_verify,known_checks,commitment
from driver19 import timed
from check_query import Oracle
import collection19,check_collection19,pool19,branch19,cancel19,information19,check_algebra19
import custody19,prepare19,analyze19,driver19


def write(path,value):path.write_text(json.dumps(value,sort_keys=True)+'\n')
def receipt(value,**extra):return dict(verification=dict(checked=True,producer_output_sha256=commitment(value),**extra))


@pytest.fixture(scope='module')
def software_archive(tmp_path_factory):
    run=tmp_path_factory.mktemp('a19-explicit-software-io');raw=run/'raw';raw.mkdir()
    rules=dict(software_control=True,domain='a19-archive-software/v1',fields=[dict(p=211,base_size=3)],
        a=1,curves_per_field=1,maximum_curve_candidates=128,sources=8,prerequisite=2,excluded_curves=[],
        seeds=[0],maximum_scalar_candidates=256,maximum_target_candidates=256,maximum_base_candidates=256,max_pair_entries=8192,
        max_retained_rows=4096,targets=2,target_policies=['general'],target_queries_per_point=2,target_prefixes=[2],
        max_affine_labels=8192,pool_size=2,maximum_pool_candidates=256,maximum_target_cache_points=4,public_base_sizes=[16])
    original=core.generate(rules,lambda v:None)['cells'][0]
    # Explicit metadata fixtures, not a real gate or independent generation proof.
    rules=dict(rules,curves_per_field=4)
    generated=dict(cells=[dict(id='p211-i'+str(i))for i in range(4)],software_repeated_fixture=True)
    write(raw/'generated.json',generated);write(raw/'generation-check.json',receipt(generated,curves=4))
    child=dict(child_pid=12,child_process_group=12,supervisor_pid=11);write(run/'child.json',child)
    write(raw/'admission.json',dict(returncode=0,command=['bash','scripts/checkpoint.sh','gate'],last_push='software-mock'))
    write(run/'checkpoint-admitted-start.json',dict(returncode=0,command=['bash','scripts/checkpoint.sh','push'],native_curves_generated=0,admission_last_push='software-mock',**child))
    for ci in range(4):
        cid='p211-i'+str(ci);cell=deepcopy(original);cell['id']=cid;prepared={}
        for program in custody19.PROGRAMS:
            rr=dict(rules,program_id=program);prefix=cid+'.'+program+'.';events=[];helper=pool=None
            if program=='unknown16':
                pool=pool19.build(cell,rr,events.append);write(raw/(prefix+'base.json'),pool)
                write(raw/(prefix+'base-check.json'),timed(lambda:pool19.check(cell,rr,pool),pool))
            if program=='known16':
                helper=public_base.build(cell,rr,16,events.append);write(raw/(prefix+'base.json'),helper)
                write(raw/(prefix+'base-check.json'),timed(lambda:check_base.check(cell,rr,16,helper),helper))
            p=collection19.prepare(cell,rr,helper,events.append,pool=pool);prepared[program]=p
            write(raw/(prefix+'prelude.json'),p);write(raw/(prefix+'prelude-check.json'),timed(lambda:check_collection19.preparation(cell,rr,helper,p,pool),p))
            (raw/(prefix+'setup.events.jsonl')).write_text(''.join(json.dumps(v)+'\n'for v in events))
        shared=[];meter=core.ProgressMeter(cell['fixture'],shared.append,dict(kind='shared_public_targets'))
        targets=meter.stage('public_target_generation',lambda:core.old.targets(cell,rules,meter,shared.append))
        payload=dict(generation=targets,phases=meter.phases,counters=meter.counters())
        write(raw/(cid+'.targets.json'),payload);write(raw/(cid+'.targets-check.json'),timed(lambda:check_collection19.targets(cell,rules,targets),payload))
        (raw/(cid+'.shared.events.jsonl')).write_text(''.join(json.dumps(v)+'\n'for v in shared));reference=None
        for pi,program in enumerate(custody19.PROGRAMS):
            rr=dict(rules,program_id=program);prefix=cid+'.'+program+'.';events=[];p=prepared[program];f=p['cell']['fixture']
            c=collection19.collect(p,targets,rr,events.append);proof,oracle=check_collection19.collection(p,rr,c)
            proof['pair_construction']=check_pairs(f,p['geometry'],'batched',c['pairs'],[v for v in c['collection_phases']if v['phase']!='natural_target_queries'])
            write(raw/(prefix+'collection.json'),dict(cell=p['cell'],collection=c));write(raw/(prefix+'collection-check.json'),dict(verification=dict(proof,producer_output_sha256=commitment(c))))
            meter=core.ProgressMeter(f,events.append,dict(kind='owned_target_recipe'))
            recipe=meter.stage('target_recipes',lambda:core.recipes(cell,c,rr,meter,events.append));payload=dict(selection=recipe,phases=meter.phases,counters=meter.counters())
            checker.recipes(cell,rr,recipe);write(raw/(prefix+'recipe.json'),payload);write(raw/(prefix+'recipe-check.json'),receipt(payload))
            cache=branch19.OwnedCache(c,rr,events.append);b=branch19.build(p,c,rr,recipe['policies']['general'],cache,events.append)
            write(raw/(prefix+'construction.json'),b);write(raw/(prefix+'construction-check.json'),timed(lambda:branch19.check(p,c,rr,recipe['policies']['general'],cache,b),b))
            meter=core.ProgressMeter(f,events.append,dict(kind='native_matrix_assembly'))
            case=meter.stage('native_matrix_assembly',lambda:native_case.build(p,c,b,cache,2,'anchors',meter));assembly=dict(phases=meter.phases,counters=meter.counters())
            assert commitment(case)==commitment(native_case.expected(p,c,b,cache,2,'anchors'))
            write(raw/(prefix+'case.json'),case);write(raw/(prefix+'assembly.json'),assembly)
            write(raw/(prefix+'case-check.json'),receipt(case,prepared_sha256=commitment(p),collection_sha256=commitment(c),branch_sha256=commitment(b),cache_records_sha256=commitment(cache.records),assembly_sha256=commitment(assembly)))
            for name in ('aux_cancel_joint','sparse_joint'):
                label=program if name=='aux_cancel_joint'else'joint_on_'+program
                events.append(dict(kind='batch_solver_start',execution_arm=label))
                meter=solver.Meter(f);result=cancel19.solve(case,p,meter)if name=='aux_cancel_joint'else solver.solve(case,name,meter)
                public_verify(result,case,f,meter)
                proof=check_algebra19.cancelled_target(case,p,result,f)if name=='aux_cancel_joint'else known_checks.joint_case(case,result,f)
                write(raw/(prefix+name+'.json'),result);write(raw/(prefix+name+'-check.json'),dict(verification=dict(proof,producer_output_sha256=commitment(result),input_case_sha256=commitment(case),prepared_sha256=commitment(p))))
                events.append(dict(kind='batch_solver_complete',execution_arm=label,counters=result['counters']))
            if reference is None:
                projected=check_algebra19.projected(case,p);reference=[(v['vector'],v['rhs'])for v in projected['rows']if v['kind']=='collected_source']
                payload=dict(rows=reference,projection=p['projection'],source_case_sha256=commitment(case))
                write(raw/(cid+'.reference.json'),payload);write(raw/(cid+'.reference-check.json'),receipt(payload,source_case_sha256=commitment(case),prepared_sha256=commitment(p)))
                write(raw/(cid+'.reference-floor-cost.json'),dict(phases=[],counters={}))
            meter=core.ProgressMeter(f,events.append,dict(kind='information_diagnostic'));info=information19.measure(reference,case,p,meter)
            proof=check_algebra19.information(reference,case,p,info);write(raw/(prefix+'information.json'),info)
            write(raw/(prefix+'information-check.json'),dict(verification=dict(proof,input_case_sha256=commitment(case),prepared_sha256=commitment(p),reference_sha256=commitment(reference))))
            payload=dict(records=cache.records,engine_records=cache.engines.records[cache.engine_start:],engine_start=cache.engine_start,phases=cache.meter.phases,counters=cache.meter.counters(),owner=list(cache.owner))
            write(raw/(prefix+'cache.json'),payload);write(raw/(prefix+'cache-check.json'),timed(lambda:check_collection19.target_cache(p,c,cache,Oracle(f,p['geometry'])),payload))
            index=3*ci+pi;descriptor=dict(custody19.descriptors(rules))[index]
            write(raw/(prefix+'complete.json'),dict(complete=True,case_id=index,descriptor=descriptor))
            (raw/(prefix+'events.jsonl')).write_text(''.join(json.dumps(v)+'\n'for v in events))
        write(run/('checkpoint-'+cid+'.json'),dict(returncode=0,command=['bash','scripts/checkpoint.sh','push'],closed_curve=cid,completed_curves=ci+1,checked_cases=3*(ci+1),checked_batch_solver_calls=6*(ci+1),completed_online_engines=0,stdout='explicit software-mock s3://setec-astronomy-artifacts/checkpoints/fixture/'))
    execution=dict(returncode=0,timeout=False,exception=None,source_unchanged_after=True)
    return run,rules,execution


def test_actual_archive_census_costs_and_bound_corruption(software_archive,tmp_path):
    run,rules,execution=software_archive;data=analyze19.summarize(run,rules,execution)
    assert data['panel_complete']and len(data['cells'])==12 and len(data['cold_views'])==12
    assert (data['observed_batch_starts'],data['observed_completed_batch_calls'])==(24,24)
    copied=tmp_path/'copy';shutil.copytree(run,copied)
    p=copied/'raw/p211-i0.unknown16.case.json';value=json.loads(p.read_text());value['source'][0][1]=(value['source'][0][1]+1)%value['modulus'];write(p,value)
    with pytest.raises(ValueError):analyze19.summarize(copied,rules,execution)


@pytest.mark.parametrize('complete',[True,False])
def test_actual_export_shared_instances_and_all_unknowns(software_archive,tmp_path,monkeypatch,complete):
    source,rules,execution=software_archive;run=tmp_path/'run'
    if complete:shutil.copytree(source,run)
    else:run.mkdir();execution=dict(execution,returncode=1)
    protocol=prepare19.make_protocol('0'*40);path=tmp_path/'software-only.protocol.json';write(path,protocol)
    t=custody19.tools();t.freeze(path,'0'*40,True);protocol=json.loads(path.read_text());interpreter=protocol['arms'][0]['instrument']['binary_sha256']
    write(run/'execution.json',dict(execution,source_commit='0'*40,observed_git_head='0'*40,protocol_sha256=protocol['freeze']['protocol_sha256'],started_at='2026-11-07T00:00:00+00:00',finished_at='2026-11-07T00:00:01+00:00',owner='explicit-software-fixture'))
    write(run/'host.json',dict(cpu_model='explicit software fixture',logical_cpus=1,memory_bytes=2147483648,kernel='software',hypervisor=None,isolation_tier_max=None,git_dirty=True,executable_sha256=interpreter))
    inputs=tmp_path/'software-only.inputs.json';write(inputs,rules);monkeypatch.setattr(analyze19,'INPUTS',inputs)
    monkeypatch.setattr(sys,'argv',['analyze19','--run',str(run),'--protocol',str(path)]);analyze19.main()
    export=json.loads((run/'export.json').read_text());metrics=json.loads((run/'metrics.json').read_text())
    assert len(export['runs'])==24 and len({v['instance_id']for v in export['runs']})==4
    assert not t.schema_errors(export,'experiment.export/v1')and not t.lint_export(export,protocol,run,True)
    assert metrics['verified_systems']==(12 if complete else 0)


def test_truncated_paid_prefix_and_refused_driver(tmp_path,monkeypatch):
    raw=tmp_path/'raw';raw.mkdir()
    event=dict(kind='affine_phase',context=dict(kind='unknown_pool_construction'),phase=dict(counters=dict(paid_prefix=7)))
    (raw/'p211-i0.unknown16.setup.events.jsonl').write_text(json.dumps(event)+'\n{truncated-software-tail')
    rules=dict(software_control=True,fields=[dict(p=211)],curves_per_field=4)
    data=analyze19.summarize(tmp_path,rules,dict(returncode=1,timeout=False))
    assert not data['panel_complete']and data['physical_counters']['p211-i0.unknown16.unknown_pool_construction']['paid_prefix']==7
    assert any(v.get('paid_prefix_retained')for v in data['errors'])
    monkeypatch.setattr(sys,'argv',['driver19','--inputs',str(tmp_path/'i'),'--protocol',str(tmp_path/'p'),'--release',str(tmp_path/'r'),'--out',str(tmp_path/'new-raw')])
    def refuse(*args):raise ValueError('marked admission refusal')
    def forbidden(*args):raise AssertionError('generation before admission')
    monkeypatch.setattr(driver19,'admit',refuse);monkeypatch.setattr(driver19.core,'generate',forbidden)
    with pytest.raises(ValueError,match='admission refusal'):driver19.main()
    assert not(tmp_path/'new-raw').exists()

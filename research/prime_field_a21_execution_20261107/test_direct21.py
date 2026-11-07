"""Marked p<=211 and explicit synthetic controls; never a native pilot."""
from copy import deepcopy
import json,sys
from pathlib import Path
import pytest
from deps21 import solver,check_source,public_verify,cancel19,check_algebra19,commitment
from test_formal20 import tiny
import direct21,check21,custody21,prepare21,analyze21


def fixture(tiny,known_count=1):
    original,_=tiny;f=deepcopy(original['fixture']);r=f['r'];p=f['p'];P=tuple(f['P']);labels=[1,3,7]
    points=[check_source.old.multiply(p,0,f['a'],x,P)for x in labels]
    definitions=[];aux_labels=[]
    for i,pair in enumerate(([(0,1),(1,1)],[(0,-1),(2,1)])):
        label=sum(labels[j]*s for j,s in pair)%r;point=check_source.old.multiply(p,0,f['a'],label,P)
        canonical=min(point,(point[0],-point[1]%p));orientation=1 if canonical==point else-1
        components=[[j,s*orientation]for j,s in pair];vector=[0]*3
        for j,s in components:vector[j]=s%r
        definitions.append(dict(auxiliary_index=i,components=components,old_coefficients=vector,point=list(canonical)))
        points.append(canonical);aux_labels.append(label*orientation%r)
    f['factor_base']=[dict(point=list(v))for v in points]
    known=[[j,labels[j]]for j in range(known_count)]
    old_basis=[[j,-1 if j==2 else 1]for j in reversed(range(known_count,3))]
    mapping=[None]*3
    for j,label in known:mapping[j]=['known',label]
    for i,(j,s)in enumerate(old_basis):mapping[j]=['unknown',i,s]
    prep=dict(cell=dict(fixture=f),norm_size=3,known=known,basis=old_basis+[[3,1],[4,1]],projection=dict(U=len(old_basis),native_to_projected=mapping),formal_definitions=definitions,auxiliary_role='formalpair16')
    source=[];origins=[]
    for j,label in known:source.append(([int(k==j)for k in range(5)],label));origins.append(dict(kind='supplied_native_unit'))
    for i,d in enumerate(definitions):source.append(([-v%r for v in d['old_coefficients']]+[int(k==i)for k in range(2)],0));origins.append(dict(kind='formal_definition'))
    # Collected old numeric units are explicit software fixture equations,
    # not substituted as prerequisite knowledge by any producer.
    for j in (0,1):source.append(([int(k==j)for k in range(5)],labels[j]));origins.append(dict(kind='collected_source'))
    targets=[];target=[]
    for t in range(8):
        vector=[0]*5
        if t%2==0:vector[3]=2;label=2*aux_labels[0]%r
        else:vector[3]=1;vector[4]=r-1;label=(aux_labels[0]-aux_labels[1])%r
        outside=[0]*8;outside[t]=r-1
        target.append(dict(vector=vector,outside=outside,rhs=0))
        q=check_source.old.multiply(p,0,f['a'],label,P);targets.append(dict(index=t,point=list(q)))
    case=dict(width=5,target_count=8,modulus=r,source=source,source_origins=origins,target=target,targets=targets)
    return case,prep


@pytest.mark.parametrize('known_count',[0,1,2,3])
def test_signed_projection_multiplicity_native_lift_and_nonrecoveries(tiny,known_count):
    case,prep=fixture(tiny,known_count);f=prep['cell']['fixture']
    meter=solver.Meter(f);direct=direct21.solve(case,prep,meter);public_verify(direct,case,f,meter)
    assert check21.verify(case,prep,direct)['checked']
    aux=cancel19.solve(case,prep,solver.Meter(f));assert check_algebra19.cancelled_target(case,prep,aux,f)['checked']
    joint=solver.solve(case,'sparse_joint',solver.Meter(f))
    assert [[(v['identifiable'],v['scalar'])for v in a['recoveries']]for a in (direct,aux,joint)].count([(v['identifiable'],v['scalar'])for v in direct['recoveries']])==3
    if known_count<3:assert [v['identifiable']for v in direct['recoveries']]==[t%2==0 for t in range(8)]
    assert direct['counters']['formal_definition_rows_elided']==2
    assert direct['counters']['formal_signed_component_accumulations']>0
    assert direct['counters']['original_row_certificates_verified']==sum(v['identifiable']for v in direct['recoveries'])
    for change in ('weight','projection','counter'):
        bad=deepcopy(direct)
        if change=='weight':bad['recoveries'][0]['original_row_weights'][known_count]=(bad['recoveries'][0]['original_row_weights'][known_count]+1)%case['modulus']
        elif change=='projection':bad['projection']['rows'][0][0]=(bad['projection']['rows'][0][0]+1)%case['modulus']
        else:bad['counters']['Fr.field_mul']=bad['counters'].get('Fr.field_mul',0)+1
        with pytest.raises(ValueError):check21.verify(case,prep,bad)


@pytest.mark.parametrize('change',['coefficient','definition','map','numeric_auxiliary','component'])
def test_refuse_changed_symbolic_boundary(tiny,change):
    case,prep=fixture(tiny);case=deepcopy(case);prep=deepcopy(prep)
    if change=='coefficient':prep['formal_definitions'][0]['old_coefficients'][0]=0
    elif change=='definition':case['source'][1][0][0]=(case['source'][1][0][0]+1)%case['modulus']
    elif change=='map':prep['projection']['native_to_projected'][2][-1]=1
    elif change=='numeric_auxiliary':prep['known'].append([3,4])
    else:prep['formal_definitions'][0]['components'][0][1]=0
    with pytest.raises(ValueError):direct21.solve(case,prep,solver.Meter(prep['cell']['fixture']))


def test_native_refuses_before_row_work(tiny):
    case,prep=fixture(tiny);prep['cell']['fixture']['p']=262139
    meter=solver.Meter(prep['cell']['fixture'])
    with pytest.raises(ValueError,match='admitted driver'):direct21.solve(case,prep,meter)
    assert not meter.phases


def test_prospective_grid_and_original_budget():
    p=prepare21.make_protocol('0'*40);t=custody21.tools()
    assert not t.schema_errors(p,'experiment.protocol/v1')and not t.lint_protocol(p,custody21.HERE)
    assert len(list(t.seeds_table(p)))==12 and p['sample_size']['instances']==4
    assert len(custody21.BUDGET_INPUTS)==24
    rules=custody21.expected_rules();assert len(rules['cases'])==4 and rules['new_curves']==rules['new_native_targets']==0


def test_explicit_repeated_tiny_archive_and_all_unknown(tiny,tmp_path,monkeypatch):
    # Four IDs repeat this SAME tiny fixture. Admission/checkpoints are mocked
    # metadata here; no native invocation, independent replicate or S3 claim.
    case,prep=fixture(tiny);raw=tmp_path/'raw';raw.mkdir();rules=dict(cases=[])
    def write(path,value):path.write_text(json.dumps(value)+'\n')
    pc=tmp_path/'public-case.json';pp=tmp_path/'public-prep.json';write(pc,case);write(pp,prep)
    producer=dict(case=dict(path=str(pc),sha256=custody21.digest(pc)),prepared=dict(path=str(pp),sha256=custody21.digest(pp)))
    child=dict(child_pid=12,child_process_group=12,supervisor_pid=11);write(tmp_path/'child.json',child)
    write(raw/'admission.json',dict(returncode=0,command=['bash','scripts/checkpoint.sh','gate'],last_push='software-mock'))
    write(tmp_path/'checkpoint-admitted-start.json',dict(returncode=0,command=['bash','scripts/checkpoint.sh','push'],admission_last_push='software-mock',native_curves_generated=0,**child))
    for i in range(4):
        cid='explicit-software-'+str(i);descriptor=dict(cell_id=cid,producer=producer);rules['cases'].append(descriptor);events=[]
        for method in custody21.ARMS:
            meter=solver.Meter(prep['cell']['fixture'])
            value=direct21.solve(case,prep,meter)if method=='direct_formal'else cancel19.solve(case,prep,meter)if method=='aux_cancel_joint'else solver.solve(case,method,meter)
            public_verify(value,case,prep['cell']['fixture'],meter)
            proof=check21.verify(case,prep,value)if method=='direct_formal'else check_algebra19.cancelled_target(case,prep,value)if method=='aux_cancel_joint'else __import__('deps21').known_checks.joint_case(case,value,prep['cell']['fixture'])
            proof.update(input_case_sha256=commitment(case),prepared_sha256=commitment(prep),producer_output_sha256=commitment(value))
            write(raw/(cid+'.'+method+'.json'),value);write(raw/(cid+'.'+method+'-check.json'),dict(verification=proof))
            events.extend([dict(kind='batch_solver_start',execution_arm=method,case_id=i),dict(kind='batch_solver_complete',execution_arm=method,case_id=i,counters=value['counters'])])
        (raw/(cid+'.events.jsonl')).write_text(''.join(json.dumps(v)+'\n'for v in events))
        write(raw/(cid+'.complete.json'),dict(complete=True,descriptor=descriptor,all_methods_agree=True,historical_outcomes_agree=True))
        write(tmp_path/('checkpoint-'+cid+'.json'),dict(returncode=0,closed_curve=cid,command=['bash','scripts/checkpoint.sh','push'],completed_curves=i+1,checked_cases=i+1,checked_batch_solver_calls=3*(i+1),completed_online_engines=0,stdout='s3://setec-astronomy-artifacts/checkpoints/software-mock/'))
    execution=dict(returncode=0,timeout=False,exception=None,source_unchanged_after=True)
    data=analyze21.summarize(tmp_path,rules,execution);assert data['panel_complete']and len(data['rows'])==12
    protocol=prepare21.make_protocol('0'*40);path=tmp_path/'software-only.protocol.json';write(path,protocol)
    t=custody21.tools();t.freeze(path,'0'*40,True);protocol=json.loads(path.read_text());interpreter=protocol['arms'][0]['instrument']['binary_sha256']
    inputs=tmp_path/'software-only.inputs.json';write(inputs,rules)
    unknown=tmp_path/'all-unknown';(unknown/'raw').mkdir(parents=True)
    for run,complete in ((tmp_path,True),(unknown,False)):
        write(run/'execution.json',dict(execution,returncode=0 if complete else 1,source_commit='0'*40,observed_git_head='0'*40,protocol_sha256=protocol['freeze']['protocol_sha256'],started_at='2026-11-07T00:00:00+00:00',finished_at='2026-11-07T00:00:01+00:00',owner='explicit-software-fixture'))
        write(run/'host.json',dict(cpu_model='explicit software fixture',logical_cpus=1,memory_bytes=2147483648,kernel='software',hypervisor=None,isolation_tier_max=None,git_dirty=True,executable_sha256=interpreter))
        monkeypatch.setattr(sys,'argv',['analyze21','--run',str(run),'--protocol',str(path),'--inputs',str(inputs)])
        analyze21.main();export=json.loads((run/'export.json').read_text());metrics=json.loads((run/'metrics.json').read_text())
        assert len(export['runs'])==12 and len({v['instance_id']for v in export['runs']})==4
        assert not t.schema_errors(export,'experiment.export/v1')and not t.lint_export(export,protocol,run,True)
        assert metrics['verified_systems']==(12 if complete else 0)
    # A coordinated local counter/phase/event edit still differs from its
    # preserved independent producer-output binding.
    path=raw/'explicit-software-0.direct_formal.json';bad=json.loads(path.read_text());bad['counters']['Fr.field_mul']+=1;write(path,bad)
    with pytest.raises(ValueError):analyze21.summarize(tmp_path,rules,execution)
    data=analyze21.summarize(unknown,rules,dict(returncode=1));assert not data['panel_complete']and len(data['rows'])==12 and not any(v['verified']for v in data['rows'])


def test_truncated_paid_prefix_and_admission_refusal(tmp_path,monkeypatch):
    import driver21
    raw=tmp_path/'raw';raw.mkdir()
    event=dict(kind='batch_solver_failed',execution_arm='direct_formal',case_id=0,phases=[dict(counters=dict(paid_prefix=7))])
    (raw/'software.events.jsonl').write_text(json.dumps(event)+'\n{explicit truncated software tail')
    rules=dict(cases=[dict(cell_id='software')]);value=analyze21.summarize(tmp_path,rules,dict(returncode=1))
    assert not value['panel_complete']and value['physical_counters']['paid_prefix']==7 and value['errors'][0]['paid_prefix_retained']
    monkeypatch.setattr(sys,'argv',['driver21','--inputs',str(tmp_path/'i'),'--protocol',str(tmp_path/'p'),'--release',str(tmp_path/'r'),'--out',str(tmp_path/'new-raw')])
    def refuse(*args):raise ValueError('marked admission refusal')
    monkeypatch.setattr(driver21,'admit',refuse)
    with pytest.raises(ValueError,match='admission refusal'):driver21.main()
    assert not(tmp_path/'new-raw').exists()

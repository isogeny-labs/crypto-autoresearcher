"""Describe actual calls and costs; preserve failed and unexecuted prefixes."""
import argparse,json,os
from collections import Counter
from pathlib import Path
from deps21 import commitment,known_checks
from custody21 import ROOT,HERE,ARMS,load,write_once,digest,tools
from streams21 import lines

COLS=['case_id','cell_id','method','verified','identified_targets','identified_mask','system_columns','system_rank',
    'fp_add','fp_sub','fp_mul','fp_inv','fr_add','fr_sub','fr_mul','fr_inv']


def summarize(run,rules,execution):
    raw=run/'raw';rows=[];errors=[];started=completed=failed=0;physical=Counter();phases=[];loads=[];checkpoints=[]
    def optional(path):return load(path)if path.exists()else None
    admission=optional(raw/'admission.json');start=optional(run/'checkpoint-admitted-start.json');child=optional(run/'child.json')
    startup=bool(admission and start and child and admission.get('returncode')==0 and start.get('returncode')==0 and
        admission.get('command')==['bash','scripts/checkpoint.sh','gate']and start.get('command')==['bash','scripts/checkpoint.sh','push']and
        start.get('admission_last_push')==admission.get('last_push')and all(start.get(k)==child.get(k)for k in ('child_pid','child_process_group','supervisor_pid'))and start.get('native_curves_generated')==0)
    for index,d in enumerate(rules['cases']):
        cid=d['cell_id'];events=[]
        try:
            for ev in lines(raw/(cid+'.events.jsonl')):events.append(ev)
        except Exception as error:errors.append(dict(path=cid+'.events.jsonl',error_type=type(error).__name__,error=str(error),paid_prefix_retained=True))
        starts=Counter();done={}
        for ev in events:
            kind=ev.get('kind')
            if kind=='batch_solver_start':started+=1;starts[ev['execution_arm']]+=1
            elif kind=='batch_solver_complete':
                completed+=1;done[ev['execution_arm']]=ev;physical.update(ev['counters'])
            elif kind=='batch_solver_failed':
                failed+=1
                for phase in ev['phases']:physical.update(phase['counters'])
            elif kind=='producer_input_load':loads.append(dict(cell_id=cid,**ev))
        complete=optional(raw/(cid+'.complete.json'));cp=optional(run/('checkpoint-'+cid+'.json'))
        checkpoint=bool(cp and cp.get('returncode')==0 and cp.get('closed_curve')==cid and cp.get('command')==['bash','scripts/checkpoint.sh','push']and
            (cp.get('completed_curves'),cp.get('checked_cases'),cp.get('checked_batch_solver_calls'),cp.get('completed_online_engines'))==(index+1,index+1,3*(index+1),0)and
            's3://setec-astronomy-artifacts/checkpoints/'in cp.get('stdout',''))
        checkpoints.append(dict(cell_id=cid,valid=checkpoint))
        outcomes=[]
        for method in ARMS:
            result=optional(raw/(cid+'.'+method+'.json'));receipt=optional(raw/(cid+'.'+method+'-check.json'))
            valid=bool(startup and checkpoint and complete and complete.get('complete')is True and complete.get('descriptor')==d and
                complete.get('all_methods_agree')is True and complete.get('historical_outcomes_agree')is True and result and receipt and method in done)
            row=dict(case_id=index,cell_id=cid,method=method,verified=valid)
            if valid:
                proof=receipt['verification'];case=load(ROOT/d['producer']['case']['path']);prep=load(ROOT/d['producer']['prepared']['path'])
                if (proof.get('checked')is not True or proof['input_case_sha256']!=commitment(case)or proof['prepared_sha256']!=commitment(prep)or
                    proof['producer_output_sha256']!=commitment(result)or starts[method]!=1 or done[method]['counters']!=result['counters']):raise ValueError('producer/checker/event custody mismatch')
                known_checks.phase_counts(result)
                mask=sum(1<<i for i,v in enumerate(result['recoveries'])if v['identifiable'])
                if len(result['recoveries'])!=8 or proof['identified']!=mask.bit_count():raise ValueError('target census mismatch')
                row.update(identified_targets=mask.bit_count(),identified_mask=mask,system_columns=result['system']['columns'],system_rank=result['system']['rank'])
                for field in ('Fp','Fr'):
                    for op in ('add','sub','mul','inv'):row[field.lower()+'_'+op]=result['counters'].get(field+'.field_'+op,0)
                if any(type(v)is not int or v<0 for v in result['counters'].values()):raise ValueError('counter encoding')
                outcomes.append([(v['identifiable'],v['scalar'])for v in result['recoveries']]);phases.extend(dict(cell_id=cid,method=method,**p)for p in result['phases'])
            rows.append(row)
        if outcomes and any(v!=outcomes[0]for v in outcomes):raise ValueError('actual method outcome mismatch')
    complete=bool(execution.get('returncode')==0 and execution.get('timeout')is False and execution.get('exception')is None and
        execution.get('source_unchanged_after')is True and len(rows)==12 and all(v['verified']for v in rows)and (started,completed,failed)==(12,12,0)and not errors)
    return dict(schema='prime-field-a21-analysis/v1',panel_complete=complete,rows=rows,phases=phases,physical_counters=dict(physical),
        input_loads=loads,observed_batch_starts=started,observed_completed_batch_calls=completed,observed_failed_batch_calls=failed,
        closed_checkpoints=checkpoints,errors=errors,new_curves=0,new_targets=0,inference='All four conditioned A20 formal cases. Three actual cold algebra methods; no fresh holdout, population, clock or weighted cost inference.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('run','inputs','protocol'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();rules=load(a.inputs);protocol=load(a.protocol);execution=load(a.run/'execution.json');host=load(a.run/'host.json');data=summarize(a.run,rules,execution)
    metrics=dict(schema='prime-field-a21-metrics/v1',physical_attempts=1,planned_systems=12,planned_batch_calls=12,
        verified_systems=sum(v['verified']for v in data['rows']),unknown_systems=sum(not v['verified']for v in data['rows']),panel_complete=data['panel_complete'],
        source_commit=execution['source_commit'],protocol_sha256=execution['protocol_sha256'],columns=COLS,rows=[[v.get(k)for k in COLS]for v in data['rows']],
        observed_batch_starts=data['observed_batch_starts'],observed_completed_batch_calls=data['observed_completed_batch_calls'],observed_failed_batch_calls=data['observed_failed_batch_calls'],physical_counters=data['physical_counters'])
    write_once(a.run/'metrics.json',metrics);data['metrics_sha256']=digest(a.run/'metrics.json');write_once(a.run/'analysis.json',data)
    t=tools();export=t.export_skeleton(protocol,str(a.protocol.resolve()),'local','A21-'+a.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor')
    export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(a.run/'host.json'),summary={k:host[k]for k in export['host']['summary']})
    export['runs']=[]
    ids={v['id']for v in protocol['metrics']['primary']+protocol['metrics']['secondary']}
    for row in data['rows']:
        counted={k:v for k,v in row.items()if k in ids and type(v)is int}
        export['runs'].append(t.run_row(run_id='A21-'+str(len(export['runs'])),arm=row['method'],instance_id=str(row['case_id']),seed=0,replicate=0,warmup=False,
            status='succeeded'if row['verified']else'timeout'if execution['timeout']else'interrupted',measurements=dict(counted=counted,counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['sharedhost']),verification=dict(status='verified'if row['verified']else'not_run',verifier='producer independent dense/native/public checker; scientific standing unverified'),
            started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['backend_record']=dict(physical_attempts=1,planned_systems=12,planned_batch_calls=12,new_curves=0,new_targets=0,verified_systems=metrics['verified_systems'],partial_work_unknown=not data['panel_complete'])
    export['files']=[t.file_entry(a.run,str(v.relative_to(a.run)),'raw')for v in sorted(a.run.rglob('*'))if v.is_file()and v.name!='.gitignore']
    export['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze21.py',a.run.resolve()),sha256=digest(HERE/'analyze21.py'),bytes=(HERE/'analyze21.py').stat().st_size)
    export['analysis']['outputs']=[t.file_entry(a.run,k,'analysis')for k in ('metrics.json','analysis.json')];export['flow']=t.compute_flow(export['runs'])
    errors=t.schema_errors(export,'experiment.export/v1')or t.lint_export(export,protocol,a.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(a.run/'export.json',export,compact=True)
    print(json.dumps(dict(panel_complete=data['panel_complete'],verified_systems=metrics['verified_systems'],batch_calls=data['observed_completed_batch_calls'])))


if __name__=='__main__':main()

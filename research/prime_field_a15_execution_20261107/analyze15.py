"""Bind retained component outputs/checks and export every attempted/missing row."""
import argparse
from collections import Counter
from pathlib import Path
import gzip,json,os
from custody15 import HERE,ROOT,INPUTS,load,digest,write_once,tools,PARAMETERS
from check15 import commitment
from deps15 import core

CURVES=('p262139-i0','p262139-i1','p524287-i0','p524287-i1')


def checkpoint_status(receipts):
    if not set(receipts)<=set(CURVES):raise ValueError('unexpected checkpoint curve')
    for i,cid in enumerate(CURVES):
        if cid not in receipts:continue
        value=receipts[cid]
        if value['closed_curve']!=cid or value['completed_tables']!=4*(i+1) or value['command']!=['bash','scripts/checkpoint.sh','push']:
            raise ValueError('closed-curve checkpoint identity/ordinal mismatch')
    return len(receipts)==4 and all(value['returncode']==0 for value in receipts.values())


def lines(path):
    path=Path(path)
    if not path.exists():path=Path(str(path)+'.gz')
    if not path.exists():return
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as stream:
        for line in stream:
            if line.strip():yield json.loads(line)


def summarize(raw,rules):
    rows=[];physical=Counter();errors=[]
    for item in rules['snapshots']:
        directory=raw/item['id'];snapshot=load(ROOT/item['path'])
        checks={(v['kind'],v.get('method'),v.get('query_index')):v for v in lines(directory/'checks.jsonl')}
        state={m:dict(table=item['id'],method=m,verified=False,build=None,queries=0,verified_queries=0,rows=0,
                      observed_phase_counters=Counter(),query_counters=Counter(),method_complete=False) for m in ('scalar','batched')}
        for event in lines(directory/'events.jsonl'):
            if event.get('kind')=='affine_phase':
                context=event['context'];phase=event['phase'];counts=phase['counters']
                if any(type(v)is not int or v<0 for v in counts.values()):raise ValueError('phase counter encoding')
                physical.update(counts);state[context['method']]['observed_phase_counters'].update(counts)
        for output in lines(directory/'outputs.jsonl'):
            method=output['method'];s=state[method];kind=output['kind']
            if kind=='built':
                if s['build']is not None:raise ValueError('duplicate construction output')
                s['build']=output
                check=checks.get(('pair_check',method,None))
                if check:
                    value=check['verification']
                    if check.get('producer_output_sha256')!=commitment(output):raise ValueError('construction cost/output checker binding')
                    if not value['checked'] or value['pairs_sha256']!=output['pairs_sha256'] or output['pairs_sha256']!=snapshot['prior_ordered_pairs_sha256']:
                        raise ValueError('construction checker binding')
                    phase_counts=Counter()
                    for phase in output['phases']:phase_counts.update(phase['counters'])
                    if phase_counts!=Counter(output['counters']) or phase_counts!=Counter(value['construction_counters']):
                        raise ValueError('construction phase/independent counter disagreement')
                    if any(output['counters'].get(k,0)!=v for k,v in value['construction_arithmetic'].items()):
                        raise ValueError('construction independent Fp schedule disagrees')
                    s['pair_verified']=True;s['pair_stage_counters']=value['pair_stage_counters']
            elif kind=='query':
                qi=output['query_index']
                if qi!=s['queries'] or qi>=len(snapshot['queries']):raise ValueError('query output order')
                s['queries']+=1;s['rows']+=len(output['record']['rows'])
                s['query_counters'].update(output['phase']['counters'])
                check=checks.get(('query_check',method,qi))
                if check:
                    expected=snapshot['queries'][qi]
                    value=check['verification']
                    if check.get('producer_output_sha256')!=commitment(output):raise ValueError('query cost/output checker binding')
                    if not value['checked'] or value['record_sha256']!=commitment(output['record']) or value['record_sha256']!=expected['expected_record_sha256']:
                        raise ValueError('query checker/retained commitment binding')
                    if output['engine_record']['points_sha256']!=expected['expected_signed_points_sha256']:
                        raise ValueError('signed query commitment')
                    if any(output['phase']['counters'].get(k,0)!=v for k,v in value['query_arithmetic'].items()):
                        raise ValueError('query independent Fp schedule disagrees')
                    if any(Counter(output['engine_record']['engines'][engine]['counters'])!=Counter(counts)
                            for engine,counts in value['engine_count_check']['engine_totals'].items()):
                        raise ValueError('query independently checked engine counters disagree')
                    s['verified_queries']+=1
            elif kind=='method_complete':
                if output['queries']!=s['queries'] or output['query_counters']!=dict(s['query_counters']) or output['rows']!=s['rows']:
                    raise ValueError('method summary/counter mismatch')
                s['method_complete']=True
            else:raise ValueError('unknown producer output kind')
        for method,s in state.items():
            s['verified']=bool(s['method_complete'] and s.get('pair_verified') and s['verified_queries']==len(snapshot['queries']))
            if s['verified']:
                if Counter(s['build']['counters'])+s['query_counters']!=s['observed_phase_counters']:
                    raise ValueError('complete phase conservation')
            else:errors.append(dict(table=item['id'],method=method,error='incomplete or unchecked component; retained work remains unverified'))
            s['observed_phase_counters']=dict(s['observed_phase_counters']);s['query_counters']=dict(s['query_counters'])
            rows.append(s)
    return rows,dict(physical),errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();rules=load(INPUTS);protocol=load(args.protocol)
    execution,host=load(args.run/'execution.json'),load(args.run/'host.json')
    rows,physical,errors=summarize(args.run/'raw',rules)
    checkpoint_receipts={cid:load(args.run/('checkpoint-'+cid+'.json')) for cid in CURVES if (args.run/('checkpoint-'+cid+'.json')).exists()}
    checkpoints_complete=checkpoint_status(checkpoint_receipts)
    checkpoints=list(checkpoint_receipts.values())
    complete=all(row['verified'] for row in rows) and checkpoints_complete and execution['returncode']==0 and execution['source_unchanged_after']
    metrics=dict(schema='prime-field-a15-metrics/v1',panel_complete=complete,physical_attempts=1,
        conditioned_input_reuse=True,new_target_solver_calls=0,independent_new_target_draws=0,
        verified_builds=sum(row['verified'] for row in rows),verified_query_calls=sum(row['verified_queries'] for row in rows),
        physical_counters=physical,rows=rows,errors=errors,partial_work_unknown=not complete,
        source_commit=execution['source_commit'],checkpoints=checkpoints,parameters=PARAMETERS)
    write_once(args.run/'metrics.json',metrics,compact=True)
    write_once(args.run/'analysis.json',dict(schema='prime-field-a15-analysis/v1',metrics_sha256=digest(args.run/'metrics.json'),
        producer_unverified=True,resources=execution,
        interpretation='Exact finite pair/query/native-row equivalence and separately counted cold construction stages. Retained A14 inputs are conditioned reuse, no new target recovery or solver calls. Fp inversion internals, Python/NumPy/IO/checker overhead unexpanded; explicit allocation traffic is not peak memory or calibrated complete cost.',
        metrics=metrics),compact=True)
    t=tools();export=t.export_skeleton(protocol,str(args.protocol.resolve()),'local','A15-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor')
    export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']})
    export['runs']=[]
    for i,row in enumerate(rows):
        counted={}
        if row['build']:
            counts=row['build']['counters']
            counted.update({'build_fp_'+op:counts.get('Fp.field_'+op,0) for op in ('add','sub','mul','inv')})
            counted.update(ordered_pairs=row['build']['ordered_pairs'],queries=row['queries'],verified_queries=row['verified_queries'],
                pair_array_bytes=counts.get('pair_array_allocated_bytes',0),new_target_solver_calls=0)
        export['runs'].append(t.run_row(run_id='A15-'+str(i),arm=row['method'],instance_id=str(i//2),seed=0,replicate=0,warmup=False,
            status='succeeded' if row['verified'] else 'timeout' if execution['timeout'] else 'interrupted',
            measurements=dict(counted=counted,counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['sharedhost']),
            verification=dict(status='verified' if row['verified'] else 'not_run',verifier='producer plain group/full triple/miss/counter checks, no signed standing'),
            started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['backend_record']=dict(physical_attempts=1,planned_builds=32,planned_query_calls=17920,verified_builds=metrics['verified_builds'],
        verified_query_calls=metrics['verified_query_calls'],new_target_solver_calls=0,partial_work_unknown=not complete,physical_counters=physical)
    export['files']=[t.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file() and p.name!='.gitignore']
    export['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze15.py',args.run.resolve()),sha256=digest(HERE/'analyze15.py'),bytes=(HERE/'analyze15.py').stat().st_size)
    export['analysis']['outputs']=[t.file_entry(args.run,name,'analysis') for name in ('metrics.json','analysis.json')]
    export['flow']=t.compute_flow(export['runs'])
    findings=t.schema_errors(export,'experiment.export/v1') or t.lint_export(export,protocol,args.run,True)
    if findings:raise ValueError(json.dumps(findings))
    write_once(args.run/'export.json',export,compact=True)
    print(json.dumps({k:metrics[k] for k in ('panel_complete','verified_builds','verified_query_calls','new_target_solver_calls')}))


if __name__=='__main__':main()

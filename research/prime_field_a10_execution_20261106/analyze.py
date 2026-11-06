"""Mechanical observations from closed raw records; never reruns native math."""
import argparse,gzip,json,os
from pathlib import Path
from collections import Counter
from common import HERE,ROOT,INPUTS,ARMS,load,digest,write_once,tools

def optional(path):
    path=Path(path);found=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(found)>1:raise ValueError('ambiguousencoding')
    return load(found[0]) if found else None

def events(path):
    path=Path(path)
    if not path.is_file():path=Path(str(path)+'.gz')
    if not path.is_file():return []
    raw=gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()
    return [json.loads(v) for v in raw.splitlines()]

def add(phases):return dict(sum((Counter(v['counters']) for v in phases),Counter()))
def normalized(case):
    r=case['modulus'];keys=set()
    for v,b in case['source']:
        row=v+[b];pivot=next((x for x in row if x),None)
        if pivot is not None:
            inverse=pow(pivot,-1,r);keys.add(tuple(x*inverse%r for x in row))
    return len(keys)

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);a=p.parse_args()
    protocol=load(a.protocol);rules=load(INPUTS);execution=load(a.run/'execution.json');host=load(a.run/'host.json');cells=[];construction=[];collection_totals=Counter();shared=[];observed={arm:Counter() for arm in ARMS};failed={arm:Counter() for arm in ARMS};collection_checks=[];caseindex=0;unknown_work=False;producer_calls=0
    schedules=[kind+str(seed) for seed in rules['seeds'] for kind in ('ap','hash')]
    for field in rules['fields']:
        for index in range(rules['curves_per_field']):
            cell_id='p'+str(field['p'])+'-i'+str(index);raw=optional(a.run/'raw'/(cell_id+'.json'));co=optional(a.run/'raw'/(cell_id+'.collection.json'));checked=optional(a.run/'raw'/(cell_id+'.collection-check.json'));journal=events(a.run/'raw'/(cell_id+'.events.jsonl'))
            records={} if raw is None else {(v['descriptor']['arm'],v['descriptor']['prefix'],v['descriptor']['scope']):v for v in raw['records']}
            if checked:collection_checks.append(checked)
            for ev in journal:
                if ev['kind']=='solver_complete':observed[ev['result']['arm']].update(ev['result']['counters']);producer_calls+=1
                elif ev['kind']=='solver_failed':failed[ev['arm']].update(add(ev['phases']));unknown_work=True
                elif ev['kind']=='case_input':shared.append(dict(descriptor=ev['descriptor'],phases=ev['shared_phases']))
                elif ev['kind']=='failure':unknown_work=True
            if co:
                col=co['collection'];collection_totals.update(col['collection_counters'])
                if add(col['collection_phases'])!=col['collection_counters']:raise ValueError('collection phase conservation')
                common=[v for v in col['collection_phases'] if not any(v['phase'].startswith(s+'_') for s in schedules)]
                for schedule,rec in col['arms'].items():
                    pre=[v for v in col['collection_phases'] if v['phase']in (schedule+'_label_cache_setup',schedule+'_constructor_selection')]
                    for budget in rec['budgets']:
                        prefix=budget['prefix'];phase_ids={v for b in rec['budgets'] if b['prefix']<=prefix for v in b['phase_ids']}
                        phases=[v for v in col['collection_phases'] if v['phase']in phase_ids];cc=add([v for v in phases if v['phase'].endswith('_source_construction')])
                        public={m['target_index'] for q in rec['knowledge'] if q['prefix']<=prefix for m in q.get('direct_targets',[])}
                        construction.append(dict(cell_id=cell_id,schedule=schedule,prefix=prefix,selection=rec['selection'],constructor_counters=cc,shared_counters=add(common),arm_prepaid_counters=add(pre),prefix_counters=add(phases),known_direct_targets=sorted(public),**{k:v for k,v in budget.items() if k not in ('prefix','phase_ids')}))
            elif journal:
                # Every finished/failed stage is emitted immediately; do not also sum budget views.
                for ev in journal:
                    if ev['kind']=='collection_phase':collection_totals.update(ev['phase']['counters'])
                unknown_work=True
            for schedule in schedules:
                for prefix in rules['prefixes']:
                    for scope in rules['scopes']:
                        rec=records.get((schedule,prefix,scope));verified=rec is not None and rec['verification']['checked']is True and checked is not None and checked['verification']['checked']is True
                        if verified:
                            matched=[v for v in journal if v.get('descriptor')==rec['descriptor']]
                            if [v['kind'] for v in matched]!=['case_started','case_input','solver_complete','solver_complete','case_checked']:raise ValueError('casejournalcoverage')
                            if [v['result'] for v in matched if v['kind']=='solver_complete']!=rec['results']:raise ValueError('journalproducerbinding')
                            if next(v['case'] for v in matched if v['kind']=='case_input')!=rec['case']:raise ValueError('journalinputbinding')
                        for method in ARMS:
                            row=dict(cell_id=cell_id,schedule=schedule,prefix=prefix,scope=scope,arm=method,instance_id=str(caseindex),verified=verified,status='verified' if verified else 'unknown')
                            if verified:
                                result=next(v for v in rec['results'] if v['arm']==method);counts=result['counters'];info=rec['verification'];system=result['system']
                                if add(result['phases'])!=counts:raise ValueError('solverphaseconservation')
                                row.update(identified_targets=info['identified'],source_rank=info['source_rank'],delta=info['delta'],base_rank_after_cancellation=info['base_rank_after_cancellation'],base_columns=rec['case']['width'],source_rows=len(rec['case']['source']),target_rows=len(rec['case']['target']),distinct_equations=normalized(rec['case']),matrix_rank=system['rank'],matrix_columns=system['columns'],**{'fr_'+key:counts.get('Fr.field_'+key,0) for key in ('add','sub','mul','inv')},identified_indices=[v['target_index'] for v in result['recoveries'] if v['identifiable']])
                            cells.append(row)
                        caseindex+=1
    generation_check=optional(a.run/'raw/generation-check.json')
    generation_valid=generation_check is not None and generation_check['verification']['checked']is True and generation_check['verification']['curves']==4
    complete=generation_valid and execution['returncode']==0 and not execution['timeout'] and execution['source_unchanged_after'] and not execution['exception'] and all(v['verified'] for v in cells) and len(cells)==864
    unknown_work|=not complete
    totals={arm:dict(observed[arm]+failed[arm]) for arm in ARMS}
    summary=dict(schema='prime-field-a10-holdout-analysis/v1',panel_complete=complete,cells=cells,construction=construction,collection_counters=dict(collection_totals),arm_totals=totals,failed_solver_phase_counters={a:dict(v) for a,v in failed.items()},shared_projection_counters=add([p for v in shared for p in v['phases']]),collection_checks=collection_checks,generation_check=generation_check,generation_valid=generation_valid,solver_calls_verified=sum(v['verified'] for v in cells),observed_producer_calls=producer_calls,unknown_cells=sum(not v['verified'] for v in cells),physical_attempts=1,partial_work_unknown=unknown_work,diagnostic_resources=execution,cost_scope='One sharedcollection/curve, disjointprefix physicalarmwork; scope andsolver analyses are actualcoldcalls. Budgetcostreferences are views ofshared+prepaid+prefix+projection+chosen solver, never extraexecutions. Fp/Fr/group/logical units separate; checker/generation/OS/IO coveredbyinclusiveCPU notfullyprimitiveexpanded. Rawfailedphaseprefixes retained, missingworkunknown.')
    write_once(a.run/'analysis.json',summary,compact=True)
    t=tools();e=t.export_skeleton(protocol,str(a.protocol.resolve()),'local','A10-'+a.run.name)
    e['producer']=dict(runtime='codex',model=None,session=None,role='executor');e['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty']);e['host'].update(path='host.json',sha256=digest(a.run/'host.json'),summary={k:host[k] for k in e['host']['summary']});e['runs']=[]
    keys=[v['id'] for v in protocol['metrics']['primary']]
    for c in cells:
        e['runs'].append(t.run_row(run_id='A10-'+c['arm']+'-'+c['instance_id'],arm=c['arm'],instance_id=c['instance_id'],seed=0,replicate=0,warmup=False,status='succeeded' if c['verified'] else 'timeout' if execution['timeout'] else 'interrupted',measurements=dict(counted={k:c[k] for k in keys if k in c},counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),isolation=dict(tier=None,contended=None,blockers=['sharedhost']),verification=dict(status='verified' if c['verified'] else 'not_run',verifier='independentdense/group/oracle'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in e['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    e['backend_record']=dict(physical_attempts=1,paired_cases=432,solver_calls_verified=summary['solver_calls_verified'],observed_producer_calls=producer_calls,partial_work_unknown=unknown_work,collection_counters=dict(collection_totals),shared_projection_counters=summary['shared_projection_counters'],arm_totals=totals,wall_valid=False,diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')})
    e['files']=[t.file_entry(a.run,str(path.relative_to(a.run)),'raw') for path in sorted(a.run.rglob('*')) if path.is_file()]
    e['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze.py',a.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size);e['analysis']['outputs']=[t.file_entry(a.run,'analysis.json','analysis')];e['flow']=t.compute_flow(e['runs'])
    errors=t.schema_errors(e,'experiment.export/v1') or t.lint_export(e,protocol,a.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(a.run/'export.json',e,compact=True);print(json.dumps(dict(complete=complete,solver_rows=len(cells),unknown=summary['unknown_cells'],producer_calls=producer_calls,collection_counters=dict(collection_totals))))
if __name__=='__main__':main()

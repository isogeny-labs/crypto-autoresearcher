"""Export retained paired results only; no collection or solver work."""
import argparse,json,os,gzip
from pathlib import Path
from collections import Counter
from common import HERE,ROOT,INPUTS,ARMS,load,digest,write_once,tools,observed_journal_work

def optional(path):
    path=Path(path);candidates=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(candidates)>1:raise ValueError('ambiguous retained encoding')
    return None if not candidates else load(candidates[0])

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);a=p.parse_args()
    rules=load(INPUTS);protocol=load(a.protocol);execution=load(a.run/'execution.json');host=load(a.run/'host.json');fixtures=load(ROOT/rules['public_fixtures']['path']);cells=[];caseindex=0;shared=[];all_events=[];phase_totals={arm:{} for arm in ARMS}
    for cell in fixtures['cells']:
        data=optional(a.run/'raw'/(cell['id']+'.json'));records={} if data is None else {(v['descriptor']['arm'],v['descriptor']['prefix'],v['descriptor']['scope']):v for v in data['records']}
        journal=a.run/'raw'/(cell['id']+'.events.jsonl');encoded=journal if journal.is_file() else Path(str(journal)+'.gz');events=[]
        if encoded.is_file():events=[json.loads(v) for v in (gzip.decompress(encoded.read_bytes()).decode() if encoded.suffix=='.gz' else encoded.read_text()).splitlines()]
        all_events.extend(events)
        for schedule in rules['source_schedules']:
            for prefix in rules['prefixes']:
                for scope in rules['scopes']:
                    rec=records.get((schedule,prefix,scope));verified=rec is not None and rec['verification']['checked']is True and rec['verification']['old_control']is True and rec['verification']['a8_dense_control']is True and rec['verification']['all_modes_equal']is True
                    if verified:
                        desc=rec['descriptor'];events_case=[v for v in events if v.get('descriptor')==desc]
                        if [v['kind'] for v in events_case]!=['case_started','case_input']+['solver_complete']*4+['case_checked']:raise ValueError('case journal coverage')
                        if [v['result'] for v in events_case if v['kind']=='solver_complete']!=rec['results']:raise ValueError('journal solver bytes differ')
                        if next(v['case'] for v in events_case if v['kind']=='case_input')!=rec['case']:raise ValueError('journal input differs')
                        shared.append(dict(instance_id=str(caseindex),descriptor=desc,phases=rec['shared_phases']))
                    for arm in ARMS:
                        row=dict(cell_id=cell['id'],schedule=schedule,prefix=prefix,scope=scope,arm=arm,instance_id=str(caseindex),verified=verified,status='verified' if verified else 'unknown')
                        if verified:
                            result=next(v for v in rec['results'] if v['arm']==arm);counts=Counter()
                            for phase in result['phases']:
                                if phase['status']!='complete' or phase['wall_valid']is not False:raise ValueError('incompletephase')
                                counts.update(phase['counters'])
                            if dict(counts)!=result['counters']:raise ValueError('phase conservation')
                            for phase in result['phases']:phase_totals[arm].setdefault(phase['phase'],Counter()).update(phase['counters'])
                            lift=next(v for v in result['phases'] if v['phase']=='certificate_lifting')['counters'];system=result['system']
                            row.update(identified_targets=rec['verification']['identified'],matrix_columns=system['columns'],matrix_rank=system['rank'],matrix_nullity=system['nullity'],source_rows=len(rec['case']['source']),target_rows=len(rec['case']['target']),fr_add=counts.get('Fr.field_add',0),fr_sub=counts.get('Fr.field_sub',0),fr_mul=counts.get('Fr.field_mul',0),fr_inv=counts.get('Fr.field_inv',0),certificate_lift_sub=lift.get('Fr.field_sub',0),verified_original_certificates=counts.get('original_row_certificates_verified',0),counters=dict(counts),base_rank_after_cancellation=rec['verification']['base_rank_after_cancellation'])
                        cells.append(row)
                    caseindex+=1
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['exception'] and not execution['timeout'] and len(cells)==1152 and all(c['verified'] for c in cells)
    totals={arm:dict(sum((Counter(c['counters']) for c in cells if c['verified'] and c['arm']==arm),Counter())) for arm in ARMS}
    shared_counts=dict(sum((Counter(p['counters']) for v in shared for p in v['phases']),Counter()))
    summary=dict(schema='prime-field-a9-solver-analysis/v1',panel_complete=complete,unknown_cells=sum(not c['verified'] for c in cells),paired_cases=288,solver_calls_verified=sum(c['verified'] for c in cells),physical_processes=1,shared_projection_counters=shared_counts,shared_projection_records=shared,cells=cells,arm_totals=totals,arm_phase_totals=phase_totals,physical_work_coverage=dict(finalized_pairs=len(shared),planned_pairs=288,partial_work_unknown=len(shared)!=288),cost_scope='Cold supplied-row solvers only. Shared projection once/case outside arm totals. Prior collection not rerun or free. All phases included; overlappingFp/group units and different Fr primitives not collapsed into scalar weights. Separatechecker unmetered internals and invalid diagnostic clocks explicit.')
    # Primitive phases/counters remain in raw and arm aggregates; avoid duplicate rowcounter payload.
    for c in cells:c.pop('counters',None)
    prior=rules['prior_failed_attempt'];prior_exec=load(ROOT/prior['files'][0]['path']);prior_prefix=load(ROOT/prior['files'][2]['path'])
    old_events=[json.loads(v) for v in gzip.decompress((ROOT/prior['files'][3]['path']).read_bytes()).decode().splitlines()]
    current_observed=observed_journal_work(all_events);current_observed['partial_work_unknown']|=not complete or execution['timeout'] or execution['returncode']!=0 or execution['exception']is not None
    old_observed=observed_journal_work(old_events)
    if old_observed['observed_completed_producer_calls']!=prior_prefix['computed_arm_outputs']:raise ValueError('priorprefix journal count differs')
    if old_observed['observed_arm_counters']!=prior_prefix['observed_arm_counters']:raise ValueError('priorprefix counters differ')
    if complete and current_observed['observed_completed_producer_calls']!=1152:raise ValueError('completedpanel journal coverage differs')
    summary['campaign_accounting']=dict(physical_attempts=2,completed_panel_solver_calls=summary['solver_calls_verified'],current_observed_completed_producer_calls=current_observed['observed_completed_producer_calls'],prior_observed_unverified_solver_calls=old_observed['observed_completed_producer_calls'],cumulative_observed_producer_calls=current_observed['observed_completed_producer_calls']+old_observed['observed_completed_producer_calls'],current_journal_work=current_observed,prior_journal_work=old_observed,prior_arm_counters=old_observed['observed_arm_counters'],prior_projection_counters=old_observed['shared_projection_counters'],cumulative_arm_counters={arm:dict(Counter(current_observed['observed_arm_counters'][arm])+Counter(old_observed['observed_arm_counters'][arm])) for arm in ARMS},cumulative_projection_counters=dict(Counter(current_observed['shared_projection_counters'])+Counter(old_observed['shared_projection_counters'])),prior_execution=prior_exec,current_execution=execution,absolute_deadline=prior['absolute_deadline'],cost_scope='Completed and failed-prefix producer phases charged fromjournals regardlessof finalization. Prior4outputs remainunverified. Unrecorded crashwork explicitunknown, notzero. Old/newinclusiveCPU/wall includechecker/IO/startup separately, no invented Frunits or inclusivephaseclock sums.')
    write_once(a.run/'analysis.json',summary,compact=True);t=tools();e=t.export_skeleton(protocol,str(a.protocol.resolve()),'local','A9-'+a.run.name)
    e['producer']=dict(runtime='codex',model=None,session=None,role='executor');e['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty']);e['host'].update(path='host.json',sha256=digest(a.run/'host.json'),summary={k:host[k] for k in e['host']['summary']});e['runs']=[]
    keys=[v['id'] for v in protocol['metrics']['primary']]
    for c in cells:
        e['runs'].append(t.run_row(run_id='A9-'+c['arm']+'-'+c['instance_id'],arm=c['arm'],instance_id=c['instance_id'],seed=0,replicate=0,warmup=False,status='succeeded' if c['verified'] else 'timeout' if execution['timeout'] else 'interrupted',measurements=dict(counted={k:c[k] for k in keys if k in c},counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),isolation=dict(tier=None,contended=None,blockers=['sharedhost']),verification=dict(status='verified' if c['verified'] else 'not_run',verifier='dense/public/A8control'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in e['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    e['backend_record']=dict(campaign_accounting=summary['campaign_accounting'],physical_processes=1,paired_cases=288,solver_calls_verified=summary['solver_calls_verified'],shared_projection_counters=shared_counts,arm_totals=totals,wall_valid=False,diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')})
    e['files']=[t.file_entry(a.run,str(path.relative_to(a.run)),'raw') for path in sorted(a.run.rglob('*')) if path.is_file()];e['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze.py',a.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size);e['analysis']['outputs']=[t.file_entry(a.run,'analysis.json','analysis')];e['flow']=t.compute_flow(e['runs'])
    errors=t.schema_errors(e,'experiment.export/v1') or t.lint_export(e,protocol,a.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(a.run/'export.json',e,compact=True);print(json.dumps(dict(complete=complete,solver_rows=len(cells),unknown=summary['unknown_cells'],arm_totals=totals)))
if __name__=='__main__':main()

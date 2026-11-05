"""Export retained paired results only; no collection or solver work."""
import argparse,json,os,gzip
from pathlib import Path
from collections import Counter
from common import HERE,ROOT,INPUTS,ARMS,load,digest,write_once,tools

def optional(path):
    path=Path(path);candidates=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(candidates)>1:raise ValueError('ambiguous retained encoding')
    return None if not candidates else load(candidates[0])

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);a=p.parse_args()
    rules=load(INPUTS);protocol=load(a.protocol);execution=load(a.run/'execution.json');host=load(a.run/'host.json');fixtures=load(ROOT/rules['public_fixtures']['path']);cells=[];caseindex=0;shared=[];phase_totals={arm:{} for arm in ARMS}
    for cell in fixtures['cells']:
        data=optional(a.run/'raw'/(cell['id']+'.json'));records={} if data is None else {(v['descriptor']['arm'],v['descriptor']['prefix'],v['descriptor']['scope']):v for v in data['records']}
        journal=a.run/'raw'/(cell['id']+'.events.jsonl');encoded=journal if journal.is_file() else Path(str(journal)+'.gz');events=[]
        if encoded.is_file():events=[json.loads(v) for v in (gzip.decompress(encoded.read_bytes()).decode() if encoded.suffix=='.gz' else encoded.read_text()).splitlines()]
        for schedule in rules['source_schedules']:
            for prefix in rules['prefixes']:
                for scope in rules['scopes']:
                    rec=records.get((schedule,prefix,scope));verified=rec is not None and rec['verification']['checked']is True and rec['verification']['old_control']is True
                    if verified:
                        desc=rec['descriptor'];events_case=[v for v in events if v.get('descriptor')==desc]
                        if [v['kind'] for v in events_case]!=['case_started','case_input','solver_complete','solver_complete','case_checked']:raise ValueError('case journal coverage')
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
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['exception'] and not execution['timeout'] and len(cells)==576 and all(c['verified'] for c in cells)
    totals={arm:dict(sum((Counter(c['counters']) for c in cells if c['verified'] and c['arm']==arm),Counter())) for arm in ARMS}
    shared_counts=dict(sum((Counter(p['counters']) for v in shared for p in v['phases']),Counter()))
    summary=dict(schema='prime-field-a8-solver-analysis/v1',panel_complete=complete,unknown_cells=sum(not c['verified'] for c in cells),paired_cases=288,solver_calls_verified=sum(c['verified'] for c in cells),physical_processes=1,shared_projection_counters=shared_counts,shared_projection_records=shared,cells=cells,arm_totals=totals,arm_phase_totals=phase_totals,physical_work_coverage=dict(finalized_pairs=len(shared),planned_pairs=288,partial_work_unknown=len(shared)!=288),cost_scope='Cold supplied-row solvers only. Shared projection once/case outside arm totals. Prior collection not rerun or free. All phases included; overlappingFp/group units and different Fr primitives not collapsed into scalar weights. Separatechecker unmetered internals and invalid diagnostic clocks explicit.')
    write_once(a.run/'analysis.json',summary,compact=True);t=tools();e=t.export_skeleton(protocol,str(a.protocol.resolve()),'local','A8-'+a.run.name)
    e['producer']=dict(runtime='codex',model=None,session=None,role='executor');e['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty']);e['host'].update(path='host.json',sha256=digest(a.run/'host.json'),summary={k:host[k] for k in e['host']['summary']});e['runs']=[]
    keys=[v['id'] for v in protocol['metrics']['primary']]
    for c in cells:
        e['runs'].append(t.run_row(run_id='A8-'+a.run.name+'-'+c['arm']+'-'+c['instance_id'],arm=c['arm'],instance_id=c['instance_id'],seed=0,replicate=0,warmup=False,status='succeeded' if c['verified'] else 'timeout' if execution['timeout'] else 'interrupted',measurements=dict(counted={k:c[k] for k in keys if k in c},counters=c.get('counters',{}),wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),isolation=dict(tier=None,contended=None,blockers=['sharedmanagedworkstation; diagnosticclocks']),verification=dict(status='verified' if c['verified'] else 'not_run',verifier='Separateprojection/dense-affine/kernel/originalrow/RHS/publicchecks'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in e['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    e['backend_record']=dict(physical_processes=1,paired_cases=288,solver_calls_verified=summary['solver_calls_verified'],shared_projection_counters=shared_counts,arm_totals=totals,wall_valid=False,diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')})
    e['files']=[t.file_entry(a.run,str(path.relative_to(a.run)),'raw') for path in sorted(a.run.rglob('*')) if path.is_file()];e['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze.py',a.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size);e['analysis']['outputs']=[t.file_entry(a.run,'analysis.json','analysis')];e['flow']=t.compute_flow(e['runs'])
    errors=t.schema_errors(e,'experiment.export/v1') or t.lint_export(e,protocol,a.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(a.run/'export.json',e,compact=True);print(json.dumps(dict(complete=complete,solver_rows=len(cells),unknown=summary['unknown_cells'],arm_totals=totals)))
if __name__=='__main__':main()

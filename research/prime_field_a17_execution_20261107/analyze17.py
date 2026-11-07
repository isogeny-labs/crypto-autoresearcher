"""Bind owned query programs and paid costs; retain incomplete and failed prefixes."""
import argparse,gzip,json,os
from pathlib import Path
from collections import Counter,defaultdict
from deps17 import commitment
from custody17 import HERE,ROOT,INPUTS,PROGRAMS,load,write_once,digest,tools,descriptors
from cost17 import cold,phase_total,dominates,ARITHMETIC
from analyze16 import bound,phase_binding,pair_cost_binding,counts_valid
from cold14 import prior
from baseline import costs
from streams17 import lines

COLS=['case_id','cell_id','program','base_arm','target_horizon','target_policy','scope','verified','certificate_checked',
    'native_columns','supplied_columns','base_columns','source_rows','target_rows','identified_targets','identified_mask',
    'geometric_queries','skipped_slots','executed_extra_slots','certified_targets','formal_endpoints','omitted_reference_rows']


def optional(path):
    if path.exists():return json.loads(path.read_text())
    compressed=Path(str(path)+'.gz')
    return json.loads(gzip.decompress(compressed.read_bytes())) if compressed.exists() else None


def complete_checkpoint(receipt,cid,ordinal):
    return bool(receipt and receipt.get('returncode')==0 and receipt.get('command')==['bash','scripts/checkpoint.sh','push'] and
        receipt.get('closed_curve')==cid and receipt.get('completed_curves')==ordinal and receipt.get('checked_cases')==2*ordinal and
        receipt.get('checked_batch_solver_calls')==3*ordinal and receipt.get('completed_online_engines')==ordinal and
        's3://setec-astronomy-artifacts/checkpoints/'in receipt.get('stdout',''))


def phase_journal(phases,events):
    observed=[v['phase'] for v in events if v['kind']=='affine_phase']
    if Counter(map(commitment,phases))!=Counter(map(commitment,observed)):raise ValueError('complete physical phase/journal bytes differ')


def summarize(run,rules,execution):
    raw=run/'raw';plans=dict(descriptors(rules));rows={};views=[];curves=[];errors=[];checkpoints=[];consequences=[]
    physical=defaultdict(Counter);observed=defaultdict(Counter);engine_checked={v:Counter() for v in costs.ENGINES}
    started=finished=failed=online_started=online_finished=online_failed=0
    def read(path):
        try:return optional(path)
        except Exception as error:errors.append(dict(path=str(path),error_type=type(error).__name__,error=str(error)));return None
    def events(path):
        try:return list(lines(path))
        except Exception as error:errors.append(dict(path=str(path),error_type=type(error).__name__,error=str(error)));return []
    start,child,admission=read(run/'checkpoint-admitted-start.json'),read(run/'child.json'),read(raw/'admission.json')
    startup=bool(start and child and admission and admission.get('returncode')==0 and admission.get('command')==['bash','scripts/checkpoint.sh','gate'] and
        start.get('command')==['bash','scripts/checkpoint.sh','push'] and start.get('returncode')==0 and start.get('native_curves_generated')==0 and
        start.get('admission_last_push')==admission.get('last_push') and all(start.get(k)==child.get(k) for k in ('child_pid','child_process_group','supervisor_pid')))
    if not startup:errors.append(dict(error='missing/failed actual admitted-start checkpoint or PID binding'))
    generated,generation=read(raw/'generated.json'),read(raw/'generation-check.json')
    generation_valid=bool(startup and bound(generated,generation) and generation['verification'].get('curves')==4)
    for ev in events(raw/'generation.events.jsonl'):
        if ev['kind']=='affine_phase':physical['generation'].update(ev['phase']['counters'])
        if ev['kind'].endswith('_failed'):errors.append(dict(event=ev))
    ordinal=0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            ordinal+=1;cid='p'+str(field['p'])+'-i'+str(ci);owned={}
            shared_events=events(raw/(cid+'.shared.events.jsonl'))
            for ev in shared_events:
                if ev['kind']=='affine_phase':physical[cid+'.shared_public_targets'].update(ev['phase']['counters'])
                if ev['kind'].endswith('_failed'):errors.append(dict(cell_id=cid,event=ev))
            targets,target_check=read(raw/(cid+'.targets.json')),read(raw/(cid+'.targets-check.json'))
            target_valid=bool(generation_valid and bound(targets,target_check))
            if target_valid:phase_binding(targets);phase_journal(targets['phases'],shared_events)
            for arm in PROGRAMS:
                prefix=cid+'.'+arm+'.';evs=events(raw/(prefix+'events.jsonl'))
                batch_events={};batch_starts={};complete_query=None
                for ev in evs:
                    kind=ev['kind']
                    if kind=='affine_phase':
                        if not counts_valid(ev['phase']['counters']):raise ValueError('invalid physical counter prefix')
                        physical[cid+'.'+arm+'.'+ev['context'].get('kind','construction')].update(ev['phase']['counters'])
                    elif kind=='batch_solver_start':
                        key=ev['execution_arm'];started+=1
                        if key in batch_starts:raise ValueError('duplicate actual batch solver start')
                        batch_starts[key]=ev
                    elif kind=='batch_solver_complete':
                        key=ev['execution_arm'];finished+=1
                        if key not in batch_starts or key in batch_events:raise ValueError('unstarted/duplicate actual batch solver completion')
                        batch_events[key]=ev;observed[key].update(ev['counters'])
                    elif kind=='batch_solver_failed':
                        failed+=1;observed[ev['execution_arm']].update(phase_total(ev['phases']));errors.append(dict(cell_id=cid,event=ev))
                    elif kind=='online_start':online_started+=1
                    elif kind=='query_program_complete':
                        if complete_query is not None:raise ValueError('duplicate complete query')
                        complete_query=ev
                        if arm=='suppress':online_finished+=1
                    elif kind=='online_failed':online_failed+=1;errors.append(dict(cell_id=cid,event=ev))
                    elif kind.endswith('_failed'):errors.append(dict(cell_id=cid,event=ev))
                names=('base','prelude','recipe','collection','construction','query','cache','primary','joint','cold','complete')
                val={name:read(raw/(prefix+name+'.json')) for name in names}
                chk={name:read(raw/(prefix+name+'-check.json')) for name in ('base','prelude','recipe','collection','construction','query','primary','joint')}
                owned[arm]=val
                certified=bool(bound(val['query'],chk['query']) and bound(val['primary'],chk['primary']) and bound(val['joint'],chk['joint']))
                valid=bool(target_valid and certified and all(bound(val[name]['collection'] if name=='collection' and val[name] else val[name],chk[name])
                    for name in ('base','prelude','recipe','collection','construction')) and val['cache'] and val['cold'] and val['complete'])
                idx=2*(ordinal-1)+PROGRAMS.index(arm);row=dict(case_id=idx,**plans[idx],verified=False,certificate_checked=certified)
                if certified:
                    query,primary,joint=val['query'],val['primary'],val['joint'];case=query['case']
                    primary_mask=sum(1<<v['target_index'] for v in primary['recoveries'] if v['identifiable'])
                    if primary_mask!=sum(1<<v['target_index'] for v in joint['recoveries'] if v['identifiable']):raise ValueError('own primary/joint target mask disagreement')
                    if [(v['identifiable'],v['scalar']) for v in primary['recoveries']]!=[(v['identifiable'],v['scalar']) for v in joint['recoveries']]:raise ValueError('own primary/joint target scalar disagreement')
                    row.update(native_columns=case['width'],supplied_columns=len(case['source']),base_columns=0,source_rows=len(case['source']),
                        target_rows=len(case['target']),identified_targets=primary_mask.bit_count(),identified_mask=primary_mask,
                        geometric_queries=len(val['cache']['records']) if val['cache'] else None,skipped_slots=sum(v['kind']=='slot_skipped' for v in query['schedule']),
                        executed_extra_slots=sum(v['kind']=='slot_queried' and v['origin']=='extra' for v in query['schedule']),
                        certified_targets=len(primary.get('certificates',[])),formal_endpoints=24*rules['targets'],
                        solver_counters={arm:primary['counters'],'joint_on_'+arm:joint['counters']})
                if valid:
                    built,pre,recipe,col,cloud,query,cache,primary,joint=(val[v] for v in ('base','prelude','recipe','collection','construction','query','cache','primary','joint'))
                    if col['cell']!=pre['cell'] or built['cell']!=pre['cell']:raise ValueError('own native fixture differs')
                    col=col['collection']
                    if any(v.get('arm_owner')!=arm for v in (built,pre,col,recipe)):raise ValueError('paid construction owner differs')
                    if (cloud['owner']!=query['owner'] or cache['owner']!=query['owner'] or query['owner']['arm']!=arm or
                        query['owner']['horizon']!=24 or query['owner']['cache_limit']!=24*rules['targets'] or
                        len(cache['records'])>24*rules['targets'] or cache['engine_start']!=len(col['query_engine_records'])):raise ValueError('owned full-horizon/cache identity')
                    if chk['query']['verification']['cache_output_sha256']!=commitment(cache):raise ValueError('cache output/cost binding')
                    if query['construction_sha256']!=commitment(cloud) or complete_query['producer_output_sha256']!=commitment(query):raise ValueError('query journal/output binding')
                    if chk['joint']['verification']['primary_output_sha256']!=commitment(primary):raise ValueError('paired native checker primary binding')
                    all_phases=[]
                    for value in (built,pre,recipe,cloud,cache):phase_binding(value);all_phases+=value['phases']
                    phase_binding(col,'collection_phases','collection_counters');all_phases+=col['collection_phases']
                    for name in ('assembly','scheduling'):
                        phase_binding(query,name+'_phases',name+'_counters');all_phases+=query[name+'_phases']
                    phase_binding(primary);phase_binding(joint)
                    if arm=='suppress':
                        if primary!=query['online']:raise ValueError('primary is not the same actual online engine')
                        all_phases+=primary['phases'];observed[arm].update(primary['counters'])
                    else:
                        if arm not in batch_events or batch_events[arm]['counters']!=primary['counters']:raise ValueError('actual full batch result/cost binding')
                    if 'joint_on_'+arm not in batch_events or batch_events['joint_on_'+arm]['counters']!=joint['counters']:raise ValueError('actual own-pool joint result/cost binding')
                    expected_batch={arm,'joint_on_'+arm} if arm=='full' else {'joint_on_'+arm}
                    if set(batch_starts)!=expected_batch or set(batch_events)!=expected_batch:raise ValueError('actual batch census per program')
                    phase_journal(all_phases,evs)
                    pair_cost_binding(col,chk['collection']['verification']['pair_construction'])
                    for engine in costs.ENGINES:
                        engine_checked[engine].update(chk['collection']['verification']['query_engines']['engine_totals'][engine])
                        engine_checked[engine].update(chk['query']['verification']['cache']['query_engines']['engine_totals'][engine])
                    if recipe['counters'].get('target_recipe_hashes',0)!=chk['recipe']['verification']['independent_hashes']:raise ValueError('recipe hash schedule')
                    view=cold(arm,built,pre,col,recipe,targets,cloud,query,cache,primary)
                    if view!=val['cold']:raise ValueError('complete cold vector recomputation differs')
                    marker=val['complete']
                    if marker.get('complete')is not True or marker.get('case_id')!=idx or marker.get('descriptor')!=plans[idx] or any(marker[k+'_output_sha256']!=commitment(val[k]) for k in ('query','primary','joint','cold')):raise ValueError('complete own case marker')
                    row['verified']=True;views.append(dict(case_id=idx,descriptor=plans[idx],identified_mask=row['identified_mask'],**view))
                rows[idx]=row
            span,marker=read(raw/(cid+'.row-consequences.json')),read(raw/(cid+'.complete.json'))
            if all(rows[2*(ordinal-1)+j]['verified'] for j in range(2)) and span and marker:
                if span.get('checked')is not True or span.get('not_target_solver')is not True:raise ValueError('postpair row diagnostic status')
                a,b=owned['full'],owned['suppress']
                if span['reference_case_sha256']!=commitment(a['query']['case']) or span['candidate_case_sha256']!=commitment(b['query']['case']) or len(span['witnesses'])!=len(a['query']['case']['target']):raise ValueError('postpair row consequence identity')
                proposed=[ev['witness'] for ev in shared_events if ev['kind']=='row_consequence_proposed']
                checked=[ev for ev in shared_events if ev['kind']=='row_consequence_checked']
                if proposed!=span['witnesses'] or len(checked)!=len(proposed) or any(v['reference_target_row']!=i or v['witness_sha256']!=commitment(proposed[i]) for i,v in enumerate(checked)):raise ValueError('row-consequence journal binding')
                if a['base']['cell']!=b['base']['cell'] or a['base']['knowledge']!=b['base']['knowledge'] or a['recipe']['selection']!=b['recipe']['selection']:raise ValueError('paired base or recipe identity')
                if any(a['construction'][k]!=b['construction'][k] for k in ('recipe','endpoints','selections','scalar_events','labels','equations','counters')):raise ValueError('paid full24 construction parity')
                if rows[2*(ordinal-1)]['identified_mask']!=rows[2*(ordinal-1)+1]['identified_mask']:raise ValueError('safe suppression lost target identities')
                if (marker.get('complete')is not True or marker.get('curve_index')!=ordinal-1 or marker.get('checked_case_systems')!=2*ordinal or
                    marker.get('completed_batch_solver_calls')!=3*ordinal or marker.get('completed_online_engines')!=ordinal or marker.get('verified_execution_rows')!=4*ordinal or
                    marker.get('row_consequences_sha256')!=commitment(span) or marker.get('full_construction_equal')is not True or marker.get('identified_mask')!=rows[2*(ordinal-1)]['identified_mask']):raise ValueError('complete curve census/binding')
                consequences.append(dict(cell_id=cid,proof=span));curves.append(dict(cell_id=cid,fixture=a['base']['cell']['fixture']))
                for j in range(2):rows[2*(ordinal-1)+j]['omitted_reference_rows']=span['omitted_reference_rows']
            receipt=read(run/('checkpoint-'+cid+'.json'));valid=complete_checkpoint(receipt,cid,ordinal)
            checkpoints.append(dict(cell_id=cid,valid=valid,receipt=receipt))
            if not valid:errors.append(dict(cell_id=cid,error='missing/failed exact closed-curve canonical checkpoint'))
    cells=[rows.get(idx,dict(case_id=idx,**desc,verified=False,certificate_checked=False)) for idx,desc in plans.items()]
    full=bool(execution.get('returncode')==0 and not execution.get('timeout') and not execution.get('exception') and execution.get('source_unchanged_after') and
        len(curves)==4 and not errors and all(v['verified'] for v in cells) and (started,finished,failed,online_started,online_finished,online_failed)==(12,12,0,4,4,0))
    engines={e:dict(sum((Counter(costs.engine_arithmetic(v)[e]) for v in physical.values()),Counter())) for e in costs.ENGINES}
    if full and any(Counter(engines[e])!=engine_checked[e] for e in costs.ENGINES):raise ValueError('physical endpoint engines differ from independent receipts')
    return dict(cells=cells,cold_views=views,curves=curves,row_consequences=consequences,errors=errors,panel_complete=full,
        physical_counters={k:dict(v) for k,v in physical.items()},observed_algorithm_counters={k:dict(v) for k,v in observed.items()},
        query_engine_totals=engines,closed_curve_checkpoints=checkpoints,admitted_start_checkpoint=start,
        observed_batch_solver_starts=started,observed_completed_batch_solver_calls=finished,observed_failed_batch_solver_calls=failed,
        observed_online_starts=online_started,observed_completed_online_engines=online_finished,observed_failed_online_engines=online_failed)


def comparisons(views):
    out=[]
    by={(v['descriptor']['cell_id'],v['program']):v for v in views}
    for (cid,program),candidate in by.items():
        if program!='suppress' or (cid,'full')not in by:continue
        reference=by[cid,'full']
        for engine in costs.ENGINES:
            a=dict(identified_mask=candidate['identified_mask'],counters=candidate['single_engine_counters'][engine])
            b=dict(identified_mask=reference['identified_mask'],counters=reference['single_engine_counters'][engine])
            out.append(dict(cell_id=cid,query_engine=engine,candidate_mask=a['identified_mask'],reference_mask=b['identified_mask'],
                candidate_dominates_arithmetic=dominates(a,b),reference_dominates_arithmetic=dominates(b,a),
                candidate_dominates_retained=dominates(a,b,sorted(a['counters'].keys()|b['counters'].keys())),
                reference_dominates_retained=dominates(b,a,sorted(a['counters'].keys()|b['counters'].keys()))))
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();rules,protocol=load(INPUTS),load(args.protocol);execution,host=load(args.run/'execution.json'),load(args.run/'host.json')
    data=summarize(args.run,rules,execution);cells=data['cells']
    metrics=dict(schema='prime-field-a17-metrics/v1',panel_complete=data['panel_complete'],physical_attempts=1,
        planned_systems=8,planned_batch_solver_calls=12,planned_online_engines=4,planned_export_execution_rows=16,
        verified_systems=sum(v['verified'] for v in cells),unknown_systems=sum(not v['verified'] for v in cells),
        verified_export_execution_rows=2*sum(v['verified'] for v in cells),observed_certified_systems=sum(v['certificate_checked'] for v in cells),
        columns=COLS,rows=[[v.get(k) for k in COLS] for v in cells],physical_counters=data['physical_counters'],
        observed_algorithm_counters=data['observed_algorithm_counters'],query_engine_totals=data['query_engine_totals'],
        source_commit=execution['source_commit'],protocol_sha256=execution['protocol_sha256'],partial_work_unknown=not data['panel_complete'],
        **{k:v for k,v in data.items() if k.startswith('observed_') and k!='observed_algorithm_counters'})
    write_once(args.run/'metrics.json',metrics,compact=True)
    analysis=dict(schema='prime-field-a17-analysis/v1',**data,matched_comparisons=comparisons(data['cold_views']),diagnostic_resources=execution,
        metrics_sha256=digest(args.run/'metrics.json'),inference='Fully paid known48/full24 construction; causal suppression only after own native/public proof. Compare actual queries and separate construction/query/online arithmetic, not logical slots as cost. Four paired curves/32 public targets; no unknown-base transfer, calibrated runtime/whole-attack/novelty or signed independent execution/replay claim.')
    write_once(args.run/'analysis.json',analysis,compact=True);prior.encode_large(args.run/'analysis.json')
    t=tools();export=t.export_skeleton(protocol,str(args.protocol.resolve()),'local','A17-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor');export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']});export['runs']=[]
    metric_ids={v['id'] for v in protocol['metrics']['primary']}
    for cell in cells:
        for arm in (cell['program'],'joint_on_'+cell['program']):
            counted={k:cell[k] for k in COLS if type(cell.get(k))is int and k in metric_ids}
            if cell['verified']:counted.update({'fr_'+op:cell['solver_counters'][arm].get('Fr.field_'+op,0) for op in ('add','sub','mul','inv')})
            export['runs'].append(t.run_row(run_id='A17-'+str(len(export['runs'])),arm=arm,instance_id=str(cell['case_id']//2),seed=0,replicate=0,warmup=False,
                status='succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'interrupted',
                measurements=dict(counted=counted,counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
                isolation=dict(tier=None,contended=None,blockers=['sharedhost']),verification=dict(status='verified' if cell['verified'] else 'not_run',verifier='producer group/constructor/causal/native/cost checks; no signed independent standing'),
                started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['backend_record']=dict(physical_attempts=1,planned_systems=8,planned_batch_solver_calls=12,planned_online_engines=4,planned_export_execution_rows=16,
        verified_export_execution_rows=metrics['verified_export_execution_rows'],physical_counters=data['physical_counters'],partial_work_unknown=not data['panel_complete'])
    export['files']=[t.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file() and p.name!='.gitignore']
    export['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze17.py',args.run.resolve()),sha256=digest(HERE/'analyze17.py'),bytes=(HERE/'analyze17.py').stat().st_size)
    export['analysis']['outputs']=[t.file_entry(args.run,name,'analysis') for name in ('metrics.json','analysis.json')];export['flow']=t.compute_flow(export['runs'])
    errors=t.schema_errors(export,'experiment.export/v1') or t.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export,compact=True);prior.encode_large(args.run/'export.json')
    print(json.dumps(dict(panel_complete=data['panel_complete'],verified_systems=metrics['verified_systems'],batch_calls=data['observed_completed_batch_solver_calls'],online_engines=data['observed_completed_online_engines'])))


if __name__=='__main__':main()

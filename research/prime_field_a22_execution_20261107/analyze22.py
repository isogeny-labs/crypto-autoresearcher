"""Bind published producer/checker payloads; retain unknown cases and paid prefixes."""
import argparse,json,os
from pathlib import Path
from collections import Counter,defaultdict
from deps22 import commitment
from custody22 import HERE,ROOT,INPUTS,PROGRAMS,load,write_once,digest,tools,descriptors
from streams22 import lines
from analyze17 import optional,phase_journal
from analyze16 import bound,phase_binding,pair_cost_binding,counts_valid
from baseline import costs
from cold14 import prior

COLS=['case_id','cell_id','program','verified','certificate_checked','native_columns','old_columns','auxiliary_slots',
    'source_rows','target_rows','identified_targets','identified_mask','source_delta','full_delta','supplied_K_delta',
    'collected_after_K','target_marginal_delta','direct_base_gain','cross_row_gain','reference_rank','base_rank_after',
    'outside_rank','geometric_queries','formal_definition_rows','expanded_old_joint_rank','definition_only_delta',
    'direct_identified_targets','direct_identified_mask','direct_fr_mul','direct_fr_inv']


def summarize(run,rules,execution):
    raw=run/'raw';errors=[];physical=defaultdict(Counter);observed=defaultdict(Counter);checked_engines={e:Counter()for e in costs.ENGINES}
    def read(p):
        try:return optional(p)
        except Exception as error:errors.append(dict(path=str(p),error_type=type(error).__name__,error=str(error)));return None
    def journal(p):
        values=[]
        try:
            for v in lines(p):values.append(v)
        except Exception as error:errors.append(dict(path=str(p),error_type=type(error).__name__,error=str(error),paid_prefix_retained=True))
        return values
    start,child,admission=read(run/'checkpoint-admitted-start.json'),read(run/'child.json'),read(raw/'admission.json')
    startup=bool(start and child and admission and admission.get('returncode')==0 and admission.get('command')==['bash','scripts/checkpoint.sh','gate']and
        start.get('command')==['bash','scripts/checkpoint.sh','push']and start.get('returncode')==0 and start.get('native_curves_generated')==0 and
        start.get('admission_last_push')==admission.get('last_push')and all(start.get(k)==child.get(k)for k in ('child_pid','child_process_group','supervisor_pid')))
    generated,generation=read(raw/'generated.json'),read(raw/'generation-check.json')
    generation_valid=bool(startup and bound(generated,generation)and generation['verification'].get('curves')==4)
    cells=[];cold=[];direct_cold=[];checkpoints=[];started=finished=failed=0;norm_inputs={}
    for case_id,descriptor in descriptors(rules):
        cid,program=descriptor['cell_id'],descriptor['program'];prefix=cid+'.'+program+'.';evs=[];starts=Counter();done={}
        if program==PROGRAMS[0]:
            cp=read(run/('checkpoint-'+cid+'.json'));ordinal=case_id//4+1
            valid=bool(cp and cp.get('returncode')==0 and cp.get('command')==['bash','scripts/checkpoint.sh','push']and
                cp.get('closed_curve')==cid and cp.get('completed_curves')==ordinal and cp.get('checked_cases')==4*ordinal and
                cp.get('checked_batch_solver_calls')==9*ordinal and cp.get('completed_online_engines')==0 and
                's3://setec-astronomy-artifacts/checkpoints/'in cp.get('stdout',''))
            checkpoints.append(dict(cell_id=cid,valid=valid,receipt=cp))
            shared=journal(raw/(cid+'.shared.events.jsonl'))
            for ev in shared:
                if ev.get('kind')=='affine_phase':physical[cid+'.shared_targets'].update(ev['phase']['counters'])
        for name in ('setup.events','events'):
            events=journal(raw/(prefix+name+'.jsonl'));evs.extend(events)
            for ev in events:
                kind=ev.get('kind')
                if kind=='affine_phase':
                    counts=ev['phase']['counters']
                    if not counts_valid(counts):raise ValueError('invalid paid prefix counter')
                    physical[prefix+ev['context'].get('kind','construction')].update(counts)
                elif kind=='batch_solver_start':started+=1;starts[ev['execution_arm']]+=1
                elif kind=='batch_solver_complete':
                    finished+=1;observed[ev['execution_arm']].update(ev['counters'])
                    if ev['execution_arm']in done:raise ValueError('duplicate actual solver completion')
                    done[ev['execution_arm']]=ev
                elif kind=='batch_solver_failed':
                    failed+=1;observed[ev['execution_arm']].update(sum((Counter(p['counters'])for p in ev['phases']),Counter()));errors.append(ev)
                elif kind=='failure'or kind.endswith('_failed'):errors.append(ev)
        names=('base','prelude','recipe','collection','construction','cache','case','assembly','aux_cancel_joint','sparse_joint','direct_formal','information','complete')
        val={name:read(raw/(prefix+name+'.json'))for name in names}
        chk={name:read(raw/(prefix+name+'-check.json'))for name in ('base','prelude','recipe','collection','construction','cache','case','aux_cancel_joint','sparse_joint','direct_formal','information','expanded')}
        target,target_check=read(raw/(cid+'.targets.json')),read(raw/(cid+'.targets-check.json'))
        direct_ok=program!='formalpair16'or bound(val['direct_formal'],chk['direct_formal'])
        certified=bool(direct_ok and bound(val['aux_cancel_joint'],chk['aux_cancel_joint'])and bound(val['sparse_joint'],chk['sparse_joint'])and bound(val['information'],chk['information'])and chk['expanded']and chk['expanded']['verification'].get('checked')is True)
        all_bound=bool(all(bound(val[name]['collection']if name=='collection'and val[name]else val[name],chk[name])for name in ('prelude','recipe','collection','construction','cache'))and
            (program=='norm32'or bound(val['base'],chk['base'])))
        valid=bool(generation_valid and bound(target,target_check)and certified and all_bound and bound(val['case'],chk['case'])and val['assembly']and val['complete']and checkpoints[-1]['valid'])
        row=dict(case_id=case_id,**descriptor,verified=valid,certificate_checked=certified)
        if certified:
            primary,joint,info=val['aux_cancel_joint'],val['sparse_joint'],val['information'];case=val['case']
            if not case:raise ValueError('certified case bytes absent')
            expanded=chk['expanded']['verification']
            if (expanded['applicable']is not(program=='formalpair16')or expanded['input_case_sha256']!=commitment(case)or
                expanded['prepared_sha256']!=commitment(val['prelude'])or expanded['primary_sha256']!=commitment(primary)or
                expanded['information_sha256']!=commitment(info)):raise ValueError('expanded-old semantic oracle custody differs')
            reference=read(raw/(cid+'.reference.json'))
            reference_check=read(raw/(cid+'.reference-check.json'))
            if not bound(reference,reference_check)or commitment(reference['rows'])!=commitment(info['reference']):raise ValueError('information reference receipt differs')
            if program=='norm32':norm_inputs[cid]=(commitment(case),commitment(val['prelude']))
            if (reference['source_case_sha256'],reference_check['verification']['prepared_sha256'])!=norm_inputs[cid]:raise ValueError('reference borrowed own K/another program')
            for name in ('aux_cancel_joint','sparse_joint','information'):
                proof=chk[name]['verification']
                if proof['input_case_sha256']!=commitment(case)or proof['prepared_sha256']!=commitment(val['prelude']):raise ValueError('algebra case/input binding differs')
            if chk['information']['verification']['reference_sha256']!=commitment(reference['rows']):raise ValueError('reference input hash differs')
            if [(v['identifiable'],v['scalar'])for v in primary['recoveries']]!=[(v['identifiable'],v['scalar'])for v in joint['recoveries']]:raise ValueError('primary/native target disagreement')
            if program=='formalpair16':
                direct=val['direct_formal'];proof=chk['direct_formal']['verification']
                if proof['input_case_sha256']!=commitment(case)or proof['prepared_sha256']!=commitment(val['prelude']):raise ValueError('direct case/preparation custody mismatch')
                if [(v['identifiable'],v['scalar'])for v in direct['recoveries']]!=[(v['identifiable'],v['scalar'])for v in primary['recoveries']]:raise ValueError('direct/auxiliary target disagreement')
                if proof['native_joint_rank']!=chk['sparse_joint']['verification']['joint_rank']or proof['identified']!=sum(v['identifiable']for v in direct['recoveries']):raise ValueError('direct native rank/target receipt mismatch')
            mask=sum(1<<v['target_index']for v in primary['recoveries']if v['identifiable']);view=info['views'];full=view['full']['total']
            if program=='formalpair16'and(expanded['target_mask']!=mask or expanded['old_base_rank_after']!=full['base_rank_after']or expanded['definition_only_old_base_delta']!=0):raise ValueError('expanded-old/cancelled semantics differ')
            row.update(native_columns=case['width'],old_columns=info['projection']['old_width'],auxiliary_slots=case['width']-val['prelude']['norm_size'],
                source_rows=len(case['source']),target_rows=len(case['target']),identified_targets=mask.bit_count(),identified_mask=mask,
                source_delta=view['source']['total']['delta'],full_delta=full['delta'],supplied_K_delta=view['full']['supplied']['delta'],
                collected_after_K=view['full']['collected_after_own_K'],target_marginal_delta=info['target_marginal_delta'],
                direct_base_gain=full['direct_base_gain'],cross_row_gain=full['cross_row_gain'],reference_rank=full['reference_rank'],base_rank_after=full['base_rank_after'],
                outside_rank=full['outside_rank'],geometric_queries=len(val['cache']['records'])if val['cache']else None,
                solver_counters={program:primary['counters'],'joint_on_'+program:joint['counters']},information_counters=info['counters'])
            row.update(formal_definition_rows=sum(v['kind']=='formal_definition'for v in case['source_origins']),
                expanded_old_joint_rank=expanded.get('expanded_joint_rank'),definition_only_delta=expanded.get('definition_only_old_base_delta'))
        if certified:
            row.update(direct_identified_targets=None,direct_identified_mask=None,direct_fr_mul=None,direct_fr_inv=None)
            if program=='formalpair16':
                row.update(direct_identified_targets=sum(v['identifiable']for v in direct['recoveries']),direct_identified_mask=sum(1<<v['target_index']for v in direct['recoveries']if v['identifiable']),direct_fr_mul=direct['counters'].get('Fr.field_mul',0),direct_fr_inv=direct['counters'].get('Fr.field_inv',0))
                row['solver_counters']['direct_on_'+program]=direct['counters']
        if valid:
            expected={program:val['aux_cancel_joint'],'joint_on_'+program:val['sparse_joint']}
            if program=='formalpair16':expected['direct_on_'+program]=val['direct_formal']
            if dict(starts)!={k:1 for k in expected}or set(done)!=set(expected):raise ValueError('actual solver start/completion census')
            if any(done[k]['counters']!=v['counters']for k,v in expected.items()):raise ValueError('actual solver event counters differ')
            proof=chk['case']['verification']
            if any(proof[key]!=commitment(value)for key,value in (
                ('prepared_sha256',val['prelude']),('collection_sha256',val['collection']['collection']),('branch_sha256',val['construction']),
                ('cache_records_sha256',val['cache']['records']),('assembly_sha256',val['assembly']))):raise ValueError('native assembly custody differs')
            for name in ('prelude','recipe','construction','cache','assembly','aux_cancel_joint','sparse_joint','information'):phase_binding(val[name])
            if program=='formalpair16':phase_binding(val['direct_formal'])
            if program!='norm32':phase_binding(val['base'])
            c=val['collection']['collection'];phase_binding(c,'collection_phases','collection_counters');phase_binding(c['arms']['ap0'])
            pair_cost_binding(c,chk['collection']['verification']['pair_construction'])
            if val['complete']['case_id']!=case_id or val['complete']['descriptor']!=descriptor:raise ValueError('case descriptor binding')
            if val['complete']['solver_calls']!=len(expected)or val['complete']['direct_checked']is not(program=='formalpair16'):raise ValueError('actual direct/aux/native case call census')
            source=c['arms']['ap0']
            # Counter/phase conservation alone cannot validate either endpoint
            # engine. Reconcile the independently reconstructed record totals
            # against the exact namespaces removed by select_engine.
            for counter_groups,receipt in (([c['collection_counters'],source['counters']],chk['collection']['verification']['query_engines']),
                ([val['cache']['counters']],chk['cache']['verification']['query_engines'])):
                actual=sum((Counter(v)for v in counter_groups),Counter())
                engines=costs.engine_arithmetic(actual)
                if any(Counter(engines[e])!=Counter(receipt['engine_totals'][e])for e in costs.ENGINES):raise ValueError('physical endpoint engines differ from independent receipts')
                for e in costs.ENGINES:checked_engines[e].update(receipt['engine_totals'][e])
            phases=[v for name in ('prelude','recipe','construction','cache','assembly','information')for v in val[name]['phases']]
            phases+=c['collection_phases']+source['phases']
            if program!='norm32':phases+=val['base']['phases']
            else:
                floor=read(raw/(cid+'.reference-floor-cost.json'));phase_binding(floor);phases+=floor['phases']
            phase_journal(phases,evs)
            components=dict(auxiliary_construction={}if program=='norm32'else val['base']['counters'],own_prerequisite_and_projection=val['prelude']['counters'],
                own_pair_index_natural=c['collection_counters'],own_AP0_source=source['counters'],own_recipe=val['recipe']['counters'],
                own_full_target_construction=val['construction']['counters'],own_query_cache=val['cache']['counters'],own_native_assembly=val['assembly']['counters'],
                shared_public_target=target['counters'],primary_target_algebra=val['aux_cancel_joint']['counters'])
            paid=dict(sum((Counter(v)for v in components.values()),Counter()))
            cold.append(dict(cell_id=cid,program=program,identified_mask=row['identified_mask'],full_delta=row['full_delta'],components=components,
                physical_engine_counters=paid,single_engine_counters={e:costs.select_engine(paid,e)for e in costs.ENGINES},
                separately_paid_information=val['information']['counters'],separately_paid_native_joint=val['sparse_joint']['counters']))
            if program=='formalpair16':
                own_components=dict(components,primary_target_algebra=val['direct_formal']['counters'])
                own_paid=dict(sum((Counter(v)for v in own_components.values()),Counter()))
                direct_cold.append(dict(cell_id=cid,program=program,algorithm='direct_formal',acquisition_shared_with='formalpair16 auxiliary-first/native views; nonadditive',identified_mask=row['direct_identified_mask'],full_delta=row['full_delta'],components=own_components,physical_engine_counters=own_paid,single_engine_counters={e:costs.select_engine(own_paid,e)for e in costs.ENGINES}))
        cells.append(row)
    complete=bool(execution.get('returncode')==0 and execution.get('timeout')is False and execution.get('exception')is None and execution.get('source_unchanged_after')is True and
        all(v['verified']for v in cells)and (started,finished,failed)==(36,36,0)and not errors)
    engines={e:dict(sum((Counter(costs.engine_arithmetic(v)[e])for v in physical.values()),Counter()))for e in costs.ENGINES}
    if complete and any(Counter(engines[e])!=checked_engines[e]for e in costs.ENGINES):raise ValueError('physical aggregate endpoint engines differ from independent receipts')
    return dict(panel_complete=complete,cells=cells,cold_views=cold,direct_cold_views=direct_cold,physical_counters={k:dict(v)for k,v in physical.items()},observed_algorithm_counters={k:dict(v)for k,v in observed.items()},
        observed_batch_starts=started,observed_completed_batch_calls=finished,observed_failed_batch_calls=failed,closed_checkpoints=checkpoints,errors=errors,
        query_engine_totals=engines,checked_query_engine_totals={e:dict(v)for e,v in checked_engines.items()},generation=generated if generation_valid else None,partial_work_unknown=not complete)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True);args=parser.parse_args()
    rules,protocol=load(INPUTS),load(args.protocol);execution,host=load(args.run/'execution.json'),load(args.run/'host.json')
    data=summarize(args.run,rules,execution);cells=data['cells']
    metrics=dict(schema='prime-field-a22-metrics/v1',panel_complete=data['panel_complete'],physical_attempts=1,planned_systems=16,planned_batch_calls=36,
        verified_systems=sum(v['verified']for v in cells),unknown_systems=sum(not v['verified']for v in cells),columns=COLS,rows=[[v.get(k)for k in COLS]for v in cells],
        source_commit=execution['source_commit'],protocol_sha256=execution['protocol_sha256'],**{k:data[k]for k in ('physical_counters','observed_algorithm_counters','observed_batch_starts','observed_completed_batch_calls','observed_failed_batch_calls','partial_work_unknown')})
    write_once(args.run/'metrics.json',metrics,compact=True)
    analysis=dict(schema='prime-field-a22-analysis/v1',**data,diagnostic_resources=execution,metrics_sha256=digest(args.run/'metrics.json'),
        inference='Fixed four fresh20/21-bit curves/32 targets; four actual additional direct formal calls, four separately paid programs. Delta eliminates auxiliary AND target U. Separate own K and learned increment; named target unit membership. No weighted winner, calibrated runtime/whole-attack gain, novel method, generic advantage or signed independent standing.')
    write_once(args.run/'analysis.json',analysis,compact=True);prior.encode_large(args.run/'analysis.json')
    t=tools();export=t.export_skeleton(protocol,str(args.protocol.resolve()),'local','A22-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor');export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k]for k in export['host']['summary']});export['runs']=[]
    ids={v['id']for v in protocol['metrics']['primary']}
    for cell in cells:
        for arm in ([cell['program'],'joint_on_'+cell['program'],'direct_on_'+cell['program']]if cell['program']=='formalpair16'else[cell['program'],'joint_on_'+cell['program']]):
            counted={k:cell[k]for k in COLS if type(cell.get(k))is int and k in ids}
            if cell['verified']:counted.update({'fr_'+op:cell['solver_counters'][arm].get('Fr.field_'+op,0)for op in ('add','sub','mul','inv')})
            export['runs'].append(t.run_row(run_id='A22-'+str(len(export['runs'])),arm=arm,instance_id=str(cell['case_id']//4),seed=0,replicate=0,warmup=False,
                status='succeeded'if cell['verified']else'timeout'if execution['timeout']else'interrupted',measurements=dict(counted=counted,counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
                isolation=dict(tier=None,contended=None,blockers=['sharedhost']),verification=dict(status='verified'if cell['verified']else'not_run',verifier='producer public geometry/native/dense/cost checks; unverified scientific standing'),
                started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['backend_record']=dict(physical_attempts=1,planned_systems=16,planned_batch_calls=36,verified_systems=metrics['verified_systems'],partial_work_unknown=not data['panel_complete'])
    export['files']=[t.file_entry(args.run,str(p.relative_to(args.run)),'raw')for p in sorted(args.run.rglob('*'))if p.is_file()and p.name!='.gitignore']
    export['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze22.py',args.run.resolve()),sha256=digest(HERE/'analyze22.py'),bytes=(HERE/'analyze22.py').stat().st_size)
    export['analysis']['outputs']=[t.file_entry(args.run,name,'analysis')for name in ('metrics.json','analysis.json')];export['flow']=t.compute_flow(export['runs'])
    errors=t.schema_errors(export,'experiment.export/v1')or t.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export,compact=True);prior.encode_large(args.run/'export.json')
    print(json.dumps(dict(panel_complete=data['panel_complete'],verified_systems=metrics['verified_systems'],batch_calls=data['observed_completed_batch_calls'])))


if __name__=='__main__':main()

"""Bind full program/horizon outputs and costs; preserve partial attempt rows."""
import argparse,json,os
from collections import Counter,defaultdict
from pathlib import Path
from deps16 import costs,commitment
from programs16 import PROGRAMS,rules_for,validate_descriptor
from custody16 import HERE,ROOT,INPUTS,load,write_once,digest,tools,descriptors,methods,arm_id,export_arm
from streams16 import lines
from cold16 import prior,total,collection_view,dominates,ARITHMETIC

COLS=['case_id','cell_id','program','base_arm','target_horizon','source_schedule','source_prefix','target_policy',
      'target_prefix','scope','verified','certificate_checked','base_columns','native_columns','supplied_columns',
      'source_rank','native_source_rank','outside_rank','delta','after_cancellation_rank','identified_targets',
      'identified_mask','source_rows','target_rows','decomposition_rows','knowledge_rows']


def counts_valid(counts):
    return isinstance(counts,dict) and all(type(v)is int and v>=0 for v in counts.values())


def bound(value,check):
    if value is None or check is None or not check.get('verification',{}).get('checked'):return False
    if check['verification'].get('producer_output_sha256')!=commitment(value):
        raise ValueError('full producer output/cost checker commitment differs')
    return True


def phase_binding(value,phase_key='phases',counter_key='counters'):
    if not counts_valid(value[counter_key]) or any(not counts_valid(p['counters']) or p['status']!='complete' or p['wall_valid']is not False for p in value[phase_key]):
        raise ValueError('invalid complete phase/counter record')
    if Counter(total(value[phase_key]))!=Counter(value[counter_key]):raise ValueError('complete phase/counter conservation')
    return True


def pair_cost_binding(collected,proof):
    phases=[p for p in collected['collection_phases'] if p['phase']!='natural_target_queries']
    construction=Counter(total(phases))
    names={'pair_construction','pair_batch_inputs','pair_denominators','pair_batch_inversion',
        'pair_shared_formulas','pair_output_negations','pair_table_materialization'}
    pairs=Counter(total([p for p in phases if p['phase']in names]))
    if construction!=Counter(proof['construction_counters']) or pairs!=Counter(proof['pair_stage_counters']):
        raise ValueError('checked pair construction cost/phase disagreement')
    if any(construction.get(k,0)!=v for k,v in proof['construction_arithmetic'].items()) or any(
        pairs.get(k,0)!=v for k,v in proof['arithmetic'].items()):
        raise ValueError('independent pair arithmetic schedule disagreement')
    return True


def summarize(run,rules,execution):
    raw=run/'raw';plans=dict(descriptors(rules));rows={};cold=[];audits=[];errors=[];curves=[];checkpoints=[]
    physical=defaultdict(Counter);observed=defaultdict(Counter)
    refs={};branch_refs={};branch_checks={};info_refs={};checked_engines={engine:Counter() for engine in costs.ENGINES}
    observed_completed_calls=observed_failed_calls=0
    def read(path):
        try:return prior.optional(path)
        except Exception as error:errors.append(dict(path=str(path),error_type=type(error).__name__,error=str(error)));return None
    def readlines(path):
        try:yield from lines(path)
        except Exception as error:errors.append(dict(path=str(path),error_type=type(error).__name__,error=str(error)))
    start,child,admission=read(run/'checkpoint-admitted-start.json'),read(run/'child.json'),read(raw/'admission.json')
    startup_valid=bool(start and child and admission and admission['returncode']==0 and
        admission['command']==['bash','scripts/checkpoint.sh','gate'] and start['admission_last_push']==admission['last_push'] and
        start['returncode']==0 and start['native_curves_generated']==0 and
        start['command']==['bash','scripts/checkpoint.sh','push'] and start['child_pid']==child['child_pid'] and
        start['child_process_group']==child['child_process_group'] and start['supervisor_pid']==child['supervisor_pid'])
    if not startup_valid:errors.append(dict(error='missing/failed actual admitted-start checkpoint or PID binding'))
    generated,generation=read(raw/'generated.json'),read(raw/'generation-check.json')
    expected_curves=len(rules['fields'])*rules['curves_per_field']
    generation_valid=bool(startup_valid and bound(generated,generation) and generation['verification']['curves']==expected_curves)
    curve_ordinal=0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            curve_ordinal+=1
            cid='p'+str(field['p'])+'-i'+str(ci)
            for event in readlines(raw/(cid+'.events.jsonl')):
                kind=event['kind'];pid=event.get('program')
                if kind=='affine_phase':
                    owner=pid or ('public_base.'+event['public_base_program'] if 'public_base_program'in event else
                        'recipes'+str(event['target_recipe_horizon']) if 'target_recipe_horizon'in event else 'shared')
                    counts=event['phase']['counters']
                    if not counts_valid(counts):raise ValueError('invalid actual phase prefix counters')
                    physical[owner+'.'+event['context'].get('kind','target_construction')].update(counts)
                elif kind=='branch_output':branch_refs[cid,pid,json.dumps(event['context'],sort_keys=True)]=event['record']
                elif kind=='branch_checked':branch_checks[cid,pid,json.dumps(event['context'],sort_keys=True)]=event
                elif kind in ('case_input','case_checked','solver_complete'):
                    label='input' if kind=='case_input' else 'check' if kind=='case_checked' else event['arm']
                    refs[event['case_id'],label]=event['record']
                    if kind=='solver_complete':
                        observed[arm_id(event['descriptor'],event['arm'])].update(event['counters']);observed_completed_calls+=1
                elif kind in ('information_output','information_checked'):
                    info_refs[event['case_id'],'output' if kind=='information_output' else 'check']=event['record']
                elif kind=='solver_failed':
                    observed_failed_calls+=1
                    observed[arm_id(event['descriptor'],event['arm'])].update(total(event['phases']));errors.append(dict(cell_id=cid,event=event))
                elif kind in ('information_failed','failure','horizon_branch_failed'):
                    # Immediate phase prefixes above already include failed work.
                    errors.append(dict(cell_id=cid,event=event))
            preludes={p['id']:read(raw/(cid+'.'+p['id']+'.prelude.json')) for p in PROGRAMS}
            sources={p['id']:read(raw/(cid+'.'+p['id']+'.source.json')) for p in PROGRAMS}
            caches={p['id']:read(raw/(cid+'.'+p['id']+'.query-cache.json')) for p in PROGRAMS}
            built={p['id']:read(raw/(cid+'.'+p['id']+'.base.json')) for p in PROGRAMS if p['base_size']is not None}
            build_checks={pid:read(raw/(cid+'.'+pid+'.base-check.json')) for pid in built}
            checks={p['id']:{suffix:read(raw/(cid+'.'+p['id']+'.'+suffix+'.json')) for suffix in
                    ('prelude-check','source-check','query-check')} for p in PROGRAMS}
            targets,target_check=read(raw/(cid+'.targets.json')),read(raw/(cid+'.targets-check.json'))
            recipes={h:read(raw/(cid+'.target-recipes-h'+str(h)+'.json')) for h in (8,24)}
            recipe_checks={h:read(raw/(cid+'.target-recipes-h'+str(h)+'-check.json')) for h in (8,24)}
            prefix_check=read(raw/(cid+'.target-recipe-prefix-check.json'));complete=read(raw/(cid+'.complete.json'))
            shared_valid=bool(generation_valid and bound(targets,target_check) and
                all(bound(recipes[h],recipe_checks[h]) for h in (8,24)) and prefix_check and prefix_check['verification']['checked'])
            if shared_valid:
                phase_binding(targets)
                for h in (8,24):
                    phase_binding(recipes[h])
                    if recipes[h]['counters'].get('target_recipe_hashes',0)!=recipe_checks[h]['verification']['independent_hashes']:
                        raise ValueError('independent target recipe hash counter disagreement')
            program_valid={}
            for p in PROGRAMS:
                pid=p['id'];pre,source,cache=preludes[pid],sources[pid],caches[pid];cc=checks[pid]
                valid=bool(shared_valid and bound(pre,cc['prelude-check']) and source and
                    bound(source['collection'],cc['source-check']) and bound(cache,cc['query-check']) and
                    (p['base_size']is None or bound(built[pid],build_checks[pid])))
                if valid:
                    phase_binding(pre);phase_binding(source['collection'],'collection_phases','collection_counters');phase_binding(cache)
                    if source['cell']!=pre['cell']:raise ValueError('source/prelude native fixture differs')
                    if p['base_size']is not None:
                        phase_binding(built[pid])
                        if (built[pid]['owner_program']!=pid or built[pid]['target_horizon']!=p['horizon'] or
                            built[pid]['public_base_size']!=p['base_size']):raise ValueError('own public constructor provenance differs')
                    if (pre['program_id']!=pid or source['collection']['program_id']!=pid or cache['owner']['program']!=pid or
                        pre['target_horizon']!=p['horizon'] or cache['owner']['horizon']!=p['horizon']):raise ValueError('program horizon provenance differs')
                    maximum=rules_for(rules,pid)['maximum_target_cache_points']
                    if (cache['owner']['maximum_cache_points']!=maximum or len(cache['records'])>maximum or
                        cache['engine_start']!=len(source['collection']['query_engine_records'])):
                        raise ValueError('program cache cap/engine scope differs')
                    pair_cost_binding(source['collection'],cc['source-check']['verification']['pair_construction'])
                    for engine in costs.ENGINES:
                        checked_engines[engine].update(cc['source-check']['verification']['query_engines']['engine_totals'][engine])
                        checked_engines[engine].update(cc['query-check']['verification']['query_check']['query_engines']['engine_totals'][engine])
                program_valid[pid]=valid
            if all(program_valid.values()) and complete and complete['complete']:
                ordinal=curve_ordinal;expected_cases=ordinal*len(plans)//expected_curves
                if (complete['cases_checked']!=expected_cases or complete['solver_calls']!=2*expected_cases or
                    complete['information_audits']!=ordinal*rules['information_audits']//expected_curves or complete['curve_index']!=ordinal-1):
                    raise ValueError('closed curve complete marker census differs')
                curves.append(dict(cell_id=cid,fixtures={pid:preludes[pid]['cell']['fixture'] for pid in preludes}))
            if rules['closed_curve_checkpoint']:
                receipt=read(run/('checkpoint-'+cid+'.json'));ordinal=len(checkpoints)+1
                valid=prior.checkpoint_valid(receipt,cid,ordinal,ordinal*len(plans)//expected_curves)
                checkpoints.append(dict(cell_id=cid,valid=valid,receipt=receipt))
                if not valid:errors.append(dict(cell_id=cid,error='missing/failed exact closed-curve canonical checkpoint'))
            branches,outputs,checked=(iter(readlines(raw/(cid+'.'+name+'.jsonl'))) for name in ('branches','solver-outputs','case-checks'))
            current=None
            for item in readlines(raw/(cid+'.case-inputs.jsonl')):
                idx,desc=item['case_id'],item['descriptor'];rr=validate_descriptor(rules,desc)
                if plans.get(idx)!=desc or idx in rows:raise ValueError('fixed case descriptor/order')
                pid=desc['program'];context={k:desc[k] for k in ('source_schedule','source_prefix','target_policy')}
                key=(cid,pid,json.dumps(context,sort_keys=True))
                if current is None or current['program']!=pid or current['context']!=context:
                    current=next(branches,None)
                    if current and (current['program']!=pid or current['context']!=context or not prior.record_binding(current,branch_refs.get(key))):
                        raise ValueError('branch program/order/journal binding')
                if current and key in branch_checks and not bound(current['branch'],branch_checks[key]):raise ValueError('branch cost binding')
                if current and key in branch_checks:phase_binding(current['branch'])
                results=[next(outputs,None) for method in methods(desc)];check=next(checked,None)
                certified=bool(current and check and check['case_id']==idx and check['descriptor']==desc and check['verification']['checked'] and
                    all(v and v['case_id']==idx and v['arm']==method for method,v in zip(methods(desc),results,strict=True)))
                valid=bool(certified and program_valid[pid] and key in branch_checks)
                row=dict(case_id=idx,**desc,verified=valid,certificate_checked=certified)
                if certified:
                    for label,value in [('input',item),('check',check),*zip(methods(desc),results,strict=True)]:
                        if not prior.record_binding(value,refs.get((idx,label))):raise ValueError('case stream/journal byte binding')
                    case,info=item['case'],check['verification']['partial']
                    if check['verification']['case_sha256']!=commitment(case):raise ValueError('native case checker commitment')
                    row.update(base_columns=info['original_unknown_columns'],native_columns=case['width'],supplied_columns=info['supplied_columns'],
                        source_rank=info['source_rank'],native_source_rank=info['native_source_rank'],outside_rank=info['outside_rank'],delta=info['delta'],
                        after_cancellation_rank=info['base_rank_after_cancellation'],identified_targets=info['identified'],source_rows=len(case['source']),target_rows=len(case['target']),
                        decomposition_rows=sum(v['kind']=='decomposition' for v in case['target']),knowledge_rows=sum(v['kind']!='decomposition' for v in case['target']),
                        assembly_counters=total(item['shared_phases']),solver_counters={})
                    for method,result in zip(methods(desc),results,strict=True):
                        value=result['result'];phase_binding(value)
                        if check['verification']['solver_output_sha256'][method]!=commitment(value):raise ValueError('full solver cost/output checker binding')
                        mask=sum(1<<v['target_index'] for v in value['recoveries'] if v['identifiable'])
                        if 'identified_mask'in row and row['identified_mask']!=mask:raise ValueError('paired target identity mismatch')
                        row['identified_mask']=mask;row['solver_counters'][method]=value['counters']
                    if valid:
                        view=collection_view(pid,preludes[pid],sources[pid]['collection'],built.get(pid),current['branch'],caches[pid],
                            recipes[desc['target_horizon']],targets,desc['target_prefix'],rr)
                        options={method:{engine:dict(Counter(view['engine_collection_counters'][engine])+Counter(row['assembly_counters'])+
                            Counter(row['solver_counters'][method])) for engine in costs.ENGINES} for method in methods(desc)}
                        cold.append(dict(case_id=idx,descriptor=desc,identified_mask=row['identified_mask'],collection=view,solver_engine_counters=options))
                rows[idx]=row
            information_checks=iter(readlines(raw/(cid+'.information-checks.jsonl')))
            for item in readlines(raw/(cid+'.information.jsonl')):
                idx,norm_idx=item['hybrid_case_id'],item['norm_case_id']
                if not prior.record_binding(item,info_refs.get((idx,'output'))):raise ValueError('information output/journal binding')
                if plans.get(idx)!=item['descriptor'] or plans[idx]['program']!='hybrid8' or plans.get(norm_idx,{}).get('program')!='norm8':
                    raise ValueError('old-coordinate matched case identities')
                if any(plans[idx][k]!=plans[norm_idx][k] for k in plans[idx] if k not in ('base_arm','program')):raise ValueError('matched old coordinates/horizon differ')
                check=next(information_checks,None)
                if check and (check['hybrid_case_id']!=idx or check['norm_case_id']!=norm_idx or check['descriptor']!=item['descriptor'] or not prior.record_binding(check,info_refs.get((idx,'check')))):
                    raise ValueError('information checker stream binding')
                good=bound(item['result'],check);phase_binding(item['result'])
                audits.append(dict(norm_case_id=norm_idx,hybrid_case_id=idx,descriptor=item['descriptor'],
                    verified=bool(good and rows.get(idx,{}).get('verified') and rows.get(norm_idx,{}).get('verified')),
                    certificate_checked=good,ranks=item['result']['ranks'],increments=item['result']['increments'],delta_vs_old=item['result']['delta_vs_old'],
                    outside_rank=item['result']['outside']['rank'],counters=item['result']['counters'],old_kernel_dimension=len(check['verification']['old_kernel']) if good else None))
            if all(program_valid.values()) and any(next(v,None)is not None for v in (branches,outputs,checked,information_checks)):
                raise ValueError('extra records beyond fixed program census')
    cells=[rows.get(idx,dict(case_id=idx,**desc,verified=False,certificate_checked=False)) for idx,desc in plans.items()]
    full=bool(execution['returncode']==0 and not execution['timeout'] and not execution['exception'] and execution['source_unchanged_after'] and
        len(curves)==expected_curves and not errors and all(v['verified'] for v in cells) and len(audits)==rules['information_audits'] and all(v['verified'] for v in audits))
    if len({v['hybrid_case_id'] for v in audits})!=len(audits):raise ValueError('duplicate old-coordinate audit')
    engines={engine:dict(sum((Counter(costs.engine_arithmetic(v)[engine]) for v in physical.values()),Counter())) for engine in costs.ENGINES}
    if full and any(Counter(engines[e])!=checked_engines[e] for e in costs.ENGINES):raise ValueError('physical query counters differ from checked engine receipts')
    return dict(cells=cells,cold_views=cold,information_audits=audits,curves=curves,errors=errors,panel_complete=full,
        physical_counters={k:dict(v) for k,v in physical.items()},observed_arm_counters={k:dict(v) for k,v in observed.items()},
        query_engine_totals=engines,closed_curve_checkpoints=checkpoints,admitted_start_checkpoint=start,
        observed_completed_solver_calls=observed_completed_calls,observed_failed_solver_calls=observed_failed_calls)


def comparisons(cold):
    paired=[]
    for candidate in cold:
        a=candidate['descriptor'];refs=[]
        for reference in cold:
            b=reference['descriptor']
            if (a['cell_id'],a['target_policy'])!=(b['cell_id'],b['target_policy']):continue
            if a['program']=='known48_24':
                take=b['target_prefix']==8 and b['program']in ('known48_8','known32_8','norm8','hybrid8')
            elif a['program']in ('norm8','hybrid8'):
                take=a['target_prefix']==b['target_prefix'] and (b['program']in ('known32_8','known48_8') or
                    a['program']=='hybrid8' and b['program']=='norm8' and all(a[k]==b[k] for k in ('source_schedule','source_prefix','scope')))
            else:take=a['program']=='known48_8' and b['program']=='known32_8' and a['target_prefix']==b['target_prefix']
            if take:refs.append(reference)
        for reference in refs:
            for engine in costs.ENGINES:
                left=dict(identified_mask=candidate['identified_mask'],counters=candidate['solver_engine_counters']['partial_joint'][engine])
                right=dict(identified_mask=reference['identified_mask'],counters=reference['solver_engine_counters']['partial_joint'][engine])
                dimensions=sorted(left['counters'].keys()|right['counters'].keys())
                paired.append(dict(candidate_case_id=candidate['case_id'],reference_case_id=reference['case_id'],query_engine=engine,
                    candidate_mask=left['identified_mask'],reference_mask=right['identified_mask'],
                    candidate_dominates_arithmetic=dominates(left,right,ARITHMETIC),reference_dominates_arithmetic=dominates(right,left,ARITHMETIC),
                    candidate_dominates_retained=dominates(left,right,dimensions),reference_dominates_retained=dominates(right,left,dimensions)))
    return paired


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();rules,protocol=load(INPUTS),load(args.protocol);execution,host=load(args.run/'execution.json'),load(args.run/'host.json')
    data=summarize(args.run,rules,execution);cells=data['cells'];plans=dict(descriptors(rules))
    metrics=dict(schema='prime-field-a16-metrics/v1',panel_complete=data['panel_complete'],physical_attempts=1,
        planned_systems=len(plans),planned_solver_calls=2*len(plans),verified_systems=sum(v['verified'] for v in cells),unknown_systems=sum(not v['verified'] for v in cells),
        verified_solver_calls=2*sum(v['verified'] for v in cells),observed_certified_systems=sum(v['certificate_checked'] for v in cells),
        observed_completed_solver_calls=data['observed_completed_solver_calls'],observed_failed_solver_calls=data['observed_failed_solver_calls'],
        verified_information_audits=sum(v['verified'] for v in data['information_audits']),columns=COLS,rows=[[v.get(k) for k in COLS] for v in cells],
        physical_counters=data['physical_counters'],observed_arm_counters=data['observed_arm_counters'],query_engine_totals=data['query_engine_totals'],
        closed_curve_checkpoints=data['closed_curve_checkpoints'],source_commit=execution['source_commit'],protocol_sha256=execution['protocol_sha256'],partial_work_unknown=not data['panel_complete'])
    write_once(args.run/'metrics.json',metrics,compact=True)
    analysis=dict(schema='prime-field-a16-analysis/v1',**data,matched_comparisons=comparisons(data['cold_views']),diagnostic_resources=execution,
        metrics_sha256=digest(args.run/'metrics.json'),inference='Fresh matched target masks and separately included owned-horizon cold vectors, no endpoint-count equal-cost inference. Target portfolios8/24 independent, same first8 symbolic recipes; no future setup/knowledge/cost. Supplied labels are not learned rank; old-base Delta only after U cancellation on matched norm/hybrid coordinates. Views dependent; generation/hash/pow/Python/NumPy/checker/OS/IO unexpanded, clocks invalid. Producer checks unverified without signed independent replay.')
    write_once(args.run/'analysis.json',analysis,compact=True);prior.encode_large(args.run/'analysis.json')
    t=tools();export=t.export_skeleton(protocol,str(args.protocol.resolve()),'local','A16-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor');export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']});export['runs']=[]
    metric_ids={v['id'] for v in protocol['metrics']['primary']}
    for cell in cells:
        for method in methods(cell):
            counted={k:cell[k] for k in COLS if k in cell and type(cell[k])is int and k in metric_ids}
            if cell['verified']:counted.update({'fr_'+op:cell['solver_counters'][method].get('Fr.field_'+op,0) for op in ('add','sub','mul','inv')})
            export['runs'].append(t.run_row(run_id='A16-'+str(len(export['runs'])),arm=export_arm(method),instance_id=str(cell['case_id']),seed=0,replicate=0,warmup=False,
                status='succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'interrupted',
                measurements=dict(counted=counted,counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
                isolation=dict(tier=None,contended=None,blockers=['sharedhost']),verification=dict(status='verified' if cell['verified'] else 'not_run',verifier='producer plain group/constructor/native/dense checks; no signed standing'),
                started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['backend_record']=dict(physical_attempts=1,planned_systems=len(plans),planned_solver_calls=len(export['runs']),verified_solver_calls=metrics['verified_solver_calls'],
        verified_information_audits=metrics['verified_information_audits'],physical_counters=metrics['physical_counters'],observed_arm_counters=metrics['observed_arm_counters'],partial_work_unknown=not data['panel_complete'])
    export['files']=[t.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file() and p.name!='.gitignore']
    export['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze16.py',args.run.resolve()),sha256=digest(HERE/'analyze16.py'),bytes=(HERE/'analyze16.py').stat().st_size)
    export['analysis']['outputs']=[t.file_entry(args.run,name,'analysis') for name in ('metrics.json','analysis.json')];export['flow']=t.compute_flow(export['runs'])
    errors=t.schema_errors(export,'experiment.export/v1') or t.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export,compact=True);prior.encode_large(args.run/'export.json')
    print(json.dumps(dict(panel_complete=data['panel_complete'],verified_systems=metrics['verified_systems'],verified_solver_calls=metrics['verified_solver_calls'],information_audits=metrics['verified_information_audits'])))


if __name__=='__main__':main()

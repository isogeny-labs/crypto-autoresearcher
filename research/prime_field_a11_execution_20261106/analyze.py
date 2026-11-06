"""Mechanical streamed accounting, compact committed metrics and unified export."""
from collections import Counter
import argparse,gzip,json,os
from pathlib import Path
from common import HERE,ROOT,INPUTS,ARMS,load,digest,write_once,tools
from streaming import lines
COLS=['case_id','cell_id','source_schedule','source_prefix','target_policy','target_prefix','scope','verified','base_columns','source_rank','outside_rank','delta','after_cancellation_rank','identified_targets','identified_mask','source_rows','target_rows','decomposition_rows','knowledge_rows','joint_rank','joint_columns','joint_fr_add','joint_fr_sub','joint_fr_mul','joint_fr_inv','cancel_rank','cancel_columns','cancel_fr_add','cancel_fr_sub','cancel_fr_mul','cancel_fr_inv']

def optional(path):
    path=Path(path)
    if not path.is_file() and not Path(str(path)+'.gz').is_file():return None
    return load(path)
def total(phases):return dict(sum((Counter(p['counters']) for p in phases),Counter()))
def encode_large(path):
    path=Path(path)
    if path.stat().st_size<1048576:return None
    data=path.read_bytes();archive=Path(str(path)+'.gz')
    with archive.open('xb') as f:f.write(gzip.compress(data,compresslevel=6,mtime=0))
    if gzip.decompress(archive.read_bytes())!=data:raise ValueError('derived encoding mismatch')
    ignore=path.parent/'.gitignore';old=ignore.read_text() if ignore.exists() else ''
    line='/'+path.name+'\n'
    if line not in old:ignore.write_text(old+line)
    receipt=dict(original_path=path.name,original_sha256=digest(path),original_bytes=len(data),archive_path=archive.name,archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,encoding='gzip6mtime0; logicalJSON retainedhydrated/ignored')
    write_once(path.parent/'derived-encodings'/(path.stem+'.json'),receipt);return receipt

def descriptors(rules):
    index=0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid='p'+str(field['p'])+'-i'+str(ci)
            for seed in rules['seeds']:
                for factory in ('ap','hash'):
                    for prefix in rules['source_prefixes']:
                        for policy in rules['target_policies']:
                            for budget in rules['target_prefixes']:
                                for scope in rules['scopes']:
                                    yield index,dict(cell_id=cid,source_schedule=factory+str(seed),source_prefix=prefix,target_policy=policy,target_prefix=budget,scope=scope);index+=1

def source_cost(collected,arm,prefix,rules):
    orders=collected['selection']['orders'];phases=collected['collection_phases'];chosen=[]
    for phase in phases:
        name=phase['phase']
        if name=='schedule_derivation':continue
        if not any(name.startswith(a+'_') for a in orders):chosen.append(phase);continue
        if name in (arm+'_label_cache_setup',arm+'_constructor_selection'):chosen.append(phase);continue
        if name.startswith(arm+'_'):
            tail=name[len(arm)+1:];part=tail.split('_',1)[0]
            if part.isdigit() and int(part)<=prefix:chosen.append(phase)
    # Exact logical recipe partition; no invented per-arm clock allocation.
    recipe=Counter()
    for row in collected['selection']['trace']:
        if row['seed']!=int(arm[-1]):continue
        if arm.startswith('ap') and row['kind']=='ap_candidate':recipe['source_hash_attempts']+=2;recipe['ap_horizon_scalar_tests']+=rules['sources']
        if arm.startswith('hash') and row['kind']=='hash_candidate':recipe['source_hash_attempts']+=1
    return dict(Counter(total(chosen))+recipe)

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);a=p.parse_args();rules=load(INPUTS);protocol=load(a.protocol);execution=load(a.run/'execution.json');host=load(a.run/'host.json');raw=a.run/'raw'
    plans=list(descriptors(rules));planned=len(plans);expected_curves=len(rules['fields'])*rules['curves_per_field'];source_schedules=2*len(rules['seeds']);expected=dict(plans);rows={};costs=[];observed={arm:Counter() for arm in ARMS};failed={arm:Counter() for arm in ARMS};physical={k:Counter() for k in ('source','target_recipes','target_queries','target_construction','projection')};journalrefs={};errors=[];checked_curves=[];query_summary=[];curve_info=[]
    def read_optional(path):
        try:return optional(path)
        except Exception as error:errors.append(dict(path=str(path),error_type=type(error).__name__,error=str(error)));return None
    def read_lines(path):
        try:yield from lines(path)
        except Exception as error:errors.append(dict(path=str(path),error_type=type(error).__name__,error=str(error)))
    generation=read_optional(raw/'generation-check.json');generation_valid=generation is not None and generation['verification']['checked']is True and generation['verification']['curves']==expected_curves
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid='p'+str(field['p'])+'-i'+str(ci)
            for event in read_lines(raw/(cid+'.events.jsonl')):
                kind=event['kind']
                if kind=='solver_complete':observed[event['arm']].update(event['counters']);journalrefs[event['case_id'],event['arm']]=event['record']
                elif kind=='solver_failed':failed[event['arm']].update(total(event['phases']));errors.append(dict(cell_id=cid,event=event))
                elif kind=='case_input':physical['projection'].update(total(event['shared_phases']));journalrefs[event['case_id'],'input']=event['record']
                elif kind=='case_checked':journalrefs[event['case_id'],'check']=event['record']
                elif kind=='collection_phase':physical['source'].update(event['phase']['counters'])
                elif kind=='affine_phase':
                    context=event['context'];group='target_recipes' if context.get('kind')=='target_recipes' else 'target_queries' if context.get('kind')=='shared_target_queries' else 'target_construction';physical[group].update(event['phase']['counters'])
                elif kind=='failure':errors.append(dict(cell_id=cid,event=event))
            source=read_optional(raw/(cid+'.source.json'));sourcecheck=read_optional(raw/(cid+'.source-check.json'));cache=read_optional(raw/(cid+'.query-cache.json'));cachecheck=read_optional(raw/(cid+'.query-check.json'));complete=read_optional(raw/(cid+'.complete.json'))
            target_recipe=read_optional(raw/(cid+'.target-recipes.json'))
            curve_valid=bool(source and cache and target_recipe and generation_valid and sourcecheck and sourcecheck['verification']['checked'] and cachecheck and cachecheck['verification']['checked'] and complete and complete['complete'])
            if curve_valid:checked_curves.append(cid)
            if not source:continue
            cell=source['cell'];col=source['collection'];curve_info.append(dict(cell_id=cid,fixture=cell['fixture'],base_columns=col['projection']['U']))
            if cache:
                if total(cache['phases'])!=cache['counters']:raise ValueError('global target cache phase conservation')
                query_summary.append(dict(cell_id=cid,physical_cached_points=len(cache['records']),queries=cache['counters'].get('target_queries',0)+col['collection_counters'].get('target_queries',0),logical_requests=cache['counters'].get('logical_target_requests',0)))
            branches=iter(read_lines(raw/(cid+'.branches.jsonl')));inputs=iter(read_lines(raw/(cid+'.case-inputs.jsonl')));outputs=iter(read_lines(raw/(cid+'.solver-outputs.jsonl')));checks=iter(read_lines(raw/(cid+'.case-checks.jsonl')))
            qphases={} if not cache else {v['phase']:v['counters'] for v in cache['phases']};current_branch=None
            for item in inputs:
                idx=item['case_id'];desc=item['descriptor']
                if expected.get(idx)!=desc:raise ValueError('fixed case descriptor/order')
                context=dict(source_schedule=desc['source_schedule'],source_prefix=desc['source_prefix'],target_policy=desc['target_policy'])
                if current_branch is None or current_branch['context']!=context:
                    entry=next(branches,None);current_branch=None if entry is None else entry['branch']
                    if current_branch is not None and current_branch['context']!=context:raise ValueError('branch stream order')
                result=[next(outputs,None),next(outputs,None)];checked=next(checks,None)
                valid=bool(curve_valid and current_branch and all(v is not None and v['case_id']==idx and v['arm']==arm for v,arm in zip(result,ARMS,strict=True)) and checked and checked['case_id']==idx and checked['verification']['checked'])
                row=dict(case_id=idx,**desc,verified=valid)
                if valid:
                    # Bind the exact append-only stream objects to the journal receipts.
                    import hashlib
                    for label,value in [('input',item),('check',checked),*[(arm,value) for arm,value in zip(ARMS,result,strict=True)]]:
                        encoded=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode();ref=journalrefs.get((idx,label))
                        if not ref or ref['sha256']!=hashlib.sha256(encoded).hexdigest() or ref['bytes']!=len(encoded):raise ValueError('stream/journal digest')
                    info=checked['verification'];case=item['case'];row.update(base_columns=case['width'],source_rank=info['source_rank'],outside_rank=info['outside_rank'],delta=info['delta'],after_cancellation_rank=info['base_rank_after_cancellation'],identified_targets=info['identified'],source_rows=len(case['source']),target_rows=len(case['target']),decomposition_rows=sum(v['kind']=='decomposition' for v in case['target']),knowledge_rows=sum(v['kind']!='decomposition' for v in case['target']))
                    summaries={}
                    for arm,value in zip(ARMS,result,strict=True):
                        value=value['result'];counts=value['counters']
                        if total(value['phases'])!=counts:raise ValueError('solver phase conservation')
                        short='joint' if arm=='sparse_joint' else 'cancel';row[short+'_rank']=value['system']['rank'];row[short+'_columns']=value['system']['columns']
                        for key in ('add','sub','mul','inv'):row[short+'_fr_'+key]=counts.get('Fr.field_'+key,0)
                        mask=sum(1<<v['target_index'] for v in value['recoveries'] if v['identifiable'])
                        if 'identified_mask'in row and row['identified_mask']!=mask:raise ValueError('paired target identities differ')
                        row['identified_mask']=mask;summaries[arm]=counts
                    if desc['scope']=='relations' and cache:
                        budget=next(v for v in current_branch['budgets'] if v['target_prefix']==desc['target_prefix']);query_ids=sorted({v['query_id'] for v in current_branch['requests'] if v['step']<=desc['target_prefix']});new_ids=[v for v in query_ids if not cache['records'][v]['seeded_natural']];query_cost=Counter()
                        for qid in new_ids:
                            for name in cache['records'][qid]['phase_ids']:query_cost.update(qphases[name])
                        sharedcache=Counter()
                        for name in ('target_query_cache_setup','natural_decomposition_cache_seed'):sharedcache.update(qphases[name])
                        recipe_count=0 if desc['target_policy']=='walk' else sum((1 if v['policy']=='hash_offset' else 2) for v in target_recipe['selection']['trace'] if v['policy']==desc['target_policy'])
                        counters=Counter(source_cost(col,desc['source_schedule'],desc['source_prefix'],rules))+Counter(budget['counters'])+query_cost+sharedcache+Counter(target_recipe_hashes=recipe_count)
                        costs.append(dict(cell_id=cid,context=context,target_prefix=desc['target_prefix'],query_ids=query_ids,new_physical_query_references=new_ids,cold_collection_counters=dict(counters),branch_counters=budget['counters'],source_counters=source_cost(col,desc['source_schedule'],desc['source_prefix'],rules),additional_query_counters=dict(query_cost),logical_requests=rules['targets']*desc['target_prefix'],derived_cold_cache_hits=rules['targets']*desc['target_prefix']-len(new_ids),scope='Cold many-target constructor/collector vector references, including exact per-arm recipe partition. No invented replay or clock. Source fixture generation legacy counts and projection/chosen solver remain separate.'))
                    row['solver_counters']=summaries
                rows[idx]=row
    cells=[]
    for idx,desc in plans:cells.append(rows.get(idx,dict(case_id=idx,**desc,verified=False)))
    full=bool(execution['returncode']==0 and not execution['timeout'] and not execution['exception'] and execution['source_unchanged_after'] and len(checked_curves)==expected_curves and not errors and all(v['verified'] for v in cells))
    if full:
        expected_views=planned//len(rules['scopes'])
        expected_sources=sum(2*v['base_size'] for v in rules['fields'])*rules['curves_per_field']*source_schedules*rules['sources']
        expected_pairs=sum(2*v['base_size']*(v['base_size']-1) for v in rules['fields'])*rules['curves_per_field']
        expected_requests=expected_curves*source_schedules*len(rules['source_prefixes'])*len(rules['target_policies'])*rules['targets']*rules['target_queries_per_point']
        maximum_queries=sum(2*v['base_size'] for v in rules['fields'])*rules['curves_per_field']*rules['targets']*(1+len(rules['target_policies'])*(rules['target_queries_per_point']-1))
        if len(costs)!=expected_views or physical['source'].get('source_queries')!=expected_sources or physical['source'].get('pair_table_insertions')!=expected_pairs:raise ValueError('complete physical census')
        if sum(v['logical_requests'] for v in query_summary)!=expected_requests or sum(v['queries'] for v in query_summary)>maximum_queries:raise ValueError('physical endpoint alias budget')
    metric_rows=[[c.get(k) for k in COLS] for c in cells];metrics=dict(schema='prime-field-a11-metrics/v1',panel_complete=full,physical_attempts=1,planned_systems=planned,planned_solver_calls=2*planned,verified_systems=sum(v['verified'] for v in cells),columns=COLS,rows=metric_rows,source_commit=execution['source_commit'],protocol_sha256=execution['protocol_sha256'],physical_counters={k:dict(v) for k,v in physical.items()},query_summary=query_summary,observed_arm_counters={a:dict(observed[a]+failed[a]) for a in ARMS},partial_work_unknown=not full or bool(errors))
    write_once(a.run/'metrics.json',metrics,compact=True)
    summary=dict(schema='prime-field-a11-analysis/v1',panel_complete=full,physical_attempts=1,verified_systems=metrics['verified_systems'],verified_solver_calls=2*metrics['verified_systems'],unknown_systems=planned-metrics['verified_systems'],cells=cells,cold_collection_views=costs,physical_counters=metrics['physical_counters'],observed_arm_counters=metrics['observed_arm_counters'],failed_arm_phase_counters={a:dict(v) for a,v in failed.items()},partial_work_unknown=metrics['partial_work_unknown'],query_summary=query_summary,curves=curve_info,generation_check=generation,errors=errors,diagnostic_resources=execution,metrics_sha256=digest(a.run/'metrics.json'),cost_scope='Separate Fp/Fr/group/logical vectors; actual physical work disjoint and cold views reference shared deterministic point queries, never extra executions/clocks. Legacy fixture/rejection/checker/OS/pow internals not fully primitive-expanded. No complete calibrated whole-attack cost or signed replay standing.')
    write_once(a.run/'analysis.json',summary,compact=True);encode_large(a.run/'analysis.json')
    t=tools();e=t.export_skeleton(protocol,str(a.protocol.resolve()),'local','A11-'+a.run.name);e['producer']=dict(runtime='codex',model=None,session=None,role='executor');e['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty']);e['host'].update(path='host.json',sha256=digest(a.run/'host.json'),summary={k:host[k] for k in e['host']['summary']});e['runs']=[];keys=[v['id'] for v in protocol['metrics']['primary']]
    for c in cells:
        for arm in ARMS:
            counted={k:c[k] for k in keys if k in c and c[k]is not None};short='joint' if arm=='sparse_joint' else 'cancel'
            if c['verified']:
                for key in ('add','sub','mul','inv'):counted['fr_'+key]=c[short+'_fr_'+key]
            e['runs'].append(t.run_row(run_id='A11-'+arm+'-'+str(c['case_id']),arm=arm,instance_id=str(c['case_id']),seed=0,replicate=0,warmup=False,status='succeeded' if c['verified'] else 'timeout' if execution['timeout'] else 'interrupted',measurements=dict(counted=counted,counters={},wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),isolation=dict(tier=None,contended=None,blockers=['sharedhost']),verification=dict(status='verified' if c['verified'] else 'not_run',verifier='producer independent-arithmetic/dense/oracle code; no signed standing'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    for arm in e['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    e['backend_record']=dict(physical_attempts=1,systems_verified=metrics['verified_systems'],solver_calls_verified=2*metrics['verified_systems'],physical_counters=metrics['physical_counters'],observed_arm_counters=metrics['observed_arm_counters'],partial_work_unknown=metrics['partial_work_unknown'],wall_valid=False,diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')})
    e['files']=[t.file_entry(a.run,str(path.relative_to(a.run)),'raw') for path in sorted(a.run.rglob('*')) if path.is_file() and path.name!='.gitignore'];e['analysis']['script']=dict(path=os.path.relpath(HERE/'analyze.py',a.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size);e['analysis']['outputs']=[t.file_entry(a.run,name,'analysis') for name in ('analysis.json','metrics.json')];e['flow']=t.compute_flow(e['runs'])
    errs=t.schema_errors(e,'experiment.export/v1') or t.lint_export(e,protocol,a.run,True)
    if errs:raise ValueError(json.dumps(errs))
    write_once(a.run/'export.json',e,compact=True);encode_large(a.run/'export.json');print(json.dumps(dict(complete=full,verified_systems=metrics['verified_systems'],unknown_systems=summary['unknown_systems'],metrics_bytes=(a.run/'metrics.json').stat().st_size,query_summary=query_summary)))
if __name__=='__main__':main()

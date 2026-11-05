"""Export only retained records; do not generate scientific inputs or queries."""
import argparse
from collections import Counter
import gzip
import importlib.util
import json
import os
from pathlib import Path
from common import HERE,ROOT,INPUTS,ARMS,digest,write_once,export_cell

def load(path):
    candidates=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(candidates)>1:raise ValueError('ambiguous retained encoding')
    if not candidates:return None
    with (gzip.open(candidates[0],'rt') if candidates[0].suffix=='.gz' else candidates[0].open()) as stream:return json.load(stream)

def phases(values):
    total=Counter()
    if len({v['phase'] for v in values})!=len(values):raise ValueError('duplicate disjoint phase')
    for v in values:
        if v['status']!='complete' or v['wall_valid']is not False:raise ValueError('invalid phase status')
        if any(type(x)is not int or x<0 for x in v['counters'].values()):raise ValueError('invalid counter')
        total.update(v['counters'])
    return dict(total)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True);a=p.parse_args()
    rules=load(INPUTS);protocol=load(a.protocol);execution=load(a.run/'execution.json');host=load(a.run/'host.json');cells=[];costs=[];checks=[]
    for ci,cell in enumerate(rules['cells']):
        stem=cell['id'];value=load(a.run/'raw'/(stem+'.json'));snapshot=load(a.run/'raw'/(stem+'.collection.json'));verification=load(a.run/'raw'/(stem+'.verification.json'))
        checked={};journal=a.run/'raw'/(stem+'.events.jsonl');events=[]
        if journal.is_file():events=[json.loads(line) for line in journal.read_text().splitlines()]
        elif Path(str(journal)+'.gz').is_file():events=[json.loads(line) for line in gzip.decompress(Path(str(journal)+'.gz').read_bytes()).decode().splitlines()]
        if value:
            if value['cell_id']!=stem or value['inputs_sha256']!=digest(INPUTS) or value['complete']is not True or value['projection']!=cell['projection'] or value['target_generation']!=cell['target_generation']:raise ValueError('result identity differs')
            if not snapshot or {k:v for k,v in value.items() if k not in ('prefixes','total_counters')}!={k:v for k,v in snapshot.items() if k not in ('prefixes','total_counters')}:raise ValueError('immutable collection differs')
            if phases(value['collection_phases'])!=value['collection_counters'] or phases(value['collection_phases']+[q for rec in value['prefixes'] for q in rec['phases']])!=value['total_counters']:raise ValueError('phase conservation differs')
            for arm in ARMS:
                rows=[e['row'] for e in events if e.get('kind')=='source_accepted' and e['arm']==arm]
                key=lambda row:(row['source_scalar'],row['triple'],row['signs'])
                if sorted(rows,key=key)!=value['arms'][arm]['rows']:raise ValueError('source journal incomplete')
                blocks=[{k:v for k,v in e.items() if k not in ('kind','target','arm')} for e in events if e.get('kind')=='query_complete' and e['arm']==arm]
                if blocks!=value['arms'][arm]['status_blocks']:raise ValueError('query journal incomplete')
            target=[{k:v for k,v in e.items() if k not in ('kind','target','arm')} for e in events if e.get('kind')=='query_complete' and e['target']]
            if target!=value['target_collection']['status_blocks']:raise ValueError('target query journal incomplete')
            if verification:
                if verification.get('checked')is not True or verification.get('complete_sum_oracle')is not True:raise ValueError('false verification')
                checked={(v['arm'],v['prefix'],v['scope']):v for v in verification['prefixes']}
                if len(checked)!=72:raise ValueError('incomplete verification scope')
            costs.append(dict(cell_id=stem,phase_records_path='raw/'+stem+('.json' if (a.run/'raw'/(stem+'.json')).is_file() else '.json.gz'),collection_counters=value['collection_counters'],total_counters=value['total_counters']))
            oldpath=ROOT/cell['a6_final_path']
            if digest(oldpath)!=cell['a6_final_sha256']:raise ValueError('parent A6bytes differ')
            old=load(oldpath)
            for arm in ARMS:
                original=old['selection']['schedules'][arm]
                if value['selection']['schedules'][arm][:64]!=original or [row for row in value['arms'][arm]['rows'] if row['source_scalar'] in original]!=old['arms'][arm]['rows']:raise ValueError('A6 first64source control differs')
            if value['target_collection']['rows']!=old['target_collection']['rows']:raise ValueError('A6 target rows differ')
            for rec in value['prefixes']:
                if rec['prefix']==64:
                    prior=next(v for v in old['prefixes'] if v['prefix']==64 and v['arm']==rec['arm'] and v['scope']==rec['scope'])
                    for k in ('base','joint','singles','joint_recoveries','outside_target_rank','base_rank_after_target_cancellation','target_base_rank_gain','distinct_equations'):
                        if rec[k]!=prior[k]:raise ValueError('A6budget64 control differs: '+k)
        records={} if value is None else {(v['arm'],v['prefix'],v['scope']):v for v in value['prefixes']}
        for arm in ARMS:
            for count in rules['prefixes']:
                for scope in ('relations','anchors'):
                    rec=records.get((arm,count,scope));summary=checked.get((arm,count,scope));verified=rec is not None and summary is not None
                    entry=dict(cell_id=stem,instance_id=str(ci),arm=arm,prefix=count,scope=scope,verified=verified,status='verified' if verified else 'unknown')
                    if verified:
                        if any(rec['base'][k]!=summary['base_'+k] for k in ('rank','nullity')):raise ValueError('checked rank summary differs')
                        entry.update(summary)
                        entry['anchor_gain']=summary['anchor_augmented_rank']-summary['relation_rank']
                        entry['joint_base_nullity']=summary['base_columns']-summary['base_rank_after_target_cancellation']
                        bc=rec['budget_costs'];construct=bc['construction']['counters']
                        entry.update(construction_scalar_multiplications=construct.get('source_scalar_multiplications',0),construction_cache_hits=construct.get('source_point_cache_hits',0),construction_field_multiplications=construct.get('Fp.field_mul',0),construction_group_additions=construct.get('Fp.group_add',0),prerequisite_scalar_multiplications=bc['prerequisite']['counters']['prerequisite_scalar_multiplications'],source_queries=bc['queries']['counters'].get('source_queries',0))
                    cells.append(entry)
        checks.append(dict(cell_id=stem,checked=False if verification is None else verification['checked'],verification_path='raw/'+stem+'.verification.json'))
    complete=execution['returncode']==0 and execution['source_unchanged_after'] and not execution['timeout'] and not execution['exception'] and all(c['verified'] for c in cells)
    analysis=dict(schema='a7-source-control-analysis/v1',cells=cells,panel_complete=complete,unknown_cells=sum(not c['verified'] for c in cells),independent_checks=checks,physical_cost_records=costs,a6_budget64_control=complete,
        physical_work_coverage=dict(coverage='finalized_cells_only',finalized_cells=len(costs),total_cells=len(rules['cells']),partial_work_unknown=len(costs)<len(rules['cells']),note='Subtotals omit unfinalized work; missing cells are not zero-work observations.'),
        physical_work=dict(source_queries=sum(v['total_counters'].get('source_queries',0) for v in costs),target_queries=sum(v['total_counters'].get('target_queries',0) for v in costs),pair_entries=sum(v['total_counters'].get('pair_table_insertions',0) for v in costs)),
        cost_scope='Oneprocess,4sharedtables/targetstreams,16executedsource schedules,288scope analyses. Disjoint phases once; no summing cumulative/inclusive clocks or overlapping Fp/Fr/group/logical units.')
    write_once(a.run/'analysis.json',analysis)
    spec=importlib.util.spec_from_file_location('_a7_protocol_tools',ROOT/'tools/experiment_protocol.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export=tools.export_skeleton(protocol,str(a.protocol.resolve()),'local','A7-'+a.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor');export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(a.run/'host.json'),summary={k:host[k] for k in export['host']['summary']});export['runs']=[]
    keys=[v['id'] for v in protocol['metrics']['primary']]
    for c in cells:
        counters={}
        if c['arm']=='window' and c['prefix']==0 and c['scope']=='relations':
            cost=next((v for v in costs if v['cell_id']==c['cell_id']),None)
            if cost:
                native=load(a.run/'raw'/(c['cell_id']+'.json'));counters=native['collection_counters']
        instance,seed=export_cell(int(c['instance_id']),c['prefix'],c['scope'],c['arm'],rules['prefixes'])
        export['runs'].append(tools.run_row(run_id='A7-'+a.run.name+'-'+c['cell_id']+'-'+c['arm']+'-'+str(c['prefix'])+'-'+c['scope'],arm=c['arm'],instance_id=instance,seed=seed,replicate=0,warmup=False,
            status='succeeded' if c['verified'] else 'timeout' if execution['timeout'] else 'interrupted',measurements=dict(counted={k:c[k] for k in keys if k in c},counters=counters,wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['shared managed workstation; diagnostic clocks']),verification=dict(status='verified' if c['verified'] else 'not_run',verifier='Separate complete hash/sum/table/query/anchor/dense-affine/weight checks'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner']))
    export['backend_record']=dict(physical_executions=1,physical_work=analysis['physical_work'],physical_cost_records='analysis.json physical_cost_records',wall_valid=False,shared_diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')})
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files']=[tools.file_entry(a.run,str(path.relative_to(a.run)),'raw') for path in sorted(a.run.rglob('*')) if path.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',a.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size));export['analysis']['outputs']=[tools.file_entry(a.run,'analysis.json','analysis')];export['flow']=tools.compute_flow(export['runs'])
    errors=tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,a.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(a.run/'export.json',export);print(json.dumps(dict(complete=complete,scope_records=len(cells),unknown=analysis['unknown_cells'])))

if __name__=='__main__':main()

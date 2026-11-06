"""Admitted fresh affine-target panel; stream every input/output before its check."""
import argparse,json
from pathlib import Path
from time import perf_counter,process_time
from contextlib import ExitStack
import affine_core as core
import affine_solver as solver
import affine_check,check_source,batch_check
from check_solver import check
from common import ROOT,SOURCES,PARAMETERS,load,write_once,systems
from streaming import append,close_encodings,checkpoint_curve
from crypto_autoresearcher.index_calculus.execution_gate import admit

def main():
    p=argparse.ArgumentParser()
    for n in ('inputs','protocol','release','out'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise ValueError('fresh output required')
    if core.PARAMETERS!=PARAMETERS:raise ValueError('native/admin parameter drift')
    admission=admit(ROOT,a.protocol,a.inputs,SOURCES,PARAMETERS,a.release)
    rules=load(a.inputs)
    if systems(rules)!=PARAMETERS['systems']:raise ValueError('case grid differs')
    a.out.mkdir(parents=True);write_once(a.out/'admission.json',admission)
    with (a.out/'generation.events.jsonl').open('x') as stream:
        def event(v):append(stream,v)
        try:
            generated=core.generate(rules,event,core._NATIVE_CAPABILITY);write_once(a.out/'generated.json',generated)
            wall,cpu=perf_counter(),process_time();verified=check_source.check_generation(rules,generated)
            verified['field_prime_selection']=batch_check.field_selection(rules,generated)
            write_once(a.out/'generation-check.json',dict(verification=verified,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
        except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    count=0;curves=0
    for cell in generated['cells']:
        cid=cell['id']
        with ExitStack() as stack:
            events=stack.enter_context((a.out/(cid+'.events.jsonl')).open('x'));branchstream=stack.enter_context((a.out/(cid+'.branches.jsonl')).open('x'));inputstream=stack.enter_context((a.out/(cid+'.case-inputs.jsonl')).open('x'));outputstream=stack.enter_context((a.out/(cid+'.solver-outputs.jsonl')).open('x'));checks=stack.enter_context((a.out/(cid+'.case-checks.jsonl')).open('x'))
            def event(v):append(events,v)
            try:
                collected=core.collect_sources(cell,rules,event,core._NATIVE_CAPABILITY);write_once(a.out/(cid+'.source.json'),dict(cell=cell,collection=collected),compact=True)
                wall,cpu=perf_counter(),process_time();sourcecheck,triple_oracle=check_source.collection(cell,rules,collected)
                sourcecheck['query_engines']=batch_check.records(cell,collected['query_engine_records'],[(None if t['point'] is None else t['point']) for t in collected['target_generation']['targets']]+[v['point'] for arm in collected['selection']['orders'] for v in collected['arms'][arm]['sources']])
                write_once(a.out/(cid+'.source-check.json'),dict(verification=sourcecheck,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
                group_oracle=affine_check.GroupOracle(cell['fixture'],collected['target_generation']['targets']);recipe_meter=core.ProgressMeter(cell['fixture'],event,dict(kind='target_recipes'))
                selection=recipe_meter.stage('target_recipes',lambda:core.recipes(cell,collected,rules,recipe_meter,event,core._NATIVE_CAPABILITY));write_once(a.out/(cid+'.target-recipes.json'),dict(selection=selection,phases=recipe_meter.phases,counters=recipe_meter.counters()))
                affine_check.recipes(cell,rules,selection);cache=core.QueryCache(cell,collected,rules,event,core._NATIVE_CAPABILITY)
                for arm in [kind+str(seed) for seed in rules['seeds'] for kind in ('ap','hash')]:
                    for source_prefix in rules['source_prefixes']:
                        for policy in rules['target_policies']:
                            context=dict(source_schedule=arm,source_prefix=source_prefix,target_policy=policy);event(dict(kind='branch_started',context=context))
                            branch=core.construct_branch(cell,collected,rules,selection['policies'][policy],arm,source_prefix,policy,cache,event,core._NATIVE_CAPABILITY)
                            receipt=append(branchstream,dict(context=context,branch=branch));event(dict(kind='branch_output',context=context,record=receipt))
                            wall,cpu=perf_counter(),process_time();verified=affine_check.branch(cell,collected,rules,selection['policies'][policy],branch,cache,group_oracle)
                            event(dict(kind='branch_checked',context=context,verification=verified,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
                            for target_prefix in rules['target_prefixes']:
                                for scope in rules['scopes']:
                                    desc=dict(cell_id=cid,source_schedule=arm,source_prefix=source_prefix,target_policy=policy,target_prefix=target_prefix,scope=scope);event(dict(kind='case_started',case_id=count,descriptor=desc))
                                    met=solver.Meter(cell['fixture']);case=met.stage('shared_projection',lambda:core.case_input(cell,collected,branch,cache,target_prefix,scope,met));receipt=append(inputstream,dict(case_id=count,descriptor=desc,case=case,shared_phases=met.phases));event(dict(kind='case_input',case_id=count,record=receipt,shared_phases=met.phases));results=[]
                                    for method in ('sparse_joint','sparse_cancel'):
                                        m=solver.Meter(cell['fixture']);result=None
                                        try:
                                            result=solver.solve(case,method,m)
                                            def public():
                                                for record,target in zip(result['recoveries'],case['targets'],strict=True):
                                                    if record['identifiable']:
                                                        if not m.equal(m.e.mul(record['scalar'],tuple(cell['fixture']['P'])),tuple(target['point'])):raise ValueError('public target equation')
                                                        m.other['public_target_certificates_verified']+=1
                                            m.stage('public_target_verification',public);result['phases']=list(m.phases);result['counters']=solver.counters(m.phases)
                                            receipt=append(outputstream,dict(case_id=count,arm=method,result=result));event(dict(kind='solver_complete',case_id=count,arm=method,record=receipt,counters=result['counters']));results.append(result)
                                        except BaseException as error:event(dict(kind='solver_failed',case_id=count,arm=method,phases=m.phases,partial_result=result,error_type=type(error).__name__,error=str(error)));raise
                                    wall,cpu=perf_counter(),process_time();expected=affine_check.expected_case(cell,collected,branch,cache,target_prefix,scope)
                                    if core.source.code(case)!=core.source.code(expected):raise ValueError('independent affine projection')
                                    verified=check(case,results,cell['fixture']);receipt=append(checks,dict(case_id=count,descriptor=desc,verification=verified,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False));event(dict(kind='case_checked',case_id=count,record=receipt,verification=verified));count+=1
                write_once(a.out/(cid+'.query-cache.json'),dict(records=cache.records,engine_records=cache.engines.records[cache.engine_start:],phases=cache.meter.phases,counters=cache.meter.counters()),compact=True)
                wall,cpu=perf_counter(),process_time();verified=affine_check.query_cache(cell,collected,cache,triple_oracle)
                verified['query_engines']=batch_check.records(cell,cache.engines.records[cache.engine_start:],[v['point'] for v in cache.records if not v['seeded_natural']],start=cache.engine_start)
                write_once(a.out/(cid+'.query-check.json'),dict(verification=verified,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False));write_once(a.out/(cid+'.complete.json'),dict(complete=True,cases_checked=count,curve_index=curves,query_check=verified))
            except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
        # All curve writers are closed; checkpoint closed bytes, never a growing journal.
        curves+=1;close_encodings(a.out,cid)
        if rules['closed_curve_checkpoint']:checkpoint_curve(a.out.parent,cid,count,curves)
    if count!=rules['systems']:raise ValueError('incomplete fixed census')
    print(json.dumps(dict(complete=True,systems=count,solver_calls=count*2,physical_processes=1,closed_curve_checkpoints=curves,software_control=rules.get('software_control',False))))
if __name__=='__main__':main()

"""One normally admitted fresh five-program8/24-horizon attempt, no retries."""
import argparse
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter,process_time
from deps16 import core,solver,NATIVE_CAPABILITY,public_base,old_check,checker,check_source
from deps16 import native_case,partial_solver,check_partial,known_checks,information,check_information,commitment
import collection16,branch16,checks16
from ownership16 import OwnedTargetCache
from programs16 import PROGRAMS,rules_for,recipe_prefix
from custody16 import ROOT,SOURCES,PARAMETERS,load,write_once,descriptors,methods,validate_rules
from streams16 import append,close_encodings,checkpoint_curve,admitted_start
from driver14 import public_verify
from crypto_autoresearcher.index_calculus.execution_gate import admit


def timed(operation):
    wall,cpu=perf_counter(),process_time();value=operation()
    return dict(verification=value,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise ValueError('fresh raw output required')
    admission=admit(ROOT,args.protocol,args.inputs,SOURCES,PARAMETERS,args.release)
    rules=load(args.inputs);validate_rules(rules);plans=dict(descriptors(rules))
    if len(plans)!=rules['systems'] or 2*len(plans)!=rules['solver_calls']:raise ValueError('fixed program census')
    args.out.mkdir(parents=True);write_once(args.out/'admission.json',admission)
    # No curve writer exists during this real admitted-start checkpoint.
    admitted_start(args.out.parent,admission)
    with (args.out/'generation.events.jsonl').open('x') as journal:
        emit=lambda value:append(journal,value)
        try:
            generated=core.generate(rules,emit,core._NATIVE_CAPABILITY)
            write_once(args.out/'generated.json',generated)
            def generation_check():
                value=check_source.check_generation(rules,generated)
                from shared import batch_check
                value['field_prime_selection']=batch_check.field_selection(rules,generated)
                value['producer_output_sha256']=commitment(generated)
                return value
            write_once(args.out/'generation-check.json',timed(generation_check))
        except BaseException as error:
            emit(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    count=calls=audits=curves=0
    for original in generated['cells']:
        cid=original['id']
        with ExitStack() as stack:
            streams={name:stack.enter_context((args.out/(cid+'.'+name+'.jsonl')).open('x')) for name in
                ('events','branches','case-inputs','solver-outputs','case-checks','information','information-checks')}
            event=lambda value:append(streams['events'],value)
            try:
                built={};prepared={}
                # Every actual public base constructor precedes target selection.
                for p in PROGRAMS:
                    if p['base_size']is None:continue
                    rr=rules_for(rules,p['id'])
                    emit=lambda value,p=p:event(dict(public_base_program=p['id'],public_base_size=p['base_size'],**value))
                    value=public_base.build(original,rr,p['base_size'],emit,NATIVE_CAPABILITY)
                    value=dict(value,owner_program=p['id'],target_horizon=p['horizon'])
                    built[p['id']]=value
                    write_once(args.out/(cid+'.'+p['id']+'.base.json'),value,compact=True)
                    write_once(args.out/(cid+'.'+p['id']+'.base-check.json'),
                        timed(lambda p=p,rr=rr:checks16.public_base(original,rr,p['id'],built[p['id']])))
                if built['known48_8']['cell']!=built['known48_24']['cell'] or built['known48_8']['knowledge']!=built['known48_24']['knowledge']:
                    raise ValueError('independent identical-size public base recipe differs')
                for p in PROGRAMS:
                    pid=p['id'];rr=rules_for(rules,pid)
                    emit=lambda value,p=p:event(dict(program=p['id'],base_arm=p['base'],**value))
                    helper=built[pid] if p['base']=='hybrid' else None
                    prep=(collection16.prepare(original,rr,helper,emit,NATIVE_CAPABILITY) if p['source'] else
                          collection16.prepare_known(built[pid],rr,emit,NATIVE_CAPABILITY))
                    prepared[pid]=prep
                    write_once(args.out/(cid+'.'+pid+'.prelude.json'),prep,compact=True)
                    def prelude_check(p=p,rr=rr,helper=helper,prep=prep):
                        check=(old_check.preparation(original,rr,helper,prep) if p['source'] else
                               old_check.known_preparation(original,rr,built[p['id']],prep))
                        return dict(checked=True,program=p['id'],plain_group=check,producer_output_sha256=commitment(prep))
                    write_once(args.out/(cid+'.'+pid+'.prelude-check.json'),timed(prelude_check))
                target_meter=core.ProgressMeter(original['fixture'],event,dict(kind='shared_public_targets'))
                targets=target_meter.stage('target_generation',lambda:core.old.targets(original,rules,target_meter,event))
                target_payload=dict(generation=targets,phases=target_meter.phases,counters=target_meter.counters())
                write_once(args.out/(cid+'.targets.json'),target_payload)
                def target_check():
                    value=old_check.targets(original,rules,targets)
                    value['producer_output_sha256']=commitment(target_payload);return value
                write_once(args.out/(cid+'.targets-check.json'),timed(target_check))
                recipes={}
                for horizon,representative in ((8,'norm8'),(24,'known48_24')):
                    rr=rules_for(rules,representative)
                    emit=lambda value,horizon=horizon:event(dict(target_recipe_horizon=horizon,**value))
                    meter=core.ProgressMeter(original['fixture'],emit,dict(kind='target_recipes',target_horizon=horizon))
                    recipe=meter.stage('target_recipes',lambda:core.recipes(original,dict(target_generation=targets),rr,meter,emit,core._NATIVE_CAPABILITY))
                    recipes[horizon]=recipe
                    recipe_payload=dict(selection=recipe,phases=meter.phases,counters=meter.counters())
                    write_once(args.out/(cid+'.target-recipes-h'+str(horizon)+'.json'),recipe_payload)
                    def recipe_check(recipe=recipe,rr=rr,recipe_payload=recipe_payload):
                        checker.recipes(original,rr,recipe)
                        hashes=sum(1 if v['policy']=='hash_offset' else 2 for v in recipe['trace'])
                        if recipe_payload['counters'].get('target_recipe_hashes',0)!=hashes:
                            raise ValueError('independent target recipe hash counts')
                        return dict(checked=True,producer_output_sha256=commitment(recipe_payload),independent_hashes=hashes)
                    write_once(args.out/(cid+'.target-recipes-h'+str(horizon)+'-check.json'),
                        timed(recipe_check))
                write_once(args.out/(cid+'.target-recipe-prefix-check.json'),timed(lambda:
                    dict(checked=recipe_prefix(recipes[8],recipes[24],rules['targets'],rules['target_policies']))))
                norm_cases={}
                for p in PROGRAMS:
                    pid=p['id'];rr=rules_for(rules,pid);prep=prepared[pid];cell=prep['cell'];f=cell['fixture']
                    emit=lambda value,p=p:event(dict(program=p['id'],base_arm=p['base'],**value))
                    collected=(collection16.collect if p['source'] else collection16.collect_known)(prep,targets,rr,emit,NATIVE_CAPABILITY)
                    write_once(args.out/(cid+'.'+pid+'.source.json'),dict(cell=cell,collection=collected),compact=True)
                    wall,cpu=perf_counter(),process_time();checked,oracle=checks16.collection(prep,rr,collected)
                    write_once(args.out/(cid+'.'+pid+'.source-check.json'),dict(verification=checked,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
                    cache=OwnedTargetCache(collected.query_index,collected['natural_records'],rr,emit,NATIVE_CAPABILITY)
                    group_oracle=checker.GroupOracle(f,targets['targets'])
                    schedules=[kind+str(seed) for seed in rules['seeds'] for kind in ('ap','hash')] if p['source'] else ['known']
                    prefix=rules['sources'] if p['source'] else 0
                    for schedule in schedules:
                        for policy in rules['target_policies']:
                            context=dict(source_schedule=schedule,source_prefix=prefix,target_policy=policy)
                            recipe=recipes[p['horizon']]['policies'][policy]
                            branch=branch16.build(cell,collected,rr,recipe,schedule,prefix,policy,cache,emit,NATIVE_CAPABILITY)
                            receipt=append(streams['branches'],dict(program=pid,base_arm=p['base'],context=context,branch=branch))
                            emit(dict(kind='branch_output',context=context,record=receipt))
                            checked=timed(lambda:checks16.branch(cell,collected,rr,recipe,branch,cache,group_oracle))
                            emit(dict(kind='branch_checked',context=context,**checked))
                            for budget in rr['target_prefixes']:
                                for scope in (rr['norm_scopes'] if p['source'] else [rr['known_scope']]):
                                    desc=dict(cell_id=cid,program=pid,base_arm=p['base'],target_horizon=p['horizon'],**context,target_prefix=budget,scope=scope)
                                    if plans.get(count)!=desc:raise ValueError('descriptor execution order differs')
                                    assembly=core.ProgressMeter(f,emit,dict(kind='native_matrix_assembly',case_id=count))
                                    case=assembly.stage('native_matrix_assembly',lambda:native_case.build(prep,collected,branch,cache,budget,scope,assembly))
                                    receipt=append(streams['case-inputs'],dict(case_id=count,descriptor=desc,case=case,shared_phases=assembly.phases))
                                    emit(dict(kind='case_input',case_id=count,descriptor=desc,record=receipt,shared_phases=assembly.phases))
                                    outputs=[]
                                    for method in methods(desc):
                                        meter=solver.Meter(f);result=None
                                        try:
                                            result=partial_solver.solve(case,prep['known'],prep['basis'],meter) if method=='partial_joint' else solver.solve(case,method,meter)
                                            public_verify(result,case,f,meter)
                                            receipt=append(streams['solver-outputs'],dict(case_id=count,arm=method,result=result))
                                            emit(dict(kind='solver_complete',case_id=count,descriptor=desc,arm=method,record=receipt,counters=result['counters']))
                                            outputs.append(result);calls+=1
                                        except BaseException as error:
                                            emit(dict(kind='solver_failed',case_id=count,descriptor=desc,arm=method,partial_result=result,phases=meter.phases,error_type=type(error).__name__,error=str(error)))
                                            raise
                                    def check_case():
                                        if commitment(case)!=commitment(native_case.expected(prep,collected,branch,cache,budget,scope)):
                                            raise ValueError('independent native case assembly')
                                        partial=check_partial.check(case,prep['known'],prep['basis'],outputs[0],f)
                                        joint=known_checks.joint_case(case,outputs[1],f)
                                        if [(v['identifiable'],v['scalar']) for v in outputs[0]['recoveries']]!=[(v['identifiable'],v['scalar']) for v in outputs[1]['recoveries']]:
                                            raise ValueError('partial/native joint target outcome differs')
                                        return dict(checked=True,partial=partial,joint=joint,case_sha256=commitment(case),
                                            solver_output_sha256={method:commitment(value) for method,value in zip(methods(desc),outputs,strict=True)})
                                    checked=timed(check_case)
                                    receipt=append(streams['case-checks'],dict(case_id=count,descriptor=desc,**checked))
                                    emit(dict(kind='case_checked',case_id=count,descriptor=desc,record=receipt,verification=checked['verification']))
                                    key=(schedule,policy,budget,scope)
                                    if pid=='norm8':norm_cases[key]=(count,case)
                                    if pid=='hybrid8':
                                        norm_id,old_case=norm_cases[key];diagnostic=None;output_receipt=None
                                        meter=core.ProgressMeter(f,emit,dict(kind='information_diagnostic',case_id=count,norm_case_id=norm_id))
                                        try:
                                            diagnostic=information.compare(old_case,prepared['norm8'],case,prep,meter)
                                            output_receipt=append(streams['information'],dict(norm_case_id=norm_id,hybrid_case_id=count,descriptor=desc,result=diagnostic))
                                            emit(dict(kind='information_output',case_id=count,norm_case_id=norm_id,record=output_receipt,counters=diagnostic['counters']))
                                            def information_check():
                                                value=check_information.check(old_case,prepared['norm8'],case,prep,diagnostic)
                                                value['producer_output_sha256']=commitment(diagnostic);return value
                                            checked=timed(information_check)
                                            receipt=append(streams['information-checks'],dict(norm_case_id=norm_id,hybrid_case_id=count,descriptor=desc,**checked))
                                            emit(dict(kind='information_checked',case_id=count,norm_case_id=norm_id,record=receipt,verification=checked['verification']))
                                            audits+=1
                                        except BaseException as error:
                                            emit(dict(kind='information_failed',case_id=count,norm_case_id=norm_id,output_record=output_receipt,phases=meter.phases,error_type=type(error).__name__,error=str(error)));raise
                                    count+=1
                    payload=checks16.cache_payload(cache)
                    write_once(args.out/(cid+'.'+pid+'.query-cache.json'),payload,compact=True)
                    write_once(args.out/(cid+'.'+pid+'.query-check.json'),timed(lambda:checks16.target_cache(prep,collected,cache,oracle,rr)))
                write_once(args.out/(cid+'.complete.json'),dict(complete=True,cases_checked=count,solver_calls=calls,information_audits=audits,curve_index=curves))
            except BaseException as error:
                event(dict(kind='failure',error_type=type(error).__name__,error=str(error),partial_case=getattr(error,'partial_case',None)));raise
        curves+=1;close_encodings(args.out,cid)
        if rules['closed_curve_checkpoint']:checkpoint_curve(args.out.parent,cid,count,curves)
    if count!=rules['systems'] or calls!=rules['solver_calls'] or audits!=rules['information_audits']:raise ValueError('incomplete fixed program census')
    print(__import__('json').dumps(dict(complete=True,systems=count,solver_calls=calls,information_audits=audits,physical_attempts=1,closed_curve_checkpoints=curves)))


if __name__=='__main__':main()

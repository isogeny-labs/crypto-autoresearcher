"""One normally admitted norm/unknown/formal/numeric four-program experiment."""
import argparse
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter,process_time
from deps20 import core,solver,NATIVE_CAPABILITY,public_base,check_base,checker,check_source,commitment
from deps20 import known_checks,public_verify,check_pairs
from custody20 import ROOT,SOURCES,PARAMETERS,PROGRAMS,load,write_once,descriptors,validate_rules,rules_for
from streams20 import append,close_encodings,checkpoint_curve,admitted_start
import pool19,collection19,check_collection19,branch19,cancel19,information19,check_algebra19
import formal_pool20,preparation20,native_case20 as native_case,check_formal20
from crypto_autoresearcher.index_calculus.execution_gate import admit


def timed(operation,payload=None):
    wall,cpu=perf_counter(),process_time();value=operation()
    if payload is not None:value=dict(value,producer_output_sha256=commitment(payload))
    return dict(verification=value,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise ValueError('fresh raw output required')
    admission=admit(ROOT,args.protocol,args.inputs,SOURCES,PARAMETERS,args.release)
    rules=load(args.inputs);validate_rules(rules);plans=dict(descriptors(rules))
    if len(plans)!=16:raise ValueError('fixed prospective case census')
    args.out.mkdir(parents=True);write_once(args.out/'admission.json',admission);admitted_start(args.out.parent,admission)
    with (args.out/'generation.events.jsonl').open('x')as journal:
        event=lambda v:append(journal,v)
        try:
            generated=core.generate(rules,event,core._NATIVE_CAPABILITY);write_once(args.out/'generated.json',generated)
            def generation_check():
                from shared import batch_check
                value=check_source.check_generation(rules,generated);value['field_prime_selection']=batch_check.field_selection(rules,generated);return value
            write_once(args.out/'generation-check.json',timed(generation_check,generated))
        except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    cases=calls=curves=0
    for original in generated['cells']:
        cid=original['id'];prepared={};reference=None
        # All auxiliary builds and owned prerequisites precede target draw.
        for program in PROGRAMS:
            rr=rules_for(rules,program);prefix=cid+'.'+program+'.'
            with (args.out/(prefix+'setup.events.jsonl')).open('x')as journal:
                event=lambda v:append(journal,v)
                try:
                    helper=pool=None
                    if program=='unknown16':
                        pool=pool19.build(original,rr,event,NATIVE_CAPABILITY)
                        write_once(args.out/(prefix+'base.json'),pool,compact=True)
                        write_once(args.out/(prefix+'base-check.json'),timed(lambda:pool19.check(original,rr,pool),pool))
                    if program=='formalpair16':
                        pool=formal_pool20.build(original,rr,event,NATIVE_CAPABILITY)
                        write_once(args.out/(prefix+'base.json'),pool,compact=True)
                        write_once(args.out/(prefix+'base-check.json'),timed(lambda:formal_pool20.check(original,rr,pool),pool))
                    if program=='known16':
                        helper=public_base.build(original,rr,16,event,NATIVE_CAPABILITY)
                        write_once(args.out/(prefix+'base.json'),helper,compact=True)
                        write_once(args.out/(prefix+'base-check.json'),timed(lambda:check_base.check(original,rr,16,helper),helper))
                    prep=preparation20.prepare(original,rr,helper,event,NATIVE_CAPABILITY,pool)
                    prepared[program]=prep
                    write_once(args.out/(prefix+'prelude.json'),prep,compact=True)
                    write_once(args.out/(prefix+'prelude-check.json'),timed(lambda:preparation20.check(original,rr,helper,prep,pool),prep))
                except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
        with (args.out/(cid+'.shared.events.jsonl')).open('x')as journal:
            event=lambda v:append(journal,v);meter=core.ProgressMeter(original['fixture'],event,dict(kind='shared_public_targets'))
            targets=meter.stage('public_target_generation',lambda:core.old.targets(original,rules,meter,event))
            target_payload=dict(generation=targets,phases=meter.phases,counters=meter.counters())
            write_once(args.out/(cid+'.targets.json'),target_payload)
            write_once(args.out/(cid+'.targets-check.json'),timed(lambda:check_collection19.targets(original,rules,targets),target_payload))
        for program in PROGRAMS:
            rr=rules_for(rules,program);prefix=cid+'.'+program+'.';prep=prepared[program];f=prep['cell']['fixture']
            with (args.out/(prefix+'events.jsonl')).open('x')as journal:
                event=lambda v:append(journal,v)
                try:
                    collected=collection19.collect(prep,targets,rr,event,NATIVE_CAPABILITY)
                    write_once(args.out/(prefix+'collection.json'),dict(cell=prep['cell'],collection=collected),compact=True)
                    def collection_check():
                        value,oracle=check_collection19.collection(prep,rr,collected)
                        phases=[]
                        for phase in collected['collection_phases']:
                            if phase['phase']=='natural_target_queries':break
                            phases.append(phase)
                        value['pair_construction']=check_pairs(f,prep['geometry'],'batched',collected['pairs'],phases)
                        return value
                    write_once(args.out/(prefix+'collection-check.json'),timed(collection_check,collected))
                    meter=core.ProgressMeter(f,event,dict(kind='owned_target_recipe'))
                    recipe=meter.stage('target_recipes',lambda:core.recipes(original,collected,rr,meter,event,core._NATIVE_CAPABILITY))
                    payload=dict(selection=recipe,phases=meter.phases,counters=meter.counters())
                    write_once(args.out/(prefix+'recipe.json'),payload)
                    write_once(args.out/(prefix+'recipe-check.json'),timed(lambda:dict(checked=checker.recipes(original,rr,recipe)is not False),payload))
                    cache=branch19.OwnedCache(collected,rr,event,NATIVE_CAPABILITY)
                    branch=branch19.build(prep,collected,rr,recipe['policies']['general'],cache,event,NATIVE_CAPABILITY)
                    write_once(args.out/(prefix+'construction.json'),branch,compact=True)
                    write_once(args.out/(prefix+'construction-check.json'),timed(lambda:branch19.check(prep,collected,rr,recipe['policies']['general'],cache,branch),branch))
                    assembly=core.ProgressMeter(f,event,dict(kind='native_matrix_assembly'))
                    case=assembly.stage('native_matrix_assembly',lambda:native_case.build(prep,collected,branch,cache,8,'anchors',assembly))
                    write_once(args.out/(prefix+'case.json'),case,compact=True)
                    write_once(args.out/(prefix+'assembly.json'),dict(phases=assembly.phases,counters=assembly.counters()))
                    if commitment(case)!=commitment(native_case.expected(prep,collected,branch,cache,8,'anchors')):raise ValueError('independent native assembly differs')
                    write_once(args.out/(prefix+'case-check.json'),timed(lambda:dict(checked=True,
                        prepared_sha256=commitment(prep),collection_sha256=commitment(collected),branch_sha256=commitment(branch),
                        cache_records_sha256=commitment(cache.records),assembly_sha256=commitment(dict(phases=assembly.phases,counters=assembly.counters()))),case))
                    outputs=[]
                    for label,method in ((program,'aux_cancel_joint'),('joint_on_'+program,'sparse_joint')):
                        event(dict(kind='batch_solver_start',execution_arm=label,case_id=cases));meter=solver.Meter(f);result=None
                        try:
                            result=cancel19.solve(case,prep,meter)if method=='aux_cancel_joint'else solver.solve(case,method,meter)
                            public_verify(result,case,f,meter)
                            write_once(args.out/(prefix+method+'.json'),result,compact=True)
                            def check():
                                value=check_algebra19.cancelled_target(case,prep,result,f)if method=='aux_cancel_joint'else known_checks.joint_case(case,result,f)
                                return dict(value,input_case_sha256=commitment(case),prepared_sha256=commitment(prep))
                            write_once(args.out/(prefix+method+'-check.json'),timed(check,result))
                            event(dict(kind='batch_solver_complete',execution_arm=label,case_id=cases,counters=result['counters']));outputs.append(result);calls+=1
                        except BaseException as error:
                            event(dict(kind='batch_solver_failed',execution_arm=label,case_id=cases,partial_result=result,phases=meter.phases,error_type=type(error).__name__,error=str(error)));raise
                    if [(v['identifiable'],v['scalar'])for v in outputs[0]['recoveries']]!=[(v['identifiable'],v['scalar'])for v in outputs[1]['recoveries']]:raise ValueError('cancellation/native joint disagreement')
                    meter=core.ProgressMeter(f,event,dict(kind='information_diagnostic'))
                    if program=='norm32':
                        def floor():
                            projected=information19.project(case,prep,meter)
                            return [(v['vector'],v['rhs'])for v in projected['rows']if v['kind']=='collected_source']
                        reference=meter.stage('common_norm_source_only_floor',floor)
                        write_once(args.out/(cid+'.reference-floor-cost.json'),dict(phases=[meter.phases[-1]],counters=meter.phases[-1]['counters']))
                        reference_payload=dict(rows=reference,projection=prep['projection'],source_case_sha256=commitment(case))
                        write_once(args.out/(cid+'.reference.json'),reference_payload)
                        def reference_check():
                            projected=check_algebra19.projected(case,prep)
                            expected=[(v['vector'],v['rhs'])for v in projected['rows']if v['kind']=='collected_source']
                            if commitment(expected)!=commitment(reference):raise ValueError('pure norm floor differs')
                            return dict(checked=True,source_case_sha256=commitment(case),prepared_sha256=commitment(prep))
                        write_once(args.out/(cid+'.reference-check.json'),timed(reference_check,reference_payload))
                    diagnostic=information19.measure(reference,case,prep,meter)
                    write_once(args.out/(prefix+'information.json'),diagnostic,compact=True)
                    def info_check():
                        value=check_algebra19.information(reference,case,prep,diagnostic)
                        return dict(value,input_case_sha256=commitment(case),prepared_sha256=commitment(prep),reference_sha256=commitment(reference))
                    write_once(args.out/(prefix+'information-check.json'),timed(info_check,diagnostic))
                    write_once(args.out/(prefix+'expanded-check.json'),timed(lambda:check_formal20.check(case,prep,outputs[0],diagnostic)))
                    cache_payload=dict(records=cache.records,engine_records=cache.engines.records[cache.engine_start:],engine_start=cache.engine_start,phases=cache.meter.phases,counters=cache.meter.counters(),owner=list(cache.owner))
                    write_once(args.out/(prefix+'cache.json'),cache_payload,compact=True)
                    def cache_check():
                        from check_query import Oracle
                        return check_collection19.target_cache(prep,collected,cache,Oracle(f,prep['geometry']))
                    write_once(args.out/(prefix+'cache-check.json'),timed(cache_check,cache_payload))
                    descriptor=plans[cases]
                    if descriptor['cell_id']!=cid or descriptor['program']!=program:raise ValueError('fixed descriptor order')
                    write_once(args.out/(prefix+'complete.json'),dict(complete=True,case_id=cases,descriptor=descriptor,solver_calls=2,information_checked=True))
                    cases+=1
                except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error),partial_case=getattr(error,'partial_case',None)));raise
        curves+=1;close_encodings(args.out,cid);checkpoint_curve(args.out.parent,cid,curves,cases,calls,0)
    if(cases,calls,curves)!=(16,32,4):raise ValueError('incomplete prospective census')
    print(__import__('json').dumps(dict(complete=True,systems=cases,batch_solver_calls=calls,information_diagnostics=cases,physical_attempts=1)))


if __name__=='__main__':main()

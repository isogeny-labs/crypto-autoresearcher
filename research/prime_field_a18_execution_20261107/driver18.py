"""One admitted fresh full24 construction/query-suppression panel, no retries."""
import argparse
from contextlib import ExitStack
from pathlib import Path
from copy import deepcopy
from time import perf_counter,process_time
from deps18 import core,solver,NATIVE_CAPABILITY,public_base,check_base,checker,check_source,old_check
from deps18 import collection16,checks16,partial_solver,check_partial,known_checks,public_verify,commitment
from custody18 import ROOT,SOURCES,PARAMETERS,load,write_once,validate_rules,descriptors,PROGRAMS
from streams18 import append,close_encodings,admitted_start,checkpoint_curve
from ownership17 import OwnedCache
from cost17 import cache_payload,cold
import preconstruct17,query17,check_construct17,check_query18,check_span17
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
    if len(plans)!=8:raise ValueError('fixed four-curve/eight-program census')
    args.out.mkdir(parents=True);write_once(args.out/'admission.json',admission)
    admitted_start(args.out.parent,admission)
    with (args.out/'generation.events.jsonl').open('x') as stream:
        event=lambda value:append(stream,value)
        try:
            generated=core.generate(rules,event,core._NATIVE_CAPABILITY)
            write_once(args.out/'generated.json',generated)
            def verify_generation():
                from shared import batch_check
                value=check_source.check_generation(rules,generated)
                value['field_selection']=batch_check.field_selection(rules,generated)
                value['producer_output_sha256']=commitment(generated);return value
            write_once(args.out/'generation-check.json',timed(verify_generation))
        except BaseException as error:
            event(dict(kind='generation_failed',error_type=type(error).__name__,error=str(error)));raise
    cases=batches=online=curves=0
    for original in generated['cells']:
        cid=original['id']
        try:
            with ExitStack() as stack:
                streams={arm:stack.enter_context((args.out/(cid+'.'+arm+'.events.jsonl')).open('x')) for arm in PROGRAMS}
                shared=stack.enter_context((args.out/(cid+'.shared.events.jsonl')).open('x'))
                buffers={arm:[] for arm in PROGRAMS}
                def emit(arm,value):
                    receipt=append(streams[arm],value);buffers[arm].append(deepcopy(value));return receipt
                def shared_event(value):return append(shared,value)
                try:
                    built={}
                    # Both actual independently cold public bases precede targets.
                    for arm in PROGRAMS:
                        value=public_base.build(original,rules,48,lambda v,arm=arm:emit(arm,v),NATIVE_CAPABILITY)
                        value.update(arm_owner=arm,owner_program='known48_24',target_horizon=24)
                        built[arm]=value
                        write_once(args.out/(cid+'.'+arm+'.base.json'),value,compact=True)
                        write_once(args.out/(cid+'.'+arm+'.base-check.json'),timed(lambda arm=arm:
                            dict(checked=True,arm_owner=arm,plain_group=check_base.check(original,rules,48,built[arm]),producer_output_sha256=commitment(built[arm]))))
                    if built['suppress']['cell']!=built['full']['cell'] or built['suppress']['knowledge']!=built['full']['knowledge']:
                        raise ValueError('mathematically identical public base recipe differs')
                    meter=core.ProgressMeter(original['fixture'],shared_event,dict(kind='shared_public_targets'))
                    targets=meter.stage('target_generation',lambda:core.old.targets(original,rules,meter,shared_event))
                    target_payload=dict(generation=targets,phases=meter.phases,counters=meter.counters())
                    write_once(args.out/(cid+'.targets.json'),target_payload)
                    def check_targets():
                        value=old_check.targets(original,rules,targets);value['producer_output_sha256']=commitment(target_payload);return value
                    write_once(args.out/(cid+'.targets-check.json'),timed(check_targets))
                    results={};clouds={};recipes={};checks={}
                    for arm in PROGRAMS:  # candidate first, never reference answers before a skip
                        event=lambda value,arm=arm:emit(arm,value)
                        prep=collection16.prepare_known(built[arm],rules,event,NATIVE_CAPABILITY);prep['arm_owner']=arm
                        write_once(args.out/(cid+'.'+arm+'.prelude.json'),prep,compact=True)
                        write_once(args.out/(cid+'.'+arm+'.prelude-check.json'),timed(lambda:
                            dict(checked=True,plain_group=old_check.known_preparation(original,rules,built[arm],prep),producer_output_sha256=commitment(prep))))
                        rmeter=core.ProgressMeter(prep['cell']['fixture'],event,dict(kind='own_general24_recipe'))
                        selected=rmeter.stage('target_recipes',lambda:core.recipes(original,dict(target_generation=targets),rules,rmeter,event,core._NATIVE_CAPABILITY))
                        recipe_payload=dict(selection=selected,phases=rmeter.phases,counters=rmeter.counters(),arm_owner=arm)
                        recipes[arm]=selected
                        write_once(args.out/(cid+'.'+arm+'.recipe.json'),recipe_payload)
                        def check_recipe():
                            checker.recipes(original,rules,selected)
                            expected=2*len(selected['trace'])
                            if recipe_payload['counters'].get('target_recipe_hashes',0)!=expected:raise ValueError('independent GENERAL recipe hash count')
                            return dict(checked=True,independent_hashes=expected,producer_output_sha256=commitment(recipe_payload))
                        write_once(args.out/(cid+'.'+arm+'.recipe-check.json'),timed(check_recipe))
                        collected=collection16.collect_known(prep,targets,rules,event,NATIVE_CAPABILITY);collected['arm_owner']=arm
                        write_once(args.out/(cid+'.'+arm+'.collection.json'),dict(cell=prep['cell'],collection=collected),compact=True)
                        wall,cpu=perf_counter(),process_time();proof,oracle=checks16.collection(prep,rules,collected)
                        write_once(args.out/(cid+'.'+arm+'.collection-check.json'),dict(verification=proof,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
                        recipe=selected['policies']['general']
                        cloud=preconstruct17.build(prep['cell'],collected,rules,recipe,event,arm,NATIVE_CAPABILITY);clouds[arm]=cloud
                        write_once(args.out/(cid+'.'+arm+'.construction.json'),cloud,compact=True)
                        write_once(args.out/(cid+'.'+arm+'.construction-check.json'),timed(lambda:
                            check_construct17.check(prep['cell'],collected,rules,recipe,cloud,arm,NATIVE_CAPABILITY)))
                        cache=OwnedCache(prep['cell'],collected,rules,recipe,arm,event,NATIVE_CAPABILITY)
                        result=query17.execute(prep,collected,cloud,cache,rules,arm,event,NATIVE_CAPABILITY);results[arm]=result
                        if arm=='suppress':online+=1
                        write_once(args.out/(cid+'.'+arm+'.query.json'),result,compact=True)
                        cp=cache_payload(cache);write_once(args.out/(cid+'.'+arm+'.cache.json'),cp,compact=True)
                        write_once(args.out/(cid+'.'+arm+'.query-check.json'),timed(lambda:
                            check_query18.check(prep,collected,cloud,cache,result,buffers[arm],rules,arm,oracle,NATIVE_CAPABILITY)))
                        case=result['case'];fixture=prep['cell']['fixture']
                        if arm=='suppress':primary=result['online']
                        else:
                            m=solver.Meter(fixture);primary=None
                            event(dict(kind='batch_solver_start',execution_arm='full',method='partial_joint'))
                            try:
                                primary=partial_solver.solve(case,prep['known'],[],m);public_verify(primary,case,fixture,m);batches+=1
                                event(dict(kind='batch_solver_complete',execution_arm='full',method='partial_joint',counters=primary['counters']))
                            except BaseException as error:
                                event(dict(kind='batch_solver_failed',execution_arm='full',method='partial_joint',partial_result=primary,phases=m.phases,error_type=type(error).__name__,error=str(error)));raise
                        write_once(args.out/(cid+'.'+arm+'.primary.json'),primary,compact=True)
                        if arm=='full':
                            write_once(args.out/(cid+'.'+arm+'.primary-check.json'),timed(lambda:
                                dict(checked=True,plain_native=check_partial.check(case,prep['known'],[],primary,fixture),producer_output_sha256=commitment(primary))))
                        else:
                            write_once(args.out/(cid+'.'+arm+'.primary-check.json'),dict(verification=dict(checked=True,
                                source='same actual online engine as complete query-check, no additional primary solver call',producer_output_sha256=commitment(primary))))
                        joint_meter=solver.Meter(fixture);joint=None
                        event(dict(kind='batch_solver_start',execution_arm='joint_on_'+arm,method='sparse_joint'))
                        try:
                            joint=solver.solve(case,'sparse_joint',joint_meter);public_verify(joint,case,fixture,joint_meter);batches+=1
                            event(dict(kind='batch_solver_complete',execution_arm='joint_on_'+arm,method='sparse_joint',counters=joint['counters']))
                        except BaseException as error:
                            event(dict(kind='batch_solver_failed',execution_arm='joint_on_'+arm,partial_result=joint,phases=joint_meter.phases,error_type=type(error).__name__,error=str(error)));raise
                        write_once(args.out/(cid+'.'+arm+'.joint.json'),joint,compact=True)
                        def check_joint():
                            value=known_checks.joint_case(case,joint,fixture)
                            if [(v['identifiable'],v['scalar']) for v in primary['recoveries']]!=[(v['identifiable'],v['scalar']) for v in joint['recoveries']]:raise ValueError('primary/candidate-pool native joint outcomes differ')
                            return dict(checked=True,plain_native=value,producer_output_sha256=commitment(joint),primary_output_sha256=commitment(primary))
                        write_once(args.out/(cid+'.'+arm+'.joint-check.json'),timed(check_joint))
                        view=cold(arm,built[arm],prep,collected,recipe_payload,target_payload,cloud,result,cp,primary)
                        write_once(args.out/(cid+'.'+arm+'.cold.json'),view,compact=True)
                        descriptor=dict(cell_id=cid,program=arm,base_arm='known48',target_horizon=24,target_policy='general',scope='supplied')
                        if plans.get(cases)!=descriptor:raise ValueError('fixed case order')
                        write_once(args.out/(cid+'.'+arm+'.complete.json'),dict(complete=True,case_id=cases,descriptor=descriptor,
                            query_output_sha256=commitment(result),primary_output_sha256=commitment(primary),joint_output_sha256=commitment(joint),cold_output_sha256=commitment(view)))
                        checks[arm]=dict(mask=sum(1<<v['target_index'] for v in primary['recoveries'] if v['identifiable']))
                        cases+=1
                    if recipes['suppress']!=recipes['full']:raise ValueError('independently derived common recipe differs')
                    for key in ('recipe','endpoints','selections','scalar_events','labels','equations','counters'):
                        if clouds['suppress'][key]!=clouds['full'][key]:raise ValueError('full paid construction semantic/counter parity differs: '+key)
                    span=check_span17.check(results['full'],results['suppress'],built['full']['cell']['fixture'],shared_event)
                    write_once(args.out/(cid+'.row-consequences.json'),span,compact=True)
                    if checks['suppress']['mask']!=checks['full']['mask']:raise ValueError('all-known safe row suppression lost a target')
                    write_once(args.out/(cid+'.complete.json'),dict(complete=True,curve_index=curves,checked_case_systems=cases,
                        completed_batch_solver_calls=batches,completed_online_engines=online,verified_execution_rows=cases*2,
                        row_consequences_sha256=commitment(span),full_construction_equal=True,identified_mask=checks['full']['mask']))
                except BaseException as error:
                    shared_event(dict(kind='curve_failed',error_type=type(error).__name__,error=str(error),checked_case_systems=cases,
                        completed_batch_solver_calls=batches,completed_online_engines=online,partial_work_unknown=True));raise
        finally:
            # ExitStack has closed every scientific writer, including on failure.
            close_encodings(args.out,cid)
        curves+=1;checkpoint_curve(args.out.parent,cid,curves,cases,batches,online)
    if (curves,cases,batches,online)!=(4,8,12,4):raise ValueError('complete prospective panel census')


if __name__=='__main__':main()

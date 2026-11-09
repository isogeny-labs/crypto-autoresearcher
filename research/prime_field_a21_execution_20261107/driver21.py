"""One admitted three-method component comparison, never a new holdout panel."""
import argparse,json
from pathlib import Path
from time import process_time,perf_counter
from deps21 import solver,commitment,known_checks,public_verify,cancel19,check_algebra19,NATIVE_CAPABILITY
from custody21 import ROOT,SOURCES,PARAMETERS,ARMS,load,write_once,validate_rules,digest
from streams21 import append,admitted_start,checkpoint_curve
from crypto_autoresearcher.index_calculus.execution_gate import admit
import direct21,check21


def timed(fn):
    wall,cpu=perf_counter(),process_time();value=fn()
    return dict(verification=value,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('inputs','protocol','release','out'):parser.add_argument('--'+key,type=Path,required=True)
    a=parser.parse_args()
    if a.out.exists():raise ValueError('fresh raw output required')
    admission=admit(ROOT,a.protocol,a.inputs,SOURCES,PARAMETERS,a.release)
    rules=load(a.inputs);validate_rules(rules);a.out.mkdir(parents=True)
    write_once(a.out/'admission.json',admission);admitted_start(a.out.parent,admission)
    calls=0
    for index,descriptor in enumerate(rules['cases']):
        cid=descriptor['cell_id'];outputs=[]
        with (a.out/(cid+'.events.jsonl')).open('x')as journal:
            event=lambda v:append(journal,v)
            for method in ARMS:
                result=None;meter=None
                event(dict(kind='batch_solver_start',case_id=index,execution_arm=method))
                try:
                    start=process_time();inputs={}
                    for name,binding in descriptor['producer'].items():
                        path=ROOT/binding['path']
                        if digest(path)!=binding['sha256']:raise ValueError('conditioned producer input changed')
                        inputs[name]=load(path)
                    event(dict(kind='producer_input_load',execution_arm=method,case_id=index,cpu_seconds=process_time()-start,
                        bytes=sum((ROOT/v['path']).stat().st_size for v in descriptor['producer'].values()),checker_data_loaded=False))
                    case,prep=inputs['case'],inputs['prepared'];f=prep['cell']['fixture'];meter=solver.Meter(f)
                    if method=='direct_formal':result=direct21.solve(case,prep,meter,NATIVE_CAPABILITY)
                    elif method=='aux_cancel_joint':result=cancel19.solve(case,prep,meter)
                    else:result=solver.solve(case,method,meter)
                    public_verify(result,case,f,meter)
                    write_once(a.out/(cid+'.'+method+'.json'),result,compact=True)
                    def check():
                        if method=='direct_formal':value=check21.verify(case,prep,result)
                        elif method=='aux_cancel_joint':value=check_algebra19.cancelled_target(case,prep,result,f)
                        else:value=known_checks.joint_case(case,result,f)
                        return dict(value,input_case_sha256=commitment(case),prepared_sha256=commitment(prep),producer_output_sha256=commitment(result))
                    write_once(a.out/(cid+'.'+method+'-check.json'),timed(check))
                    event(dict(kind='batch_solver_complete',execution_arm=method,case_id=index,counters=result['counters']));calls+=1;outputs.append(result)
                except BaseException as error:
                    event(dict(kind='batch_solver_failed',execution_arm=method,case_id=index,partial_result=result,
                        phases=[]if meter is None else meter.phases,error_type=type(error).__name__,error=str(error)));raise
            outcomes=[[(v['identifiable'],v['scalar'])for v in out['recoveries']]for out in outputs]
            if any(v!=outcomes[0]for v in outcomes):raise ValueError('actual three-method disagreement')
            # Historical outputs are checker-only and loaded only AFTER all
            # three actual cold producers have finished this case.
            for label in ('aux_cancel_joint','sparse_joint'):
                binding=descriptor['checker_only'][label];old=load(ROOT/binding['path'])
                if [(v['identifiable'],v['scalar'])for v in old['recoveries']]!=outcomes[0]:raise ValueError('historical native outcome mismatch')
            write_once(a.out/(cid+'.complete.json'),dict(complete=True,case_id=index,descriptor=descriptor,actual_solver_calls=3,
                all_methods_agree=True,historical_outcomes_agree=True,producer_input_hashes=descriptor['producer']))
        checkpoint_curve(a.out.parent,cid,index+1,index+1,calls,0)
    if calls!=12:raise ValueError('exact twelve actual calls required')
    print(json.dumps(dict(complete=True,conditioned_cases=4,actual_batch_solver_calls=12,new_curves=0,new_targets=0)))


if __name__=='__main__':main()

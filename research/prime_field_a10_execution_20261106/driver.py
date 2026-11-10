"""Admitted one-attempt fresh panel; every observed prefix is journalled."""
import argparse,json
from pathlib import Path
from time import perf_counter,process_time
import core,solver,check
from common import ROOT,HERE,SOURCES,PARAMETERS,load,write_once,digest
from crypto_autoresearcher.index_calculus.execution_gate import admit

def main():
    p=argparse.ArgumentParser()
    for n in ('inputs','protocol','release','out'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise ValueError('fresh output required')
    if core.PARAMETERS!=PARAMETERS:raise ValueError('parameter parity')
    admission=admit(ROOT,a.protocol,a.inputs,SOURCES,PARAMETERS,a.release)
    rules=load(a.inputs);a.out.mkdir(parents=True);write_once(a.out/'admission.json',admission)
    count=0
    with (a.out/'generation.events.jsonl').open('x') as stream:
        def event(value):stream.write(json.dumps(value,sort_keys=True)+'\n');stream.flush()
        try:
            generated=core.generate(rules,event,core._NATIVE_CAPABILITY);write_once(a.out/'generated.json',generated)
            wall,cpu=perf_counter(),process_time();verified=check.check_generation(rules,generated)
            write_once(a.out/'generation-check.json',dict(verification=verified,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
        except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    for cell in generated['cells']:
        records=[]
        with (a.out/(cell['id']+'.events.jsonl')).open('x') as stream:
            def event(value):stream.write(json.dumps(value,sort_keys=True)+'\n');stream.flush()
            try:
                collected=core.collect(cell,rules,event,core._NATIVE_CAPABILITY)
                write_once(a.out/(cell['id']+'.collection.json'),dict(cell=cell,collection=collected),compact=True)
                wall,cpu=perf_counter(),process_time();verified=check.collection(cell,rules,collected)
                write_once(a.out/(cell['id']+'.collection-check.json'),dict(verification=verified,wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
                for arm in collected['selection']['orders']:
                    for prefix in rules['prefixes']:
                        for scope in rules['scopes']:
                            desc=dict(cell_id=cell['id'],arm=arm,prefix=prefix,scope=scope);event(dict(kind='case_started',descriptor=desc))
                            meter=solver.Meter(cell['fixture']);case=meter.stage('shared_projection',lambda:core.case_input(cell,collected,arm,prefix,scope,meter))
                            event(dict(kind='case_input',descriptor=desc,case=case,shared_phases=meter.phases));results=[]
                            for method in ('sparse_joint','sparse_cancel'):
                                met=solver.Meter(cell['fixture'])
                                try:
                                    result=solver.solve(case,method,met)
                                    def public():
                                        for rec,target in zip(result['recoveries'],case['targets'],strict=True):
                                            if rec['identifiable']:
                                                if not met.equal(met.e.mul(rec['scalar'],tuple(cell['fixture']['P'])),tuple(target['point'])):raise ValueError('public target certificate')
                                                met.other['public_target_certificates_verified']+=1
                                    met.stage('public_target_verification',public);result['phases']=met.phases;result['counters']=solver.counters(met.phases)
                                    results.append(result);event(dict(kind='solver_complete',descriptor=desc,result=result))
                                except BaseException as error:event(dict(kind='solver_failed',descriptor=desc,arm=method,phases=met.phases,error_type=type(error).__name__,error=str(error)));raise
                            wall,cpu=perf_counter(),process_time()
                            if core.code(case)!=core.code(check.expected_case(cell,collected,arm,prefix,scope)):raise ValueError('independent projection')
                            verified=check.check(case,results,cell['fixture']);record=dict(descriptor=desc,case=case,shared_phases=meter.phases,results=results,verification=verified,checker_diagnostics=dict(wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
                            records.append(record);event(dict(kind='case_checked',descriptor=desc,verification=verified));count+=1
                write_once(a.out/(cell['id']+'.json'),dict(cell=cell,records=records,complete=True),compact=True)
            except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    if count!=rules['systems']:raise ValueError('incomplete case census')
    print(json.dumps(dict(complete=True,paired_systems=count,solver_calls=count*2,physical_processes=1)))
if __name__=='__main__':main()

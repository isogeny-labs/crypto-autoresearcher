"""Admit, load exact old rows, cold-rebuild both solvers, retain/check every case."""
import argparse,json
from pathlib import Path
from time import perf_counter,process_time
import core
from check import check,expected_case
from common import ROOT,HERE,SOURCES,PARAMETERS,load,check_parents,write_once,digest
from crypto_autoresearcher.index_calculus.execution_gate import admit

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('inputs','protocol','release','out'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise ValueError('fresh output required')
    if core.PARAMETERS!=PARAMETERS:raise ValueError('native/admin parameters differ')
    admission=admit(ROOT,a.protocol,a.inputs,SOURCES,PARAMETERS,a.release)
    rules=check_parents();fixtures=load(ROOT/rules['public_fixtures']['path']);a.out.mkdir(parents=True);write_once(a.out/'admission.json',admission)
    count=0
    for cell,parent in zip(fixtures['cells'],rules['parent_files'],strict=True):
        if parent['cell_id']!=cell['id']:raise ValueError('parent order')
        raw=load(ROOT/parent['path']);records=[];filename=a.out/(cell['id']+'.events.jsonl')
        with filename.open('x') as stream:
            def event(value):stream.write(json.dumps(value,sort_keys=True)+'\n');stream.flush()
            try:
                for arm in rules['source_schedules']:
                    for prefix in rules['prefixes']:
                        for scope in rules['scopes']:
                            descriptor=dict(cell_id=cell['id'],arm=arm,prefix=prefix,scope=scope);event(dict(kind='case_started',descriptor=descriptor))
                            order=raw['selection']['schedules'][arm][:prefix]
                            rows=[row for row in raw['arms'][arm]['rows'] if row['source_scalar']in order]
                            if scope=='anchors':rows += [row for row in raw['arms'][arm]['anchor_rows'] if row['source_scalar']in order]
                            meter=core.Meter(cell['fixture'])
                            def project():
                                return dict(width=cell['projection']['U'],target_count=rules['targets'],modulus=cell['fixture']['r'],source=[core.old.direct.project(row,cell['projection'],meter) for row in rows],target=[dict(target_index=row['target_index'],vector=v,rhs=b) for row in raw['target_collection']['rows'] for v,b in [core.old.direct.project(row,cell['projection'],meter)]],targets=raw['target_generation']['targets'])
                            case=meter.stage('shared_projection',project)
                            event(dict(kind='case_input',descriptor=descriptor,case=case,shared_phases=meter.phases))
                            def completed(result):event(dict(kind='solver_complete',descriptor=descriptor,result=result))
                            def failed(arm,phases,result,error):event(dict(kind='solver_failed',descriptor=descriptor,arm=arm,phases=phases,partial_result=result,error_type=type(error).__name__,error=str(error)))
                            results=core.compare(case,cell['fixture'],capability=core._NATIVE_CAPABILITY,on_result=completed,on_failure=failed)
                            wall,cpu=perf_counter(),process_time()
                            expected=expected_case(cell,raw,descriptor)
                            # JSON changes tuples to lists only; canonical equality avoids representation artifacts.
                            if json.dumps(case,sort_keys=True)!=json.dumps(expected,sort_keys=True):raise ValueError('independent projection differs')
                            prior=next(v for v in raw['prefixes'] if all(v[k]==descriptor[k] for k in ('arm','prefix','scope')))
                            verified=check(case,results,cell['fixture'],prior)
                            record=dict(descriptor=descriptor,case=case,shared_phases=meter.phases,results=results,verification=verified,checker_diagnostics=dict(wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
                            records.append(record);event(dict(kind='case_checked',descriptor=descriptor,verification=verified));count+=1
                write_once(a.out/(cell['id']+'.json'),dict(schema='a8-cold-solver-results/v1',cell_id=cell['id'],parent_sha256=parent['sha256'],inputs_sha256=digest(a.inputs),records=records,complete=True))
            except BaseException as error:event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    if count!=rules['systems']:raise ValueError('incomplete system count')
    print(json.dumps(dict(complete=True,paired_systems=count,solver_calls=count*2,physical_processes=1)))
if __name__=='__main__':main()

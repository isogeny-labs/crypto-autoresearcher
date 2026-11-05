"""Admit before source derivation; keep raw collection before matrix analysis."""
import argparse
import json
from pathlib import Path
from time import perf_counter,process_time
import core
from check import check,check_generation
from common import SOURCES,PARAMETERS,digest,write_once
from crypto_autoresearcher.index_calculus.execution_gate import admit


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise ValueError('fresh native output required')
    if core.PARAMETERS!=PARAMETERS:raise ValueError('native/admin parameters differ')
    admission=admit(core.ROOT,a.protocol,a.inputs,SOURCES,PARAMETERS,a.release)
    rules=json.loads(a.inputs.read_text());a.out.mkdir(parents=True);write_once(a.out/'admission.json',admission)
    with (a.out/'generation.events.jsonl').open('x') as stream:
        def event(v):stream.write(json.dumps(v,sort_keys=True)+'\n');stream.flush()
        generated=core.generate(rules,event,capability=core._NATIVE_CAPABILITY)
    generated['inputs_sha256']=digest(a.inputs);write_once(a.out/'generated.json',generated)
    wall,cpu=perf_counter(),process_time()
    try:write_once(a.out/'generation.verification.json',check_generation(rules,generated))
    finally:write_once(a.out/'generation.check-phase.json',dict(diagnostic_wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
    for cell in generated['cells']:
        with (a.out/(cell['id']+'.events.jsonl')).open('x') as stream:
            def event(v):stream.write(json.dumps(v,sort_keys=True)+'\n');stream.flush()
            try:
                result,meter=core.collect(cell,rules,event,capability=core._NATIVE_CAPABILITY)
                result['inputs_sha256']=digest(a.inputs);write_once(a.out/(cell['id']+'.collection.json'),result)
                for arm in ('window','hash0','hash1','hash2'):
                    for count in rules['prefixes']:
                        for anchor in (False,True):
                            result['prefixes'].append(core.analyze_prefix(cell,rules,result,meter,arm,count,anchor))
                result['total_counters']=meter.counters();write_once(a.out/(cell['id']+'.json'),result)
                events=[json.loads(line) for line in (a.out/(cell['id']+'.events.jsonl')).read_text().splitlines()]
                wall,cpu=perf_counter(),process_time()
                try:
                    verified=check(cell,rules,result,events)
                    write_once(a.out/(cell['id']+'.verification.json'),verified)
                finally:
                    write_once(a.out/(cell['id']+'.check-phase.json'),dict(phase='separate_checker',diagnostic_wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu,wall_valid=False))
            except BaseException as error:
                event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    print(json.dumps(dict(complete=True,curves=len(generated['cells']),scope_records=96,physical_panels=1)))


if __name__=='__main__':main()

"""Admit before source derivation; keep raw collection before matrix analysis."""
import argparse
import json
from pathlib import Path
import core
from check import check
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
    for cell in rules['cells']:
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
                write_once(a.out/(cell['id']+'.verification.json'),check(cell,rules,result,events))
            except BaseException as error:
                event(dict(kind='failure',error_type=type(error).__name__,error=str(error)));raise
    print(json.dumps(dict(complete=True,curves=len(rules['cells']),scope_records=96,physical_panels=1)))


if __name__=='__main__':main()

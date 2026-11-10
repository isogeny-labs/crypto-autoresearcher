"""One admitted complete retained-input pair comparison, no new target solvers."""
import argparse
from pathlib import Path
from datetime import datetime,timezone
import subprocess
import json
from deps15 import NATIVE_CAPABILITY
from custody15 import HERE,ROOT,INPUTS,SOURCES,PARAMETERS,load,write_once
from execute15 import execute
from streams14 import close_encodings
from crypto_autoresearcher.index_calculus.execution_gate import admit


def checkpoint(run,cid,tables):
    note=ROOT/'.resume/RESUME.md'
    with note.open('a') as stream:
        stream.write('\nA15 closed-curve progress '+datetime.now(timezone.utc).isoformat()+': '+cid+', '+str(tables)+' complete table comparisons. All writers closed/encoded. Same single consumed attempt; no restart.\n')
    p=subprocess.run(['bash','scripts/checkpoint.sh','push'],cwd=ROOT,capture_output=True,text=True)
    receipt=dict(command=['bash','scripts/checkpoint.sh','push'],returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,
                 completed_tables=tables,closed_curve=cid,observed_utc=datetime.now(timezone.utc).isoformat())
    write_once(run/('checkpoint-'+cid+'.json'),receipt)
    if p.returncode:raise RuntimeError('canonical closed-curve checkpoint failed: '+p.stderr)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise ValueError('fresh raw output required')
    admitted=admit(ROOT,args.protocol,args.inputs,SOURCES,PARAMETERS,args.release)
    rules=load(args.inputs)
    args.out.mkdir(parents=True)
    write_once(args.out/'admission.json',admitted)
    query_rules=dict(software_control=False,fields=[dict(p=p) for p in (262139,524287)],max_pair_entries=8192,max_retained_rows=4096)
    completed=queries=pairs=0
    try:
        for i,item in enumerate(rules['snapshots']):
            snapshot=load(ROOT/item['path'])
            if snapshot['id']!=item['id'] or len(snapshot['queries'])!=item['queries']:
                raise ValueError('retained table identity/query census')
            result=execute(snapshot,query_rules,args.out/item['id'],NATIVE_CAPABILITY)
            completed+=1;queries+=len(snapshot['queries']);pairs+=result['methods'][0]['build']['ordered_pairs']
            close_encodings(args.out/item['id'],'')
            if i%4==3:checkpoint(args.out.parent,item['id'].split('.')[0],completed)
        if completed!=16 or queries!=8960 or pairs!=51968:raise ValueError('complete finite component census')
        write_once(args.out/'complete.json',dict(complete=True,tables=completed,methods=2,
            query_calls=2*queries,query_engine_calls=4*queries,ordered_pair_outputs=2*pairs,target_solver_calls=0))
    except BaseException as error:
        write_once(args.out/'failure.json',dict(error_type=type(error).__name__,error=str(error),completed_tables=completed,
            completed_queries_per_method=queries,completed_pairs_per_method=pairs,partial_work_unknown=True))
        raise


if __name__=='__main__':main()

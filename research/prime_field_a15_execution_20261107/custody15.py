"""Exact A15 runtime/input closure and immutable custody helpers."""
from pathlib import Path
from hashlib import sha256
import subprocess
from deps15 import HERE, ROOT
import custody14 as prior

INPUTS=HERE/'inputs.json'
NATIVE=HERE
PARAMETERS=dict(tables=16,methods=['scalar','batched'],queries_per_method=8960,
    ordered_pairs_per_method=51968,new_target_solver_calls=0,maximum_native_width=48,
    maximum_pair_entries=8192,maximum_retained_rows=4096,query_engines=['scalar','batch'])
MODULES=['deps15','pairbuild15','check15','execute15','custody15','driver15','supervise15','prepare15','analyze15','transcribe15']
SOURCES=list(dict.fromkeys([*[HERE/(n+'.py') for n in MODULES],*prior.SOURCES]))
digest,load,write_once,git,tools=prior.digest,prior.load,prior.write_once,prior.git,prior.tools


def bindings(commit):
    rules=load(INPUTS)
    paths=[INPUTS,ROOT/'research/prime_field_a14_execution_20261106/protocol.json',
           *[ROOT/v['path'] for v in rules['snapshots']]]
    groups=[]
    for group in (SOURCES,paths):
        result={}
        for path in group:
            relative=str(path.relative_to(ROOT));actual=digest(path)
            published=subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)
            if sha256(published).hexdigest()!=actual:raise ValueError('exact source/input differs: '+relative)
            result[relative]=actual
        groups.append(result)
    for item in rules['snapshots']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('transcribed snapshot differs')
    if len(rules['snapshots'])!=16 or sum(v['queries'] for v in rules['snapshots'])!=8960:
        raise ValueError('exact retained input census')
    if sum(2*v['geometric_atoms']*(v['geometric_atoms']-1) for v in rules['snapshots'])!=51968:
        raise ValueError('retained pair census')
    return groups

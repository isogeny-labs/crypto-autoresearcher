"""Bind the complete inherited source and immutable conditioned public inputs."""
from copy import deepcopy
from hashlib import sha256
import subprocess
from deps21 import HERE,ROOT,prior,commitment
INPUTS=HERE/'inputs.json';NATIVE=HERE
ARMS=['direct_formal','aux_cancel_joint','sparse_joint']
PARAMETERS=dict(conditioned_cases=4,batch_solver_calls=12,execution_arms=ARMS,old_native_slots=32,formal_auxiliaries=16,
    maximum_native_width=48,maximum_joint_width=64,maximum_rows=4096,public_targets_per_case=8,cold_algebra=True,
    recollection=False,new_curve_holdouts=False,numeric_formal_labels=False)
BUDGET_INPUTS=[*prior.BUDGET_INPUTS,prior.HERE/'runs/a20-formal-pair-c4d124/execution.json',
    *[prior.HERE/('validation/'+name+'-postprocess-resource.json')for name in ('native-analysis','native-report','database-v24','raw-archive')]]
MODULES=['deps21','direct21','check21','custody21','streams21','driver21','prepare21','supervise21','analyze21']
SOURCES=list(dict.fromkeys([*[HERE/(v+'.py')for v in MODULES],*prior.SOURCES]))
digest,load,write_once,git,tools=prior.digest,prior.load,prior.write_once,prior.git,prior.tools


def expected_rules():
    run=prior.HERE/'runs/a20-formal-pair-c4d124';cases=[]
    for p in (262139,524287):
        for i in (0,1):
            cid='p'+str(p)+'-i'+str(i);prefix=run/'raw'/(cid+'.formalpair16.')
            def entry(suffix):
                path=__import__('pathlib').Path(str(prefix)+suffix+'.json')
                return dict(path=str(path.relative_to(ROOT)),sha256=digest(path))
            cases.append(dict(cell_id=cid,producer=dict(case=entry('case'),prepared=entry('prelude')),
                checker_only={k:entry(k)for k in ('aux_cancel_joint','sparse_joint','expanded-check')}))
    return dict(schema='prime-field-direct-formal-inputs/v1',conditioned_raw_commit='d1aecf8367ba8b9d7f622c57d6caaf03d70979c7',
        parent_source_commit='6c38d374472f7d2112e20aa9e17482f9a38e657f',cases=cases,parameters=PARAMETERS,
        new_native_targets=0,new_curves=0,rejected_collision_harvesting=False)


def validate_rules(rules):
    if commitment(rules)!=commitment(expected_rules()):raise ValueError('immutable four-case manifest differs')


def bindings(commit):
    rules=load(INPUTS);validate_rules(rules)
    inputs=[INPUTS,prior.HERE/'protocol.json',*BUDGET_INPUTS]
    for case in rules['cases']:
        inputs.extend(ROOT/v['path']for group in ('producer','checker_only')for v in case[group].values())
    groups=[]
    for paths in (SOURCES,inputs):
        values={}
        for p in paths:
            name=str(p.relative_to(ROOT));actual=digest(p)
            if sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=actual:raise ValueError('unpublished source/input: '+name)
            values[name]=actual
        groups.append(values)
    return groups

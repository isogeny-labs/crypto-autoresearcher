"""Prospective formal-pair dictionary closure; original deadline and fixed grid."""
from copy import deepcopy
from hashlib import sha256
import subprocess
from deps20 import HERE,ROOT,prior,commitment
INPUTS=HERE/'inputs.json';NATIVE=HERE
PROGRAMS=['norm32','unknown16','formalpair16','known16'];ARMS=[v for p in PROGRAMS for v in (p,'joint_on_'+p)]
PARAMETERS=deepcopy(prior.PARAMETERS)
PARAMETERS.update(programs=PROGRAMS,execution_arms=ARMS,case_systems=16,batch_solver_calls=32,information_diagnostics=16,export_execution_rows=32,
    formal_auxiliaries=16,expanded_semantic_oracles=4,rejected_collision_equations_used=False,definition_order='after_common_units_before_collection')
BUDGET_INPUTS=[*prior.BUDGET_INPUTS,prior.HERE/'runs/a19-unknown-pool-a8fa30/execution.json',
    *[prior.HERE/('validation/'+name+'-postprocess-resource.json')for name in ('native-analysis','native-report','database-v23','raw-archive','followup-literature')]]
MODULES=['deps20','formal_pool20','preparation20','native_case20','check_formal20','custody20','streams20','driver20','prepare20','supervise20','analyze20']
SOURCES=list(dict.fromkeys([*[HERE/(v+'.py')for v in MODULES],*prior.SOURCES]))
digest,load,write_once,git,tools=prior.digest,prior.load,prior.write_once,prior.git,prior.tools


def expected_rules():
    previous=load(prior.INPUTS);value=deepcopy(previous);generated=load(prior.HERE/'runs/a19-unknown-pool-a8fa30/raw/generated.json')
    value.update(schema='prime-field-formal-pair-inputs/v1',domain='prime-field-formal-pair-dictionary/20261107/v1',
        excluded_curves=previous['excluded_curves']+[[v['fixture']['p'],v['fixture']['b']]for v in generated['cells']],
        exclusion_sources=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p))for p in (prior.INPUTS,prior.HERE/'runs/a19-unknown-pool-a8fa30/raw/generated.json')],
        systems=16,solver_calls=32,information_audits=16,programs=PROGRAMS,base_arms=PROGRAMS,export_execution_rows=32,formal_pool_size=16,
        rejected_collision_equations_used=False,one_definition_per_distinct_nonold_sign_class=True,expanded_semantic_oracles=4)
    return value


def validate_rules(rules):
    if rules.get('software_control')is True:
        if not rules['fields']or any(v['p']>211 for v in rules['fields']):raise ValueError('marked p<=211 controls only')
        return
    expected=expected_rules()
    if commitment(rules)!=commitment(expected):raise ValueError('exact prospective formal-pair rules differ')
    if len(expected['excluded_curves'])!=44 or len({tuple(v)for v in expected['excluded_curves']})!=44:raise ValueError('exact44 exclusions required')


def rules_for(rules,program):
    if program not in PROGRAMS:raise ValueError('unknown cold program')
    value=deepcopy(rules);value.update(program_id=program,base_kind=program);return value


def descriptors(rules):
    index=0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            for program in PROGRAMS:
                yield index,dict(cell_id='p'+str(field['p'])+'-i'+str(ci),program=program,base_arm=program,source_schedule='ap0',source_prefix=128,
                    target_policy='general',target_horizon=8,target_prefix=8,scope='anchors')
                index+=1


def executions(rules):
    for i,d in descriptors(rules):
        yield i,d['program'],d;yield i,'joint_on_'+d['program'],d


def bindings(commit):
    rules=load(INPUTS);validate_rules(rules)
    inputs=[INPUTS,prior.HERE/'protocol.json',*[ROOT/v['path']for v in rules['exclusion_sources']],*BUDGET_INPUTS]
    groups=[]
    for paths in (SOURCES,inputs):
        group={}
        for p in paths:
            name=str(p.relative_to(ROOT));actual=digest(p)
            if sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=actual:raise ValueError('published source/input mismatch: '+name)
            group[name]=actual
        groups.append(group)
    return groups

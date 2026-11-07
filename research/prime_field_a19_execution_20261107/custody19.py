"""Prospective unknown-pool closure, fixed inputs and independent execution grid."""
from copy import deepcopy
from hashlib import sha256
import subprocess
from deps19 import HERE,ROOT,prior,commitment

INPUTS=HERE/'inputs.json';NATIVE=HERE
PROGRAMS=['norm32','unknown16','known16']
ARMS=[v for p in PROGRAMS for v in (p,'joint_on_'+p)]
PARAMETERS=dict(curves=4,targets=8,case_systems=12,batch_solver_calls=24,information_diagnostics=12,
    programs=PROGRAMS,execution_arms=ARMS,export_execution_rows=24,source_schedule='ap0',sources=128,
    old_norm_slots=32,auxiliary_slots=16,target_horizon=8,target_policy='general',maximum_native_width=48,
    maximum_joint_width=64,maximum_pair_entries=8192,maximum_rows=4096,maximum_affine_labels=8192,
    maximum_target_cache_points=64,pair_constructor='a15_batched',query_engines=['scalar','batch'])
BUDGET_INPUTS=[*prior.BUDGET_INPUTS,prior.HERE/'runs/a18-certified-transfer-8f1213/execution.json',
    *[prior.HERE/('validation/'+name+'-postprocess-resource.json')for name in ('native-report','database-v22','followup-literature')]]
MODULES=['deps19','pool19','geometry19','collection19','check_collection19','branch19','cancel19','information19',
    'check_algebra19','custody19','streams19','driver19','prepare19','supervise19','analyze19']
SOURCES=list(dict.fromkeys([*[HERE/(v+'.py')for v in MODULES],*prior.SOURCES]))
digest,load,write_once,git,tools=prior.digest,prior.load,prior.write_once,prior.git,prior.tools


def expected_rules():
    value=deepcopy(load(ROOT/'research/prime_field_a16_execution_20261107/inputs.json'))
    previous=load(prior.INPUTS);generated=load(prior.HERE/'runs/a18-certified-transfer-8f1213/raw/generated.json')
    value.update(schema='prime-field-unknown-pool-inputs/v1',domain='prime-field-unknown-pool-cancellation/20261107/v1',
        excluded_curves=previous['excluded_curves']+[[v['fixture']['p'],v['fixture']['b']]for v in generated['cells']],
        exclusion_sources=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p))for p in (prior.INPUTS,prior.HERE/'runs/a18-certified-transfer-8f1213/raw/generated.json')],
        seeds=[0],source_schedules=['ap0'],prefixes=[128],target_prefixes=[8],target_policies=['general'],
        systems=12,solver_calls=24,information_audits=12,scopes=['anchors'],norm_scopes=['anchors'],
        public_base_sizes=[16],base_arms=PROGRAMS,solvers=['aux_cancel_joint','sparse_joint'],programs=PROGRAMS,
        target_horizons=[8],short_target_prefixes=[8],maximum_target_cache_points=64,
        maximum_target_cache_points_by_horizon={'8':64},pool_size=16,maximum_pool_candidates=10000,
        maximum_native_width=48,maximum_joint_width=64,query_suppression=False,export_execution_rows=24)
    return value


def validate_rules(rules):
    if rules.get('software_control')is True:
        if not rules['fields']or any(v['p']>211 for v in rules['fields']):raise ValueError('marked p<=211 controls only')
        return
    expected=expected_rules()
    if commitment(rules)!=commitment(expected):raise ValueError('exact prospective unknown-pool rules differ')
    if len(expected['excluded_curves'])!=40 or len({tuple(v)for v in expected['excluded_curves']})!=40:raise ValueError('exact40 exclusions required')


def rules_for(rules,program):
    if program not in PROGRAMS:raise ValueError('unknown cold program')
    out=deepcopy(rules);out.update(program_id=program,base_kind=program)
    return out


def descriptors(rules):
    index=0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            for program in PROGRAMS:
                yield index,dict(cell_id='p'+str(field['p'])+'-i'+str(ci),program=program,base_arm=program,
                    source_schedule='ap0',source_prefix=128,target_policy='general',target_horizon=8,target_prefix=8,scope='anchors')
                index+=1


def executions(rules):
    for i,d in descriptors(rules):
        yield i,d['program'],d
        yield i,'joint_on_'+d['program'],d


def bindings(commit):
    rules=load(INPUTS);validate_rules(rules)
    inputs=[INPUTS,prior.HERE/'protocol.json',ROOT/'research/prime_field_a16_execution_20261107/inputs.json',
        *[ROOT/v['path']for v in rules['exclusion_sources']],*BUDGET_INPUTS]
    groups=[]
    for paths in (SOURCES,inputs):
        group={}
        for p in paths:
            name=str(p.relative_to(ROOT));actual=digest(p)
            if sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=actual:raise ValueError('published source/input mismatch: '+name)
            group[name]=actual
        groups.append(group)
    return groups


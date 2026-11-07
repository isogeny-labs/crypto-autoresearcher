"""Prospective fresh known-base query experiment: exact closure and execution map."""
from hashlib import sha256
import subprocess
from deps17 import HERE,ROOT,custody16

INPUTS=HERE/'inputs.json';NATIVE=HERE
PROGRAMS=['suppress','full'];ARMS=['suppress','full','joint_on_suppress','joint_on_full']
PARAMETERS=dict(curves=4,targets=8,programs=PROGRAMS,execution_arms=ARMS,case_systems=8,
    online_engine_executions=4,batch_solver_calls=12,joint_controls=8,export_execution_rows=16,
    supplied_known_base=48,target_horizon=24,target_policy='general',formal_endpoints_per_program=192,
    mandatory_natural_queries=8,source_queries=0,maximum_native_width=48,maximum_joint_width=64,
    maximum_pair_entries=8192,maximum_rows=4096,maximum_affine_labels=8192,maximum_target_cache_points=192,
    pair_constructor='a15_batched',query_engines=['scalar','batch'])
MODULES=['deps17','ownership17','preconstruct17','online17','query17','check_online17','check_construct17',
    'check_query17','check_span17','custody17','streams17','driver17','prepare17','supervise17','analyze17','cost17']
SOURCES=list(dict.fromkeys([*[HERE/(name+'.py') for name in MODULES],*custody16.SOURCES]))
digest,load,write_once,git,tools=custody16.digest,custody16.load,custody16.write_once,custody16.git,custody16.tools


def validate_rules(rules):
    if rules.get('software_control'):
        if not rules['fields'] or any(v['p']>211 for v in rules['fields']):raise ValueError('marked p<=211 preparation only')
        return
    expected=dict(schema='prime-field-certified-query-inputs/v1',domain='prime-field-certified-query-suppression/20261107/v1',
        fields=[dict(p=262139,base_size=32,bits=18),dict(p=524287,base_size=32,bits=19)],curves_per_field=2,a=2,
        maximum_curve_candidates=128,maximum_target_candidates=128,maximum_scalar_candidates=10000,maximum_base_candidates=10000,
        maximum_field_candidates=128,field_rule='largest_prime_below_power_of_two',sources=0,seeds=[],prerequisite=0,
        source_prefixes=[0],prefixes=[0],target_prefixes=[24],target_queries_per_point=24,target_horizons=[24],target_policies=['general'],
        targets=8,max_retained_rows=4096,max_pair_entries=8192,max_affine_labels=8192,systems=8,solver_calls=12,
        online_engine_executions=4,export_execution_rows=16,information_audits=0,base_arms=['known48'],scopes=['supplied'],
        public_base_sizes=[48],helpers=0,known_scope='supplied',programs=PROGRAMS,execution_arms=ARMS,source_free=True,
        program_id='known48_24',base_kind='known48',maximum_native_width=48,maximum_joint_width=64,maximum_target_cache_points=192,
        closed_curve_checkpoint=True,pair_constructor='a15_batched',query_engines=['scalar','batch'],operational_query_engine='batch',
        extra_query_order='step1..23_then_target0..7',full_construction_before_extra_queries=True,
        query_skip_rule='own_current_target_membership_and_prefix_native_and_public_certificate',native_supplied_labels_required=48,
        targets_drawn_after_both_base_builds=True,solvers=['partial_joint','sparse_joint'])
    if any(rules.get(k)!=v or type(rules[k])is not type(v) for k,v in expected.items()):raise ValueError('fixed prospective A17 rule differs')
    if set(rules)!=set(expected)|{'excluded_curves','exclusion_sources'}:raise ValueError('undeclared or stale A17 input field')


def descriptors(rules):
    index=0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid='p'+str(field['p'])+'-i'+str(ci)
            for arm in PROGRAMS:
                yield index,dict(cell_id=cid,program=arm,base_arm='known48',target_horizon=24,target_policy='general',scope='supplied')
                index+=1


def executions(rules):
    for index,descriptor in descriptors(rules):
        program=descriptor['program'];yield index,program,descriptor
        yield index,'joint_on_'+program,descriptor


def bindings(commit):
    rules=load(INPUTS);validate_rules(rules)
    inputs=[INPUTS,ROOT/'research/prime_field_a16_execution_20261107/protocol.continuation.json',
        *[ROOT/v['path'] for v in rules['exclusion_sources']]]
    groups=[]
    for paths in (SOURCES,inputs):
        group={}
        for path in paths:
            name=str(path.relative_to(ROOT));actual=digest(path)
            if sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=actual:raise ValueError('published source/input mismatch: '+name)
            group[name]=actual
        groups.append(group)
    for item in rules['exclusion_sources']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('exclusion source digest differs')
    previous=load(ROOT/rules['exclusion_sources'][0]['path']);generated=load(ROOT/rules['exclusion_sources'][1]['path'])
    expected=previous['excluded_curves']+[[v['fixture']['p'],v['fixture']['b']] for v in generated['cells']]
    if rules['excluded_curves']!=expected or len(expected)!=32 or len({tuple(v) for v in expected})!=32:raise ValueError('exact32 prior coefficient exclusions')
    return groups

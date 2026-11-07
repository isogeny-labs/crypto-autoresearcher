"""Exact A16 source/input closure and the prospective finite native census."""
from hashlib import sha256
import subprocess
from deps16 import HERE,ROOT,prior
from programs16 import PROGRAMS,descriptors

INPUTS=HERE/'inputs.json';NATIVE=HERE
PARAMETERS=dict(curves=4,targets=8,programs=[p['id'] for p in PROGRAMS],
    source_seeds=[0,1,2],sources=128,short_target_prefixes=[1,2,4,8],long_target_prefixes=[24],
    target_horizons=[8,24],systems=1260,solver_calls=2520,information_audits=576,
    maximum_native_width=48,maximum_joint_width=64,maximum_pair_entries=8192,maximum_rows=4096,
    maximum_affine_labels=8192,maximum_target_cache_points_by_horizon={'8':176,'24':560},
    pair_constructor='a15_batched',query_engines=['scalar','batch'])
MODULES=['deps16','programs16','collection16','ownership16','branch16','checks16','cold16',
    'custody16','streams16','driver16','supervise16','prepare16','analyze16']
SOURCES=list(dict.fromkeys([*[HERE/(n+'.py') for n in MODULES],*prior.SOURCES]))
digest,load,write_once,git,tools=prior.digest,prior.load,prior.write_once,prior.git,prior.tools


def validate_rules(rules):
    if rules.get('software_control'):
        if not rules['fields'] or any(v['p']>211 for v in rules['fields']):raise ValueError('marked tiny control only')
        return
    expected=dict(targets=8,sources=128,curves_per_field=2,a=2,seeds=[0,1,2],
        short_target_prefixes=[1,2,4,8],target_prefixes=[1,2,4,8],target_queries_per_point=8,
        target_policies=['walk','hash_offset','general'],norm_scopes=['relations','anchors'],known_scope='supplied',
        systems=1260,solver_calls=2520,information_audits=576,max_pair_entries=8192,max_retained_rows=4096,max_affine_labels=8192,
        programs=PARAMETERS['programs'],maximum_target_cache_points_by_horizon={'8':176,'24':560},pair_constructor='a15_batched',
        target_horizons=[8,24],closed_curve_checkpoint=True,prerequisite=64,known_sources=0,helpers=16,
        public_base_sizes=[16,32,48],solvers=['partial_joint','sparse_joint'],source_prefixes=[128],prefixes=[0,128],
        maximum_curve_candidates=128,maximum_target_candidates=128,maximum_field_candidates=128,
        maximum_scalar_candidates=10000,maximum_base_candidates=10000,field_rule='largest_prime_below_power_of_two',
        domain='prime-field-target-effort/20261107/v1',
        fields=[dict(p=262139,base_size=32,bits=18),dict(p=524287,base_size=32,bits=19)])
    if any(rules.get(k)!=v for k,v in expected.items()):raise ValueError('native fixed program rules differ')
    plans=list(descriptors(rules))
    if len(plans)!=1260 or sum(v['base_arm']=='hybrid' for _,v in plans)!=576:raise ValueError('exact native program census')


def bindings(commit):
    rules=load(INPUTS);validate_rules(rules)
    paths=[INPUTS,ROOT/'research/prime_field_a14_execution_20261106/protocol.json',
           *[ROOT/v['path'] for v in rules['exclusion_sources']]]
    groups=[]
    for group in (SOURCES,paths):
        values={}
        for path in group:
            relative=str(path.relative_to(ROOT));actual=digest(path)
            if sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=actual:
                raise ValueError('exact published source/input differs: '+relative)
            values[relative]=actual
        groups.append(values)
    for entry in rules['exclusion_sources']:
        if digest(ROOT/entry['path'])!=entry['sha256']:raise ValueError('prior exclusion provenance differs')
    old=load(ROOT/rules['exclusion_sources'][0]['path']);generated=load(ROOT/rules['exclusion_sources'][1]['path'])
    expected=old['excluded_curves']+[[v['fixture']['p'],v['fixture']['b']] for v in generated['cells']]
    if rules['excluded_curves']!=expected or len(expected)!=28 or len({tuple(v) for v in expected})!=28:
        raise ValueError('exact28 exclusion provenance')
    return groups


def methods(descriptor):return ['partial_joint','sparse_joint']
def export_arm(method):return dict(partial_joint='partial_known',sparse_joint='joint_reference')[method]
def arm_id(descriptor,method):return descriptor['program']+'.'+method

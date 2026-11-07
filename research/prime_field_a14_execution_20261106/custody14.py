"""A14 exact dependency/input closure and fixed prospective program census."""
from pathlib import Path
from shared import core

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE, INPUTS = HERE, HERE/'inputs.json'
prior = core.solver.module('_a14_prior_custody', 'research/prime_field_a13_execution_20261106/custody.py')
digest, load, write_once, git, tools = prior.digest, prior.load, prior.write_once, prior.git, prior.tools
PARAMETERS = dict(curves=4, targets=8, base_size=32, helpers=16,
    base_arms=['norm', 'hybrid', 'known32', 'known48'], public_base_sizes=[16, 32, 48],
    seeds=[0, 1, 2], sources=128, source_prefixes=[128], known_sources=0,
    target_prefixes=[1, 2, 4, 8], target_policies=['walk', 'hash_offset', 'general'],
    systems=1248, solver_calls=2496, information_audits=576,
    maximum_rows=4096, maximum_width=64, maximum_pair_entries=8192,
    query_engines=['scalar', 'batch'], operational_query_engine='batch')
LOCAL_MODULES = ['shared', 'guards', 'partial_solver', 'check_partial', 'geometry',
    'query_index', 'check_query', 'public_base', 'check_base', 'source_construct',
    'check_construct', 'target_cache', 'mixed_collection', 'check_mixed',
    'affine_branch', 'native_case', 'information', 'check_information',
    'custody14', 'streams14', 'driver14', 'supervise14', 'prepare14', 'cold14', 'analyze14']
SOURCES = list(dict.fromkeys([*[HERE/(name+'.py') for name in LOCAL_MODULES], *prior.SOURCES]))


def bindings(commit):
    from hashlib import sha256
    import subprocess
    groups = []
    paths = [INPUTS, ROOT/'research/prime_field_a13_execution_20261106/protocol.json',
             *[ROOT/item['path'] for item in load(INPUTS)['exclusion_sources']]]
    for group in (SOURCES, paths):
        values = {}
        for path in group:
            relative = str(path.relative_to(ROOT))
            actual = digest(path)
            if sha256(subprocess.check_output(['git', 'show', commit+':'+relative], cwd=ROOT)).hexdigest() != actual:
                raise ValueError('exact published source/input differs: '+relative)
            values[relative] = actual
        groups.append(values)
    for item in load(INPUTS)['exclusion_sources']:
        if digest(ROOT/item['path']) != item['sha256']:
            raise ValueError('prior coefficient exclusion provenance differs')
    return groups


def descriptors(rules):
    index = 0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid = 'p'+str(field['p'])+'-i'+str(ci)
            for base in rules['base_arms']:
                sources = base in ('norm', 'hybrid')
                schedules = [kind+str(seed) for seed in rules['seeds'] for kind in ('ap', 'hash')] if sources else ['known']
                for schedule in schedules:
                    for policy in rules['target_policies']:
                        for budget in rules['target_prefixes']:
                            for scope in (rules['norm_scopes'] if sources else [rules['known_scope']]):
                                yield index, dict(cell_id=cid, base_arm=base, source_schedule=schedule,
                                    source_prefix=rules['sources'] if sources else 0,
                                    target_policy=policy, target_prefix=budget, scope=scope)
                                index += 1


def methods(descriptor):
    return ['partial_joint', 'sparse_joint']


def export_arm(method):
    return dict(partial_joint='partial_known', sparse_joint='joint_reference')[method]


def arm_id(descriptor, method):
    return descriptor['base_arm']+'.'+method

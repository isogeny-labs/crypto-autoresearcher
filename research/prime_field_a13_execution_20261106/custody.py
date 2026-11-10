"""Exact A13 native closure, input custody and immutable-output utilities."""
from pathlib import Path
from baseline import core

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = HERE / 'inputs.json'
NATIVE = HERE
prior = core.solver.module('_a13_prior_custody', 'research/prime_field_a12_execution_20261106/common.py')
digest, load, write_once, git, tools = prior.digest, prior.load, prior.write_once, prior.git, prior.tools
PARAMETERS = dict(curves=4, targets=8, base_size=32, base_arms=['norm', 'known'],
    seeds=[0, 1, 2], sources=128, source_prefixes=[128], known_sources=0,
    target_prefixes=[1, 2, 4, 8], target_policies=['walk', 'hash_offset', 'general'],
    systems=624, solver_calls=1248, maximum_rows=4096, maximum_width=64,
    query_engines=['scalar', 'batch'], operational_query_engine='batch')
ARMS = ['norm_joint', 'norm_cancel', 'known_direct', 'known_joint']
SOURCES = list(dict.fromkeys([*[HERE / (name + '.py') for name in
    ('baseline', 'paid_base', 'known_solver', 'known_checks', 'known_collection',
     'custody', 'streams', 'driver', 'prepare', 'supervise', 'analyze', 'cold_costs')], *prior.SOURCES]))


def bindings(commit):
    from hashlib import sha256
    import subprocess
    groups = []
    inputs = [INPUTS, ROOT / 'research/prime_field_a12_execution_20261106/protocol.json',
              *[ROOT / v['path'] for v in load(INPUTS)['exclusion_sources']]]
    for paths in (SOURCES, inputs):
        values = {}
        for path in paths:
            relative = str(path.relative_to(ROOT))
            actual = digest(path)
            if sha256(subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=ROOT)).hexdigest() != actual:
                raise ValueError('source/input differs from exact published commit: ' + relative)
            values[relative] = actual
        groups.append(values)
    for item in load(INPUTS)['exclusion_sources']:
        if digest(ROOT / item['path']) != item['sha256']:
            raise ValueError('exclusion provenance bytes differ')
    return groups


def descriptors(rules):
    index = 0
    for field in rules['fields']:
        for ci in range(rules['curves_per_field']):
            cid = 'p' + str(field['p']) + '-i' + str(ci)
            for base in rules['base_arms']:
                schedules = [kind + str(seed) for seed in rules['seeds'] for kind in ('ap', 'hash')] if base == 'norm' else ['known']
                for schedule in schedules:
                    for policy in rules['target_policies']:
                        for budget in rules['target_prefixes']:
                            for scope in (rules['norm_scopes'] if base == 'norm' else [rules['known_scope']]):
                                yield index, dict(cell_id=cid, base_arm=base, source_schedule=schedule,
                                    source_prefix=rules['sources'] if base == 'norm' else 0,
                                    target_policy=policy, target_prefix=budget, scope=scope)
                                index += 1


def methods(descriptor):
    return ['sparse_joint', 'sparse_cancel'] if descriptor['base_arm'] == 'norm' else ['known_direct', 'sparse_joint']


def arm_id(descriptor, method):
    return ('norm_joint' if method == 'sparse_joint' else 'norm_cancel') if descriptor['base_arm'] == 'norm' else 'known_direct' if method == 'known_direct' else 'known_joint'


def export_arm(method):
    return 'joint_reference' if method == 'sparse_joint' else 'base_aware'

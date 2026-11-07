"""Exact prospective fixed-known48 transfer closure and declared field inputs."""
from copy import deepcopy
from hashlib import sha256
import subprocess
from deps18 import HERE,ROOT,prior,commitment

INPUTS=HERE/'inputs.json';NATIVE=HERE
PROGRAMS=list(prior.PROGRAMS);ARMS=list(prior.ARMS)
PARAMETERS=deepcopy(prior.PARAMETERS);PARAMETERS.update(field_bits=[20,21],certificate_origin_attribution=True)
BUDGET_INPUTS=[*prior.BUDGET_INPUTS,prior.HERE/'runs/a17-certified-query-178e0d/execution.json',
    *[prior.HERE/('validation/'+name+'-postprocess-resource.json') for name in ('native-report','database-v21','native-report-v2')]]
MODULES=['deps18','custody18','streams18','driver18','prepare18','supervise18','analyze18','check_query18']
SOURCES=list(dict.fromkeys([*[HERE/(v+'.py') for v in MODULES],*prior.SOURCES]))
digest,load,write_once,git,tools=prior.digest,prior.load,prior.write_once,prior.git,prior.tools


def expected_rules():
    value=deepcopy(load(prior.INPUTS));generated=load(prior.HERE/'runs/a17-certified-query-178e0d/raw/generated.json')
    value.update(schema='prime-field-certified-query-transfer-inputs/v1',domain='prime-field-certified-query-transfer/20261107/v1',
        fields=[dict(p=1048573,base_size=32,bits=20),dict(p=2097143,base_size=32,bits=21)],
        excluded_curves=value['excluded_curves']+[[v['fixture']['p'],v['fixture']['b']] for v in generated['cells']],
        exclusion_sources=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p)) for p in (prior.INPUTS,prior.HERE/'runs/a17-certified-query-178e0d/raw/generated.json')])
    return value


def validate_rules(rules):
    if rules.get('software_control')is True:
        if not rules['fields'] or any(v['p']>211 for v in rules['fields']):raise ValueError('marked p<=211 controls only')
        return
    expected=expected_rules()
    if commitment(rules)!=commitment(expected):raise ValueError('fixed prospective transfer rules differ')
    if len(expected['excluded_curves'])!=36 or len({tuple(v) for v in expected['excluded_curves']})!=36:raise ValueError('exact36 prior model exclusions')


def descriptors(rules):yield from prior.descriptors(rules)
def executions(rules):yield from prior.executions(rules)


def bindings(commit):
    rules=load(INPUTS);validate_rules(rules)
    inputs=[INPUTS,prior.HERE/'protocol.json',*[ROOT/v['path'] for v in rules['exclusion_sources']],*BUDGET_INPUTS]
    groups=[]
    for paths in (SOURCES,inputs):
        group={}
        for path in paths:
            name=str(path.relative_to(ROOT));actual=digest(path)
            if sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=actual:raise ValueError('published source/input mismatch: '+name)
            group[name]=actual
        groups.append(group)
    return groups

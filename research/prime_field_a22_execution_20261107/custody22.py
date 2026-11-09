"""Fixed fresh 20/21-bit transfer, original remaining budget and actual calls."""
from copy import deepcopy
from hashlib import sha256
import subprocess
from deps22 import HERE,ROOT,prior,acquisition,commitment
INPUTS=HERE/'inputs.v2.json';NATIVE=HERE
PROGRAMS=['norm32','unknown16','formalpair16','known16']
ARMS=[v for p in PROGRAMS for v in ([p,'joint_on_'+p,'direct_on_'+p]if p=='formalpair16'else[p,'joint_on_'+p])]
PARAMETERS=deepcopy(acquisition.PARAMETERS)
PARAMETERS.update(execution_arms=ARMS,batch_solver_calls=36,export_execution_rows=36,direct_formal_solver_calls=4,
    field_bits=[20,21],fields=[1048573,2097143],new_field_transfer=True)
BUDGET_INPUTS=[*prior.BUDGET_INPUTS,prior.HERE/'runs/a21-direct-formal-a4de6f/execution.json',
    *[prior.HERE/('validation/'+name+'-postprocess-resource.json')for name in ('native-analysis','native-report','database-v25','raw-archive')]]
MODULES=['deps22','custody22','streams22','driver22','prepare22','supervise22','analyze22']
SOURCES=list(dict.fromkeys([*[HERE/(v+'.py')for v in MODULES],*prior.SOURCES]))
digest,load,write_once,git,tools=prior.digest,prior.load,prior.write_once,prior.git,prior.tools


def expected_rules():
    previous=load(acquisition.INPUTS);value=deepcopy(previous);generated=load(acquisition.HERE/'runs/a20-formal-pair-c4d124/raw/generated.json')
    value.update(schema='prime-field-larger-formal-transfer-inputs/v1',domain='prime-field-larger-formal-transfer/20261107/v1',
        fields=[dict(p=1048573,base_size=32,bits=20),dict(p=2097143,base_size=32,bits=21)],
        excluded_curves=previous['excluded_curves']+[[v['fixture']['p'],v['fixture']['b']]for v in generated['cells']],
        exclusion_sources=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p))for p in (acquisition.INPUTS,acquisition.HERE/'runs/a20-formal-pair-c4d124/raw/generated.json')],
        solver_calls=36,export_execution_rows=36,direct_formal_solver_calls=4,new_field_transfer=True)
    return value


def validate_field_metadata(fields):
    """Configuration shape only; never select a prime or generate a curve."""
    for field in fields:
        if (set(field)!={'p','base_size','bits'}or any(type(field[k])is not int for k in field)or
            field['bits']not in (20,21)or field['p'].bit_length()!=field['bits']or field['base_size']!=32):
            raise ValueError('explicit field bits/p/base_size metadata required')


def validate_rules(rules):
    if rules.get('software_control')is True:
        if not rules['fields']or any(v['p']>211 for v in rules['fields']):raise ValueError('marked p<=211 controls only')
        return
    expected=expected_rules()
    validate_field_metadata(rules['fields'])
    if commitment(rules)!=commitment(expected):raise ValueError('exact fresh transfer rules differ')
    if len(expected['excluded_curves'])!=48 or len({tuple(v)for v in expected['excluded_curves']})!=48:raise ValueError('exact48 exclusions required')


def rules_for(rules,program):
    if program not in PROGRAMS:raise ValueError('unknown cold program')
    value=deepcopy(rules);value.update(program_id=program,base_kind=program);return value


def descriptors(rules):
    yield from acquisition.descriptors(rules)


def executions(rules):
    for i,d in descriptors(rules):
        yield i,d['program'],d;yield i,'joint_on_'+d['program'],d
        if d['program']=='formalpair16':yield i,'direct_on_'+d['program'],d


def bindings(commit):
    rules=load(INPUTS);validate_rules(rules)
    inputs=[INPUTS,acquisition.HERE/'protocol.json',prior.HERE/'protocol.json',*[ROOT/v['path']for v in rules['exclusion_sources']],*BUDGET_INPUTS]
    groups=[]
    for paths in (SOURCES,inputs):
        group={}
        for p in paths:
            name=str(p.relative_to(ROOT));actual=digest(p)
            if sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=actual:raise ValueError('published source/input mismatch: '+name)
            group[name]=actual
        groups.append(group)
    return groups

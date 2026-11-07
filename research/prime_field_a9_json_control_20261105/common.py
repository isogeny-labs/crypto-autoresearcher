"""Exact source, manifest and retained parent bindings; no solver calls."""
from hashlib import sha256
from pathlib import Path
import gzip,json,subprocess,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];NATIVE=HERE;INPUTS=HERE/'inputs.json'
PARAMETERS=dict(systems=288,solver_calls=1152,functional_control=True,targets=8,cold_rebuild=True,original_row_certificates=True,maximum_rows=4096,maximum_width=64)
ARMS=['dense_joint','dense_cancel','sparse_joint','sparse_cancel']
SOURCES=[HERE/(n+'.py') for n in ('common','core','check','driver','prepare','supervise','analyze')]+[
 *[ROOT/'research/prym_experiment_design_20261019/implementation'/(n+'.py') for n in ('arithmetic','independent','fixtures','relations')],
 *[ROOT/'research/prime_field_a4_execution_20261030'/(n+'.py') for n in ('core','check')],
 ROOT/'research/prime_field_a3_execution_20261030/core.py',ROOT/'research/prime_field_a8_execution_20261105/check.py',ROOT/'research/prym_factor_base_width_20261025/check_inputs.py',ROOT/'tools/curve_identity.py',
 ROOT/'research/p256_factor_base_parallel_20261026/runtime/checkpoint_gate.py',ROOT/'scripts/checkpoint.sh',ROOT/'src/crypto_autoresearcher/index_calculus/execution_gate.py',ROOT/'src/crypto_autoresearcher/index_calculus/curve.py',ROOT/'tools/experiment_protocol.py',ROOT/'schemas/experiment-protocol.v1.json',ROOT/'schemas/experiment-export.v1.json']

def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def load(path):
    path=Path(path);return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def write_once(path,value,compact=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=None if compact else 2,separators=(',',':') if compact else None,sort_keys=True);f.write('\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def bindings(commit):
    groups=[]
    for paths in (SOURCES,[*[ROOT/v['path'] for v in load(INPUTS)['prior_failed_attempt']['files'] if not v['path'].endswith('.gz')],INPUTS,HERE/'public-fixtures.json',ROOT/'research/prime_field_a7_execution_20261104/protocol.json',ROOT/'research/prime_field_a7_execution_20261104/runs/a7-source-budgets-d1f98d/raw/.artifacts.json',ROOT/'research/prime_field_a8_execution_20261105/runs/a8-cold-solvers-7f32b1/raw/.artifacts.json',ROOT/'research/prime_field_a8_execution_20261105/protocol.json']):
        result={}
        for p in paths:
            relative=str(p.relative_to(ROOT));sha=digest(p)
            if sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=sha:raise ValueError('source/input differs from pinned commit: '+relative)
            result[relative]=sha
        groups.append(result)
    check_parents();return groups

def check_parents():
    rules=load(INPUTS)
    if digest(ROOT/rules['public_fixtures']['parent_path'])!=rules['public_fixtures']['parent_sha256']:raise ValueError('parent public fixture bytes')
    if (ROOT/rules['public_fixtures']['parent_path']).read_bytes()!=(ROOT/rules['public_fixtures']['path']).read_bytes():raise ValueError('copied fixture differs')
    if digest(ROOT/rules['public_fixtures']['path'])!=rules['public_fixtures']['sha256']:raise ValueError('public fixtures hash')
    for item in rules['parent_files']+rules['a8_control_files']+rules['prior_failed_attempt']['files']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('parent raw hash')
    return rules

def tools():
    spec=importlib.util.spec_from_file_location('_a9json_protocol_tools',ROOT/'tools/experiment_protocol.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v


def remaining_watchdog(release,prior,now):
    """Enforce cumulative CPU/wall and original absolute deadline at launch."""
    from datetime import datetime
    from math import floor
    maximum=release['campaign_max_cpu_wall_seconds']
    remaining=floor(min(release['watchdog_seconds'],(datetime.fromisoformat(release['absolute_deadline'])-now).total_seconds(),maximum-prior['cpu_user_seconds']-prior['cpu_sys_seconds'],maximum-prior['diagnostic_wall_seconds']))
    if remaining<=0:raise ValueError('original cumulative deadline/allowance exhausted')
    return remaining


def observed_journal_work(events):
    """Charge completed outputs and failed solver prefixes, not finalized rows alone."""
    from collections import Counter
    completed={arm:Counter() for arm in ARMS};failed={arm:Counter() for arm in ARMS};shared=Counter();calls=0;failed_events=0;errors=0;started=set();checked=set()
    for event in events:
        kind=event['kind']
        if kind in ('case_started','case_checked'):
            identity=tuple(sorted(event['descriptor'].items()))
            (started if kind=='case_started' else checked).add(identity)
        if kind=='case_input':
            for phase in event['shared_phases']:shared.update(phase['counters'])
        elif kind=='solver_complete':
            result=event['result'];calls+=1;completed[result['arm']].update(result['counters'])
        elif kind=='solver_failed':
            failed_events+=1
            for phase in event['phases']:failed[event['arm']].update(phase['counters'])
        elif kind=='failure':errors+=1
    return dict(observed_completed_producer_calls=calls,failed_solver_events=failed_events,failure_events=errors,completed_arm_counters={a:dict(v) for a,v in completed.items()},failed_arm_phase_counters={a:dict(v) for a,v in failed.items()},observed_arm_counters={a:dict(completed[a]+failed[a]) for a in ARMS},shared_projection_counters=dict(shared),partial_work_unknown=bool(errors or failed_events or started-checked),coverage='Journalled completed outputs and solver_failed phase prefixes; a crash can leave unrecorded work, marked unknown. Inclusive processresources retained separately, never converted to Frunits.')

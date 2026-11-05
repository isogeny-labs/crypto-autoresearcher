"""Exact source, manifest and retained parent bindings; no solver calls."""
from hashlib import sha256
from pathlib import Path
import gzip,json,subprocess,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];NATIVE=HERE;INPUTS=HERE/'inputs.json'
PARAMETERS=dict(systems=288,targets=8,cold_rebuild=True,original_row_certificates=True,maximum_rows=4096,maximum_width=64)
ARMS=['full_joint','cancellation_first']
SOURCES=[HERE/(n+'.py') for n in ('common','core','check','driver','prepare','supervise','analyze')]+[
 *[ROOT/'research/prym_experiment_design_20261019/implementation'/(n+'.py') for n in ('arithmetic','independent','fixtures','relations')],
 *[ROOT/'research/prime_field_a4_execution_20261030'/(n+'.py') for n in ('core','check')],
 ROOT/'research/prime_field_a3_execution_20261030/core.py',ROOT/'research/prym_factor_base_width_20261025/check_inputs.py',ROOT/'tools/curve_identity.py',
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
    for paths in (SOURCES,[INPUTS,HERE/'public-fixtures.json',ROOT/'research/prime_field_a7_execution_20261104/protocol.json',ROOT/'research/prime_field_a7_execution_20261104/runs/a7-source-budgets-d1f98d/raw/.artifacts.json']):
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
    for item in rules['parent_files']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('parent raw hash')
    return rules

def tools():
    spec=importlib.util.spec_from_file_location('_a8_protocol_tools',ROOT/'tools/experiment_protocol.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v

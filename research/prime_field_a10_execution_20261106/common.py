"""Exact A10 source/input custody, immutable writes and prospective release helpers."""
from hashlib import sha256
from pathlib import Path
import gzip,json,subprocess,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];NATIVE=HERE;INPUTS=HERE/'inputs.json'
PARAMETERS=dict(curves=4,targets=8,seeds=[0,1,2],sources=128,prefixes=[0,8,16,24,32,48,64,96,128],systems=432,solver_calls=864,maximum_rows=4096,maximum_width=64)
ARMS=['sparse_joint','sparse_cancel']
SOURCES=[HERE/(n+'.py') for n in ('common','core','construct','solver','check','driver','prepare','supervise','analyze')]+[
 *[ROOT/'research/prym_experiment_design_20261019/implementation'/(n+'.py') for n in ('arithmetic','independent','fixtures','relations')],
 ROOT/'research/prime_field_a9_json_control_20261105/core.py',ROOT/'research/prime_field_a4_execution_20261030/core.py',ROOT/'research/prime_field_a4_execution_20261030/check.py',ROOT/'research/prime_field_a3_execution_20261030/core.py',ROOT/'research/prym_factor_base_width_20261025/check_inputs.py',ROOT/'tools/curve_identity.py',
 ROOT/'research/p256_factor_base_parallel_20261026/runtime/checkpoint_gate.py',ROOT/'scripts/checkpoint.sh',ROOT/'src/crypto_autoresearcher/index_calculus/execution_gate.py',ROOT/'src/crypto_autoresearcher/index_calculus/curve.py',ROOT/'src/crypto_autoresearcher/index_calculus/targets.py',ROOT/'src/crypto_autoresearcher/index_calculus/factor_base.py',ROOT/'src/crypto_autoresearcher/index_calculus/linalg.py',ROOT/'src/crypto_autoresearcher/index_calculus/__init__.py',ROOT/'tools/experiment_protocol.py',ROOT/'schemas/experiment-protocol.v1.json',ROOT/'schemas/experiment-export.v1.json']
SOURCES=list(dict.fromkeys([*SOURCES,*sorted((ROOT/'src/crypto_autoresearcher/index_calculus').glob('*.py')),ROOT/'src/crypto_autoresearcher/__init__.py']))

def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def load(path):
    path=Path(path)
    if not path.is_file():path=Path(str(path)+'.gz')
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def write_once(path,value,compact=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=None if compact else 2,separators=(',',':') if compact else None,sort_keys=True);f.write('\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def bindings(commit):
    groups=[]
    for paths in (SOURCES,[INPUTS,ROOT/'research/prime_field_a7_execution_20261104/protocol.json',*[ROOT/v['path'] for v in load(INPUTS)['exclusion_sources']]]):
        result={}
        for p in paths:
            relative=str(p.relative_to(ROOT));sha=digest(p)
            if sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=sha:raise ValueError('source/input differs from pinned commit: '+relative)
            result[relative]=sha
        groups.append(result)
    for item in load(INPUTS)['exclusion_sources']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('exclusion source hash')
    return groups
def tools():
    spec=importlib.util.spec_from_file_location('_a10_protocol',ROOT/'tools/experiment_protocol.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

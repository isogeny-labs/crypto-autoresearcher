"""A12 exact source/input custody and immutable output utilities."""
from hashlib import sha256
from pathlib import Path
import gzip,json,subprocess,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];NATIVE=HERE;INPUTS=HERE/'inputs.json'
PARAMETERS=dict(curves=4,targets=8,seeds=[0,1,2],sources=128,source_prefixes=[64,128],target_prefixes=[1,2,4,8],target_policies=['walk','hash_offset','general'],systems=1152,solver_calls=2304,maximum_rows=4096,maximum_width=64,query_engines=['scalar','batch'],operational_query_engine='batch')
ARMS=['sparse_joint','sparse_cancel']
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=module('_a12_prior_custody','research/prime_field_a11_execution_20261106/common.py')
SOURCES=list(dict.fromkeys([*[HERE/(n+'.py') for n in ('common','runtime_numpy','frontier','costs','batch_query','batch_check','source_collection','affine_core','affine_construct','affine_registry','affine_solver','affine_check','check_source','check_solver','streaming','driver','prepare','supervise','analyze')],*prior.SOURCES,ROOT/'research/prime_field_a10_execution_20261106/core.py',ROOT/'research/prime_field_a10_execution_20261106/construct.py',ROOT/'research/prime_field_a10_execution_20261106/solver.py',ROOT/'research/prime_field_a10_execution_20261106/check.py',ROOT/'src/crypto_autoresearcher/index_calculus/_accel.py']))
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
    for paths in (SOURCES,[INPUTS,ROOT/'research/prime_field_a11_execution_20261106/protocol.json',*[ROOT/v['path'] for v in load(INPUTS)['exclusion_sources']]]):
        values={}
        for path in paths:
            relative=str(path.relative_to(ROOT));sha=digest(path)
            if sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=sha:raise ValueError('source/input differs from exact published commit: '+relative)
            values[relative]=sha
        groups.append(values)
    for item in load(INPUTS)['exclusion_sources']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('exclusion bytes')
    return groups
def tools():return module('_a12_protocol_tools','tools/experiment_protocol.py')
def systems(rules):return len(rules['fields'])*rules['curves_per_field']*2*len(rules['seeds'])*len(rules['source_prefixes'])*len(rules['scopes'])*len(rules['target_policies'])*len(rules['target_prefixes'])

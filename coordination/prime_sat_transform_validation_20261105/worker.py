"""Prospective local validation worker. No candidate imports until main and cgroup/hash checks."""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    auth_path, output = map(Path, sys.argv[1:3])
    auth = json.loads(auth_path.read_text())
    if auth.get('execution_authorized') is not True:
        raise PermissionError('published exact-source admission required')
    if os.getuid() != auth['worker_uid']:
        raise PermissionError('worker must run as ec2-user, not root')
    repo = Path(auth['repository_root']).resolve()
    relative = next(x.split('::', 1)[1] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
    cg = Path('/sys/fs/cgroup') / relative.lstrip('/')
    raw = {name: (cg / name).read_text().strip() for name in ('cpu.max','memory.max','memory.swap.max')}
    quota, period = raw['cpu.max'].split()
    if quota == 'max' or int(quota) > int(period) or raw['memory.max'] == 'max' or int(raw['memory.max']) > 2147483648 or raw['memory.swap.max'] != '0':
        raise RuntimeError('actual kernel resource limits absent or too loose')
    (output/'resource-readback.json').write_text(json.dumps({'cgroup':relative,'properties':raw,'cpu_semantics':'quota is throttle to one CPU equivalent, not affinity','uid':os.getuid()},indent=2)+'\n')
    bindings = auth['bindings']
    for group in ('source16_sha256','baseline_sha256','runtime_files_sha256'):
        for name, expected in bindings[group].items():
            path = Path(name) if Path(name).is_absolute() else repo/name
            if sha(path) != expected:
                raise RuntimeError('input hash changed: '+name)
    # The external systemd RuntimeMaxSec already covers this import boundary.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(repo))
    token = {'execution_authorized':True,'source_sha256':auth['candidate_identity'],'attempt_index':auth['attempt_index']}
    if auth['role'] == 'producer':
        module = importlib.import_module('research.prime_sat_transform_integration_20261103.software_controls')
        result = module.run_suite(output/'raw',run_native=True,admission=token)
    elif auth['role'] == 'independent':
        path=repo/auth['independent_controls']['path']
        if sha(path)!=auth['independent_controls']['sha256']:
            raise RuntimeError('independent controls changed after publication')
        spec=importlib.util.spec_from_file_location('independent_transform_controls',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result=module.run_independent(output/'raw',admission=token)
    else:
        raise ValueError('unknown role')
    (output/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':
    try:
        main()
    except BaseException as error:
        try:
            out=Path(sys.argv[2]);(out/'worker-error.json').write_text(json.dumps({'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()},indent=2)+'\n')
        finally:
            raise

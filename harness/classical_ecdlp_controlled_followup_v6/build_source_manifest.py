#!/usr/bin/env python3
"""Build derived source locks; this command creates no approval or execution."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import source_closure

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', required=True, type=Path)
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    pins = {name: hashlib.sha256((HERE/'core'/name).read_bytes()).hexdigest()
            for name in source_closure.MATH_NAMES}
    driver = HERE/'driver.py'
    text = driver.read_text()
    changed = re.sub(r'^PINS=.*$', 'PINS='+repr(pins), text, count=1, flags=re.M)
    if a.write and changed != text:
        driver.write_text(changed)
    elif changed != text:
        raise SystemExit('dependency pins stale; run build_source_manifest.py --write')
    paths, _ = source_closure.collect(a.repo_root, HERE)
    lock = {'schema': 'controlled-followup-v6.source-lock/v1',
            'future_expected_capture_keyset': sorted(paths)}
    lock_bytes = (json.dumps(lock, indent=2)+'\n').encode()
    if a.write:
        (HERE/'source-lock.json').write_bytes(lock_bytes)
    elif (HERE/'source-lock.json').read_bytes() != lock_bytes:
        raise SystemExit('source keyset stale')
    files = {}
    for path in sorted(HERE.rglob('*')):
        if (path.is_file() and (path.suffix == '.py' or path.suffix == '.json' and 'verification' not in path.relative_to(HERE).parts)
                and path.name != 'source-manifest.json' and '__pycache__' not in path.parts):
            data = path.read_bytes()
            files[path.relative_to(HERE).as_posix()] = {
                'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    manifest = {'schema': 'controlled-followup-v6.source-manifest/v1',
                'sources': files, 'excludes': ['source-manifest.json'],
                'publication_binding': 'Native config names the actual published commit; this inventory binds content only.'}
    encoded = (json.dumps(manifest, indent=2)+'\n').encode()
    if a.write:
        (HERE/'source-manifest.json').write_bytes(encoded)
    elif (HERE/'source-manifest.json').read_bytes() != encoded:
        raise SystemExit('source content inventory stale')
    source_closure.reconstruct(a.repo_root, HERE)
    print(json.dumps({'sources': len(files), 'capture_keys': len(paths),
                      'write': a.write, 'scientific_draws': 0}))


if __name__ == '__main__':
    main()

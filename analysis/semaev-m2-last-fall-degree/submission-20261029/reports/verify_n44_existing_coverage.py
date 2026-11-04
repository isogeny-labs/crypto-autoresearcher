#!/usr/bin/env python3
"""Reconcile two expansion inputs with previously certified panel inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def reconcile(item, raw, publication, maker, python):
    request = load(raw / 'request.json')
    result = load(raw / 'result.json')
    acknowledgement = load(publication)
    assert item['degree'] == request['degree'] == result['degree'] == 4
    assert item['id'] == request['prior_id'] == result['prior_id']
    assert item['record'] == request['record']
    assert result['status'] == 'certificate_verified'
    assert result['last_fall_degree_lower_bound'] == 5
    assert result['certified_codimension_lower_bound'] > result['exact_solutions']
    assert all(result['steps'][step]['returncode'] == 0 and not result['steps'][step]['timeout']
               for step in ('produce', 'check', 'count'))
    with tempfile.TemporaryDirectory(prefix='n44-existing-coverage-') as temp:
        temp = Path(temp)
        record_path, generated = temp / 'record.json', temp / 'input.sys'
        record_path.write_text(json.dumps([item['record']]) + '\n')
        subprocess.run([python, str(maker), str(record_path), item['record']['name'],
                        str(generated)], check=True, capture_output=True, text=True)
        system_sha = sha(generated)
    assert system_sha == request['system_sha256'] == sha(raw / 'input.sys')
    certificate_sha = sha(raw / 'certificate.bin')
    assert certificate_sha == result['certificate_sha256'] == acknowledgement['certificate_sha256']
    checker = (raw / 'check.stdout.txt').read_text()
    pattern = r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)'
    match = re.search(pattern, checker)
    assert match and int(match.group(1)) == result['certified_codimension_lower_bound']
    assert int((raw / 'count.stdout.txt').read_text().strip()) == result['exact_solutions']
    if 'files' in acknowledgement:
        assert len(acknowledgement['files']) >= 1
        assert all('anonymous_url' in f and 'sha256' in f for f in acknowledgement['files'])
        assert 'anonymous HTTPS GET and SHA256 for every asset' in acknowledgement['checks']
    else:
        assert acknowledgement['anonymous_download_verified']
        assert acknowledgement['downloaded_certificate_hash_verified']
    return dict(id=item['id'], prior_result_id=result['id'], system_sha256=system_sha,
                certificate_sha256=certificate_sha,
                certified_codimension_lower_bound=result['certified_codimension_lower_bound'],
                exact_solutions=result['exact_solutions'],
                last_fall_degree_lower_bound=5,
                prior_request_sha256=sha(raw / 'request.json'),
                prior_result_sha256=sha(raw / 'result.json'),
                publication_sha256=sha(publication),
                source='previously completed and published panel input; no new closure')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expansion-plan', type=Path, required=True)
    p.add_argument('--maker', type=Path, required=True)
    p.add_argument('--prior03', type=Path, required=True)
    p.add_argument('--prior04', type=Path, required=True)
    p.add_argument('--publication03', type=Path, required=True)
    p.add_argument('--publication04', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--python', default=sys.executable)
    args = p.parse_args()
    plan = load(args.expansion_plan)
    items = {item['id']: item for item in plan['items']}
    rows = [reconcile(items[name], raw, publication, args.maker, args.python)
            for name, raw, publication in (
                ('fresh-n44-rand-03', args.prior03, args.publication03),
                ('fresh-n44-rand-04', args.prior04, args.publication04))]
    output = dict(schema='semaev.cross-campaign-coverage/v1',
                  expansion_plan_sha256=sha(args.expansion_plan),
                  maker_sha256=sha(args.maker),
                  rows=rows,
                  inference='Both named expansion inputs were certified in earlier panel runs.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'rows': len(rows), 'ids': [row['id'] for row in rows]}))


if __name__ == '__main__':
    main()

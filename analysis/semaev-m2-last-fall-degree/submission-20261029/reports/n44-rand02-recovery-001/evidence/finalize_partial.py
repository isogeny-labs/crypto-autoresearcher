#!/usr/bin/env python3
"""Close one interrupted D4 attempt using its retained certificate and replayed checker."""
import hashlib
import json
from pathlib import Path
import re


DATA = Path('/home/ec2-user/fall-degree-data-20261029')
ATTEMPT = DATA / 'expansion/fresh-n44-rand-02/attempt-001'
RECOVERY = DATA / 'n44-rand02-recovery-20261101'
NAME = 'fresh-n44-rand-02'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def semantic_lines(path):
    return [re.sub(r'\s+\[\d+(?:\.\d+)?s\]$', '', line)
            for line in path.read_text().splitlines()]


def main():
    request = json.loads((RECOVERY / 'request.json').read_text())
    replay = json.loads((RECOVERY / 'recheck-result.json').read_text())
    assert request['id'] == NAME and Path(request['source_attempt']) == ATTEMPT
    assert replay['request_sha256'] == digest(RECOVERY / 'request.json')
    assert replay['returncode'] == 0 and replay['certificate_sha256'] == request['certificate_sha256']
    assert digest(ATTEMPT / 'certificate.bin') == request['certificate_sha256']
    assert digest(ATTEMPT / 'check.stdout.txt') == request['original_checker_stdout_sha256']
    assert digest(RECOVERY / 'recheck.stdout.txt') == replay['recheck_stdout_sha256']
    assert digest(RECOVERY / 'recheck.stderr.txt') == replay['recheck_stderr_sha256']
    assert not (RECOVERY / 'recheck.stderr.txt').read_bytes()
    assert semantic_lines(ATTEMPT / 'check.stdout.txt') == semantic_lines(RECOVERY / 'recheck.stdout.txt')
    original = json.loads((DATA / 'expansion/plan.json').read_text())
    assert digest(DATA / 'expansion/plan.json') == request['original_plan_sha256']
    item, = (x for x in original['items'] if x['id'] == NAME and x['degree'] == 4)
    started = json.loads((ATTEMPT / 'started.json').read_text())
    assert started['plan_sha256'] == request['original_plan_sha256']
    assert started['parameters'] == item
    argv = json.loads((ATTEMPT / 'check.argv.json').read_text())
    assert argv == request['argv']
    record = item['record']
    assert argv[-(6 + len(record['V_basis_hex'])):] == [
        str(ATTEMPT / 'certificate.bin'), str(record['n']), record['modulus_hex'],
        str(record['a2']), record['a6_hex'], record['z_hex'], *record['V_basis_hex']]
    count = json.loads((DATA / 'expansion/counts' / NAME / 'attempt-001/result.json').read_text())
    assert count['status'] == 'completed' and count['returncode'] == 0
    assert count['plan_sha256'] == request['original_plan_sha256'] and count['parameters'] == record
    assert count['ordered_solutions'] == 2
    assert (DATA / 'expansion/counts' / NAME / 'attempt-001/count.stdout.txt').read_text().strip() == '2'
    output = (RECOVERY / 'recheck.stdout.txt').read_text()
    match = re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)', output)
    assert match and int(match[1]) == 31780
    assert 'W4_one 0' in (ATTEMPT / 'closure.stdout.txt').read_text()
    artifacts = {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size}
                 for p in ATTEMPT.iterdir() if p.is_file()}
    result = dict(schema='semaev.recovered-certificate-result/v1', id=NAME,
                  status='certificate_verified', parameters=item,
                  plan_sha256=request['original_plan_sha256'],
                  source_commit=started['source_commit'],
                  binary_sha256=started['binary_sha256'],
                  system_sha256=digest(ATTEMPT / 'input.sys'),
                  certificate_sha256=request['certificate_sha256'],
                  certificate_bytes=(ATTEMPT / 'certificate.bin').stat().st_size,
                  producer_contains_one=0,
                  certified_codimension_lower_bound=31780,
                  claim='1 not in W_4; exact count below checked codimension proves LFD at least 5',
                  recovery={'request_sha256': digest(RECOVERY / 'request.json'),
                            'recheck_result_sha256': digest(RECOVERY / 'recheck-result.json'),
                            'original_wrapper_exit': 'unobserved',
                            'closure_rerun': False,
                            'checker_replay_returncode': 0,
                            'checker_mathematical_lines_match': True},
                  artifacts=artifacts)
    save(ATTEMPT / 'result.json', result)
    canonical = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    inference = dict(id=NAME, last_fall_degree_lower_bound=5,
                     justification='Dossier Proposition 1.4: exact count 2 < independently checked codimension 31780',
                     count=count, closure_result_canonical_sha256=canonical,
                     scope='Recovered terminal evidence for this exact named Boolean presentation; no asymptotic inference.')
    inference_name = f'inference-{canonical}.json'
    save(ATTEMPT.parent / inference_name, inference)
    save(DATA / 'n43n44-d4-tail-local-001' / f'{NAME}.recovered.json',
         {'id': NAME, 'status': 'certificate_verified', 'result_sha256': digest(ATTEMPT / 'result.json'),
          'inference_files': [inference_name], 'recovery_request_sha256': digest(RECOVERY / 'request.json'),
          'original_owner_exit': 'unobserved'})
    print(json.dumps({'id': NAME, 'status': 'certificate_verified',
                      'checked_codimension': 31780, 'exact_solutions': 2,
                      'last_fall_degree_lower_bound': 5,
                      'result_sha256': digest(ATTEMPT / 'result.json')}), flush=True)


if __name__ == '__main__':
    main()

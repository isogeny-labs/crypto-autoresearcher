#!/usr/bin/env python3
"""Replay this source review's lightweight checks; no Lean build or primality claim."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
BASE = '23c5aeca09f8f512d90755193660c1b2aa509714'
PLAN = 'd549627b2737cd94bbd8a9ab26c248a66319d94b'
B1 = Path('research/endosweep_dk_exact_20261016')
B6 = Path('research/endosweep_dk_exact_batch6_20261105')
B7 = Path('research/endosweep_dk_exact_batch7_20261106')
LEAN = Path('formal/CryptoResearch/Endosweep/DkExactBatch7.lean')
TARGET = Path('formal/targets/endosweep-dk-exact-batch7-discriminants.yaml')
FACTOR_COMMIT = '752de68c3f96557981753dd63873789b5d00ff74'
result = {'base': BASE, 'plan': PLAN, 'checks': {}, 'inputs': {}}

def blob(path, revision=BASE):
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def record(name, condition, detail=None):
    assert condition, name
    result['checks'][name] = {'passed': True, 'detail': detail}

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

manifest = (ROOT / B7 / 'SHA256SUMS').read_text().splitlines()
source_paths = [B7 / line.split()[1] for line in manifest]
source_paths += [B7 / 'SHA256SUMS', B7 / 'README.md', B1 / 'make_factorizations.py',
                 B1 / 'build_dk_exact.py', B1 / 'lean/gen_dk_exact_lean.py', LEAN, TARGET]
for path in source_paths:
    data = (ROOT / path).read_bytes()
    record(f'base_bytes:{path}', data == blob(path) == blob(path, PLAN))
    result['inputs'][str(path)] = {'bytes': len(data), 'sha256': digest(data)}
for line in manifest:
    sha, name = line.split()
    record(f'manifest:{name}', digest((ROOT / B7 / name).read_bytes()) == sha)
factor_bytes = (ROOT / B7 / 'brainpoolP512r1.factors.json').read_bytes()
record('original_factor_commit_bytes', factor_bytes == blob(B7 / 'brainpoolP512r1.factors.json', FACTOR_COMMIT))
record('original_factor_commit_is_ancestor', subprocess.run(
    ['git', 'merge-base', '--is-ancestor', FACTOR_COMMIT, BASE], cwd=ROOT).returncode == 0)

doc = json.loads((ROOT / B7 / 'dk_exact.json').read_text())
row, = doc['curves']
fac, = [json.loads(line) for line in (ROOT / B7 / 'factorizations.jsonl').read_text().splitlines()]
factor = json.loads(factor_bytes)
survey_line, = (ROOT / B7 / 'provenance/survey_selected.jsonl').read_text().splitlines()
survey = json.loads(survey_line)
snap7 = json.loads((ROOT / B7 / 'provenance/driver_state.snapshot7.json').read_text())
snap6 = json.loads(blob(B6 / 'provenance/driver_state.snapshot6.json'))
event7 = (ROOT / B7 / 'provenance/driver_events.snapshot7.log').read_bytes()
event6 = blob(B6 / 'provenance/driver_events.snapshot6.log')
C = factor['cofactor_C152']
entry = snap7[C]
p54, p98 = [int(factor['factors'][k]) for k in ('p54', 'p98')]
record('curve_name', row['curve'] == fac['curve'] == factor['curve'] == survey['name'] == entry['curve'] == 'brainpool/brainpoolP512r1')
record('factor_record_snapshot_link', entry['C'] == C and entry['primes'] == [str(p54), str(p98)] and entry['open'] == [] and p54 * p98 == int(C))
record('snapshot_transition', set(snap6) == set(snap7) and len(snap7) == 43 and
       {e['curve'] for e in snap7.values() if not e['open']} - {e['curve'] for e in snap6.values() if not e['open']} == {row['curve']} and
       all(snap7[c] == e for c, e in snap6.items() if not e['open']))
record('snapshot_all_products', all(math.prod(int(x) for x in e['primes'] + e['open']) == int(c) for c, e in snap7.items()))
record('event_log_prefix', event7.startswith(event6), {'old_lines': len(event6.splitlines()), 'new_lines': len(event7.splitlines())})
record('survey_verbatim_prior_open', survey_line in blob(B6 / 'provenance/survey_open.jsonl').decode().splitlines())
record('raw_factor_event', f'2026-11-06T14:01:46Z brainpool/brainpoolP512r1: ECM B1=11000000 raw factor {p54} of C152' in event7.decode())
record('factorization_data_link', fac['factors'] == row['factorization'] == [['557', 1], [str(p54), 1], [str(p98), 1]] and
       int(fac['N']) == int(row['N_4q_minus_t2']) == 557 * int(C))
sys.path.insert(0, str(ROOT / B1))
builder = load_module('source_review_builder', B1 / 'build_dk_exact.py')
maker = load_module('source_review_maker', B1 / 'make_factorizations.py')
replay = maker.replay(int(C), [p54, p98], entry['log'])
record('found_by_replay', fac['found_by'] == row['found_by'] == ['PARI factor(N, 2^32) (survey, 10 s screen)', replay[p54], replay[p98]])
record('markdown_regeneration', builder.markdown(doc, B7.name) == (ROOT / B7 / 'dk_exact.md').read_text())

upstream_path = OUT / 'std-curves-brainpool-77fe6e3.json'
upstream_bytes = upstream_path.read_bytes()
upstream = {c['name']: c for c in json.loads(upstream_bytes)['curves']}
result['inputs'][str(upstream_path.relative_to(ROOT))] = {'bytes': len(upstream_bytes), 'sha256': digest(upstream_bytes)}
r, t = upstream['brainpoolP512r1'], upstream['brainpoolP512t1']
p, n, h = int(r['field']['p'], 16), int(r['order'], 16), int(r['cofactor'], 16)
record('pinned_source_parameters', (int(row['p']), int(row['n']), row['h'], int(row['t'])) ==
       (p, n, h, int(r['characteristics']['trace_of_frobenius'])) and int(row['t']) == p + 1 - h * n)
record('no_upstream_cm_disc', 'cm_disc' not in r['characteristics'])
# Constants transcribed from RFC 5639 section 3.7 during this review.
rfc_p = int('AADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3', 16)
rfc_n = int('AADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA70330870553E5C414CA92619418661197FAC10471DB1D381085DDADDB58796829CA90069', 16)
Z = int('12EE58E6764838B69782136F0F2D3BA06E27695716054092E60A80BEDB212B64E585D90BCE13761F85C3F1D2A64E3BE8FEA2220F01EBA5EEB0F35DBD29D922AB', 16)
record('rfc_p_n_h', (p, n, h) == (rfc_p, rfc_n, 1))
a, b = [int(r['params'][k]['raw'], 16) for k in ('a', 'b')]
at, bt = [int(t['params'][k]['raw'], 16) for k in ('a', 'b')]
record('rfc_isomorphism_coefficients', math.gcd(Z, p) == 1 and at == a * pow(Z, 4, p) % p and bt == b * pow(Z, 6, p) % p and at == p - 3)
record('curve_nonsingularity_residue', (4 * pow(a, 3, p) + 27 * b * b) % p != 0)
record('hasse_interval_numeric', (p + 1 - n) ** 2 <= 4 * p and n > 4 * math.isqrt(p) + 2)

generator = ROOT / B1 / 'lean/gen_dk_exact_lean.py'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONOPTIMIZE='0')
with tempfile.TemporaryDirectory(prefix='b7-source-review-') as temp:
    temp = Path(temp)
    output = temp / 'DkExactBatch7.lean'
    args = [sys.executable, str(generator), str(ROOT), str(output), '--dir', str(B7), '--module', 'DkExactBatch7', '--target', str(TARGET)]
    run = subprocess.run(args, capture_output=True, text=True, env=env)
    record('lean_regeneration', run.returncode == 0 and output.read_bytes() == (ROOT / LEAN).read_bytes(),
           {'returncode': run.returncode, 'stdout': run.stdout, 'generated_sha256': digest(output.read_bytes())})
    mutant = temp / B7
    mutant.mkdir(parents=True)
    mutated_doc = json.loads(json.dumps(doc))
    mutated_fac = json.loads(json.dumps(fac))
    bad = str(p54)[:-1] + '8'
    mutated_doc['curves'][0]['factorization'][1][0] = bad
    mutated_fac['factors'][1][0] = bad
    (mutant / 'dk_exact.json').write_text(json.dumps(mutated_doc))
    (mutant / 'factorizations.jsonl').write_text(json.dumps(mutated_fac) + '\n')
    args[2], args[3] = str(temp), str(temp / 'bad.lean')
    bad_run = subprocess.run(args, capture_output=True, text=True, env=env)
    record('digit_mutation_rejected', bad_run.returncode != 0 and 'AssertionError' in bad_run.stderr and not (temp / 'bad.lean').exists(),
           {'returncode': bad_run.returncode, 'stderr': bad_run.stderr})

result['primality_replayed'] = False
result['primality_reason'] = 'No gp executable or cypari2 module available; this script does not replace a primality proof.'
result['python'] = sys.version
(OUT / 'source-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'checks_passed': len(result['checks']), 'inputs_hashed': len(result['inputs']), 'primality_replayed': False,
                  'output': str(OUT / 'source-checks.json')}, indent=2))

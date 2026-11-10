"""Check (1) raw_result_sha256 in each stdout kv line against the base64 payload bytes;
(2) the producer's band input counts.json units equal the reader's unit construction from raw phases.
Usage: python3 -I check_counts_input.py <runs_dir> <counts.json> <decoded_runs.json>"""
import base64, hashlib, json, os, sys
runs_dir, counts_p, dec_p = sys.argv[1:4]
ok = bad = 0
for n in sorted(os.listdir(runs_dir)):
    if not n.endswith('.stdout.txt'):
        continue
    lines = open(os.path.join(runs_dir, n)).read().splitlines()
    kv = [l for l in lines if l.startswith('online_ms=')][0]
    want = dict(t.split('=', 1) for t in kv.split())['raw_result_sha256']
    raw = base64.b64decode([l for l in lines if l.startswith('raw_b64=')][0][8:])
    if hashlib.sha256(raw).hexdigest() == want: ok += 1
    else: bad += 1
print('raw_result_sha256 match', ok, 'mismatch', bad)
counts = json.load(open(counts_p))
print('counts.json top keys', sorted(counts)[:20], 'schema', counts.get('schema'), 'r_bits', counts.get('r_bits'), 'reference', counts.get('reference'))
arms = counts['arms']
print('arms', {a: (v['family'], len(v['units'])) for a, v in arms.items()})
dec = json.load(open(dec_p))
ph = {}
for x in dec:
    d = x['decoded']
    if d['arm'] == 'rT':
        ph[('rT', d['panel'])] = d['records'][0]['outcome']['charges_setup_and_solve']
        continue
    oc = [r['op_counts'] for r in d['records'] if isinstance(r.get('op_counts'), dict) and 'phases' in r['op_counts']][0]
    ph[(d['arm'], d['panel'])] = oc['phases']
UP = ('setup', 'linear_algebra', 'between_linear_algebra_and_targets', 'targets')
mism = []
for p in sorted(arms['rT']['units']):
    for arm, (k, c) in (('S', ('kS', 'cS')), ('P', ('kP', 'cP'))):
        u = dict(ph[(k, 's000')]['rank_stage'])
        for q in UP:
            for kk, v in ph[(c, p)][q].items():
                u[kk] += v
        if u != arms[arm]['units'][p]:
            mism.append((arm, p, {kk: (u.get(kk), arms[arm]['units'][p].get(kk)) for kk in set(u) | set(arms[arm]['units'][p]) if u.get(kk) != arms[arm]['units'][p].get(kk)}))
    if dict(ph[('rT', p)]) != arms['rT']['units'][p]:
        mism.append(('rT', p, (ph[('rT', p)], arms['rT']['units'][p])))
print('unit mismatches', len(mism), mism[:3])

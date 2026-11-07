"""Reader's own identity check of the counted replay (run 39882571652) against the archived
stacked twin (run 38862448935), on the fields PROTOCOL.md lines 56-66 lists, from raw stdout only.
Usage: python3 -I twin_identity.py decoded_runs.json decoded_twin.json"""
import json, sys, collections
new = json.load(open(sys.argv[1])); old = json.load(open(sys.argv[2]))
def idx(rows):
    m = collections.defaultdict(list)
    for x in rows:
        d = x['decoded']; m[(d['arm'], d['panel'])].append((x['file'], d))
    return m
N, O = idx(new), idx(old)
def tgt(d): return d['records'][0]
def summ(d):
    for r in d['records']:
        if r.get('kind') == 'compact_orbit_dlp_summary': return r
COLD = ('point_indices', 'x_codes', 'pinned_intermediates', 'probes', 'root_calls', 'relation_checks', 'skipped_symmetric_states', 'recovered_scalar')
RANK = ('rank_attempt_probes', 'rank_relations_blake3', 'rank_probes_total', 'rank_root_calls_total', 'rank_attempts', 'rank_relations', 'rank_failures', 'rank')
report = []
for key, lst in sorted(N.items()):
    arm, p = key
    olds = O.get(key, [])
    if arm == 'kS' or arm == 'kP':
        olds = [o for o in olds if o[0] == ('00042.stdout.txt' if arm == 'kS' else '00043.stdout.txt')]
    if not olds:
        report.append((key, 'NO_TWIN')); continue
    nd = lst[0][1]; od = olds[0][1]
    diffs = []
    if arm == 'rT':
        a, b = tgt(nd), tgt(od)
        if str(a['recovered_scalar']) != str(b['recovered_scalar']): diffs.append('scalar')
        if a['outcome']['charges_setup_and_solve'] != b['outcome']['charges_setup_and_solve']: diffs.append('charges')
    else:
        a, b = tgt(nd), tgt(od)
        if arm in ('cS', 'cP'):
            for f in COLD:
                if a.get(f) != b.get(f): diffs.append(f)
            sa, sb = summ(nd), summ(od)
            if sa.get('index_digest') != sb.get('index_digest'): diffs.append('index_digest')
        else:
            sa, sb = summ(nd), summ(od)
            for f in RANK:
                if sa.get(f) != sb.get(f): diffs.append(f)
            if str(a['recovered_scalar']) != str(b['recovered_scalar']): diffs.append('scalar')
            if sa.get('index_digest') != sb.get('index_digest'): diffs.append('index_digest')
    report.append((key, olds[0][0], 'identical' if not diffs else diffs))
bad = [r for r in report if r[-1] != 'identical']
print('compared', len(report), 'non-identical', len(bad), bad[:5])
print('twin cS/cP extra panels:', sorted(set(k[1] for k in O if k[0] in ('cS','cP')) - set(k[1] for k in N if k[0] in ('cS','cP'))))
for arm in ('kS','kP'):
    for f, d in O[(arm,'s000')] + O.get((arm,'s001'), []):
        s = summ(d); print(arm, f, d['panel'], 'rank_probes_total', s.get('rank_probes_total'), 'rank_attempts', s.get('rank_attempts'), 'rank', s.get('rank'))
    s = summ(N[(arm,'s000')][0][1]); print(arm, 'new', 'rank_probes_total', s.get('rank_probes_total'), 'rank_attempts', s.get('rank_attempts'), 'rank', s.get('rank'))

"""Proves-too-much and sensitivity controls for the reader's band recompute.

1. Raw-file perturbation (scratch copy): copy the 124 raw stdout files to a scratch dir,
   add DELTA to one counter (cS s007, phases.targets.root_index_probes) inside the base64
   payload of one file, re-encode, then (a) the reader's raw_result_sha256 check must flag
   exactly that file, (b) decode + protocol_band must move the S cells by the predicted amount.
2. Known-false conclusion: on the real data, 'S is cheaper than rT at every weight' must be
   refused (the order flips). Positive control: scale every IC unpriced counter by 1e-3 in a
   copy; the same rule must now rank S cheaper at every weight (the instrument can see an IC win).
3. Search every published S/P gap cell (band.md, BASELINES.md table) for a value < 1 at w >= 0.1.
Usage: python3 -I proves_too_much.py <runs_dir> <scratch_dir> <band.md> <BASELINES.md>
"""
import base64, hashlib, json, os, re, shutil, subprocess, sys

runs_dir, scratch, band_md, baselines_md = sys.argv[1:5]
here = os.path.dirname(os.path.abspath(__file__))
out = {}

# ---- 1. raw perturbation in a scratch copy
dst = os.path.join(scratch, 'runs_perturbed')
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(runs_dir, dst)
target_file = None
DELTA = 50_000_000
for n in sorted(os.listdir(dst)):
    if not n.endswith('.stdout.txt'):
        continue
    p = os.path.join(dst, n)
    lines = open(p).read().splitlines()
    raw_i = [i for i, l in enumerate(lines) if l.startswith('raw_b64=')][0]
    d = json.loads(base64.b64decode(lines[raw_i][8:]))
    if d['arm'] == 'cS' and d['panel'] == 's007':
        for r in d['records']:
            oc = r.get('op_counts')
            if isinstance(oc, dict) and 'phases' in oc:
                oc['phases']['targets']['root_index_probes'] += DELTA
                oc['end_to_end']['root_index_probes'] += DELTA
        lines[raw_i] = 'raw_b64=' + base64.b64encode(json.dumps(d, separators=(',', ':')).encode()).decode()
        open(p, 'w').write('\n'.join(lines) + '\n')
        target_file = n
out['perturbed_file'] = target_file
out['perturbation'] = 'cS s007 phases.targets.root_index_probes +%d (and end_to_end)' % DELTA

def run(args):
    return subprocess.run([sys.executable, '-I'] + args, capture_output=True, text=True, check=True).stdout

hash_out = run([os.path.join(here, 'check_counts_input.py'), dst,
                os.path.join(os.path.dirname(runs_dir), 'counts.json'), os.path.join(here, 'decoded_runs.json')])
out['hash_check_on_perturbed_copy'] = hash_out.splitlines()[0]
dec = os.path.join(scratch, 'decoded_perturbed.json')
run([os.path.join(here, 'decode_runs.py'), dst, dec])
pb = os.path.join(scratch, 'protocol_band_perturbed.json')
run([os.path.join(here, 'protocol_band.py'), dec, pb])
base = json.load(open(os.path.join(here, 'protocol_band.json')))['models']['protocol']
pert = json.load(open(pb))['models']['protocol']
cells = {}
for w in ('0', '0.1', '1'):
    b0 = base['gap']['S'][w][0]['ratio']; p0 = pert['gap']['S'][w][0]['ratio']
    rT = base['arms']['rT']['cost'][w][0]
    predicted = b0 + float(w) * DELTA / 20 / rT   # mean over 20 points
    cells[w] = {'baseline': b0, 'perturbed': p0, 'predicted': predicted, 'moved': p0 != b0,
                'matches_prediction': abs(p0 - predicted) < 1e-9 * max(1, predicted)}
    cells[w]['P_unchanged'] = base['gap']['P'][w][0]['ratio'] == pert['gap']['P'][w][0]['ratio']
out['perturbed_S_cells'] = cells

# ---- 2. known-false conclusion and positive control (in-memory copies of real units)
def rank_rule(costs_arm, costs_ref):
    signs = {(a > r) - (a < r) for a, r in zip(costs_arm, costs_ref)}
    return 'arm cheaper at every weight' if signs == {-1} else ('ref cheaper at every weight' if signs == {1} else 'unresolved')
S = base['arms']['S']; R = base['arms']['rT']
real = [S['mean_group'] + w * S['mean_unpriced'] for w in (0, 0.1, 1)]
ref = [R['mean_group'] + w * R['mean_unpriced'] for w in (0, 0.1, 1)]
out['known_false_IC_beats_rho_across_band_on_real_data'] = rank_rule(real, ref)
scaled = [S['mean_group'] + w * S['mean_unpriced'] * 1e-3 for w in (0, 0.1, 1)]
out['positive_control_IC_unpriced_x1e-3'] = {'costs': scaled, 'ref': ref, 'ruling': rank_rule(scaled, ref)}

# ---- 3. published cells < 1 at w >= 0.1
found = []
for path in (band_md, baselines_md):
    for ln, line in enumerate(open(path), 1):
        m = re.match(r'\s*\|\s*(S|P)( = k[SP] \+ c[SP])?\s*\|(.*)\|\s*$', line)
        if not m:
            continue
        cols = [c.strip() for c in m.group(3).split('|')]
        if len(cols) != 3 or not re.match(r'^[0-9]', cols[0]):
            continue
        heads = [float(re.match(r'([0-9.]+)', c).group(1)) for c in cols]
        found.append({'file': os.path.basename(path), 'line': ln, 'arm': m.group(1), 'w0': heads[0],
                      'w0.1': heads[1], 'w1': heads[2], 'IC_below_rho_at_w>=0.1': heads[1] < 1 or heads[2] < 1})
out['published_gap_rows'] = found
out['any_published_IC_win_at_w_ge_0.1'] = any(f['IC_below_rho_at_w>=0.1'] for f in found)
# the unpublished cell that WOULD show an IC win: cold arm alone (rank stage dropped)
cs = base['gap']['cS_only']['0.1'][0]
out['unpublished_cS_only_w0.1_if_rank_stage_dropped'] = cs
print(json.dumps(out, indent=1))

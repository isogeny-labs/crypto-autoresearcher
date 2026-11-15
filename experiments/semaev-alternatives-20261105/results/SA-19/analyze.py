"""thresholds (50% crossing, linear interpolation) with bootstrap CIs for the coord-mode form lattices; writes results/thresholds.json"""
import json, collections, numpy as np
rows = [json.loads(l) for l in open('/home/user/semaev-runs/SA-19/results/lattice.jsonl')]
rows = [r for r in rows if r['mode'] == 'coord']
cells = collections.defaultdict(dict)
for r in rows: cells[(r['name'], r['bits'])][r['delta']] = (r['success'], r['trials'])
def thr(rates):
    ds = sorted(rates); last = None
    for i, d in enumerate(ds):
        if rates[d] >= 0.5: last = i
    if last is None or last == len(ds) - 1: return None
    r0, r1 = rates[ds[last]], rates[ds[last + 1]]
    return ds[last] + (r0 - 0.5) / (r0 - r1) * (ds[last + 1] - ds[last])
rng = np.random.default_rng(0); out = []
for (name, bits), c in sorted(cells.items()):
    rates = {d: s / n for d, (s, n) in c.items()}; t = thr(rates); bs = []
    for _ in range(2000):
        rr = {d: rng.binomial(n, s / n) / n for d, (s, n) in c.items()}
        v = thr(rr)
        if v is not None: bs.append(v)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    # recovery counts at the two criterion points
    out.append(dict(name=name, bits=bits, threshold=round(t, 4), ci=[round(lo, 4), round(hi, 4)], n_bootstrap=len(bs),
                    rate_at_0_125=rates.get(0.125), rate_at_0_13=rates.get(0.13), rate_at_0_135=rates.get(0.135), rate_at_0_12=rates.get(0.12)))
    print(out[-1])
json.dump(out, open('/home/user/semaev-runs/SA-19/results/thresholds.json', 'w'), indent=1)

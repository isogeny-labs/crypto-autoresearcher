# Censoring-valid lower bound on the node-count exponent (no distributional model).
# For quantile level q: at B_lo the q-quantile of true nodes is <= U = q-quantile of observed nodes with
# timeouts/false negatives set to +inf (finite only if more than a q fraction solved); at B_hi the q-quantile of
# true nodes is >= L = q-quantile of observed nodes with timeouts kept at nodes-at-cap (a lower bound per run;
# false negatives set to their reported node count floor 1). If quantiles scale as B^alpha then
# alpha >= log2(L/U) / log2(B_hi/B_lo). Bootstrap over instances within each B. Appends to fits_table.md.
import json, math, random, collections
import numpy as np, sys
MET = sys.argv[1] if len(sys.argv) > 1 else 'nodes'
FLOOR = 1 if MET == 'nodes' else 0.01
rows = []
for f in ['raw_m2.jsonl', 'raw_m3.jsonl', 'raw2_m2.jsonl', 'raw2_m3.jsonl']:
    for l in open(f): rows.append(json.loads(l))
def cls(r):
    s = str(r['status'])
    if s == 'skipped': return 'skipped'
    if s == 'timelimit': return 'timeout'
    if r['verified'] is True: return 'ok'
    return 'false'
def q_upper(rs, q):
    v = sorted(max(r[MET], FLOOR) if cls(r) == 'ok' else math.inf for r in rs)
    return v[min(len(v) - 1, int(math.floor(q * len(v))))]
def q_lower(rs, q):
    v = sorted(max(r[MET] or FLOOR, FLOOR) for r in rs)
    return v[min(len(v) - 1, int(math.floor(q * len(v))))]
out = ["", f"## Censoring-valid lower bound on the quantile exponent (model-free), metric = {MET} (floor {FLOOR})", "",
       "alpha_q >= log2(L_q(B_hi)/U_q(B_lo)) / log2(B_hi/B_lo); timeouts enter as lower bounds, unsolved as +inf at B_lo.", "",
       "| m | form | q | B_lo -> B_hi (doublings) | U_q(B_lo) | L_q(B_hi) | lower bound on exponent | bootstrap 95% CI of the bound | n at B_lo / B_hi |",
       "|--|--|--|--|--|--|--|--|--|"]
rng = random.Random(1)
for m, (Blo, Bhi) in [(2, (16, 256)), (3, (4, 64))]:
    for form in ['raw', 'lll', 'vieta']:
        lo = [r for r in rows if r['m'] == m and r['form'] == form and r['B'] == Blo and cls(r) != 'skipped']
        hi = [r for r in rows if r['m'] == m and r['form'] == form and r['B'] == Bhi and cls(r) != 'skipped']
        d = math.log2(Bhi / Blo)
        for q in [0.1, 0.25, 0.4]:
            U = q_upper(lo, q); L = q_lower(hi, q)
            est = math.log2(L / U) / d if U < math.inf else -math.inf
            bs = []
            for _ in range(2000):
                a = [rng.choice(lo) for _ in lo]; b = [rng.choice(hi) for _ in hi]
                u = q_upper(a, q); l = q_lower(b, q)
                bs.append(math.log2(l / u) / d if u < math.inf else -math.inf)
            bs.sort()
            ci = (bs[int(.025 * len(bs))], bs[int(.975 * len(bs)) - 1])
            f = lambda x: '-inf' if x == -math.inf else f'{x:.2f}'
            out.append(f"| {m} | {form} | {q} | {Blo} -> {Bhi} ({d:.0f}) | {U:.3g} | {L:.3g} | {f(est)} | [{f(ci[0])}, {f(ci[1])}] | {len(lo)} / {len(hi)} |")
open('fits_table.md', 'a').write('\n'.join(out) + '\n')
print('\n'.join(out))

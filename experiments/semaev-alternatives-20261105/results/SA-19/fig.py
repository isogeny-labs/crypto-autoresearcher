"""SA-19 figure: (A) planted-recovery rate vs delta for the Edwards-y (budget 8) and Weierstrass-x (budget 9) form
lattices at 64/96/128 bits; (B) single-relation budget per coordinate class; (C) effective budget w/r of
multi-equation (modulus p) coefficient spaces.  Writes fig_sa19.png."""
import json, collections, glob
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
D = '/home/user/semaev-runs/SA-19/results/'
rows = [json.loads(l) for l in open(D + 'lattice.jsonl')]; rows = [r for r in rows if r['mode'] == 'coord']
cells = collections.defaultdict(dict)
for r in rows: cells[(r['name'], r['bits'])][r['delta']] = r['rate']
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
cols = {64: 'C0', 96: 'C1', 128: 'C2'}
for (name, bits), rates in sorted(cells.items()):
    ds = sorted(rates)
    ax[0].plot(ds, [rates[d] for d in ds], ('-o' if name == 'edwards_y' else '--s'), color=cols[bits], ms=4,
               label='%s %d bits' % ('Edwards y (w=8)' if name == 'edwards_y' else 'Weierstrass x (w=9)', bits))
ax[0].axvline(1 / 9, color='gray', ls=':'); ax[0].text(1 / 9, 1.02, '1/9', ha='center', fontsize=8)
ax[0].axvline(1 / 8, color='k', ls=':'); ax[0].text(1 / 8, 1.02, '1/8', ha='center', fontsize=8)
ax[0].axvline(1 / 9 + 0.02, color='r', ls='-.', lw=0.8); ax[0].text(1 / 9 + 0.02, 1.02, 'SUCCESS', color='r', ha='center', fontsize=8)
ax[0].axhline(0.5, color='gray', lw=0.5)
ax[0].set_xlabel('delta = log B / log p'); ax[0].set_ylabel('planted recovery rate (40 trials)'); ax[0].legend(fontsize=7); ax[0].set_title('A. form lattice, m = 2')
# B: budgets per coordinate class
co = json.load(open(D + 'coords.json')) + json.load(open(D + 'coords3.json'))
labs, ws = [], []
seen = set()
for r in co:
    if r.get('w') is None: continue
    key = r['label']
    if key in seen: continue
    seen.add(key); labs.append(key); ws.append(r['w'])
order = sorted(range(len(ws)), key=lambda i: ws[i])
ax[1].barh([labs[i] for i in order], [ws[i] for i in order], color=['C3' if ws[i] < 9 else 'C0' for i in order])
ax[1].axvline(9, color='gray', ls=':'); ax[1].set_xscale('log'); ax[1].set_xlabel('single-relation budget w (log scale)')
ax[1].tick_params(axis='y', labelsize=6); ax[1].set_title('B. budget by coordinate (pole divisor) class')
# C: multi-equation effective budgets
sym = json.load(open(D + 'sym_budget.json'))
sc = json.load(open(D + 'search_c.json'))
for fam, mk in (('sym_tot', 'o'), ('sym_box', 's')):
    pts = [(r['dim'], r['ratio']) for r in sym if r['family'] == fam and r['ratio']]
    ax[2].plot([p[0] for p in pts], [p[1] for p in pts], mk + '-', label=fam + ' (Vieta, valid lattice)')
for fam, mk in (('tot', '^'), ('box', 'v'), ('mult_tot', 'x')):
    pts = sorted((r['dim'], r['ratio']) for r in sc.get(fam, []) if r['ratio'])
    ax[2].plot([p[0] for p in pts], [p[1] for p in pts], mk + ':', alpha=0.6, label=fam + ' (non-symmetric W; counts only)')
ax[2].axhline(9, color='gray', ls=':'); ax[2].text(2, 9.2, 'w = 9 (S_3)', fontsize=8)
ax[2].axhline(8, color='k', ls=':'); ax[2].text(2, 7.4, 'w = 8 (Edwards y)', fontsize=8)
ax[2].set_xscale('log'); ax[2].set_xlabel('lattice dimension n'); ax[2].set_ylabel('effective budget w / r'); ax[2].legend(fontsize=7)
ax[2].set_title('C. multi-equation lattices, modulus p (m = 2)'); ax[2].set_ylim(6, 30)
plt.tight_layout(); plt.savefig('/home/user/semaev-runs/SA-19/fig_sa19.png', dpi=130)
print('saved')

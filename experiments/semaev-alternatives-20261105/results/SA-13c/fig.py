import json, math, os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
# (1) step (b): cov_b against Pi_J
for tag, mk in [('0_7', 'o'), ('2_5', 's'), ('m3_11', '^')]:
    rows = json.load(open('exp_b_rows_%s.json' % tag))
    P = np.array([r['PiJ'] for r in rows], float); c = np.array([r['cov'] for r in rows], float)
    ax[0].loglog(P, np.maximum(c, 0.5), mk, ms=4, alpha=.6, label='curve %s' % tag.replace('m', '-').replace('_', ','))
P = np.logspace(0, 19, 50); ax[0].loglog(P, P, 'k--', lw=1, label='cov_b = Pi_J (cost)'); ax[0].loglog(P, P ** (2 / 3), 'k:', lw=1, label='Pi_J^(2/3)')
ax[0].set_xlabel('Pi_J = prod_{W_j >= p} W_j/p'); ax[0].set_ylabel('cov_b (k*=1 branch, exact; 0 drawn at 0.5)')
ax[0].set_title('(b) general q(T): coverage vs cost'); ax[0].legend(fontsize=7)
# (2) volume inequality level 2
V = json.load(open('exp_vol_level2.json'))
for k, (key, mk) in enumerate([('(0, 7)', 'o'), ('(2, 5)', 's'), ('(-3, 11)', '^')]):
    bal = V[key]['balanced']
    ax[1].semilogx([b[0] ** 30 for b in bal], [b[2] for b in bal], mk + '-', label='balanced W=B^(8-j), curve %s' % key)
    ax[1].axhline(V[key]['sup'][0], color='C%d' % k, ls=':', lw=1)
ax[1].axhline(8.7, color='k', ls='--', lw=1, label='proved C_2 = 8.7'); ax[1].axhline(0.5, color='gray', ls='-.', lw=1, label='1/2 (balanced asymptote)')
ax[1].set_xlabel('omega'); ax[1].set_ylabel('c2 / omega^(1/15)'); ax[1].set_ylim(0, 1.2); ax[1].set_title('level-2 volume inequality (dotted: sup over tight boxes)')
ax[1].legend(fontsize=7)
# (3) H-sep-free enumeration
import re, ast
def parse_out(fn):
    rows = []; n = None
    for line in open(fn):
        m = re.match(r'p=\d+, \d+ x-coordinates, (\d+) pairs', line)
        if m: n = int(m.group(1))
        m = re.match(r'W=(\(.*?\)) log_p\(omega\)=([\d.]+) cost=(\d+) covered=(\d+) structural=(\d+) wrap_only=(\d+) flags=(\{.*?\}) heur_wrap=([\d.]+)', line)
        if m:
            rows.append(dict(W=ast.literal_eval(m.group(1)), log_p_omega=float(m.group(2)), cost=int(m.group(3)), covered=int(m.group(4)),
                             structural=int(m.group(5)), wrap_only=int(m.group(6)), x_with=ast.literal_eval(m.group(7)), heuristic_wrap=float(m.group(8))))
    return dict(n_pairs=n, rows=rows)
if os.path.exists('exp_a_caseA_out.txt'):
    A = parse_out('exp_a_caseA_out.txt'); rows = A['rows']; n = A['n_pairs']
    lo = np.array([r['log_p_omega'] for r in rows]); cov = np.array([r['covered'] for r in rows], float)
    sq = np.array([r['x_with'].get('A_sq', 0) for r in rows], float); st = np.array([r['structural'] for r in rows], float)
    hw = np.array([r['heuristic_wrap'] for r in rows], float); cost = np.array([r['cost'] for r in rows], float)
    o = np.argsort(lo)
    ax[2].semilogy(lo[o], np.maximum(cov[o], .3), 'ko-', label='covered pairs (exact, p=103)')
    ax[2].semilogy(lo[o], np.maximum(sq[o], .3), 'r^', label="pairs with a short-lift square u=c m'^2")
    ax[2].semilogy(lo[o], np.maximum(st[o], .3), 'bs', label='pairs with a structural certificate')
    ax[2].semilogy(lo[o], np.maximum(hw[o], .3), 'g:', label='random-wraparound heuristic 32 omega n/p^6')
    ax[2].axhline(n, color='gray', lw=1); ax[2].set_xlabel('log_p omega'); ax[2].set_ylabel('pairs (of %d)' % n)
    ax[2].set_title('(a) Lambda_x meets box, no H-sep: all coverage is short-lift squares'); ax[2].legend(fontsize=7)
plt.tight_layout(); plt.savefig('fig_sa13c.png', dpi=110); print('saved')

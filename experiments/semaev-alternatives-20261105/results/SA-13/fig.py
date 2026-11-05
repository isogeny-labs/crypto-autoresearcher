import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
r=json.load(open('exp3_rows.json')); e=json.load(open('exp1_rows.json'))
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
cols={72:'tab:blue',96:'tab:green',128:'tab:red'}
for pb in (72,96,128):
    for w,ls in ((False,'--'),(True,'-')):
        pts=[(x['delta'],x['success']/x['trials']) for x in r if x['p_bits']==pb and x['weighted']==w]
        ax[0].plot(*zip(*pts),ls,color=cols[pb],marker='o',ms=3,label=f"{pb} bit, {'weighted' if w else 'unweighted'}")
ax[0].axvline(1/12,color='gray',ls=':'); ax[0].axvline(1/9,color='k',ls=':')
ax[0].text(1/12+0.0005,0.05,'1/12',rotation=90,fontsize=8); ax[0].text(1/9+0.0005,0.05,'1/9',rotation=90,fontsize=8)
ax[0].set_xlabel('delta (B = p^delta)'); ax[0].set_ylabel('planted 2-decomposition recovered (40 trials)')
ax[0].set_title('3-dim kernel lattice: weights (B^4,B^3,B^2) move threshold 1/12 -> 1/9'); ax[0].title.set_fontsize(9); ax[0].legend(fontsize=7)
V=[x['V']/x['p'] for x in e]; fr=[x['frac_nonempty'] for x in e]; bd=[min(1,x['thm1_bound']) for x in e]; mc=[x['mean_count'] for x in e]
ax[1].loglog(V,fr,'o-',label='measured Pr[answer nonempty] (exact, all T in F_p)')
ax[1].loglog(V,bd,'k--',label='Theorem R1 bound min(1, D(V-1)/p), D=2')
ax[1].loglog(V,mc,'s-',label='mean list length')
ax[1].loglog(V,[max(1e-3,2*int(x['W'][0]*x['W'][1]*x['W'][2]/x['p'])) if x['W'][0]*x['W'][1]*x['W'][2]>=x['p'] else float('nan') for x in e],'^',label='van der Corput lower bound 2*floor(prod W/p)')
ax[1].set_xlabel('V/p, V = prod(2W_j+1)'); ax[1].set_title('exact check, p=100003, n=3, D=2',fontsize=9); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig('fig_sa13.png',dpi=130)

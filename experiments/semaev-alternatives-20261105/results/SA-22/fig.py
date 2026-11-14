import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('model_out.json'))['rows']
arms=list(dict.fromkeys(r['arm'] for r in d))
fig,ax=plt.subplots(figsize=(9,6))
for a in arms:
    pts=[(r['n'],r['log2_ratio']) for r in d if r['arm']==a and r['lam']==0.1 and r['log2_ratio']<1e9]
    ls='-' if a.startswith('PT') else '--'
    ax.plot(*zip(*pts),ls,marker='o',ms=3,label=a)
ax.axhline(0,color='k',lw=1); ax.axhline(40,color='r',lw=.8,ls=':')
ax.set_xlabel('log2 N (group order bits)'); ax.set_ylabel('log2( projected cost / rho )'); ax.set_title('SA-22: projected total cost relative to rho (unpriced work 0.1 GAE/field op)')
ax.legend(fontsize=6,loc='upper left'); fig.tight_layout(); fig.savefig('fig_sa22.png',dpi=130)

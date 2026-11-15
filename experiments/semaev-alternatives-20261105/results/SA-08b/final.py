import json,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
res=json.load(open('crossings.json'))
def mk(K,kind):
    A=2*K;S=[(u,v) for u in range(A+1) for v in range(A+1) if kind=='box' or u+v<=A+K]
    return sum(min(K,min(a,b)//2) for a,b in S)/sum(a+b for a,b in S)
print("Minkowski delta_K at K=200: box %.4f simplex %.4f"%(mk(200,'box'),mk(200,'simplex')))
print("lambda2 - GH crossing (planted, box):")
for bits in (48,64,96):
    print(bits,[(r['K'],round(r['cross_l2']-r['cross_gh'],4)) for r in sorted(res,key=lambda r:r['K']) if r['bits']==bits and r['kind']=='box' and r['planted'] and r['cross_gh'] and r['cross_l2']])
    ex=[(r['K'],round(r['cross_l2']-r['mink'],4)) for r in sorted(res,key=lambda r:r['K']) if r['bits']==bits and r['kind']=='box' and r['planted'] and r['cross_l2']]
    print(' excess over Minkowski',ex, 'monotone decreasing:',all(ex[i][1]>ex[i+1][1] for i in range(len(ex)-1)))
fig,ax=plt.subplots(figsize=(6.5,4.2))
for bits,c in ((48,'C0'),(64,'C1'),(96,'C2')):
    R=sorted([r for r in res if r['bits']==bits and r['kind']=='box' and r['planted'] and r['cross_l2']],key=lambda r:r['K'])
    ax.plot([1/r['K'] for r in R],[r['cross_l2'] for r in R],'o-',c=c,label=f'lambda_2 crossing, {bits} bit')
Ks=np.arange(1,13); ax.plot(1/Ks,[mk(k,'box') for k in Ks],'k--',label='Minkowski delta_K (determinant)')
ax.axhline(1/6,c='r',ls=':',label='1/6'); ax.axhline(1/6+.01,c='r',ls='-.',lw=.6,label='1/6+0.01 (SUCCESS bar)')
ax.set_xlabel('1/K'); ax.set_ylabel('delta'); ax.set_xlim(0,1.05); ax.legend(fontsize=7); plt.tight_layout(); plt.savefig('fig_crossing.png',dpi=130)

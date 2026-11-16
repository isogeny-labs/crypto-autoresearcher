import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,3,figsize=(15,4.2))
r=json.load(open('exp2_volume_rows_E3e+06.json'))
for k,v in r.items():
    d=v['by_decade_of_c']; xs=sorted(int(i) for i in d); ax[0].plot([10**x for x in xs],[d[str(x)] for x in xs],'o-',label='curve '+k)
ax[0].axhline(1.0,ls=':',c='gray'); ax[0].set_xscale('log'); ax[0].set_ylim(0,1.0); ax[0].set_xlabel('c = #covered pairs (decade)'); ax[0].set_ylabel('max c / (W0 W1 W2)^{2/9}')
ax[0].set_title('Volume inequality: worst ratio (proved bound 2.86 + O(1))'); ax[0].legend(fontsize=7)
rows=json.load(open('exp3_rows.json'))
for fam,(w1,w2) in {'(W1,W2)=(300,200)':(300,200),'(30,20)':(30,20)}.items():
    s=[x for x in rows if x['W'][1]==w1 and x['W'][2]==w2 and x['ratio_rest_to_GH']]
    ax[1].plot([x['omega_over_q'] for x in s],[x['ratio_rest_to_GH'] for x in s],'o-',label=fam)
ax[1].axhline(1,ls=':',c='gray'); ax[1].set_xscale('log'); ax[1].set_xlabel('omega / p^2'); ax[1].set_ylabel('mean list (T>=T*) / Gaussian heuristic'); ax[1].set_title('mod p^2, p=10007: equidistribution test'); ax[1].legend(fontsize=7)
for bits,c in ((96,'C0'),(64,'C1'),(52,'C2'),(40,'C3')):
    rr=json.load(open('exp6_rows_%d.json'%bits))
    ax[2].plot([x['B'] for x in rr],[np.median(x['nodes_list']) for x in rr],'o-',c=c,label='p ~ 2^%d (median nodes)'%bits)
B=np.array([4,8192]); ax[2].plot(B,B+1,'k:',label='B+1 (outer loop)')
ax[2].set_xscale('log',base=2); ax[2].set_yscale('log',base=2); ax[2].set_xlabel('B'); ax[2].set_ylabel('nodes visited'); ax[2].set_title('Square-restricted enumeration: cost ~ B^1'); ax[2].legend(fontsize=7)
plt.tight_layout(); plt.savefig('fig_sa13b.png',dpi=120)

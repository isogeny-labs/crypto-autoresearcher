import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rt=json.load(open('rank_table_comb.json')); th=json.load(open('theory_table_v2.json'))
fig,ax=plt.subplots(1,2,figsize=(10,3.8))
b=[str(r['bound']) for r in rt]
ax[0].bar([i-0.2 for i in range(len(rt))],[r['points'] for r in rt],0.4,label='distinct points')
ax[0].bar([i+0.2 for i in range(len(rt))],[r['rank'] for r in rt],0.4,label='rank of relation matrix')
ax[0].set_xticks(range(len(rt))); ax[0].set_xticklabels(['cond<=%s'%x for x in b]); ax[0].set_yscale('log'); ax[0].legend(); ax[0].set_title('Measured (levels 1,5,7,35)')
for i,r in enumerate(rt): ax[0].text(i+0.2,r['rank']*1.1+0.5,'%.2f'%r['ratio'],ha='center',fontsize=8)
ax[1].semilogx([t['B'] for t in th[1:]],[t['ratio'] for t in th[1:]],'o-',label='Euler-system rank / points (char. count, all inert-prime conductors <= B)')
ax[1].axhline(0.5,color='r',ls='--',label='success threshold 1/2'); ax[1].set_ylim(0,0.6); ax[1].set_xlabel('conductor bound B'); ax[1].legend(fontsize=7,loc='upper right'); ax[1].set_title('rank/points')
plt.tight_layout(); plt.savefig('fig_rank_ratio.png',dpi=130)

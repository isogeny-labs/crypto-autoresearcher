import json,bisect
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
meta=json.load(open('c37_4k/meta.json')); R=json.load(open('rank_37a1_4k.json'))['all_cumulative']
H={int(k):v for k,v in meta['H'].items()}; N=0; xs=[];ys=[]
for m in meta['conductors']:
    N+=H[m]
    if m>=15: xs.append(m); ys.append(R[str(m)][1]/N)
fig,ax=plt.subplots(1,2,figsize=(11,4))
ax[0].step(xs,ys,where='post',label='37a1 / 43a1 / 53a1, K=Q(sqrt-7)  (exact rank)')
ax[0].axvline(750,color='gray',ls=':')
ax[0].axhspan(0.12,0.15,color='C1',alpha=.15,label='frozen prediction [0.12,0.15]')
ax[0].axhline(0.15,color='r',ls='--',lw=1,label='KILL threshold 0.15'); ax[0].axhline(0.1254,color='g',ls=':',label='character-count limit 0.1254')
ax[0].set_xscale('log'); ax[0].set_xlabel('conductor bound B'); ax[0].set_ylabel('rank / points'); ax[0].set_ylim(0,0.3); ax[0].legend(fontsize=7); ax[0].set_title('SA-09c rank/points, B up to 4000')
d=json.load(open('descent30_summary.json'))
labs=['primary\n(60k targets)','replication\n(600k targets)']
for i,t in enumerate(('primary','replication')):
    x=d[t]; n=x['n_targets']; lo,hi=x['garwood95_rate']
    ax[1].errorbar(i,x['heegner_rate']*1e4,yerr=[[ (x['heegner_rate']-lo)*1e4],[(hi-x['heegner_rate'])*1e4]],fmt='o',color='C0',capsize=4,label='Heegner (Garwood 95%)' if i==0 else None)
    ax[1].plot(i+0.15,x['expected_hits_from_exact_Heegner_U']/n*1e4,'s',color='C3',label='exact |U|/#E (random-set control equal)' if i==0 else None)
ax[1].set_xticks([0,1]); ax[1].set_xticklabels(labs); ax[1].set_ylabel('hit rate x 1e4'); ax[1].legend(fontsize=7); ax[1].set_title('descent, p~2^30, 3 primes (37a1)')
plt.tight_layout(); plt.savefig('fig_09c.png',dpi=130)
import csv
rows=[]
for f in ('rank_37a1.json','rank_43a1.json','rank_53a1.json','rank_37a1_4k.json'):
    rows+=json.load(open(f))['rows']
w=csv.writer(open('results_rank_ratio_table.csv','w'))
w.writerow(['curve','B','conductors','points','relations','rank','ratio','char_count_rank','rank_eq_charcount'])
for r in rows: w.writerow([r['curve'],r['B'],r['conductors'],r['points'],r['relations'],r['rank'],round(r['ratio'],5),r['char_count_rank'],r['rank_eq_charcount']])

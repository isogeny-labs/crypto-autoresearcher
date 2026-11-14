import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def load(*fs):
    d={}
    for f in fs:
        for r in json.load(open(f)): d[r['B']]=r
    return [d[k] for k in sorted(d)]
series={'37a1 (non-CM), K=Q(sqrt-7), h=1':load('rank37.json','rank37_big.json','rank37_bigger.json','rank37_proj.json'),
        '36a1 (CM), K=Q(sqrt-47), h=5':load('rank36_47.json','rank36_47_bigger.json'),
        '36a1 (CM), K=Q(sqrt-23), h=3 (SA-09 field)':load('rank36_23.json','rank36_23_big.json')}
th={'37a1 (non-CM), K=Q(sqrt-7), h=1':'theory37.json','36a1 (CM), K=Q(sqrt-47), h=5':'theory36_47.json','36a1 (CM), K=Q(sqrt-23), h=3 (SA-09 field)':'theory36_23.json'}
fig,ax=plt.subplots(1,2,figsize=(12,4.5))
tab=[]
for (k,v),c in zip(series.items(),['C0','C1','C2']):
    ax[0].plot([r['B'] for r in v],[r['ratio'] for r in v],'o-',color=c,label=k+' (measured rank)')
    t=json.load(open(th[k])); ax[1].semilogx([r['B'] for r in t],[r['ratio'] for r in t],'s--',color=c,label=k)
    for r in v: tab.append({'curve_field':k,**{x:r[x] for x in ('B','conductors','points','relations','rank','ratio','character_count_rank')}})
ax[0].axhline(0.15,color='k',ls=':'); ax[0].text(5,0.152,'KILL threshold 0.15'); ax[0].set_xlabel('conductor bound B'); ax[0].set_ylabel('rank / points'); ax[0].set_title('Measured rank of Kolyvagin relation matrix'); ax[0].legend(fontsize=7)
ax[1].axhline(0.15,color='k',ls=':'); ax[1].set_xlabel('conductor bound B (log)'); ax[1].set_title('Character-count formula (equal to measured rank at every B tested)'); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig('fig_rank_ratio_09b.png',dpi=130)
json.dump(tab,open('results_rank_ratio_table.json','w'),indent=1)
import csv
w=csv.DictWriter(open('results_rank_ratio_table.csv','w'),fieldnames=list(tab[0])); w.writeheader(); w.writerows(tab)
print(all(r['rank']==r['character_count_rank'] for r in tab),len(tab))
for r in tab:
    if r['curve_field'].startswith('37'): print(r['B'],r['points'],r['rank'],round(r['ratio'],4))

import json,collections,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows=json.load(open('all_rows.json'))
fig,ax=plt.subplots(1,2,figsize=(11,4))
for (t,N,c) in ((1,4,'C0'),(2,6,'C1'),(3,6,'C2')):
    for bits,ls in ((56,'--'),(96,'-')):
        v=sorted([r for r in rows if r['t']==t and r['N']==N and r['bits']==bits and r['curve']=='small'],key=lambda r:r['delta'])
        if v: ax[0].plot([r['delta'] for r in v],[r['success']/r['trials'] for r in v],ls,color=c,label=f"t={t},N={N},{bits}b")
ax[0].axvline(1/6,color='k',ls=':');ax[0].text(1/6,.5,'1/6',rotation=90)
ax[0].set_xlabel('delta=log_p B');ax[0].set_ylabel('planted recovery rate');ax[0].legend(fontsize=7);ax[0].set_title('LLL determinant oracle (measured)')
th=json.load(open('theory_out.json'))
Ns=[2,3,4,5,6,8,10,16,24,40]
for t in (1,2,3,4,6,10): ax[1].plot(Ns,[th['rect'][str(t)][str(n)] for n in Ns],marker='o',label=f"t={t}")
ax[1].axhline(1/6,color='k',ls=':');ax[1].set_xscale('log');ax[1].set_xlabel('N (square [0..N]^2)');ax[1].set_ylabel('provable delta');ax[1].legend(fontsize=7);ax[1].set_title('Provable threshold sum(u)/sum(w)')
plt.tight_layout();plt.savefig('fig_sa18.png',dpi=130)

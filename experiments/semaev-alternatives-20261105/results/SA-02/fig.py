import json, numpy as np, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
for pb,c in ((40,'C0'),(52,'C1'),(64,'C2')):
    rows=json.load(open(f'sieve_u_p{pb}.json'))
    ax[0].loglog([r['B'] for r in rows],[r['mean_time'] for r in rows],'o-',c=c,label=f'u-sieve (PARI), {pb}-bit p')
Bg=np.array([64,32768.]); ax[0].loglog(Bg,2e-5*Bg/ 1.0,'k--',lw=.8,label='slope 1')
ax[0].set_xlabel('B'); ax[0].set_ylabel('mean time to recovery (s)'); ax[0].legend(fontsize=7); ax[0].set_title('Per-u sieve: exponent ~1.0')
for f,lab,c in (('batch_ctrl_p64_t2.json','window, plain (x1,v), t=2','C3'),('batch_conic_p64_t2.json','window, conic (e1,v), t=2','C4'),('batch_ctrl_p64_t3_none.json','window, plain (x1,v), t=3','C5')):
    if os.path.exists(f):
        rows=json.load(open(f)); ok=[r for r in rows if r['succ']>=0.8*r['n']]
        ax[1].loglog([r['B'] for r in ok],[r['exp_time'] for r in ok],'s-',c=c,label=lab)
rows=json.load(open('sieve_u_p64.json')); ax[1].loglog([r['B'] for r in rows],[r['mean_time'] for r in rows],'o-',c='C2',label='per-u sieve, 64-bit')
ax[1].set_xlabel('B'); ax[1].set_ylabel('expected time to recovery (s)'); ax[1].legend(fontsize=7); ax[1].set_title('Batch-window lattice (64-bit p), recovered rows only')
plt.tight_layout(); plt.savefig('fig_sa02.png',dpi=130)

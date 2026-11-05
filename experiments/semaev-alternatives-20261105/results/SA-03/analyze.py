import json,glob,math,random
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng=np.random.default_rng(3)
# ---------- census ----------
recs=[]
for f in sorted(glob.glob('census_p*.jsonl')):
    recs+= [json.loads(l) for l in open(f)]
recs.sort(key=lambda r:(r['pbits'],r['B']))
rows=[]
def slope(xs,ys):
    return np.polyfit(np.log(xs),np.log(ys),1)[0]
lines=["| p bits | B | targets | M=B^4 | mean N_sq (planted) | 4B^10/p | mean N_sq (random ctrl) | mean N_pos (mode1) | mean N_Dall | mean N_both | mean N_dec | min N_dec | ratio N_both/N_sq | planted in box |","|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
byp={}
for r in recs:
    T=r['targets']; n=len(T)
    nsq=np.mean([t['Nsq'] for t in T]); both=np.mean([t['Nboth'] for t in T]); dec=np.mean([t['Ndec'] for t in T])
    ctrl=np.mean([t['Nsq'] for t in r['controls']]) if r['controls'] else float('nan')
    cdec=np.mean([t['Ndec'] for t in r['controls']]) if r['controls'] else float('nan')
    cboth=np.mean([t['Nboth'] for t in r['controls']]) if r['controls'] else float('nan')
    npos=np.mean([t['Npos'] for t in T]) if r['mode']==1 else float('nan')
    nd=np.mean([t['NDall'] for t in T]) if r['mode']==1 else float('nan')
    lines.append(f"| {r['pbits']} | {r['B']} | {n} | {r['M']} | {nsq:.4g} | {r['est_Nsq']:.4g} | {ctrl:.4g} | {npos:.4g} | {nd:.4g} | {both:.4g} | {dec:.4g} | {min(t['Ndec'] for t in T)} | {both/nsq:.3g} | {r['planted_in_box']}/{n} |")
    byp.setdefault(r['pbits'],[]).append((r,T))
    r['_ctrl']=(cdec,cboth)
open('census_table.md','w').write("\n".join(lines)+"\n")
print("\n".join(lines))
ctrl_lines=["| p bits | B | control targets | mean N_sq | max N_dec | max N_both |","|---|---|---|---|---|---|"]
for r in recs:
    if r['controls']:
        C=r['controls']; ctrl_lines.append(f"| {r['pbits']} | {r['B']} | {len(C)} | {np.mean([c['Nsq'] for c in C]):.4g} | {max(c['Ndec'] for c in C)} | {max(c['Nboth'] for c in C)} |")
open('census_controls.md','w').write("\n".join(ctrl_lines)+"\n"); print("\n".join(ctrl_lines))
# ratio exponent fit: per prime, configs with mean Nsq>=20
fit_lines=["| p bits | B range used | #configs | fitted c (ratio ~ B^-c) | bootstrap 95% CI |","|---|---|---|---|---|"]
fits={}
for pb,lst in sorted(byp.items()):
    use=[(r,T) for r,T in lst if np.mean([t['Nsq'] for t in T])>=20]
    if len(use)<3: 
        fit_lines.append(f"| {pb} | - | {len(use)} | not enough configs with N_sq>=20 | |"); continue
    Bs=np.array([r['B'] for r,T in use],float)
    def fitfun(sample):
        ys=[np.mean([t['Nboth'] for t in s])/np.mean([t['Nsq'] for t in s]) for s in sample]
        return -slope(Bs,ys)
    base=fitfun([T for r,T in use])
    bs=[]
    for _ in range(1000):
        sam=[[T[i] for i in rng.integers(0,len(T),len(T))] for r,T in use]
        bs.append(fitfun(sam))
    lo,hi=np.percentile(bs,[2.5,97.5]); fits[pb]=(base,lo,hi,Bs)
    fit_lines.append(f"| {pb} | {int(Bs.min())}-{int(Bs.max())} ({math.log2(Bs.max()/Bs.min()):.1f} doublings) | {len(use)} | {base:.2f} | [{lo:.2f}, {hi:.2f}] |")
open('census_fit.md','w').write("\n".join(fit_lines)+"\n"); print("\n".join(fit_lines))
# sieve table
Q=[3,5,7,11,13]
Im={}
for q in Q:
    s=set()
    for x1 in range(q):
        for x2 in range(q):
            s.add((((x1*x2)**2-28*(x1+x2))%q,(-2*(x1*x2*(x1+x2)+14))%q,((x1-x2)**2)%q))
    Im[q]=len(s)
sl=["| p bits | B | N_sq | iterations (work) | survivors after q=3 | 3,5 | 3,5,7 | 3,5,7,11 | 3,5,7,11,13 | predicted fraction (prod Im/q^3 * ... ) | measured fraction (all 5) | image cosets prod|Im| |","|---|---|---|---|---|---|---|---|---|---|---|---|"]
pred=1.0
for q in Q: pred*=Im[q]/q**3
sieve_rows=[]
for r in recs:
    T=r['targets']
    if np.mean([t['Nsq'] for t in T])<1000: continue
    n0=np.mean([t['surv'][0] for t in T]); sv=[np.mean([t['surv'][k] for t in T]) for k in range(1,6)]
    it=np.mean([t['Niter'] for t in T])
    sl.append(f"| {r['pbits']} | {r['B']} | {n0:.4g} | {it:.4g} | "+" | ".join(f"{x:.4g}" for x in sv)+f" | {pred:.3g}x(sq-leading adj.) | {sv[-1]/n0:.3g} | {np.prod([Im[q] for q in Q]):.3g} |")
    # cost model: prefix of primes: setups = prod Im (cosets) ; candidates = survivors
    best=None
    for k in range(0,6):
        setups=float(np.prod([Im[q] for q in Q[:k]])) if k else 1.0
        cand=n0 if k==0 else sv[k-1]
        cost=setups+cand
        if best is None or cost<best[0]: best=(cost,k,setups,cand)
    sieve_rows.append(dict(pbits=r['pbits'],B=r['B'],Nsq=n0,Niter=it,best_cost=best[0],best_k=best[1]))
open('sieve_table.md','w').write("\n".join(sl)+"\n"+"\n"+json.dumps(Im)+"\n"); print("\n".join(sl)); print(Im)
json.dump(sieve_rows,open('sieve_rows.json','w'),indent=1)
for s in sieve_rows: print(s)
# ---------- figure ----------
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
cols={20:'C0',24:'C1',28:'C2',32:'C3'}
for pb,lst in sorted(byp.items()):
    Bs=[r['B'] for r,T in lst]; ns=[np.mean([t['Nsq'] for t in T]) for r,T in lst]; rt=[np.mean([t['Nboth'] for t in T])/np.mean([t['Nsq'] for t in T]) for r,T in lst]
    ax[0].loglog(Bs,rt,'o-',color=cols.get(pb),label=f'p~2^{pb}')
Bg=np.array([6,8,11,16,23,32,45,64,91.])
for pb in byp: 
    p=2**pb; ax[0].loglog(Bg,np.minimum(1,p/(4*Bg**10)),':',color=cols.get(pb),lw=1)
ax[0].set_xlabel('B'); ax[0].set_ylabel('structured / small square-leading forms'); ax[0].set_title('Census ratio (dotted: p/(4B^10))'); ax[0].legend()
json.dump({str(k):[float(v[0]),float(v[1]),float(v[2])] for k,v in fits.items()},open('census_fit.json','w'))
plt.tight_layout(); plt.savefig('fig_census.png',dpi=130)

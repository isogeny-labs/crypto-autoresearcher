import json,glob,math,sympy as sp
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rng=np.random.default_rng(11)
def slope(x,y): return np.polyfit(np.log(x),np.log(y),1)[0]
def boot_slope(x,y,nb=2000):
    x=np.array(x,float);y=np.array(y,float);n=len(x);b=[]
    for _ in range(nb):
        i=rng.integers(0,n,n)
        if len(set(i))<3: continue
        b.append(slope(x[i],y[i]))
    return slope(x,y),np.percentile(b,[2.5,97.5])
out=[]
# ---------- (b) by-discriminant sweep ----------
bd={}
for f in sorted(glob.glob('bydisc_p*.jsonl')):
    for l in open(f):
        r=json.loads(l); bd.setdefault(r['pbits'],[]).append(r)
tab=["| p bits | B | |F| pairs (|S_F|) | targets found | CVP calls | lattice i-steps | lattice candidates | square-S candidates | integral c0 (exact forms) | total sweep work W |","|---|---|---|---|---|---|---|---|---|"]
W={}
for pb,lst in sorted(bd.items()):
    for r in lst:
        rc=r['recs']; m=lambda k: np.mean([x['ops'][k] for x in rc])
        w=m('cvp')+m('isteps')+m('cands')
        tab.append(f"| {pb} | {r['B']} | {rc[0]['npairs']} | {sum(x['found'] for x in rc)}/{len(rc)} | {m('cvp'):.0f} | {m('isteps'):.1f} | {m('cands'):.1f} | {m('sq'):.2f} | {m('integral'):.2f} | {w:.0f} |")
        W.setdefault(pb,[]).append((r['B'],rc[0]['npairs'],w,m('cvp')))
open('bydisc_table.md','w').write("\n".join(tab)+"\n"); print("\n".join(tab))
fl=["| p bits | quantity | B range | doublings | fitted exponent | 95% CI (bootstrap over B-configs) |","|---|---|---|---|---|---|"]
fitres={}
for pb,v in sorted(W.items()):
    for name,idx in (("sweep work W (CVP+steps+cands)",2),("number of discriminants |S_F|",1)):
        for lo,hi in ((6,128),(6,32)):
            sel=[t for t in v if lo<=t[0]<=hi and t[1]>=3]
            if len(sel)<4: continue
            B=[t[0] for t in sel]; y=[t[idx] for t in sel]
            s,ci=boot_slope(B,y)
            fl.append(f"| {pb} | {name} | {min(B)}-{max(B)} | {math.log2(max(B)/min(B)):.1f} | {s:.2f} | [{ci[0]:.2f}, {ci[1]:.2f}] |")
            fitres[(pb,name,lo,hi)]=(s,ci[0],ci[1])
open('bydisc_fit.md','w').write("\n".join(fl)+"\n"); print("\n".join(fl))
# ---------- sieve model: best Q-sieve cost with exact |Im_q| and exact square-leading survival ----------
def sieve_stats(q):
    from collections import Counter
    img=set()
    for x1 in range(q):
        for x2 in range(q):
            img.add((((x1*x2)**2-28*(x1+x2))%q,(-2*(x1*x2*(x1+x2)+14))%q,((x1-x2)**2)%q))
    c2cnt=Counter(i[2] for i in img)
    # c2=s^2 with s uniform mod q -> P(c2 residue = r) = #{s: s^2=r}/q ; given c2, other coords uniform -> hit prob |Im_{c2}|/q^2
    P=0.0
    for s in range(q): P+=c2cnt.get((s*s)%q,0)/q**2/q
    return len(img),P
primes=[q for q in sp.primerange(3,200)]
ST={q:sieve_stats(q) for q in primes}
# check against measured survival
cs=json.load(open('count_scan.json'))
meas=[]
for l in open('census_p32.jsonl'):
    r=json.loads(l)
    if r['B']==45:
        n0=np.mean([t['surv'][0] for t in r['targets']]); sv=[np.mean([t['surv'][k] for t in r['targets']]) for k in range(1,6)]
        cum=1.0; pr=[]
        for q in (3,5,7,11,13): cum*=ST[q][1]; pr.append(cum)
        meas=[(q,sv[i]/n0,pr[i]) for i,q in enumerate((3,5,7,11,13))]
sv_lines=["| primes sieved up to | measured cumulative survival (p~2^32, B=45) | predicted prod P_q |","|---|---|---|"]+[f"| {q} | {m:.4g} | {pr:.4g} |" for q,m,pr in meas]
open('sieve_pred_vs_meas.md','w').write("\n".join(sv_lines)+"\n"); print("\n".join(sv_lines))
def best_sieve(Nsq):
    best=(Nsq,0,1)
    setups=1.0; surv=1.0
    for k,q in enumerate(primes,1):
        setups*=ST[q][0]; surv*=ST[q][1]
        c=setups+Nsq*surv
        if c<best[0]: best=(c,k,setups)
    return best
rows=[]
for pb in (32,28):
    for r in cs:
        pass
allrows=[]
for r in json.load(open('count_scan.json')):
    allrows.append((r['pbits'],r['B'],r['mean_Nsq']))
for r in json.load(open('count_scan_p24_partial.json')):
    allrows.append((r['pbits'],r['B'],r['mean_Nsq']))
st=["| p bits | B | exact N_sq | unsieved census cost (N_sq) | best prime-sieve cost (setups+survivors) | #primes at optimum | generic lookup B | pair enumeration B^2/2 |","|---|---|---|---|---|---|---|---|"]
sv={}
for pb,B,n in sorted(allrows):
    c,k,s=best_sieve(n); st.append(f"| {pb} | {B} | {n:.4g} | {n:.4g} | {c:.4g} | {k} | {B} | {B*B/2:.0f} |"); sv.setdefault(pb,[]).append((B,c,n))
open('sieve_model_table.md','w').write("\n".join(st)+"\n"); print("\n".join(st))
sl=["| p bits | B range | doublings | exponent of N_sq | exponent of best sieve cost | 95% CI (bootstrap) |","|---|---|---|---|---|---|"]
sfit={}
for pb,v in sorted(sv.items()):
    sel=[t for t in v if t[2]>1e4]
    if len(sel)<4: continue
    B=[t[0] for t in sel]
    s1=slope(B,[t[2] for t in sel]); s2,ci=boot_slope(B,[t[1] for t in sel])
    sl.append(f"| {pb} | {min(B)}-{max(B)} | {math.log2(max(B)/min(B)):.1f} | {s1:.2f} | {s2:.2f} | [{ci[0]:.2f}, {ci[1]:.2f}] |"); sfit[pb]=(s2,ci[0],ci[1])
open('sieve_fit.md','w').write("\n".join(sl)+"\n"); print("\n".join(sl))
# ratio exponent from exact N_sq with N_both=1 (observed up to B=45; planted lower bound beyond)
rl=["| p bits | B range | doublings | exponent c in 1/N_sq ~ B^-c | 95% CI |","|---|---|---|---|---|"]
ratfit={}
for pb in (24,28,32):
    sel=[(B,n) for p_,B,n in allrows if p_==pb and n>=100]
    if len(sel)<4: continue
    B=[b for b,n in sel]; y=[1/n for b,n in sel]
    s,ci=boot_slope(B,y); rl.append(f"| {pb} | {min(B)}-{max(B)} | {math.log2(max(B)/min(B)):.1f} | {-s:.3f} | [{-ci[1]:.3f}, {-ci[0]:.3f}] |"); ratfit[pb]=(-s,-ci[1],-ci[0])
open('ratio_fit_exactNsq.md','w').write("\n".join(rl)+"\n"); print("\n".join(rl))
# ---------- figure ----------
fig,ax=plt.subplots(1,3,figsize=(15,4.3))
cols={20:'C0',24:'C1',28:'C2',32:'C3'}
for f in sorted(glob.glob('census_p*.jsonl')):
    L=[json.loads(l) for l in open(f)]; pb=L[0]['pbits']
    Bs=[r['B'] for r in L]; rt=[np.mean([t['Nboth'] for t in r['targets']])/np.mean([t['Nsq'] for t in r['targets']]) for r in L]
    ax[0].loglog(Bs,rt,'o-',color=cols[pb],label=f'p~2^{pb} (measured)')
    Bg=np.array([6,8,11,16,23,32,45,64,91,128.]); ax[0].loglog(Bg,np.minimum(1,2**pb/(4*Bg**10)),':',color=cols[pb],lw=1)
ax[0].set_xlabel('B');ax[0].set_ylabel('structured / square-leading small forms');ax[0].set_title('(a) census ratio; dotted p/(4B^10)');ax[0].legend(fontsize=7)
for pb,v in sorted(W.items()):
    B=[t[0] for t in v]; ax[1].loglog(B,[t[2] for t in v],'o-',label=f'sweep work, p~2^{pb}')
Bg=np.array([6,128.]); ax[1].loglog(Bg,Bg**2/8*2,'k--',label='~B^2 slope'); ax[1].loglog(Bg,Bg*2,'k:',label='B slope (lookup)')
ax[1].set_xlabel('B');ax[1].set_ylabel('work');ax[1].set_title('(b) per-discriminant CVP sweep');ax[1].legend(fontsize=7)
for pb,v in sorted(sv.items()):
    B=[t[0] for t in v]; ax[2].loglog(B,[t[1] for t in v],'s-',label=f'best prime-sieve, p~2^{pb}'); ax[2].loglog(B,[t[2] for t in v],'.--',label=f'unsieved N_sq, p~2^{pb}',alpha=.5)
ax[2].loglog([16,128],[16,128],'k:',label='B');ax[2].set_xlabel('B');ax[2].set_title('(c) small-prime sieve of the census');ax[2].legend(fontsize=6)
plt.tight_layout();plt.savefig('fig_sa03.png',dpi=130)
json.dump(dict(bydisc={str(k):v for k,v in fitres.items()},sieve={str(k):v for k,v in sfit.items()},ratio_exact={str(k):v for k,v in ratfit.items()}),open('fits.json','w'),indent=1)

"""Predictor comparison on existing cells + figure + slope bootstrap."""
import json, random, glob, math
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from math import comb
OUT='/home/user/semaev-runs/SA-11/out/'
# measured reference values quoted in prereg / crypto repo
dig_m2 = {s: 4 + s//2 for s in range(2,9)}                # measured ffd=d_last on 106/106 draws (arms U s=2..7, P s=2..8)
cells = []   # (label, family, param, measured, n_draws)
for s in range(2,8): cells.append((f'digit m=2 U s={s}','digit',(2,s),4+s//2,{2:12,3:12,4:12,5:12,6:8,7:4}[s]))
for s in range(2,9): cells.append((f'digit m=2 P s={s}','digit',(2,s),4+s//2,{2:8,3:8,4:8,5:8,6:8,7:4,8:2}[s]))
cells.append(('digit m=3 U s=4','digit',(3,4),13,4)); cells.append(('digit m=3 U s=5','digit',(3,5),13,4))
tower_meas = {1:3,2:4,3:4,4:4,5:4,6:5,7:5,8:5,9:5,10:6}   # medians quoted in PREREGISTRATION (reported by session; raw rows not in repo)
for t,v in tower_meas.items(): cells.append((f'tower Kummer m=2 t={t}','tower',(2,t),v,None))

def pred_null_usupp(fam,par):      # support-matched null (measured by repo and re-measured here): digits s+3 ; m=3: D=12,n=3s
    if fam=='digit':
        m,s=par; e=2**(m-1); D=m*e; n=m*s
        # entropy/first-moment: least c with C(n,c-D)>C(n,c)
        c=D
        while comb(n,c-D)<=comb(n,c): c+=1
        return c
    m,t=par; n=m*t; D=2
    c=D
    while comb(n,c-D)<=comb(n,c): c+=1
    return c
def pred_cav(fam,par): return pred_null_usupp(fam,par)       # annealed/RS first-moment predictor == support-matched null
def pred_top(fam,par):
    if fam=='digit':
        m,s=par; e=2**(m-1); return s//2 + e//2 + 1 + (m-1)*e
    return 4                                   # top-form annihilator y10*y11 (theorem D3 in repo): ffd=4; no d_F content
def pred_const4(fam,par): return 4
def pred_tower_cstep(fam,par): return 4 + (par[1]-2)//4 if par[1]>=2 else 3
res={}
for name,fn in (('P_cav (annealed/RS entropy)',pred_cav),('P_top (graded annihilator of leading form)',pred_top),('constant 4 (trivial)',pred_const4)):
    ok=0; per=[]
    for lab,fam,par,meas,nd in cells:
        pr=fn(fam,par); per.append((lab,meas,pr,abs(pr-meas)))
        ok += abs(pr-meas)<=1
    res[name]=dict(within1=ok,total=len(cells),per=per)
    dig=[x for x,c in zip(per,cells) if c[1]=='digit']; tow=[x for x,c in zip(per,cells) if c[1]=='tower']
    res[name]['digit_within1']=(sum(x[3]<=1 for x in dig),len(dig)); res[name]['tower_within1']=(sum(x[3]<=1 for x in tow),len(tow))
    res[name]['digit_exact']=sum(x[3]==0 for x in dig)
for k,v in res.items(): print(k,v['within1'],'/',v['total'],'digit',v['digit_within1'],'exact',v['digit_exact'],'tower',v['tower_within1'])
json.dump({k:dict(v) for k,v in res.items()}, open(OUT+'predictor_comparison.json','w'), default=str)

# tower slope: measured medians t=2..10, bootstrap CI over cells (no raw rows: resample residual-free via jackknife/bootstrap on points)
ts=np.arange(2,11); ys=np.array([tower_meas[t] for t in ts])
sl=np.polyfit(ts,ys,1)[0]
rng=np.random.default_rng(0); bs=[]
for _ in range(5000):
    i=rng.integers(0,len(ts),len(ts))
    if len(set(ts[i]))<3: continue
    bs.append(np.polyfit(ts[i],ys[i],1)[0])
lo,hi=np.percentile(bs,[2.5,97.5])
print('tower slope d_F vs t (t=2..10): OLS %.3f  bootstrap95 [%.3f, %.3f]'%(sl,lo,hi))
# annealed slope: least c with C(2t,c-2)>C(2t,c) => c = t+2 -> slope 1
print('annealed predictor slope 1.0 ; C-step slope 0.25')
json.dump(dict(slope=sl,lo=lo,hi=hi),open(OUT+'tower_slope.json','w'))

# figure
fig,ax=plt.subplots(1,2,figsize=(10,4))
ss=np.arange(2,9)
ax[0].plot(ss,[4+s//2 for s in ss],'ko-',label='measured (106 draws)')
ax[0].plot(ss,[pred_cav('digit',(2,s)) for s in ss],'r^--',label='P_cav / Usupp null = s+3')
ax[0].plot(ss,[pred_top('digit',(2,s)) for s in ss],'bs:',label='P_top (graded annihilator)',markerfacecolor='none')
rows=json.load(open(OUT+'digit_gr_rows.json'))
for arm,mk,cl in (('real','x','g'),('usupp','+','m'),('ublock','1','c')):
    xs=[r['s'] for r in rows if r['arm']==arm and r['status']=='ok']; yy=[r['ffd'] for r in rows if r['arm']==arm and r['status']=='ok']
    ax[0].scatter(xs,yy,marker=mk,c=cl,s=50,label=f'own run: {arm}',zorder=5)
ax[0].set_xlabel('digits s (m=2)'); ax[0].set_ylabel('first fall degree'); ax[0].legend(fontsize=7); ax[0].set_title('Digits')
tt=np.arange(1,11)
ax[1].plot(tt,[tower_meas[t] for t in tt],'ko-',label='measured d_F (repo medians)')
ax[1].plot(tt,[t+2 for t in tt],'r^--',label='P_cav annealed: t+2 (slope 1)')
ax[1].plot(tt,[4]*10,'bs:',label='P_top: ffd = 4 (no d_F content)',markerfacecolor='none')
tr=[]
for f in glob.glob(OUT+'tower_rows_*.json'): tr+=json.load(open(f))
for kind,mk,cl in (('real','x','g'),('null','+','m')):
    xs=[r['t'] for r in tr if r['kind']==kind and r['dF']]; yy=[r['dF'] for r in tr if r['kind']==kind and r['dF']]
    ax[1].scatter(xs,yy,marker=mk,c=cl,s=60,label=f'own run d_F: {kind}',zorder=5)
ax[1].set_xlabel('tower height t (m=2)'); ax[1].set_ylabel('d_F'); ax[1].legend(fontsize=7); ax[1].set_title('Kummer towers')
plt.tight_layout(); plt.savefig(OUT+'fig_predictors.png',dpi=130)

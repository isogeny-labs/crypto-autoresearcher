import json, glob, os, collections, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O=os.path.dirname(os.path.abspath(__file__))+'/../out/ms/'
sets=[('m2_digit','m=2 norm (RR) digit'),('m2_digit_null','m=2 norm digit, curve-free null'),('m2_S','m=2 S_3 digit'),
      ('m2_V','m=2 norm (RR) + vanishing'),('m2_SV','m=2 S_3 + vanishing'),
      ('m3_digit','m=3 norm (RR) digit'),('m3_digit_null','m=3 norm digit, curve-free null'),('m3_S','m=3 S_4 digit'),
      ('m3_V','m=3 norm (RR) + vanishing'),('m3_SV','m=3 S_4 + vanishing')]
rows=[]; res={}
for f,name in sets:
    d=collections.defaultdict(list)
    for l in open(O+f+'.jsonl'):
        r=json.loads(l); d[r['B']].append(r)
    res[f]={}
    for B in sorted(d):
        rs=d[B]; ok=[r for r in rs if r['status']=='ok']
        degs=sorted(set(r['fdeg'] for r in ok))
        res[f][B]=dict(fdeg=[r['fdeg'] for r in ok],timeouts=len(rs)-len(ok),nvars=rs[0]['nvars'],p=rs[0]['p'],
                       maxmat=max((r['maxmat'] for r in ok),default=None,key=lambda x:x[0]*x[1] if x else 0),secs=max((r['secs'] for r in ok),default=None))
        rows.append(f"| {name} | {B} | {rs[0]['p']} | {rs[0]['nvars']} | {[r['fdeg'] for r in ok] or '-'} | {res[f][B]['maxmat']} | {res[f][B]['secs']} | {len(rs)-len(ok) or ''} |")
# slopes in s = log2 B (least squares on per-B values, all seeds agree)
sl={}
for f,_ in sets:
    pts=[(np.log2(B),v['fdeg'][0]) for B,v in res[f].items() if v['fdeg']]
    if len(pts)>=3:
        x,y=np.array(pts).T; A=np.vstack([x,np.ones_like(x)]).T; c=np.linalg.lstsq(A,y,rcond=None)[0]; sl[f]=dict(slope_per_bit=round(c[0],3),intercept=round(c[1],3),n=len(pts),Bmax=int(2**x.max()))
hdr="| system | B | p | nvars | msolve F4 max degree (per seed) | max matrix | secs | timeouts |\n|---|---|---|---|---|---|---|---|\n"
open(O+'msolve_table.md','w').write(hdr+"\n".join(rows)+"\n\nLeast-squares slope of degree vs log2 B:\n"+json.dumps(sl,indent=1))
json.dump(dict(cells=res,slopes=sl),open(O+'msolve_summary.json','w'),indent=1)
print(hdr+"\n".join(rows)); print(json.dumps(sl,indent=1))
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
sty={'digit':('o-','C0'),'digit_null':('x:','C0'),'S':('s--','C3'),'V':('o-','C2'),'SV':('s--','C1')}
for f,name in sets:
    m=f[1]; kind=f[3:]
    B=[b for b,v in res[f].items() if v['fdeg']]; y=[res[f][b]['fdeg'][0] for b in B]
    a=ax[0] if kind in ('digit','digit_null','S') else ax[1]
    st,c=sty[kind]; a.plot(B,y,st,color=c,alpha=1 if m=='2' else .55,lw=2 if m=='3' else 1.2,label=name)
ax[0].set_title('digit presentation (bits, x_i<2^s)'); ax[1].set_title('vanishing-polynomial base x_i in [1,B]')
for a in ax: a.set_xscale('log',base=2); a.set_xlabel('B'); a.set_ylabel('msolve F4 max degree'); a.grid(alpha=.3); a.legend(fontsize=7)
ax[1].set_yscale('log',base=2)
plt.tight_layout(); plt.savefig(O+'fig_msolve_degree.png',dpi=130)

import numpy as np, json
from scipy.optimize import curve_fit
S={
 '(i) S_4 in x, m=3 [SA-01]':{2:.01435546875,3:.021533203125,4:.02578125,5:.028564453125,6:.030615234375},
 '(ii) Vieta e1,e2,e3 graded, m=3':{2:.018506530761718747,3:.024913330078124997,4:.0275498046875},
 '(iii)-Groebner m=3 (best of MILP/LP gens; t=4 = Vieta bound)':{2:.01931982421875,3:.025356445312500003,4:.0275498046875},
 '(iv)-Groebner m=3 (max of chain+S4+u-gen MILP and (i))':{2:.016906640625000004,3:.02340703125,4:.02578125,5:.028564453125,6:.030615234375},
 '(i) m=4 (sym LP=exact)':{2:.0024552208426619894,3:.004804426666667059},
}
f3=lambda t,D,a,b:D-a/t-b/t**2
f2=lambda t,D,a:D-a/t
out={}
for k,d in S.items():
    ts=np.array(sorted(d),float); v=np.array([d[int(t)] for t in ts]); r={}
    for name,f,np_ in (('D-a/t',f2,2),('D-a/t-b/t^2',f3,3)):
        if len(ts)<np_+ (0 if np_==2 else 1) : continue
        try:
            p,_=curve_fit(f,ts,v,maxfev=20000); loo=[]
            for j in range(len(ts)):
                m=np.ones(len(ts),bool); m[j]=False
                if m.sum()<np_: continue
                q,_=curve_fit(f,ts[m],v[m],maxfev=20000); loo.append(q[0])
            r[name]=dict(D=round(p[0],4),loo=[round(min(loo),4),round(max(loo),4)] if loo else None)
        except Exception as e: r[name]=str(e)
    out[k]=r; print(k,d.keys(),r)
json.dump(out,open('fits.json','w'),indent=1)

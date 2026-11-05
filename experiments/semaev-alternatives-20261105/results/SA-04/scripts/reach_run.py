import json, itertools, sympy as sp, numpy as np, sys, time
from jm import *
sup=json.load(open('../out/vieta_support.json'))
res={}
def extrap(r):
    ks=sorted(r)[-3:]
    # fit delta(k)=A - B/k - C/k^2 on last three
    M=np.array([[1,-1/k,-1/k**2] for k in ks]); y=np.array([r[k][0] for k in ks])
    return float(np.linalg.solve(M,y)[0])
def run(name,supp,w,kmax):
    t=time.time(); r=reach(supp,w,kmax=kmax)
    ex=extrap(r)
    print(name,"w",w,{k:round(v[0],5) for k,v in r.items()},"extrap",round(ex,5),"dim@kmax",r[kmax][2],"t",round(time.time()-t,1),flush=True)
    res[name]=dict(w=w,deltas={k:v[0] for k,v in r.items()},extrap=ex,dims={k:v[2] for k,v in r.items()})
# controls: S_3 and S_4 in x-coordinates
run("S3_x(1,1)",[(i,j) for i in range(3) for j in range(3)],(1,1),10)
X=sp.symbols('x1:4'); T=sp.Symbol('T'); xR=sp.Integer(17); a,b=3,5
def S3(u,v,t): return sp.expand((u-v)**2*t**2-2*((u+v)*(u*v+a)+2*b)*t+((u*v-a)**2-4*b*(u+v)))
S4=sp.expand(sp.resultant(S3(X[0],X[1],T),S3(X[2],xR,T),T))
supp=sp.Poly(S4,*X).monoms()
print("S4 support size",len(supp),"max deg per var",[max(m[i] for m in supp) for i in range(3)],flush=True)
run("S4_x(1,1,1)",supp,(1,1,1),5)
for m in (2,3,4):
    s=[tuple(x) for x in sup[str(m)]['support']]
    run("Vieta_m%d"%m,s,tuple(range(1,m+1)),{2:12,3:7,4:4}[m])
json.dump(res,open('../out/reach_results.json','w'),indent=1)

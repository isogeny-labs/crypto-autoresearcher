import sys; sys.path.insert(0,'/home/user/semaev-runs/SA-25/src')
import sa25, ctypes, json, math, random, os, numpy as np
from sa25 import lib, BASE
from sympy.ntheory import sqrt_mod
res={}
for l in open(BASE+'/results/e2e.jsonl'):
    o=json.loads(l); p,n,N=o['p'],o['n'],o['N']; h=N//n; lib.ec_setp(p); rng=random.Random(2500+p)
    def rpt():
        while True:
            x=rng.randrange(p); d=(4*(x**3-x*x-10*x-20)+1)%p
            if d==0 or pow(d,(p-1)//2,p)!=1: continue
            s=sqrt_mod(d,p); return x,((s-1)*pow(2,-1,p))%p
    while True:
        x,y=rpt(); gx,gy,gi=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
        lib.ec_smul1(p,x,y,h,ctypes.byref(gx),ctypes.byref(gy),ctypes.byref(gi))
        if not gi.value: break
    secs=[];adds=[];ok=0
    dpb=max(1,int(math.log2(n)/2)-4)
    for ti in range(5):
        k=rng.randrange(1,n); qx,qy,qi=ctypes.c_int64(),ctypes.c_int64(),ctypes.c_int()
        lib.ec_smul1(p,gx.value,gy.value,k,ctypes.byref(qx),ctypes.byref(qy),ctypes.byref(qi))
        for r in range(200):
            ad=ctypes.c_int64(); sec=ctypes.c_double()
            kk=lib.ec_rho(p,n,gx.value,gy.value,qx.value,qy.value,7000*ti+r+1,dpb,200000+400*int(math.sqrt(n)),ctypes.byref(ad),ctypes.byref(sec))
            ok+=(kk==k); secs.append(sec.value); adds.append(ad.value)
    res[p]={'n':n,'secs':secs,'adds':adds,'correct':ok,'load':os.getloadavg()[0]}
    print(p,n,np.mean(secs),np.mean(adds),ok,flush=True)
json.dump(res,open(BASE+'/results/rho_times.json','w'))

# exact N_sq (count-only, mode 2) over a wider B range; validated against mode 0 in census runs
import random,subprocess,json,sys,time
from common import *
res=[]
for bits in (28,32):
    p=prime34(bits); rng=random.Random(5000+bits)
    for B in (16,23,32,45,64,91,128,181):
        if 4*B**10/p>3e12: continue
        pl=planted(p,B,12,rng)
        if pl is None: continue
        t=time.time()
        o=subprocess.run(['nice','-n','10','./census2',str(p),str(B),'2'],input="\n".join(str(x[0]) for x in pl)+"\n",capture_output=True,text=True,timeout=3000).stdout
        rows=[list(map(int,l.split())) for l in o.strip().split("\n")]
        nsq=[r[1] for r in rows]; it=[r[6] for r in rows]
        rec=dict(pbits=bits,B=B,n=len(rows),mean_Nsq=sum(nsq)/len(nsq),min_Nsq=min(nsq),max_Nsq=max(nsq),pred=4*B**10/p,mean_iter=sum(it)/len(it),Nsq_list=nsq,sec=time.time()-t)
        res.append(rec); print(bits,B,rec['mean_Nsq'],rec['pred'],rec['sec'],flush=True)
        json.dump(res,open('count_scan.json','w'))

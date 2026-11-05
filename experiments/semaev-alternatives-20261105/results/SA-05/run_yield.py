# main yield experiment: structured small-height base vs random control of equal size
import subprocess, json, sys, os, math, time
from fractions import Fraction
from common import *
os.makedirs('raw',exist_ok=True)
KS=[int(a) for a in sys.argv[1].split(',')]; NP=int(sys.argv[2]); HS=[int(a) for a in sys.argv[3].split(',')]; OUT=sys.argv[4]
def S3(x1,x2,x3):
    e1=x1+x2; e2=x1*x2
    return x3*x3*(e1*e1-4*e2)-2*x3*(e1*e2+14)+e2*e2-28*e1
def run(p,xs,tag,T=100000,seed=1):
    bf=f'/tmp/sa05_{os.getpid()}_base.txt'; tf=f'raw/{tag}_triples.txt'
    if isinstance(xs,str): src=xs
    else:
        open(bf,'w').write('\n'.join(map(str,xs))); src=bf
    r=subprocess.run(['./sumset',str(p),src,str(T),str(seed),tf],capture_output=True,text=True,timeout=900)
    return json.loads(r.stdout)
with open(OUT,'a') as fo:
  for k in KS:
    for p in primes_for(k,NP):
        for h in HS:
            pts=small_pts(p,h); B=len(pts)
            if B>6200 or B<10: continue
            lookup={x:(a,b) for a,b,x in pts}
            tag=f'k{k}_p{p}_h{h}'
            t=time.time()
            res=run(p,[x for a,b,x in pts],tag+'_rat')
            # exact classification of listed triples
            glob=wr=0
            for l in open(f'raw/{tag}_rat_triples.txt'):
                x1,x2,xd,kk=map(int,l.split())
                F=[Fraction(*lookup[x]) for x in (x1,x2)]
                # xD is x(P+Q) or x(P-Q): test S3(x1,x2,xd) over Q with xd rational from lookup
                if xd in lookup and S3(F[0],F[1],Fraction(*lookup[xd]))==0: glob+=1
                else: wr+=1
            res.update(variant='rational',k=k,h=h,listed_global=glob,listed_wrapped=wr)
            rc=run(p,f'rand:{B}:{p%1000+h}',tag+'_ctrl'); rc.update(variant='control',k=k,h=h)
            # integer base with similar B (b=1): a in [-H,H]
            H=B//2*2//2 if False else B
            ipts=small_pts(p,B,integer_only=True)
            ri=run(p,[x for a,b,x in ipts],tag+'_int'); ri.update(variant="integer",k=k,h=B)
            lookupi={x:a for a,b,x in ipts}
            for r_ in (res,rc,ri): r_['M']=p/2
            fo.write(json.dumps(res)+'\n'+json.dumps(rc)+'\n'+json.dumps(ri)+'\n'); fo.flush()
            print(tag,B,res['D'],res['triples'],rc['triples'],ri['B'],ri['triples'],round(time.time()-t,1),flush=True)

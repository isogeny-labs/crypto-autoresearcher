import subprocess, json, sys, os, time, math
from fractions import Fraction
from common import *
os.makedirs('raw',exist_ok=True)
def S3(x1,x2,x3):
    e1=x1+x2; e2=x1*x2
    return x3*x3*(e1*e1-4*e2)-2*x3*(e1*e2+14)+e2*e2-28*e1
def run(p,src,tag,T,seed):
    if not isinstance(src,str):
        bf=f'raw/{tag}_base.txt'; open(bf,'w').write('\n'.join(map(str,src))); src=bf
    t=time.time()
    r=subprocess.run(['nice','-n','10','./sumset2',str(p),src,str(T),str(seed),f'raw/{tag}_triples.txt',f'raw/{tag}_thits.txt'],capture_output=True,text=True,timeout=1500)
    d=json.loads(r.stdout); d['sec']=round(time.time()-t,1); return d
def int_pts(p,B):
    res=[];a=0
    while len(res)<B:
        for aa in ([0] if a==0 else [a,-a]):
            f=(aa**3+7)%p
            if f and pow(f,(p-1)//2,p)==1: res.append(aa%p)
        a+=1
    return res[:B]
def find_h(p,Btarget):
    h=20
    while True:
        h+=2
        if len(small_pts(p,h))>=Btarget: return h
def addp(P1,P2,p):
    (x1,y1),(x2,y2)=P1,P2
    l=(y2-y1)*pow(x2-x1,-1,p)%p; x3=(l*l-x1-x2)%p; return x3
def yof(x,p): return pow((x**3+7)%p,(p+1)//4,p)
def verify_thits(p,tag):
    ok=bad=0; tg=set()
    for l in open(f'raw/{tag}_thits.txt'):
        x1,x2,v,k=map(int,l.split())
        P1=(x1,yof(x1,p)); y2=yof(x2,p); P2=(x2,y2 if k==0 else (-y2)%p)
        if addp(P1,P2,p)==v: ok+=1; tg.add(v)
        else: bad+=1
    return ok,bad,len(tg)
KS=[int(a) for a in sys.argv[1].split(',')]; NP=int(sys.argv[2]); FAC=float(sys.argv[3]); T=int(sys.argv[4]); OUT=sys.argv[5]
with open(OUT,'a') as fo:
  for k in KS:
    for p in primes_for(k,NP):
        Bt=int(FAC*p**(1/3)); h=find_h(p,Bt)
        pts=small_pts(p,h); B=len(pts); lookup={x:(a,b) for a,b,x in pts}
        tag=f'k{k}_p{p}'
        out={'k':k,'p':p,'h':h,'B':B,'p13':p**(1/3)}
        # structured
        r=run(p,[x for a,b,x in pts],tag+'_rat',T,11); glob=wr=0; seen=set()
        for l in open(f'raw/{tag}_rat_triples.txt'):
            x1,x2,xd,kk=map(int,l.split())
            key=frozenset((x1,x2,xd))
            if key in seen: continue
            seen.add(key)
            if xd in lookup and S3(Fraction(*lookup[x1]),Fraction(*lookup[x2]),Fraction(*lookup[xd]))==0: glob+=1
            else: wr+=1
        r.update(listed_global=glob,listed_wrapped=wr, tverify=verify_thits(p,tag+'_rat')); out['rational']=r
        rc=run(p,f'rand:{B}:{p%1000+h}',tag+'_ctrl',T,11); rc['distinct']=len({frozenset(map(int,l.split()[:3])) for l in open(f'raw/{tag}_ctrl_triples.txt')}); rc['tverify']=verify_thits(p,tag+'_ctrl'); out['control']=rc
        ri=run(p,int_pts(p,B),tag+'_int',T,11); ri['distinct']=len({frozenset(map(int,l.split()[:3])) for l in open(f'raw/{tag}_int_triples.txt')}); ri['tverify']=verify_thits(p,tag+'_int'); out['integer']=ri
        out['gen_trip']=B*(B-1)*(B-2)/(p/2)/3  # distinct unordered relations   # N*(B-2)/M, N=B(B-1) sums, M=p/2 abscissae
        fo.write(json.dumps(out)+'\n'); fo.flush()
        print(tag,h,B,'glob',glob,'wr',wr,'ctrl',rc['distinct'],'int',ri['distinct'],'gen',round(out['gen_trip'],1),'thits',r['thits'],rc['thits'],ri['thits'],r['sec'],flush=True)

import random,subprocess,json,sys,time
from common import *
bits=int(sys.argv[1]); out=open(f'census_p{bits}.jsonl','a')
p=prime34(bits)
rng=random.Random(1000+bits)
Bs=[6,8,11,16,23,32,45,64,91]
def run(xs,B,mode):
    o=subprocess.run(['nice','-n','10','./census',str(p),str(B),str(mode)],input="\n".join(map(str,xs))+"\n",capture_output=True,text=True,timeout=3000).stdout
    return [list(map(int,l.split())) for l in o.strip().split("\n")]
for B in Bs:
    est=4*B**10/p; estpos=8*B**12/p
    if est>3.5e8: print('skip',bits,B,est); continue
    nt=200 if est<=1e7 else (30 if est<=4e7 else 6)
    nc=30 if est<=1e7 else 0
    mode=1 if estpos<=3e6 else 0
    t=time.time()
    pl=planted(p,B,nt,rng)
    if pl is None: print('skip (fewer than 2 QR x)',bits,B); continue
    # sanity: planted vector in L_R and in box
    M=B**4; inbox=0
    for xR,x1,x2 in pl:
        c0,c1,c2=S3vec(x1,x2); assert (c0+c1*xR+c2*xR*xR)%p==0
        inbox+= max(abs(c0),abs(c1))<=M
    rows=run([x[0] for x in pl],B,mode)
    ctrl=[]
    if nc:
        xs=[]
        while len(xs)<nc:
            x=rng.randrange(1,p)
            if is_qr(x**3+7,p): xs.append(x)
        ctrl=run(xs,B,mode)
    rec=dict(pbits=bits,p=p,B=B,M=M,mode=mode,ntargets=nt,planted_in_box=inbox,est_Nsq=est,
             targets=[dict(xR=r[0],x1=pl[i][1],x2=pl[i][2],Nsq=r[1],Npos=r[2],NDall=r[3],Nboth=r[4],Ndec=r[5],Niter=r[6],surv=r[7:]) for i,r in enumerate(rows)],
             controls=[dict(xR=r[0],Nsq=r[1],Npos=r[2],NDall=r[3],Nboth=r[4],Ndec=r[5],Niter=r[6],surv=r[7:]) for r in ctrl],
             seconds=time.time()-t)
    out.write(json.dumps(rec)+"\n"); out.flush()
    print(bits,B,nt,mode,round(time.time()-t,1),flush=True)

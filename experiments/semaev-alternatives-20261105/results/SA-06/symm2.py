# Generalised: symmetrised polynomial with nfree free u-variables of S_n (n=nfree [all small] or nfree+1 [target fixed]).
import sys, json, random, itertools, numpy as np, time
import cypari2
pari=cypari2.Pari(); pari.allocatemem(400*10**6)
Q=int(pari("nextprime(2^61)"))
def set_modulus(q):
    global Q
    Q=int(q)
pari("S3(x,y,z)=(x-y)^2*z^2-2*((x+y)*(x*y+a)+2*b)*z+(x*y-a)^2-4*b*(x+y);")
pari("S4f(u,v,w,z)=polresultant(S3(u,v,'Y),S3(w,z,'Y),'Y);")
pari("Sn(xs)=my(n=#xs); if(n==3,S3(xs[1],xs[2],xs[3]), if(n==4,S4f(xs[1],xs[2],xs[3],xs[4]), polresultant(S3(xs[1],xs[2],'Z), S4f('Z,xs[3],xs[4],xs[5]),'Z)));")
def sym_poly(a,b,tau,nfree,fixed_target,seed=1):
    random.seed(seed)
    n=nfree+(1 if fixed_target else 0)
    c=(3*tau*tau+a)%Q
    pari(f"a=Mod({a},{Q});b=Mod({b},{Q});")
    d=2**(n-2)
    xR=random.randrange(1,Q)
    W=[[random.randrange(2,Q) for _ in range(d+1)] for _ in range(nfree)]
    U=[[ (w+c*pow(w,-1,Q))%Q for w in Wi] for Wi in W]
    def ev(ws):
        xs=[(tau+w)%Q for w in ws]
        x1p=(tau+c*pow(ws[0],-1,Q))%Q
        tail=[xR] if fixed_target else []
        s1=pari("Sn(%s)"%("["+",".join(f"Mod({x},{Q})" for x in xs+tail)+"]"))
        s2=pari("Sn(%s)"%("["+",".join(f"Mod({x},{Q})" for x in [x1p]+xs[1:]+tail)+"]"))
        nrm=1
        for w in ws[1:]: nrm=nrm*pow(w,d,Q)%Q
        if fixed_target: pass
        return int((s1*s2).lift())*pow(nrm,-1,Q)%Q
    F=np.empty((d+1,)*nfree,dtype=object)
    for idx in itertools.product(range(d+1),repeat=nfree):
        F[idx]=ev([W[i][idx[i]] for i in range(nfree)])
    for ax in range(nfree):
        V=pari("matrix(%d,%d,i,j,Mod(%s[i]^(j-1),%d))"%(d+1,d+1,str(U[ax]).replace(" ",""),Q))
        Vi=V**-1
        Vi=np.array([[int(Vi[i,j].lift()) for j in range(d+1)] for i in range(d+1)],dtype=object)
        F=np.moveaxis(np.tensordot(Vi,F,axes=([1],[ax])) % Q,0,ax)
    ws=[random.randrange(2,Q) for _ in range(nfree)]
    uu=[(w+c*pow(w,-1,Q))%Q for w in ws]
    val=0
    for idx in itertools.product(range(d+1),repeat=nfree):
        t=int(F[idx])
        for i in range(nfree): t=t*pow(uu[i],idx[i],Q)%Q
        val=(val+t)%Q
    ok=(val==ev(ws))
    supp=[list(map(int,idx)) for idx in itertools.product(range(d+1),repeat=nfree) if int(F[idx])%Q!=0]
    return supp,ok
if __name__=="__main__":
    cells={"gen2t":(2,-3,1),"j0_2t":(0,-8,2),"j1728_2t":(7,0,0)}
    out={}
    for name,(a,b,tau) in cells.items():
        for n in (3,4,5):
            for fixed in (True,False):
                nfree=n-1 if fixed else n
                if (n==5 and not fixed) and len(sys.argv)>1 and sys.argv[1]=="skip5": continue
                t0=time.time()
                supp,ok=sym_poly(a,b,tau,nfree,fixed)
                key=f"{name}|S{n}|{'target' if fixed else 'allsmall'}"
                out[key]=dict(a=a,b=b,tau=tau,nfree=nfree,support=supp,interp_check=ok)
                print(key,len(supp),"of",(2**(n-2)+1)**nfree,"check",ok,round(time.time()-t0,1),flush=True)
    json.dump(out,open("supports_sym.json","w"))

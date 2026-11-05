# Compute S_3,S_4,S_5 by resultants (PARI) and dump exponent supports.
import sys, json, time
import cypari2
pari = cypari2.Pari(); pari.allocatemem(700*10**6)
pari("Y;X;x1;x2;x3;x4;x5;")
pari("S3(x,y,z)=(x-y)^2*z^2-2*((x+y)*(x*y+a)+2*b)*z+(x*y-a)^2-4*b*(x+y);")
pari("S4f(u,v,w,z)=polresultant(S3(u,v,'Y),S3(w,z,'Y),'Y);")
pari("VARS=[x1,x2,x3,x4,x5];")
pari("""mons(P,i,n)=if(i>n,return(List([[[],P]])));
 my(L=List(),v=VARS[i]); for(k=0,poldegree(P,v), my(c=polcoef(P,k,v)); if(c!=0, my(M=mons(c,i+1,n)); for(j=1,#M, listput(L,[concat([k],M[j][1]),M[j][2]]))));L;""")
def build(a,b,mmax=4):
    pari(f"a={a};b={b};")
    out={2:pari("S3(x1,x2,x3)")}
    if mmax>=3: out[3]=pari("S4f(x1,x2,x3,x4)")
    if mmax>=4: out[4]=pari("polresultant(S3(x1,x2,'X),S4f('X,x3,x4,x5),'X)")
    return out
def supp(P,nv):
    vs=[f"x{i}" for i in range(1,nv+1)]
    pari.set_global = None
    pari("TMP="+str(P)) if False else None
    return None
def get_support(expr,nv):
    
    L=pari("mons(%s,1,%d)"%(expr,nv))
    res=[]
    for i in range(len(L)):
        e=[int(z) for z in L[i][0]]; c=int(L[i][1]); res.append((e,c))
    return res
if __name__=="__main__":
    a,b=int(sys.argv[1]),int(sys.argv[2]); mmax=int(sys.argv[3])
    t=time.time(); o=build(a,b,mmax)
    for m,P in o.items():
        pari(f"TMP{m}={P};")
        pari(f"TMP=TMP{m};")
        s=get_support("TMP",m+1); print(m,len(s),time.time()-t,flush=True)

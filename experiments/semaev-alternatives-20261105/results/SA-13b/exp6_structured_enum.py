# Structured enumeration of short vectors of L_R = {(c0,c1,c2): c0+c1 T+c2 T^2 = 0 mod p} with SQUARE leading coefficient c2=d^2
# (Fincke-Pohst with c2 as the outermost coordinate, restricted to squares; inner level = exact 2-dim enumeration in the kernel lattice L2).
# Box W=(W0,W1,W2) = max |G_k| over 1<=x1<=x2<=B for y^2=x^3+7.  nodes = (#d tried) + (#inner lattice points visited).
# Planted instance: x1,x2<=B random x-coords of F_p points, R=P1+P2, T=x(R).  Verifies that the planted G(x) is found.
import random, math, json, sys, time
from sympy import nextprime
from lib import G_arrays
a,b=0,7
def mkprime(bits):
    p=nextprime(2**bits)
    while p%4!=3: p=nextprime(p)
    return p
def add(P,Q,p):
    (x1,y1),(x2,y2)=P,Q
    if x1==x2:
        l=(3*x1*x1+a)*pow(2*y1,-1,p)%p
    else: l=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
def pt(x,p):
    r=(x**3+a*x+b)%p
    y=pow(r,(p+1)//4,p)
    return (x,y) if y*y%p==r else None
def reduce2(T,p,W0,W1):
    """Gauss-reduce L2={(c0,c1): c0+c1 T=0 mod p} w.r.t. the weighted norm (c0/W0)^2+(c1/W1)^2, in exact integer arithmetic (scale by W0*W1)."""
    b1=(p,0); b2=(-T%p,1)
    def nrm(v): return (v[0]*W1)**2+(v[1]*W0)**2
    def dot(u,v): return u[0]*v[0]*W1*W1+u[1]*v[1]*W0*W0
    while True:
        if nrm(b1)>nrm(b2): b1,b2=b2,b1
        mu=dot(b1,b2); nn=dot(b1,b1)
        k=(2*mu+nn)//(2*nn)          # round(mu/nn)
        if k==0: break
        b2=(b2[0]-k*b1[0],b2[1]-k*b1[1])
    return b1,b2
def inner_points(b1,b2,z0,W0,W1):
    """all (c0,c1) = z0 + u1 b1 + u2 b2 with |c0|<=W0,|c1|<=W1 (exact)."""
    det=b1[0]*b2[1]-b1[1]*b2[0]
    # u = M^{-1} (c - z0), M=[[b1x,b2x],[b1y,b2y]];  u1=( b2y*(cx-z0x) - b2x*(cy-z0y))/det,  u2=(-b1y*(cx-z0x)+b1x*(cy-z0y))/det
    lo1=hi1=lo2=hi2=None
    us1=[];us2=[]
    for cx in (-W0,W0):
        for cy in (-W1,W1):
            dx=cx-z0[0]; dy=cy-z0[1]
            us1.append((b2[1]*dx-b2[0]*dy, det)); us2.append((-b1[1]*dx+b1[0]*dy, det))
    def rng(us):
        vals=[(n if d>0 else -n, abs(d)) for n,d in us]
        lo=min((n//d) for n,d in vals)      # floor
        hi=max(-((-n)//d) for n,d in vals)  # ceil
        return lo,hi
    l1,h1=rng(us1); l2,h2=rng(us2)
    out=[]
    for u1 in range(l1,h1+1):
        for u2 in range(l2,h2+1):
            c0=z0[0]+u1*b1[0]+u2*b2[0]; c1=z0[1]+u1*b1[1]+u2*b2[1]
            if -W0<=c0<=W0 and -W1<=c1<=W1: out.append((c0,c1))
    return out
def trial(p,B,rng):
    while True:
        x1=rng.randint(1,B); x2=rng.randint(1,B)
        P1=pt(x1,p); P2=pt(x2,p)
        if P1 and P2 and not(x1==x2 and False): break
    R=add(P1,P2,p) if x1!=x2 else add(P1,P1,p)
    T=R[0]
    # planted vector
    G0,G1,G2=G_arrays(x1,x2,a,b)
    assert (G0+G1*T+G2*T*T)%p==0
    W0=B**4+8*abs(b)*B+a*a; W1=2*(2*B*B*B+2*abs(b)+2*abs(a)*B*B)+1; W2=B*B
    b1,b2=reduce2(T,p,W0,W1)
    nodes=0; found=None; first_hit=None; pts_total=0
    for d in range(0,B+1):
        c2=d*d; nodes+=1
        t=(-c2*T*T)%p
        # two representatives of t: t and t-p (c0 may be negative); the lattice coset covers both since shifts by b1=(p,0) are lattice vectors
        pts=inner_points(b1,b2,(t,0),W0,W1)
        nodes+=len(pts); pts_total+=len(pts)
        if (G0,G1) in pts and c2==G2 and found is None:
            found=d; first_hit=nodes
    return dict(found=found is not None, d_star=abs(x1-x2), nodes=nodes, first_hit=first_hit, pts=pts_total, W=(W0,W1,W2))
if __name__=="__main__":
    bits=int(sys.argv[1]); ks=[int(s) for s in sys.argv[2].split(',')]; ntr=int(sys.argv[3])
    p=mkprime(bits); rng=random.Random(bits); rows=[]
    for k in ks:
        B=2**k; t0=time.time(); res=[trial(p,B,rng) for _ in range(ntr)]
        ok=sum(r['found'] for r in res)
        row=dict(bits=bits,p=p,B=B,k=k,trials=ntr,found=ok,mean_nodes=sum(r['nodes'] for r in res)/ntr,mean_first_hit=sum(r['first_hit'] for r in res if r['found'])/max(1,ok),
                 mean_inner_pts=sum(r['pts'] for r in res)/ntr/(B+1),nodes_list=[r['nodes'] for r in res],
                 list_pred=(8*res[0]['W'][0]*res[0]['W'][1]*res[0]['W'][2]/p), secs=time.time()-t0)
        rows.append(row); print("bits=%d B=2^%d found %d/%d mean nodes %.1f  inner pts/d %.3f  (V/p=%.3g) %.1fs"%(bits,k,ok,ntr,row['mean_nodes'],row['mean_inner_pts'],row['list_pred'],row['secs']),flush=True)
    json.dump(rows,open('exp6_rows_%d.json'%bits,'w'))

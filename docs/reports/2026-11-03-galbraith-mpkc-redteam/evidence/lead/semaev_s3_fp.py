"""Independent check (lead): Semaev S3 over F_p. Count F_p-roots (x1,x2,x3) vs
x-triples of points P1,P2,P3 in E(F_p) with P1+P2+P3=O for some signs."""
import sys, json
def run(p,a,b):
    sq={}
    for y in range(p): sq.setdefault(y*y%p,[]).append(y)
    pts=[(x,y) for x in range(p) for y in sq.get((x**3+a*x+b)%p,[])]
    def add(P,Q):
        if P is None: return Q
        if Q is None: return P
        (x1,y1),(x2,y2)=P,Q
        if x1==x2 and (y1+y2)%p==0: return None
        l=((3*x1*x1+a)*pow(2*y1,-1,p) if P==Q else (y2-y1)*pow(x2-x1,-1,p))%p
        x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)
    good=set()
    for P in pts:
        for Q in pts:
            R=add(P,Q)
            if R is not None: good.add((P[0],Q[0],R[0]))
    def S3(x1,x2,x3):
        return ((x1-x2)**2*x3**2-2*((x1+x2)*(x1*x2+a)+2*b)*x3+(x1*x2-a)**2-4*b*(x1+x2))%p
    roots=[(x1,x2,x3) for x1 in range(p) for x2 in range(p) for x3 in range(p) if S3(x1,x2,x3)==0]
    bad=[r for r in roots if r not in good]
    missing=[g for g in good if S3(*g)!=0]
    return dict(p=p,a=a,b=b,Fp_roots=len(roots),roots_without_Fp_points=len(bad),example=bad[:2],point_triples_not_roots=len(missing))
print(json.dumps([run(31,2,3),run(37,1,5)],indent=1))

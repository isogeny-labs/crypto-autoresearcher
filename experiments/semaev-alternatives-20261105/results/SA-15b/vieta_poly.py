"""Build, for one SA-15 instance, the Vieta-coordinate relation F(e1..e4)=0 mod p (S_5 in elementary symmetric functions,
total degree <= 8 in e) as the kernel of evaluations at random on-curve decompositions of R (any 3 free points, 4th determined)."""
import itertools, random, time, cypari2
pari=cypari2.Pari(); pari.allocatemem(800*10**6,silent=True)
def monos(n=4,d=8):
    out=[]
    for e in itertools.product(range(d+1),repeat=n):
        if sum(e)<=d: out.append(e)
    return out
MONOS=monos()
def relation(p,R,seed=1):
    E=pari.ellinit([0,7],p); rng=random.Random(seed)
    Rp=pari([int(R[0]),int(R[1])])
    rows=[]
    while len(rows)<len(MONOS)+25:
        Ps=[E.random() for _ in range(3)]
        S=Ps[0]; 
        for q in Ps[1:]: S=pari.elladd(E,S,q)
        P4=pari.elladd(E,Rp,pari.ellneg(E,S))
        if len(P4)<2 or len(Ps[0])<2: continue
        if any(len(q)<2 for q in Ps): continue
        xs=[int(q[0]) for q in Ps]+[int(P4[0])]
        e1=sum(xs)%p; e2=sum(xs[i]*xs[j] for i,j in itertools.combinations(range(4),2))%p
        e3=sum(xs[i]*xs[j]*xs[k] for i,j,k in itertools.combinations(range(4),3))%p; e4=xs[0]*xs[1]*xs[2]*xs[3]%p
        e=[e1,e2,e3,e4]; pw=[[pow(ei,k,p) for k in range(9)] for ei in e]
        rows.append([pw[0][m[0]]*pw[1][m[1]]%p*pw[2][m[2]]%p*pw[3][m[3]]%p for m in MONOS])
    M=pari.matrix(len(rows),len(MONOS),[v for r in rows for v in r])
    K=pari.matker(M*pari.Mod(1,p))
    return K
if __name__=="__main__":
    import json
    D=json.load(open("/home/user/semaev-runs/SA-15/instances.json")); g=D['groups'][0]; p=int(g['p']); i=g['instances'][0]
    t=time.time(); K=relation(p,(i['R']['x'],i['R']['y'])); print(len(K), time.time()-t)

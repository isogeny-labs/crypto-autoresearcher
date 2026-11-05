import json,sys,random
from fp import *
data=sys.argv[1]; nprimes=int(sys.argv[2]); out=sys.argv[3]
d=json.load(open(data)); lv=sorted(int(k) for k in d['levels'])
import math as _m; ps=find_primes(_m.lcm(*lv),2**19,2**21,nprimes); print('primes',ps,flush=True)
H={m:d['levels'][str(m)]['h'] for m in lv}
edges=[(e['n'],e['m']) for e in d['edges']]
res={'levels':lv,'h':H,'primes':ps,'per_prime':[]}
def embed(F):
    top=max(lv)
    emb={}
    if top==35:
        rts,_=F.roots(35); assert len(rts)==144,len(rts)
        rho=rts[0]; emb[35]=rho
        emb[5]=F.Hval(5,35,rho); emb[7]=F.Hval(7,35,rho)
        emb[1]=F.Hval(1,5,emb[5]); assert emb[1]==F.Hval(1,7,emb[7])
    else:
        r1=F.roots(1)[0][0]; emb[1]=r1
        for m in lv:
            if m!=1: emb[m]=[r for r in F.roots(m)[0] if F.Hval(1,m,r)==r1][0]
    return emb
for p in ps:
    F=Fp(p,d); emb=embed(F)
    pts={m:F.points(m,emb[m]) for m in lv}
    onc=all((y*y-x**3-1)%p==0 for m in lv for x,y in pts[m])
    allp=[(m,i) for m in lv for i in range(H[m])]
    distinct=len(set(pts[m][i] for m,i in allp)); distinct_pm=len(set(min(q,(q[0],(-q[1])%p)) for q in (pts[m][i] for m,i in allp)))
    nE=int(pari(f'ellcard(ellinit([0,0,0,0,1],{p}))'))
    rel_ok={}; rel_tot={}
    for e in d['edges']:
        n,m,a=e['n'],e['m'],e['a']; ok=0
        for i,row in enumerate(e['nb']):
            S=None
            for g in row: S=add(S,pts[m][g-1],p)
            ok+=(S==mul(a,pts[n][i],p))
        rel_ok[f'{n}>{m}']=ok; rel_tot[f'{n}>{m}']=len(e['nb'])
    # controls
    random.seed(p)
    ctrl_wrong={}  # incompatible embedding for level 5 (or lowest nontrivial)
    m0=7; e0=F.edge(1,m0)
    rts=F.roots(m0)[0]; bad=[r for r in rts if F.Hval(1,m0,r)!=emb[1]]
    okc=0;totc=0
    for r in bad[:4]:
        Pm=F.points(m0,r)
        for i,row in enumerate(e0['nb']):
            S=None
            for g in row: S=add(S,Pm[g-1],p)
            okc+=(S==mul(e0['a'],pts[1][i],p)); totc+=1
    ctrl_wrong={'level':m0,'tested':totc,'passed':okc}
    # random-subset control: random (l+1)-subsets with random signs among level m0
    l=e0['l']; okr=0; trials=20000
    for _ in range(trials):
        idx=random.sample(range(H[m0]),l+1); S=None
        for g in idx:
            q=pts[m0][g]; q=q if random.random()<.5 else neg(q,p); S=add(S,q,p)
        okr+=(S==mul(e0['a'],pts[1][random.randrange(H[1])],p))
    ctrl_rand={'trials':trials,'passed':okr,'expected_if_random':trials/nE}
    # rank table by conductor bound
    rt=[]
    for bound in lv:
        sub=[m for m in lv if m<=bound]
        if bound==35 or bound==max(lv): pass
        cols={(m,i):k for k,(m,i) in enumerate([(m,i) for m in sub for i in range(H[m])])}
        rows=[]
        for e in d['edges']:
            n,m,a=e['n'],e['m'],e['a']
            if n in sub and m in sub:
                for i,row in enumerate(e['nb']):
                    r=[0]*len(cols)
                    for g in row: r[cols[(m,g-1)]]+=1
                    r[cols[(n,i)]]-=a
                    rows.append(r)
        # edges with 35 need both 5 and 7: only included once 35 in sub
        rk=rank_modq(rows,len(cols)) if rows else 0
        rt.append({'bound':bound,'levels':sub,'points':len(cols),'relations':len(rows),'rank':rk,'ratio':rk/len(cols)})
    res['per_prime'].append({'p':p,'#E':nE,'on_curve':onc,'points_total':len(allp),'distinct_points':distinct,'distinct_up_to_sign':distinct_pm,
       'relations_ok':rel_ok,'relations_total':rel_tot,'control_wrong_embedding':ctrl_wrong,'control_random_subsets':ctrl_rand,'rank_table':rt})
    print(json.dumps(res['per_prime'][-1]),flush=True)
json.dump(res,open(out,'w'),indent=1)

import json,sys,random,math
from fpg import *
data,nprimes,out,ptsout=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
d=json.load(open(data)); lv=sorted(int(k) for k in d['levels']); Dk=d['D']; top=max(lv,key=lambda m:d['levels'][str(m)]['h'])
ps=find_primes(Dk,math.lcm(*lv),2**18,2**22,nprimes,bad=[d['N']]); print('primes',ps,flush=True)
H={m:d['levels'][str(m)]['h'] for m in lv}
res={'levels':lv,'h':H,'primes':ps,'per_prime':[]}
alle=sorted(d['edges'],key=lambda e:-e['m'])
def embed(F):
    rts,_=F.roots(top); assert len(rts)==H[top],(len(rts),H[top])
    emb={top:rts[0]}
    for e in alle:
        n,m=e['n'],e['m']
        if m not in emb: continue
        v=F.Hval(n,m,emb[m])
        if n in emb: assert emb[n]==v,('inconsistent embedding',n,m)
        else: emb[n]=v
    for m in sorted(lv,reverse=True):
        if m in emb: continue
        par=[e for e in alle if e['m']==m]
        good=[r for r in F.roots(m)[0] if all(F.Hval(e['n'],m,r)==emb[e['n']] for e in par)]
        assert good,('no compatible root',m); emb[m]=good[0]
    return emb
allpts={}
for p in ps:
    F=Fp(p,d); emb=embed(F)
    pts={m:[to_short(q,p) for q in F.points(m,emb[m])] for m in lv}
    onc=all((v*v-u**3-CA*u-16)%p==0 for m in lv for u,v in pts[m])
    allp=[(m,i) for m in lv for i in range(H[m])]
    distinct=len(set(pts[m][i] for m,i in allp))
    nE=int(pari(f'ellcard(ellinit([0,0,1,-1,0],{p}))'))
    rel_ok={}; rel_tot={}
    for e in d['edges']:
        n,m,a=e['n'],e['m'],e['a']; ok=0
        for i,row in enumerate(e['nb']):
            S=None
            for g in row: S=add(S,pts[m][g-1],p)
            ok+=(S==mul(a,pts[n][i],p))
        rel_ok[f'{n}>{m}']=ok; rel_tot[f'{n}>{m}']=len(e['nb'])
    random.seed(p)
    # wrong-embedding control on the top level, edge n>top with a!=0 and h(n)>1
    ctrl=[]
    for e in d['edges']:
        n,m,a=e['n'],e['m'],e['a']
        if m!=top or a==0 or H[n]==1: continue
        rts=F.roots(m)[0]; bad=[r for r in rts if F.Hval(n,m,r)!=emb[n]]
        okc=totc=0
        for r in bad[:6]:
            Pm=[to_short(q,p) for q in F.points(m,r)]
            for i,row in enumerate(e['nb']):
                S=None
                for g in row: S=add(S,Pm[g-1],p)
                okc+=(S==mul(a,pts[n][i],p)); totc+=1
        ctrl.append({'edge':f'{n}>{m}','tested':totc,'passed':okc})
    # random signed (l+1)-subset control on top-level edge with a!=0
    ctrl_rand=[]
    for e in d['edges']:
        n,m,a,l=e['n'],e['m'],e['a'],e['l']
        if m!=top or a==0: continue
        okr=0; trials=20000
        for _ in range(trials):
            idx=random.sample(range(H[m]),l+1); S=None
            for g in idx:
                q=pts[m][g]; q=q if random.random()<.5 else neg(q,p); S=add(S,q,p)
            okr+=(S==mul(a,pts[n][random.randrange(H[n])],p))
        ctrl_rand.append({'edge':f'{n}>{m}','trials':trials,'passed':okr,'expected_if_random':trials/nE})
    rt=[]
    for bound in lv:
        sub=[m for m in lv if m<=bound]
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
        rk=rank_modq(rows,len(cols)) if rows else 0
        rt.append({'bound':bound,'levels':sub,'points':len(cols),'relations':len(rows),'rank':rk,'ratio':rk/len(cols)})
    allpts[p]={str(m):pts[m] for m in lv}
    res['per_prime'].append({'p':p,'#E':nE,'on_curve':onc,'points_total':len(allp),'distinct_points':distinct,
       'relations_ok':rel_ok,'relations_total':rel_tot,'control_wrong_embedding':ctrl,'control_random_subsets':ctrl_rand,'rank_table':rt})
    print(json.dumps(res['per_prime'][-1]),flush=True)
json.dump(res,open(out,'w'),indent=1); json.dump(allpts,open(ptsout,'w'))

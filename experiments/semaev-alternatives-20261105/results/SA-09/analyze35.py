# Resumed executor: exact F_p verification including conductor 35 (all four edges 1>5, 1>7, 5>35, 7>35).
# Merges data_157.json (levels 1,5,7; edges 1>5,1>7; 400 digits) with data_35.json (level 35; edges 5>35,7>35; 1600 digits).
import json,sys,random,math
from fp import *
a=json.load(open('data_157.json')); b=json.load(open('data_35.json'))
d={'levels':dict(a['levels']),'edges':list(a['edges'])}
d['levels']['35']=b['levels']['35']; d['edges']+=b['edges']
json.dump(d,open('data_merged.json','w'))
nprimes=int(sys.argv[1]) if len(sys.argv)>1 else 3
lv=[1,5,7,35]; H={m:d['levels'][str(m)]['h'] for m in lv}
ps=find_primes(35,2**19,2**21,nprimes); print('primes',ps,flush=True)
res={'levels':lv,'h':H,'primes':ps,'per_prime':[]}
for p in ps:
    F=Fp(p,d)
    rts,_=F.roots(35); assert len(rts)==144,len(rts)
    emb={35:rts[0]}; emb[5]=F.Hval(5,35,rts[0]); emb[7]=F.Hval(7,35,rts[0])
    e1a=F.Hval(1,5,emb[5]); e1b=F.Hval(1,7,emb[7]); compat=(e1a==e1b); emb[1]=e1a
    # embedding sanity: H images are roots of the lower-level class polynomials
    roots_ok={m:(emb[m] in F.roots(m)[0]) for m in (1,5,7)}
    pts={m:F.points(m,emb[m]) for m in lv}
    onc=all((y*y-x**3-1)%p==0 for m in lv for x,y in pts[m])
    allp=[pts[m][i] for m in lv for i in range(H[m])]
    nE=int(pari(f'ellcard(ellinit([0,0,0,0,1],{p}))'))
    rel_ok={}; rel_tot={}
    for e in d['edges']:
        n,m,aa=e['n'],e['m'],e['a']; ok=0
        for i,row in enumerate(e['nb']):
            S=None
            for g in row: S=add(S,pts[m][g-1],p)
            ok+=(S==mul(aa,pts[n][i],p))
        rel_ok[f'{n}>{m}']=ok; rel_tot[f'{n}>{m}']=len(e['nb'])
    # wrong-embedding control at level 35 on edge 5>35 (l=7, a_7=-4); edge 7>35 has l=5, a_5=0 and is embedding-insensitive
    random.seed(p); e0=F.edge(5,35); assert e0['a']==-4
    bad=[r for r in rts if F.Hval(5,35,r)!=emb[5]]
    okc=totc=0
    for r in random.sample(bad,6):
        Pm=F.points(35,r)
        for i,row in enumerate(e0['nb']):
            S=None
            for g in row: S=add(S,Pm[g-1],p)
            okc+=(S==mul(e0['a'],pts[5][i],p)); totc+=1
    # random-subset control: random signed 8-subsets of level-35 points against a_7 * random level-5 point
    okr=0; trials=20000
    for _ in range(trials):
        S=None
        for g in random.sample(range(144),8):
            q=pts[35][g]; q=q if random.random()<.5 else neg(q,p); S=add(S,q,p)
        okr+=(S==mul(-4,pts[5][random.randrange(18)],p))
    r={'p':p,'#E':nE,'embedding_compatible_1':compat,'H_images_are_roots':roots_ok,'on_curve':onc,'points_total':len(allp),
       'distinct_points':len(set(allp)),'relations_ok':rel_ok,'relations_total':rel_tot,
       'control_wrong_embedding_35':{'tested':totc,'passed':okc},
       'control_random_subsets_35':{'trials':trials,'passed':okr,'expected_if_random':trials/nE}}
    res['per_prime'].append(r); print(json.dumps(r),flush=True)
json.dump(res,open('res_35.json','w'),indent=1)

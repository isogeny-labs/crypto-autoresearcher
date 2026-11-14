# Reduce the 49 Heegner points of 37a1 (K=Q(sqrt-7), conductors 1,3,5,13,15) mod primes ~2^30 that split completely in the ring class field of conductor 195
import json,sys,random,math,time
from fpg import *
d=json.load(open('data37c.json')); lv=sorted(int(k) for k in d['levels']); Dk=d['D']; top=max(lv,key=lambda m:d['levels'][str(m)]['h'])
ps=find_primes(Dk,math.lcm(*lv),2**30,2**30+2**28,5,bad=[d['N']]); print('primes',ps,[math.log2(p) for p in ps],flush=True)
H={m:d['levels'][str(m)]['h'] for m in lv}
alle=sorted(d['edges'],key=lambda e:-e['m'])
def embed(F):
    rts,_=F.roots(top); assert len(rts)==H[top],(len(rts),H[top])
    emb={top:rts[0]}
    for e in alle:
        n,m=e['n'],e['m']
        if m not in emb: continue
        v=F.Hval(n,m,emb[m])
        if n in emb: assert emb[n]==v
        else: emb[n]=v
    for m in sorted(lv,reverse=True):
        if m in emb: continue
        par=[e for e in alle if e['m']==m]
        good=[r for r in F.roots(m)[0] if all(F.Hval(e['n'],m,r)==emb[e['n']] for e in par)]
        assert good; emb[m]=good[0]
    return emb
out={};info=[]
for p in ps:
    t0=time.time(); F=Fp(p,d); emb=embed(F)
    pts={m:[to_short(q,p) for q in F.points(m,emb[m])] for m in lv}
    onc=all((v*v-u**3-CA*u-16)%p==0 for m in lv for u,v in pts[m])
    allp=[q for m in lv for q in pts[m]]; distinct=len(set(allp))
    ec=pari(f'ellinit([0,0,1,-1,0],{p})'); nE=int(pari.ellcard(ec))
    rel_ok=0;rel_tot=0
    for e in d['edges']:
        n,m,a=e['n'],e['m'],e['a']
        for i,row in enumerate(e['nb']):
            S=None
            for g in row: S=add(S,pts[m][g-1],p)
            rel_ok+=(S==mul(a,pts[n][i],p)); rel_tot+=1
    # order of subgroup spanned: exponent of span = lcm of orders (use factorisation of #E)
    fac=[(int(q),int(e)) for q,e in zip(*[list(map(int,x)) for x in pari.factor(nE).mat_to_vecs()] ) ] if False else None
    grp=[int(x) for x in pari.ellgroup(ec)]
    # compute subgroup order via lcm of point orders (lower bound for |<S>| when E(F_p) cyclic, equals exponent of span)
    ords=[]
    for q in set(allp):
        # map short-model point to original: u=4x, v=8y+4
        x=q[0]*pow(4,-1,p)%p; y=(q[1]-4)*pow(8,-1,p)%p
        ords.append(int(pari.ellorder(ec,pari(f'[Mod({x},{p}),Mod({y},{p})]'),nE)))
    expS=math.lcm(*ords)
    r={'p':p,'log2p':math.log2(p),'#E':nE,'group':grp,'on_curve':onc,'points':len(allp),'distinct':distinct,'relations_ok':rel_ok,'relations_total':rel_tot,'exponent_of_span':expS,'span_index_lower_bound':nE//expS if nE%expS==0 else None,'sec':round(time.time()-t0,1)}
    print(json.dumps(r),flush=True); info.append(r); out[str(p)]=allp
json.dump(out,open('pts30.json','w')); json.dump(info,open('pts30_info.json','w'),indent=1)

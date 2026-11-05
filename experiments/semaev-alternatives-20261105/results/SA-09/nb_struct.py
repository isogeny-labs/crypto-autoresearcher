# combinatorial relation structure (complex-analytic, prec 120): neighbour lists and rank by conductor bound
import cypari2,json,time
from fp import rank_modq
pari=cypari2.Pari(); pari.allocatemem(400*10**6); pari.set_real_precision(120)
pari('read("heeg.gp")'); pari('setM()'); pari('tol=10^(-120+40)')
lv=[1,5,7,35]; edges=[(1,5),(1,7),(5,35),(7,35)]
t0=time.time(); H={}
for m in lv:
    pari(f'Lv{m}=level({m},11)'); H[m]=int(pari(f'#Lv{m}')); print('level',m,H[m],time.time()-t0,flush=True)
E=[]
for n,m in edges:
    l=m//n; a=int(pari(f'ellan(E,{l})[{l}]'))
    pari(f'nbl=vector({H[n]},i, my(zs=nbz(Lv{n}[i][2],{l})); vector(#zs,k,matchidx(zs[k],Lv{m},tol)))')
    nb=[[int(x) for x in r] for r in pari('nbl')]
    pari(f'res=vecmax(vector({H[n]},i, my(zs=nbz(Lv{n}[i][2],{l}), s=vecsum(zs)-({a})*Lv{n}[i][3], d=zcs(s)); abs(d[1])+abs(d[2])))')
    res=float(pari('log(res+1e-99999)/log(10.)'))
    flat=[x for r in nb for x in r]; assert 0 not in flat and len(set(flat))==H[m]
    print('edge',n,m,'l',l,'a',a,'hecke residual log10',res,time.time()-t0,flush=True)
    E.append({'n':n,'m':m,'l':l,'a':a,'nb':nb,'res':res})
json.dump({'H':H,'edges':E},open('nb_struct.json','w'))
rt=[]
for bound in lv:
    sub=[m for m in lv if m<=bound]
    cols={}
    for m in sub:
        for i in range(H[m]): cols[(m,i)]=len(cols)
    rows=[]
    for e in E:
        if e['n'] in sub and e['m'] in sub:
            for i,row in enumerate(e['nb']):
                r=[0]*len(cols)
                for g in row: r[cols[(e['m'],g-1)]]+=1
                r[cols[(e['n'],i)]]-=e['a']
                rows.append(r)
    rk=rank_modq(rows,len(cols)) if rows else 0
    rt.append({'bound':bound,'points':len(cols),'relations':len(rows),'rank':rk,'ratio':rk/len(cols)})
    print(rt[-1])
json.dump(rt,open('rank_table_comb.json','w'),indent=1)

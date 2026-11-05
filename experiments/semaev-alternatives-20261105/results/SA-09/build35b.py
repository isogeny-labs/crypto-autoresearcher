# Resume run (SA-09, resumed executor): level-35 algebraisation at 1600 digits.
# Reuses neighbour lists from nb_struct.json (prec 120) instead of recomputing all 300 neighbour phiz values;
# spot-checks the first fibre of each edge at full precision. Levels 1,5,7 coefficient data are taken from data_157.json.
import cypari2,time,sys,json
prec=1600; out='data_35.json'
pari=cypari2.Pari(); pari.allocatemem(500*10**6); pari.set_real_precision(prec)
pari('read("heeg.gp")'); pari('setM()')
pari(f'bd=10^({prec}\\3); tol=10^(-{prec}+60)')
nbs=json.load(open('nb_struct.json'))
t0=time.time()
def log(*a): print(f'[{time.time()-t0:7.1f}s]',*a,flush=True)
data={'prec':prec,'levels':{},'edges':[]}
for m in [5,7,35]:
    pari(f'Lv{m}=level({m},11)'); log('level',m,'h',int(pari(f'#Lv{m}')))
m=35; h=144
pari(f'T35=grptab(Lv35); e35=principal(Lv35,35)')
errc=pari('vecmax(vector(#Lv35,i,abs(Lv35[i][5]^2-Lv35[i][4]^3-1)))')
pari('xs=vector(#Lv35,i,Lv35[i][4]); ys=vector(#Lv35,i,Lv35[i][5]); LM=lagmat(xs); M=LM[2]; P=LM[1]')
F=[]; maxerr=-9999
for d in range(1,h+1):
    r=pari(f'recvec(vector({h},c,xs[T35[c,{d}]])*M,bd)')
    F.append([[str(z) for z in q] for q in r[0]]); maxerr=max(maxerr,float(r[1]))
log(' f recognised, max log10 err',maxerr)
r=pari('recvec(ys*M,bd)'); G=[[str(z) for z in q] for q in r[0]]; maxerr=max(maxerr,float(r[1]))
r=pari('recvec(Vecrev(P),bd)'); Pc=[[str(z) for z in q] for q in r[0]]; maxerr=max(maxerr,float(r[1]))
sz=max(len(s) for f in F for q in f for s in q)
data['levels']['35']={'h':h,'e':int(pari('e35')),'F':F,'G':G,'P':Pc,'maxlogerr':maxerr,'maxdigits_F':sz,'curve_err':str(errc)[:12]}
log(' G,P recognised, max log10 err',maxerr,'max digits',sz)
json.dump(data,open(out,'w'))
for e in nbs['edges']:
    n,mm,l,a,nb=e['n'],e['m'],e['l'],e['a'],e['nb']
    if mm!=35: continue
    # spot check first fibre at full precision
    chk=[int(x) for x in pari(f'my(zs=nbz(Lv{n}[1][2],{l})); vector(#zs,k,matchidx(zs[k],Lv35,tol))')]
    res=float(pari(f'my(zs=nbz(Lv{n}[1][2],{l}), s=vecsum(zs)-({a})*Lv{n}[1][3], d=zcs(s)); log(abs(d[1])+abs(d[2])+1e-99999)/log(10.)'))
    assert chk==nb[0], ('fibre mismatch',n,chk,nb[0])
    par=[0]*144
    for i,row in enumerate(nb):
        for g in row: par[g-1]=i+1
    assert 0 not in par
    parv=str(par).replace(' ','')
    r=pari(f'recvec(vector(144,g,Lv{n}[Vec({parv})[g]][4])*M,bd)')
    H=[[str(z) for z in q] for q in r[0]]
    log('edge',n,'->',35,'l',l,'a',a,'fibre1 match ok, residual log10',res,'H maxerr',float(r[1]),'H maxdigits',max(len(s) for q in H for s in q))
    data['edges'].append({'n':n,'m':35,'l':l,'a':a,'nb':nb,'par':par,'H':H,'hecke_res_log10_fibre1':res,'H_logerr':float(r[1])})
    json.dump(data,open(out,'w'))
log('written',out)

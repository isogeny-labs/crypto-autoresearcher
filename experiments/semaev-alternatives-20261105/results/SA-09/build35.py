import cypari2,time,sys,json
prec=int(sys.argv[1]); levels=[int(a) for a in sys.argv[2].split(',')]
edges=[(int(a.split('>')[0]),int(a.split('>')[1])) for a in sys.argv[3].split(',')]  # n>m
out=sys.argv[4]
pari=cypari2.Pari(); pari.allocatemem(500*10**6); pari.set_real_precision(prec)
pari('read("heeg.gp")'); pari('setM()')
pari(f'bd=10^({prec}\\3); tol=10^(-{prec}+60)')
SKIP=[int(a) for a in sys.argv[5].split(',')] if len(sys.argv)>5 else []
data={'prec':prec,'levels':{},'edges':[]}
t0=time.time()
def log(*a): print(f'[{time.time()-t0:7.1f}s]',*a,flush=True)
for m in levels:
    pari(f'Lv{m}=level({m},11); T{m}=grptab(Lv{m}); e{m}=principal(Lv{m},{m})')
    h=int(pari(f'#Lv{m}')); log('level',m,'h',h)
    errc=pari(f'vecmax(vector(#Lv{m},i,abs(Lv{m}[i][5]^2-Lv{m}[i][4]^3-1)))')
    e=int(pari(f'e{m}'))
    if m in SKIP:
        continue
    pari(f'xs=vector(#Lv{m},i,Lv{m}[i][4]); ys=vector(#Lv{m},i,Lv{m}[i][5]); LM=lagmat(xs); M=LM[2]; P=LM[1]')
    # f_d for all d : X_d = f_d(x_e)
    F=[]; maxerr=-9999
    for d in range(1,h+1):
        r=pari(f'recvec(vector({h},c,xs[T{m}[c,{d}]])*M,bd)')
        F.append([[str(z) for z in q] for q in r[0]]); maxerr=max(maxerr,float(r[1]))
    log(' f recognised, max log10 err',maxerr)
    r=pari('recvec(ys*M,bd)'); G=[[str(z) for z in q] for q in r[0]]; maxerr=max(maxerr,float(r[1]))
    r=pari('recvec(Vecrev(P),bd)'); Pc=[[str(z) for z in q] for q in r[0]]; maxerr=max(maxerr,float(r[1]))
    log(' G,P recognised, max log10 err',maxerr)
    # sizes
    sz=max(len(s) for f in F for q in f for s in q)
    data['levels'][m]={'h':h,'e':e,'F':F,'G':G,'P':Pc,'maxlogerr':maxerr,'maxdigits_F':sz,'curve_err':str(errc)[:12]}
    log(' max digits in F',sz)
for (n,m) in edges:
    if m in SKIP: continue
    l=m//n; a=int(pari(f'ellan(E,{l})[{l}]')); hn=int(pari(f'#Lv{n}')); hm=int(pari(f'#Lv{m}'))
    pari(f'nbl=vector({hn},i, my(zs=nbz(Lv{n}[i][2],{l})); vector(#zs,k,matchidx(zs[k],Lv{m},tol)))')
    nb=[[int(x) for x in row] for row in pari('nbl')]
    flat=[x for r in nb for x in r]
    assert 0 not in flat and len(set(flat))==hm, ('neighbour matching failed',n,m,len(set(flat)),hm)
    # residual of Hecke relation
    pari(f'res=vecmax(vector({hn},i, my(zs=nbz(Lv{n}[i][2],{l}), s=vecsum(zs)-({a})*Lv{n}[i][3], d=zcs(s)); abs(d[1])+abs(d[2])))')
    res=float(pari('log(res+1e-99999)/log(10.)'))
    par=[0]*hm
    for i,row in enumerate(nb):
        for g in row: par[g-1]=i+1
    pari('nbl=0')
    # H_{n<-m}: nodes x^{(m)}; values x^{(n)}_{par}
    pari(f'xs=vector({hm},i,Lv{m}[i][4]); LM=lagmat(xs); M=LM[2]')
    parv=str(par).replace(' ','')
    r=pari(f'recvec(vector({hm},g,Lv{n}[Vec({parv})[g]][4])*M,bd)')
    H=[[str(z) for z in q] for q in r[0]]
    log('edge',n,'->',m,'l',l,'a_l',a,'hecke residual log10',res,'H maxerr',float(r[1]),'H maxdigits',max(len(s) for q in H for s in q))
    data['edges'].append({'n':n,'m':m,'l':l,'a':a,'nb':nb,'par':par,'H':H,'hecke_res_log10':res,'H_logerr':float(r[1])})
json.dump(data,open(out,'w'))
log('written',out)

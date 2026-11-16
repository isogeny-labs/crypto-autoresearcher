# usage: build_gen2.py prec items out curve N D beta nbjson ; items like L13,L39,E3>39 ; merges into out
import cypari2,time,sys,json,os
prec=int(sys.argv[1]); items=sys.argv[2].split(',')
out,CURVE,NN,DK,BETA,nbf=sys.argv[3],sys.argv[4],int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]),sys.argv[8]
pari=cypari2.Pari(); pari.allocatemem(800*10**6); pari.set_real_precision(prec)
pari(f'E=ellinit({CURVE}); Nn={NN}; Dk={DK}'); pari('read("heegN.gp")'); pari('setM()')
pari(f'bd=10^({prec}\\3); tol=10^(-{prec}+60)')
nbs=json.load(open(nbf)); 
data=json.load(open(out)) if os.path.exists(out) else {'N':NN,'D':DK,'curve':CURVE,'prec':prec,'levels':{},'edges':[]}
t0=time.time()
def log(*a): print(f'[{time.time()-t0:7.1f}s]',*a,flush=True)
def lev(m):
    if f'Lv{m}' in have: return
    pari(f'Lv{m}=level({m},{BETA})'); have.add(f'Lv{m}')
have=set()
for it in items:
    if it[0]=='L':
        m=int(it[1:]); lev(m); h=int(pari(f'#Lv{m}'))
        pari(f'T{m}=grptab(Lv{m}); e{m}=principal(Lv{m},{m})')
        pari(f'xs=vector(#Lv{m},i,Lv{m}[i][4]); ys=vector(#Lv{m},i,Lv{m}[i][5]); LM=lagmat(xs); M=LM[2]; P=LM[1]')
        errc=pari(f'vecmax(vector(#Lv{m},i,abs(Lv{m}[i][5]^2+Lv{m}[i][5]-Lv{m}[i][4]^3+Lv{m}[i][4])))')
        F=[]; maxerr=-9999
        for d in range(1,h+1):
            r=pari(f'recvec(vector({h},c,xs[T{m}[c,{d}]])*M,bd)')
            F.append([[str(z) for z in q] for q in r[0]]); maxerr=max(maxerr,float(r[1]))
        r=pari('recvec(ys*M,bd)'); G=[[str(z) for z in q] for q in r[0]]; maxerr=max(maxerr,float(r[1]))
        r=pari('recvec(Vecrev(P),bd)'); Pc=[[str(z) for z in q] for q in r[0]]; maxerr=max(maxerr,float(r[1]))
        sz=max(len(s) for f in F for q in f for s in q)
        data['levels'][str(m)]={'h':h,'e':int(pari(f'e{m}')),'F':F,'G':G,'P':Pc,'maxlogerr':maxerr,'maxdigits_F':sz,'curve_err':str(errc)[:12],'prec':prec}
        log('level',m,'h',h,'maxlogerr',round(maxerr,1),'maxdigits',sz,'bd digits',prec//3)
    else:
        n,m=[int(x) for x in it[1:].split('>')]; lev(n); lev(m)
        e=[x for x in nbs['edges'] if x['n']==n and x['m']==m][0]; l,a,nb=e['l'],e['a'],e['nb']; hm=len(set(g for r in nb for g in r))
        chk=[int(x) for x in pari(f'my(zs=nbz(Lv{n}[1][2],{l})); vector(#zs,k,matchidx(zs[k],Lv{m},tol))')]
        res=float(pari(f'my(zs=nbz(Lv{n}[1][2],{l}), s=vecsum(zs)-({a})*Lv{n}[1][3], d=zcs(s)); log(abs(d[1])+abs(d[2])+1e-99999)/log(10.)'))
        assert chk==nb[0],('fibre mismatch',n,m)
        par=[0]*hm
        for i,row in enumerate(nb):
            for g in row: par[g-1]=i+1
        assert 0 not in par
        pari(f'xs=vector({hm},i,Lv{m}[i][4]); LM=lagmat(xs); M=LM[2]')
        parv=str(par).replace(' ','')
        r=pari(f'recvec(vector({hm},g,Lv{n}[Vec({parv})[g]][4])*M,bd)')
        Hh=[[str(z) for z in q] for q in r[0]]
        data['edges']=[x for x in data['edges'] if not (x['n']==n and x['m']==m)]
        data['edges'].append({'n':n,'m':m,'l':l,'a':a,'nb':nb,'par':par,'H':Hh,'hecke_res_log10_fibre1':res,'H_logerr':float(r[1])})
        log('edge',n,'>',m,'fibre1 ok res',round(res,1),'H maxerr',round(float(r[1]),1),'H maxdigits',max(len(s) for q in Hh for s in q))
    json.dump(data,open(out,'w'))

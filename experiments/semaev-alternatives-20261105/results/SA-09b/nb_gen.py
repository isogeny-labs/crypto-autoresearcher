# neighbour lists (complex analytic, low precision). usage: nb_gen.py prec levels edges out curve N D beta
import cypari2,json,time,sys
from fpg import rank_modq
prec=int(sys.argv[1]); lv=[int(a) for a in sys.argv[2].split(',')]
edges=[(int(a.split('>')[0]),int(a.split('>')[1])) for a in sys.argv[3].split(',')]
out,CURVE,NN,DK,BETA=sys.argv[4],sys.argv[5],int(sys.argv[6]),int(sys.argv[7]),int(sys.argv[8])
pari=cypari2.Pari(); pari.allocatemem(400*10**6); pari.set_real_precision(prec)
pari(f'E=ellinit({CURVE}); Nn={NN}; Dk={DK}'); pari('read("heegN.gp")'); pari('setM()'); pari(f'tol=10^(-{prec}+40)')
t0=time.time(); H={}
for m in lv:
    pari(f'Lv{m}=level({m},{BETA})'); H[m]=int(pari(f'#Lv{m}')); print('level',m,H[m],round(time.time()-t0,1),flush=True)
E=[]
for n,m in edges:
    l=m//n; a=int(pari(f'ellan(E,{l})[{l}]'))
    pari(f'nbl=vector({H[n]},i, my(zs=nbz(Lv{n}[i][2],{l})); vector(#zs,k,matchidx(zs[k],Lv{m},tol)))')
    nb=[[int(x) for x in r] for r in pari('nbl')]
    pari(f'res=vecmax(vector({H[n]},i, my(zs=nbz(Lv{n}[i][2],{l}), s=vecsum(zs)-({a})*Lv{n}[i][3], d=zcs(s)); abs(d[1])+abs(d[2])))')
    res=float(pari('log(res+1e-99999)/log(10.)'))
    flat=[x for r in nb for x in r]; assert 0 not in flat and len(set(flat))==H[m],('match fail',n,m)
    print('edge',n,m,'l',l,'a',a,'hecke residual log10',round(res,1),round(time.time()-t0,1),flush=True)
    E.append({'n':n,'m':m,'l':l,'a':a,'nb':nb,'res':res})
json.dump({'H':H,'edges':E,'D':DK,'N':NN},open(out,'w'))

# Char-0 relation lattice among Heegner points in E(C)=C/Lambda via LLL on lattice coordinates.
import cypari2,sys,json,time
from fpylll import IntegerMatrix, LLL
levels=[int(a) for a in sys.argv[1].split(',')]; prec=int(sys.argv[2]); out=sys.argv[3]
pari=cypari2.Pari(); pari.allocatemem(400*10**6); pari.set_real_precision(prec)
pari('read("heeg.gp")'); pari('setM()')
D=prec-40
pts=[]; lab=[]
t0=time.time()
for m in levels:
    pari(f'Z=vector(#heegner_forms({m},11),i,phiz(tau_of(heegner_forms({m},11)[i],{m})))') if False else None
    pari(f'HF={m}; Hs=heegner_forms({m},11); Zs=vector(#Hs,i,zcs(phiz(tau_of(Hs[i],{m}))))')
    h=int(pari('#Zs'))
    for i in range(h):
        u=pari(f'floor(Zs[{i+1}][1]*10^{D}+1/2)'); v=pari(f'floor(Zs[{i+1}][2]*10^{D}+1/2)')
        pts.append((int(u),int(v))); lab.append((m,i))
    print('level',m,h,time.time()-t0,flush=True)
n=len(pts); B=IntegerMatrix(n+2,n+2)
for i,(u,v) in enumerate(pts):
    B[i,i]=1; B[i,n]=u; B[i,n+1]=v
B[n,n]=0; B[n,n]=0
B[n,n]=10**D; B[n+1,n+1]=10**D
# columns n, n+1 hold the weighted residuals; rows n,n+1 hold the integer shifts
# (first n columns for these two rows are 0)
t=time.time(); LLL.reduction(B); print('LLL',time.time()-t,flush=True)
norms=[]
for r in range(n+2):
    row=[B[r,c] for c in range(n+2)]
    nm=sum(x*x for x in row[:n])**0.5; res=max(abs(row[n]),abs(row[n+1]))
    norms.append((nm,res,sum(1 for x in row[:n] if x)))
norms.sort()
print([ (round(a,2),float(b),c) for a,b,c in norms[:40]])
json.dump({'levels':levels,'n':n,'prec':prec,'D':D,'sorted_norm_resid_support':[(a,float(b),c) for a,b,c in norms]},open(out,'w'))

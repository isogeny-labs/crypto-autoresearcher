import polys, random
from polys import *
a,b=3,5
o=build(a,b,4)
S5=o[4]
print([int(pari(f'poldegree({S5},{v})')) for v in ['x1','x2','x3','x4','x5']], int(pari.poldegree(o[3],'x1')))
# numeric test over F_p
p=1000003
E=pari(f"E=ellinit([{a},{b}],{p});")
import cypari2
for trial in range(3):
    pts=[]
    while len(pts)<4:
        x=random.randrange(p)
        r=pari(f"E=ellinit([{a},{b}],{p}); ellordinate(E,{x})")
        if len(r)>0: pts.append(pari(f"[{x},{int(r[0])}]*Mod(1,{p})"))
    pari(f"E=ellinit([{a},{b}],{p});")
    pts=[pari(f"[Mod({int(P[0].lift())},{p}),Mod({int(P[1].lift())},{p})]") for P in pts]
    s=pari(f"E=ellinit([{a},{b}],{p});0")
    tot=pari(f"elladd(E,[{int(pts[0][0].lift())},{int(pts[0][1].lift())}],[{int(pts[1][0].lift())},{int(pts[1][1].lift())}])")
    for P in pts[2:]:
        tot=pari(f"elladd(E,{tot},[{int(P[0].lift())},{int(P[1].lift())}])")
    x5=int(tot[0].lift())
    xs=[int(P[0].lift()) for P in pts]+[x5]
    val=pari(f"subst(subst(subst(subst(subst({S5},x1,{xs[0]}),x2,{xs[1]}),x3,{xs[2]}),x4,{xs[3]}),x5,{xs[4]})")
    print(int(val)%p)

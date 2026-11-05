import cypari2
pari=cypari2.Pari()
# positive control: s=2, P=(2,8) on Y^2=X^3+56 (from x=1); Q=3P+nothing. Map 3P and P to E(F_p) and test 3P1=P2 relation via pipeline
s=2; E=pari('ellinit([0,56])'); P=pari('[2,8]'); P3=pari.ellmul(E,P,3)
hm=pari.ellheightmatrix(E,[P,P3]); ratio=pari.bestappr(hm[0,1]/hm[1,1],1000)
print('rank',pari.ellrank(E)[:2],'ratio P1/P2 =',ratio,'(expect 1/3)')
p=int(pari('nextprime(2^40+99)'))
while int(pari.kronecker(s,p))!=1: p=int(pari.nextprime(p+1))
rs=int(pari(f'lift(sqrt(Mod({s},{p})))'))
Ep=pari(f'ellinit([0,7],{p})')
def red(Q): # twist (X,Y)->(X/s, Y*sqrt(s)/s^2)
    X,Y=Q
    return pari(f'[Mod({X}/{s},{p}),Mod({Y}*{rs}/{s*s},{p})]') if False else [pari(f'Mod({int(X.numerator())},{p})/Mod({int(X.denominator())*s},{p})'), pari(f'Mod({int(Y.numerator())},{p})*{rs}/Mod({int(Y.denominator())*s*s},{p})')]
R1=red(P); R2=red(P3)
print(pari.ellisoncurve(Ep,R1),pari.ellisoncurve(Ep,R2))
print('3*R1-R2 =',pari.elladd(Ep,pari.ellmul(Ep,R1,3),pari.ellneg(Ep,R2)))

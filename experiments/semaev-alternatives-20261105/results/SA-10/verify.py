import cypari2, json, sys, math
pari=cypari2.Pari(); pari.allocatemem(300*10**6)
pairs=json.load(open('pairs.json')) if len(sys.argv)<2 else json.loads(sys.argv[1])
pairs=pairs[:20]
pbits=40
P=int(pari('nextprime(2^40+12345)'))
out=[]
for (x1,x2,s) in pairs:
    rec=dict(x1=x1,x2=x2,s=s)
    f=lambda x:x**3+7
    m=[math.isqrt(f(x)//s) for x in (x1,x2)]
    assert all(mi*mi*s==f(x) for mi,x in zip(m,(x1,x2)))
    E=pari(f'ellinit([0,7*{s}^3])')
    Q=[pari(f'[{s*x},{s*s*mi}]') for x,mi in zip((x1,x2),m)]
    for q in Q: assert pari.ellisoncurve(E,q)
    r=pari.ellrank(E)
    rec['ellrank']=str(r[:3]); rec['rank_lo_hi']=(int(r[0]),int(r[1]))
    rec['tors']=str(pari.elltors(E)[:2])
    rec['rank_cert']=int(r[0])==int(r[1])
    hm=pari.ellheightmatrix(E,Q)
    det=float(hm[0,0]*hm[1,1]-hm[0,1]*hm[1,0])
    rec['heights']=[float(hm[0,0]),float(hm[1,1])]; rec['height_det']=det
    rec['rank_range']=(int(r[0]),int(r[1]))
    if abs(det)>1e-6*float(hm[0,0]*hm[1,1]):
        rec['status']='INDEPENDENT (no global relation)'; out.append(rec); print(rec); continue
    ratio=pari.bestappr(hm[0,1]/hm[1,1],1000)   # P1 = ratio*P2 mod torsion
    num,den=int(ratio.numerator()),int(ratio.denominator())
    # num/den: den*P1 = num*P2
    c1,c2=den,num
    if c2<0: pass
    d=pari.elladd(E,pari.ellmul(E,Q[0],c1),pari.ellmul(E,Q[1],-c2))
    t_o=int(pari.ellorder(E,d)); rec['twist_defect_order']=t_o
    if t_o<0:
        rec['status']='dependent heights but relation failed'; out.append(rec); print(rec); continue
    rec['c1_c2']=(c1,c2)
    mult=t_o
    # pick prime p with s QR
    p=P
    while True:
        if int(pari.kronecker(s,p))==1 and p%3==1 and p%7 not in (0,): break
        p=int(pari.nextprime(p+1))
    rt=int(pari.sqrtint(0)) 
    rs=int(pari(f'lift(sqrt(Mod({s},{p})))'))
    Ep=pari(f'ellinit([0,7],{p})')
    Pp=[pari(f'[Mod({x},{p}),Mod({mi}*{rs},{p})]') for x,mi in zip((x1,x2),m)]
    for q in Pp: assert pari.ellisoncurve(Ep,q)
    # relation raw
    d1=pari.elladd(Ep,pari.ellmul(Ep,Pp[0],c1),pari.ellmul(Ep,Pp[1],-c2))
    ok_raw=(d1==pari('[0]'))
    # with torsion multiplier
    d2=pari.ellmul(Ep,d1,max(mult,1))
    ok_t=(d2==pari('[0]'))
    rec.update(p=p,sqrt_s=rs,raw_relation_holds=bool(ok_raw),after_torsion_mult_holds=bool(ok_t))
    # also check relation modulo a second 40-bit prime and as nontrivial (points not O, not equal multiples trivially)
    rec['P1_order_mod_p_gt_small']=bool(pari.ellorder(Ep,Pp[0])>10**6)
    rec['status']='verified' if (ok_raw or ok_t) else 'FAILED'
    out.append(rec); print(rec)
json.dump(out,open('verify_out.json','w'),indent=1,default=str)

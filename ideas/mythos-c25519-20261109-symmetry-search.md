# Mythos ECDLP ideation — symmetry-search (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

## LEADS

Notation: $p=2^{255}-19$, $a=-1$, $d=-121665/121666$, $A=486662$, $a_{24}=121665$, $i=2^{(p-1)/4}=\sqrt{-1}$. Extended model $E\subset\mathbb P^3$: $-X^2+Y^2=Z^2+dT^2,\; XY=ZT$, $x=X/Z,\;y=Y/Z,\;T/Z=xy$. Rational torsion used: $O=(0{:}1{:}1{:}0)$, $T_2=(0{:}-1{:}1{:}0)$, $T_4=(i{:}0{:}1{:}0)$, $-T_4=(-i{:}0{:}1{:}0)$; $\langle T_4\rangle=\{O,T_4,T_2,-T_4\}$. Over $\mathbb F_p(\sqrt d)$ the four points with $Z=0$: $\pm Q_\infty=(0{:}\pm\sqrt d{:}0{:}1)$, $Q_2=(\sqrt{-d}{:}0{:}0{:}1)$, $Q_2'=(-\sqrt{-d}{:}0{:}0{:}1)$. $\Delta_Q=\{(P_1,P_2):P_2-P_1=Q\}\subset E\times E$. Op counts assume $a=-1$, $d$ non-square, $B=1$, cofactor 8.

**1. `[known]` HCD-2008 extended addition, $a=-1$ Niels form — baseline, and the repository is 3 M + 1 I above it.**
$A=(Y_1-X_1)(Y_2-X_2),\;B=(Y_1+X_1)(Y_2+X_2),\;C=2d\,T_1T_2,\;D=2Z_1Z_2,\;E=B-A,\;F=D-C,\;G=D+C,\;H=B+A$; $X_3=EF,\;Y_3=GH,\;Z_3=FG,\;T_3=EH$. Cost 8M+1c (7M mixed, $Z_2=1$). Complete on $E(\mathbb F_p)\times E(\mathbb F_p)$: $F,G\neq0$ because $Z_1Z_2=\pm dT_1T_2$ would force $d$ square. Symmetry: $(X,Y)\mapsto(Y\!-\!X,Y\!+\!X)$ is the rational hyperbolic rotation that diagonalises the pair $(X_1Y_2{+}Y_1X_2,\;Y_1Y_2{+}X_1X_2)$; it is rational exactly because $-a=1$ is a square. Repo `EdPoint::add` computes `C` as `fe_mul(fe_mul(T1,2), fe_mul(d,T2))` (3 M), `D` as 2 M, and calls `ed25519_d()` — one `fe_inv` — per addition: measured 11M+0S+1I. Replace with the law above with `d` a cached constant: saves 3 M + 1 I per add. Surface: `src/ecc/ed25519.rs::EdPoint::add`.

**2. `[known]` HCD doubling, $a=-1$, and the T-lazy variant.** $A=X^2,B=Y^2,C=2Z^2,E=(X+Y)^2-A-B,G=B-A,F=G-C,H=-(A+B)$; $X_3=EF,Y_3=GH,Z_3=FG,T_3=EH$: 4M+4S. Repo computes $C$ via `fe_mul(2, Z²)`: 5M+4S. If the next operation is another doubling, skip $T_3$: 3M+4S (keep $(E,F,G,H)$ as the "completed" intermediate; HCD/EFD `dbl-2008-hwcd`). Complete on all points (doubling has no exceptional input on a complete Edwards curve). Symmetry: coordinate scaling only. Surface: `EdPoint::double`, `scalar_mul`.

**3. `[adaptation]` Ansatz A solved: the bidegree-(2,2) addition laws on the $\mathbb P^3$ model form a 4-dimensional space with a Segre basis $L_{\alpha\beta}$, $\alpha,\beta\in\{s,d\}$.**
Ansatz: $X_3,Y_3,Z_3,T_3$ are bihomogeneous forms of bidegree (2,2) in $(X_1,Y_1,Z_1,T_1)\times(X_2,Y_2,Z_2,T_2)$; 100 monomials each, 400 unknowns; constraint $(X_3{:}Y_3{:}Z_3{:}T_3)=P_1{+}P_2$ wherever nonzero, imposed as $X_3-x_3Z_3=Y_3-y_3Z_3=T_3-x_3y_3Z_3=0$ at sampled pairs; quotient by the $4\cdot36$-dimensional ideal part. Solution (predicted $D=4$, script asserts it): spanned by
$x$-pencil $(E,G)$ with $E=x_3G$ on $E\times E$: $(E_s,G_s)=(X_1Y_2{+}Y_1X_2,\;Z_1Z_2{+}dT_1T_2)$, $(E_d,G_d)=(T_1Z_2{+}Z_1T_2,\;Y_1Y_2{-}X_1X_2)$;
$y$-pencil $(H,F)$ with $H=y_3F$: $(H_s,F_s)=(Y_1Y_2{+}X_1X_2,\;Z_1Z_2{-}dT_1T_2)$, $(H_d,F_d)=(T_1Z_2{-}Z_1T_2,\;X_1Y_2{-}Y_1X_2)$;
$L_{\alpha\beta}=(E_\alpha F_\beta,\;G_\alpha H_\beta,\;F_\beta G_\alpha,\;E_\alpha H_\beta)$. $L_{ss}$ is HCD; $L_{dd}$ is HCD's dual law; $L_{sd},L_{ds}$ are new mixed members.
Exceptional divisors (hand-verified on the listed translates, script re-asserts): $L_{ss}$: $\Delta_{Q_\infty}{+}\Delta_{-Q_\infty}{+}\Delta_{Q_2}{+}\Delta_{Q_2'}$ (no $\mathbb F_p$-point ⇒ complete). $L_{dd}$: $\Delta_O{+}\Delta_{T_2}{+}\Delta_{T_4}{+}\Delta_{-T_4}$. $L_{sd}$: $\Delta_O{+}\Delta_{T_2}{+}\Delta_{Q_\infty}{+}\Delta_{-Q_\infty}$. $L_{ds}$: $\Delta_{T_4}{+}\Delta_{-T_4}{+}\Delta_{Q_2}{+}\Delta_{Q_2'}$. Each is a coset of one of the two cyclic order-4 subgroups $\langle T_4\rangle,\langle Q_\infty\rangle$ of the order-8 group $\langle T_4,Q_\infty\rangle\subset E[4]$. Group action: translations are linear on the model: $\tau_{T_2}=(-X,-Y,Z,T)$, $\tau_{T_4}=(iY,iX,Z,-T)$, $\tau_{Q_\infty}=(\sqrt d X,-\sqrt d Y,dT,-Z)$, $\tau_{Q_2}=(\sqrt{-d}\,Y,-\sqrt{-d}\,X,dT,Z)$, negation $\iota=(-X,Y,Z,-T)$; every $L_{\alpha\beta}$ is equivariant (an eigenvector) under $\iota$ and the rational translations, and the model isomorphism $\psi:(X,Y,Z,T)\mapsto(T,Z,Y,X)$ onto $E_{d,a}$ ($y\mapsto1/y$) pulls the $E_{d,a}$-standard law back to $L_{ds}$ — this is where "dual" comes from. Input swap $S_2$: $L_{ss},L_{ds}$ are $+1$, $L_{sd},L_{dd}$ are $-1$ (all four coordinates negate). Costs: $L_{ss}$ 8M+1c, $L_{dd}$ 8M+0c, $L_{sd},L_{ds}$ 12M+1c. Surface: `tools/ansatz_edwards25519.sage` (below), test module beside `ed25519.rs`. **Record 1.**

**4. `[adaptation]` The dual law $L_{dd}$ needs no $d$: 8M+0c in the same Niels cache, with cross pairing.**
$A'=(Y_1{+}X_1)(Y_2{-}X_2),\;B'=(Y_1{-}X_1)(Y_2{+}X_2),\;C'=T_1Z_2,\;D'=Z_1T_2$; $E=2(C'{+}D'),\;F=A'{-}B',\;G=A'{+}B',\;H=2(C'{-}D')$; $X_3=EF,Y_3=GH,Z_3=FG,T_3=EH$ (all scaled by 4 relative to $L_{dd}$). Identity check: $A'{+}B'=2(Y_1Y_2{-}X_1X_2)=2G_d$, $A'{-}B'=2(X_1Y_2{-}Y_1X_2)=2F_d$. Exception: all four outputs vanish iff $P_2-P_1\in\langle T_4\rangle$; in particular never usable for doubling ($S_2$-antisymmetry forces $L(P,P)=0$). Branch-free. Use: differential-test oracle for `add` (Lead 10) and an $8$M+$0$c add in windowed multiplication where the table entry is provably $\notin$ acc$+\langle T_4\rangle$ (needs an argument per use; not claimed as a speedup for the repo's double-and-add, which does hit acc$=P$).

**5. `[speculative]` Lower bound: no straight-line program of the two-level shape (bilinear forms, then pairwise products) computes any law in the Ansatz-A space in fewer than 8 non-scalar multiplications; the separable ansatz is worse.**
Any $L$ in the space is, by the Segre structure, $(EF,GH,FG,EH)$ with $E,G$ in the $x$-pencil and $H,F$ in the $y$-pencil. (i) $EF,GH,FG,EH$ are four linearly independent quadratic forms in $(E,F,G,H)$ (pairwise distinct products of the 2×2 outer product $(E,G)^\top(F,H)$), and each multiplication or squaring adds at most one dimension to the span of computed quadratics ⇒ ≥4 final-level multiplications. (ii) For every $(\lambda{:}\mu),(\lambda'{:}\mu')$ the four bilinear forms $\lambda E_s{+}\mu E_d,\dots$ are linearly independent on $E\times E$ (the 16 bilinear monomials are independent there, rank asserted by the script) ⇒ bilinear tensor rank ≥4 ⇒ ≥4 bilinear-level multiplications. Total ≥8, attained by Leads 1 and 4. Ansatz C ("separable": $X_3=\sum_j q_j(P_1)r_j(P_2)$) was exhausted: $X_3^{ss}$ expands to $X_1Z_1{\cdot}Y_2Z_2+Y_1Z_1{\cdot}X_2Z_2-dX_1T_1{\cdot}Y_2T_2-dY_1T_1{\cdot}X_2T_2$ (separable rank 4), likewise $Y_3$ (4), $T_3$ (4), $Z_3=Z_1^2Z_2^2-d^2T_1^2T_2^2$ (2): 14M plus 8 cached per-point products — dominated. Scope caveat: this bounds the two stratified ansätze, not every straight-line program (mixed-degree cancellation tricks are outside the ansatz). Surface: same script, section 5.

**6. `[speculative]` $S_2$-invariant Montgomery ladder: the step is symmetric in the two registers, the secret bit enters only as the sign of one antisymmetric coordinate; symmetry costs 2 M per step.**
State for registers $R_0=(X_0{:}Z_0),R_1=(X_1{:}Z_1)$ with $R_1-R_0=P=(u_P{:}1)$: $\sigma_1=X_0Z_1{+}X_1Z_0,\;\sigma_2=X_0X_1,\;\pi=Z_0Z_1,\;\delta=X_0Z_1{-}X_1Z_0$ (bidegree (1,1), one common scale; relation $\sigma_1^2-\delta^2=4\sigma_2\pi$). Step with bit $b$, $s=1-2b$: $u=\sigma_1+s\delta\;(=2X_bZ_{1-b}),\;w=2\pi\;(=2Z_bZ_{1-b})$; if $u=w=0$ (⇔ $R_{1-b}=O$, ⇔ $R_b=\mp P$) set $(u,w)\leftarrow(u_P,1)$ by constant-time cmov. Doubling: $A=u{+}w,\;B=u{-}w,\;AA=A^2,\;BB=B^2,\;E=AA{-}BB,\;X_D=AA\cdot BB,\;Z_D=E(AA+a_{24}E)$ [2M+2S+1c]. Differential add (symmetric): $X_A=(\sigma_2-\pi)^2,\;Z_A=u_P\,\delta^2$ [1M+2S] (RFC's $DA{+}CB=2(\sigma_2{-}\pi)$, $DA{-}CB=-2\delta$). New state: $\sigma_1'=X_DZ_A{+}X_AZ_D,\;\sigma_2'=X_DX_A,\;\pi'=Z_DZ_A,\;\delta'=s\,(X_DZ_A{-}X_AZ_D)$ [4M]. Start after the forced bit 254: $R_0=P,\;R_1=2P=((u_P^2{-}1)^2{:}4u_P(u_P^2{+}Au_P{+}1))$; last step outputs $R_0'=\mathrm{cmov}_b((X_D{:}Z_D),(X_A{:}Z_A))$, $x=X_0'\cdot Z_0'^{\,p-2}$. Cost 7M+4S+1c + 2 conditional negations + 1 zero-test + 1 cmov, vs RFC 5M+4S+1c + 2 cswaps. Complete for all $u$ (collapses to 0 on low-order inputs exactly where RFC does). Branch-free, uniform bit reads. Symmetry: the group $S_2\times\{\pm1\}$ acting on $(R_0,R_1)$ and on $\delta$; the standard step is *not* $S_2$-symmetric (it doubles $R_0$). Surface: new `ladder_sym` in `x25519.rs`, test `s2_ladder == rfc_ladder` on RFC vectors, random $u$, low-order $u$. **Record 2.**

**7. `[adaptation]` Constant-time Ed25519 scalar multiplication through the existing ladder: zero-cost Edwards→Kummer map, Okeya–Sakurai $v$-recovery, RFC 7748 §4.1 map back.**
Edwards $(X{:}Y{:}Z{:}T)\mapsto$ Montgomery $(U{:}W)=(Z{+}Y{:}Z{-}Y)$ (0 M; this *is* the Edwards $y$-line ladder). Affine input $P=(x,y)$: $u_P=(1{+}y)/(1{-}y),\;v_P=c\,u_P/x,\;c^2=-486664$. Ladder returns $(X_2{:}Z_2)=[k]P,\;(X_3{:}Z_3)=[k{+}1]P$. Recovery ($B=1$, derived by eliminating $v_Q^2$ between $v_Q^2=u_Q^3{+}Au_Q^2{+}u_Q$ and the chord formula): $v_Q=\frac{(u_Pu_Q{+}1)(u_P{+}u_Q)+2Au_Pu_Q-u_{Q+P}(u_Q{-}u_P)^2}{2v_P}$; projectively $N=[(u_PX_2{+}Z_2)(u_PZ_2{+}X_2)+2AX_2Z_2]Z_3-X_3(X_2{-}u_PZ_2)^2,\;D'=2v_PZ_2Z_3,\;(X_Q{:}Y_Q{:}Z_Q)=(X_2D'{:}N{:}Z_2D')$ [10M+1S+1c]. Back: $y=(X_Q{-}Z_Q)/(X_Q{+}Z_Q),\;x=c\,X_Q/Y_Q$ [1I batched: 5M+1c+1I]. Sign of $c$ cancels in the round trip (script asserts both signs agree). Exceptions: $P\in\{O,T_2\}$ ($x=0$), $[k]P\in\{O,-P\}$ ($Z_2=0$ or $Z_3=0$) — fix by final cmov; any $0\le k<2^{255}$ (leading zeros are handled by the $(1{:}0)$ start). Cost per 255-bit scalar: $255(5M{+}4S{+}1c)+15M{+}1S{+}2c{+}1I\approx1290M{+}1021S{+}257c{+}1I$ vs repo `scalar_mul` ≈ $255(5M{+}4S)+127(11M{+}1I)=2672M{+}1020S{+}127I$ (ideal HCD: $2036M{+}1020S{+}127c$), variable-time. **Record 3.**

**8. `[known]` Ladder step is 5M+4S+1c; the repo executes 9M+1c.** `aa=fe_mul(a,a)`, `bb`, `x3=fe_mul(s,s)`, `dm_sq` are squarings; `fe_sq` exists in `curve25519.rs` and is already used by `ed25519.rs`. Surface: `x25519.rs::ladder`.

**9. `[adaptation]` Zero-cost metamorphic oracles from the model's linear automorphisms.** (a) Montgomery: $u(P{+}(0,0))=1/u(P)$, so for clamped (even) $k$: `x25519(k, u⁻¹) == x25519(k, u)` for all $u\neq0$ (curve and twist). (b) Edwards: $[k](P{+}T_4)=[k]P+[k\bmod4]T_4$ with $\tau_{T_4}(X,Y,Z,T)=(iY,iX,Z,-T)$: `scalar_mul(k, τ(P)) == τ^{k mod 4}(scalar_mul(k,P))`; (c) $\iota$: `scalar_mul(k, neg P) == neg scalar_mul(k,P)`. Each buys a self-checking test with no new arithmetic. Surface: tests beside `x25519.rs`, `ed25519.rs`.

**10. `[adaptation]` Completeness control that proves too much on purpose.** Over $\mathbb F_{p^2}=\mathbb F_p(\sqrt d)$ the four laws are a complete system (at every pair at least one is nonzero and all nonzero ones agree) and $L_{ss}$ vanishes identically on $\Delta_{\pm Q_\infty},\Delta_{Q_2},\Delta_{Q_2'}$; over $\mathbb F_p$ it never vanishes. A test harness for `add` must observe the failures in $\mathbb F_{p^2}$ and none in $\mathbb F_p$; a harness that passes on both is not testing completeness. Paired with the dual-law oracle of Lead 4 (`add == L_dd` off $P_2{-}P_1\in\langle T_4\rangle$; `L_dd == 0` on it). **Record 4.**

**11. `[known]` Permanent rotated representation $(U,V,Z,T)=(Y{-}X,Y{+}X,Z,T)$, checked and dominated.** Addition keeps 8M+1c (saves 4 additions). Doubling: $G=UV$ (1M), $E=(V^2{-}U^2)/2$, $H=-(U^2{+}V^2)/2$ (2S), $C=2Z^2$ (1S), then 4 products: 5M+3S vs 4M+4S — a 1S→1M trade, a loss whenever S<M. Filed as exhausted.

**12. `[known]` Free involution and inversion-free equality.** $\iota$ costs 2 negations ⇒ signed windows halve tables; verification equality $X_1Z_2=X_2Z_1\wedge Y_1Z_2=Y_2Z_1$ (2M) replaces `to_affine` (1I). Surface: `EdPoint::neg`, `is_identity`/encode-compare paths.

**13. `[speculative]` Complete-system selection is dominated.** Choosing the first nonzero of $L_{ss},L_{sd},L_{ds},L_{dd}$ branch-free costs ≥ 8M+12M+… per add; since $L_{ss}$ alone is complete over $\mathbb F_p$, this is only useful over extensions (e.g. pairing or $\mathbb F_{p^2}$ twist code), not for the repo. Filed to close the direction.

### Script: `tools/ansatz_edwards25519.sage` (run: `sage tools/ansatz_edwards25519.sage`)

```python
# Ansatz search for bidegree-(2,2) addition laws on the P^3 model of Edwards25519,
# the two bilinear pencils, exceptional divisors, S2/Heisenberg characters,
# the Ansatz-B rank bound, the S2-invariant ladder and the ladder->Edwards composition.
import itertools, random
random.seed(25519)
p = 2**255 - 19; F = GF(p)
a = F(-1); d = F(-121665)/F(121666); A = F(486662); a24 = F(121665)
assert (-F(1)).is_square() and not d.is_square()                      # completeness hypotheses
assert not F(2).is_square() and not F(486660).is_square() and F(-486664).is_square()
i_ = F(-1).sqrt()
O  = (F(0),F(1),F(1),F(0)); T2 = (F(0),F(-1),F(1),F(0))
T4 = (i_,F(0),F(1),F(0));   T4n = (-i_,F(0),F(1),F(0))

def rand_pt(K=F):
    while True:
        y = K.random_element(); num = y**2 - 1; den = K(d)*y**2 + 1   # x^2=(y^2-1)/(d y^2-a)
        if den != 0 and (num/den).is_square():
            x = (num/den).sqrt() * (-1)**random.randint(0,1); z = K.random_element()
            if z: return (x*z, y*z, z, x*y*z)
def on_curve(P): X,Y,Z,T = P; return a*X**2+Y**2 == Z**2+d*T**2 and X*Y == Z*T
def same(P,Q): return all(P[i]*Q[j] == P[j]*Q[i] for i in range(4) for j in range(4))
def is_zero(P): return all(c == 0 for c in P)

# ---- Segre basis of the law space (Ansatz A/B) ----
def forms(P,Q):
    X1,Y1,Z1,T1 = P; X2,Y2,Z2,T2_ = Q
    return dict(Es=X1*Y2+Y1*X2, Gs=Z1*Z2+d*T1*T2_, Hs=Y1*Y2-a*X1*X2, Fs=Z1*Z2-d*T1*T2_,
                Ed=T1*Z2+Z1*T2_, Gd=Y1*Y2+a*X1*X2, Hd=T1*Z2-Z1*T2_, Fd=X1*Y2-Y1*X2)
def law(P,Q,xs,ys):
    f = forms(P,Q); E,G = f['E'+xs],f['G'+xs]; H,Fm = f['H'+ys],f['F'+ys]
    return (E*Fm, G*H, Fm*G, E*H)                                     # (X3,Y3,Z3,T3)
LAWS = {'ss':('s','s'),'sd':('s','d'),'ds':('d','s'),'dd':('d','d')}
def add_aff(P,Q):                                                     # oracle: complete affine law
    x1,y1 = P[0]/P[2],P[1]/P[2]; x2,y2 = Q[0]/Q[2],Q[1]/Q[2]
    x3 = (x1*y2+y1*x2)/(1+d*x1*x2*y1*y2); y3 = (y1*y2-a*x1*x2)/(1-d*x1*x2*y1*y2)
    return (x3,y3,F(1),x3*y3)

# (1) correctness where nonzero, (2) rational exceptional divisors, (3) S2 character
EXC = {'ss':[], 'sd':[O,T2], 'ds':[T4,T4n], 'dd':[O,T2,T4,T4n]}
for _ in range(200):
    P,Q = rand_pt(),rand_pt(); S = add_aff(P,Q)
    for k,(xs,ys) in LAWS.items():
        L = law(P,Q,xs,ys); assert not is_zero(L) and same(L,S), k
        sgn = 1 if k in ('ss','ds') else -1
        assert all(law(Q,P,xs,ys)[j] == sgn*L[j] for j in range(4)), ('S2',k)
for k,(xs,ys) in LAWS.items():
    for T in [O,T2,T4,T4n]:
        for _ in range(30):
            P = rand_pt(); Q = law(P,T,'s','s')                       # Q = P + T via complete law
            assert is_zero(law(P,Q,xs,ys)) == (T in EXC[k]), (k,T)

# (4) dimension of the bidegree-(2,2) law space modulo the ideal
R = PolynomialRing(F,'X1,Y1,Z1,T1,X2,Y2,Z2,T2'); v = R.gens()
m1 = list(itertools.combinations_with_replacement(v[:4],2)); m2 = list(itertools.combinations_with_replacement(v[4:],2))
mons = [u[0]*u[1]*w[0]*w[1] for u in m1 for w in m2]                 # 100 monomials
pairs = [(rand_pt(),rand_pt()) for _ in range(700)]
def ev(m,P,Q): return m(*(list(P)+list(Q)))
r_fun = matrix(F,[[ev(m,P,Q) for m in mons] for P,Q in pairs]).rank(); assert r_fun == 64
rows = []; z = [F(0)]*100
for P,Q in pairs:
    S = add_aff(P,Q); x3,y3 = S[0],S[1]; e = [ev(m,P,Q) for m in mons]
    rows.append(e+z+[-x3*c for c in e]+z); rows.append(z+e+[-y3*c for c in e]+z)
    rows.append(z+z+[-x3*y3*c for c in e]+e)
Kl = matrix(F,rows).right_kernel(); D = Kl.dimension() - 4*(100-r_fun)
print('dim bidegree-(2,2) addition laws mod ideal =', D); assert D == 4
def law_poly(xs,ys):
    L = law(v[:4],v[4:],xs,ys); return vector(F,sum([[c.monomial_coefficient(m) for m in mons] for c in L],[]))
for k in LAWS: assert law_poly(*LAWS[k]) in Kl
assert matrix(F,[sum([list(law(P,Q,*LAWS[k])) for P,Q in pairs[:60]],[]) for k in LAWS]).rank() == 4

# (5) Ansatz B: the two pencils and the rank-4 obstruction
bil = [u*w for u in v[:4] for w in v[4:]]
assert matrix(F,[[ev(m,P,Q) for m in bil] for P,Q in pairs]).rank() == 16
for idx,name in ((0,'x-pencil (E,G)'),(1,'y-pencil (H,F)')):
    rows = []
    for P,Q in pairs:
        S = add_aff(P,Q); e = [ev(m,P,Q) for m in bil]; rows.append(e+[-S[idx]*c for c in e])
    dimp = matrix(F,rows).right_kernel().dimension(); print(name,'dim =',dimp); assert dimp == 2
fs = forms(v[:4],v[4:]); coeffs = lambda b: [b.monomial_coefficient(m) for m in bil]
for _ in range(50):
    l,m,l2,m2 = [F.random_element() for _ in range(4)]
    E = l*fs['Es']+m*fs['Ed']; G = l*fs['Gs']+m*fs['Gd']; H = l2*fs['Hs']+m2*fs['Hd']; Fm = l2*fs['Fs']+m2*fs['Fd']
    assert matrix(F,[coeffs(b) for b in (E,G,H,Fm)]).rank() == 4      # => >= 4 bilinear mults, >= 8 total

# (6) group action: rational translations and negation are linear and every law is equivariant
tau_T4 = lambda P: (i_*P[1], i_*P[0], P[2], -P[3]); neg = lambda P: (-P[0],P[1],P[2],-P[3])
P = rand_pt(); assert same(tau_T4(P), law(P,T4,'s','s'))
for k,(xs,ys) in LAWS.items():
    P,Q = rand_pt(),rand_pt()
    assert same(law(tau_T4(P),Q,xs,ys), tau_T4(law(P,Q,xs,ys)))
    assert same(law(neg(P),neg(Q),xs,ys), neg(law(P,Q,xs,ys)))

# (7) F_{p^2} control: complete system, and the exceptional divisor of L_ss is the 4 points at infinity
K2 = GF(p**2,'w'); sd = K2(d).sqrt(); smd = (-K2(d)).sqrt()
INF = [(K2(0),sd,K2(0),K2(1)),(K2(0),-sd,K2(0),K2(1)),(smd,K2(0),K2(0),K2(1)),(-smd,K2(0),K2(0),K2(1))]
for Qi in INF:
    assert on_curve(Qi)
    for _ in range(20):
        P = rand_pt(K2); Ls = [law(P,Qi,*LAWS[k]) for k in LAWS]; nz = [L for L in Ls if not is_zero(L)]
        assert nz and all(same(nz[0],L) for L in nz)                  # complete system over F_{p^2}
        assert is_zero(law(P,nz[0],'s','s'))                          # L_ss vanishes on Delta_{Q_inf}
for _ in range(50): P,Q = rand_pt(),rand_pt(); assert not is_zero(law(P,Q,'s','s'))

# (8) RFC 7748 ladder, S2-invariant ladder, metamorphic 1/u test
def rfc_pair(k,u):
    x2,z2,x3,z3,sw = F(1),F(0),u,F(1),0
    for t in range(254,-1,-1):
        kt = (k>>t)&1
        if sw^kt: x2,x3,z2,z3 = x3,x2,z3,z2
        sw = kt
        Aa=x2+z2; AA=Aa**2; Bb=x2-z2; BB=Bb**2; E=AA-BB; C=x3+z3; Dd=x3-z3; DA=Dd*Aa; CB=C*Bb
        x3=(DA+CB)**2; z3=u*(DA-CB)**2; x2=AA*BB; z2=E*(AA+a24*E)
    if sw: x2,x3,z2,z3 = x3,x2,z3,z2
    return x2,z2,x3,z3
rfc = lambda k,u: (lambda r: r[0]*r[1]**(p-2))(rfc_pair(k,u))
def s2_ladder(k,u):                                                   # k clamped: bit 254 set
    assert (k>>254)&1 == 1
    X2,Z2 = (u**2-1)**2, 4*u*(u**2+A*u+1)                             # R0 = P, R1 = 2P
    s1,s2,pi,de = u*Z2+X2, u*X2, Z2, u*Z2-X2
    for t in range(253,-1,-1):
        b = (k>>t)&1; s = 1-2*b
        uu,w = s1+s*de, 2*pi
        if uu == 0 and w == 0: uu,w = u,F(1)                           # R_{1-b}=O  (cmov in Rust)
        Aa=uu+w; Bb=uu-w; AA=Aa**2; BB=Bb**2; E=AA-BB; Xd=AA*BB; Zd=E*(AA+a24*E)
        Xa=(s2-pi)**2; Za=u*de**2
        s1,s2,pi,de = Xd*Za+Xa*Zd, Xd*Xa, Zd*Za, s*(Xd*Za-Xa*Zd)
        if t == 0: X0,Z0 = (Xd,Zd) if b == 0 else (Xa,Za)              # single final cmov
    return X0*Z0**(p-2)
def clamp(k): return (k & ~7 & ((1<<255)-1)) & ~(1<<255) | (1<<254)
LOW = [F(0),F(1),F(p-1),F(325606250916557431795983626356110631294008115727848805560023387167927233504),
       F(39382357235489614581723060781553021112529911719440698176882885853963445705823)]
for u in LOW: assert rfc(8|(1<<254)*0 if False else clamp(8),u) == 0   # all low-order inputs -> 0
for _ in range(40):
    k = clamp(random.getrandbits(256)); u = random.choice(LOW+[F.random_element() for _ in range(5)])
    assert s2_ladder(k,u) == rfc(k,u)
    if u != 0: assert rfc(k,1/u) == rfc(k,u)                           # tau_{(0,0)} metamorphic test
assert rfc(clamp(0xa546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4),
           F(0x4c1cabd0a603a9103b35b326ec2466727c5fb124a4c19435db3030586768dbe6)) == \
       F(0xc3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552)         # RFC 7748 vector 1 (LE ints)

# (9) composition: Edwards scalar multiplication through the x-only ladder
c = F(-486664).sqrt()
def ed_mul(k,P):
    Rr = O
    for t in range(255,-1,-1):
        Rr = law(Rr,Rr,'s','s')
        if (k>>t)&1: Rr = law(Rr,P,'s','s')
    return Rr
def ed_via_ladder(k,P,cc):
    x,y = P[0]/P[2],P[1]/P[2]; uP = (1+y)/(1-y); vP = cc*uP/x
    X2,Z2,X3,Z3 = rfc_pair(k,uP)
    N = ((uP*X2+Z2)*(uP*Z2+X2) + 2*A*X2*Z2)*Z3 - X3*(X2-uP*Z2)**2; Dp = 2*vP*Z2*Z3
    XQ,YQ,ZQ = X2*Dp, N, Z2*Dp
    yE = (XQ-ZQ)/(XQ+ZQ); xE = cc*XQ/YQ
    return (xE,yE,F(1),xE*yE)
for _ in range(20):
    P = rand_pt(); k = random.randrange(2,2**253)
    assert same(ed_mul(k,P), ed_via_ladder(k,P,c)) and same(ed_via_ladder(k,P,c), ed_via_ladder(k,P,-c))
print('all assertions passed')
```

Primary assertions: `D == 4`; both pencils have dimension 2; rank-4 of every pencil member's factor set (the 8-multiplication floor in Ansatz B); the rational/infinite exceptional divisors of $L_{ss},L_{sd},L_{ds},L_{dd}$ as listed; $S_2$ characters $(+,-,+,-)$; `s2_ladder == rfc` on random, RFC and low-order inputs; `ed_mul == ed_via_ladder`. (The test on line `for u in LOW` should read `assert rfc(clamp(8),u) == 0` — a stray conditional was left in that line; the intended assertion is the clamped-scalar zero output on the five low-order inputs.)

# Mythos ECDLP ideation — symmetry-search (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

**Status.** I had no tools, so the script below has not been run. The polynomial identities, characters, op counts and exceptional sets were derived by hand in this session. The dimension result is also argued by hand but should be treated as pending until assertions A2/A3 pass. Literature references are recalled pointers, not support.

**Result of the search.** The ansatz was exhausted and no law below 8M exists in it. The solution space is a product of two pencils whose corners are the two HWCD laws. The search produced four useful items: a classification with a lower bound, an exact exceptional set for the swap-odd law, a 13M+1c sum-and-difference pair, and a 2S small-order test.

## LEADS

**Notation.** Extended coordinates $(X:Y:Z:T)$, $x=X/Z$, $y=Y/Z$, $XY=ZT$, on $-x^2+y^2=1+dx^2y^2$. Write $U=Y+X$, $V=Y-X$, $t=x_1x_2y_1y_2$, $\delta=P_1-P_2$, $i=\sqrt{-1}$, $k=2d$. The eight bilinear forms used throughout:

$$N_x^s=X_1Y_2+Y_1X_2,\quad D_x^s=Z_1Z_2+dT_1T_2,\quad N_y^s=Y_1Y_2+X_1X_2,\quad D_y^s=Z_1Z_2-dT_1T_2$$
$$N_x^d=T_1Z_2+Z_1T_2,\quad D_x^d=Y_1Y_2-X_1X_2,\quad N_y^d=T_1Z_2-Z_1T_2,\quad D_y^d=X_1Y_2-Y_1X_2$$

Superscript $s$ is the unified (standard) law and $d$ is the dual law.

**1. `[adaptation]` Bilinear ansatz on the extended coordinate ring: solved, 8M floor.**
- **Ansatz $\mathcal A$:** $x_3=N_x/D_x$, $y_3=N_y/D_y$, each form in $R_1\otimes R_1$ with $R_1=\langle X,Y,Z,T\rangle$, weight $(1,1)$ under independent scaling of the two inputs. That is 16 monomials per form and 64 unknowns. Outputs are $X_3=N_xD_y$, $Y_3=N_yD_x$, $Z_3=D_xD_y$, $T_3=N_xN_y$ (4M).
- **Solution:** $(N_x,D_x)=\lambda(N_x^s,D_x^s)+\mu(N_x^d,D_x^d)$ and $(N_y,D_y)=\lambda'(N_y^s,D_y^s)+\mu'(N_y^d,D_y^d)$. Nothing else.
- **Why dimension 2:** the 16 monomials are independent on $E\times E$ ($E\subset\mathbb P^3$ is a non-degenerate quartic). Denominators are sections of a bundle of degree 0 on the fibres of $\delta$, so any nonzero section has divisor $\delta^*(\text{degree-2 divisor})$ and $h^0=2$.
- **Exact identities (hand-checked)**, with $c_j=-x_j^2+y_j^2-1-dx_j^2y_j^2$:
  - $(x_1y_1+x_2y_2)(1+dt)-(x_1y_2+y_1x_2)(y_1y_2-x_1x_2)=-x_1y_1c_2-x_2y_2c_1$
  - $(x_1y_1-x_2y_2)(1-dt)-(y_1y_2+x_1x_2)(x_1y_2-y_1x_2)=-x_1y_1c_2+x_2y_2c_1$
- **Group action:** $\tau=(i,0)$ has order 4 and acts linearly, $(X,Y,Z,T)\mapsto(iY,iX,Z,-T)$. It is diagonal on $(U,V,Z,T)$ with characters $(i,-i,1,-1)$. The group $\Gamma=\langle\tau_{\rm anti}:(P_1,P_2)\mapsto(P_1+\tau,P_2-\tau),\ \sigma:\text{swap},\ \nu\times\nu\rangle\cong D_4\times C_2$ has order 16.
- **Orbits:** the 16 eigen-monomials split 4+4+4+4 by $\tau_{\rm anti}$-character.
  - $\chi^0$: $U_1U_2,V_1V_2,Z_1Z_2,T_1T_2$. These are exactly the four HWCD unified products.
  - $\chi^2$: $U_1V_2,V_1U_2,Z_1T_2,T_1Z_2$. These are exactly the four HWCD dedicated products.
  - $\chi^{\pm1}$: the eight monomials $U_1Z_2,Z_1V_2,V_1T_2,T_1U_2$ and $U_1T_2,T_1V_2,Z_1U_2,V_1Z_2$.
  - Under $\langle\sigma,\nu\rangle$ (signs ignored) the orbit sizes are 2,1,1,2,2,4,4.
- **Obstruction:** both pencils have eigenlines only in $\chi^0$ and $\chi^2$, so the $\chi^{\pm1}$ monomials carry no law.
- **Lower bound:** the eight basis forms have disjoint monomial supports. So for every $(\lambda{:}\mu),(\lambda'{:}\mu')$ the four forms are linearly independent, which forces at least 4 layer-1 products. With 4 output products the floor is 8M.
- **Corner costs over $\mathbb F_p$:** $ss$ = 8M+1c (HWCD unified), $dd$ = 8M (HWCD dedicated), $sd$ = $ds$ = 9M+1c.
- **Completeness:** the law fails iff $\lambda+\mu\,y(\delta)=0$ or $\lambda'+\mu'\,x(\delta)=0$.
- **Exhausted:** $\mathcal A$. **Not exhausted:** non-pure bidegree-(2,2) outputs, intra-point products and squarings, cached operands.
- **Surface:** new `scripts/ed25519_law_ansatz.py` (A1–A7); informs `EdPoint::add`.

**2. `[adaptation]` The swap-odd law and what the symmetry costs.**
- **Law** (HWCD dedicated, $a=-1$): $A=V_1U_2$, $B=U_1V_2$, $C=2Z_1T_2$, $D=2T_1Z_2$, $E=D+C$, $F=B-A$, $G=B+A$, $H=D-C$; $X_3=EF$, $Y_3=GH$, $Z_3=FG$, $T_3=EH$.
- **Count:** 8M + 0c + 10a.
- **Symmetry:** $\sigma$ acts freely on the products ($A\leftrightarrow B$, $C\leftrightarrow D$) and sends the output 4-vector to its negative. The unified law fixes each product and the vector.
- **Cost of the symmetry:** a $\sigma$-odd polynomial vector vanishes on the diagonal, so no such law can double. The exact exceptional set is $Z_3=0\iff\delta\in E(\mathbb F_p)[4]=\{(0,\pm1),(\pm i,0)\}$, because $F=2D_y^d\propto x(\delta)$ and $G=2D_x^d\propto y(\delta)$.
- **What it buys:** no $d$, and $Z_3=0$ is a free test for equality modulo $E[4]$.
- **Validity in `scalar_mul`** (MSB-first, $\mathrm{ord}\,P=\ell$): the add step has $\delta=(2\lfloor k/2^{j+1}\rfloor-1)P$. It is never exceptional for $0\le k<\ell$. It is exceptional for the clamped scalars with $k\gg 3=(\ell+1)/2$.
- **Constant time:** branch-free, but not complete.
- **Surface:** `EdPoint::add` variant; A5, A8.

**3. `[adaptation]` Co-Z sum-and-difference pair.**
- **Symmetry:** the involution $P_2\mapsto-P_2$ acts on layer 1 as $U_2\leftrightarrow V_2$, $C\mapsto-C$, and fixes $Z_3=D^2-C^2$.
- **Law:** $A=V_1V_2$, $B=U_1U_2$, $A'=V_1U_2$, $B'=U_1V_2$, $C=k\,T_1T_2$, $D=2Z_1Z_2$, $F=D-C$, $G=D+C$, $E=B-A$, $H=B+A$, $E'=B'-A'$, $H'=B'+A'$, $Z_\pm=FG$.
  - $P_1+P_2=(EF:GH:Z_\pm:EH)$
  - $P_1-P_2=(E'G:FH':Z_\pm:E'H')$
- **Count:** 13M + 1c + 11a, against 16M + 2c + 18a for two HWCD unified adds.
- **Completeness:** complete on $E(\mathbb F_p)$, since both halves are the unified law. Branch-free.
- **Use:** the joint table $\{A,B,A+B,A-B\}$ for $[s]B-[h]A$ in verification. The shared $Z$ lets one inversion normalise both points.
- **Surface:** `src/ecc/ed25519.rs`; A9.

**4. `[adaptation]` Small-order predicate in 2S.**
- **Predicate:** $P\in E(\mathbb F_p)[8]\iff XY(X^2+Y^2)=0\iff U^4=V^4$. Test $U^2=V^2$ or $U^2=-V^2$.
- **Count:** 2S + 3a, 0M, 0I.
- **Proof:** complete doubling gives $T(2P)=EH=-2XY(X^2+Y^2)$ with $Z(2P)\ne0$, and $E(\mathbb F_p)[4]=\{T=0\}$.
- **Baseline:** assumed three doublings plus `is_identity`, which is 12M + 12S + 3 fe_mul-by-2 + 1I + 2M as coded. The verify path is not in the BRIEF excerpt, so this baseline is an assumption.
- **Limit:** it does not replace the $[\ell]P$ subgroup check.
- **Surface:** `ed25519.rs` verify; A10.

**5. `[adaptation]` A pencil of complete swap-even laws (negative on cost).**
- **Law**, with $A,B$ as in lead 3, $W=(Z_1+T_1)(Z_2+T_2)-Z_1Z_2-T_1T_2$, $Q=4Y_1Y_2-A-B$:
  - $2N_x=(B-A)+2\kappa W$
  - $2D_x=2Z_1Z_2+k\,T_1T_2+\kappa Q$
  - $2N_y=A+B$
  - $2D_y=2Z_1Z_2-k\,T_1T_2$
- **Count:** 10M + 3c.
- **Completeness:** complete on $E(\mathbb F_p)$ iff $-1/\kappa\notin y(E(\mathbb F_p))$, i.e. iff $(1-\kappa^2)/(\kappa^2+d)$ is a non-residue.
- **Reading:** completeness is not unique to the unified law, but the unified corner is the only complete law at the 8M floor among the corners. The pencil costs 2M more.
- **Surface:** A7.

**6. `[speculative]` Hyperplane classification of all bidegree-(2,2) laws.**
- **Recalled statement** (Kohel 2011, pointer only): the full space is $W_x\otimes W_y$ of dimension 4, and the law attached to $aX+bY+cZ+eT$ fails iff $\delta$ lies on that hyperplane.
- **Correspondence:** $Z\leftrightarrow ss$, $T\leftrightarrow dd$, $X\leftrightarrow sd$, $Y\leftrightarrow ds$.
- **Consequence if true:** a law is complete iff its hyperplane misses $E(\mathbb F_p)$. Swap-odd laws are $aX+eT$ and always contain $(0,\pm1)$.
- **Test:** enumerate a complete $a=-1$ Edwards curve over a small prime in `scripts/ed_hyperplane_laws.sage`.

**7. `[known]` HWCD unified with cached $k=2d$ (baseline hygiene, HCD 2008).**
- **Current cost:** `EdPoint::add` performs 12 `fe_mul` and 1 `fe_inv` per call, because `ed25519_d()` recomputes $121666^{-1}$ on every call.
- **Target:** 8M + 1c + 9a. This removes an inversion from the hot path.
- **Also:** `double` spends one `fe_mul` on $2\cdot Z^2$, which should be an addition (4M + 4S).

**8. `[adaptation]` Completeness and rank are coupled in the mixed laws.**
- The pair $\{Z_1Z_2\pm dT_1T_2,\ T_1Z_2\mp Z_1T_2\}$ is a $2\times2\times2$ tensor with slices $M_1,M_2$. The eigenvalues of $M_1^{-1}M_2$ satisfy $\lambda^2=-1/d$.
- Since $d$ is a non-square, the rank is 3 over $\mathbb F_p$ and 2 over $\mathbb F_p(\sqrt{-d})$.
- So $sd$ and $ds$ cost 9M+1c on Curve25519, and would cost 8M exactly on curves where the unified law is incomplete.
- **Surface:** A6.

**9. `[adaptation]` Ed25519 scalar multiplication through the X25519 ladder.**
- **Edwards $y$ is free:** the ladder variables $a=X_2+Z_2$, $b=X_2-Z_2$ give $y([k]P)=b/a$. This is the Hadamard symmetry $(X:Z)\mapsto(X+Z:X-Z)$.
- **Sign of $x$ by Okeya–Sakurai** from $(X_Q:Z_Q)=[k]P$, $(X_\oplus:Z_\oplus)=[k+1]P$, affine $(x_P,y_P)$:
  - $Y'=Z_\oplus\left[(X_Q+x_PZ_Q+2AZ_Q)(x_PX_Q+Z_Q)-2AZ_Q^2\right]-(X_Q-x_PZ_Q)^2X_\oplus$
  - $X'=2y_PZ_QZ_\oplus X_Q$, $\quad Z'=2y_PZ_QZ_\oplus Z_Q$
  - Cost: 10M + 1S + 2c.
- **Map to extended Edwards**, $c=\sqrt{-486664}$: $(cX'(X'+Z'):Y'(X'-Z'):Y'(X'+Z'):cX'(X'-Z'))$, 4M + 1c. The script fixes the sign of $c$ by asserting that $u=9$ maps to `base_x()`.
- **Total:** 1289M + 1021S + 258c, uniform. Double-and-add, even after lead 7, is about 2020M + 1012S + 126c and variable-time.
- **Exceptions:** $k\equiv0,-1\pmod\ell$ (where $Z'=0$) and $y_P=0$. The locus $u=-1$ has no rational point because $A-2$ is a non-square.
- **Surface:** `x25519.rs::ladder` (expose $x_3,z_3$) and `ed25519.rs`.

**10. `[known]` Ladder-state invariant from the biquadratic forms.**
- **Forms:** $B_{00}=(X_2X_3-Z_2Z_3)^2$, $B_{11}=(X_2Z_3-Z_2X_3)^2$, $B_{01}=(X_2Z_3+Z_2X_3)(X_2X_3+Z_2Z_3)+2AX_2Z_2X_3Z_3$.
- **Invariant:** $B_{11}x_1^2-2B_{01}x_1+B_{00}=0$ at every step.
- **Symmetry:** translation by $(0,0)$, $(X:Z)\mapsto(Z:X)$, swaps $B_{00}\leftrightarrow B_{11}$ and fixes $B_{01}$.
- **Count:** 8M + 3S + 1c per check.
- **Surface:** property test in `x25519.rs` tests.

**11. `[known]` $\tau$-eigen coordinates $(U,V,Z,T)$ as state: exhausted, no gain.**
- **Add:** $Z_3=FG$, $T_3=EH$, $U_3=(G+E)(H+F)-Z_3-T_3$, $V_3=(G-E)(H+F)-Z_3+T_3$. This is 8M + 1c with 11a.
- **Double:** $G=UV$, $E=(U^2-V^2)/2$, $H=-(U^2+V^2)/2$, which is 5M + 3S (or 4M + 4S).

**12. `[known]` Hot-path hygiene outside the formulas.**
- `is_identity` should test $X=0\wedge Y=Z$ projectively (0M) instead of 1I + 2M.
- The ladder calls `fe_mul` 10 times per step where RFC 7748 needs 5M + 4S + 1c; use `fe_sq`.
- `if s == 1 { swap }` is a scalar-dependent branch, despite the module comment. An arithmetic cswap removes it, but `BigUint` stays variable-time.

### Script (`scripts/ed25519_law_ansatz.py`, not run)

```python
#!/usr/bin/env python3
"""Ansatz solve + checks for bilinear addition laws on Edwards25519 (extended coords).
A1 identities | A2 symbolic solve (generic d): dim W_x = dim W_y = 2 | A3 nullity 2 at
Curve25519's d | A4 tau characters | A5 swap parity | A6 rank obstruction | A7 pencil
exceptional set | A8 dedicated law fails iff P1-P2 in E[4] | A9 co-Z pair | A10 small order."""
import random
import sympy as sp

p = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
inv = lambda a: pow(a % p, p - 2, p)
leg = lambda a: pow(a % p, (p - 1) // 2, p)
d = (-121665 * inv(121666)) % p
I = pow(2, (p - 1) // 4, p)
assert I * I % p == p - 1 and leg(d) == p - 1 and leg(-1) == 1
rng = random.Random(20261109)

def sqrt_mod(a):
    a %= p
    r = pow(a, (p + 3) // 8, p)
    for c in (r, r * I % p):
        if c * c % p == a:
            return c
    return None

def rand_aff():
    while True:
        y = rng.randrange(p)
        x = sqrt_mod((y * y - 1) * inv(1 + d * y * y))   # x^2 = (y^2-1)/(1+d y^2)
        if x is not None:
            return ((-x) % p if rng.getrandbits(1) else x, y)

def aadd(P, Q):
    (x1, y1), (x2, y2) = P, Q
    t = d * x1 * x2 * y1 * y2 % p
    return ((x1*y2 + y1*x2) * inv(1 + t) % p, (y1*y2 + x1*x2) * inv(1 - t) % p)
aneg = lambda P: ((-P[0]) % p, P[1])
def amul(k, P):
    R = (0, 1)
    while k:
        if k & 1: R = aadd(R, P)
        P = aadd(P, P); k >>= 1
    return R
def ext(P):
    z = rng.randrange(1, p)
    return (P[0]*z % p, P[1]*z % p, z, P[0]*P[1]*z % p)
def aff(E):
    X, Y, Z, T = E
    assert Z % p != 0 and (X*Y - Z*T) % p == 0
    return (X * inv(Z) % p, Y * inv(Z) % p)

def forms(P1, P2):
    X1, Y1, Z1, T1 = P1; X2, Y2, Z2, T2 = P2
    return dict(Nxs=(X1*Y2 + Y1*X2) % p, Dxs=(Z1*Z2 + d*T1*T2) % p,
                Nys=(Y1*Y2 + X1*X2) % p, Dys=(Z1*Z2 - d*T1*T2) % p,
                Nxd=(T1*Z2 + Z1*T2) % p, Dxd=(Y1*Y2 - X1*X2) % p,
                Nyd=(T1*Z2 - Z1*T2) % p, Dyd=(X1*Y2 - Y1*X2) % p)

def law(P1, P2, lx=(1, 0), ly=(1, 0)):          # (lambda:mu) x (lambda':mu')
    f = forms(P1, P2)
    Nx = (lx[0]*f['Nxs'] + lx[1]*f['Nxd']) % p; Dx = (lx[0]*f['Dxs'] + lx[1]*f['Dxd']) % p
    Ny = (ly[0]*f['Nys'] + ly[1]*f['Nyd']) % p; Dy = (ly[0]*f['Dys'] + ly[1]*f['Dyd']) % p
    return (Nx*Dy % p, Ny*Dx % p, Dx*Dy % p, Nx*Ny % p), Dx, Dy

def known(dv):                                   # coefficient vectors, index 4*i+j, (X,Y,Z,T)=0..3
    def vec(N, D):
        v = [0] * 32
        for (i, j), c in N.items(): v[4*i + j] = c
        for (i, j), c in D.items(): v[16 + 4*i + j] = c
        return v
    return dict(xs=vec({(0, 1): 1, (1, 0): 1}, {(2, 2): 1, (3, 3): dv}),
                xd=vec({(3, 2): 1, (2, 3): 1}, {(1, 1): 1, (0, 0): -1}),
                ys=vec({(1, 1): 1, (0, 0): 1}, {(2, 2): 1, (3, 3): -dv}),
                yd=vec({(3, 2): 1, (2, 3): -1}, {(0, 1): 1, (1, 0): -1}))

# ---- A1: exact identities with explicit cofactors (generic d) ----
x1, y1, x2, y2, dd = sp.symbols('x1 y1 x2 y2 d')
c1 = -x1**2 + y1**2 - 1 - dd*x1**2*y1**2
c2 = -x2**2 + y2**2 - 1 - dd*x2**2*y2**2
tt = x1*x2*y1*y2
assert sp.expand((x1*y1 + x2*y2)*(1 + dd*tt) - (x1*y2 + y1*x2)*(y1*y2 - x1*x2)
                 + x1*y1*c2 + x2*y2*c1) == 0
assert sp.expand((x1*y1 - x2*y2)*(1 - dd*tt) - (y1*y2 + x1*x2)*(x1*y2 - y1*x2)
                 + x1*y1*c2 - x2*y2*c1) == 0

# ---- A2: symbolic solve of the ansatz, generic d ----
MON = [a*b for a in (x1, y1, 1, x1*y1) for b in (x2, y2, 1, x2*y2)]
def solve_ansatz(Ns, Ds, vecs, tag):
    n = sp.symbols('n%s_0:16' % tag); e = sp.symbols('e%s_0:16' % tag)
    N = sum(c*m for c, m in zip(n, MON)); D = sum(c*m for c, m in zip(e, MON))
    P = sp.Poly(sp.expand(N*Ds - D*Ns), y1, y2)
    r1, s1, r2, s2 = 1 + x1**2, 1 - dd*x1**2, 1 + x2**2, 1 - dd*x2**2   # y_j^2 = r_j/s_j
    red = 0
    for (a, b), c in P.terms():
        assert a <= 2 and b <= 2
        red += c * (r1 if a == 2 else s1) * (r2 if b == 2 else s2) * y1**(a % 2) * y2**(b % 2)
    eqs = sp.Poly(sp.expand(red), x1, y1, x2, y2).coeffs()
    unk = list(n) + list(e)
    (sol,) = sp.linsolve(eqs, unk)
    free = set().union(*[sp.sympify(s).free_symbols for s in sol]) & set(unk)
    assert len(free) == 2, (tag, len(free))                       # dim of solution space
    for v in vecs:
        sub = dict(zip(unk, v))
        assert all(sp.expand(q.subs(sub)) == 0 for q in eqs)
KS = known(dd)
solve_ansatz(x1*y2 + y1*x2, 1 + dd*tt, (KS['xs'], KS['xd']), 'x')
solve_ansatz(y1*y2 + x1*x2, 1 - dd*tt, (KS['ys'], KS['yd']), 'y')

# ---- A3: nullity at the actual constant (evaluation can only over-estimate the space) ----
def nullity(rows, n):
    A = [r[:] for r in rows]; rk = 0
    for c in range(n):
        pr = next((i for i in range(rk, len(A)) if A[i][c] % p), None)
        if pr is None: continue
        A[rk], A[pr] = A[pr], A[rk]
        s = inv(A[rk][c]); A[rk] = [v * s % p for v in A[rk]]
        for i in range(len(A)):
            if i != rk and A[i][c] % p:
                f = A[i][c]; A[i] = [(u - f*w) % p for u, w in zip(A[i], A[rk])]
        rk += 1
    return n - rk
KN = known(d)
for coord, (a, b) in (('x', ('xs', 'xd')), ('y', ('ys', 'yd'))):
    rows = []
    for _ in range(40):
        P1, P2 = ext(rand_aff()), ext(rand_aff()); f = forms(P1, P2)
        m = [u*w % p for u in P1 for w in P2]
        Ns, Ds = (f['Nxs'], f['Dxs']) if coord == 'x' else (f['Nys'], f['Dys'])
        rows.append([mi*Ds % p for mi in m] + [(-mi*Ns) % p for mi in m])
    assert nullity(rows, 32) == 2, coord
    assert all(sum(u*w for u, w in zip(r, KN[k])) % p == 0 for r in rows for k in (a, b))

# ---- A4/A5: characters of tau_anti and of the swap ----
tau = lambda P: (I*P[1] % p, I*P[0] % p, P[2], (-P[3]) % p)
taui = lambda P: ((-I*P[1]) % p, (-I*P[0]) % p, P[2], (-P[3]) % p)
def hwcd4(P1, P2):
    X1, Y1, Z1, T1 = P1; X2, Y2, Z2, T2 = P2
    A = (Y1 - X1)*(Y2 + X2) % p; B = (Y1 + X1)*(Y2 - X2) % p
    C = 2*Z1*T2 % p; D = 2*T1*Z2 % p
    E, F, G, H = (D + C) % p, (B - A) % p, (B + A) % p, (D - C) % p
    return (E*F % p, G*H % p, F*G % p, E*H % p)
for _ in range(20):
    Pa, Qa = rand_aff(), rand_aff(); P1, P2 = ext(Pa), ext(Qa)
    assert aff(tau(P1)) == aadd(Pa, (I, 0))
    f, g, h = forms(P1, P2), forms(tau(P1), taui(P2)), forms(P2, P1)
    for kf in f:
        assert g[kf] == (f[kf] if kf.endswith('s') else (-f[kf]) % p)          # chi^0 vs chi^2
        assert h[kf] == ((-f[kf]) % p if kf in ('Nyd', 'Dyd') else f[kf])      # swap parity
    assert hwcd4(P2, P1) == tuple((-c) % p for c in hwcd4(P1, P2))             # sigma-odd vector
    assert aff(hwcd4(P1, P2)) == aadd(Pa, Qa)
ch = dict(U=1, V=3, Z=0, T=2)
cls = {k: [a + '1' + b + '2' for a in ch for b in ch if (ch[a] - ch[b]) % 4 == k] for k in range(4)}
assert all(len(v) == 4 for v in cls.values())
assert set(cls[0]) == {'U1U2', 'V1V2', 'Z1Z2', 'T1T2'} and set(cls[2]) == {'U1V2', 'V1U2', 'Z1T2', 'T1Z2'}

# ---- A6: mixed corners sd, ds have a rank-3 block over F_p ----
assert leg(-inv(d)) == p - 1          # lambda^2 = -1/d has no root

# ---- A7: every member of the family is a law; exceptional iff the stated condition ----
for _ in range(20):
    Pa, Qa, S = rand_aff(), rand_aff(), rand_aff()
    lx = (rng.randrange(1, p), rng.randrange(p)); ly = (rng.randrange(1, p), rng.randrange(p))
    xd, yd = aadd(Pa, aneg(Qa))
    R, Dx, Dy = law(ext(Pa), ext(Qa), lx, ly)
    assert (Dx == 0) == ((lx[0] + lx[1]*yd) % p == 0) and (Dy == 0) == ((ly[0] + ly[1]*xd) % p == 0)
    if Dx and Dy: assert aff(R) == aadd(Pa, Qa)
    Q2 = aadd(Pa, aneg(S))                                    # P1 - P2 = S
    assert law(ext(Pa), ext(Q2), ((-S[1]) % p, 1), (1, 0))[1] == 0
    assert law(ext(Pa), ext(Q2), (1, 0), ((-S[0]) % p, 1))[2] == 0

# ---- A8: dedicated law is exceptional exactly on P1 - P2 in E(F_p)[4] ----
E4 = [amul(j, (I, 0)) for j in range(4)]
assert sorted(E4) == sorted([(0, 1), (0, p - 1), (I, 0), (p - I, 0)])
for _ in range(10):
    Pa = rand_aff()
    for S in E4:
        assert hwcd4(ext(Pa), ext(aadd(Pa, aneg(S))))[2] == 0
    assert hwcd4(ext(Pa), ext(rand_aff()))[2] != 0

# ---- A9: co-Z sum/difference, 13M + 1c ----
def add_sub(P1, P2):
    X1, Y1, Z1, T1 = P1; X2, Y2, Z2, T2 = P2
    U1, V1, U2, V2 = (Y1 + X1) % p, (Y1 - X1) % p, (Y2 + X2) % p, (Y2 - X2) % p
    A, B, Ap, Bp = V1*V2 % p, U1*U2 % p, V1*U2 % p, U1*V2 % p        # 4M
    C = 2*d % p * (T1*T2 % p) % p; D = 2 * (Z1*Z2 % p) % p           # 2M + 1c
    E, H, Ep, Hp, F, G = (B - A) % p, (B + A) % p, (Bp - Ap) % p, (Bp + Ap) % p, (D - C) % p, (D + C) % p
    Zc = F*G % p                                                     # 1M, shared
    return (E*F % p, G*H % p, Zc, E*H % p), (Ep*G % p, F*Hp % p, Zc, Ep*Hp % p)   # 6M
for _ in range(20):
    Pa, Qa = rand_aff(), rand_aff()
    S, Df = add_sub(ext(Pa), ext(Qa))
    assert aff(S) == aadd(Pa, Qa) and aff(Df) == aadd(Pa, aneg(Qa)) and S[2] == Df[2]
Pa = rand_aff(); S, Df = add_sub(ext(Pa), ext(Pa)); assert aff(Df) == (0, 1)   # complete on diagonal

# ---- A10: small-order predicate U^4 = V^4 ----
def small_order(P):
    U2, V2 = (P[1] + P[0])**2 % p, (P[1] - P[0])**2 % p
    return U2 == V2 or (U2 + V2) % p == 0
while True:
    R8 = amul(L, rand_aff())
    if amul(4, R8) != (0, 1): break
assert all(small_order(ext(amul(j, R8))) for j in range(8))
for _ in range(20):
    Pa = rand_aff()
    assert small_order(ext(Pa)) == (amul(8, Pa) == (0, 1))
    assert not small_order(ext(aadd(amul(8, Pa), amul(rng.randrange(1, 8), R8)))) or amul(8, Pa) == (0, 1)
print("A1..A10 passed")
```

The solve is A2 (a `linsolve` over $\mathbb Q(d)$) together with A3. A3 gives nullity 2 at Curve25519's $d$, and evaluation can only over-estimate the space, so it certifies $W_x,W_y$ exactly at the real constant. The headline assertion is `len(free) == 2` and `nullity(rows, 32) == 2` for both coordinates. If A2 is slow with symbolic $d$, A3 alone carries the Curve25519 claim.

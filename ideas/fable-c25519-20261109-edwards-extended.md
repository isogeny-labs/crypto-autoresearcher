# Mythos ECDLP ideation — edwards-extended (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

Nothing below was executed: I have no tools, so every identity and count is a hand derivation, and the named scripts are proposals, not existing files. `src/ecc/curve25519.rs` is not quoted in the BRIEF, so the costs of `fe_inv` and `fe_sq` are assumptions wherever they matter. No lead beats the literature's operation counts; the deltas are against the repository as quoted, plus three small lemmas (leads 8, 10, 11).

**Notation.** $E:\ -x^2+y^2=1+dx^2y^2$ over $\mathbb F_p$, $p=2^{255}-19$, $a=-1=i^2$, $d=-121665/121666$ (non-square), $k=2d$, $B=1$, cofactor 8. Extended coordinates are $(X:Y:Z:T)$ with $x=X/Z$, $y=Y/Z$, $T=XY/Z$, $Z\neq0$. A multiplication by 2 is counted as 1a. The affine law is
$$x_3=\frac{x_1y_2+y_1x_2}{1+dx_1x_2y_1y_2},\qquad y_3=\frac{y_1y_2+x_1x_2}{1-dx_1x_2y_1y_2}.$$
Rational torsion: $\mathcal O=(0,1)$, $T_2=(0,-1)$, $T_4^{\pm}=(\pm i,0)$, so $E[4](\mathbb F_p)=\{xy=0\}$, plus four points of order 8.

**Repository baseline, counted from the BRIEF excerpt.**
- `EdPoint::add` costs 1I + 12 `fe_mul` + 9a per call. `ed25519_d()` is rebuilt each call (1 `fe_inv`, 1 `fe_mul`, 1 `fe_sub`), `c` takes three `fe_mul`, and `dd` takes two.
- `EdPoint::double` costs 4 `fe_sq` + 5 `fe_mul` (one is a multiplication by 2) + 7a.
- `scalar_mul` on an $n$-bit scalar of Hamming weight $h$ does $n$ doublings and $h$ additions, with a secret-dependent branch.

## LEADS

**1. Unified extended addition, $a=-1$** `[known]` (HWCD 2008; not filed in the BRIEF §2 index)
- Law: $A=(Y_1-X_1)(Y_2-X_2)$, $B=(Y_1+X_1)(Y_2+X_2)$, $C=k\,T_1T_2$, $D=2Z_1Z_2$, $E=B-A$, $F=D-C$, $G=D+C$, $H=B+A$; $X_3=EF$, $Y_3=GH$, $Z_3=FG$, $T_3=EH$.
- Check: $E=2(X_1Y_2+Y_1X_2)$, $H=2(Y_1Y_2+X_1X_2)$, $G=2(Z_1Z_2+dT_1T_2)$, $F=2(Z_1Z_2-dT_1T_2)$. So $X_3/Z_3=E/G=x_3$, $Y_3/Z_3=H/F=y_3$ and $X_3Y_3=Z_3T_3$.
- Count: HWCD state 8M + 1D (recalled). My hand count is 8M + 1c + 9a (8 add/sub and one doubling).
- Status: complete under the hypotheses of lead 7; branch-free.
- Symmetry: the $(Y\pm X)$ pairing is the factorisation $-x^2+y^2=(y-x)(y+x)$, available only for $a=-1$.
- Surface: the body of `EdPoint::add`.

**2. Hoist $k=2d$ and turn the ×2 multiplications into additions** `[adaptation]`
- Same law as lead 1, with $C=k\cdot(T_1T_2)$ and $D=Z_1Z_2+Z_1Z_2$. It returns the same four field elements as today.
- Count: 1I + 12 `fe_mul` + 9a becomes 8M + 1c + 9a. An inversion leaves the hot path.
- Surface: replaces `let d = ed25519_d();`, `let two = …;`, the `let c = fe_mul(&fe_mul(&self.t, &two), &fe_mul(&d, &other.t));` line and the `let dd = …` line.
- Check: Rust test `add_hoisted_matches_legacy` asserting coordinate-wise equality.

**3. Dedicated doubling, sign-normalised** `[known]`
- Law: $A=X_1^2$, $B=Y_1^2$, $C=2Z_1^2$, $H=A+B$, $E=(X_1+Y_1)^2-H$, $G=B-A$, $F=C-G$; $(X_3:Y_3:Z_3:T_3)=(EF:GH:FG:EH)$.
- Check: $x_3=E/G=2XY/(Y^2-X^2)$ and $y_3=H/F=(X^2+Y^2)/(2Z^2-Y^2+X^2)$.
- Count: 4M + 4S + 6a (HWCD: 4M + 4S, recalled). The repository spends 4S + 5 `fe_mul` + 7a.
- Symmetry: scaling by $\lambda=-1$ removes the repository's `h = 0 − (a+b)` negation. The output is the repository's output times $-1$.
- Torsion: $T_1$ is not read. $2\mathcal O=2T_2=\mathcal O$ and $2T_4^\pm=T_2$. The formula is invariant under $(X,Y)\mapsto(-X,-Y)$, which is translation by $T_2$.
- Surface: `EdPoint::double`, lines `c`, `e`, `h`, `f`.

**4. Completed coordinates on $\mathbb P^1\times\mathbb P^1$ with lazy $T$** `[adaptation]` (HWCD mixed coordinates and ref10's p1p1/p2/p3 structure, recalled)
- Model: $\bar P=((E:G),(H:F))$ with $x=E/G$, $y=H/F$.
- Completion: $\sigma_4=(EF:GH:FG:EH)$ costs 4M and is the Segre map, whose image is the quadric $XY=ZT$. $\sigma_3=(EF:GH:FG)$ costs 3M.
- Rule: use $\sigma_3$ when the next operation is a doubling, $\sigma_4$ when it is an addition.
- Count: doubling is 3M + 4S or 4M + 4S; readdition is 7M or 8M. A window of $w$ doublings and one readdition costs $w(3M+4S)+8M$, against $w(4M+4S)+8M+1c$ all-extended.
- Lower bound: $EF,GH,FG,EH$ are linearly independent bilinear forms, so 4M and 3M are optimal for completion by bilinear products.
- Surface: a new `EdCompleted` type, with `double`, `add` and `scalar_mul` rewritten on it.

**5. Mixed addition with an affine cache** `[known]`
- Cache: $\nu(P_2)=(\nu_1,\nu_2,\nu_3)=(y_2+x_2,\ y_2-x_2,\ k\,x_2y_2)$.
- Law: $A=(Y_1-X_1)\nu_2$, $B=(Y_1+X_1)\nu_1$, $C=T_1\nu_3$, $D=2Z_1$, then $E,F,G,H$ and outputs as in lead 1.
- Count: 7M + 7a to extended and 3M + 7a to completed. Without the cache it is 7M + 1c + 9a.
- Torsion: $\nu(\mathcal O)=(1,1,0)$ returns $P_1$; $\nu(T_2)=(-1,-1,0)$ returns $(-x_1,-y_1)$.
- Surface: `acc.add(self)` in `scalar_mul` when `self` came from `from_affine`. Today `Z_2=1` is multiplied in anyway.
- Caveat: normalising a table to affine by batch inversion costs 1I + 3(n−1)M + about 4M per entry to save 1M per readdition. For 64 readditions that does not pay unless I < 64M minus the setup.

**6. Readdition with a cached coordinate** `[adaptation]`
- Cache: $\kappa(P_2)=(Y_2^+,Y_2^-,Z_2',T_2')=(Y_2+X_2,\ Y_2-X_2,\ 2Z_2,\ kT_2)$, built once for 1c + 3a.
- Law: $A=(Y_1-X_1)Y_2^-$, $B=(Y_1+X_1)Y_2^+$, $C=T_1T_2'$, $D=Z_1Z_2'$, then $E,F,G,H$ and outputs as in lead 1.
- Count: 8M + 6a, 0c (4M + 6a to completed).
- Symmetry: $x\mapsto-x$ gives $\kappa(-P_2)=(Y_2^-,Y_2^+,Z_2',-T_2')$. Subtraction is a swap plus $F\leftrightarrow G$, so signed digits halve the table.
- Torsion: $\kappa(\mathcal O)=(1,1,2,0)$ and $\kappa(T_2)=(-1,-1,2,0)$.
- Surface: a new `EdCached` type used by `scalar_mul`.

**7. Completeness certificate for leads 1–6** `[adaptation]`
- Hypotheses: $p$ odd; $a=-1$ is a square (true since $p\equiv5\bmod 8$); $d$ is a non-square; both inputs are $\mathbb F_p$-points of $E$ with $Z\ne0$ and $XY=ZT$.
- Lemma: under these hypotheses $\varepsilon=dx_1x_2y_1y_2\notin\{\pm1\}$. The proof is in record 3.
- Consequence: $F=2Z_1Z_2(1-\varepsilon)\ne0$ and $G=2Z_1Z_2(1+\varepsilon)\ne0$. For doubling, $G=Z^2(1+dx^2y^2)$ and $F=Z^2(1-dx^2y^2)$.
- Torsion table for lead 1: adding $\mathcal O=(0:1:1:0)$ gives $4Z_2\cdot(X_2:Y_2:Z_2:T_2)$. Adding $T_2$ gives $(-x_2,-y_2)$. Adding $T_4^+$ gives $(iy_2,ix_2)$. $P+(-P)$ gives $E=0$ and $H/F=1$ by $Y^2-X^2=Z^2+dT^2$.
- Not covered: $\mathbb F_{p^2}$-points (where $d$ is a square), tuples with $XY\ne ZT$, and off-curve inputs.
- Surface: tests in `src/ecc/ed25519.rs` and a proposed `scripts/ed25519_formulas_check.sage`.

**8. $d$-free dual addition: exact exceptional set and a 2M coset test** `[adaptation]`
- Law (HWCD dedicated, recalled): $A'=(Y_1-X_1)(Y_2+X_2)$, $B'=(Y_1+X_1)(Y_2-X_2)$, $C'=2Z_1T_2$, $D'=2T_1Z_2$, $E'=D'+C'$, $F'=B'-A'$, $G'=B'+A'$, $H'=D'-C'$; output $(E'F':G'H':F'G':E'H')$.
- Count: 8M + 10a, 0c.
- Exceptional set: $F'=2(X_1Y_2-Y_1X_2)$ and $G'=2(Y_1Y_2-X_1X_2)$ are the numerators of $x(P_1-P_2)$ and $y(P_1-P_2)$ in the complete law. The formula therefore fails exactly when $P_1-P_2\in E[4](\mathbb F_p)$, and then returns $(0:0:0:0)$.
- Verdict: never complete, since the diagonal is exceptional. It is dominated by lead 6 for repeated addends, which already has 0c.
- Useful by-product: $P_1\equiv P_2 \pmod{E[4]}$ if and only if $F'G'=0$, a test costing 2M + 6a with no $Z$ and no inversion.

**9. Trading one M for one S in doubling** `[adaptation]`
- S-form (lead 3): $E=(X+Y)^2-H$, total 4M + 4S + 6a.
- M-form: $E=2(X\cdot Y)$, total 5M + 3S + 5a.
- Rule: the S-form wins if and only if $M-S>a$.
- When it wins: with dedicated limb squaring ($n(n+1)/2$ word products against $n^2$; 15 against 25 for five limbs). It ties or loses when `fe_sq` wraps `fe_mul`.
- Rejected second trade: $2Z_1Z_2=(Z_1+Z_2)^2-Z_1^2-Z_2^2$ needs $Z_1^2$, which no formula here produces, so it costs 2S + 3a against 1M + 1a.
- Surface: line `e` of `double`.

**10. Inversion-free torsion and identity tests from the doubling factors** `[adaptation]`
- Claim: $P\in E[8](\mathbb F_p)$ if and only if $T(2P)=EH=2XY(X^2+Y^2)=0$.
- Proof: $F,G\ne0$ by lead 7, so $EH=0$ if and only if $x(2P)y(2P)=0$, that is $2P\in E[4]$.
- Count: 2S + 1a and three zero tests, against three doublings for $[8]P$.
- Related tests: $P=\mathcal O$ if and only if $X=0$ and $Y=Z$ (0M). $P_1=P_2$ if and only if $X_1Z_2=X_2Z_1$ and $Y_1Z_2=Y_2Z_1$ (4M).
- Surface: `is_identity` (currently 1I + 2M through `to_affine`) and the small-order rejection in verification. That code is not quoted, so its current cost is unknown.

**11. Simultaneous $P+Q$ and $P-Q$** `[adaptation]`
- Law: with $A,B,C,D$ from lead 1 and $A',B'$ from lead 8, $P+Q$ has $(E,F,G,H)=(B-A,\ D-C,\ D+C,\ B+A)$ and $P-Q$ has $(B'-A',\ D+C,\ D-C,\ B'+A')$.
- Count: 14M + 1c + 11a for both, against 16M + 2c + 18a.
- Symmetry: $x\mapsto-x$ fixes $D$ and negates $C$.
- Surface: a Straus table $\{B\pm A\}$ in verification (public data).

**12. Signed radix-16 schedule on leads 4 and 6** `[adaptation]`
- Table: $\kappa(jP)$ for $j=1..8$, costing 40M + 16S + 8c.
- Main loop: 63 windows of $20M+16S$ each, about 1300M + 1024S in total, uniform in the scalar.
- Baseline: the repository's expected cost for $n=253$, $h\approx127$ is about 2789 `fe_mul` + 1012 `fe_sq` + 127I.
- Constant time: the digit lookup scans all 8 entries with masks, and the sign is applied by the swap of lead 6. `BigUint` arithmetic itself is not constant-time, so this fixes the schedule only.
- Surface: `scalar_mul`.

**13. Rotated accumulator $(U:V:Z:T)$, $U=Y+X$, $V=Y-X$** `[speculative]`
- Doubling front: $P=U^2$, $Q=V^2$, $R=UV$, $W=Z^2$, giving completed $((P-Q:2R),(P+Q:4W-2R))$ at 1M + 3S + 6a.
- Completion: $U_3=GH+EF$, $V_3=GH-EF$, $Z_3=FG$, $T_3=EH$.
- Readdition front: $A=V_1Y_2^-$, $B=U_1Y_2^+$, saving 2a that reappear in completion.
- Count: doubling is worse than lead 4 by $(M-S)+2a$. I predict it is dominated unless $S>M$, and file it so it is not re-derived.

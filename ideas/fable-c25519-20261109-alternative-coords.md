# Mythos ECDLP ideation — alternative-coords (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

Nothing here was executed: every count is a hand count from the formulas as written, and the named scripts are proposed files, not existing ones. I re-derived each law by hand from the affine Edwards, Montgomery or Weierstrass law, except where marked recalled. The recalled items are the Jacobi-quartic addition law (two spot checks only), the literature counts, and the theta-constant relation in L8.

Baseline read from the BRIEF, with $c_d$ a multiply by the generic 255-bit $d$ or $2d$ and $c_s$ a multiply by a 17-bit constant:

| Routine | Nominal | As written |
|---|---|---|
| `EdPoint::double` | $4M+4S$ | 5 `fe_mul` + 4 `fe_sq` + 7a (the ×2 is a `fe_mul`) |
| `EdPoint::add` | $8M+1c_d$ | 12 `fe_mul` + 1 `fe_inv` + 9a (`ed25519_d()` is recomputed per call) |
| `ladder` step | $5M+4S+1c_s+8a$ | 10 `fe_mul`; the swap is `if s == 1` |
| `scalar_mul` | $8M+4S+0.5c_d$ per bit | binary double-and-add, about 253 doublings + 126 additions |

Throughout: $a=-1$, $d=-121665/121666$ non-square, $-1$ square, $B=1$, $A=486662$, $a_{24}=121665$. $E(\mathbb F_p)\cong\mathbb Z/8\times\mathbb Z/\ell$, with $E[4](\mathbb F_p)=\{(0,1),(0,-1),(\pm i,0)\}$, $i^2=-1$. $T_2=(0,-1)$, $T_4=(i,0)$.

## LEADS

**1. [known] Projective Edwards $(X:Y:Z)$, no $T$.** $x=X/Z$, $y=Y/Z$.
- Doubling: $B=(X_1+Y_1)^2$, $C=X_1^2$, $D=Y_1^2$, $F=D-C$, $H=Z_1^2$, $J=F-2H$; $X_3=(B-C-D)J$, $Y_3=-F(C+D)$, $Z_3=FJ$. Cost $3M+4S+7a$.
- Addition: $A=Z_1Z_2$, $B=A^2$, $C=X_1X_2$, $D=Y_1Y_2$, $E=d\,CD$, $F=B-E$, $G=B+E$; $X_3=AF\big((X_1+Y_1)(X_2+Y_2)-C-D\big)$, $Y_3=AG(D+C)$, $Z_3=FG$. Cost $10M+1S+1c_d+7a$.
- Completeness: complete and strongly unified. $FG=A^4(1-d^2x_1^2x_2^2y_1^2y_2^2)\neq0$ because $d$ is non-square and $-1$ is square.
- Symmetry: scaling $\lambda(X,Y,Z)$; $x\mapsto-x$ is $X\mapsto-X$.
- Verdict: per binary bit $8M+4.5S+0.5c_d$, which is $0.5S$ slower than the baseline. Only the doubling half is useful (see lead 2).
- Constant time: branch-free. Surface: `EdPoint::double`.

**2. [adaptation] Factored $T$: $(X:Y:Z:T_a:T_b)$ with $T=T_aT_b$.**
- Doubling never reads $T$ and produces $T_3=e\cdot h$. Store $(e,h)$ unmultiplied: doubling drops to $3M+4S$.
- The addition pays $T_1=T_aT_b$ ($1M$) and emits $(E,H)$ unmultiplied, so it stays at $8M$ against a cached operand.
- Per bit: $7M+4S$, against the baseline $8M+4S+0.5c_d$.
- Completeness: unchanged, same rational functions. Symmetry: torus $(\lambda X,\lambda Y,\lambda Z,\mu T_a,\lambda\mu^{-1}T_b)$.
- Formulas are in Record 1. Surface: replaces `EdPoint`.

**3. [adaptation] Second-$Y$ basis $U=Y+X$, $V=Y-X$ (replacing $X$).**
- The unified law's bilinear part diagonalises: $A=V_1V_2$, $B=U_1U_2$.
- Negation is $(U,V,T)\mapsto(V,U,-T)$. $+T_2$ is $(U,V)\mapsto(-U,-V)$. $+T_4$ is $(U,V,T)\mapsto(iU,-iV,-T)$, so $E[4]$ acts diagonally.
- Negative on count: $0M$, $0S$ saved. It removes $4a$ per addition on the inputs and adds $2a$ on the outputs.
- It buys a branch-free signed table: conditional negation is one conditional swap plus one conditional sign.
- Combined with lead 2 in Record 1.

**4. [adaptation] Inverted Edwards $(X:Y:Z)$, $x=Z/X$, $y=Z/Y$.** Curve $(X^2-Y^2)Z^2=X^2Y^2+dZ^4$.
- Addition $9M+1S+1c_d$; doubling $3M+4S+1c_{2d}$ (formulas in Record 2).
- The doubling constant can be made small. Clearing $121666$: $D'=121666D$, $X_3=CD'$, $Z_3=D'E$, $Y_3=E(121666\,C+243330\,Z_1^2)$, which is $3c_s$.
- Not complete: $E[4](\mathbb F_p)$ is unrepresentable, and the output is degenerate iff the true sum lies in $E[4]$.
- On $\langle B\rangle\setminus\{O\}$: doubling never fails; addition fails iff $P_2=-P_1$.
- Per bit $7.5M+4.5S+1.5c$: dominated by lead 2 and by the baseline.

**5. [known] Dual ($d$-free) addition, exact exceptional locus on Curve25519.**
- Affine: $x_3=\dfrac{x_1y_1+x_2y_2}{y_1y_2-x_1x_2}$, $y_3=\dfrac{x_1y_1-x_2y_2}{x_1y_2-y_1x_2}$.
- Extended: $A=(Y_1-X_1)(Y_2+X_2)$, $B=(Y_1+X_1)(Y_2-X_2)$, $C=2Z_1T_2$, $D=2T_1Z_2$, $E=D+C$, $F=B-A$, $G=B+A$, $H=D-C$; $(X_3,Y_3,T_3,Z_3)=(EF,GH,EH,FG)$. Cost $8M$, no constant.
- Locus: over $\mathbb F_p$, $x_1y_2-y_1x_2=0$ iff $P_2\in\{P_1,P_1+T_2\}$, and $y_1y_2-x_1x_2=0$ iff $P_2=P_1\pm T_4$. A line through the origin meets the curve in four points whose $x^2$ values multiply to $1/(dt^2)$, a non-square, so the other two are irrational.
- So the law is valid iff $P_1-P_2\notin E[4](\mathbb F_p)$. On $\langle B\rangle$ it fails only on the diagonal.
- It saves $1c_d$ against an uncached unified addition and nothing against a cached one. It is not unified, so it is unsuitable for a constant-time accumulator.

**6. [adaptation] Edwards $(Y:Z)$ ladder is the XZ ladder conjugated by a Hadamard.**
- Map $(X_M:Z_M)=(Z+Y:Z-Y)$, a bijection of $\mathbb P^1$. RFC 7748's $A,B,C,D$ are $2Z_2,2Y_2,2Z_3,2Y_3$.
- Step cost $5M+4S+1c_s+8a$, identical to the baseline. Negative on count.
- It buys entry from an Ed25519 $y$ and exit to either $u$ or $y$ with no map inversion. Record 3.

**7. [adaptation] $w=y^2$ factors doubling into two degree-2 maps.**
- $y(2P)=g(y^2)$ with $g(w)=\dfrac{1-2w-dw^2}{dw^2-2dw-1}$, and $u(2P)=\dfrac{-(d+1)w}{(dw+1)(w-1)}$.
- With $w=BB/AA$ and $d=-a_{24}/(a_{24}+1)$ this is exactly $AA\cdot BB/\big(E(AA+a_{24}E)\big)$.
- $w$ is a Möbius image of the $x$-coordinate of $E/\langle T_2\rangle$: $w=\dfrac{x'-A-2}{x'-A+2}$, $x'=u+1/u+A$.
- The RFC split $2S\mid 2M+1c_s$ is already this factorisation, so no count change. Record 3.

**8. [speculative] Squared-theta Kummer line on $E/\langle T_2\rangle$.**
- $E/\langle T_2\rangle$ is $y^2=x(x-(A+2))(x-(A-2))$, with full rational 2-torsion and Legendre parameter $\lambda=(A-2)/(A+2)=-d$.
- Under the recalled relation $\mu=a^4/(a^4-b^4)$, the choice $\mu=1/\lambda$ gives $(b^2/a^2)^2=1/121666$. This is a square, since $A+2=4\cdot121666$ is a square.
- The choices $\mu=\lambda$ and $\mu=1-\lambda$ give $-1/121665$ and $-121665$, both non-squares.
- So rational theta constants may exist, but $b^2/a^2=\pm121666^{-1/2}$ is a generic 255-bit value. The small-constant advantage is lost, and I expect no win over $5M+4S+1c_s$.
- $1/\lambda$ also lands on the twist's Legendre curve, which is harmless for $x$-only arithmetic.
- Test: `scripts/kl_isogenous_25519.sage` computes the constants and counts.

**9. [known] Jacobian on $W: y^2=x^3+a_Wx+b_W$.** $x=u+A/3$, $y=v$, $a_W=1-A^2/3$, $b_W=(2A^3-9A)/27$ (map filed as IDEA-20260807-e6d79e).
- Doubling $1M+8S+1c$; mixed addition $7M+4S$; full addition $11M+5S$ (formulas in Record 4).
- Addition fails for $P_1=P_2$, $P_1=O$, $P_2=O$. Doubling is exception-free.
- Per bit $4.5M+10S+1c$ against $7M+4S$: slower, and incomplete. $a_W\neq-3$.

**10. [known] Chudnovsky $(X,Y,Z,Z^2,Z^3)$.**
- Addition: $U_1=X_1ZZ_2$, $U_2=X_2ZZ_1$, $S_1=Y_1ZZZ_2$, $S_2=Y_2ZZZ_1$, $H=U_2-U_1$, $I=(2H)^2$, $J=HI$, $r=2(S_2-S_1)$, $V=U_1I$, $X_3=r^2-J-2V$, $Y_3=r(V-X_3)-2S_1J$, $Z_3=((Z_1+Z_2)^2-ZZ_1-ZZ_2)H$, $ZZ_3=Z_3^2$, $ZZZ_3=Z_3ZZ_3$. Cost $10M+4S$.
- Doubling is Record 4's doubling with $ZZ$ cached plus $ZZ_3$, $ZZZ_3$: $2M+8S+1c$.
- It gains $1M+1S$ per addition and loses $1M$ per doubling. Net loss at one addition per two doublings. Same exceptions as lead 9. State is 5 elements.

**11. [known] Co-$Z$ Jacobian, a true two-$Y$ state $(X_1,Y_1,X_2,Y_2,Z)$.**
- ZADDU: $C=(X_1-X_2)^2$, $W_1=X_1C$, $W_2=X_2C$, $D=(Y_1-Y_2)^2$, $A_1=Y_1(W_1-W_2)$, $X_3=D-W_1-W_2$, $Y_3=(Y_1-Y_2)(W_1-X_3)-A_1$, $Z_3=Z(X_1-X_2)$. $P_1$ is updated to $(W_1,A_1,Z_3)$. Cost $5M+2S$.
- ZADDC adds $\bar D=(Y_1+Y_2)^2$, $\bar X_3=\bar D-W_1-W_2$, $\bar Y_3=(Y_1+Y_2)(W_1-\bar X_3)-A_1$. Cost $6M+3S$.
- Ladder step is ZADDC then ZADDU: $11M+5S$. The $(X,Y)$-only variant is recalled as $8M+6S$, unverified.
- Slower than $5M+4S+1c_s$, but it yields $y$. Fails iff $X_1=X_2$; in a ladder on order-$\ell$ input that is only $[2j+1]P=O$.

**12. [adaptation] Jacobi quartic model, complete because $A^2-4$ is non-square.**
- $J: Y^2=\varepsilon X^4-2\delta X^2+1$, $\varepsilon=(A^2-4)/16$, $\delta=A/4$. Map $X=2u/v$, $Y=(u^2-1)/(u^2+Au+1)$ (checked by hand).
- Exceptional loci of the map: $O\mapsto(0,1)$, $(0,0)\mapsto(0,-1)$.
- Recalled law: $X_3=\dfrac{X_1Y_2+Y_1X_2}{1-\varepsilon X_1^2X_2^2}$, $Y_3=\dfrac{(1+\varepsilon X_1^2X_2^2)(Y_1Y_2-2\delta X_1X_2)+2\varepsilon X_1X_2(X_1^2+X_2^2)}{(1-\varepsilon X_1^2X_2^2)^2}$.
- Complete on $J(\mathbb F_p)$: $\varepsilon$ non-square makes the denominator non-zero and the points at infinity irrational.
- Derived doubling, weights $x=X/Z$, $y=Y/Z^2$: $Z_3=Z^4-\varepsilon X^4$, $X_3=2XZ\cdot Y$, $Y_3=2Y^2(Z^4+\varepsilon X^4)-Z_3^2$. Cost $2M+7S+1c$.
- Derived addition: at most $10M+3S+3c$.
- A second complete model, but slower than lead 1's doubling. Test: `scripts/jq25519.sage`.

**13. [known] Non-existence over $\mathbb F_p$.**
- Twisted Hessian needs a rational point of order 3, but $3\nmid 8\ell$.
- Jacobi intersections and square-$d$ Edwards or squared-theta models need $E[2]\subset E(\mathbb F_p)$. $u^2+Au+1$ is irreducible, so $E[2](\mathbb F_p)=\mathbb Z/2$.
- $x=ix'$ gives the untwisted model $x'^2+y^2=1-d\,x'^2y^2$ with $-d$ still non-square.
- This closes those families for $\mathbb F_p$-isomorphic models. Isogenous models stay open (lead 8).

**14. [adaptation] Call-count measurement of the current code.**
- Instrument `fe_mul`, `fe_sq`, `fe_inv` and record per-operation calls. Prediction: 12 `fe_mul` + 1 `fe_inv` per `add`, 5 + 4 per `double`, 10 per ladder step.
- This separates formula-level gains (leads 2 and 3) from implementation gains: hoisting $2d$, and replacing ×2 by an addition.
- The ladder swap and `scalar.bit(t)` branch on secret bits, so the doc comment "constant-time by construction" does not hold for this code.
- Surface: `src/ecc/curve25519.rs` test-only counters.

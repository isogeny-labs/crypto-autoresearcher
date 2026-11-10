# Mythos ECDLP ideation — maps-isogeny (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

## LEADS

**Verification status.** Every identity below was derived and checked by hand in this session, including hand evaluations at the toy curve $p=13$, $A=7$. Nothing was machine-run. I do not quote the decimal values of $\gamma$, $v_B$ or the order-8 $u$-coordinates from memory; the proposed scripts compute them.

**Notation and constants.**
- Montgomery $M$: $v^2=u^3+Au^2+u$, projective $(U:V:W)$, $O=(0:1:0)$, $A=486662$.
- Edwards $E$: $-x^2+y^2=1+dx^2y^2$, extended $(X:Y:Z:T)$ with $XY=ZT$.
- $A+2=486664=4\cdot121666$, $A-2=486660=4\cdot121665$, $d=-\dfrac{A-2}{A+2}$, $1+d=\dfrac1{121666}$.
- $\gamma^2=-(A+2)=-486664$, $i^2=-1$, $s^2=121666$.
- Squareness, from the BRIEF's hypotheses: $-1$ is a square and $\gamma$ exists, so $A+2$ and $121666$ are squares. Since $d$ is a non-square, $121665$ and $A-2$ are non-squares, and $A^2-4=-d(A+2)^2$ is a non-square.
- Counts use the BRIEF's notation; "c" marks a constant multiply, and I say when the constant is full-size.

---

**1. [known] Montgomery ↔ short Weierstrass is projective-linear (filed as IDEA-20260807-e6d79e; cited, not re-filed).**
- Law: $x_w=u+A/3$, $y_w=v$, $a_w=1-A^2/3$, $b_w=A(2A^2-9)/27$.
- Projective: $(X_w:Y_w:Z_w)=(3U+AW:3V:3W)$, inverse $(U:V:W)=(3X_w-AZ_w:3Y_w:3Z_w)$.
- Count: $1c$ (small) $+\,\approx 5a$ each way.
- Exceptional locus: empty. $O\mapsto O$ and $(0,0)\mapsto(A/3,0)$.
- Completeness: the map preserves everything but carries none. The Weierstrass model has the rational 2-torsion point $(A/3,0)$, so the odd-order hypothesis of the Renes–Costello–Batina complete law fails (recalled, pointer only).
- Symmetry: translation of the $x$-line, commuting with $\pm1$.
- Surface: test helper only.

**2. [known] The affine birational map $\beta:E\to M$, with sign and exceptional loci (RFC 7748 baseline).**
- Law: $u=\dfrac{1+y}{1-y}$, $v=\dfrac{\gamma u}{x}$; inverse $x=\dfrac{\gamma u}{v}$, $y=\dfrac{u-1}{u+1}$.
- Sign convention: $x_Bv_B=9\gamma$, with $x_B$ the even root from the BRIEF. Flipping $\gamma$ flips $v_B$; X25519 never sees the sign. The script asserts which root matches RFC 7748's $V(P)$.
- Base point: $u=9\Rightarrow y=8/10=4/5$, and $y=4/5\Rightarrow u=(9/5)/(1/5)=9$.
- Exceptional loci of the affine formulas:
  - $y=1$: identity $(0,1)\mapsto O$.
  - $x=0,\ y=-1$: $(0,-1)\mapsto(0,0)$, a $0/0$ in $v$.
  - $v=0$: only $(0,0)$ is rational, because $A^2-4$ is a non-square.
  - $u=-1$: no rational point, because $v^2=A-2$ is a non-square.
- Result: with the two extensions, $\beta$ is a group isomorphism $E(\mathbb F_p)\cong M(\mathbb F_p)$. The affine formulas lose two points.
- Count: $1I+5M+1c$ per direction.
- Surface: `src/ecc/x25519.rs` and `src/ecc/ed25519.rs` have no conversion today.
- Doc bug: the comment `A24 = (486662 + 2) / 4 = 121665` is wrong. $121665=(A-2)/4$, which is what RFC 7748's $z_2=E(AA+a_{24}E)$ needs. The code is right; the comment is not.

**3. [adaptation] Complete quadratic lift $\Lambda: M\to$ extended Edwards (Record 1).**
- Law, with $Q=U^2+AUW+W^2$:
$$\Lambda(U:V:W)=(\gamma V(U+W)\ :\ V^2-Q\ :\ V^2+Q\ :\ \gamma V(U-W)).$$
- Count: $3M+2S+2c+5a$ projective; $3M+1S+1c+6a$ affine. The constants are $486660$ (small) and $\gamma$ (full-size).
- Completeness: $\Lambda(O)=(0:1:1:0)$ and $\Lambda(0:0:1)=(0:-1:1:0)$. The common zeros are $V=Q=0$, the non-rational 2-torsion pair, so no rational point is lost.
- Comparison: the denominator-cleared chart $(\gamma U(U+W):V(U-W):V(U+W):\gamma U(U-W))$ costs $4M+1c$ and vanishes identically at $O$ and at $(0,0)$.
- Symmetry: $v\mapsto-v$ acts as $(X,T)\mapsto(-X,-T)$; translation by $(0,0)$ acts as $(X,Y)\mapsto(-X,-Y)$.
- Surface: new `EdPoint::from_montgomery` in `src/ecc/ed25519.rs`.

**4. [adaptation] Exit charts $E\to M$: a unique linear chart with one exceptional point, and a parity obstruction (Record 2).**
- Linear chart: $E_1(X:Y:Z:T)=(X+T:\gamma(Z+Y):X-T)$, $1c+3a$. Identity $\mapsto(0:2\gamma:0)=O$. All three forms vanish only at $(0:-1:1:0)$.
- Quadratic chart: $E_2=(-(X^2+dT^2):-\gamma(XZ+dTY):(Z-Y)^2)$, $2M+3S+3c$. It sends $(0:-1:1:0)\mapsto(0:0:1)$ and vanishes only at the identity.
- Obstruction: a degree-$n$ chart has a base divisor of degree $4n-3$, which is odd. A complete single chart must therefore vanish on a Galois orbit of odd size $\ge3$. No chart built on rational points and points at infinity is complete.
- $x$-only exit: $(U:W)=(Z+Y:Z-Y)$ is complete, $2a$.
- Symmetry: the hyperplane class of the extended model is $3(O)+((0,-1))$.
- Surface: `EdPoint::to_montgomery`, and `x25519_base` via Edwards.

**5. [adaptation] The transported unified law and where it lands.**
- Law (HWCD unified, $a=-1$):
  - $A_1=(Y_1-X_1)(Y_2-X_2)$, $B_1=(Y_1+X_1)(Y_2+X_2)$, $C_1=2dT_1T_2$, $D_1=2Z_1Z_2$.
  - $E=B_1-A_1$, $F=D_1-C_1$, $G=D_1+C_1$, $H=B_1+A_1$.
  - $(X_3:Y_3:Z_3:T_3)=(EF:GH:FG:EH)$.
  - Count: $8M+1c+9a$; complete because $1\pm dx_1x_2y_1y_2\ne0$.
- Where it lands: pulled back along $\Lambda$, it is a complete addition of full Montgomery points. The result is in extended Edwards coordinates, which are the Segre coordinates of $(\gamma U:V)\times(U-W:U+W)$. No Montgomery-native complete system appears.
- Count: $14M+4S+5c$ for two projective inputs, $14M+2S+3c$ for two affine inputs, plus $1c$ to exit by $E_1$.
- Weierstrass: prepend lead 1 for a few more small-constant multiplies.
- Verdict: this is not cheaper than staying in Edwards. It only gives Montgomery and Weierstrass inputs a complete law they otherwise lack.
- Surface: tests against `EdPoint::add`.

**6. [known] The Hadamard map on the $x$-line and Edwards $y$-only differential addition (Record 3).**
- Map: $h(U:W)=(Z:Y)=(U+W:U-W)$, i.e. $y=(u-1)/(u+1)$. It is a bijection of $\mathbb P^1(\mathbb F_p)$, covering curve and twist. Twist $u=-1\mapsto y=\infty$.
- Observation: the ladder's `a = x2+z2`, `b = x2−z2`, `c`, `d` are $2Z_2,2Y_2,2Z_3,2Y_3$ in Edwards coordinates.
- Law: with difference $(Z_1:Y_1)$, $m_1=Y_3Z_2$, $m_2=Z_3Y_2$:
$$Z_5=(Z_1-Y_1)(m_1+m_2)^2+(Z_1+Y_1)(m_1-m_2)^2,\quad Y_5=(Z_1-Y_1)(m_1+m_2)^2-(Z_1+Y_1)(m_1-m_2)^2.$$
- Affine form: $y_5=\dfrac{2y_2y_3-y_1(y_2^2+y_3^2)}{y_2^2+y_3^2-2y_1y_2y_3}$, with no curve constant.
- Count: $4M+2S+6a$, or $3M+2S$ with a normalised difference. This is identical to Montgomery, so there is no saving.
- What it buys: the ladder output gives Edwards $y=(X_2-Z_2)/(X_2+Z_2)$ at the same $1I+1M$ as $u$.
- What it does not buy: entering from Edwards $y$ with a projective difference costs $+1M$ per step, $255M$ in total. That is about one inversion ($\approx254S+11M$), so it is a wash.
- Surface: `ladder` in `src/ecc/x25519.rs`.

**7. [adaptation] No coordinate change turns differential addition into an addition (Record 3).**
- Proof: for any map $g$ on the $x$-line and any $F$, $F(g(x(P)),g(x(Q)))$ takes the same value at $(P,Q)$ and $(P,-Q)$. But $x(P+Q)=x(P-Q)$ only if $2P=O$ or $2Q=O$.
- On Curve25519: the rational 2-torsion is $\{O,(0,0)\}$, so every other pair is a counterexample.
- Consequence: the third argument $x(P-Q)$, or one sign bit per point, is forced. The Edwards law consumes exactly that sign information.
- Symmetry: the involution $(P,Q)\mapsto(P,-Q)$.

**8. [adaptation] Uniform-sequence Edwards scalar multiplication: ladder, $y$-recovery, then $\Lambda$.**
- Inputs: affine $P=(u_P,v_P)$ and ladder outputs $(X_2:Z_2)=x([k]P)$, $(X_3:Z_3)=x([k+1]P)$.
- Recovery law:
$$N=\big[(u_PX_2+Z_2)(u_PZ_2+X_2+2AZ_2)-2AZ_2^2\big]Z_3-(u_PZ_2-X_2)^2X_3,\qquad D=2v_PZ_2Z_3,$$
$$(U:V:W)=(X_2D:N:Z_2D).$$
- Derivation: from $2v_Pv_Q=(u_Pu_Q+1)(u_P+u_Q+2A)-2A-(u_P-u_Q)^2u_{P+Q}$, which I re-derived from the chord formula.
- Count: recovery $9M+2S+2c$, then $\Lambda$ at $3M+2S+2c$. Total: $255\times(5M+4S+1c)+12M+4S+4c+1I$ for entry.
- Exceptional set: $v_P=0$, $[k]P=O$, or $[k+1]P=O$ (the output is $(0:0:0)$).
  - For $P=B$ and clamped $k$: no clamped scalar is a multiple of $\ell$. Exactly one has $k+1\equiv0 \pmod \ell$, namely $k=5\ell-1$, because $\ell\equiv5\pmod 8$.
  - For nonces $r\in[0,\ell)$: $r=0$ and $r=\ell-1$.
  - These need a masked select; the law is not complete without it.
- Replaces: `EdPoint::scalar_mul`, which is variable-time and pays about 126 inversions per call (lead 13).
- Constant-time: the operation sequence is uniform. The BigUint arithmetic and the branchy swap in `ladder` are not.

**9. [adaptation] The 4-isogenous small-$d$ curve and clamp absorption (Record 4).**
- Curve: $\bar E:-x^2+y^2=1+121665x^2y^2$, complete, with $\bar d=a_{24}$.
- Isogeny: $\psi(x,y)=\left(-\dfrac{y^2}{x^2},\ \dfrac{i\,y(2+x^2-y^2)}{x^3}\right)$ lands on Curve25519.
- $x$-only forms: $(U:W)=(-Y^2:X^2)$ at $2S$; dual $(Y':Z')=((U-W)^4-4(A+2)U^2W^2:Q^2-(A^2-4)U^2W^2)$ at $1M+4S+3c$. Both are total on $\mathbb P^1(\mathbb F_p)$.
- What is lost: $\psi$ is 2-to-1 on rational points with kernel $\{(0,1),(0,-1)\}$, and its image is the index-2 subgroup. It is not a model of the full group.
- Clamp absorption: $[k]P=\psi([k/4]\hat\psi(P))$ for $4\mid k$.
- Count: an uncached unified add is $8M+1c$ with $c=243330$, against $9$ general multiplies on Edwards25519. With cached $2dT$ tables the gain is zero.

**10. [known] Fixed-base `x25519_base` through Edwards with the complete $x$-exit.**
- Current cost: $255\times(5M+4S+1c)+1I$, written as 10 `fe_mul` per step.
- Replacement: radix-16 with 64 mixed additions into a precomputed table of cached affine points $(y+x,\ y-x,\ 2dxy)$, at $7M$ each, about $448M$. Then $u=(Z+Y)/(Z-Y)$ at $1I+1M$.
- Completeness: $Z-Y=0$ only at the identity, which a clamped scalar never reaches on $\langle B\rangle$ (lead 8).
- Constant-time: requires a uniform masked scan of each 16-entry row.
- Status: standard technique in production libraries (recalled). Listed as a baseline for `ecbench`, not as novelty.

**11. [known] Torsion and base-point correspondence, to be used as the oracle for every transport.**

| order | Edwards | Montgomery |
|---|---|---|
| 1 | $(0,1)$ | $O$ |
| 2 | $(0,-1)$ | $(0,0)$ |
| 4 | $(\epsilon i,0)$, $\epsilon=\pm1$ | $(1,-\epsilon i\gamma)$, with $(i\gamma)^2=A+2$ |
| 8 | $y_8^2=\dfrac{s}{s+1}$, $x_8=\pm i\,y_8$ | $u_8+1/u_8=2+4s$, i.e. $u_8=1+2s\pm2\sqrt{s^2+s}$ |
| $\ell$ | $(x_B,4/5)$ | $(9,\,9\gamma/x_B)$ |

- Order 8: $s=\pm\sqrt{121666}$ is taken with the sign making $s/(s+1)$ a square. The two rational $u$-values are $u_8$ and $1/u_8$, corresponding to $y_8$ and $-y_8$.
- Twist: $u=0$ (order 2) and $u=-1\leftrightarrow y=\infty$ (order 4; twist cofactor 4 is recalled).
- Surface: tests beside the RFC 7748 vectors.

**12. [speculative] The 2-isogenous curve with full rational 2-torsion and small roots.**
- Law: $\chi(u,v)=\left(\dfrac{u^2+Au+1}{u},\ \dfrac{v(1-u^2)}{u^2}\right)$ maps $M$ to $E_2:y^2=x(x-486660)(x-486664)$.
- Legendre parameter: $\mu=\dfrac{A-2}{A+2}=-d$.
- Exceptional locus: $u=0$. The kernel is $\{O,(0,0)\}$, so the map is 2-to-1 and the group becomes $\mathbb Z/2\times\mathbb Z/4\ell$. A point is lost.
- Kummer line: a squared-theta Kummer line (Karati–Sarkar, recalled) needs $(b^2/a^2)^2\in\{1-1/\mu'\}$ over the $\lambda$-orbit of $\mu$. The only square values are $1/121666$ and $121666$, so $b^2/a^2=\pm s^{\pm1}$ is rational but full-size.
- Predicted outcome: no gain over $5M+4S+1c$, because the theta constants are not small. Filed as a lead so the negative is measured rather than assumed.

**13. [known] Repository hot-path defects that any transport must not inherit.**
- `EdPoint::add` calls `ed25519_d()`, which performs one `fe_inv` and one `fe_mul` on every addition. Together with the 11 `fe_mul` in `add`, that is $12$ multiplies $+1I$ where $8M+1c$ suffices.
- `double` multiplies by the constant 2 with `fe_mul`.
- `ladder` squares with `fe_mul` and swaps with `if s == 1`, a secret-dependent branch, despite the module doc saying "constant-time by construction".
- Fix: a cached constant, additions for doublings, and a masked swap. This removes an inversion from the hot path without any change of model.

---

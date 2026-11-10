# Mythos ECDLP ideation — montgomery-xz (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

Nothing below has been executed: I have no tools, so every count and identity is derived by hand from the BRIEF excerpts, and the script and test names are proposed, not existing. Notation: `M`, `S`, `c`, `a`, `I` as in the BRIEF, plus `s` for a multiplication by a 0/1 value (a mask). Curve: $v^2=u^3+Au^2+u$, $A=486662$, $B=1$, $a_{24}=(A-2)/4=121665$, $T=(0,0)$, $O=(1:0)$.

## LEADS

**1. Baseline XZ step as implemented in `ladder()` — [known] (RFC 7748)**
- **Model:** $(X_2:Z_2)=jP$, $(X_3:Z_3)=(j+1)P$, affine $x_1$.
- **Law:** $A=X_2+Z_2$, $B=X_2-Z_2$, $C=X_3+Z_3$, $D=X_3-Z_3$, $AA=A^2$, $BB=B^2$, $E=AA-BB$, $DA=D\cdot A$, $CB=C\cdot B$, then
  $$X_3'=(DA+CB)^2,\quad Z_3'=x_1(DA-CB)^2,\quad X_2'=AA\cdot BB,\quad Z_2'=E\,(AA+a_{24}E).$$
- **Count:** 5M+4S+1c+8a per bit, coded as 10 `fe_mul` calls. Total for 255 bits: 1275M+1020S+255c+2040a, plus I+1M.
- **Completeness:** doubling is correct on all of $\mathbb P^1$, including $O$ and $T$ (both give $(1:0)$). Differential addition needs $x_1\notin\{0,\infty\}$; for $u=0$ the state degenerates to $(0:0)$ and the output is 0, as RFC 7748 expects.
- **Repo defects visible in the excerpt:**
  - The comment says `A24 = (486662 + 2)/4 = 121665`. That is arithmetically false: $(A+2)/4=121666$. The code is correct because it uses $AA+a_{24}E$ with $(A-2)/4$.
  - `if s == 1 { swap }` is a secret-dependent branch and `BigUint` is variable-time, so the module doc's "constant-time by construction" does not hold for this implementation.
  - The four squarings use `fe_mul`, although `fe_sq` exists.
  - Separately, `EdPoint::add` calls `ed25519_d()`, which runs `fe_inv(121666)` on every addition.
- **Unchecked:** the all-zero result relies on `fe_inv(0)=0`, which I cannot see.

**2. Arithmetic conditional swap — [known]**
- **Law:** with $s=k_t\oplus k_{t+1}$,
  $$\delta_X=s\,(X_2-X_3),\ X_2\leftarrow X_2-\delta_X,\ X_3\leftarrow X_3+\delta_X;\qquad \delta_Z=s\,(Z_2-Z_3),\ Z_2\leftarrow Z_2-\delta_Z,\ Z_3\leftarrow Z_3+\delta_Z.$$
- **Count:** 2s+6a per bit, four field elements written.
- **Constant-time:** branch-free, each bit read once. In `BigUint` a multiply by 0 is still data-dependent, so this removes the branch, not the leak.
- **Surface:** replaces the `if s == 1` block in `ladder()`.

**3. Select ladder: two one-way selects instead of two swaps — [adaptation]**
- **Model:** slot 0 $(U_0:W_0)$ holds the last doubling output, slot 1 $(U_1:W_1)$ the last addition output. Init $(1:0)$, $(x_1:1)$, $k_{255}:=0$, $\sigma_t=k_t\oplus k_{t+1}$.
- **Law:** $A_i=U_i+W_i$, $B_i=U_i-W_i$, $m_1=B_1A_0$, $m_2=A_1B_0$,
  $$U_1'=(m_1+m_2)^2,\quad W_1'=x_1(m_1-m_2)^2,$$
  $$A=A_0+\sigma_t(A_1-A_0),\quad B=B_0+\sigma_t(B_1-B_0),$$
  $$AA=A^2,\ BB=B^2,\ E=AA-BB,\quad U_0'=AA\cdot BB,\quad W_0'=E(AA+a_{24}E).$$
  Output is slot $k_0$, which is slot 0 for every clamped scalar.
- **Count:** 5M+4S+1c+8a plus 2s+4a, two elements written. Against lead 2 this saves 2a and two masked writes per bit (510a total). M and S are unchanged.
- **Symmetry:** differential addition is symmetric in its two points. Exchanging $(A_0,B_0)\leftrightarrow(A_1,B_1)$ swaps $m_1,m_2$, fixing the sum and negating the squared difference, so only the doubling needs the bit.
- **Completeness:** same as lead 1.
- **Check:** Rust test `ladder_select_matches_reference`. Record 1.

**4. Clamp-aware schedule — [adaptation]**
- **Idea:** bits 254 (=1) and 0–2 (=0) are public inside `x25519()`.
- **Law:**
  - Init: slot 1 $=(u:1)$; slot 0 $=\mathrm{dbl}(u:1)$ with $A=u+1$, $B=u-1$; previous bit 1.
  - Run lead 3 for $t=253,\dots,3$ (251 steps).
  - Select slot $k_3$ and apply three doublings $X'=AA\cdot BB$, $Z'=E(AA+a_{24}E)$.
- **Count:** 1263M+1012S+255c+2024a. This saves exactly 12M+8S+16a and three select stages (0.87% of M+S).
- **Completeness:** for $u\ne0$ both schedules compute $x([k]P)$ exactly on curve and twist. For $u=0$ both give 0 (states are $O$, $T$ or $(0:0)$).
- **Limits:** invalid for unclamped scalars. It discards $x((k+1)P)$, so y-recovery (lead 7) must happen before the tail.

**5. Shared denominator $(X_2:X_3:Z)$ — [adaptation], dominated and less complete**
- **Law:** $A=X_2+Z$, $B=X_2-Z$, $C=X_3+Z$, $D=X_3-Z$, $DA$, $CB$, $S=(DA+CB)^2$, $N=(DA-CB)^2$, $AA$, $BB$, $E$, $T_d=AA+a_{24}E$, then
  $$W_a=x_1N,\quad W_d=E\,T_d,\quad X_d=AA\cdot BB,\qquad X_2'=X_dW_a,\quad X_3'=S\,W_d,\quad Z'=W_dW_a.$$
- **Count:** 8M+4S+1c+8a. I found no factorisation below 8M; the co-Z identities $DA-CB=2Z(X_3-X_2)$ and $E=4X_2Z$ gave 9M+5S.
- **What it buys:** a 3-element state, and only the $X$ registers need swapping.
- **Exceptions:**
  - $(O,P)$ is not representable, so start from $(P,2P)$.
  - Whenever either point is $O$, $Z'=0$ and both points are lost.
  - For prime-order $P$ this gives wrong output 0 at clamped $k=5\ell-1$ (where $(k+1)P=O$) and $k=4(\ell-1)$ (prefix $\ell-1$). The XZ ladder handles both.
- **Total:** 2035M+1018S+255c, i.e. +760M over the baseline.

**6. Co-Z Jacobian $(X:Y:Z)$ carrying $y$ — [known], dominated**
- **Model:** shifted model $\tilde x=u+A/3$ (the map is ledger IDEA-20260807-e6d79e, not re-filed), $x=X/Z^2$, $y=Y/Z^3$, common $Z$.
- **ZADDU:** $C=(X_1-X_2)^2$, $W_1=X_1C$, $W_2=X_2C$, $D=(Y_1-Y_2)^2$, $A_1=Y_1(W_1-W_2)$,
  $$X_3=D-W_1-W_2,\quad Y_3=(Y_1-Y_2)(W_1-X_3)-A_1,\quad Z_3=Z(X_1-X_2),$$
  with $P_1$ re-expressed as $(W_1:A_1:Z_3)$. Cost 5M+2S+7a.
- **ZADDC:** adds $\bar D=(Y_1+Y_2)^2$, $\bar X_3=\bar D-W_1-W_2$, $\bar Y_3=(Y_1+Y_2)(W_1-\bar X_3)-A_1$. Cost 6M+3S+11a.
- **Ladder step:** $(R_{1-b},R_b)\leftarrow\mathrm{ZADDC}(R_b,R_{1-b})$, then $(R_b,R_{1-b})\leftarrow\mathrm{ZADDU}(R_{1-b},R_b)$.
- **Init:** $M=3u_1^2+2Au_1+1$, $S=4\tilde x_1y_1^2$, $X=M^2-2S$, $Y=M(S-X)-8y_1^4$, $Z=2y_1$.
- **Count:** 11M+5S+18a per bit, or 9M+5S if $Z$ is dropped and recovered at the end.
- **Exceptions:** fails when $X_1=X_2$ or a point is $O$. That covers every low-order input, and $j\equiv0,-1,(\ell-1)/2 \pmod\ell$ on prefixes. It also needs $v$ (a square root) and cannot process twist inputs.
- **Verdict:** 2794M+1270S; not competitive on this curve.

**7. Okeya–Sakurai y-recovery from the final pair — [known] formula, exception set derived here**
- **Inputs:** $P=(x_P,y_P)$, $Q=(X_Q:Z_Q)=kP$, $(X_\oplus:Z_\oplus)=(k+1)P$.
- **Law:** $v_1=x_PZ_Q$, $v_2=X_Q+v_1$, $v_3=(X_Q-v_1)^2X_\oplus$, $v_4=2AZ_Q$, $v_5=x_PX_Q+Z_Q$,
  $$Y'=\big((v_2+v_4)v_5-v_4Z_Q\big)Z_\oplus-v_3,\quad w=2y_PZ_QZ_\oplus,\quad X'=wX_Q,\quad Z'=wZ_Q.$$
- **Count:** 10M+1S+1c+7a. No inversion beyond the one the x-only output already needs.
- **Derivation:** from $2y_Py_Q=(x_Px_Q+1)(x_P+x_Q+2A)-2A-(x_P-x_Q)^2x_\oplus$.
- **Exceptions:** output $(0:0:0)$ exactly when $y_P=0$, $Q=O$, or $Q=-P$.
- **Clamped case:** for clamped $k$ and $P$ of order $\ell$, $Q=O$ is impossible ($8\ell>2^{255}$). $Q=-P$ happens for exactly one scalar, $k^\ast=5\ell-1$ (since $\ell\equiv5 \bmod 8$).

**8. Recovery fused into extended Edwards, no inversion — [adaptation]**
- **Law:** with $c^2=-486664$, skip $Z'$ and output
  $$X_E=cX'(X_Q+Z_Q),\quad Y_E=Y'(X_Q-Z_Q),\quad Z_E=Y'(X_Q+Z_Q),\quad T_E=cX'(X_Q-Z_Q).$$
- **Count:** 13M+1S+2c+9a fused ($c$ is full-size).
- **Exceptions:** $Z_E=0$ exactly when lead 7 fails or $Q=T$.
- **Surface:** a uniform alternative to `EdPoint::scalar_mul`. The current path costs about 2168M+1020S per 255 bits and branches on scalar bits; the ladder path costs I+1295M+1021S+258c. Record 3.

**9. The $x\mapsto1/x$ symmetry — [adaptation] as a control**
- **Where it acts:** translation by $T$ is $(X:Z)\mapsto(Z:X)$. In Hadamard coordinates it is $(A,B)\mapsto(A,-B)$.
- **Step level:** applying it to both points fixes $A,C$ and negates $B,D$, hence negates $DA,CB$. All four step outputs are identical field elements.
- **What it saves in the formula:** the two forms the addition needs, $X_2X_3-Z_2Z_3$ and $X_3Z_2-X_2Z_3$, span the $(-1)$-eigenspace, whose Hadamard basis is the two rank-one products $D\!\cdot\!A$, $C\!\cdot\!B$. That is 2M instead of 4M, and the doubling depends only on $(AA,BB)$. RFC 7748 already uses all of this, so there is no further M/S saving.
- **What is new:**
  - A vector-free oracle: $X25519(k,u)=X25519(k,u^{-1})$ for $u\ne0$ and clamped (even) $k$.
  - Along the two runs, exactly one slot is reciprocal at each prefix (the odd multiple).
- **Blind spot:** a wrong $a_{24}$ still passes, because any Montgomery curve has $T$.
- Record 4.

**10. Hadamard (Edwards-$y$) state with projective base — [known]**
- **Model:** state $(S_i:D_i)=(X_i+Z_i:X_i-Z_i)$, which is $(Z_E:Y_E)$. Base $(X_1:Z_1)=(Z_E+Y_E:Z_E-Y_E)$.
- **Law:** $m_1=D_3S_2$, $m_2=S_3D_2$, $p=Z_1(m_1+m_2)^2$, $q=X_1(m_1-m_2)^2$, $S_3'=p+q$, $D_3'=p-q$; $AA=S_2^2$, $BB=D_2^2$, $E=AA-BB$, $r=AA\cdot BB$, $t=E(AA+a_{24}E)$, $S_2'=r+t$, $D_2'=r-t$.
- **Count:** 6M+4S+1c+8a. Removes the entry inversion at +255M. It wins only if $255M<254S+11M$, i.e. $S/M>0.96$, so no gain is claimed.
- **Exceptions:** as lead 1, with $O=(1:1)$ and $T=(1:-1)$.

**11. Fixed-base right-to-left ladder for `x25519_base` — [known] (recalled: Oliveira–López–Hışıl–Faz-Hernández–Rodríguez-Henríquez 2017; re-derived here)**
- **Setup:** $k'=k/8$, $S$ of order 4 with $x(S)=1$, $P_i=2^iP$, public table $\mu_i=(x(P_i)+1)/(x(P_i)-1)$.
- **Law:** $R\leftarrow\mathrm{xADD}(R_{sel},P_i;\ \text{diff}=R_{oth})$ per bit:
  $$X'=Z_{oth}\big(\mu_i(X-Z)+(X+Z)\big)^2,\quad Z'=X_{oth}\big(\mu_i(X-Z)-(X+Z)\big)^2.$$
  Then three doublings.
- **Count:** 3M+2S+4a per bit. Total 762M+510S+3c+1020a, against 1020M+1020S+510c today (for $u=9$ the multiply by $x_1$ is a small constant).
- **Completeness:** exception-free for every clamped scalar by a coset argument. Record 2.

**12. Kummer-line transfer through $E\to E/\langle T\rangle$ — [speculative]**
- **Facts derived here:** $A^2-4$ is a non-square, so $E[2](\mathbb F_p)=\{O,T\}$ and $E$ has no Legendre model. The quotient $E'$ is $Y^2=X(X-(A-2))(X-(A+2))$. Scaling by the square $A+2$ gives $y^2=x(x-1)(x-\mu)$ with $\mu=(A-2)/(A+2)=-d$.
- **Use:** for even $k$, $[k]P=\hat\varphi([k/2]\varphi(P))$, with $\varphi:(X:Z)\mapsto(AA:BB)$ costing 2S+2a.
- **Status:** assuming the recalled relation $\mu^\ast=a^4/(a^4-b^4)$, the only square candidate is $b^2/a^2=\pm2/\sqrt{A+2}$, a full-size constant. Each constant multiply then costs M, so no count below 5M+4S+1c is shown and no speedup is claimed.
- **Check:** Sage script asserting the Legendre symbols and $\mu=-d$.

**Totals on one clamped 255-bit scalar (final I+1M excluded)**

| Form | Per bit | Total |
|---|---|---|
| Repo `ladder()` | 5M+4S+1c+8a, branch | 1275M+1020S+255c+2040a |
| Lead 2 swap | +2s+6a | same M/S |
| Lead 3 select | +2s+4a | same M/S, 510a fewer than lead 2 |
| Lead 4 | — | 1263M+1012S+255c+2024a |
| Lead 5 | 8M+4S+1c+8a | 2035M+1018S+255c+2036a |
| Lead 6 | 11M+5S+18a | 2794M+1270S, plus a square root |
| Lead 10 | 6M+4S+1c+8a | 1530M+1020S+255c, minus one I |
| Lead 11 (base only) | 3M+2S+4a | 762M+510S+3c+1020a |

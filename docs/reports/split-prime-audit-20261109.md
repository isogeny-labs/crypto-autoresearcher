# Independent audit — split-prime ECDLP study (2026-11-09)

Audit of `research/split_prime_ecdlp_20261107` against the study text, its
follow-ups, the CryptoLean declarations, and the internal red team (F1–F10).
Generated with `claude-mythos-5-1` from a brief containing those documents.
`claude-fable-5-2` was also asked and refused the task (`category=cyber`); no
finding here comes from that model.

Verdict: the §3 obstruction holds with repairs. The repairs below do not change
the conclusion that the split-prime pattern reaches `E(F_p)` only through scalars
or DLP-preserving isomorphisms; they correct the `l = n` remark, the
"fiber polynomials" wording, the canonical-lift computability claim, and the §4
baseline derivation text.

## VERDICT

**Holds with listed repairs.** Items (1) and (2) of the §3 theorem are correct as theorems (and the Lean declarations `hom_card_prime_bijective`, `endo_cyclic_eq_zsmul` are faithful abstractions of their group-theoretic cores). Item (3) is correct for Galois/pairing data but false as literally written for "fiber polynomials" (D2). The setting paragraph misidentifies the second rational $n$-isogeny (D1) and mislabels an automatic identity as a checked hypothesis (D5). The corollary is a generic-model statement, as F1/F8 already say. Nothing I found changes the conclusion that the split-prime pattern reaches $E(\mathbb{F}_p)$ only through scalars or DLP-preserving isomorphisms.

## DEFECTS

**D1 — minor — §3 Setting, sentence "The exclusion ℓ ≠ n is a convenience, not a gap".**
Claim: the two rational $n$-isogenies are $\pi-1$ and $\pi-p$, acting as $0$ and $1-p$.
Defect: $\deg(\pi-p)=N(\pi-p)=(\pi-p)(\bar\pi-p)=p-pt+p^2=p\,n$, not $n$; $\pi-p=-\pi\circ(\bar\pi-1)$ is a $pn$-isogeny. The second degree-$n$ rational endomorphism is $\bar\pi-1=t-1-\pi$, kernel the $\pi$-eigenline with eigenvalue $p$ on $E[n]$ (char. poly mod $n$: $x^2-(p+1)x+p=(x-1)(x-p)$, eigenvalues distinct since $p\equiv1\bmod n$ would force $t=2$), scalar $\bar\pi-1\equiv t-2\equiv p-1\pmod n$. Also item (1) genuinely fails at $\ell=n$: $\pi-1$ is the zero map on $E(\mathbb{F}_p)$, not an isomorphism. The scalar-only conclusion survives via item (2).
Repair: replace $\pi-p$ by $\bar\pi-1$ with scalar $p-1$, and say "item (1) fails and item (2) covers" rather than "not a gap".

**D2 — minor (false step as written) — §3 Theorem, item (3).**
Claim: "the fiber polynomials of $\varphi$ … are independent of which point of $E(\mathbb{F}_p)$ is considered."
Defect: the fiber polynomial $F_P(X)=\prod_{K\in\ker\varphi}(X-x(P+K))$ has $x(P)$ as a root (take $K=O$), so its coefficients are non-linear functions of $x(P)$; it is point-dependent. The proof sketch proves only that the *Galois type* of the fiber equals that of $\ker\varphi$. This matters because point-dependent fiber polynomials are exactly the "reads $\mathbb{F}_p$-coordinates non-linearly" class that the next paragraph places outside the theorem.
Repair: replace "fiber polynomials" with "the Galois type (factorisation pattern over $\mathbb{F}_p$) of the fiber".

**D3 — minor — §3 "What the theorem does not cover".**
Claim: "the $n$-torsion of the canonical lift is defined over $\mathbb{Z}_p$."
Defect: $\tilde E[n]\cong O/nO$ has $n^2$ points; Galois Frobenius acts as $\tilde\pi$, which is $1$ on $\tilde E[\pi-1]$ but $p\not\equiv1\pmod n$ on $\ker(\bar\pi-1)$. Only the $N$-torsion $\tilde E[\pi-1]$ ($n$ points) is $\mathbb{Q}_p$-rational. §6 correctly writes $\tilde E[\pi-1]$.
Repair: "the $(\pi-1)$-torsion".

**D4 — editorial — §3 Shimura paragraph.**
Claim: "$k$ is the element of $\mathrm{Gal}(K_N/H)\cong(O/N)^\times/\pm1$ that maps $\tilde P$ to $\tilde Q$."
Defect: $k\in(\mathbb{Z}/n)^\times$; the quotient by $\pm1$ determines only $\pm k$ (the Galois group acting faithfully on points is $\mathrm{Gal}(H(\tilde E[N])/H)\cong(O/N)^\times$; $K_N$ is its fixed field under $\pm1$). This is also the only place $O^\times=\pm1$ is used; the theorem itself does not need it. Repair: "determines $k$ up to sign".

**D5 — minor (hypothesis mislabelled) — §3 Setting.**
Claim: "$\gcd(n,\Delta)=1$ (checked for all ten curves by the red team)."
Defect: this is an identity, not a check. $(t-2)^2-\Delta=4n$, so $\Delta\equiv(t-2)^2\pmod n$; $n\mid\Delta\iff n\mid t-2$, and $|t-2|<n$ forces $t=2$, i.e. $n=p-1$, even. Hence $\gcd(n,\Delta)=1$ for every prime-order curve with $p>3$; likewise "ordinary" is automatic ($t\neq0$ since $n\ne p+1$). Repair: state these as consequences, not standing assumptions.

**D6 — editorial — §4, red-team F4 paragraph (the red team's conclusion stands; the written reason is incomplete).**
Claim: "$\ell=3$ is forced inert ($t\not\equiv0$ and $\Delta\equiv t^2+1\not\equiv0\bmod3$)."
Defect: $\not\equiv0$ excludes only the ramified case; inert needs $\Delta\equiv2$. The correct chain is $t\not\equiv0\Rightarrow t^2\equiv1\Rightarrow\Delta\equiv2$ (non-square). Conclusion and Euler factor $3/4$ are right. Note also that for $p\equiv1\pmod3$ the model gives $P(\text{split at }3)=0$ as well (inert if $t\equiv0$, zero if $t\equiv1$; $t\equiv2$ removed), so the field difference at $\ell=3$ is "inert" versus "inert w.p. $6/15$, zero w.p. $9/15$"; my recomputation gives normalisers $\approx0.65$ and $\approx0.82$, consistent with the README's $0.66$ / $0.84$–$0.86$.

**D7 — minor (internal inconsistency) — §2 vs §4 census agreement.**
§2 describes the at691 census as "8 published and 11 omitted curves in the four fields" and lists published counts "(60, 57, 58; …)"; §4 lists ten published rows including p384 and p521 (six fields) and the table has prime192v2 = 58, prime192v3 = 57. Either the census description or the row list is wrong, and the slugs p192-6013/p192-5228 are never mapped to v2/v3, so "equal … curve for curve" is asserted, not shown, for that pair. Repair: give the slug-to-curve map and correct the field/curve count.

**D8 — minor (Lean/prose mismatch, miscount, stale status) — §6a, follow-up table, §7.**
(a) Follow-up table: "seven declarations". The verbatim file has 13: three `def`s (`dick`, `dickTower`, `kumTower`) and ten theorems. (b) §6a "The Lean core of §3" — the file's own header says isogenies and Shoup are not formalised; neither §6a nor the follow-up says that item (3), the corollary, and the identification $s_\alpha=u+v$ (the content of item (2) beyond "some integer") have no Lean counterpart. (c) §7 still reads "no Lean proof" and "Candidate directions: proposed; not run", and row 1 says "not independently verified by a second producer" while §4 claims a "third producer" and §7's last row records an independent recount with zero mismatches. These postdate the red-team commit, so F10 does not cover them. Repair: count declarations correctly, name the un-formalised parts, update §7.

**D9 — minor (scope) — §6 P1 and its test description.**
Claim: "$p\equiv3\pmod4$ and $2^t\mid p+1$ (the NIST shape, where the Kummer tower does not exist)."
Defect: P-224 has $p=2^{224}-2^{96}+1\equiv1\pmod4$ and $2^{96}\mid p-1$; it is one of the ten curves and has a Kummer tower. Further, at the test primes $v_2(T_{24}-1)=v_2(T_{31}-1)=1$ ($T_{24}-1=2\cdot7{,}340{,}031$, $T_{31}-1=2\cdot1{,}023{,}410{,}175$), so the Kummer base $\{x:x^{2^t}=c\}$ has at most two elements for $t\ge2$; the "four systems on the same planted instance" line must mean a syntactic Kummer-shaped control or a different prime. Repair: say "five of the six NIST fields" and state what the Kummer arms are at $T_{24},T_{31}$.

**D10 — minor (scope claim stronger than evidence) — §6a and follow-ups, P3.**
Claim: "the seed is closed for the coordinate track as well as the generic one."
Defect: the evidence is a null at $2^{24}$ and $2^{28}$ (the proposal's $2^{32}$ arm is not reported) with a $+2\%$ planted positive control and a $\ge1\%$ kill line; the round-2 CIs are $\pm0.19\%$. A null with a stated detection floor bounds the effect at toy size; it does not close the route at cryptographic size. The README's one-paragraph answer still says the question is "untested and is proposal P3", contradicting §6a. Repair: "no effect $\ge$ (CI width) detected at $2^{24},2^{28}$; $2^{32}$ not run."

## CHECKS RUN

- Matrix-count baseline: for $\det=d\ne0$ in $GL_2(\mathbb{F}_\ell)$, split/inert/zero trace classes number $a=(\ell-2-\chi(d))/2$, $b=(\ell-\chi(d))/2$, $c=1+\chi(d)$ with class sizes $\ell^2+\ell$, $\ell^2-\ell$, $\ell^2$; total $\ell^3-\ell$ ✓. Gives $P(\text{split})=\frac{\ell-2-\chi(p)}{2(\ell-1)}$, $P(\text{zero})=\frac{(1+\chi(p))\ell}{\ell^2-1}$ as stated. After removing $\tau\equiv p+1$: $P'=\frac{\ell-4-\chi(p)}{2(\ell-2)}$ ($p\not\equiv1$), $P'=\frac{a(\ell+1)}{\ell^2-\ell-1}$ ($p\equiv1$).
- P-192 field: $p\bmod(3,5,7,11,13)=(2,4,5,9,10)$; $P'=(0,0,0.4,0.333,0.364)$; tail estimate $\sum_{17\le\ell\le691}\frac{2+\chi}{2(\ell-2)}\approx0.83$; $E\approx59.8$, $\mathrm{Var}\approx30.4$, sd $\approx5.51$ — matches table (59.7, 5.51). P-224: $p\bmod(3,5,7,11,13)=(1,1,4,8,9)$, small-$\ell$ contribution $+0.23$ vs P-192 → $E\approx60.0$ (table 60.1) ✓.
- Pooled $z$ at 691: $\sum\text{obs}=544$, $\sum E=598.7$, $\sum\mathrm{Var}\approx304.6$, $z=-54.7/17.45=-3.13$ ✓; Stouffer $\sum z=-9.90$, $/\sqrt{10}=-3.13$ ✓. Per-curve $z$: all ten agree with the table to rounding (e.g. $-17.7/5.51=-3.21$).
- $\pi(691)=125$ → 124 odd primes ✓. Twelve cutoffs ✓. Ten curves ✓.
- $p\bmod3$: P-192, P-239, P-384 $\equiv2$; P-224, P-256, P-521 $\equiv1$ ✓ (P-239 via $p=2^{239}-2^{143}-2^{95}+2^{47}-1$). $p\bmod4$: P-224 $\equiv1$, others $\equiv3$.
- F4 consistency: $0.44\times0.84/0.66=0.56$, $0.49\times0.84/0.66=0.62$ ✓; seven curves in $p\equiv2\pmod3$ fields, ratio $0.66/0.84\approx0.79$ ✓ against "0.78–0.80 on seven curves".
- $N(\pi-p)=pn$; $N(\bar\pi-1)=n$; scalars $1-p$ and $p-1$.
- $(t-2)^2-\Delta=4n$.
- $T_{24}+1=7\cdot2^{21}$, $T_{31}+1=61\cdot2^{25}$; $v_2(T-1)=1$ for both.
- Lean: read all proofs; logic of `hom_card_prime_bijective`, `endo_cyclic_eq_zsmul`, `twist_part_sum_eq_zero`, tower lemmas is sound; declaration count 13.

## CONFIRMED

- §3 item (1) and its proof (kernel order coprime to $n$, Tate's equal point counts) — theorem.
- §3 item (2): $O/N\cong\mathbb{F}_n$ since $N$ has prime norm, so every $\alpha\in O$ is congruent to an integer mod $N$; $\pi\equiv1$ gives $s_{u+v\pi}=u+v$; for $\alpha\in O\setminus\mathbb{Z}[\pi]$ the division by the index is licit because $\gcd(n,f)=1$ (automatic, D5). Lenstra's isomorphism is not actually needed in the prime-order case.
- §3 item (3) pairing argument ($t^\ell=t^n=1\Rightarrow t=1$) and Tate-pairing variant ($P\in\ell E$) — theorem.
- Shimura paragraph's dismissal: the multiplicative DLP is on the unknown residue; enumerating smooth $\alpha$ and comparing $\alpha(P)$ with $Q$ is a $\sqrt n$ collision search — correct heuristic.
- $p$-adic remark: a homomorphism from a finite group to $\mathbb{Q}_p$ is zero — trivially true (the [pcc:unverified] tag is over-cautious).
- §4 baseline model, conditioning, $z$ and pooled $z$ arithmetic — measurement consistent with the stated model.
- §5 degree $=2\times\#\{\text{split }\ell\le B\}$ for $\ell\nmid f$ — correct (horizontal only, as a multigraph).
- Red-team F4 mechanism (field-dependent $\ell=3$ factor) — confirmed numerically.
- `twist_part_sum_eq_zero` matches the P2 purity lemma exactly, including $h_2\Leftarrow E(\mathbb{F}_p)[2]=0$.
- `dickson_tower_faithful` / `kummer_tower_faithful` are correct; the docstring's "every root of $U$ lies in the Dickson base" is equivalent only for squarefree $U$ (editorial).

## RESIDUAL UNCERTAINTY

- `data/recount.json`, the report PDF, `at691.tsv`, and the follow-up RESULTS files are not in the brief; agreement claims and the $3\mid f$ (P-224), $5\mid f$ (prime239v2), embedding-degree and $z$-at-5,000/50,000 values are unchecked.
- Lean build: in the Mathlib signature I know, `modByMonic_eq_sub_mul_div (p) {q} (hq : q.Monic)` takes a monicity proof as its second explicit argument, so `modByMonic_eq_sub_mul_div a U` (used twice) would not elaborate; either the transcription differs from the built file or the Mathlib version differs. I cannot resolve this from the brief.
- Theorem 15.1 of `RESEARCH_ISOGENY_FIBERS_ECDLP.md` and its bound $(Q+2)^2/r+1/r$ are not reproduced here.
- The report's normaliser (0.83–0.84) and its Figure 4 are known only through the README's description.
- Primality of $T_{24}$, $T_{31}$ and all msolve/F4 degree and width numbers in the follow-ups are unchecked.

---

# Appendix — surviving routes and their tests

## AUDIT

### VERDICT
**Holds with listed repairs.** Items (1) and (2) of the §3 theorem are correct as proved; item (3) is correct for the *Galois structure* of the listed objects but false as literally worded for fiber polynomials (D2). The corollary holds inside the generic-plus-scalar-oracle model and nowhere else (F1, F8, not repeated). Three statements around the theorem are wrong or unsupported and need repair: the $\ell=n$ remark (D3), the "computable canonical lift" claim (D4), and the §4 baseline formulas as printed (D1). None of the repairs changes the conclusion that the split-prime pattern reaches $E(\mathbb F_p)$ only through scalars and DLP-preserving isomorphisms.

### DEFECTS

**D1 (minor, §4 Method).** *Claim:* baseline $P(\text{split}) = \frac{\ell-2-\chi(p)}{2(\ell-1)}$, $P(\text{ram}) = \frac{(1+\chi(p))\ell}{\ell^2-1}$, "the trace class $\tau\equiv p+1$ is removed and the rest renormalised." *Defect:* the printed formulas are the **unconditioned** probabilities (verified below from the $\mathrm{GL}_2(\mathbb F_\ell)$ class counts); after removing $\tau\equiv p+1$ they change, and the change is case-dependent because the removed class has discriminant $(p+1)^2-4p=(p-1)^2$: it is a split class when $p\not\equiv1\pmod\ell$ and a ramified class when $p\equiv1\pmod\ell$. The conditioned values are
$$
P_{\rm split}=\begin{cases}\dfrac{\ell-3}{2(\ell-2)} & \chi(p)=-1,\\[6pt] \dfrac{\ell-5}{2(\ell-2)} & \chi(p)=1,\ p\not\equiv1\ (\ell),\\[6pt] \dfrac{(\ell+1)(\ell-3)}{2(\ell^2-\ell-1)} & p\equiv1\ (\ell),\end{cases}\qquad
P_{\rm ram}=\begin{cases}0\\[6pt] \dfrac{2\ell}{(\ell+1)(\ell-2)}\\[6pt] \dfrac{\ell}{\ell^2-\ell-1}.\end{cases}
$$
The table's expectations ($59.7$–$60.3$ over 124 primes) are consistent with the conditioned model and **inconsistent** with the printed formulas: unconditioned, $\sum P_{\rm split} = 62-\sum_{\chi(p)=1}\frac1{\ell-1}\ \ge\ 62-\sum_{\ell\le691}\frac1{\ell-1}\approx 62-1.93 = 60.07 > 59.7$. So the code is right and the README's derivation text is not. *Repair:* print the three-case formulas (and note the printed ones are pre-conditioning).

**D2 (minor, §3 item 3).** *Claim:* "the fiber polynomials of $\varphi$ … are independent of which point of $E(\mathbb F_p)$ is considered." *Defect:* writing $x\circ\varphi = N(X)/D(X)$, the fiber polynomial above $\varphi(P)$ is $N(X)-x(\varphi(P))\,D(X)$; its coefficients depend on $x(\varphi(P))$ and its roots are $x(P+T)$, $T\in\ker\varphi$, which vary with $P$. Only the *Galois-set structure* of the fiber ($\cong\ker\varphi$ by translation by the rational point $P$) is point-independent, as the proof sketch itself says. The values $x(P+T)\in\mathbb F_{p^d}$ are a non-linear coordinate reading the theorem does not cover (route S2). *Repair:* replace "fiber polynomials" by "the Galois-module structure of the fibers".

**D3 (minor, §3 Setting).** *Claim:* "the two rational $n$-isogenies are the endomorphisms $\pi-1$ and $\pi-p$, acting as $0$ and $1-p$; the exclusion $\ell\ne n$ is a convenience, not a gap." *Defect:* $N(\pi-p)=p^2-pt+p = p\,n$, so $\pi-p=\pi\circ(1-\bar\pi)$ has degree $pn$, not $n$; the second rational $n$-isogeny is $1-\bar\pi$ (degree $N(1-\bar\pi)=n$), which does act as $1-p$. Moreover item (1) **fails** at $\ell=n$: $\pi-1$ restricted to $E(\mathbb F_p)$ is zero, not an isomorphism. The exclusion is a convenience for item (2) only. *Repair:* name $1-\bar\pi$ and say item (1) excludes $\ell=n$ because one of the two $n$-isogenies kills $E(\mathbb F_p)$ (harmless for the obstruction).

**D4 (minor, §3 "What the theorem does not cover").** *Claim:* "every point of $E(\mathbb F_p)$ has a computable canonical lift with $p$-adic coordinates." *Defect:* existence is right (the $\pi=1$ eigenspace of $\tilde E[n]$ is unramified-Frobenius-fixed, hence $\mathbb Q_p$-rational), but **computability at cryptographic $p$ is unsupported**: no construction is given, and the two standard descriptions of $\tilde E$ are a root of $\Phi_p(X,X)$ (degree $2p+2\approx2^{193}$) or of the ring class polynomial $H_{\mathcal O}$ (degree $h(\mathcal O)\approx \frac{\sqrt{|\Delta|}}{\pi}L(1,\chi)\approx 2^{95}$ for the 192-bit curves); Satoh-type lifting is polynomial in $p$, not $\log p$. What *is* computable is the torsion lift on an **arbitrary** $\mathbb Z_p$-lift $\hat E$: $0\to\hat E_1(\mathbb Z_p)\cong\mathbb Z_p\to\hat E(\mathbb Z_p)\to E(\mathbb F_p)\to0$ splits since $\mathrm{Ext}(\mathbb Z/n,\mathbb Z_p)=\mathbb Z_p/n=0$, so every lift has torsion $\cong\mathbb Z/n$ mapping isomorphically onto $E(\mathbb F_p)$, and $\hat P=\hat P_0-[n]^{-1}([n]\hat P_0)$ is Hensel-computable. That presentation is pattern-independent and CM-free, so the Shimura paragraph does not reach it. *Repair:* replace "canonical lift" with "any $\mathbb Z_p$-lift", state the infeasibility counts, keep the closure $[\mathrm{pcc{:}unverified}]$ (see S1).

**D5 (minor, §5).** *Claim:* horizontal degree $=2\times\#\{\text{split }\ell\le B\}$ with "split" $:=(\Delta/\ell)=1$. *Defect:* the JMV graph at $E$ has degree $2\#\{\ell\le B:\ \ell\nmid f_E,\ (d_K/\ell)=1\}$ where $f_E$ is the conductor of $\mathrm{End}(E)$; this exceeds the $(\Delta/\ell)=1$ count at every $\ell\mid f$ with $(d_K/\ell)=1$ when $E$ sits above the $\ell$-level of $\mathrm{End}$. The study records $3\mid f$ (P-224) and $5\mid f$ (prime239v2) but determines $\mathrm{End}(E)$ for none of the ten curves, so "degree 100" for P-224 is unverified by one or two edges. *Repair:* state the $f_E$ dependence or compute the volcano level at the small $\ell\mid f$.

**D6 (minor, §2/§3 "closes the indirect route").** The within-class null (`isogeny_class_ic_yield_20261102`) was measured on **conductor-1** classes ($h=128,300$), which have no vertical structure, while two of the ten published classes have $3\mid f$, $5\mid f$. "Model choice within the class is null" is therefore extrapolated to classes with vertical isogenies without a measurement. (Distinct from F1, which concerns between-class effects.) *Repair:* scope the sentence to conductor-1 classes.

**D7 (minor, §6a vs follow-ups Round 2).** (i) §6a reports P1 as "keeps its lower solving degree"; Round 2 records a **trade** against round 7's arm F at all nine $m=3$ cells (one degree lower, matrices $2.3$–$3.0\times$ wider) and dominance over T only at $t=3,4$. (ii) §6a's P3 rho statement rests on Round 1, where the walk was defective; only the Round-2 rerun (A/A $r=0.027/0.009$) supports the null. (iii) §6 pre-registered $2^{24},2^{28},2^{32}$; §6a reports 4,000 curves $=2\times2{,}000$, i.e. the $2^{32}$ arm was dropped without a stated reason. (iv) "seven declarations" vs. the file's 10 theorems and 3 definitions. *Repair:* rewrite §6a from Round 2, state the dropped arm, fix the count.

**D8 (minor, §7 status table).** Row 1 says the recount is "not independently verified by a second producer", while the last row records the red team's independent big-integer recount at all twelve cutoffs with zero mismatches and §2/§4 cite the at691 census as a third producer. Row 2 says "no Lean proof" after PR #3; the accurate status is: items (1), (2) formalized as existence statements over abstract finite groups (no isogeny, no Lenstra identification of $s_\alpha$), item (3) not formalized. *Repair:* update both rows.

**D9 (editorial, §3 Shimura paragraph).** "cost about one scalar multiplication each" has no count. Supporting count: for $\alpha=u+v\pi\in\mathcal O$, $v\ne0$, $N(\alpha)=(u+tv/2)^2+v^2|\Delta|/4\ \ge\ |d_K|/4\approx 2^{190}$, so a $B$-smooth principal $\alpha$ needs $\ge \log_2(|d_K|/4)/\log_2B$ isogeny steps ($\ge 21$ at $B=691$ on 192-bit curves), each costing $\Theta(\ell)$ multiplications by Vélu, i.e. not below a scalar multiplication. A walk on non-principal ideals enlarges the state space to $n\cdot h\approx 2^{192+95}$, which is worse. *Repair:* add the count.

**D10 (editorial, §3 corollary).** "$\Omega(\sqrt n)$ … cannot yield a sub-generic algorithm" is a per-instance, no-advice bound; with $S$ bits of curve-specific preprocessing the generic bound is $S\,T^2=\tilde\Omega(n)$ (Corrigan-Gibbs–Kogan), so online $T<\sqrt n$ is generic and pattern-free. *Repair:* say "total work".

**D11 (editorial).** (i) Lenstra's paper is, to my recollection, *J. Number Theory* **56** (1996), 227–241, not vol. 77 — verify (the study flags "from memory"). (ii) §2's list "(60, 57, 58; …)" is in at691 label order (139, 5228, 6013), while the §4 table reads (60, 58, 57); the mapping label$\leftrightarrow$v2/v3 is asserted, not shown. (iii) "no $\ell\le200{,}000$ divides any $n$" is vacuous for 190-bit primes $n$. (iv) "exactly as hard" via JMV should read "up to transport cost, under GRH". (v) `dickson_tower_faithful`'s docstring "every root of $U$ lies in the Dickson base" presumes all $2^t$ roots of $D_{2^t}(x)=c$ are in $\mathbb F_p$ (true for the torus choice when $2^t\mid p+1$) and $U$ squarefree; neither is in the statement.

### CHECKS RUN
1. **$\mathrm{GL}_2(\mathbb F_\ell)$, $\det=d$ class sizes:** split trace $\ell(\ell+1)$, inert $\ell(\ell-1)$, ramified $\ell^2$; counts of traces $(s,r,i)=(\tfrac{\ell-3}2,2,\tfrac{\ell-1}2)$ for $\chi(d)=1$, $(\tfrac{\ell-1}2,0,\tfrac{\ell+1}2)$ for $\chi(d)=-1$; both satisfy $(\ell+1)s+\ell r+(\ell-1)i=\ell^2-1$. Unconditioned $P_{\rm split}=s/(\ell-1)$ reproduces the printed formula. Conditioned formulas (D1) sum to 1 at $\ell=7$: $0.2+0.35+0.45$ and $\tfrac{32}{82}+\tfrac{14}{82}+\tfrac{36}{82}$.
2. **$\ell=3$ on a prime-order curve is never split:** $p\equiv2\ (3)$: $t\in\{1,2\}$, $\Delta\equiv1-8\equiv2$ (inert) — the README's forced-inert claim is correct; $p\equiv1\ (3)$: $t\in\{0,1\}$, $\Delta\equiv t^2-1\in\{2,0\}$ (inert or ramified). Model: $P_{\rm ram}(3\mid p\equiv1)=9/15=0.6$. Field residues: P-192 $=2^{192}-2^{64}-1\equiv2$, P-224 $\equiv1$, P-256 $\equiv1$, P-384 $\equiv2$, P-521 $=2^{521}-1\equiv1$, P-239 ($2^{239}-2^{143}-1$, from memory) $\equiv2$ — all match §4's grouping, so F4's seven-curve/0.78 pattern is arithmetically consistent.
3. **Pooled $z$ at 691 from the table:** $\sum\text{obs}=544$, $\sum\text{exp}=598.7$, $\sum\text{var}=304.6$, $z=-54.7/17.45=-3.13$ ✓; Stouffer $-9.90/\sqrt{10}=-3.13$ ✓; per-curve $z$ recomputed, all within $0.01$ of the table.
4. **Unconditioned lower bound** $\sum_{\ell\le691}\frac1{\ell-1}$: exact to $\ell=97$: $1.574$; tail $\approx\ln\ln691-\ln\ln100\approx0.35$; total $\approx1.93$ → unconditioned expectation $\ge60.07$ (D1).
5. **124 odd primes $\le691$:** $\pi(691)=125$ ✓. Variance $\sum P(1-P)\approx30.4\Rightarrow\sigma=5.51$ ✓.
6. **Norms:** $N(\pi-1)=p+1-t=n$; $N(\pi-p)=p-pt+p^2=pn$; $N(1-\bar\pi)=n$; $1-\bar\pi$ acts as $1-p\equiv 2-t\pmod n$ ✓.
7. **Pairings:** $e_{\ell n}(T,P)^\ell=e_{\ell n}(T,P)^n=1\Rightarrow1$; Tate: $P=[\ell\cdot(\ell^{-1}\bmod n)]P\in\ell E(\mathbb F_p)$, so the class of $P$ in $E/\ell E$ is trivial ✓.
8. **Lean:** `endo_cyclic_eq_zsmul`, `hom_card_prime_bijective` (kernel order $\mid p$; $\bot\Rightarrow$ injective $\Rightarrow$ bijective by card; $\top\Rightarrow f=0$), `twist_part_sum_eq_zero` ($\pi S=-S$, $\pi T=T$, cancel $T$, $2S=0$, apply `h2`), `dickTower_eq`/`kumTower_eq` by induction with the two `modByMonic` lemmas, `modByMonic_eq_C_iff` needing $\deg U\ge1$ — each step traced and found correct; Dickson recursion $D_{2k}=D_k^2-2$ ✓. Build itself not checked.
9. **Canonical lift:** $\tilde E[N]$ Frobenius-fixed ⇒ $\mathbb Q_p$-rational ✓; $\mathrm{Ext}(\mathbb Z/n,\mathbb Z_p)=0$ ⇒ every lift has torsion $\cong\mathbb Z/n$ (D4); $h\approx2^{95}$ from $|\Delta|\approx2^{194}$.
10. **Shimura:** $|\mathrm{Gal}(K_N/H)|=(n-1)/2$; $\mathrm{Art}(\mathfrak p)$ for $\mathfrak p=(\pi)$ acts on $\tilde E[N]$ as $\pi\equiv1$, so $\mathfrak p$ splits completely in $K_N$ and no $p$-adic embedding carries a Galois action.
11. **Isogeny-step cost bound** $N(\alpha)\ge|d_K|/4$ (D9).

### CONFIRMED
- §3 items (1), (2): separability ($\ell\ne p$), $\ker\varphi\cap E(\mathbb F_p)=0$, Tate's equal-order, cyclicity ⇒ scalar; $s_\alpha=(u+v)f^{-1}\bmod n$ well-defined because $\gcd(n,f)=1$ follows from $\gcd(n,\Delta)=1$ and $f^2\mid\Delta$. Item (3) for Galois structure and all $\ell$-pairings.
- Hypotheses on the ten curves: ordinary ($t\ne0$ since $p+1$ even, $n$ odd); $\mathcal O^\times=\pm1$ from $a=-3\ne0$, $b\ne0$; $\gcd(n,\Delta)=1$ as red-team-checked. Failure modes (unstated, F9): non-ordinary breaks (2) (non-rational endomorphisms); $\mathcal O^\times\ne\pm1$ adds known scalars (constant-factor rho gain only); $n\mid f$ breaks only the explicit formula, not the scalar statement.
- The Shimura-reciprocity dismissal in substance, with the sharper reason in check 10; the BSGS reading of smooth-$\alpha$ enumeration, with the cost count of D9.
- F4's field-mismatch mechanism (check 2); the recount's scoped agreement/disagreement statement in §4 (not the summary — F3).
- P2 purity lemma as applied: fixed points of $\pi$ are $E(\mathbb F_p)$, $E(\mathbb F_p)[2]=0$ for odd $n$.
- $\ell=p$ exclusion is also a convenience: Frobenius and Verschiebung act as $1$ and $p$.

### RESIDUAL UNCERTAINTY
Not derivable from the brief: the actual $t,\Delta,f_E,d_K$ per curve (so D5's edge count and $(d_K/3)$ for P-224); `splitcount.rs` source (whether the code's conditioning matches D1's three cases exactly — only the expectation values were checked); the uploaded report's tables and its 0.78 factor; the at691 label↔curve mapping; Lean build; Round-2 protocols and P3's CI widths for yield (power at the 1 % kill line is asserted via a +2 % planted arm only); the text of Theorem 15.1; the red-team fixes for F7, F8 (not visible, so not judged).

---

## SURVIVING ROUTES

Excluded as generic restatements (the theorem covers them): isogeny-chain rho walks (D9 count), Pohlig–Hellman on $E(\mathbb F_{p^d})$, preprocessing (D10), within-class model choice. Out of scope by Question B: quantum and implementation attacks.

**S1. $p$-adic torsion-lift presentation — `[partly examined]`** (left open by §3 "What the theorem does not cover", F2, problem record; D4).
(a) The corollary's operations are the group law, $\mathbb F_p$-rational maps and point-independent Galois data; the digits of a torsion lift $\hat P\in\hat E(\mathbb Z_p)$ beyond the first are point-dependent and not $\mathbb F_p$-affine in the log, so Shoup's simulation does not apply. The study's closure kills only the elliptic logarithm (and, by the same vanishing-on-torsion argument, $p$-adic heights); no other functional is addressed. Per D4 the *canonical* lift is not computable at scale, so the available version is an arbitrary lift, which is pattern-independent — the pattern cannot enter here.
(b) Test: two toy prime-order curves, $p\approx n\approx2^{20}$; Weierstrass lift with the same integer $(a,b)$; $N=10^5$ random $k$; features: digits 2–4 of $x,y$ of $\hat P$ and $\hat Q=[k]\hat P$ (12 features) plus $k$. Metric: $\mathbb F_p$-dimension of the space of polynomial relations of total degree $\le3$ among the 13 quantities, by linear algebra on $N\gg\binom{16}{3}=560$ monomials; control: random (non-torsion) lifts of the same points. Kill line: relation dimension equal to the control (zero torsion-specific relations) at both primes.
(c) A nonzero torsion-specific relation would be the first non-linear handle outside the coordinate track and would matter; zero closes the route at this degree/precision. Note the digits are Hensel-computable rational functions of $(x(P),y(P))$, so a proof that this is a sub-case of the coordinate track would close it fully and is cheaper than the test.
(d) Prior $0.01$ for any stage effect; $\le0.001$ for beating rho; $0$ for pattern dependence.

**S2. Extension-field presentations of the transported group — `[unexamined]`** (left open by §3 item (3) as worded (D2) and §6's kill list, which covers only $\mathbb F_p$-fibers and $\mathbb F_{p^2}$ twist translations).
Two sub-routes: (i) translation of $P$ by eigenline $\ell$-torsion $T$ rational over $\mathbb F_{p^d}$, $d=\mathrm{ord}_\ell(\lambda)$, reading $x(P+T)\in\mathbb F_{p^d}$; (ii) transport by an Atkin $\ell$-isogeny, $\mathbb F_{p^d}$-rational only, to $E'/\mathbb F_{p^d}$.
(a) The theorem requires $\mathbb F_p$-rational $\varphi$ (fails for (ii)) and covers only the Galois structure of fibers, not the values $x(P+T)$ (fails for (i)). The pattern selects exactly these $d$'s.
(b) Test: toy $p\approx2^{20}$, prime order, $d=2$; Gaudry $m=2$ decomposition over $\mathbb F_{p^2}$ (Semaev $S_3$, factor base $x\in\mathbb F_p$) on the translated/transported instance versus a native $E(\mathbb F_{p^2})$ instance at the same $p$. Metric: relations per $10^5$ $S_3$ evaluations and linear-algebra dimensions. Kill line: yield ratio in $[0.9,1.1]$ at two primes.
(c) A replicated ratio $>1.1$ would be a stage curiosity only: the known exponent for decomposition on $E(\mathbb F_{p^d})$ is $2-2/d$, giving $\approx p\approx n$ at $d=2$ and $p^{4/3}$ at $d=3$, both $\gg n^{1/2}$; Weil restriction of a curve defined over $\mathbb F_p$ is isogenous to a product containing $E$ itself, so the $n$-part does not move. The count closes the end-to-end question regardless of the test.
(d) Prior $0.01$ stage; $0$ for beating rho.

**S3. Cross-class coordinate covariates outside P3's cells — `[partly examined]`** (left open by §6a P3 and Round 2: only relation coverage and rho, at $2^{24},2^{28}$; the $2^{32}$ arm dropped (D7); F4 degree/width not an outcome).
(a) F1's gap: non-linear coordinate reading is outside the theorem and between-class dependence on $\Delta$-covariates is exactly what P3 tests; P3 did not measure the F4 solving degree or matrix dimensions, where C1's weighted-homogeneity lemma predicts curve-independence of the top form but says nothing about lower-order terms.
(b) Test: 200 prime-order curves per prime at $2^{24},2^{28}$, stratified by $E_{691}$ quintile; outcome: msolve F4 degree $D$ and maximal matrix dimensions at $m=3$, $t=3$. Metric: Spearman $\rho(E_{691},\text{F4 work})$ and Kruskal–Wallis across quintiles; planted $+2\%$ positive control. Kill line: $|\rho|<0.05$ and KW $p>0.1$ at both primes with the control detected.
(c) Replicated $|\rho|\ge0.1$ would make the seed a coordinate-track lead; a null closes the pattern for the coordinate track at the $D$/width level as well as at yield.
(d) Prior $0.02$ non-null; $0$ baseline gain.

**S4. Shimura / ray-class-field presentation — `[closed by the brief]`** (§3 last paragraph). Completion of the closure: $\mathfrak p=(\pi)$ splits completely in $K_N$ (check 10), so no $p$-adic or $\mathbb F_p$ embedding carries a $\mathrm{Gal}(K_N/H)$ action, and global representation requires degree $[K_N:\mathbb Q]=h\,(n-1)\approx2^{95}\cdot2^{192}$. No test; prior $0$.

**S5. $n$-pairing (MOV/FR) — `[closed by the brief]`** (§3; red team: embedding degree $k>20{,}000$ on all ten). Count: target field $\mathbb F_{p^k}$ of $\ge192\cdot20{,}000\approx3.8\times10^6$ bits. Prior $0$.

**S6. Anomalous ($n=p$) — `[closed by the brief]`** ($n=p$ iff $t=1$; false for all ten). Prior $0$.

**S7. Volcano level of each published curve — `[closed by the brief]` as an ECDLP route, `[unexamined]` as data** (§5, D5). Vertical isogenies are inside the theorem, so no cost implication; the only use is to correct §5's degree count. Test: walk the $\ell$-volcano at $\ell=3$ (P-224) and $\ell=5$ (prime239v2) to determine $f_E$ and $(d_K/\ell)$; metric: horizontal degree at $B=691$; no kill line (descriptive). Prior $0$ for ECDLP relevance.

# Published ECDLP barriers — annotated survey (2026-11-09)

Generated with `claude-fable-5-2` from the repository's curated frontier map. This is a report on published lower bounds and closure theorems only; it proposes no algorithm.

**Citation convention.** Each `KR-*` id carries the `KN-LIT-*` sources and read depths listed against it in `## CITATIONS`. Status tags (proven, heuristic, measured, conjectured, reported, disputed) are the map's. Arithmetic I applied to a row's formula is marked "(arithmetic on row)" and is not a published figure.

## SUMMARY

1. For a prime-order group of size $n$, the generic-group model gives a proven $\Omega(\sqrt{n})$ lower bound, and parallel rho meets it at about $\sqrt{\pi n/2}$ iterations; published gains on general prime-field curves are constant factors only (negation $\sqrt{2}$, measured $0.947\sqrt{2}$ on P-256) (KR-RHO-13bf67, KR-RHO-6239aa, KR-RHO-fb88e6, KR-RHO-825bca).
2. The published non-generic routes over $\mathbb{F}_p$ are either curve checks (small embedding degree, trace one) or recorded negatives: naive Semaev index calculus is proven, under stated statistical assumptions, to cost at least as much as generic methods, and xedni/lifting succeeds with negligible probability (KR-RHO-53c89f, KR-IC-5931ee, KR-IC-cd159a).
3. Every published sub-rho algebraic result applies to $E(\mathbb{F}_{q^n})$ with $n\ge 3$, to genus $g\ge 3$, or to special curves and fields; Diem's rigorous results leave prime fields open, and the 2016 survey reports no known attack better than rho for general prime-field curves (KR-IC-46d822, KR-IC-64659b, KR-IC-5ea2f8, KR-IC-9e610d).
4. Empirically, the largest prime-field computations are 112 and 114 bits, and the measured-rate extrapolation for P-256 is about $3.9\cdot10^{24}$ core-years (KR-RHO-33f837, KR-RHO-825bca).
5. The record does not establish a lower bound outside the generic model, an unconditional theorem excluding non-naive index calculus over $\mathbb{F}_p$, or a validated complexity predictor for the relevant polynomial systems; the map itself is curated, not exhaustive.

## FAMILIES

| Family | Mechanism | Best published complexity (status) | Regime | Published limit | KR ids |
|---|---|---|---|---|---|
| Generic collision search (rho, parallel distinguished points) | Pseudo-random walk on the group, with collisions detected through distinguished points. | $\approx\sqrt{\pi n/2}$ iterations in total, linear parallel speedup (proven); $\Theta(\sqrt{n})$ with random-oracle partition, and additive walks within a $\sqrt{\log n}$ factor of birthday (proven). Negation $\sqrt{2}$, measured $0.947\sqrt{2}$ on P-256; automorphism group of order $m$ gives $\sqrt{m}$, measured $0.790\sqrt{6}$ on BN254. P-256: ~1129 cycles/step, ~$3.9\cdot10^{24}$ core-years (reported). For $n\approx2^{256}$: $\approx2^{128.3}$ iterations, $\approx2^{127.9}$ with the measured negation factor (arithmetic on row). | Any prime-order group, all fields. | $\Omega(\sqrt{n})$ in the generic group model; automorphism gain "never changes the exponent $1/2$". | KR-RHO-6239aa, KR-RHO-93979e, KR-RHO-fb88e6, KR-RHO-0528e7, KR-RHO-825bca, KR-RHO-13bf67 |
| Generic variants (interval, multi-target, preprocessing, ordering) | The same black-box operations applied to a restricted key range, many targets, or precomputed tables. | Interval of width $N$: $(2+o(1))\sqrt{N}$ (proved), $\approx1.66\sqrt{N}$ Gaudry–Schost, $\approx1.36\sqrt{N}$ with negation. $L$ targets: $\approx\sqrt{2Ln}$ in total. Preprocessing: $\approx1.77\,l^{1/3}$ online after $\approx1.2\,l^{2/3}$ precomputation. Grumpy giants: success probability 0.71875 after $1.5\sqrt{l}$ operations. | Any group; requires interval keys, many targets, or a one-time precomputation. | Yun's generic multi-target lower bounds (tight); $S\cdot T^2=\tilde\Omega(\varepsilon N)$; $T^2 S=\tilde\Theta(C^2N)$. | KR-RHO-898783, KR-RHO-46c2c6, KR-RHO-ea34b8, KR-RHO-7d93f6, KR-RHO-fbd7b1 |
| Summation-polynomial index calculus over $\mathbb{F}_p$ | Decompose points over a factor base via Semaev's $S_m$ (degree $2^{m-2}$ per variable). | No published complexity below rho; algebraic factor bases "work only at small parameters"; the Gröbner-free variant is reported worse than rho. | Prime fields. | Yokoyama–Yasuda–Takahashi–Kogure (proven under stated statistical assumptions); 2016 survey consensus (reported). | KR-IC-5a43e5, KR-IC-5931ee, KR-IC-9e610d, KR-IC-ae532f |
| Point decomposition over $E(\mathbb{F}_{q^n})$, small fixed $n$ | Weil-restriction factor base with decomposition into $n$ or $n-1$ points. | Gaudry: $\tilde O(q^{2-2/n})$, constant $\sim n!\cdot2^{n(n-1)}$ (heuristic); $n=3$: $O(q^{10/7})$, $n=4$: $O(q^{14/9})$. Joux–Vitse: $\approx(n-1)!\,q^2\cdot\mathrm{poly}((n-1)!\,2^{(n-1)(n-2)}\log q)$ (heuristic). Diem: $L(2/3)$-type for $n\approx\sqrt{\log q}$, and for $n$ up to about $\log q$ (proven). Symmetries: about $2^{\omega(n-1)}$ gain; ~$2^{130}$ word operations for twisted Edwards over $\mathbb{F}_{q^5}$, $q\approx2^{64}$ (heuristic). Record: 149-bit subgroup of $E(\mathbb{F}_{p^6})$, ~110,000 CPU-hours (reported). | Extension fields; beats rho's $q^{n/2}$ for $n\ge3$ (Gaudry, asymptotically) or $n\ge5$ (Joux–Vitse). | Diem's open cases are prime fields and prime-degree binary fields; no summation method has beaten rho on a cryptographic-size prime-field curve. | KR-IC-46d822, KR-IC-081a58, KR-IC-64659b, KR-IC-955fd6, KR-IC-e2d81b, KR-IC-ae532f |
| Binary-field decomposition, prime degree | Descend $S_m$ to $\mathbb{F}_2$ with a subspace factor base. | Claimed $2^{c\,n^{2/3}\log n}$ (crossover $n\approx2000$), $2^{c\sqrt{n\ln n}}$, and polynomial; all disputed. Quasi-subfield improvement is conjectured. | $\mathbb{F}_{2^n}$, $n$ prime. | Evidence that the first-fall-degree assumption fails; measured far slower than rho at reachable sizes. | KR-IC-889857, KR-IC-f5c584, KR-IC-1fcdbc, KR-IC-49c882 |
| Weil descent, GHS, cover attacks | Map ECDLP on $E(\mathbb{F}_{q^n})$ to a higher-genus Jacobian over $\mathbb{F}_q$, then run index calculus there. | Genus $g$: $\tilde O(q^{2-2/g})$ with double large primes, beating $q^{g/2}$ for $g\ge3$ (heuristic). Record: subgroup over $\mathbb{F}_{2^{5\cdot31}}$, ~1,035 CPU-days (reported). | Extension fields; special fields and curves only. | "Effective only for special fields/curves" (proven mechanism, classified weak classes). | KR-IC-5ea2f8, KR-IC-a4dd54, KR-IC-ae532f |
| Pairing transfer (MOV, Frey–Rück) | Reduce ECDLP to a finite-field DLP in the embedding field. | Cost is that of the finite-field DLP; the map gives no figure. | Small embedding degree only. | Generic curves have astronomically large embedding degree; a curve check (proven). | KR-RHO-53c89f |
| Isogeny-based transfer | Move to an isogenous curve in a weaker class. | No gain for order-determined weaknesses. Tian 2023 moves some prime-order curves over $\mathbb{F}_{q^3}$ into a GHS-vulnerable class. | The published positive instance is over $\mathbb{F}_{q^3}$. | Tate's theorem plus random self-reducibility under JMV's conditions (proven). | KR-RHO-755e35, KR-IC-5ea2f8 |
| p-adic attack on anomalous curves | Lift p-adically and read the logarithm from the formal group. | Polynomial time (proven). | Trace-one curves only. | Generic curves have trace $\neq1$; a curve check. | KR-RHO-53c89f |
| Lifts to characteristic zero (xedni) | Lift points to $\mathbb{Q}$ and look for rank-deficient lifts. | Succeeds with negligible probability (proven, per the map). | Proposed for general curves. | Jacobson–Koblitz–Silverman–Stein–Teske. | KR-IC-cd159a |
| Algebraic solvers (Gröbner F4, crossbred, F4-trace, SAT/WDSat) | Solve the point-decomposition polynomial system. | SAT/WDSat up to $300\times$ faster than Magma F4 on the decomposition step (measured), "without changing the exponent relative to rho". Symmetric reformulation gives a constant/polynomial factor (reported). F4-trace and crossbred are reported mechanisms. | Binary-curve decomposition at small $n$, $l$; Boolean systems. | Semi-regular predictions do not describe descended summation systems; first-fall-degree heuristic unsafe. | KR-IC-5765d2, KR-IC-8b9daa, KR-IC-f3da82, KR-IC-e847d1, KR-IC-fbdb61, KR-IC-f5c584, KR-IC-0d2021 |
| Structural / representation (subset-sum style) | Representation technique applied to ECDLP. | $p^{1.314}$ versus rho's $O(p)$; lists alone need $p^{3/4}$ (proven negative). | $\mathbb{F}_{p^2}$. | The result is itself the limit. The map has no additive-combinatorics row (see gap 10). | KR-RHO-5b1c0a |

## WHAT IS RULED OUT

**A. Generic-group and black-box bounds**

- **Generic lower bound (theorem; KR-RHO-13bf67).** Any algorithm using only group operations and equality needs $\Omega(\sqrt{p})$ operations in a group of prime order $p$.
  - *Rules out:* any exponent below $1/2$ by black-box means, for every field type.
  - *Does not rule out:* algorithms that use the point representation; the row says a sub-$\sqrt{\ }$ algorithm "must exploit the representation". It is a model statement, not a lower bound for elliptic curves.
  - *Tightness:* rho collides in $\Theta(\sqrt{n})$ steps with a random-oracle partition, and r-adding walks are within a $\sqrt{\log n}$ factor (theorem; KR-RHO-93979e).
- **Automorphisms and negation (theorem plus measured; KR-RHO-0528e7, KR-RHO-fb88e6).** Orbit walks give $\sqrt{m}$ for an automorphism group of order $m$ ($\sqrt2$, $\sqrt4$, $\sqrt6$).
  - *Rules out:* reading an efficient endomorphism as an exponent change.
  - *Scope:* constant factors only; measured values are $0.947\sqrt2$ and $0.790\sqrt6$ (KR-RHO-825bca).
- **Multi-target (theorem; KR-RHO-46c2c6).** $L$ logarithms in one group cost about $\sqrt{2Ln}$ in total, and Yun's generic lower bounds make this tight.
  - *Rules out:* generic batch gains beyond $\sqrt{Ln}$.
  - *Does not rule out:* the amortised per-target saving itself. The row implies a single-target $\sqrt{n}$ figure is not a per-key figure when many keys share a group.
- **Preprocessing (theorem; KR-RHO-ea34b8).** $S\cdot T^2=\tilde\Omega(\varepsilon N)$, met by $\approx1.77\,l^{1/3}$ online work after $\approx1.2\,l^{2/3}$ precomputation.
  - *Rules out:* better online/table trade-offs for preprocessing algorithms.
  - *Does not rule out:* the trade-off itself. For $l\approx2^{256}$ this is $\approx2^{86.2}$ online after $\approx2^{170.9}$ precomputation with $\approx2^{85.3}$ stored points (arithmetic on row).
  - *Model:* the row does not state it; generic group model with preprocessing [recalled, unverified].
- **Time–space for collisions (theorem; KR-RHO-7d93f6).** $T^2S=\tilde\Theta(C^2N)$.
  - *Rules out:* beating parallel collision search by adding storage.
  - *Model:* not stated in the row.
- **Interval keys (theorem; KR-RHO-898783).** This is an upper bound, recorded here as a scope condition. A key confined to a width-$N$ interval costs $(2+o(1))\sqrt{N}$, down to $\approx1.36\sqrt N$ with negation. The $\sqrt{n}$ estimate presupposes keys spread over the full group.

**B. Transfer theorems and closures**

- **Pairing and anomalous transfers are curve checks (theorem; KR-RHO-53c89f).**
  - *Rules out:* these as algorithms against curves with large embedding degree and trace $\neq1$.
  - *Does not rule out:* anything about curves failing those checks. The assurance is per curve and depends on the checks having been done.
- **Isogeny closure (theorem, conditional; KR-RHO-755e35).** Isogenous curves have equal order (Tate), and ECDLP is random-self-reducible across the class under JMV's conditions.
  - *Rules out:* reaching an anomalous, small-embedding-degree, or smooth-order curve by walking the isogeny class.
  - *Does not rule out:* weaknesses not determined by group order. KR-IC-5ea2f8 records that isogenies do move some prime-order curves over $\mathbb{F}_{q^3}$ into a GHS-vulnerable class (Tian 2023). The two rows are consistent only because the closure is limited to order-determined invariants.
  - *Conditions:* JMV's conditions are not spelled out in the map. I recall they involve GRH and endomorphism-ring level [recalled, unverified].
- **Weil descent and GHS (theorem on mechanism; KR-IC-5ea2f8, KR-IC-a4dd54).** Effective only for classified special fields and curves over $\mathbb{F}_{q^n}$.
  - *Does not rule out or address:* prime fields; the map records no prime-field instance. That $n=1$ has no proper subfield to descend to is [recalled, unverified] as a statement of the map.
- **Extension-field decomposition (heuristic and theorem; KR-IC-46d822, KR-IC-081a58, KR-IC-64659b).** These are positive results with thresholds $n\ge3$ and $n\ge5$. Diem's proven subexponential range excludes prime fields by the row's own statement. They are evidence about extension fields, not a barrier for $\mathbb{F}_p$.

**C. Index calculus over prime fields**

- **Naive Semaev index calculus (theorem under stated statistical assumptions; KR-IC-5931ee).** It costs at least as much as generic algorithms over $\mathbb{F}_p$.
  - *Rules out:* the naive formulation, conditionally.
  - *Does not rule out:* other factor bases. The row's statements on algebraic factor bases ("work only at small parameters") and on the Gröbner-free variant ("reported still worse than rho") are reports of observed performance, not theorems.
- **Summation polynomials are the framework (theorem; KR-IC-5a43e5).** This rules out nothing; it fixes the per-variable degree $2^{m-2}$.
- **Survey consensus (reported; KR-IC-9e610d, KR-IC-ae532f).** No known attack better than rho for general prime-field curves (2016), and no summation method has beaten rho at cryptographic size. This is an absence of published attacks, not a bound.

**D. Lifting**

- **Xedni and lifts to characteristic zero (proven per the map; KR-IC-cd159a).** Success probability is negligible, and "lifting-based ECDLP approaches inherit this obstruction".
  - *Does not rule out:* the trace-one p-adic lift, which is the separate special case in KR-RHO-53c89f.
  - *Caveat:* I recall the original analysis combining an asymptotic argument with experiments rather than a single theorem [recalled, unverified]; the row is abstract-read.

**E. Degree-of-regularity and solver limits**

These rows limit predictors of solver cost. None is a lower bound on solving cost, and all concern Weil-descended (binary or extension) systems, not $\mathbb{F}_p$.

- **First fall degree is structurally low (theorem; KR-IC-f5c584).** The trace morphism forces first fall degree 2 for descended $S_3$, and the heuristic linking first fall degree to degree of regularity is "unsafe for these systems".
  - *Rules out:* using that heuristic as evidence in either direction.
- **Last fall degree (theorem under stated conditions; KR-IC-fbdb61).** It is bounded independently of extension degree. Solving degree, last fall degree and degree of regularity are distinct, and semi-regular predictions do not describe descended summation systems.
  - *Rules out:* semi-regular cost estimates for these systems.
- **Subexponential binary claims (disputed; KR-IC-889857).** Neither established nor refuted; the map records "no consensus".
- **Gröbner refinements (theorem; KR-IC-0d2021).** These concern affine semi-regular sequences, and by KR-IC-fbdb61 that class does not describe descended summation systems.
- **Solver engineering (measured or reported; KR-IC-5765d2, KR-IC-8b9daa, KR-IC-f3da82, KR-IC-e847d1).** Gains are constant or polynomial factors on the decomposition step. The SAT row states the exponent is unchanged relative to rho.
- **Binary measurements (measured; KR-IC-1fcdbc).** Decomposition on prime-degree binary curves is much slower than rho, with experiments reaching only small $n$ and $l$.

**F. Structural**

- **Representation technique (theorem; KR-RHO-5b1c0a).** $p^{1.314}$ over $\mathbb{F}_{p^2}$, worse than rho.
  - *Scope:* $\mathbb{F}_{p^2}$ only; the row makes no prime-field statement.

## EVIDENCE GAPS

1. Is there any published lower bound for prime-field ECDLP outside the generic group model? The map records none; KR-RHO-13bf67 is model-scoped.
2. What exactly are the "stated statistical assumptions" in KR-IC-5931ee, and has anyone checked them at 256-bit parameters? The source is abstract-read; not settled by the cited work as recorded.
3. Is there a theorem, rather than small-parameter reports, covering non-naive factor bases over $\mathbb{F}_p$? Not settled by KR-IC-5931ee.
4. Is prime-field ECDLP provably subexponential or provably not? KR-IC-64659b lists it as open.
5. Is "lifting-based approaches inherit this obstruction" (KR-IC-cd159a) a proven statement for a defined class of lifts, or a summary inference? The source is abstract-read.
6. Do JMV's conditions (KR-RHO-755e35) hold for the specific curve under assessment, and is there published work showing that every known prime-field weakness class is isogeny-invariant? The sources are a secondary note and a bulk abstract.
7. Which algebraic invariant, if any, has been validated as a cost predictor for prime-field summation systems? KR-IC-fbdb61, KR-IC-f5c584 and KR-IC-0d2021 concern descended or semi-regular systems only.
8. How current are the cost figures?
   - The P-256 extrapolation uses a 2014 single-core rate (KR-RHO-825bca).
   - No academic GPU rho paper after 2019 was found, and GPU rates are community claims without peer review (KR-RHO-e7f98e).
   - Completion of the 116-bit BN report is unverified (KR-RHO-33f837).
9. How much of the record has been verified at source? KR-RHO-13bf67 rests on secondary sources, and most index-calculus rows are abstract-read. The map is "curated, not exhaustive", and its searches are dated 2026-09-26.
10. Are there published additive-combinatorics barrier results for ECDLP? The map has no such row beyond KR-RHO-5b1c0a.
11. What does the published record say on quantum algorithms and implementation-level attacks? The map has no rows on either; a classical $2^{128}$ estimate says nothing about Shor-type attacks [recalled, unverified].

## CITATIONS

Read depth is "abstract" unless noted.

- **KR-RHO-13bf67** — generic-group $\Omega(\sqrt p)$ bound. KN-LIT-011 (secondary), KN-TECH-005 (secondary), KN-LIT-006.
- **KR-RHO-6239aa** — parallel rho, $\sqrt{\pi n/2}$. KN-LIT-73f7e1 (full text), KN-LIT-012, KN-TECH-006 (secondary).
- **KR-RHO-93979e** — rigorous rho collision bounds. KN-LIT-369623, KN-LIT-6762f2.
- **KR-RHO-fb88e6** — negation map and fruitless cycles. KN-LIT-074c32, KN-LIT-c8e485 (full text), KN-LIT-5b238b, KN-LIT-a5c59c (full text).
- **KR-RHO-0528e7** — automorphism $\sqrt m$ factor. KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c (full text), KN-TECH-018 (secondary).
- **KR-RHO-825bca** — measured rho cost on P-256 and BN254. KN-LIT-a5c59c (full text).
- **KR-RHO-33f837** — prime-field records, 112 and 114 bits. KN-LIT-095, KN-LIT-a714d3 (full text), KN-LIT-24b9c7, KN-LIT-ff80da (completion unverified).
- **KR-RHO-e7f98e** — GPU rho state of the art. KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d (community), KN-LIT-a4b3d8 (community claim).
- **KR-RHO-898783** — interval DLP constants. KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34.
- **KR-RHO-46c2c6** — multi-target $\sqrt{2Ln}$ and lower bounds. KN-LIT-f47b10, KN-LIT-7e25f1.
- **KR-RHO-ea34b8** — preprocessing trade-off and $S T^2$ bound. KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964.
- **KR-RHO-7d93f6** — time–space bound for collisions. KN-LIT-fe066e, KN-LIT-b19b9b.
- **KR-RHO-fbd7b1** — grumpy giants. KN-LIT-fbe4e0.
- **KR-RHO-53c89f** — pairing and anomalous transfers as curve checks. KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089.
- **KR-RHO-755e35** — isogeny class shares order; random self-reducibility. KN-TECH-061 (secondary), KN-LIT-171 (bulk abstract).
- **KR-RHO-5b1c0a** — representation technique over $\mathbb{F}_{p^2}$. KN-LIT-ae78e5.
- **KR-IC-5a43e5** — Semaev summation polynomials. KN-LIT-001, KN-LIT-006.
- **KR-IC-5931ee** — naive prime-field index calculus negative. KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea.
- **KR-IC-9e610d** — 2016 survey consensus. KN-LIT-006.
- **KR-IC-ae532f** — practical algebraic records. KN-LIT-634555 (full text), KN-LIT-54c462, KN-LIT-006.
- **KR-IC-46d822** — Gaudry decomposition, $\tilde O(q^{2-2/n})$. KN-LIT-002, KN-LIT-006.
- **KR-IC-081a58** — Joux–Vitse $n-1$ decomposition. KN-LIT-673219 (full text), KN-LIT-022, KN-LIT-41fe5c.
- **KR-IC-64659b** — Diem rigorous subexponential results. KN-LIT-003, KN-LIT-65f76d.
- **KR-IC-955fd6** — symmetries and torsion in decomposition. KN-LIT-004, KN-LIT-bba0c6.
- **KR-IC-e2d81b** — degree-5 extension estimates (ecGFp5). KN-LIT-8aff72 (full text), KN-LIT-8146f9 (full text), KN-LIT-004, KN-LIT-bf1772.
- **KR-IC-5ea2f8** — GHS and cover attacks; isogeny into a GHS class. KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462.
- **KR-IC-a4dd54** — hyperelliptic index calculus, genus threshold. KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde.
- **KR-IC-cd159a** — xedni and lifting failure. KN-LIT-020, KN-LIT-021.
- **KR-IC-889857** — disputed subexponential binary claims. KN-LIT-005, KN-LIT-023, KN-LIT-fa346d (full text), KN-LIT-71b758 (full text), KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006.
- **KR-IC-f5c584** — trace morphism and first fall degree. KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607 (secondary).
- **KR-IC-fbdb61** — last fall degree and solving degree. KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513 (full text), KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029.
- **KR-IC-1fcdbc** — characteristic-2 decomposition slower than rho. KN-LIT-95d1e4, KN-LIT-19665f.
- **KR-IC-49c882** — quasi-subfield polynomials. KN-LIT-0a321c (full text), KN-LIT-4fe9d2 (full text).
- **KR-IC-0d2021** — Gröbner complexity refinements. KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0.
- **KR-IC-5765d2** — SAT/XOR solvers for decomposition. KN-LIT-92b022, KN-LIT-102cdb (full text), KN-LIT-6e036d (full text).
- **KR-IC-8b9daa** — Karabina symmetric formulation. KN-LIT-327949 (full text).
- **KR-IC-f3da82** — F4 trace reuse. KN-LIT-c137bd.
- **KR-IC-e847d1** — crossbred algorithm. KN-LIT-139.

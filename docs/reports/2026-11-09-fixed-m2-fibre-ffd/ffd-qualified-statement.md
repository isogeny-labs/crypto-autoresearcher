# Qualified degree-two first-fall statement and fibre kernel audit

Date: 2026-11-09. Source-only derivation and hand-worked finite-field example. No solver campaign, build, or computational replay. Read current main problem `problems/semaev-degree-two-fall-nonzero-bridge.md` and the old dossier Corollary2.2. This note is additive; it does not modify frozen records.

## 1. Three observables that must remain distinct

For a specified normalized coordinate **list** F=(f_i), write deg for squarefree Boolean degree.

1. A nonzero degree-two-to-affine linear combination of genuine quadratic inputs is a literal Petit–Quisquater-type nonzero fall.
2. A degree-two syzygy of the top homogeneous forms, modulo the explicitly chosen trivial syzygies, may map to the **zero** full polynomial. This is a different observable.
3. A new low-degree class in W2 modulo W1 requires the residual not already be available in the lower closure. The trace identity alone does not establish this when the list already contains affine equations.

The existing problem record documents this distinction and finite corrected examples. This note does not relabel its selected-row statistics as a universal first-fall theorem.

## 2. Exact characterization when every input is genuinely quadratic

Assume every nonzero listed f_i has degree exactly2, and delete literal zero input rows. Let

P:F2^r→B_≤2,   P(c)=Σ c_i f_i,
Q:F2^r→B_2^top, Q(c)=Σ c_i f_i^top.

At total source degree2 the multipliers must be constants. Therefore a PQ nonzero fall at2 exists **if and only if**

ker Q is not contained in ker P,

or equivalently span(F)∩B_≤1≠{0}. No positive source degree<2 can use any listed equation, so this gives exact PQ FFD2 under the stated convention. A zero full-polynomial syzygy is insufficient.

For the top-form syzygy convention used in the dossier, Koszul and individual field syzygies of all degree-two inputs start at degree4. Thus a nonzero kernel of Q gives a nontrivial degree-two top syzygy and exact syzygy-FFD2, even if P(c)=0. This conclusion depends on that exact list and trivial-syzygy convention.

The Semaev trace identity supplies a known nonzero coefficient vector c with

P(c)=ell0=Tr(X+Y)+Tr(a6/z²),   Q(c)=0.

The coefficient vector is nonzero because the field trace functional h↦Tr(h/z²) is nonzero. Hence:

- Under the all-genuinely-quadratic hypothesis, syzygy-FFD2 follows.
- Under that hypothesis **and ell0≠0 as a Boolean polynomial**, PQ-FFD2 follows.
- ell0=0 does not prove that PQ-FFD2 fails: another c in ker Q can still have P(c)≠0.
- ell0≠0 is therefore sufficient for this particular trace witness, not necessary for every possible degree-two fall.

Exactly when is the trace residual nonzero? It is zero iff V⊂ker Tr and Tr(a6/z²)=0. It is the constant1 iff V⊂ker Tr and Tr(a6/z²)=1. Otherwise it is a nonconstant affine polynomial.

## 3. Mixed-degree coordinate lists need additional conditions

If some input rows are affine or constant, a trace combination may use only those rows; its source degree can then be≤1. A nonzero residual already in W1 supplies no new degree-two closure class. Also, trivial top syzygies involving linear generators can occur at degree2, so the all-quadratic argument about trivial syzygies starting at4 no longer applies.

For a literal general-list PQ test at2, one must consider multipliers g_i of degree≤2−deg(f_i), require max_i(deg g_i+deg f_i)=2, require cancellation of the degree-two top part, and require Σ g_i f_i≠0. Proving that the **first** such degree is2 also requires ruling out a degree-one fall. This is presentation-sensitive and is not determined by the trace identity alone.

For a new-class filtration statement, a clean sufficient condition is a degree≤1 trace residual ell0 in W2 but not in W1. The all-quadratic input-list assumption ensures W1=0; mixed-degree lists do not.

## 4. Hand-worked diagonal Semaev example: row basis changes FFD2 to FFD1

Let H=F4=F2(w), w²=w+1. Let K=H(z), where z²=z+w. The quadratic is irreducible over H because Tr_(H/F2)(w)=1, so K=F16 and z∉H. Take V=H, a6=1, n=4,k=2 (the m=2 diagonal). The curve is nonsingular because a6≠0; a2 is arbitrary for S3. If a rational target abscissa is required, choose Tr_(K/F2)(a2)=1: Tr_K(z)=0 and Tr_K(1/z²)=1 then give the ordinary binary curve lift criterion.

Write X=x0+x1 w, Y=y0+y1 w, s_i=x_i+y_i, and

P0=x0*y0+x1*y1,
P1=x0*y1+x1*y0+x1*y1.

The four coordinate rows of S3 in the K basis (1,w,z,wz) are

f00=P0+P1+s1+1,
f01=P1+s0,
f10=P0+s0+s1,
f11=P1+s1.

This follows directly from E1=P+s² and E0=P²+w s²+1, using w²=w+1 and idempotent Boolean coefficients. Every row has genuine degree2. Their combination

f00+f10+f01=1

is nonzero of degree0, so this list has literal PQ FFD2 (and degree-two top-syzygy FFD). The trace residual is the constant1; indeed V=H has zero absolute trace in K, while Tr_K(1/z²)=1.

Now change the coordinate row basis to

(f10, f11, l, l+1),   l=f01+f11=s0+s1,

where l+1=f00+f10+f11. The change is invertible over F2: its four rows are independent combinations of the original four. Thus it is also a legitimate coordinate descent in another field basis, with exactly the same polynomial ideal.

The final two rows are genuine affine inputs, and l+(l+1)=1 is a degree-one nonzero fall. No listed row is constant, so no degree-zero fall occurs. This presentation has literal PQ FFD1. Its top forms for those two affine rows also have a nontrivial degree-one syzygy.

The exact ordinary polynomial LFD changes at these low caps as well. Both systems are UNSAT because they derive1. In the original list all inputs, including field equations, have degree2, so V1=0 while 1∈V2; hence LFD=2. In the transformed list no literal degree-zero generator is present, so V0=0, whereas the two affine rows derive1 in V1; hence LFD=1. This independently demonstrates why row-span invariance cannot be asserted for low exact LFD without a cap qualification.

This is a concrete counterexample to **basis-independent universal FFD2** wording for arbitrary coordinate presentations. It does not contradict the qualified all-quadratic Corollary2.2 or the trace identity. It also explains why row elimination can alter a first-fall statistic without changing higher-degree closure obstructions.

## 5. Exact qualification of equation-span invariance

If two degree≤2 input lists span the same F2 space, then W_D agrees for **D≥2**, because every input is eligible at those caps. It need not agree at D=0 or1: eligibility is based on each literal generator's degree, not on the degree of every possible linear combination.

For example, F=(xy+x,xy) and G=(x,xy) have the same row span. Yet W1(F)=0 and x∈W1(G). Common Boolean field equations do not change this mismatch at cap1. Thus assertions that row-span equality preserves *every* W_D or *all* small exact LFD values are too broad. It does preserve all obstructions and refutations at caps≥2; in particular the recorded LFD≥3 examples and the growing-degree lower-bound target are unaffected.

Similarly, field extension while keeping V fixed preserves the coordinate-equation span. The correct conclusion is equality of W_D for D≥2 for these normalized quadratic systems, not an unconditional statement about all low caps or FFD. This qualifies the extension argument in `definition-audit.md` and does not modify any historical source.

## 6. Independent check of the homogeneous fibre factorization

For the affine fibre after s=X+Y is fixed, the homogeneous field map is

L_s(X)=X⁴+(s²+z)X²+zsX.

The exact factorization is

**L_s(X)=X(X+s)(X²+sX+z).**

Proof: put P=X(X+s)=X²+sX. The right side is P(P+z)=P²+zP, which expands to the displayed linearized polynomial in characteristic2.

If s∈V is nonzero, 0 and s are distinct kernel elements in V. The other factor has either zero or two roots in K; if one root r lies in V, the other r+s also lies in V. Since z≠0, those roots cannot equal0 or s. Hence the kernel on V has dimension exactly1 or2, with dimension2 iff there exists r∈V satisfying r(r+s)=z. Over K, extra roots occur iff Tr_K(z/s²)=0; that trace condition alone does not ensure they lie in V.

If s=0, the kernel is {0,sqrt(z)}∩V and has dimension0 or1. Thus the general affine-fibre dimension bound≤2 is correct, and its worst case has an explicit multiplication condition.

A useful qualified refinement follows: if z cannot be written as a product of two **distinct** elements of V, every fibre has dimension≤1. The same selector-normal-form proof underlying the k+3 bound then yields d_LFD≤k+2 for SAT and UNSAT systems. This is a conditional upper-bound refinement, not a statement that such targets exist for every half-dimensional V or that the condition holds generically.

For V=H and z∉H, every product of two elements of V lies in H, so the extra-root condition fails; this independently agrees with the one-dimensional fibres used in the subfield SAT proof.

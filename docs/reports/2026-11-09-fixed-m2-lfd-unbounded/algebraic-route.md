# Fixed-m=2 Semaev: algebraic lower-bound routes and proved obstructions

Date: 2026-11-09. Scope: theoretical analysis only. No new solver runs, compilation, cloud submissions or certificate replay. The desired unboundedness theorem is NOT proved here. The lemmas below are derived from the explicit field equations; independent review is still required before promotion.

## Target and conventions

Let K=F_(2^n), V a k-dimensional F2 subspace with k=ceil(n/2), z nonzero, a6 nonzero. Let F be the Boolean coordinate descent of

S3(x,y,z)=(xy)^2+z^2(x+y)^2+zxy+a6,

where x,y lie in V, together with Boolean field equations. W_D is the fully saturated bounded-degree closure, not merely the initial Macaulay row space. The target is an infinite sequence of such systems F_j for which d_LFD(F_j) tends to infinity. The unsatisfiable route requires independently established unsatisfiability and 1 not in W_D for growing D.

Local sources inspected: `analysis/semaev-m2-last-fall-degree/theorem-dossier.md`, especially §§0–2, the Boolean/polynomial closure bridge, branching Lemma 1.3, exact reformulation, and Theorem 2.5. The identities below use those conventions. The dossier's semi-regular model is not used as a theorem.

## Derived lemma A: quadratic-extension subfield bases have refutation degree at most 3

**Statement.** Put n=2k and H=F_(2^k) inside K=F_(2^(2k)), and take V=H. For every z outside H and every a6, if the m=2 Semaev system has no Boolean zero, then 1 belongs to W_3(F), hence d_LFD(F)<=3. If z is in H and a6 is outside H, then 1 belongs to span F (hence degree at most 2). If both z and a6 lie in H, the system is satisfiable.

**Derivation.** For z outside H, write its minimal polynomial as

z^2=p z+q, with p,q in H and p,q nonzero.

Nonzero p follows from separability of finite fields; q is a nonzero norm. Write a6=A+Bz, with A,B in H. Set s=x+y and P=xy. The H-coordinate equations of S3 are

E1=P+p s^2+B=0,
E0=P^2+q s^2+A=0.

Their full F2 descents have the same equation span as the K descent, by an invertible change of output basis. Coefficientwise squaring of an H-valued Boolean polynomial is F2-linear in its coordinate polynomials: Boolean coordinate coefficients square to themselves. Thus every coordinate of E1^2 is in the F2-span of coordinates of E1. Consequently

L(s)=E0+E1^2=p^2 s^4+q s^2+A+B^2

has all of its coordinate equations in span F. These equations are affine-linear in the Boolean coordinates of s.

The homogeneous linearized map L0(s)=p^2s^4+qs^2 has precisely two roots in H:

s=0 and s=sqrt(q)/p.

Indeed, setting t=s^2 gives t(p^2t+q)=0, and squaring is bijective in H. Hence its F2 kernel has dimension exactly one. The affine equation L(s)=0 either is inconsistent, giving a constant linear combination of original equations immediately, or confines s to an affine line s=s0+c h with c in F2 and h nonzero.

Use an invertible affine change of Boolean s-coordinates to express these rank k-1 affine equations as eliminated coordinate constraints. Such affine changes preserve W_D. Eliminating their pivot variables does not add a degree penalty: replacing a quadratic f by its restriction differs by linear constraints times polynomials of degree at most one, so the restricted f lies in W_2(F). More generally, multiplication by each variable of an eliminated affine constraint through a degree-D monomial is available within W_D. A refutation in the quotient by these linear constraints therefore lifts at the same degree for D>=2.

After eliminating those coordinates, only the one bit c controls s. Fix c=0 or c=1. On each branch, P=x(x+s)=x^2+s x is affine-linear in the Boolean coordinates of x. E1 is therefore an affine F2-linear system. E0 equals E1^2+L(s), and L(s)=0 on that branch, so E1 alone determines consistency. If the original system is unsatisfiable, both branches are inconsistent affine systems and each derives 1 by linear combination. In particular each is refuted in W_2. The branching lemma with one bit and d=2 gives 1 in W_3 of the reduced system, and the linear-elimination lifting gives 1 in W_3(F).

If z belongs to H, all nonconstant S3 terms belong to H. For a6 outside H an F2-linear output functional annihilating H but not a6 gives a nonzero constant equation. If a6 belongs to H, set s=0 and x=y=a6^(1/4), which exists uniquely in H; then S3=x^4+a6=0.

**Implication.** A tower based on the entire quadratic-extension subfield is not a candidate for unbounded *unsatisfiable* fixed-m=2 LFD. The argument does not establish an LFD upper bound for all satisfiable subfield instances; that would require a separate ideal-generation argument. It also does not rule out arbitrary k-dimensional subspaces, polynomial subspaces, or perturbed subfield bases.

## Derived lemma B: field multiplication obstructs independent quadratic gadgets

The quadratic cross term between the x and y coordinate blocks is

H_z(xy), where H_z(t)=t^2+zt.

The kernel of H_z on K is exactly {0,z}. Suppose nonzero F2-subspaces U,W of V are intended to represent independently coupled gadget blocks and all x-U versus y-W quadratic coefficients are required to vanish. Then

H_z(u w)=0 for all u in U, w in W,

so U W is contained in F2 z. Fix a nonzero u in U. Multiplication by u is injective, and uW is contained in a one-dimensional subspace, so dim W<=1. Reversing roles gives dim U<=1.

Thus two nontrivial blocks with more than one coordinate cannot be made fully uncoupled in the complete Semaev descent by simply choosing an appropriate basis V. Arbitrary hard sparse bilinear systems cannot be inserted by declaring cross terms absent. A successful reduction must handle these extra equations or exhibit a degree-controlled projection that actually removes them.

This statement concerns the full descended cross term. Projecting away selected output equations can create an easier-to-encode system, but proving the projection hard does not prove the original augmented system hard: extra equations can drastically lower refutation degree.

## Derived lemma C: an unsatisfiable degree-D closure certificate needs growing quotient rank

**Statement.** Let F be a Boolean system whose generators have degree at most two. Assume D>=2 and 1 not in W_D(F). Put

Q=B_(<=D)/W_D(F), S_j=image(B_(<=j) -> Q), r_j=dim S_j.

If F is unsatisfiable, then

r_0<r_1<...<r_(D-1), and in particular dim Q>=D.

**Proof.** For each Boolean variable x_i, multiplication gives a well-defined linear map from S_(D-1) to Q: if two representatives differ by an element of W_D of degree at most D-1, closure implies that multiplying their difference by x_i stays in W_D. Extend this map arbitrarily to a linear map M_i on all Q. Let v=[1], nonzero by hypothesis. For every squarefree monomial of degree at most D, its class is the corresponding ordered product of M_i applied to v, because every intermediate multiplication acts on a class of degree at most D-1.

Suppose r_j=r_(j+1) for some j<=D-2. Then S_j=S_(j+1) and S_j is invariant under every M_i. It contains v, so repeated monomial multiplication shows every class of every monomial of degree at most D lies in S_j; hence S_j=Q.

For any f of degree at most j, the representatives x_i x_l f and x_l x_i f agree, and x_i^2 f=x_i f in the Boolean ring. Their degrees are at most j+2<=D. Thus M_i M_l=M_l M_i and M_i^2=M_i on the spanning space Q=S_j. Commuting idempotents over F2 are simultaneously diagonalizable, with joint eigenspaces indexed by Boolean assignments a. Since each original generator has degree at most two, F(M)v=[F]=0. Decompose the nonzero vector v into joint eigencomponents. Any nonzero component v_a satisfies f(a)v_a=0 for every f in F, hence f(a)=0 for all f. This is a Boolean common zero, contradicting unsatisfiability. Therefore all asserted rank increases are strict. Since r_0=1, r_(D-1)>=D.

**Use and limit.** This gives a necessary rank-growth condition for a certificate template intended to work at arbitrarily high D. A fixed-dimensional quotient template cannot certify unbounded unsatisfiable LFD. It is not itself a lower bound on LFD: it constrains certificates conditional on 1 not in W_D. It also does not mean that ordinary scalar dual functionals are impossible; a scalar functional annihilating W_D always exists by linear algebra. The obstruction applies to a scalar quotient whose *kernel itself is multiplication-closed*, a much stronger condition.

## Why straightforward determinant and elimination arguments fail

After s=x+y, the original system is bilinear-affine in the x and s coordinates. For fixed s it is an affine-linear system in x. Its inconsistency can be expressed using augmented-rank minors, and those minors can have degrees increasing with k. This is an upper-bound construction: it produces consequences. It does not establish that every refutation must form those minors, nor that lower-degree falls cannot replace them. LFD measures saturated derivability and allows arbitrary cancellations of products of newly obtained consequences.

Likewise, a high-degree elimination polynomial can have high degree merely because it has many roots. That does not force high LFD; even systems already given by a high-degree generator can have no late fall. A valid reduction must preserve proof degree in the direction needed for the lower bound.

Embedding a fixed certified instance into larger ambient finite fields while retaining the same subspace V does not yield a growing family. Coordinate descent after an injective field embedding has the same F2 equation span, up to redundant zero/linear-combination output equations, hence the same closure. It also leaves k fixed, so it does not satisfy k=ceil(n/2) at arbitrarily large n. Conjoining multiple unsatisfiable gadgets likewise has an immediate bounded-degree refutation from any one gadget.

## A precise remaining route

The strongest remaining candidate is a family of subspaces V_j genuinely mixing field coordinates, not a full subfield and not a block-diagonal gadget sum. For each j, one must construct an unsatisfiable instance and a quotient map

T_j:B_(<=D_j)->Q_j, D_j->infinity,

such that T_j(1) is nonzero, T_j annihilates every original descended equation, and ker T_j is closed under all allowed multiplication steps. Lemma C says rank Q_j must grow at least linearly with D_j. The maps must use the actual multiplication tensor H_z(v_i v_l), including all extra cross equations; finite-field elements cannot be replaced by independent indeterminates or nilpotents without a verified degree-preserving reduction.

A conditional theorem is immediate: existence of these quotient maps and independent unsatisfiability for an infinite sequence proves d_LFD>D_j. The missing result is their construction, not the closure-to-LFD bridge. No such infinite construction is supplied in this report.

## Primary-literature positioning

The local dossier defines the closure and LFD bridge used above. External discovery checked these primary sources on 2026-11-09:

- Huang, Kosters, Yeo, *Last fall degree, HFE, and Weil descent attacks*, https://eprint.iacr.org/2015/573.pdf — relevant definition and descent framework; no theorem from this paper is imported here beyond the locally stated conventions.
- Alekhnovich and Razborov, *Lower Bounds for Polynomial Calculus: Nonbinomial Case*, primary journal entry https://m.mathnet.ru/php/archive.phtml?jrnid=tm&option_lang=eng&paperid=403&wshow=paper — general hardness criteria require structural hypotheses; this does not establish that dense Semaev descent satisfies them.
- Mikša and Nordström, *A Generalized Method for Proving Polynomial Calculus Degree Lower Bounds*, https://arxiv.org/abs/1505.01358 — expansion-based lower-bound methods are a candidate toolkit, but no reduction from those hard instances into the fixed-m=2 Semaev family is known from this analysis.

These entries were checked at abstract/search-result level, not full-paper theorem verification. Accordingly no novelty or direct applicability claim is made. Full primary-paper review is a required next step before importing a named lower-bound theorem.

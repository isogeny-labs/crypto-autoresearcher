# KN-LIT-7606 (Corrigan-Gibbs, Henzinger, Wu, "The Structured Generic-Group Model"): body read

Date 2026-11-05. This answers step (2) of `LEAD-EXO-coordinate-revealing-oracles`. [pcc:unverified]
Tags: **[read: §, page]** for the paper's text, **[proved here]**, **[reading]** for an inference from the proof that the paper does not state.

**Source.** I read the author-hosted PDF at https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf (36 pages,
595,210 bytes, sha256 `82b40c27…6af66f`). TLS verification stayed on. The server sends an incomplete chain, so I
added its intermediate from the certificate's own AIA URL to the trust bundle. The text was extracted with pypdf.
eprint.iacr.org returned 403 to automated clients, and I did not work around that.

## What the model is

- **Structured label space** [read: Def. 2.2, p. 6]. This is a finite label set L with a *partial* binary function ⋆
  that makes (L, ⋆) a commutative monoid with unique factorisation.
- **Structured labelling** [read: Def. 2.3]. This is an injective σ: Z_n → L whose group oracle agrees with ⋆
  wherever ⋆ is defined.
- **Cost** [read: §2.3, p. 7]. Only group-oracle queries are charged. Evaluating ⋆ is free.
- **Constrained by star** [read: Def. 3.1]. A label is constrained if it appears in any defined ⋆ relation.
  δ is the fraction of constrained labels.

## The bound

**Theorem 3.2** [read: p. 8]. For every structured label space there is a distribution D over labellings such that every
T-query algorithm has

    DLAdv <= δn(3T+2)/q + (3T+1)²/q + 1/n,

where q is the largest prime divisor of n. In a prime-order group this gives T = Ω(min(√q, 1/δ)).

**With preprocessing** [read: Thm. B.1]. Allowing S bits of advice gives Õ(ST²/q + δT).

**Tightness** [read: §3, App. B.4]. For every δ there is a label space and an algorithm that reach this bound. So the bound [pcc:unverified]
cannot be improved without restricting the label space.

**Applications** [read: §5]. The paper applies the bound to:
- smooth integers (Cor. 5.1–5.3, a tight subexponential bound for index calculus in Z_p^*);
- small integers;
- smooth polynomials over F_2^n (Cor. 5.5–5.6).

**No elliptic-curve theorem in the body** [read: §5.3, p. 19]. The abstract says "elliptic-curve points". But §5.3 lists
"special-case algorithms for elliptic-curve discrete log [Smart]" among algorithms "we have not yet attempted to model", and the body contains no
theorem about elliptic-curve points. KN-LIT-7606's key claim of a stated elliptic-curve-point bound is therefore not supported by this version of the
text.

**Even the integer extension is open** [read: §7, p. 20]. The conclusion says that proving any non-trivial bound when ⋆ is
integer multiplication on all labels "appears challenging", because "an overwhelming fraction of labels are involved in ⋆ constraints, so the lower
bounds of Section 3 are useless here".

## What the proof actually uses

The proof of Theorem 3.2 [read: pp. 9–11] takes an arbitrary valid labelling σ₀. It fixes σ⁻¹ = σ₀⁻¹ on every
constrained label and draws every other label uniformly. It then runs Shoup's lazy simulation with the constrained pairs
pre-loaded as constants.

Unique factorisation, associativity and the form of ⋆ play no part in the argument. Only three properties matter:
1. a fixed set of at most δn group elements has a labelling known in advance;
2. the adversary may know it completely, because the bound holds for every A, including one that has σ₀ hard-coded;
3. the side information says nothing about any other label.

**Reading** [reading; not stated by the authors; [pcc:unverified]]. The same hybrid argument therefore bounds any side
channel whose answers depend only on (σ restricted to a fixed set F of δn elements) and on membership in F. Revealing the
discrete logs of the elements of F is the strongest such channel, and the proof already grants it. The bound is the same
δn(3T+2)/q + (3T+1)²/q + 1/n.

## Answer to the row's step (2)

**Covered, but trivially: a coordinate-defined factor base, or coordinates of a fixed δ-fraction.** Suppose the solver may read
coordinates only of points in a fixed set F, for example the ⌊√p⌋ points of smallest x. Then by the reading above it gains at most
what knowing log_P of every element of F gives, and T = Ω(min(√q, 1/δ)). For a factor base of size B, 1/δ = q/B ≥ √q whenever B ≤ √q.
So that access gives **no** advantage over the generic bound, and a larger F gives a bound below √q. This closes the
"coordinates of a fixed small set" reading of the class by theorem, up to the [pcc:unverified] reading.

**Not covered: index calculus.** Summation-polynomial index calculus needs coordinates of *arbitrary* points, namely
R = [a]P + [b]Q and the decomposition candidates. These points depend on the instance, so F is the whole group and δ = 1. The bound is then
vacuous, consistent with Lemma 3 of holant-h1-ggm-lemma-20261103 (two x-queries give the log). The authors make the same point for
integers (§7). No query-model closure exists for full coordinate access, and the class is decided only by time-bounded index-calculus
measurements against matched rho. That is the row's own fall-back, step (4).

**Consequence for KN-FIND-002 / KN-FIND-b7e091.** The augmented-oracle findings cited CHW as covering elliptic-curve
point structure. CHW has no elliptic-curve theorem. Its general theorem covers only structure confined to a fixed δ-fraction, which is
the opposite of what jet, net or x-oracles reveal (values at instance-derived points). Any statement that "CHW covers the augmented
oracles" should be withdrawn. This is input to review round BATCH-9f090a, joint J2. It is not a status change made here.

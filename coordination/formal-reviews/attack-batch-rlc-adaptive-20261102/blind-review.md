# Blind mathematical review: adaptive linear batching cancellation

Date: 2026-11-02 (UTC). Archival task: Conductor T-1373.

## Scope and permitted reads

This review rederives the mathematics from the statement supplied in the task:

1. For every field F and every rho in F, let e0(rho) = -rho and e1(rho) = 1. Then e0(rho) + rho * e1(rho) = 0 while e1(rho) != 0.
2. For every finite field F and fixed a,b in F with not (a = 0 and b = 0), the set of rho such that a + rho*b = 0 has cardinality at most one.

The sole preexisting file read was the expressly permitted joint review plan:

- Path: `/var/tmp/adaptive-batching-review-plan-20261102.md`
- SHA256: `399e4373e5a010728a87e8ac28b85b10d6daca9fd5e39243f6866645a44c4492`
- Access: read the complete file with `cat`, then computed its hash with `sha256sum`.

The plan contains identifiers and a prior expectation as part of its joint description. The derivations below do not rely on that expectation. No producer Lean, target YAML, source README, PR diff, sibling review, or prior verdict was opened. No external mathematics documentation was needed. No build, experiment, or repository/PR mutation was performed. This report is a mathematical review; it does not certify a formal implementation or machine check.

## Adaptive identity

Fix an arbitrary field F and rho in F. Substitution gives

    e0(rho) + rho * e1(rho)
      = (-rho) + rho * 1
      = (-rho) + rho
      = 0.

Also e1(rho) = 1 != 0, using the nontriviality axiom of a field. Hence the pair of errors is nonzero at every challenge, even though its weighted sum is zero. No finiteness assumption is used. In characteristic two, additive negation equals the identity, and the same calculation remains valid.

The cancellation identity in fact uses only ring identities. Its additional nonzero claim requires 1 != 0, so it extends to any nontrivial unital ring. A degenerate ring with 0 = 1 would satisfy the cancellation equality but fail the nonzero claim; it is excluded by the field hypothesis.

Verdict on the first statement: correct for every field and every challenge.

## Fixed nonzero pair: root set

Fix a,b in a field with not (a = 0 and b = 0). Define

    R(a,b) = { rho in F : a + rho*b = 0 }.

There are two cases.

- If b = 0, the hypothesis forces a != 0. The equation becomes a = 0, so R(a,b) is empty.
- If b != 0, multiplying a + rho*b = 0 by the inverse of b yields rho = -a/b. Conversely this value satisfies the equation. Therefore R(a,b) = { -a/b }.

Consequently the root set has exactly zero or one element. Over a finite field this gives the claimed cardinality bound at most one. The set-theoretic uniqueness assertion holds over infinite fields as well; finiteness is only needed for an ordinary finite-cardinality/probability formulation.

A proof using no division is equally direct: if rho and sigma are both roots, subtraction gives (rho - sigma)*b = 0. When b != 0, absence of zero divisors implies rho = sigma. The b = 0 case was already excluded from having any roots. Thus absence of zero divisors suffices for this uniqueness property; the field assumption is sufficient but stronger than necessary.

Verdict on the second statement: correct, with fixedness and exclusion of the zero pair essential to the stated use.

## Requested controls

### F2

In F2, -rho = rho. The adaptive construction gives:

| rho | e0(rho) | e1(rho) | e0(rho) + rho*e1(rho) |
| --- | --- | --- | --- |
| 0 | 0 | 1 | 0 |
| 1 | 1 | 1 | 0 |

In both rows e1(rho) is nonzero. For fixed nonzero pairs, all possibilities are:

| (a,b) | R(a,b) |
| --- | --- |
| (0,1) | {0} |
| (1,0) | empty |
| (1,1) | {1} |

These exhaust the three nonzero pairs and satisfy the bound.

### Zero pair

For a = b = 0, every rho is a root. Thus R(0,0) = F. Every finite field has q >= 2 elements, so its root cardinality q is greater than one. In F2 specifically, the root set is {0,1}. The excluded zero pair would invalidate the fixed-pair bound.

### ZMod 4 boundary

In the ring Z/4Z take the fixed nonzero pair a = 2, b = 2. Then:

| rho | 2 + 2*rho modulo 4 |
| --- | --- |
| 0 | 2 |
| 1 | 0 |
| 2 | 2 |
| 3 | 0 |

The root set is {1,3}, of cardinality two. This refutes the proposed fixed-pair bound if arbitrary finite rings are substituted for finite fields. The obstruction is the nonzero zero divisor 2, since 2*2 = 0 modulo 4. It is not a counterexample to either stated field claim. The adaptive construction still cancels in Z/4Z and retains e1 = 1 != 0.

## Adaptive versus fixed quantifiers

The fixed statement establishes

    for every fixed nonzero (a,b), at most one rho solves a + rho*b = 0.

The adaptive construction instead establishes

    there exist functions e0,e1 such that, for every rho,
    the pair (e0(rho),e1(rho)) is nonzero and its weighted sum is zero.

These statements are compatible. In the second one the coefficients change with the challenge. Substituting e0(rho) = -rho and e1(rho) = 1 produces the zero function of rho, rather than one fixed nonzero linear polynomial. The fixed-polynomial root bound cannot be applied to that challenge-dependent family.

Algebraic quantifiers alone do not specify chronological protocol behavior. To interpret a,b as fixed before a challenge, a protocol must bind their values before the challenge is drawn, or otherwise establish that their conditional values cannot adapt to that challenge. Conversely, the adaptive construction is a concrete algebraic choice available if both the construction and protocol permit the relevant challenge-dependent error values.

## Bridges to probability and protocol security

For a fixed nonzero pair over a finite field of size q, a uniformly sampled challenge yields:

    Pr[a + rho*b = 0] = 0       if b = 0,
    Pr[a + rho*b = 0] = 1/q     if b != 0.

The upper bound is therefore 1/q. This conclusion requires a uniform challenge over the whole field for the pair under consideration. If the pair is random, it suffices that, conditioned on the pair and any relevant prior transcript, the challenge is still uniform and the pair is nonzero. Independence of the fresh uniform challenge from the bound pair is a sufficient way to establish that condition.

For an arbitrary challenge distribution, the appropriate upper bound is its maximum point probability, because the root set has at most one point. If the challenge is sampled uniformly from a proper subset S, the bound is at most 1/|S| when S is nonempty, and can be zero if the unique root lies outside S. A 1/q claim does not follow from root count alone for such a distribution.

For the supplied adaptive functions, the combined error is zero on every challenge. Its acceptance probability under this equality-only test is one for every challenge distribution, while e1 is always nonzero. This probability calculation follows pointwise and needs no uniformity assumption.

To turn either calculation into a protocol claim requires a specified verifier equation and a connection between its coefficients and actual protocol errors. The fixed-pair argument additionally needs binding/ordering and conditional challenge unpredictability, coverage of the zero-pair case, and any repeated-test or multiple-attempt accounting. The adaptive construction must be shown realizable by protocol-valid actions; an algebraic error pair alone does not establish that. Neither supplied statement establishes a transcript theorem or a complete protocol security result.

## Mathematical verdict

Both supplied field statements are correct. The adaptive identity is valid over every field, including F2; the fixed nonzero linear expression has at most one root, and exactly one when b != 0. The zero pair and the Z/4Z example locate two concrete failures of weakened hypotheses. Challenge-dependent coefficients explain why adaptive cancellation and the fixed-pair root bound coexist. Probability bounds require a sampling law, and protocol security requires an additional connection to binding, transcript order, and realizable protocol behavior.

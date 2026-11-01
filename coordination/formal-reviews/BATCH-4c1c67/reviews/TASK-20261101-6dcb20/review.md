# BATCH-4c1c67 · J2 blind re-derivation · TASK-20261101-6dcb20

Frozen derivation. Before this commit I read only the task card and
`blind-input.yaml` (SHA-256
`af1591364529d043e386ebb6182092a52a5d2c8b5b3f6f1a155f3080b8556f42`, matches the expected value).
Everything below comes from the definitions in that file. `raw/fall_check.py` is my own exact
checker, written from scratch (output in `raw/fall_check.out`). It agrees with every hand result.

## Answers

| System | Placement | d_F | d'_F | d_F <= d'_F? |
|---|---|---|---|---|
| A | F | 3 | 2 | **no** (3 > 2) |
| A | F + S_fe | 3 | 2 | **no** |
| B | F | 3 | 2 | **no** |
| B | F + S_fe | 3 | 2 | **no** |

- **Recovery statement: proved** (Section 3). The bound deg(g_i f_i) <= v is needed: without
  it the statement is false on A (control 2).
- **Control 1** (only the lower bound "deg(g_i s_i) >= D for some i" is kept): d_F becomes
  1 + (least degree of a nonzero element of the ideal). This gives A: 3 / 2 and B: 3 / 2
  (F / F+S_fe). With S_fe the inequality then holds for *every* system, as a tautology, so the
  modified notion proves too much.

## 0. Facts used throughout

- (F0) F_2[X] is a domain, so deg(g s) = deg g + deg s for g, s != 0. A nonzero product with
  generator s has degree >= deg s.
- (F1) red is F_2-linear. Multilinear polynomials correspond one-to-one to functions
  F_2^N -> F_2, and red(p) is the multilinear representative of the function of p. So red(g s)
  is the function red(g)·red(s), and it depends only on red(g).
- (F2) red(X^a) = X^{supp a} has degree |supp a| <= |a|. Hence deg red(q) <= deg q, and if
  red(q) has a monomial of degree v then q has a monomial of degree >= v. A reduced polynomial
  has degree at most N, and its degree is N iff its function has odd weight.
- (F3) Division by S_fe: for each monomial X^a with a_j >= 2, the identity
  X^a = X^{a-e_j} + X^{a-2e_j}(X_j^2+X_j) holds, and the multiple of X_j^2+X_j has degree
  |a|. Repeating this until the remainder is multilinear writes
  p = red(p) + sum_j h_j (X_j^2+X_j) with deg(h_j(X_j^2+X_j)) <= deg p.

## 1. System A: F = (f1, f2) = (X^2 Y, XY + X) over F_2[X, Y]

### d_F(F) = 3

*Certificate at D = 3:* g = (1, X). The products are X^2Y (degree 3 = D) and X^2Y + X^2
(degree 3). Their sum is **X^2**: nonzero, degree 2 < 3.

*No fall below 3:*
- D = 1: by (F0) every nonzero product has degree >= 2 > 1.
- D = 2: g1 = 0 (otherwise deg >= 3), and g2 is a constant c. The sum c(XY+X) is 0 or has
  degree 2. Neither is a fall.

### d_F(F + S_fe) = 3

*Certificate:* (1, X, 0, 0) with sum X^2. An alternative is (1, 0, Y, 0) with sum XY.

*No fall below 3:* D = 1 fails by (F0). At D = 2, g1 = 0 and the other cofactors are constants
c2, c3, c4. The degree-2 part of the sum is c2 XY + c3 X^2 + c4 Y^2. Since the three monomials
are distinct, the degree drops below 2 only if all c are 0, and then the sum is 0.

### d'_F(F) = d'_F(F + S_fe) = 2

By (F1), red(f1) = XY is the indicator of the point (1,1) and red(f2) = X(Y+1) is the indicator
of (1,0). Every reduced multiple is therefore in {0, XY} or in {0, XY+X} respectively, and has
degree 2 or -inf. Field-equation products reduce to 0.

*Certificate at D = 2:* g = (1, 1) (with zero cofactors on S_fe). The reduced products are
XY and XY+X, both of degree 2. The reduced sum is **X**: nonzero, degree 1 < 2.

*No fake fall at D = 1:* no reduced product has degree exactly 1.

Since S_fe adds only reduced-zero products, the placement does not matter.

## 2. System B: F = (f1, f2) = (X1X2 + X3, X1X3 + X2) over F_2[X1, X2, X3]

### d_F(F) = d_F(F + S_fe) = 3

*Certificate at D = 3:* g = (X3, X2), with zero cofactors on S_fe. The products are
X1X2X3 + X3^2 and X1X2X3 + X2^2, both of degree 3. The sum is **X2^2 + X3^2**, of degree 2.
Adding the cofactors (0, 1, 1) on S_fe instead gives the sum X2 + X3.

*No fall below 3:* D = 1 fails by (F0). At D = 2 all cofactors are constants. The degree-2 part
c1 X1X2 + c2 X1X3 (+ c3 X1^2 + c4 X2^2 + c5 X3^2) is a sum of distinct monomials, so it
vanishes only if all c are 0.

The general form at D = 3 is g1 = X3 + a, g2 = X2 + b, which gives
sum = X2^2 + X3^2 + a f1 + b f2. The top-part syzygy l1 X1X2 + l2 X1X3 = 0 forces
(l1, l2) = c(X3, X2).

### d'_F(F) = d'_F(F + S_fe) = 2

f1 and f2 are already reduced. Their supports are
S1 = supp f1 = {001, 011, 101, 110} and S2 = supp f2 = {010, 011, 110, 101}. Both have weight 4,
so both have degree 2. Each sums to a nonzero vector (001 and 010 respectively), so neither is
an affine 2-flat.

*Certificate at D = 2:* g = (1 + X1, 1). The reduced products are red((1+X1) f1) = X3 + X1X3
(degree 2) and f2 (degree 2). The reduced sum is **X2 + X3**: nonzero, degree 1 < 2. The
unreduced product (1+X1) f1 contains X1^2 X2 and has degree 3, so this is not a true fall.

*No fake fall at D = 1:* a reduced product h·f_i of degree exactly 1 is an affine non-constant
function whose support lies inside S_i. Such a support has size 4, so it would equal S_i, but
S_i is not an affine flat. A degree-0 product would need support F_2^3, which is not contained
in S_i. The field-equation products are 0.

A cross-check by hand: the common zeros of F over F_2^3 are V = {000, 100, 111}, and the only
nonzero affine function vanishing on V is X2 + X3. The parity bookkeeping on S1 ∩ S2 then leads
to exactly the certificate above.

## 3. Recovery statement: **proved**

*Claim.* Let S = F followed by S_fe. Suppose (g_i) is a fake fall at degree v on the F part
(any S_fe cofactors are discarded; they reduce to 0). Suppose also that deg(g_i f_i) <= v for
all i. Then S has a fall at degree v.

*Proof.*
1. Let p = sum g_i f_i. Then deg p <= v, and r := red(p) = sum red(g_i f_i) by linearity.
   The fake-fall conditions give r != 0 and deg r < v.
2. By (F3), p = r + sum_j h_j (X_j^2 + X_j) with deg(h_j(X_j^2+X_j)) <= deg p <= v.
3. Take the cofactors (g_1, …, g_m, h_1, …, h_N) on S. In characteristic 2 their combination
   is p + (p + r) = r. This sum is nonzero and has degree < v, which gives conditions (b)
   and (c).
4. Condition (a), upper bound: deg(g_i f_i) <= v holds by hypothesis, and the S_fe products
   are <= v by step 2.
5. Condition (a), equality: some i has deg red(g_i f_i) = v. By (F2), deg(g_i f_i) >= v, so
   deg(g_i f_i) = v. ∎

*Illustration (B, v = 3):* the fake fall (X3, X2) satisfies the bound. Here p = X2^2 + X3^2
and r = X2 + X3, and the lifted fall is (X3, X2, 0, 1, 1) with sum X2 + X3. The script
confirms it.

*Consequence.* Whenever d'_F(F + S_fe) is attained by a fake fall that satisfies the bound,
d_F(F + S_fe) <= d'_F(F + S_fe). In A and in B every fake fall at v = 2 violates the bound:
- In A, a fake fall at 2 needs red(g1 f1) = XY, so g1 != 0 and deg(g1 f1) >= 3.
- In B, the bound at v = 2 forces constant cofactors, whose sum is 0 or has degree 2.

This is exactly why the inequality fails in all four rows of the table.

## 4. Inequality d_F <= d'_F

It **fails in all four cases** (3 > 2). The strict gap is witnessed by the fake falls (1, 1)
for A and (1 + X1, 1) for B. Both use reductions X^2 -> X that a true degree-2 computation
cannot perform. In A this comes from X^2Y -> XY; in B, the unreduced product (1+X1) f1 contains
X1^2 X2.

## 5. Nearby controls

### Control 1: condition (a) replaced by "deg(g_i s_i) >= D for at least one i"

I read this as dropping the upper bound. If the upper bound "<= D for all i" were kept, then
">= D for one" together with it is just "= D for one", which is the original definition, so
nothing would change.

With the upper bound dropped, let I = (S) and let m(S) be the least degree of a nonzero element
of I.

*Claim:* d_F^mod(S) = m(S) + 1, or 1 if I contains a nonzero constant.
- Upper bound: take q ∈ I \ {0} of degree m. For any D > m, add a Koszul syzygy
  (g_1 += t s_2, g_2 += t s_1) with deg t large. This leaves the sum unchanged and makes some
  product of degree >= D.
- Lower bound: a fall at D exhibits a nonzero element of I of degree < D.

The values:
- **A, F:** m = 2. Every element of I = X·(XY, Y+1) is a multiple of X. Since
  1 ∉ (XY, Y+1) = (X, Y+1), X ∉ I, and every other element of degree <= 1 fails to vanish on
  the line X = 0. So d_F^mod = 3 (witness X^2).
- **A, F + S_fe:** X = f1 + f2 + Y(X^2+X) ∈ I, and 1 ∉ I because (0,0) is a common zero.
  So d_F^mod = 2.
- **B, F:** the grevlex Gröbner basis is {f1, f2, X2^2 + X3^2} (the S-polynomials reduce to 0).
  The only degree-<=1 candidate vanishing on V(I) = {(t,0,0)} ∪ {(1,s,s)} is X2 + X3, which is
  a nonzero normal form, so it is not in I. So m = 2 and d_F^mod = 3.
- **B, F + S_fe:** X2 + X3 ∈ I, and V = {000, 100, 111} is nonempty, so 1 ∉ I.
  So d_F^mod = 2.

The script, with cofactors up to degree 4, finds exactly these upper certificates. Its "none"
rows at bounded degree are corroboration only; the lower bounds are the hand arguments above.

*Effect on the inequality:* with F alone it still fails (3 > 2 for both A and B). With
F + S_fe it holds (2 <= 2 for both). It holds for **every** F in that placement:
1. A fake fall at D yields r = red(sum) ∈ I + I_fe with r != 0 and deg r < D.
2. Adding a syzygy with t·(X_1^2+X_1) makes some product of degree >= D.
3. Hence d_F^mod <= d'_F unconditionally.

So the modification makes the inequality hold by construction. It no longer measures a
degree-D computation: it is ideal membership with unbounded cofactors. This is a
proves-too-much control, and it shows the upper bound in (a) is what carries the content.

### Control 2: recovery without the bound deg(g_i f_i) <= v, tested on A

**Refuted.** (1, 1) is a fake fall of F at v = 2: the reduced products XY and XY+X have degree
2, and the reduced sum X has degree 1. Yet F + S_fe has no fall at degree 2 (Section 1;
d_F = 3). The unreduced product f1 has degree 3 > 2, so the dropped hypothesis is exactly the
one that fails. B gives a second counterexample at v = 2 with the fake fall (1 + X1, 1).

## Unresolved obligations

- None for the mathematics asked.
- One interpretation is recorded: Control 1 is read as replacing all of (a), and the
  alternative reading is shown to be vacuous.
- The convention deg 0 = -inf is used, so that zero cofactors satisfy (a) trivially.

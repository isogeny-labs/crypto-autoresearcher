# SAT audit of the quadratic-subfield m=2 descent

Date: 2026-11-09. Theoretical source-only work. No build, experiment, certificate replay or cloud job. Sources and closure conventions are those in `definition-audit.md`, reconciled with main `dadfb1b2a5b6e8e6045f8547d26ec2b40d4ff81a` and `analysis/boolean-fall-certificates-20261104/THEORY.md`.

## Result

Let K=F_(2^(2k)), H=F_(2^k), V=H, z∈K\H, and a6∈K×. Let F be the **multilinear-normalized F2 coordinate equations** of S3(X,Y,z), X,Y∈H, and let Ftilde also contain all explicit Boolean field equations. Then

**d_LFD(Ftilde)≤3, for SAT as well as UNSAT instances.**

This is a new written derivation, not a Lean-checked theorem or a computationally tested statement. The key SAT step is an explicit low-degree ideal argument; the number of roots alone is not being used as an LFD bound.

## 1. Affine fibres and the solution count

Write z²=pz+q and a6=A+Bz over H. Since z∉H, p,q≠0. Set s=X+Y, P=XY. The coordinate-equation span is equivalently the coordinates of

E1=P+p s²+B,
E0=P²+q s²+A.

Boolean coefficient squaring preserves this equation row span, so

Q(s)=E0+E1²=p²s⁴+q s²+A+B²

is available as an affine-linear Boolean equation system in W2. Its homogeneous kernel is exactly {0,h}, h=sqrt(q)/p≠0. Thus Q(s)=0 is empty, or has precisely two solutions s=s0+u h, u∈F2.

In the nonempty case, Gaussian elimination expresses all but one Boolean s-coordinate in terms of u. After this elimination the original quadratic rows give substituted equations in W2: each subtraction has the form (known affine constraint) times an affine polynomial, so no cap above2 is used.

For fixed u=b, s is constant and

P=X²+sX.

The E1 equation is an affine F2-linear equation in X. Its homogeneous map X↦X²+sX has at most two roots (one if s=0). E0 is then redundant if Q(s)=0. Each fibre is therefore either empty, one point, or an affine line of two points. The full Boolean zero set Z has at most4 points.

## 2. Lift every quadratic ideal consequence at cap3

Write the reduced coordinate variables as (X,u), retaining the eliminated affine constraints. Let f be any multilinear polynomial of degree≤2 that vanishes on Z. Substitute the eliminated coordinates into f, obtaining f'; the difference f−f' is already derivable at cap2 from those affine constraints. It suffices to derive f'.

For b∈{0,1}, let e_b=u+b+1 and restrict the substituted equation set to u=b. It is an affine-linear system in the Boolean X coordinates. There are two cases.

**Nonempty fibre.** Choose independent affine equations l_(b,j)=0 for this fibre by Gaussian elimination. Each l_(b,j) is an F2 scalar combination of the restricted input equations. Since f'_b=f'|_(u=b) vanishes on the affine fibre, affine coordinate elimination and Boolean normalization give

f'_b=Σ_j h_(b,j) l_(b,j)

in the Boolean ring, with deg(h_(b,j))+deg(l_(b,j))≤2. One can take nonconstant l_(b,j) of degree1 and h_(b,j) of degree≤1; the remainder is identically zero because it vanishes on all assignments of the remaining free Boolean coordinates. This is exact Boolean function equality, not ordinary-field evaluation on a larger domain.

Let H_(b,j) be the same scalar combination of the un-restricted substituted quadratic equations. Then H_(b,j)∈W2 and H_(b,j)|_(u=b)=l_(b,j). Multiplication by e_b is allowed at cap3, and Boolean selector equality gives

e_b H_(b,j)=e_b l_(b,j)∈W3.

The latter has degree≤2. Multiplying it by h_(b,j), degree≤1, is again permitted at cap3. Consequently e_b f'_b∈W3.

**Empty fibre.** Its affine equations have a scalar combination equal to1. The same selector argument gives e_b∈W3. Since deg(e_b)≤1, multiplying by f'_b of degree≤2 stays within cap3. Thus e_b f'_b∈W3 in this case also.

Finally f'=e_0 f'_0+e_1 f'_1 in the Boolean ring. Therefore every degree≤2 element of the Boolean vanishing ideal of Z belongs to W3. Including the eliminated-coordinate repair proves the assertion in the full variable set.

## 3. Why a degree-compatible Boolean Gröbner basis has degree≤2 here

Assume Z≠∅ and |Z|≤4. Its ordinary polynomial vanishing ideal I(Z) contains every x_i²−x_i and is radical with quotient dimension |Z|. For any monomial order, the initial ideal contains x_i². Hence every standard monomial is squarefree, and the number of standard monomials equals |Z|.

A minimal squarefree initial-ideal generator of degree r must have all its proper divisors standard. For r≥3 it has at least2^r−1≥7 proper divisors, impossible when there are at most4 standard monomials. A nonsquarefree minimal generator is necessarily x_i², since it is divisible by such an existing generator. Thus every minimal initial-ideal generator has degree≤2.

Choose a **degree-compatible** order. The leading monomials of the reduced Gröbner basis are those minimal generators; all tails have no higher degree. Consequently the entire reduced basis G has degree≤2.

The normalized non-field-equation basis elements lie in W3 by §2. The explicit field equations are available at cap2. The strict quotient/polynomial bridge therefore places G inside V_(Ftilde,3).

Now take any f∈I(Z) of degree e. Degree-compatible Gröbner division supplies a representation f=Σ h_i g_i with deg(h_i g_i)≤e. Set D=max(3,e). Since each g_i∈V_3⊂V_D, successive monomial multiplication derives each term without exceeding D. Hence f∈V_D. This is exactly d_LFD(Ftilde)≤3, including all high-degree ideal consequences rather than only a low-degree profile.

For Z=∅, the degree≤3 refutation in `definition-audit.md` gives the same LFD upper bound. This completes the SAT/UNSAT statement.

## 4. Exact solution algorithm and bit-cost scope

Assume a standard polynomial-basis representation of K, and a supplied full-rank F2 basis/embedding for H. From the compact curve/target/subfield data:

1. Build the compatible (H,zH) coordinate conversion by binary Gaussian elimination.
2. Compute p,q,A,B and solve the affine F2-linear system Q(s)=0.
3. If nonempty, enumerate its two s values. For each, solve X²+sX=B+p s² as a binary affine-linear system; enumerate its at most two roots and put Y=X+s.
4. Verify the original S3 equation on every returned pair.

With schoolbook field operations and naive binary Gaussian elimination, these operations admit a polynomial bit-operation bound, conservatively O(k³) for a constant number of k- or2k-dimensional linear systems and their basis-map construction, and O(k²) working bits beyond the stored input/output maps. This is an algorithmic upper bound, not a benchmark or instruction-count measurement. Generating the full dense quadratic descent from compact field parameters by a naive separate expansion may cost O(k⁴) bit operations; that expansion is unnecessary for the solution algorithm above. Input encoding and matrix-construction details must be fixed before a tighter complexity claim or measured comparison.

The LFD theorem is not inferred from this fast solution algorithm; it is established separately in §§2–3.

## 5. Targets inside H remain a separate case

If z∈H and a6∉H, a coordinate functional killing H gives a nonzero constant equation, hence a degree≤2 refutation. If z,a6∈H, there is always at least the solution X=0, Y=sqrt(a6)/z.

The latter SAT subfamily is not covered by the ≤4-point proof. Its zero set can be much larger, and coordinate-basis descent to the larger ambient field merely adds dependent equations. One may enumerate all s∈H and solve the affine equation in X for each, obtaining a straightforward O(2^k poly(k)) enumeration bound; no polynomial-time total-output claim is made for that subfamily. The generic Boolean closure bound d_LFD≤2k+1 follows because at cap N+1, N=2k, every Boolean polynomial is eligible for variable multiplication, so W_(N+1) is the full ideal. This is only a coarse upper bound, not evidence of growing LFD.

Accordingly, **V=H with outside-subfield targets cannot yield unbounded LFD, even on satisfiable instances**. The same conclusion is not yet established here for z,a6∈H. It would be incorrect to generalize the outside-target theorem to all targets without addressing that remaining SAT subfamily.

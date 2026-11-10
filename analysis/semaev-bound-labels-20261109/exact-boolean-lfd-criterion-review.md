# Exact last fall degree from all-cap Boolean closure and evaluation

Date: 2026-11-09. Independent source-only derivation for the proposed bounded exact checker. No enumeration, closure computation, or tests executed.

## Exact input and convention

Let B=F2[x_1,...,x_N]/(x_i²+x_i), with canonical multilinear representatives. Let F be the exact supplied list of such Boolean polynomials. Let W_D be its fully saturated strict closure: inputs of actual degree at most D, binary linear combinations, and multiplication of a derived polynomial by a variable only when its actual degree is at most D-1. Allow last fall degree zero. The statistic is

    d_F = min { d>=0 : f in W_max(d,deg f) for every f in I=(F) }.

Input normalization is part of the binding. This is not an assertion that replacing an arbitrary unreduced polynomial input by its multilinear representative preserves low-cap eligibility or exact LFD.

## Evaluation identifies the ideal intersection

Enumerate the entire Boolean cube and retain exactly Z={a:F(a)=0}. Evaluation on Z has kernel I in the Boolean ring. One elementary proof uses the point indicators delta_a: if a is not a common zero, some input f_i satisfies f_i(a)=1 and delta_a*f_i=delta_a, so every function supported outside Z lies in I. Conversely every ideal function vanishes on Z.

For D>=0 let M_D=sum_(j=0)^min(D,N) binomial(N,j), and let r_D be the rank of evaluation on Z restricted to these monomials. Then

    dim(I intersect B_(<=D)) = M_D-r_D.

Since W_D is always a subspace of that intersection, equality of dimensions is equivalent to W_D=I intersect B_(<=D). Call cap D deficient if

    dim W_D < M_D-r_D.

A rank comparison is sound only after independently establishing both valid derivation and full saturation for W_D, and exhaustive Z for the exact input system. A containing closed space alone can establish a lower obstruction when one is missing, but cannot certify exact W_D dimensions or upper conclusions without derivation provenance.

## Exact formula

At cap N+1 every Boolean polynomial has degree at most N and is eligible for variable multiplication. Thus W_(N+1)=I; this cap is never deficient. The exact degree is

    d_F = 0                         if no cap is deficient,
    d_F = 1+max{deficient D}         otherwise,

where it suffices to check D=0,...,N+1.

For necessity, if D is deficient choose f in I intersect B_(<=D) outside W_D. Any proposed d<=D would require f in W_max(d,deg f), a subspace of W_D, contradiction. Therefore d_F>D for every deficient cap.

For sufficiency, let d be one plus the largest deficiency, or zero if none exists. Every checked cap e>=d has W_e=I intersect B_(<=e). For any multilinear ideal polynomial f, its required cap max(d,deg f) is between d and N+1, so that equality supplies its derivation. Hence d_F<=d. This proves the formula, including the nonnegative convention.

This is why an isolated nondeficient cap does not alone determine LFD: later eligible inputs and later falls may produce a new deficient cap. The formula uses the last deficiency, not the first successful cap.

## Edge cases

- Empty solution set: the evaluation matrix has zero rows and rank zero at every cap, so ideal-intersection dimension is M_D. The formula measures when every required consequence becomes available; a constant-one input already present at cap zero gives exact degree zero.
- Proper affine ideal whose affine generators are already available: every ideal polynomial is derivable at its own degree, so no cap is deficient and exact degree is zero. Do not replace this automatically by one.
- UNSAT affine inputs without a constant input can give a deficient cap zero and no later deficiency, hence exact degree one.
- Empty input or only zero inputs: I=0, every ideal-intersection dimension is zero, every W_D=0, and exact degree is zero.
- N=0: the Boolean ring consists of constants, and all input constants are eligible at cap zero. There is no deficient cap; exact degree is zero. Checking caps zero and one is harmless.
- Zero input rows and duplicate rows change neither ideal nor closure. Genuine row mixing can expose lower-degree inputs, so the exact supplied presentation must remain bound.

For the ordinary polynomial presentation consisting of these normalized inputs plus explicit Boolean field equations, the same exact statistic follows. Multilinear reduction of a polynomial has degree no greater than its original degree, and the field-equation correction can be derived without exceeding that degree. At degrees below two there is no field-equation correction. Conversely ordinary bounded derivations map into the Boolean closure at the same cap. This bridge does not authorize silently normalizing a differently presented original generator list.

The criterion is suitable for a bounded exact checker with exhaustive assignment evaluation and independently verified all-cap closure. It proves nothing about a source/domain whose equations were reconstructed incorrectly or whose invalid selector codes were silently removed.

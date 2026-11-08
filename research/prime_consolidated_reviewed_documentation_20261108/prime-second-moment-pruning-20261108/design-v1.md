# Conditional second moments in finite arity3/4/5 interval charts

Status: source-only mathematical design. No imports, implementation, enumeration, trials, cloud, IDs, Git or canonical mutation. Assumptions: verified prime p>3, nonsingular curve Y²=X³+alpha X+beta, finite target(a,b), B=2^s<p and interval root offsets0<=d_i<=M=B-1. Let h in{3,4,5}. All original source strata, signed multiplicities, rationality, target-overlap and witness obligations remain.

Scope is prospective interval-chart mathematics, not direct application to the retained six p17 coset coefficient cells (degrees8/16, not interval width). The old software contract's k3-sharing prohibition remains unchanged. Prior packets and exhausted producer/reserved independent budgets remain frozen. Sources: charts.py normalization and composition.py:155-205 norm/target/interval generation; range_corrected compiler.py:91-117 degree/width restrictions; previous reviewed higher-arity packet for trace and scope audit. Inspect as text only.

## Exact next norm coefficients
Write U=X^h+u X^(h-1)+j X^(h-2)+... . Finite normalized norm is A²-f B_poly²=c(X-a)U and A(a)=b B_poly(a). The cases are:

h3: A=X²+vX+A0, B_poly=q, c=+1, v=A1,q=B0.
  X² row gives j=a u+v²+2A0.
  A0=bq-a²-av, so j=a u+v²+2bq-2a²-2av.

h4: A=qX²+A1X+A0, B_poly=X+v, c=-1, v=B0,q=A2.
  X³ row gives j=a u+v²+alpha-2q A1.
  Target pivot remains A0=b(a+v)-a²q-a A1.

h5: A=X³+vX²+A1X+A0, B_poly=qX+B0, c=+1, v=A2,q=B1.
  X⁴ row gives j=a u+v²+2A1-2qB0.
  Target pivot remains A0=b(B0+aq)-a³-a²v-a A1.

All three retain u=a+2v-q². None of these identities divides by a target coordinate. They are necessary coefficient identities; the rest of the norm is not discarded.

## Exact conditional integer moment bounds
Let S=sum_i d_i and E=sum_{i<j} d_i d_j. Vieta gives

    u=-ht-S modp,
    j=binom(h,2)t²+(h-1)t S+E modp.

Indeed each t appears h-1 times alongside each d_i in pair products. Also2E=S²-Q with Q=sum_i d_i², as an INTEGER identity. Handle B=1 separately: M=0, S=E=0.

For M>0 and each integer0<=S<=hM define c=floor(S/M), r=S-cM, and d=floor(S/h), r0=S-hd. Then

    Qmax=c M²+r²,
    Qmin=(h-r0)d²+r0(d+1)²,
    Emin(S)=(S²-Qmax)/2,
    Emax(S)=(S²-Qmin)/2.

At S=hM use c=h,r=0; no extra nonzero remainder coordinate exists. Both extrema are attained. For Qmin, if two entries differ by at least2, transfer1 from the larger to the smaller: squares strictly decrease, until entries are balanced. For Qmax, transfer mass from the smaller of two interior entries to the larger until one hits0 or M: squares strictly increase, leaving at most one interior entry. Feasibility of both configurations follows from0<=S<=hM. All numerators are even because d_i² and d_i have the same parity.

These are exact extrema, NOT the exact attainable E set. For example h3,M>=3,S=3 has partitions(3,0,0),(2,1,0),(1,1,1), giving E=0,2,3; E=1 lies inside the bound interval but is unattainable.

Let W_h(S)=Emax-Emin and let R2_h(S)=min(p,W_h(S)+1). The residues of the ENTIRE necessary integer interval [Emin,Emax] form a cyclic interval of exactly R2_h(S) field values. They may wrap; canonical residue representatives are deduplicated, not counted multiple times. If W_h(S)>=p-1 this bound alone permits all field residues. Unattainable holes may still exist, but the interval bound cannot exploit them.

If hM<p the first moment S is uniquely determined by its residue. If hM>=p, a residue S0 admits several integer sums S=S0+lp in[0,hM]. The safe second-moment condition is the UNION of the allowed residue intervals over all such integer lifts. Choosing only S0 could discard valid charts. The shift binom(h,2)t²+(h-1)t S is unchanged modulo p by a lift, but the extrema can change. Integer-lift enumeration must be charged, or a separately proved equivalent union representation used.

## Affine moment coordinates versus nonlinear elimination
The change from support auxiliaries(u,j) to moment residues(S0,E0) is invertible affine over F_p:

    S0=-u-ht,
    E0=j+(h-1)t u+binom(h,2)t²;
    u=-ht-S0,
    j=E0+(h-1)t S0+binom(h,2)t².

Combining E0's formula with the previously reviewed trace change (v,u)->(z,w) is still affine if j is replaced by E0 and z=S0 is retained. Substitution into ALL quadratic field rows preserves degree<=2. This by itself replaces auxiliaries; it does not remove a free projected coefficient, reduce field count, or prove lower regularity.

Further projected-variable elimination is a different operation. For h5 solving A1=(j-a u-v²+2qB0)/2 is quadratic; eager substitution into other quadratic rows can raise degree4. Keep A1 as a determined auxiliary and retain its original equation if degree2 rows are required. For h4,q!=0 solving A1=(a u+v²+alpha-j)/(2q) is rational and requires a verified nonzero branch/inverse; it is not an affine substitution. Moving E0 into the projection and A1 out is bijective only when recovery is unique and all rows/inverses are checked. Existing source/bit layouts and transcript checkers do not automatically implement any of these role changes.

## Scoped coefficient recovery and the h4 zero fiber
Assume first that hM<p, so each S is a unique moment value. For each allowed E residue, j is fixed by the moment formula and v=(q²+u-a)/2.

h3: substitution gives the quartic

    4j=4au+(q²+u-a)²+8bq-8a²-4a(q²+u-a).

Its leading coefficient in q is1 after multiplying by4, hence it has at most4 field roots. This is a positive conditional elimination result: fixed first and second moments leave at most4 projected coefficient candidates. A producer must find ALL roots, with complete certified field-root extraction, and retain each q; replacing projected q solely by E would collapse distinct original projections. Charge quartic root finding and its completeness proof. All remaining source equations and witnesses still need checking.

h4,q!=0: each(S,E,q) determines a unique A1 through the rational formula and then A0. Keep the actual q inverse/nonzero branch. For q=0, v=(u-a)/2 and the row forces

    j0=a u+v²+alpha,
    E0forced=j0-binom(h,2)t²-(h-1)tS.

If this forced residue lies outside the allowed interval residues, reject the fiber. If it lies inside, ALL p choices of A1 remain candidates for subsequent rows. Never divide by q or discard this branch; E does not determine A1 there. The normalized h4 chart remains linear-B when q=0.

h5: each(S,E,q,B0) determines a unique A1 through the denominator2 formula and then A0. Original zero/constant/linear-B strata still constrain(q,B0), exactly as before. No nonzero condition on q is introduced here.

## Exact enumeration bounds and why moment-pair loops do not repay themselves
In the injective-S regime define A_h=sum_{S=0}^{hM} R2_h(S), the number of necessary residue moment pairs admitted by INTERVAL bounds. This counts a superset of feasible moments. Then

- h3: traversing all pairs requires A3 quartic-root problems and produces at most4A3 q candidates before remaining checks.
- h4: nonzero-q parameter candidates are exactly(p-1)A4 before remaining rows. Add p*N0 for the q=0 branch, where N0 is the number of S whose forced E is allowed;0<=N0<=hM+1.
- h5: the unstratified grid has p²A5 entries. Its zero, constant, linear B strata respectively have A5, (p-1)A5 and p(p-1)A5 entries, summing to p²A5.

For fixed h and growing B, the integer interval-width sum is Theta(B³). Upper bound: there are O(B) sums and widths O(B²). Lower bound: for S in[M/2,M], Qmax=S² and Qmin=S²/h+O(h), giving widthTheta(B²) forTheta(B) integer sums. Thus A_h=Theta(B*min(p,B²)) along injective-S parameter families, with constants depending on fixed h. In particular if p grows faster than B², A_h=Theta(B³). No equality between this interval-superset count and actual feasible moment count is claimed.

Even h3 then requiresTheta(B³) moment-pair root problems, versus a complete direct baseline with O(B²) group-operation candidates. h4/h5 still retain field factors. When residue bounds saturate, their nominal moment-grid reductions vanish rather than improve. These are enumeration/count boundaries, not conversion factors between root-finding, field and group-operation times. The complete deterministic pair/triple meet-in-the-middle baselines, output costs and fair comparisons are frozen in baseline-v1.md.

## Concrete next decision
Retain the exact sharp moment inequalities and conditional h3 quartic reduction as reusable necessary-condition results. Do NOT scale naive moment-pair grids solely because they replace one field coefficient by an interval. Useful continuation must either check the bounds cheaply on partial assignments without enumerating all pairs, exploit attainable-moment structure beyond these bounds at lower cost, or use further algebraic constraints to remove remaining field parameters. Any proposal must beat the workload of a complete direct/MITM baseline after preprocessing, output and certificate/witness costs are charged.

No general degree-of-regularity conclusion follows. The original coset cells need a separate support transport; interval moments cannot silently replace their predicates. Existing implementation prohibitions, all106+6/five-lead scope and attempts remain unchanged. Freeze independent written review before report/publication; no native execution admission is created.

# Telescoping range certificates and full-cube completion

2026-10-31. Unreviewed derivation and prospective integration design. No code implementation, solver call, fixed suite or benchmark. Outside the current authenticated-interface review. Uses the compressed range construction and incremental domain-coverage draft; neither is independently accepted here.

## A constant-multiplier refutation for every domain-empty prefix

For one prime-field block, put t=p-1 with one positions j1>...>jh. The authenticated generators are e_k=s_k-s_(k-1)*x_jk for 2<=k<=h, with s1 alias x_j1, and g_j=s_r*x_j for every zero position j of t, where r counts threshold one positions above j.

Let rho be any partial Boolean assignment, including an LSB-first prefix in any global variable order. Let L be the minimum decoded input value, obtained by setting unassigned input bits to zero. Suppose L>=p. At the highest position j where L and t differ, t_j=0 and L_j=1. Every threshold-one position above j has L=1. A one in L must already be fixed by rho, so rho fixes x_j and x_j1,...,x_jr all to one.

Consequently rho(g_j)=rho(s_r) and rho(e_k)=rho(s_k)-rho(s_(k-1)) for 2<=k<=r. This remains true if rho also fixes any state variables. Telescoping gives the exact identity

    1 = rho(g_j) - sum_{k=2}^r rho(e_k).

For r=1 the sum is empty and rho(g_j)=1 because both aliased input bits are fixed to one. Thus at most r<=h generators with constant multipliers +1 and -1 suffice. The selected restricted generators have degree at most one. This is an ordinary polynomial identity over F_p; no Boolean reduction is needed to establish this particular identity. Multipliers must be serialized canonically, with -1 represented by p-1, and zero entries for every unused generator in the existing adapter's required vector.

Concrete algebraic example: p=7, t=110, e2=s-x2*x1 and g0=s*x0. If a prefix fixes x2=x1=x0=1, the restricted identity is 1=s-(s-1). For p=5, either x2=x1=1 or x2=x0=1 directly restricts its forbidden generator to 1. These are hand-derived identities, not executed checks.

## Complete the transcript, preserve the full-cube checker

Require the solver's authenticated polynomial system to include the compressed range generators for every field block, with range states outside the projected bits. Preserve all original arithmetic equations and model projection. SAT may use comparator CNF for propagation. That solver CNF is not itself a completeness proof.

Construct the existing prefix trie from supplied learned-prefix records and supplied model projections, after normal record validation (or let the unchanged final checker perform that validation). Traverse the trie with the domain-minimum invariant from the prior draft. At each domain-empty cylinder, append a learned record with that cylinder's exact blocking clause and the telescoping multiplier vector above, then stop that branch. At a supplied terminal stop the branch. At a missing child that intersects the domain, return an uncovered assignment; do not claim completeness. At a full-depth nonterminal apply the same rule. Never invoke a solver or enumerate suffix assignments to complete coverage.

If relative-domain traversal succeeds, the original terminals plus newly certified domain-empty terminals cover the full Boolean cube: binary splits partition all assignments, and every stopped branch is now an explicit terminal. Call the unchanged adapter with the full-cube domain declaration (empty domain_cnf, aux_bound=None), the full authenticated polynomial list, and the augmented transcript. Its ordinary identity and model checks validate all records; its original full-cube coverage checker establishes completeness. A valid censored transcript stays declared censored under the existing status rule.

The empty domain passed to this checker is a truthful full-cube proof scope. Range restrictions are in the polynomial generators, and skipped cylinders are covered by explicit polynomial identities. It is not a claim that the SAT solver used empty bootstrap CNF, nor an alteration of its recorded execution. Preserve the actual solver CNF and unmodified raw solver answer as separate inputs, and record the augmented answer as a distinct compiler artifact.

## Trust and accounting

The new completion generator need not become trusted completeness logic: a bad identity, clause, witness or incomplete cover is rejected by the unchanged checker. Public polynomial/circuit authentication remains essential; the existing generic adapter alone does not authenticate intended mathematics. This construction does not remove that dependency. It also does not ensure the SAT solver finishes or finds inexpensive arithmetic refutations.

With T trie nodes, there are O(T) branch boundaries, hence O(T) possible added certificates; each certificate uses at most h nonzero constant multipliers for its chosen field. There is no suffix-space expansion in this construction. Existing vector serialization may still cost the full generator count per certificate, and the old verifier restricts all generators and checks all multiplier entries. Charge those operations, generator authentication, trie construction, CNF construction, transcript copying, model checks and signed reconstruction. The bound is a derivation, not measured performance or a regularity claim. The degree-at-most-one observation applies only to these restricted range refutations.

## Next fixed contract

Compare three paths on identical complete projected sets: full-cube polynomial-range control; comparator-CNF search plus certificate completion checked by the unchanged full-cube adapter; and, only if still useful, the separately authenticated relative-domain checker. Freeze exact input and projection alignment first. Challenge missing recurrences, wrong generator indices, wrong signs/modulus, altered bit ordering, partial state assignments, r=1, multiple fields, interleaved bit positions, a projection boundary through a block, omitted valid projection, forged native UNSAT, and genuinely censored solver answers. Independent tests must verify the actual serialized certificates with the current adapter. No implementation or run is launched by this note.

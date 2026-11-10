# Independent review: exponential size barrier for truncated UNSAT quotients

2026-11-10. Source-only proof review; no execution of closure computations or experiments.

Let B be the Boolean polynomial ring in N variables, D>=2, and let pi:B_{<=D}->Q be surjective. Put U=ker(pi). Assume U contains every input equation, each input has degree at most D, and x_i u belongs to U whenever u belongs to U and deg(u)<=D-1. Assume pi(1) is nonzero and the supplied system is independently known to be UNSAT.

**Confirmed conclusion:** dim Q >= 2^(D-1). In particular, a parameter-uniform growing-cap certificate cannot retain a fixed or merely polynomial-in-D quotient dimension. This is a necessary condition, not a construction or an LFD lower bound by itself.

Choose graded lexicographic order on the squarefree monomials, inherited from the ordinary polynomial term order. For nonzero f in U with leading monomial m of degree d<D, and variable x_i absent from m, the leading monomial of the Boolean product x_i f is x_i m. Indeed, every term containing x_i loses the extra degree on Boolean reduction, so has degree at most d, whereas x_i m has degree d+1. Among the terms not containing x_i, ordinary multiplicativity preserves their order. No other monomial can reduce to x_i m. Hence the initial monomial set of U is upward closed under squarefree multiplication within degree D.

The complement, the standard monomials, is a downset. Ordinary finite-dimensional row elimination shows that these monomials form a basis of B_{<=D}/U. In particular their number equals dim Q; this argument does not claim that U is a global ideal.

For completeness, let Q_e=pi(B_{<=e}). A plateau Q_e=Q_{e+1} with e<=D-2 would propagate to all of Q. To see propagation, replace degree-(e+1) representatives by degree-at-most-e representatives modulo U, multiply the difference one variable at a time while its degree is at most D-1, and induct on the degree. Consequently every quotient vector admits a representative of degree at most e. Kernel closure then defines each variable action on all Q. The actions commute and are idempotent because representatives of degree at most e can be multiplied twice within cap D. The cyclic vector pi(1) generates Q, so this is a cyclic module for the full Boolean algebra. Each input annihilates pi(1), hence by commutativity the whole module. UNSAT means the Boolean input ideal is the unit ideal, contradicting pi(1)!=0.

Thus Q_{D-2} is a proper subspace of Q_{D-1}. Degree-compatible elimination supplies a standard monomial m of degree D-1. Every divisor of m is standard by the downset property. There are exactly 2^(D-1) such divisors, proving the claim.

Important boundaries:

- q must mean actual rank of pi; an arbitrary declared codomain dimension is not the certificate dimension.
- A merely degree-sorted arbitrary ordering is insufficient for the leading-product argument; a multiplicative degree-compatible term order such as graded lex is sufficient.
- All generators used in the UNSAT assertion must be admitted at this cap. An excluded high-degree generator cannot justify the module contradiction.
- If the system has solutions, quotient evaluation modules are legitimate. The same rank conclusion holds if an independent argument excludes a global Boolean quotient of this dimension, for example a rank excess over the true solution count combined with the plateau argument. UNSAT is the simplest stated hypothesis.
- The exponential lower bound concerns certificate representation size at cap D. It neither proves that such certificates exist nor proves degree growth for Semaev inputs.

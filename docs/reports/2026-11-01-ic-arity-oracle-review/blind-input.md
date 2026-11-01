# Independent real-expression analysis

Read only this file, your own task card, and AGENTS.md. Work in the isolated
input directory supplied by the Coordinator; it must contain no Git history,
producer source, candidate answers, receipt, other reports or parent transcript.
If isolation or independence is absent, stop and report the exact missing gate.
No broad repository or Internet search for these expressions is permitted.

Let m, b, k be real numbers with m >= 2, b > 0 and k >= 0. Define

```text
A(m,b) = max(0, 1 - b*(m-1))
U(m,b) = max(0, 1 - b*m) + b
F(m,b,k) = max(A(m,b) + k*b, 2*b)
G(m,b,k) = max(U(m,b) + k*b, 2*b).
```

Independently derive the lower envelope over b > 0 of each expression for all
allowed m,k. Distinguish a minimum from a nonattained infimum; give every
parameter condition, equality case, boundary and counterexample to an
incorrect unrestricted statement. Determine exactly when each optimized value
is below, equal to, or above 1/2, and compare F and G pointwise.

Analyze the parameter classes k >= m/2 and k = m-1 without being supplied a
candidate conclusion. Check m=2,3,4,5, the parameter breakpoints you derive,
and large-m limits symbolically. Explain the difference between a pointwise
inequality and a statement uniform along m=m(n), b=b(n), k=k(n).

Optional interpretation to audit: with r>1, let B=r^b. One semantics returns
all decompositions, another returns at most one; the expressions are proposed
normalized exponents. Assumptions would be needed for yield, required
independent relations, linear algebra and oracle cost. State precisely what
these formulas alone cannot establish about probability, rank, actual
algorithms, finite costs, memory or growing-arity terms such as m! and r^o(1).
No factual source claim beyond these supplied mathematical definitions is
needed. Do not seek the producer's derivation.

Write a complete derivation or explicit unresolved obstruction, and a truthful
read/session/model/effort attestation for joint B. No scientific runs,
benchmarks, solver sweeps, builds, source edits or official status changes.
Remain blind throughout this task. Any later unblinding requires a separate
prospective written task after your output is sealed and archived.

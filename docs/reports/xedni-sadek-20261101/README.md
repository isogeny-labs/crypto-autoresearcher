# Xedni: dependency-bound audit and conditional repair

2026-11-01. Archive owner: TASK-20261101-fbd859. Question: RQ-XEDN-3bfe2e.
Hypothesis: H-XEDN-292264 (proposed, not independently reviewed).
Related: [PR 1986](https://github.com/isogeny-labs/crypto-autoresearcher/pull/1986),
[issue 1985](https://github.com/isogeny-labs/crypto-autoresearcher/issues/1985).

## Observations and provenance

The earlier interactive audit found an invalid prime-divisor inference in
Sadek's *On dependence of rational points on elliptic curves*, Theorem 4.4
proof. Source: https://arxiv.org/pdf/1605.02961 (v1, 2016-05-10);
published counterpart: https://mathreports.ca/download/1173/ (2016, 38(2),
75-84). Provenance: retrieved; verified_by: codex-root, 2026-11-01. The
published page 83 and preprint page 10 both contain the step. These are the
same work, not independent corroborations. No author correction was located
in the limited earlier search; absence of a result does not prove absence.

The theorem assumes GRH, non-CM E/Q, all mod-prime Galois representations
surjective, E(Q) free of positive rank, and a supplied full basis. It excludes
j-values 256(t+1)^3/t, t^2+1728, -4t^3(t+8), 1728-t^2 and 1728 +/- 2t^2
for rational t where defined. The inputs are already rational P and subgroup
Gamma, not arbitrary external residues. The proof passes from |n_j| <= C to
ell <= sqrt(C) for a prime divisor ell of n_j. Its explicit cutoff uses this
step. No coefficient-discovering lift construction is supplied.

**Derived:** for nonzero n_j the available implication is ell <= |n_j| <= C.
In rank one P=[3]P1 gives C=3 by bilinearity of the height pairing, while
ell=3 violates ell^2 <= C. This disproves the inference, not the theorem's
conclusion or the underlying local-to-global principle. Independent full-proof
review is still required. Zero has no finite set of prime divisors to enumerate.

The historical command and its actual raw output are preserved in
`prior-command.txt` and `prior-output.txt`. They are imported conversation
evidence, not a harness RUN, preregistered experiment, or new independent replay.
The earlier final answer reformatted the executed command/output; this import
uses the actual tool invocation and dictionary output instead. Historical
Python version, seed, CPU usage and dirty-tree state were not captured. No
timing is inferred from that omission.

## Conditional arithmetic repair and open hypothesis

**Derived conditional lemma:** let integers B>=2, r>=1, K>=1 satisfy
2<=ell<=B and 1<=k<=K. Then

    (ell^2-1)(ell^2-ell) ell^(2(k+1)r+4k)
      <= (B^2-1)(B^2-B) B^(2(K+1)r+4K) = M_star.

Every factor is positive and monotone on this domain; increasing the exponent
is valid because the base is at least two. This algebraic statement does not
require ell prime. `test_bounds.py` implements the two integer expressions
and software controls, including invalid-domain and tight-equality cases.

**Proposed H-XEDN-292264:** a complete explicit local-test cutoff can be
reconstructed using a rigorously certified integer B >= max(2,C), admissible
integer K, and M_star, after independently repairing the field-selection and
exceptional coefficient cases. We do NOT replace the published theorem with
this conditional lemma. In particular, ceiling logarithmic lower bounds is
necessary but is not by itself a proof of admissible homothety/field choices.

**Proof-search map:** baseline is the original degree expression, not a lift
search. The observable collision is a small coefficient bound with a prime
coefficient near its upper endpoint. The constructive change is only an
integer majorant. Quantifiers are universal over the conditional integer
domain, not over all lifts. A proves-too-much control must refuse n_j=0 and
must handle n_j=+/-1 without silently taking a maximum over an empty set.
The method's ceiling is a justified test cutoff for supplied rational data.

### Next bounded check (proposed, not launched)

Freeze B in 2..64, r in 1..4, K in 1..8, all primes ell<=B, and 1<=k<=K.
Check exact integer domination, with ell=B,k=K equality controls when B is
prime and explicit invalid-input controls. One worker; no randomness; stop
after the finite grid or a recorded infrastructure failure. Record every tuple,
both integer values, counters, versions, wall/CPU/RSS, and exceptions. A single
valid-domain violation falsifies the implemented inequality; zero violations
does not certify the number-theoretic bridge. Obtain the repository's frozen
protocol, checkpoint and run admission before a scientific sweep. These
parameters are not a change to an existing frozen Xedni trial.

## Certificate, recovery and costs

| Stage | Required input or certificate | Cost/status |
| --- | --- | --- |
| Lift construction | External residues and compatible rational points | Not implemented by this source; search/failures unknown |
| Basis/height preprocessing | Full saturated basis and rigorous upper C | Must be charged; not measured |
| Arithmetic majorant | Certified B and admissible integer K | Exact integer exponentiation; bit lengths grow with K,r,log B |
| Local sieve | Justified test-prime range and subgroup membership | Enumerate and test every required prime; no runtime measured |
| Coefficient search | Integer witness in the rational group | Naive box has at most (2 floor(C)+1)^r candidates; rational bit costs additional |
| Verification/recovery | Exact rational group identity and reduction compatibility | For aP+bQ=O and Q=[x]P of order N, unique recovery needs gcd(b,N)=1 |

Construction, rejected candidates, verification, recovery, preprocessing,
memory and setup reuse are unmeasured. The conditional majorant is not a full
cost bound. Finite-prime successes alone are not accepted dependencies;
retain exact rational verification as the acceptance gate.

## Comparison and obligation status

The earlier supplied V2 baseline remains 68 doubling-section checks with one
residue per prime; 1,944 rational fits from 24 finite point pairs, 20 having
finite-field coefficients in [-8,8], zero certified rational dependencies
in that box. Those are historical observations, not rerun here.

| Obligation | Status | Next evidence |
| --- | --- | --- |
| False square-root implication | Producer-derived counterexample | Independent source/definition review |
| Conditional integer domination | Producer proof and software tests | Independent derivation |
| Full corrected prime cutoff | Unknown | Admissible integer k, field choice, zero/unit handling |
| Arbitrary-residue lift construction | Unknown | Explicit candidate construction and coverage certificate |
| Useful dependency discovery | Unknown | Exact rational relation with recovery conditions |
| Computational advantage/scaling | Unknown | Complete measured paired cost study |

Typed path: supplied E/Q points --reduction at good p--> E(F_p) points;
no reverse construction is supplied. The weakest missing edge is compatible
dependent-lift construction, not reduction evaluation.

## Repository integration and literature-first check

Read the existing Cheon certificate report at
`analysis/xedni-cheon/20261007-certificates/REPORT.md` and inspected
`knowledge/frontiers/ecdlp/`, including KR-IC-cd159a. GitHub search for Sadek
and open Xedni PRs was also used. The KB MCP search endpoint was unavailable;
this fallback is not an exhaustive novelty audit. No existing canonical
frontier graph or scientific status changes: this adds a source-audit problem
and proposed repair, not evidence of a different attack cost. The historical
Cheon diagram remains historical and unmodified. No production target is used.

The unresolved proof bridge is tracked in
`problems/xedni-sadek-explicit-cutoff.md`. Source, diagram and PDF are together;
the SVG itself is editable. Validation and archive custody are separate from
independent scientific review. No EV/DEC record or approved EXP is created.

Requested deliverables: PR and tracked hypothesis are this snapshot's scope;
new lift trials and full theorem repair remain open. See `VALIDATION.md` for
actual software checks and unavailable repository-wide checks.

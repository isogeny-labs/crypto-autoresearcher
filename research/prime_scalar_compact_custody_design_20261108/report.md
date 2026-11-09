# Arbitrary-subcube certificates and compact validation custody

Status: written derivation and design with independent static critique and corrections disposed. No candidate,
oracle, metadata phase, replay or empirical comparison was executed.

The mathematical construction extends the fixed-prefix scalar certificate to
any restriction set S. If a generator f becomes c≠0, successively substituting
variables in S gives explicit multipliers h_r with
f-c = sum_r (x_(i_r)-a_(i_r))h_r. For D=deg(f), each nonzero multiplier has
degree at mostD-1, so the conditional refutation has degree at mostD.
The fixed-value equations are essential to that conclusion.

The Boolean subcube indicator chi instead gives chi*f=c*chi modulo Boolean
field equations. Its displayed product degree is bounded by D+|S|. The
corresponding clause excludes the whole certified subcube and preserves every
full root. Auxiliary literals must be retained when the witness depends on them;
a short clause does not itself prove that a projected assignment has no witness.

One deletion pass, using a fresh restriction of the original generator for each
test, yields an inclusion-minimal scalar-constant restriction in at most|S|
tests. A failed deletion cannot become successful after further deletions,
because restricting a constant more finely preserves it. This is not minimum
cardinality: at the zero assignment, f=1+sum_e product_(i in e)x_i becomes
constant exactly when the fixed-variable set hits every support e. The draft
therefore identifies both a practical bounded search family and its optimization
limit. No new general implicant-shrinking principle or global degree-of-regularity
bound is claimed.

Validation custody is a separate prerequisite. The previous preparation stopped
at the unchanged4MiB diagnostic allocation before any metadata phase, leaving
manifest and builder/audit receipts absent. The proposed representation retains
one ref map, explicit validated deltas, immutable commit/claims-tree results and
actual command-output custody. It must reconstruct both every semantic map and
any exact raw output it claims to preserve. Repeated claims-tree content can be
represented once without changing the native highest-epoch/conflict decision,
conditional on successful object reads, identical local records, stable parser/configuration and the same relevant time predicates. This is not equivalence of runtime successes, command failures or deadlines.

The byte formula counts initial state, deltas, unique tree entries, unique raw
blobs, headers and reserved failure custody. Arbitrary churn can require full-size
deltas; the design must refuse before crossing the existing cap. It makes no
promise that all future repositories fit. This source/design step introduces no
runtime helper or retry.

Next mathematical work is to identify cheaply certifiable projected-variable-only
restriction sets in the actual quartic, membership-augmented and quadratic-lift
encodings, while preserving complete projected sets, chart coverage, witness
reconstruction and certificate checking costs. The reviewed compact-custody
specification can support a separately admitted implementation if its proof and
byte accounting survive critique. Neither path consumes the reserved independent
scientific slot or resets the original two exhausted producer slots.

A symbolic order-dependence example makes the distinction concrete. For
f=1+xy+xz at assignment(0,0,0), fixing x=0 gives constant1. Fixing y=z=0
also gives constant1, and neither y nor z can then be deleted. Deleting x
first from the full assignment therefore yields{y,z}, whereas deleting y
and then z first yields{x}. Both results are inclusion-minimal; only the
latter has minimum cardinality for this example. Here D=2. With S={x},
the telescoping identity is f-1=x(y+z), and the conditional certificate
is1=f-x(y+z), with product degree2. This is hand-derived algebra, not an
executed fixture or benchmark.

The independent critic found no mathematical defect under the stated hypotheses
and confirmed the native fence's content/epoch/conflict premise by source
inspection. Three custody qualifications were incorporated: strict reversible
ref-name handling, common boot/clock-domain timing with the native300-second
freshness check, and conditional rather than full runtime equivalence. Concrete
writer implementation, crash handling and byte-budget enforcement remain
future obligations. The completed packet is a reviewed written design; no
software correctness or measured performance acceptance is implied.

Sources: research/prime_scalar_compact_custody_design_20261108/mathematical-note.md
(explicit identities, degree bounds and deletion proof); specification.md and
proof-obligations.md in the same directory (custody premises and reconstruction);
independent-static-review.md (exact input hashes and correction disposition).
Native design decision DEC-20261108-17a496; source/design TASK-20261108-b69b89;
snapshot TASK-20261108-d60cc4. Prior implicant work: Deharbe, Fontaine,
Le Berre and Mazure, Computing prime implicants, FMCAD2013,
https://www.verit-solver.org/papers/fmcad2013.pdf. This attribution locates
prior shrinking/minimality work; no novelty claim is made here.

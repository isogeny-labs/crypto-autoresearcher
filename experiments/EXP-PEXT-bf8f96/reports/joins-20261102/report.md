# Direct streaming class × T-coset × projective-structure join

2026-11-02 · EXP-PEXT-bf8f96 · H-PEXT-c3a11d · TASK-20261102-d8d2b5

The arithmetic interface now streams exact ordinal ranges of a supplied ordered model list crossed with every canonical rational-T coset and projective structure. It skips structure prefixes by direct unranking, retains literal quartic scalars and emits the conjugate forms. Independent fixed-fixture replay verifies complete model/T/structure coverage and arbitrary adjacent shard unions. This completes the join component at the supplied-input scope; the existing scientific contract remains review_required/unapproved, and no full prescribed-cohort join or cover/genus trial was launched.

## Source and checked fixture results

Five source files are in this successor archive:

- [quotient_core.rs](../../implementation/quotient_core.rs): visit_structures_range, with visit_structures delegating its full range.
- [join_core.rs](../../implementation/join_core.rs): private-context-bound JoinPlan, validated ordered models, canonical T targets, checked offsets and JoinedRow callback streaming.
- [join_certificate.rs](../../implementation/join_certificate.rs): only the three named software fixtures; JSON collection is bounded, not the production serializer.
- [check_join_certificate.py](../../implementation/check_join_certificate.py): separate polynomial arithmetic, points/doubles/cosets, literal forms, cocycles and full fixture shard-union replay.
- [test_join_certificate.py](../../implementation/test_join_certificate.py): five software test methods.

| Software fixture | Supplied classes | T-class blocks | Structures per block | Joined rows | Replay |
|---|---:|---:|---:|---:|---|
| F3 complete classes | 8 | 14 | 1 | 14 | PASS |
| F5 complete classes | 12 | 24 | 1 | 24 | PASS |
| F27 fixed characteristic-3 model | 1 | 2 | 819 | 1,638 | PASS |

[software-tests.txt](software-tests.txt) binds actual source hashes, compiler/interpreter versions, commands, exit codes and retained warnings. Its final marker is ALL_JOIN_SOFTWARE_CHECKS_PASS. Eight Rust tests and 25 Python methods pass: 6 quotient, 5 structure, 5 class, 4 compact-input and 5 join methods. The join methods separately check the full three fixtures; actual native adjacent shards and reversed submission order; 15 row/header mutations plus duplicate-coset/fixture rejection; translation-involution identity on all control points; and CLI positive/wrong-fixture replay.

The direct range test compares every emitted matrix against the original explicit A1/A2/B nested loops over F3, F27 and F125, including concatenated 17-row ranges. A single final-index access in the largest prescribed field F2197 checks direct suffix access; it is not a full F2197 join. Join tests compare complete rows with 113-row range concatenation, reject bad bounds and insufficient caps, accept explicit empty ranges, check callback-error propagation and reject duplicate/singular/invalid models and unsupported degrees.

## Exact ordinal plan and unranking

For a fixed context and supplied model list, every class c has canonical targets T_c from the complete E(K)/2E(K) partition. Let S=(Q^3-Q)/(q^3-q). The private plan computes

    class_offset[c] = S * sum_{j<c} |T_j|,
    ordinal(c,t,s) = class_offset[c] + t*S + s,
    0 <= s < S.

Multiplication/addition of the total are checked u64 operations before the immutable plan is built. Remaining offset arithmetic is bounded by those checked prefix totals. The entire model slice is validated before point/coset construction; exact duplicate models, singular or invalid coefficients and declared model-count limit violations are rejected. Models are not identified by j-invariants. The plan certifies its supplied slice; cohort completeness additionally requires binding the slice byte-for-byte to the already verified full cohort input.

Range calls are half-open [start,end), validate end<=total, reject a row cap below end-start, return zero for an empty valid interval and propagate callback errors immediately. They scan only the small class/T plan and emit the intersecting structure intervals; there is no traversal of earlier structure rows.

The structure transversal keeps the previous frozen internal-log order. A1 has (infinity,0,c), c in rep_a1. A2 has (infinity,b,c), b in rep_a2 and finite c!=b, with block width Q-1. B has a in rep_b, b in P1(K) except a, c in P1(K) except a,b, with width Q*(Q-1). Arithmetic unranking skips excluded indices in sorted order, correctly allowing infinity in B. The normalized matrix is reconstructed from each ordered triple. Supported degrees remain 1,3,5,7; the complete original abstract n3/n5/n7 placement arm is a separate obligation.

## Literal scalar and join identities

For target T, F_T is exactly curve.quotient_form(T). T=O retains the homogeneous cubic with its simple projective-infinity branch point; finite T uses the explicit same-curve quartic. The row is bound to its model, exact T, class/coset/structure indices and ordinal, normalized N and C(N)=N^-1 sigma(N). It emits

    G(X,Z) = F_T(dX-bZ,-cX+aZ),
    conjugates[i] = sigma^i(G), 0 <= i < n.

Since G(N(X,Z))=det(N)^4 F_T(X,Z), the corresponding weighted ordinate is multiplied by det(N)^2. Literal coefficients retain the actual scalar square class. No monic normalization, branch-support-only replacement or rank/genus computation occurs in this interface. The checker expands each transformed form independently and compares every conjugate coefficient and closure.

Internal arithmetic uses the pinned field's logarithmic labels; the fixture certificate emits polynomial-basis indices with the full field identity. The ordering version is log-point-coset-transversal/v1. A production identity must bind that full table, ordered input bytes and ordering/source version; indices alone are insufficient.

## Independent coverage and shard proof

The fixture checker reconstructs complete normalized model families for F3/F5; the F27 fixture explicitly supplies one fixed model, not all classes over F27. It reconstructs every rational point, the doubled subgroup and its complete disjoint cosets, and compares exact canonical targets. Full joined row order then forces each class/T block to contain every structure ordinal exactly once.

The checker independently computes normalized C(N)=N^-1 sigma(N). Equality of two such cocycles is equivalent to equality of left PGL2(Fq) cosets. Exactly S distinct cocycles therefore proves complete left-coset coverage. It requires the same matrix at a given structure ordinal in every T block. This certifies global coverage and consistent ordering; it does not independently enforce the exact source transversal assignment at each ordinal. The separate Rust nested-reference test checks that assignment for its fixed fields.

Shard headers must match exactly, duplicate ranges are rejected, each shard contains exactly end-start consecutive rows and sorting accepted shards must give a contiguous union [0,total). All row identities, literal forms and conjugates are checked. Empty shards contribute no rows; they do not replace missing positive ranges. Mutation controls exercise gaps, overlap/duplication, wrong plan/field, identity/scalar changes, repeated projective cosets and bad bounds.

This checker remains a whole-JSON software-fixture checker: at most 10,000 rows/structure indices per declared fixture and the inherited per-file loader cap apply. Production streaming custody still needs exact published cohort/plan/source/file hash binding, immutable attempt receipts, external verification of accepted shard selection, byte/resource caps and checkpoints. This component makes no production custody-hash claim. Complete production structure uniqueness needs external sorting/compact exact indexing or an independently checked transversal rank/unrank certificate, not counts/hashes alone.

## All T representatives: checked group identity and remaining coordinate transport

The stored Coset witnesses certify P=T+2Q. Translation by Q satisfies

    tau_Q o iota_T = iota_(T+2Q) o tau_Q,  iota_T(P)=T-P.

The software tests check this equality on all relevant points of every fixed control curve. This is group-level equivalence. The actual Mobius/scalar coordinate transport is not implemented or tested here.

For T'=T+2Q, its next certificate should supply A=(a,b;c,d) and nonzero kappa, verify in K(E)

    t_T'(P+Q) = (a*t_T(P)+b)/(c*t_T(P)+d),
    w_T'(P+Q) = kappa*w_T(P)/(c*t_T(P)+d)^2,
    F_T'(A(X,Z)) = kappa^2*F_T(X,Z).

Use t_O=x,w_O=y for the baseline; clear denominators and reduce modulo y^2=f(x) to avoid insufficient rational interpolation points. Equivalent targets must reindex structures by HN -> HN A^-1, giving C(N A^-1)=A*C(N)*sigma(A)^-1. Comparing the same fixed structure ordinal across different target representatives is not an invariance check. Matrix normalization factors and the resulting square/fourth-power scalars must be recorded. Do not merge distinct T cosets without additional certified automorphism data.

## Next construction and archival scope

Next bind full published cohort and plan identities to a production streaming serializer/checker/reducer, and implement the explicit all-T coordinate/scalar transport certificate. Preserve all five original class cohorts, original coordinate/random-branch controls and abstract placements. Connectedness/geometric genus, Frobenius covering descent/Type2 and original P3/descriptive H1 analysis remain subsequent scientific interfaces; they are not supplied by projective cocycle coverage.

The accompanying diagram records this arithmetic/coverage construction only. No canonical scientific graph edge, hypothesis status or admission/exit criterion changes. TASK-20261102-d8d2b5 scopes 15 exact successor paths including SR-20261102-43c569. Parent must render/inspect the PDF, create the deduplicated manifest excluding its own hash, commit an exact snapshot, run strict native content-at-commit archive verification and verify remote publication before claiming archive completion. The reported ledger baseline remains only inherited RUN-BINSTD-f7ca97 top-level-run error, with1210 suppressed legacy errors; earlier report/spec/protocol/native receipt snapshots remain unchanged.

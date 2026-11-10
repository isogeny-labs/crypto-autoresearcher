#set page(paper: "a4", margin: 19mm)
#set text(size: 10pt, font: "DejaVu Sans")
#set par(justify: false, leading: 0.65em)
#text(size: 19pt, weight: "bold")[Scalar-constant prefix extractor]
#text(size: 11pt)[Source snapshot · 7 November 2026]

*Status: `source_only_unvalidated`.* Task TASK-20261107-898896. Standalone direct restriction, binary-search reference and incidence sweep are authored. No candidate import, execution, tests, solver, field enumeration, benchmark or cloud work is authorized or performed.

#image("diagram.svg", width: 100%)

= Implemented boundary
Inputs are canonical square-free coefficient dictionaries, externally prime p, n variables and a full LSB-first Boolean assignment. Strict validation rejects bool-as-int, invalid masks and noncanonical coefficients. Caller inputs are copied. The output is a witness and structural counters, with no inverse, certificate, clause or callback.

The reference recomputes original restrictions at each binary query and retains the true endpoint's witness. Ascending generator order selects the lowest qualifying index. The sweep retains original term identities through aggregate cancellation, interprets absent-key subtraction as subtraction from zero, and tests only after a complete variable batch. Touched-generator updates avoid scanning all generators at every depth; the successful tie scan occurs once.

The least prefix is relative to the fixed variable order and scalar-inverse single-original-generator family. No-witness means full polynomial validity, not domain validity. Exceptions and interruption do not become no-witness results.

#pagebreak()
= Static evidence and cost accounting
Permitted checks are AST parsing and written source review. No runtime reference/sweep equality is claimed. Root's report-inputs binds exact artifacts and any independent static-reading disposition. Code contains no imports or top-level calls and no exception handler that converts failures to validity.

With s generators, T original terms and I term-variable incidences, reference bookkeeping is bounded by O((s + T)(1 + log(n + 1))). Sweep bookkeeping and storage are O(n + s + T + I) entries under expected constant hash probes. Reference extraction can transiently retain two residual dictionaries beyond the snapshot; the direct restriction API retains all returned residuals. These are source bounds, not measured time or bit complexity. Input copying, integer sizes, mask extraction, hashing, allocation and field arithmetic remain costs. Sweep initialization builds every incidence even if the initial predicate succeeds.

The interface specifies validation visits, original term and generator visits, incidences, modular updates, mask operators, predicates, touched/qualifying-set work and tie scans. These overlapping event counters are not summed into CPU cost. Inverse and multiplier counters are zero.

= Independent static disposition
The fresh independent reader gave witness semantics a conditional static pass and found two documentation defects. Both are corrected without changing extractor.py: permutation tests require identical witnesses and final residuals, while counters reproduce only for identical ordered inputs; actual intermediate deletion-count differences remain recorded. Storage now allows two transient residual dictionaries. The reader requested no witness-semantic source change. Static reasoning and AST success remain distinct from runtime acceptance; status is `source_only_unvalidated`.

= Integration must reconstruct the originals
No engine/checker code changes here. Future integration must independently recompute ALL original residuals through the existing `_residuals` path, confirm the selected constant, construct its inverse and full multiplier vector, and then invoke `_record_proof`. The current `_record_proof` checks supplied residuals; it does not reconstruct them itself.

Charge extraction, independent restriction, inverse, vector allocation, certificate checking and witness reconstruction separately. Preserve `_reject`, valid-model and coverage checks. Do not silently redefine leaf counters. A shorter model-triggered clause is not partial-assignment pruning. Auxiliary prefix bits cannot be truncated into a projected blocker.

= Evidence lineage and next obligation
The bound derivation-v2, refinement-v2, independent critique and disposition in coordination/prime_scalar_prefix_source_20261107 supply the mathematical specification. The public engine proof/fallback paths supply the integration boundary. These are internal source evidence, not software acceptance.

Retrieved prior context: Deharbe et al., Computing prime implicants, FMCAD 2013, #link("https://www.verit-solver.org/papers/fmcad2013.pdf")[primary paper]. It studies reducing satisfying assignments with solver structures; it does not establish this finite-field sweep. No novelty claim is made.

The separate validation-plan proposes finite software checks and requires fresh exact admission before execution. Both producer slots are consumed; the independent software slot stays reserved. All 106 coordinate plus six coefficient cells, three encodings, five leads, complete charts, identical projected sets and witness/certificate costs remain required.

No canonical frontier graph changes: this diagram is source architecture, not measured data. Provider/model authentication remains unverified under the scoped amendment. Root owns PDF inspection, hashes and publication.

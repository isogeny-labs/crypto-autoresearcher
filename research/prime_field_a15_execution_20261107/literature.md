# Signed-pair construction: source review before native work

Primary source review on 7 November 2026, scoped to the ranked
[A14 next action](../prime_field_a14_execution_20261106/next-leads.md).
The review reads A14 query_index.py and check_query.py, A12 batch_query.py
and batch_check.py, production src/crypto_autoresearcher/index_calculus/_accel.py
batch_inverse, tails.py lines 306--346, and harvest.py _scan_np. Production
already shares a denominator for signed sums, derives opposite tails and
uses product-tree inversion. A12 executes this arithmetic for signed endpoint
queries. A14 still executes four scalar additions for each unordered base pair.
The new comparison repairs that baseline at its pair-construction stage; it
proposes no new group symmetry or batch-inversion method.

The retained primary Petit/Kosters/Messeng PKC2016 paper was reread at page 8,
section 3.2 (https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf;
local PDF SHA256 a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b).
It explicitly calls its mixed field-operation/scalar-multiplication unit model
very rough and separates precomputation, relation solving and linear algebra.
It does not calibrate this program's inversion internals, array allocations,
Python/NumPy overhead, checker atlas, storage or complete attack costs.

For distinct finite geometric sign classes on the same nonsingular short
Weierstrass curve, unequal x-coordinates give a nonzero common denominator.
Compute A+B and A-B with its reciprocal, then derive -(A-B) and -(A+B).
Preserve all four sign descriptors and original native slots. The native
precondition excludes identity, order-two points and duplicate sign classes;
software controls must reject invalid geometry and exercise exceptional query
points separately. One bounded batch per base is a finite memory choice.

All 16 input geometries and all 8,960 retained endpoint queries are transcribed
from A14 at e71e73242b04856b230e8f767383eb4ad7ef57ba. Transcription performs
JSON copying, sorting and hashing only, no new group arithmetic. Each old
archive is checked against its committed CAS manifest, and small prelude files
against Git bytes. Full native row/query commitments are fixed before builders
run. This is conditioned input reuse, not fresh holdouts or new target recoveries.
The old producer evidence remains unverified under PCC-20261106-35c953.
[pcc:unverified]

No research-kb tools are exposed in this resumed session (tool discovery
returned none); the carried wrapper outage remains an explicit retrieval gap.
The review uses these direct sources and retained primary PDF, with no claim
of corpus-wide absence, independent scientific review or novelty.

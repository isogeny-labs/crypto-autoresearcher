#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Fixed-base larger-field target holdouts
Run #raw("a12-batched-holdout-6ba98a"). Producer observations, unverified PCC standing without independent signed replay/recomputation. [pcc:unverified]

Planned: four fresh first-eligible coefficient curves on F262139/F524287, base32, eight fresh canonical-y public targets each; AP/hash seeds0/1/2, source128 with prefixes64/128, three target policies and query budgets1/2/4/8, two knowledge scopes, two general-U kernel-free solvers. Completed 1152 of1152systems/2304 of2304solver calls; unknown systems 0. Complete true, return 0, timeout false. Both query engines execute per endpoint; matrices and solver outcomes are counted once. [pcc:unverified]
#image("target-recovery.svg",width:100%)
Each plotted curve/policy/budget/scope sums twelve dependent source branches, at most96target slots. Points are reused; they are not independent draws. A blank series is unknown, not zero. Fixed base/source/query budgets are retained even when no target is recovered. Field/curve/target rejection and all misses remain raw observations. [pcc:unverified]

Scientific source #raw("eaab099f6ed11eafc4e6137a923105406d4d11ce"), observed HEAD #raw("bfad3c581657cac113a81e17fab0f5f74990f547"), dirty true; exact source closure checked separately. Protocol #raw("203a3757b05c12deb4449ac04eb96e979d3aa8595ff10b4b269e4e8cb8f46e2d"). Child user/system CPU 120.943127/8.804010s, supervisor 0.701872/0.064437s; diagnostic wall 132.390871s, child peak RSS 194142208bytes. Clocks unisolated. Command/host/runtime/gate receipts retained in execution.json/host.json/raw admission. [pcc:unverified]
#pagebreak()
= Actually executed query arithmetic
#image("query-engine-costs.svg",width:100%)
#table(columns:(auto,auto,auto),inset:4pt,[Fp operation],[scalar],[batch],
[add],[0],[120800],
[sub],[1691200],[1087200],
[mul],[724800],[1075875],
[inv],[241600],[3775],)
Both engines run every physical queried endpoint, and their work is charged separately and in combined physical counters. Scalar reuses paid signed-base points. Batch shares each x-denominator over both signs within one endpoint, uses the existing product-tree technique and pays padding, evaluated dummy masked work, inversion and scalar exceptional fallbacks. NumPy semantic field-element operations count the implemented vector API, not historical scalar-equivalent accelerated-decomposition counters. Explicit array allocations/conversions/masks are retained; internal allocator/pow/OS work is not fully expanded. [pcc:unverified]

Every endpoint's exact ordered point array is compared before one accepted-row/query-miss stream is used. Separately coded plain group arithmetic and operation schedules check point hashes and scalar/batch Fp counts; a full signed-distinct-triple oracle checks every collected source/target row and miss. Tiny controls also compare the repository production NumPy helper, order-two, identity, coincident x, odd tree padding and injected failures. These local checks do not establish signed standing. [pcc:unverified]

Installed NumPy version #raw("2.5.4"), compiled extension SHA #raw("b185dfe64b07180bedc7c15fb2735b0d0f4f4e09eb9c15bd8e67f74568aebcbf"); full build configuration recorded. The uint64 p-less-than-4294967296 guard and runtime identity must hold. No unavailable engine is silently substituted. Physical source signed queries 196608 and target signed queries 44992; logical target requests 9216. Two executed engines do not double these logical request counts or the number of independent targets. [pcc:unverified]
#pagebreak()
= Information and cold program references
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[policy],[scope],[checked systems],[target slots],[positive Delta],[deficient-base recovery],
[walk],[relations],[48],[3],[36],[1],
[walk],[anchors],[48],[3],[36],[1],
[hash_offset],[relations],[48],[0],[48],[0],
[hash_offset],[anchors],[48],[4],[48],[4],
[general],[relations],[48],[7],[48],[1],
[general],[anchors],[48],[96],[48],[34],)
Table uses target budget8; at most48systems/384dependent target slots per policy/scope. Deficiency is measured after target-column cancellation. Delta subtracts actual outside-column rank from joint rank and then original source rank; original base columns never shrink by policy. Paid identity/base/public/cross-target coincidences remain explicit anchors with first-budget availability. [pcc:unverified]

Cold references include one chosen source/prefix, target policy/budget and query engine, its setup/prerequisite walks, many-target P table/symbolic Q caches, query, projection, chosen solver, lifting and public checks. The other query engine, diagnostic comparisons and batch-only index in scalar views are removed with exact namespace subtraction. Actual panel work additionally pays both controls/all arms/checkers/checkpoints. Nested views are not new executions or additive clocks. [pcc:unverified]

Finite frontiers contain 4608cold options in192matched groups. They require target-mask superset, Delta not lower and no larger included counter, with a strict change. Delta compares dimensions, not row-space containment. The arithmetic/explicit-query-allocation and all-retained-operational-counter frontiers are separate; the latter still omits unexpanded internals. Full options/dimensions/frontier memberships are in lossless analysis.json. No frontier establishes weighted/all-cost/runtime/whole-attack dominance. [pcc:unverified]

#table(columns:(auto,auto,auto),inset:4pt,[Fr operation],[joint],[outside first],
[add],[4245],[31177],
[sub],[351255],[386075],
[mul],[311016],[347426],
[inv],[1384],[1869],)
Solver phases include elimination/cancellation, target-unit row-space tests without a full production kernel, original-row lifting/certificates and public group checks. Both use symmetric unit-sign shortcuts. Scalar/batch controls share these matrix outcomes. Every raw input/output is flushed before checking; closed curves are losslessly encoded then checkpointed. Raw records were pushed before rendering this report. [pcc:unverified]

Existing technique sources: production #raw("_accel.py") #raw("batch_inverse/subtract_many"), tails.py/harvest.py/decompose.py; prior A11 record/worklist/proof status; retained PKM2016primary pp7--9. Research-KB unavailable, scoped direct-source fallback documented, no corpus-wide absence or novelty. Legacy generation merges subtraction; rejected fixtures, inversion/pow/hash, checker/Python/OS/IO primitives are incomplete. Inclusive diagnostics retain those scopes. Canonical isogeny graphs have no changed mathematical edge. [pcc:unverified]

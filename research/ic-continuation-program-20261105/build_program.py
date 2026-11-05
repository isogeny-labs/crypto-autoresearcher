"""Build the proposed continuation manifest from explicitly inspected sources."""
from pathlib import Path
import json, hashlib, shutil

ROOT=Path(__file__).resolve().parent
PINS={'isogeny-labs/crypto':'f384852fdc2a3eb448c7440c8f11ed049fa024d3',
      'isogeny-labs/ml-cryptanalysis':'eb227d3ccd93ad750abd910b91af665b88bf480e',
      'isogeny-labs/crypto-autoresearcher':'5440a26b36693841b89fc803baf73d4061df4826'}
SOURCES={
 'radix-run':('crypto','research/pkm_radix_grading_20261104/run_cells.sh'),
 'radix-protocol':('crypto','research/pkm_radix_grading_20261104/protocol.json'),
 'atlas-cost':('crypto','research/curve25519_ic_atlas_20261104/REPORT.md'),
 'trace-run':('ml-cryptanalysis','experiments/f4-trace-replay/run_cell.py'),
 'trace-protocol':('ml-cryptanalysis','experiments/f4-trace-replay/PROTOCOL.md'),
 'learning-null':('ml-cryptanalysis','experiments/fb-cost-model-e2e-l4/report.md'),
 'complete-cost':('ml-cryptanalysis','experiments/prime-coset-domain-20261031/report_p8d.md'),
 'solver-reference':('ml-cryptanalysis','experiments/published-ic-reference-arm/README.md'),
 'boundary':('crypto-autoresearcher','knowledge/open-problems/KN-OPEN-08ba7e.md'),
 'decoding-desk':('crypto-autoresearcher','docs/reports/ecdlp-leads-desk-20261104/README.md'),
 'shared-lead':('crypto-autoresearcher','knowledge/leads/ecdlp/ic-prime/LEAD-ICP-shared-coefficient-membership.yaml'),
 'secant-lead':('crypto-autoresearcher','knowledge/leads/ecdlp/ic-prime/LEAD-ICP-split-graph-secant-presentation.yaml'),
 'binary-degree':('crypto-autoresearcher','knowledge/leads/ecdlp/ic-engine/LEAD-ICE-descent-closure-degree-at-scale.yaml')}
lock=[]
for sid,(repo,path) in SOURCES.items():
 full='isogeny-labs/'+repo
 source=Path('/workspace/program-sources')/full/path
 dest=ROOT/'sources'/sid/source.name;dest.parent.mkdir(parents=True,exist_ok=True)
 if source.is_file(): shutil.copyfile(source,dest)
 else:
  if not dest.is_file(): raise FileNotFoundError(source)
 lock.append(dict(id=sid,repository=full,commit=PINS[full],path=path,
                  sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),snapshot=str(dest.relative_to(ROOT)),
                  url=f'https://github.com/{full}/blob/{PINS[full]}/{path}',standing='retrieved_source_not_independently_verified'))

costs=['setup_work','selection_work','query_work','failed_query_work','witness_extraction_work',
       'subgroup_validation_work','independent_rank','linear_algebra_work','descent_work',
       'verification_work','peak_memory_bytes','cold_total_work','reused_setup_total_work','matched_reference_work']
tracks=[]
def add(id,title,repo,leads,sources,deps,question,next_step,deliverables,controls,extra,scaling,positive,null,kind='performance'):
 tracks.append(dict(id=id,title=title,kind=kind,owner_repository='isogeny-labs/'+repo,
                    lead_refs=leads,sources=sources,dependencies=deps,execution_state='not_started',
                    question=question,next_step=next_step,deliverables=deliverables,controls=controls,
                    metrics=(costs+extra if kind=='performance' else extra),scaling=scaling,
                    outcomes=dict(positive=positive,null=null,inconclusive='Preserve every cap, missing row, failed control and source gap; correct the specific instrument/access issue and rerun only under an additive prospective amendment. No mathematical closure.'),
                    promotion='Existing Coordinator review and signed claim standing; this plan grants neither.'))
add('B0','Reproduce complete-cost incumbents','cryptanalysis',
 ['LEAD-ICB-koblitz-rho-reference','LEAD-ICP-prime-ic-constant-engineering'],['atlas-cost','complete-cost','solver-reference'],[],
 'Do the named baseline, strongest applicable solver and matched rho have complete and comparable accounting?',
 'Bind existing study inputs, code and raw exports; independently replay one original complete panel before extending it. Preserve separate prime, ordinary-binary and Koblitz strata.',
 ['baseline-lock.json with curve/subgroup/base UIDs, code/binary/protocol hashes and unit definitions','canonical exports with all historical exclusions','discrepancy report and independent review'],
 ['fresh-process A/A','known-answer logs and deliberate bad witness','strongest matched solver and rho on identical points'],[],
 'Original sizes first; no larger ladder before the reference discrepancy is resolved.',
 'Freeze replayed incumbent per stratum; admit one same-instance challenger.',
 'Repair the specific reproducibility/accounting mismatch without rewriting history.')
add('L1','Factor-base learning through complete solves','ml-cryptanalysis',
 ['LEAD-ICB-learned-cost-model-factor-base-selection'],['learning-null','solver-reference'],['B0'],
 'Does a frozen selector lower full-DLP cost on unseen curves and dimensions?',
 'Reproduce the l=4 differing-pick result, restore the pilot-dropped n=23 scope under a new protocol, then evaluate a frozen rank-aware selector against the hand rule and best available solver.',
 ['grouped train/validation/test split by curve and base family','selection search/training cost ledger','complete cold solves and held-out selector decisions'],
 ['hand rule','shuffled-label model','planted useful base feature through same learner','tied-pick A/A','no target-log or post-solve feature leakage'],['model_regret','usable_relations_per_query','rank_gain_per_relation'],
 'Reproduction n=19,23 l=4; next n=31,41 l=5,6 subject to measured preflight. n>=43 only after complete lower rungs.',
 'Replicate on a second host/seed panel; ratchet the complete-cost baseline in the same stratum.',
 'Retain model diagnostics; test whether rank or descent dominates rather than resampling favorable cells.')
add('C2','Complete-cost coset and selection improvements','ml-cryptanalysis',
 ['LEAD-ICP-algebraic-membership-factor-base','LEAD-ICP-coincidence-harvest-structured-base'],['complete-cost'],['B0'],
 'Does staged selection retain its complete-cost improvement as construction and subgroup costs grow?',
 'Replay P8d with its exact accounting, then prospectively compare legacy, staged selection, scan-all and k=1 versus k=16 jumps.',
 ['same-instance selector/solve export','construction rejection and no-usable-base rows','per-phase attribution'],
 ['selection bypass A/A','scan-all expensive positive workload','legacy','fixed-base comparison isolating selector cost'],['selection_share','coverage_probability'],
 'Original band-17 family then at least three growing field-size bands; h=1 primary and h>1 separate.',
 'Promote only the matched complete-cost gain; feed frozen construction into the scaling arm.',
 'Keep the lower-scale gain; locate the cost crossover and retain the original domain coverage.')
add('F3','F4 trace replay, fallback and learning cost','crypto',
 ['LEAD-ICB-decomposition-encoding-and-sat','LEAD-ICE-boolean-f4-f5-f6-engines'],['atlas-cost','trace-run','trace-protocol','solver-reference'],['B0'],
 'Is trace reuse cheaper including learning, failed replay, recovery and actual witness extraction?',
 'Resume the original trace comparison before transfer. Run fresh and replay with identical systems; log each attempted replay and mandatory fresh fallback.',
 ['trace-source and invalidation identities','trace learning/cache/fallback ledger','separate counted-work and isolated-wall comparisons'],
 ['A/A fresh solves','same-system replay positive control','wrong-field/base/arity trace rejected','changed-target stress','SAT and UNSAT strata with natural mixture'],['learn_work','replay_work','fallback_work','fallback_rate','trace_bytes','solver_wall_seconds'],
 'Original prime-field toy rows separately from binary n17,19 l3,4; extend n23,31 and m3,4 only after exactness. Report one-target cold and separate batches T=8,32.',
 'Freeze trace policy and price it in a complete solve; then transfer once to a new family.',
 'Keep exact rejection/fallback behavior; determine whether fill-in or trace instability explains the loss.')
add('S4','Scaling and larger-instance continuation','crypto',
 ['LEAD-ICE-descent-closure-degree-at-scale','LEAD-ICP-pkm-tower-algebraic-oracle'],['atlas-cost','binary-degree','radix-protocol'],['B0','F3'],
 'Which phase and resource grows, and does a measured improvement persist out of sample?',
 'Reproduce k16..24 without changing its frozen interpretation; freeze a prospective k26,28,30 continuation only after per-arm memory/runtime pilots and account budget readback.',
 ['phase-by-phase counts and matrix width/nnz','complete-panel fits with uncertainty and held-out-rung prediction','resource frontier retaining censored cells'],
 ['matched rho','enumeration/grid on tiny cells','same-base dense representation','A/A builds','planted structure distinct from natural target distribution'],['solving_degree','last_fall_degree','matrix_columns','matrix_nnz','fill_in','fit_exponent','prediction_error'],
 'Prime subgroup bits and binary field degree are separate axes. Proposed k26,28,30 and binary n23,31,41. No >128GiB cloud submission under current namespace policy; larger closure cells require an explicitly authorized capacity change.',
 'Add one next rung prospectively and independently replay; fit scaling only within the same algorithm and units.',
 'Publish the measured phase bottleneck and target a specific algorithmic change; never infer asymptotics from a flat finite segment.')
add('E5','Elliptic-code list decoding','crypto-autoresearcher',
 ['LEAD-ICP-elliptic-code-list-decoding','LEAD-EXO-elliptic-code-list-decoding'],['decoding-desk'],[],
 'Does the actual received-word construction yield relations more cheaply than enumeration?',
 'Retrieve and read the full Zhang-Liu ePrint/ProvSec construction; write exact divisor, code, received-word, radius, guessing and rationality assumptions before implementing it.',
 ['primary-source theorem/assumption map','exact relation-codeword correspondence','tiny exhaustive checker and prospective cost protocol'],
 ['known subset-sum codeword','zero-word radius failure negative control','plain subset enumeration','random matched code/target and same code parameters'],['list_size','guessed_agreements','valid_relation_count','decoder_work'],
 'Exact tiny p first; planned p~2^12,2^14,2^16 with matched B and k=2..6 only after correctness and measured preflight.',
 'Freeze the decoder and compare per independent relation on a growing ladder before a full-DLP experiment.',
 'State the exact received-word/parameter obstruction; leave other decoding algorithms and parameter regimes open.',kind='construction')
add('H6','Shared coefficients at higher arity','cryptanalysis',
 ['LEAD-ICP-shared-coefficient-membership','LEAD-ICP-digit-presentation-solving-degree'],['shared-lead','boundary'],[],
 'Can shared coefficients reduce complete solving work without hiding degree or rationality constraints?',
 'Prove exact signed-model-set equivalence for compact selectors at m=3,4; retain m=2 only as a correctness/empty-chart negative control. Continue the source-bound F_p trail checker rather than an unadmitted one-hot expansion.',
 ['chart-complete signed tuple bijection','native root/witness extraction','source-bound solver explanations and UNSAT replay','setup/query/storage ledger'],
 ['same-base per-root membership','dense membership','permutation quotient','empty squarefree m2 chart','repeated-root arm separate'],['selector_variables','accepted_model_count','rejected_chart_count','natural_query_slope','setup_slope'],
 'Existing development fixtures, then s6..14 natural m3 panel as its own frozen protocol. No s15..27 continuation inherited automatically.',
 'Require prospective natural-query and reusable-setup slope gates from the owning protocol, then whole-DLP cost.',
 'Identify whether roots, selectors, explanation size or coefficient construction consumes the saving.')
add('R7','Secant and alternative representations','crypto',
 ['LEAD-ICP-split-graph-secant-presentation'],['secant-lead'],[],
 'Does lower handled degree reduce complete same-base work per independent relation?',
 'Implement operational triangular/FGLM-style root discovery and share elimination across all four sign branches; do not use saved answers as a root oracle.',
 ['exact extractor with independent group replay','all chart/sign costs','unchanged historical caps plus new prospective results'],
 ['same-base dense system','matched nongraph secant','equal-size low-x/hash-x bases','tiny exhaustive root sets','repeated roots and poles'],['extraction_work','sign_branch_work','root_set_completeness','handled_degree'],
 'F17 exact controls, then prospective F83/F101/F127 d3..5 panel; higher m3,4 only after complete extraction and cost.',
 'Advance to higher arity on independently checked complete savings across at least three growing cells.',
 'Preserve the degree theorem at its scope; reject only the tested performance construction.')
add('K8','Odd and mixed-radix Kummer towers','crypto',
 ['LEAD-ICP-pkm-tower-algebraic-oracle'],['radix-run','radix-protocol'],[],
 'Does a different radix reduce arithmetic/fill-in at matched membership information?',
 'First resume frozen EXP-PKM-RADIX-001 with G0; do not alter its rows. Separately implement exponents 0,1,2 and cube rewrite rules for radix3 with exact solution-set tests before a new study.',
 ['G0 original-count regression','original weighted-grading export','radix3/mixed normal form and multiplication checker','same-base radix2/4 and matched-size 2/3 controls'],
 ['radix2 incumbent','radix4 same-base encoding','curve-free shape null','small independent enumeration','associativity and reduction confluence on tiny quotient'],['weighted_degree','unweighted_degree','field_muladds','matrix_columns','matrix_nnz','monomial_storage_bytes'],
 'Resume existing L2/L3/X2/A1 exactly. New odd-radix study begins at tiny sizes then >=3 increasing log2(base-size) rungs; fix field/curve where possible and cross the remaining mismatch.',
 'Use counted arithmetic and fill-in to choose a representation; then compare complete relation and full-DLP cost.',
 'Separate weighted-degree renaming from actual arithmetic; retain odd-radix construction if correct even when it loses.')
add('M9','Compact full-summation boundary messages','crypto',
 ['LEAD-ICP-shared-coefficient-membership','LEAD-ICP-algebraic-membership-factor-base'],['boundary'],[],
 'Can an exact message reuse full constrained summation rather than local membership alone?',
 'Define an explicit exact boundary representation over the rational two-isogeny fibre reference; implement specialization and prefix witness extraction with every addition chart.',
 ['coefficient algebra and exact precision policy','signed ordered-tuple semantics including repetitions','message construction/storage profile','full small-field count and witness equivalence'],
 ['direct full-sum reference','membership-only cache','full target/tuple table explicitly priced','identity/inverse/doubling/pole/kernel/subgroup cases'],['boundary_state_count','message_bytes','specialization_work','prefix_witness_work'],
 'Exact tiny p exhaustive first; increase base size, m=2,3,4 and target count separately. T=1 cold primary; amortized setup at T=8,32 a separate comparison.',
 'Price all intermediate states and roots before comparing against the strongest direct oracle.',
 'Identify the precise state/message explosion; do not infer a universal tensor-network lower bound.')
add('P10','Scoped summation-polynomial lower bounds','crypto-autoresearcher',
 ['LEAD-ICE-first-fall-degree-assumptions','LEAD-EXO-low-degree-query-lower-bound','LEAD-ICE-generic-oracle-arity-cost-floor'],['decoding-desk','binary-degree','shared-lead'],[],
 'Which quantified algorithm class can actually be excluded, and what proof bridges are missing?',
 'Review the written counting lemmas in PROOF_PROGRAM.md, formalize feasible statements in the owning Lean library, and audit every quantified hypothesis before attempting a solver-family lower bound.',
 ['proof_search_map with definitions and quantifiers','readable proofs plus Lean theorem/axiom map','counterexample and proves-too-much controls','explicit unresolved average-case and representation bridges'],
 ['anomalous/weak curves excluded or labelled','auxiliary-variable low-degree membership counterexample','coordinate-oracle/query-bound counterexample','small finite exact counts','alternate solver allowed as scope test'],['proof_status','formalization_status','hypotheses','counterexample_status','review_standing'],
 'General finite-group counting lemma first; then one exact solver/presentation family. No claim about all curves, all encodings or future algorithms.',
 'Publish only a faithful scoped lower bound after independent proof/Lean review; state exactly which methods remain outside it.',
 'Preserve the failed conjecture and counterexample; refine the model without weakening the original claim silently.',kind='proof')

program=dict(schema='ic.continuation-plan/v1',authority='proposal_only',created='2026-11-05',
 goal='Pursue each requested IC mechanism through exactness, complete cost, scaling and independent review.',
 source_lock=lock,complete_cost_fields=costs,workstreams=tracks,
 dispatch=dict(backend='existing lab dispatcher and run skill only',new_scheduler=False,
  preferred_initial_frontier=['B0'],
  preferred_first_two_experiments_after_B0=['F3','L1'],
  parallel_desk_preparation=['E5','P10'],max_active_scientific_experiments=2,
  current_state='not_admitted',reason='Existing WIP admission refused; checkpoint custody unavailable.',
  promotion_sequence=['source review','exactness','frozen pilot','frozen matched component panel','cold full solve','held-out scaling rung','independent replay/review','Coordinator decision']),
 limits=dict(cloud_submissions=0,cloud_usd=0,new_exp_records=0,official_goal_status_changes=0,
  note='Preparation bundle only. No extra cloud budget, capacity change or workflow waiver is implied. All numeric ladders here are prospective design proposals, not frozen authorizations.'))
(ROOT/'program.json').write_text(json.dumps(program,indent=2)+'\n')
print('Built',len(tracks),'workstreams and',len(lock),'source pins')

"""Prospective certified-query protocol and bounded remaining-window root release."""
import argparse,copy,json,subprocess,sys,re,importlib.metadata,math
from datetime import datetime,timezone,timedelta
from pathlib import Path
from deps20 import core
import runtime_numpy
from custody20 import HERE,ROOT,INPUTS,PARAMETERS,ARMS,bindings,digest,load,write_once,tools,BUDGET_INPUTS


def remaining_budget(now):
    original=load(BUDGET_INPUTS[0]);deadline=datetime.fromisoformat(original['absolute_deadline'])
    prior=[]
    for path in BUDGET_INPUTS[1:]:
        value=load(path)
        seconds=sum(value.get(k,0) for k in ('cpu_user_seconds','cpu_sys_seconds','supervisor_cpu_user_seconds','supervisor_cpu_sys_seconds'))
        prior.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path),measured_cpu_seconds=seconds))
    charge=sum(v['measured_cpu_seconds'] for v in prior)
    elapsed=max(0,(now-datetime.fromisoformat(original['issued_utc'])).total_seconds())
    # Elapsed time is a conservative one-worker reservation for unmetered work,
    # not a measurement of additional CPU. Known earlier CPU is also deducted.
    remaining=min((deadline-now).total_seconds(),21600-elapsed-charge)
    if remaining<1:raise ValueError('original window/cumulative reservation exhausted')
    return dict(absolute_deadline=deadline.isoformat(),watchdog_seconds=math.floor(remaining),
        original_release=str(BUDGET_INPUTS[0].relative_to(ROOT)),original_release_sha256=digest(BUDGET_INPUTS[0]),
        known_prior_cpu_seconds=charge,prior_measured_records=prior,elapsed_window_reservation_seconds=elapsed,
        reservation_note='Elapsed original one-worker window plus known prior native and postprocessing CPU are conservatively reserved. Elapsed time is not measured CPU. No deadline reset or extra capacity; not another A16 attempt.')



def make_protocol(commit):
    p=load(ROOT/'research/prime_field_a18_execution_20261107/protocol.json')
    p.update(protocol_id='PRIME-FIELD-A20-FORMAL-PAIR-DICTIONARY-20261107',created='2026-11-07',study_dir=str(HERE.relative_to(ROOT)),
        question='On four fresh18/19-bit curves with unchanged norm32, does a paid16point signed-pair dictionary with formal old-base definitions, without numeric helper logs, change cancelled old-base information and requested-target units at its actual costs versus norm/coordinatehashunknown16/publicknown16?',
        freeze=dict(status='draft',protocol_sha256=None,commit=None,frozen_at=None,filed_before_affected_data=None),amendments=[])
    instrument=copy.deepcopy(p['arms'][0]['instrument']);instrument.update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()),build=[[sys.executable,'-B',str(HERE.relative_to(ROOT)/'driver20.py')]])
    descriptions=dict(norm32='Unchanged norm32, independently owned prerequisites/AP0 source128/pair index and complete GENERAL8 target program.',
        unknown16='Same original norm32 plus16 first-success coordinate-hash rational subgroup points; no supplied scalar labels. All draws/roots/subgroup/sign/rejections paid. Legitimate own constructor coincidences retained.',
        formalpair16='Sixteen distinct non-old sign classes from paid signed old-native pairs; one exact homogeneous definition per point, no numeric scalar labels, rejected collision traces/costs retained but no equations harvested. Independent own direct pair construction, no borrowed pair table.',
        known16='Same original norm32 plus separately paid public known16 helper constructor/cache; different points from unknown pool, not an isolated estimate of knowing identical logs.')
    p['arms']=[]
    for arm in ARMS:
        control=arm.startswith('joint_on_');program=arm.removeprefix('joint_on_')
        p['arms'].append(dict(id=arm,role='control_positive'if control else'reference'if program=='norm32'else'candidate',
            description=('Independent native sparse_joint solve on exactly the own final rows. 'if control else'Auxiliary-first cancellation, then old-base/requested-target elimination and native certificate lifting. ')+descriptions[program],
            instrument=copy.deepcopy(instrument),parameters=copy.deepcopy(PARAMETERS)))
    p['authors']=['Root implementer and administrative exact-source Coordinator; configured model identity unverified']
    p['claims']=[dict(id='A20-cancelled-old-base-information',**{'class':'exact_computation'},decided_by=['C-unknown-pool'],
        text='Finite old-base Delta after all auxiliary/target cancellation; own K contribution, source/full marginal, direct/cross gain and requested-target unit membership. No predetermined positive yield, calibrated cost winner, new generic method, exponent or whole-attack claim.')]
    reasons=dict(aa='Deterministic marked p<=211 controls and independent public group/query/dense/certificate checks; no clock inference.',
        positive='Marked small matrix fixtures explicitly distinguish raw rank from cancelled gain, recover a target with deficient old-base rank, lift signed/known units, and replay a tiny pool/source/target collection. Native full-joint controls run on all16 own cases.',
        negative='Controls reject changed cancellation/native weights or pool rejection trace; retain negative target residuals, paid K-only gains, dependent U rank, truncated paid journal prefixes and native admission refusal. No native pilot.')
    for k,v in reasons.items():p['controls'][k]['not_applicable_reason']=v
    p['variable_ledger']=dict(independent=[dict(name='auxiliary_program',levels=['norm32','unknown16','formalpair16','known16']),dict(name='algorithm_execution',levels=ARMS)],
        factors=[dict(name='old_base',treatment='fixed',value='original norm32/projection/order',how='Common prerequisite walk64; old unknown order frozen before helpers. Auxiliary points never become learned old-base columns.'),
            dict(name='source_and_targets',treatment='fixed',value='AP0source128, GENERAL8,8public targets',how='Full own queries without recovery-based suppression; own P/Q constructor caches only. Matched identities, independently paid work.'),
            dict(name='information_reference',treatment='fixed',value='M=pure norm-only source rows',how='No helper units, source anchors, target rows or constructor labels in M. Each arm must contain the floor in its actual norm-only source-query rows.'),
            dict(name='cost_scope',treatment='fixed',value='separate Fp/Fr/logical/byte dimensions',how='Both scalar and batch engines execute. Conditional single-engine views remove measured replay only. Diagnostics/native controls/checkers retained separately; no byte-as-operation weighting.')],
        comparisons=[dict(id='C-unknown-pool',arms=ARMS,design='factorial',differs_in=['auxiliary_program','algorithm_execution'],threshold='Exact Delta/kernel/native certificates and named target masks, separately paid component vectors. No favorable effect required.')],crosses_map=False,aa_not_applicable=reasons['aa'])
    p['randomization']['arm_order_reason']='Fixed norm32 then unknown16 then formalpair16 then known16 per curve. All auxiliary/prelude builds precede public target draw. Own AP0/source/index/natural queries, own GENERAL8 recipe and full P/Q/Registry constructor, all64 target slots. Actual cancellation-first and native joint calls, then separate information diagnostics. No checker or other-arm knowledge enters a producer.'
    p['randomization']['instance_sampling']['rule']='New domain and44 pinned prior coefficient exclusions; first eligible a2 curves, two each F262139/F524287. Eight canonical-y public target hashes after all base builds. Pool16 first-success public coordinate hashes outside old norm and earlier pool sign classes. No target/pool scalar logs, yield selection, redraw or horizon expansion. Known16 uses separate public scalar recipe.'
    p['randomization']['seed_derivation'].update(seeds=[0]*32,note='Four curves/32 public targets, sixteen dependent cases and32actual batch calls/export rows; each case has cancellation-first and native-joint control.')
    p['sample_size']['power'].update(note='Exact finite four-curve matched census,16cases/32calls. No fitted scaling law or population significance.')
    p['decision_rule'].update(comparison_ids=['C-unknown-pool'],statistic='Exact old-base corrected Delta and old-kernel action; actual requested-target unit membership; separate paid counter vectors.',
        text='For source-only and complete own rows, cancel auxiliary AND target columns. Total Delta=rank([[M,0],[B,U]])-rank(U)-rank(M). K consists of own non-collected source units/anchors and accepted formal definition rows plus target Registry pure-P base matches; K contribution is separately cancelled Delta(M,K), and collected increment is Delta(M,K+B)-Delta(M,K). Source/full K differ only by actually available own target P labels; target marginal is complete minus source Delta. Direct gain uses U=0 rows; cross gain is corrected Delta minus direct gain. Known16 labels are supplied information. Report positive/zero/adverse outcomes and all costs; do not infer a weighted winner.')
    p['measurement']['counters']=['Actual Fp/Fr add/sub/mul/inv; pool hashes/message bytes/root pow calls/subgroup/sign/alias/rejections, helper/base/prelude/source/constructor work; both query engines and actual A15 batched pair floor.',
        'Own pair/query arrays, source/natural/all derived query costs, matrix assembly, auxiliary cancellation/old-target elimination/unit membership/native lifting/public checks. Own information diagnostic and native joint controls separately paid. Logical payload/array bytes are not RSS or operations.']
    p['measurement']['record']=['Exact source/input/interpreter/NumPy hashes, clean pre-output Git observation, unchanged protected bytes; no invented signed execution attestation.',
        'Producer outputs before checker receipts, every draw and failed paid phase/journal prefix, all original native target and cancellation certificates. Independent dense U/stacked ranks and old-kernel syndromes.',
        'Actual PID-bound admitted-start S3 checkpoint before generation and four closed-writer curve checkpoints. Original deadline/cumulative reservation, one worker/thread2GiB/one consumed attempt, no retry/new capacity.']
    definitions=dict(identified_targets='Number of named requested target unit functionals determined.',identified_mask='Named target mask; auxiliary pivots never count as targets.',
        native_columns='Original norm32 plus0or16 auxiliary slots, aliases retained.',old_columns='Unchanged original projected norm unknowns.',auxiliary_slots='0or16 native auxiliary slots, not learned rank.',
        source_rows='Actual own native source rows including declared units/anchors.',target_rows='All own decomposition and Registry rows under complete GENERAL8.',
        source_delta='Old-base Delta after cancelling auxiliary and target U in source-only rows.',full_delta='Old-base Delta from complete own rows after cancelling all U.',
        supplied_K_delta='Complete own K information after cancellation, separately supplied constructor contribution.',collected_after_K='Complete Delta minus own K Delta.',
        target_marginal_delta='Complete Delta minus source-only Delta.',direct_base_gain='Rank gain from own rows whose U is already zero.',cross_row_gain='Additional Delta requiring cross-row outside cancellation.',
        reference_rank='Rank of pure norm source floor M.',base_rank_after='Final old-base rank after all U cancellation.',outside_rank='Actual rank(U), not count of unknown columns.',geometric_queries='Own distinct cached natural/derived target points.')
    for op in ('add','sub','mul','inv'):definitions['fr_'+op]='Actual algorithm Fr '+op+' including native lifting/public checks; pow internals unexpanded.'
    template=copy.deepcopy(p['metrics']['primary'][0]);p['metrics']['primary']=[dict(template,id=k,name=k.replace('_',' '),definition=v,source='metrics.json rows and analysis.json owned component vectors')for k,v in definitions.items()];p['metrics']['secondary']=[]
    p['analysis_plan']['script']=dict(path='analyze20.py',sha256=digest(HERE/'analyze20.py'))
    p['stopping_rules']=[dict(kind='fixed_n',preregistered=True,rule='Four fresh curves/32 public targets,4own programs=16cases,32batch calls/export rows and16information diagnostics, plus4expanded-old semantic checker calls. Complete AP0source128/GENERAL8; no redraw or coverage extension.'),
        dict(kind='invalidation',preregistered=True,rule='Native48/joint64/pairs8192/rows4096/labels8192/cache64. First-success pool16/max10000candidates.128curve/field/target candidates,10000base/scalar candidates. Retain failure/unknown paid prefixes, no expanded caps.'),
        dict(kind='budget',preregistered=True,rule='One existing worker/thread2GiB,one attempt,no retry/newcapacity. Original deadline2026-11-07T07:46:38.570520+00:00. Conservative remaining21600seconds deduct elapsed original one-worker window plus all pinned A16/A17/A18/A19 native and measured postprocessing CPU. No reset/reopened prior release.')]
    p['invalidation_rules']=['Missing exact published source/input/prospective protocol/current canonicalS3/root release/normal admission/lease/consumed marker or resource deadline prevents native execution.',
        'Old projection changed by helper knowledge, missing norm source floor, borrowed caches/labels, generated unknown-pool/target logs, auxiliary/target confusion, skipped complete queries, uncharged construction or aliases manufacturing triples invalidates a case.',
        'Independent pool/root/subgroup, group/constructor/pair/query/native assembly/target membership/cancellation/dense rank/kernel and counter payload checks must agree. Missing/failed cases remain unknown, not mathematical negatives.']
    p['inadmissible']=['Native pilot before exact prospective source approval/publication/freeze/release/normal gate.',
        'Raw augmented rank or extra unknown columns reported as original-base information; cancelling only targets while auxiliary columns remain; private helper anchors in common M.',
        'Treating separate unknown/known point sets as same-point knowledge causality, supplied labels as discovered logarithms, known target recovery as permission to skip unknown-base queries, or array bytes as operations.',
        'Weighted runtime/whole-attack/exponent/novelty or trusted independent proof claim from these finite producer observations.']
    p['extensions']=dict(model_verified=False,official_status_transition=False,grid='Four curves x4coldprograms x2actualsolvers=32exportrows;16case systems and16information diagnostics;4actual expanded-old semantic oracles.',
        ownership='All auxiliary/prelude builds before targets; complete own AP0source128/GENERAL8 with both endpoint engines, no query suppression. Shared mathematical fixtures do not lend private construction caches.',
        information='Common prerequisite substitution only in information projection; all own extra units/anchors remain K rows. U includes16aux slots plus8actual target columns, using actual rank. Source and full views with separate own K.',
        costs='Component vectors; physical dual engines and conditional single-engine views. Native joint, independent checkers, information diagnostics and curve/norm fixture generation separate. Diagnostic baseline floor projection separately in journal. Hash/pow/Python/NumPy/OS/IO/calibration partly unexpanded, no complete-S assertion.',
        proof_status='Producer checks/hash/Git/S3/admin readiness are not independently signed scientific/execution/replay proof.',
        literature='literature.md: A1/A2 cancellation precedents, A16 helper floors, A18 rank4/zero named units, organization residual collector and Nov1 byte-pricing correction. Existing generic cancellation/large-prime technique, no novelty claim.')
    p['links']=dict(design='design.md',literature='literature.md',prior='../prime_field_a19_execution_20261107/next-leads.md')
    p['literature']=[dict(ref='literature.md; A18 next-leads and full retained organization primary sources; A1/A2/A14/A15/A16 implementations',provenance='internal',verified_by='Root primary source review2026-11-07 before implementation',claim='Actual auxiliary-and-target cancellation, original-base/kernel information and own construction costs distinguish the proposed finite test; generic residual endpoints already exist.')]
    p['reporting']['graphs']=['Original-base reference/final ranks, total/direct/cross Delta and own-K/collected attribution; source/full marginal.',
        'Named independent target masks with deficient original-base rank where observed; actual cancellation/native controls.',
        'Separate pool/helper/prelude/source/pair/query/constructor/elimination/lifting/check/storage dimensions; no weighted winner. Failures/unknowns retained.']
    p['variable_ledger']['factors'].append(dict(name='formal_definition_boundary',treatment='fixed',value='One definition per distinct non-old auxiliary sign class',how='Reject old/previous sign classes; retain every rejected draw/cost but harvest no collision equations. Accepted definitions enter own source K after common units and before all collected rows. Definition-only auxiliary block is identity, giving zero old-base Delta conditional on this boundary; other own K may legitimately be informative.'))
    p['randomization']['instance_sampling']['rule']+=' Formal-pair draws hash domain|formal-pair|fullUID|index|counter; split integer into two distinct old native indices and two signs, canonicalize point with corresponding signed old coefficient vector. At most10000candidates/point. Neither target nor source yield selects a candidate.'
    p['decision_rule']['text']+=' Accepted formal definitions alone must have identity auxiliary block/zero old-base Delta. Actual own public coincidences remain K and need not have zero Delta. A separate signed expanded-old coefficient/public-point/dense semantic oracle must agree with native target unit membership and cancelled old-base ranks; preserve repeated coefficients and cancellations. This oracle is checker work, not another producer target solver.'
    p['controls']['positive']['not_applicable_reason']='Marked p<=211 formal-pool/native/expanded controls plus carried A19 controls: definition-only zeroDelta under explicit distinct/non-old invariant, legitimate informativeK, signed multiplicities up to six old occurrences, all four tiny cold programs, actual complete/all-missing32row exports and full-joint controls on all16native cases. No native pilot.'
    p['controls']['negative']['not_applicable_reason']='Reject wrong canonical signs/definitions/old aliases/duplicate points/rejected-collision knowledge, multiplicity loss and corrupt native/expanded weights; preserve nonrecoveries, coordinated cost edits, failed paid prefixes and native admission refusal.'
    p['measurement']['counters'].append('Formal old-point public subgroup/sign setup, direct candidate point adds/hashes/rejections/definition storage, all own full native pair builds, formal definition assembly and native lifts; independent expanded-old public/dense oracle CPU separately retained.')
    p['measurement']['record'].append('Four accepted formal dictionaries/one definition per distinct non-old class; no numeric labels in P caches. Source ordering is common supplied units, formal definitions, own cache/source/anchors, then target rows. Rejected equations never enter producer knowledge, even when baseline pair geometry could expose them.')
    for key,definition in [('formal_definition_rows','Actual native source rows with accepted formal_definition provenance; zero in other programs.'),('expanded_old_joint_rank','Independent expanded old-native-plus-target rank, applicable only to formal arm; native joint rank differs by auxiliary count.'),('definition_only_delta','Independent accepted definition-only old-base Delta control, conditional on one definition per distinct non-old auxiliary; null in other arms.')]:
        p['metrics']['primary'].append(dict(template,id=key,name=key.replace('_',' '),definition=definition,source='metrics.json rows and bound expanded-check.json'))
    p['extensions']['grid']='Fourcurves x4coldprograms x2actualsolvers=32exportrows;16cases/16informationdiagnostics and4expandedsemanticchecker calls, not32 independent target panels.'
    p['extensions']['formal_dictionary']='Accepted16 distinct non-old signclasses/one formal definition each; identity outside block aloneDelta0. No rejected-collision harvesting or numeric-label cache injection. Real constructor coincidences retained/attributed. Independent signed old-coefficient/public-point/dense expansion oracle and native controls.'
    p['extensions']['costs']+=' Formal pool uses own direct point additions before native pair-index build; no baseline table or abstract free reuse. All candidate costs/definition assembly/lifting retained. Expanded oracle is independently paid checker work.'
    p['reporting']['graphs'].append('Formal dictionary definitions, source/full own K contributions, expanded-old/native rank bridge and named target masks; failed/rejected candidate costs retained.')
    p['literature']=[dict(ref='literature.md; A19 next-leads and retained organization sources; native A19 information/cost controls',provenance='internal',verified_by='Root primary source read2026-11-07 before implementation',claim='Public signed-pair definitions are existing generic linear relations, not numeric helper logs. Compare actual successful-work and information after ALL outside cancellation, with no rejected-collision subsidy or novelty claim.')]
    return p


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    a=sub.add_parser('protocol');a.add_argument('--source-commit',required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--draft-preview',action='store_true');a.add_argument('--freeze',action='store_true')
    a=sub.add_parser('release');a.add_argument('--source-commit',required=True);a.add_argument('--protocol',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--owner',required=True);a.add_argument('--authorize-root',action='store_true',required=True)
    args=parser.parse_args();t=tools()
    if args.action=='protocol':
        if args.freeze and args.draft_preview:raise ValueError('draft cannot freeze')
        if not args.draft_preview:bindings(args.source_commit)
        value=make_protocol(args.source_commit);errors=t.schema_errors(value,'experiment.protocol/v1') or t.lint_protocol(value,HERE)
        if errors:raise ValueError(json.dumps(errors))
        write_once(args.out,value)
        if args.freeze:t.freeze(args.out,args.source_commit,True)
        print(json.dumps(dict(protocol=str(args.out),frozen=args.freeze)))
    else:
        source,inputs=bindings(args.source_commit);protocol=load(args.protocol)
        if protocol['freeze']['status']!='frozen' or protocol['freeze']['commit']!=args.source_commit or protocol['freeze']['filed_before_affected_data']is not True:raise ValueError('prospective exact-source freeze required')
        if any(v['instrument']['commit']!=args.source_commit for v in protocol['arms']):raise ValueError('instrument source differs')
        if subprocess.check_output(['git','show','HEAD:'+str(args.protocol.resolve().relative_to(ROOT))],cwd=ROOT)!=args.protocol.read_bytes():raise ValueError('commit frozen protocol unchanged')
        status=subprocess.run(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,capture_output=True,text=True,check=True)
        if 'last push : current ('not in status.stdout:raise ValueError('current actual canonical checkpoint required')
        checkpoint=(ROOT/'.resume/.last-push').read_text().strip()
        if not re.fullmatch(r'[0-9a-f]{64} \S+ s3://setec-astronomy-artifacts/checkpoints/\S+/',checkpoint):raise ValueError('canonical checkpoint receipt')
        now=datetime.now(timezone.utc);budget=remaining_budget(now)
        write_once(args.out,dict(schema='prime-field-a20-root-release/v1',execution_authorized=True,authority='Explicit bounded root release under standing user authorization; no official scientific status transition.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),
            protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,max_attempts=1,**budget,numpy_runtime=runtime_numpy.snapshot(),
            package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True,watchdog_seconds=budget['watchdog_seconds'],absolute_deadline=budget['absolute_deadline'])))


if __name__=='__main__':main()

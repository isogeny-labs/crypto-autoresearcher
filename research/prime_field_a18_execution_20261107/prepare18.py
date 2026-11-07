"""Prospective certified-query protocol and bounded remaining-window root release."""
import argparse,copy,json,subprocess,sys,re,importlib.metadata,math
from datetime import datetime,timezone,timedelta
from pathlib import Path
from deps18 import core
import runtime_numpy
from custody18 import HERE,ROOT,INPUTS,PARAMETERS,ARMS,bindings,digest,load,write_once,tools,BUDGET_INPUTS


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
    p=load(ROOT/'research/prime_field_a17_execution_20261107/protocol.json')
    p.update(protocol_id='PRIME-FIELD-A18-CERTIFIED-QUERY-TRANSFER-20261107',created='2026-11-07',study_dir=str(HERE.relative_to(ROOT)),
        question='On four fresh20/21-bit curves and32public targets at fixedknown48/fullGENERAL24, how do construction-prefix identifiability, remaining query coverage and separately paid costs transfer, retaining all final nonrecoveries?',
        freeze=dict(status='draft',protocol_sha256=None,commit=None,frozen_at=None,filed_before_affected_data=None),amendments=[])
    instrument=copy.deepcopy(p['arms'][0]['instrument']);instrument.update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()),build=[[sys.executable,'-B',str(HERE.relative_to(ROOT)/'driver18.py')]])
    descriptions={
        'suppress':('candidate','Four own known48/full24 constructions. Persistent eight-target row space, known substitution, unresolved membership and native/public certification before skipping later coordinates. Mandatory eight natural queries always paid.'),
        'full':('reference','Four independently cold known48/full24 constructions, all round-robin query slots, then actual partial_joint batch solve. Same public base/target/recipe identities, separately owned paid execution.'),
        'joint_on_suppress':('control_positive','Four actual native sparse_joint controls on exactly the candidate final pools; no borrowed full-reference rows.'),
        'joint_on_full':('control_positive','Four actual native sparse_joint controls on exactly the full-reference final pools.')}
    p['arms']=[dict(id=arm,role=descriptions[arm][0],description=descriptions[arm][1],instrument=copy.deepcopy(instrument),parameters=copy.deepcopy(PARAMETERS)) for arm in ARMS]
    p['authors']=['Root implementer and delegated administrative exact-source Coordinator; configured model identity unverified']
    p['claims']=[dict(id='A18-certified-query-suppression',**{'class':'exact_computation'},decided_by=['C-query-suppression'],text='Fresh finite named target outcomes, actual causally certified skips, row consequences, and separate paid primitive/array vectors. No predetermined saving, complete-cost/runtime advantage, novelty or transfer to unknown-base settings.')]
    reasons=dict(aa='Marked p<=211 deterministic repeats and independent exact group/constructor/matrix/counter checks; no clock inference.',
        positive='Seven additional A18 wrapper/attribution/export/truncated-journal controls and the carried26 A17 marked controls (actual A18 receipts named in readiness); the original seventeen marked p211 component checks with three known atoms include a real query producing a native/public certificate before later skips, and omitted reference rows reconstructed from the actual candidate. No fullwidth48 toy replay or native pilot.',
        negative='Future/borrowed/reordered or failed public certificates, missing known units/rows, altered assembly/scheduling costs even with coordinated hash edits, wrong policy/cache/owner/caps and failed paid prefixes rejected. Metadata controls do not execute native mathematics.')
    for key,reason in reasons.items():p['controls'][key]['not_applicable_reason']=reason
    p['randomization'].update(arm_order='fixed',arm_order_reason='Both independently paid public bases precede fresh target draw. Per curve suppress first, then full; each pays own pair/natural collection and complete GENERAL24 constructor/Registry before extra slots. Query round-robin step1..23 then target0..7. Candidate checks all unresolved coordinates after initial Registry, mandatory natural rows, and each executed extra slot. Full partial batch and native joint controls after each own pool. Postpair row-consequence diagnostic never feeds candidate.',
        seed_derivation=dict(method='explicit_list',seeds=[0]*16,nonce=None,note='Eight dependent case systems, four online primary engines and twelve actual batch calls, sixteen export execution rows; only four curves/32 public targets.'),
        instance_sampling=dict(independent_of_arm=True,rule='New domain, 36 pinned coefficient exclusions, first eligible a2 curves: two each F1048573/F2097143. Eight public canonical-y target hashes per curve after both base builds; no generated target scalar, redraw or outcome-dependent selection. Same mathematical known48 base built twice; duplicate construction is not a fresh mathematical base or independent target draw.'))
    p['sample_size']['instances']=4;p['sample_size']['power']['note']='Exact finite eight-case census: four matched curves/32 targets; four online engines plus twelve batch solver calls yield sixteen execution rows. No population or p-value inference.'
    p['variable_ledger'].update(independent=[dict(name='query_program',levels=['suppress','full']),dict(name='algorithm_execution',levels=ARMS)],
        factors=[dict(name='construction',treatment='fixed',value='Both own known48 and complete GENERAL24',how='Separate paid base/prelude/pair/index/natural queries, full P/Q planning/tables, all192 affine endpoints and complete Registry before extra queries; no construction saving.'),
            dict(name='safe_stopping_boundary',treatment='fixed',value='All 48 native supplied units',how='Retain all identity/base/same/cross-target equalities and natural rows. Skip only after own causal membership, original-native lift/check and public point check; unknown-base extension inadmissible.'),
            dict(name='cost_scope',treatment='fixed',value='Own complete cold physical and conditional vectors',how='Both endpoint engines physically execute. Single-engine views remove only other measured replay. Shared targets charged once per nonadditive cold view; controls/checkers separately retained.')],
        comparisons=[dict(id='C-query-suppression',arms=ARMS,design='factorial',differs_in=['query_program','algorithm_execution'],threshold='Exact target masks and full-reference row consequence witnesses, actual geometric queries versus skipped logical slots, separate eight Fp/Fr primitives and pair/query array bytes. Native joint controls compare own pools. No weighted winner or runtime inference.')],aa_not_applicable=reasons['aa'])
    p['decision_rule'].update(comparison_ids=['C-query-suppression'],statistic='Exact named masks, causally permitted skips, native row containment and separate included costs.',text='Compare own complete cold suppress versus full vectors for each curve. Every omitted reference row must follow from candidate rows, all supplied units and earlier certified target proofs. Record adverse/equal/incomparable vectors as observed. Online update/membership/lifting/public checks are charged; full reference batch scheduling differs. Neither skipped slots nor equal formal endpoints imply avoided physical query cost.')
    p['measurement'].update(counters=['Separate actual Fp/Fr add/sub/mul/inv, EC APIs and explicit pair/query NumPy allocation bytes; all own base/prelude/recipe/index/natural/full24 construction/cache/assembly/scheduling/primary algebra components.',
        'Actual physical endpoint engines, cache lookups/hits/geometric queries, certified/skipped/executed slots, online inserts/scans/lifts/checks, full batch and both-pool native joint controls.'],
        record=['Exact source/input/interpreter/NumPy identities, pre-output Git status and exact tracked/staged diffs, protected hashes before/after; no model identity or signed execution attestation invented.',
            'Producer outputs before checker receipts, immutable prefix certificates and paid failed phases; complete row-consequence proposals/checks after both programs, never candidate inputs.',
            'Actual PID-bound admitted-start canonical S3 before generation and four closed-writer curve checkpoints. One consumed release, one attempt, original deadline and conservative cumulative reservation; clocks invalid.'])
    definitions=dict(identified_targets='Number of the eight named public targets determined in this case.',identified_mask='Bit mask of named target indices, dependent across paired program/control views.',
        native_columns='Native base width including aliases; fixed48.',supplied_columns='Paid supplied-known native unit equations; fixed48, not learned information.',
        base_columns='Remaining unknown base coordinates after complete supplied substitution; zero.',target_rows='Actual retained native target rows in this own pool.',
        source_rows='Actual supplied native unit rows.',geometric_queries='Own distinct natural and derived cached points, not logical slots.',
        skipped_slots='Extra logical slots omitted only after earlier own verified certification.',executed_extra_slots='Actual extra requests including cache hits.',
        certified_targets='Targets with original-native/public prefix certificates.',formal_endpoints='All192 paid affine endpoints, including natural slots.',
        omitted_reference_rows='Full-reference native rows explained from candidate rows and earlier certificates; postpair diagnostic.')
    definitions.update(construction_certified='Candidate first certificates at the complete paid construction prefix; not independent query discoveries.',
        natural_certified='Candidate first certificates after all mandatory natural rows, excluding already certified construction targets.',
        extra_certified='Candidate first certificates after an executed extra-query prefix.',
        construction_mask='Named target mask first certified at complete paid construction.',natural_mask='Named target mask first certified after mandatory natural rows.',
        extra_mask='Named target mask first certified after extra query rows.',construction_registry_rows='Available complete Registry equations before natural-row insertion.',
        construction_target_rank='Independent diagnostic rank of the initial eight-target system after known-base substitution, not another target solver.')
    for op in ('add','sub','mul','inv'):definitions['fr_'+op]='Actual primary or native-control Fr '+op+' including native lifting/checks; pow internals unexpanded.'
    template=copy.deepcopy(p['metrics']['primary'][0]);p['metrics']['primary']=[dict(template,id=k,name=k.replace('_',' '),definition=v,source='metrics.json rows and analysis.json owned cold vectors') for k,v in definitions.items()];p['metrics']['secondary']=[]
    p['analysis_plan'].update(script=dict(path='analyze18.py',sha256=digest(HERE/'analyze18.py')))
    p['stopping_rules']=[dict(kind='fixed_n',preregistered=True,rule='Four fresh curves/32 targets, eight dependent native cases, four online primary engines plus twelve actual batch calls, sixteen export execution rows. No favorable early dataset stop or redraw.'),
        dict(kind='invalidation',preregistered=True,rule='Native48/joint64/pairs8192/rows4096/labels8192. GENERAL-only derived cache maximum192, complete24 construction and allRegistry.128 curve/field/target candidates,10000 base/scalar candidates. Retain paid prefixes and unknown remaining cases; no truncation or expanded caps.'),
        dict(kind='budget',preregistered=True,rule='One existing worker/thread,2GiB,one attempt,no automatic retry/new capacity. Original deadline2026-11-07T07:46:38.570520+00:00. At release deduct elapsed original window reservation plus all eight pinned prior native/postprocess measured CPU records from21600. This is a distinct fresh larger-field transfer study, not a third A16 attempt or reset allowance.')]
    p['invalidation_rules']=['Missing exact published closure, prospective freeze, root release, normal real admission, lease/consumed marker, original deadline/resource bound or actual start/closed checkpoints prevents complete-panel status.',
        'Any future/reference/checker/other-arm knowledge used for an online skip, certificate published before native/public checks, omitted mandatory natural or Registry rows, unknown native units, or constructor/query ownership/cost failure invalidates that case.',
        'Independent constructor/group/pair/query/counter/native matrix checks and full-payload commitments must agree. Candidate and full native joint controls must match own primary targets; independent row consequences must explain all reference rows.',
        'Phase conservation/journal bytes/checkpoint ordinals/PIDs and actual online/batch census must match. Unchecked payloads are unverified and missing cases remain unknown.']
    p['inadmissible']=['Native curve/target generation before exact published runnable source/input/protocol/current canonicalS3/root release/normal admission.',
        'Borrowing future or reference rows, suppressing unsupplied-base information, changing schedule/caps/targets after outcomes, or retrying a consumed release.',
        'Calling duplicate mathematical base constructions independent bases, repeated32 target outcomes independent draws, skipped slots physical queries saved, array traffic RSS, primitive vectors calibrated runtime/complete attack cost or novelty.']
    p['extensions']=dict(model_verified=False,official_status_transition=False,grid='Four curves x two owned programs = eight cases; candidate four online engines, full four partial_joint batch calls and eight own-pool sparse_joint controls. Sixteen algorithm export rows, not sixteen batch solver calls.',
        ownership='Both public48 base builds before targets; own complete GENERAL24 setup/192 endpoints/Registry, independent caches and natural8 queries. Candidate first; fixed round-robin extras; no future work subsidy.',
        safe_boundary='All base units supplied. Omitted-row native proof uses actual candidate rows plus earlier target certificate and known units; no unknown-base generalization.',
        cost_limits='Separate physical/conditional vectors and logical costs, nonadditive cold views. Curve generation/order/norm fixture, independent checkers/row diagnostic, hash/pow internals/Python/NumPy/OS/IO remain separately retained or partly unexpanded. No calibrated runtime/attack-cost assertion.',
        cloud_policy='Original deadline and conservative remaining-window reservation, one existing worker/thread2GiB/one attempt/no retry/new capacity.',
        checkpoint_semantics='Actual admitted-start/PIDs before generation and four closed-curve lossless gzip/hash checkpoints; no restore/restart.',
        proof_status='Producer checks/hash/Git/S3/admin readiness are not signed independent scientific/execution/replay proof.',
        literature='literature.md: A17 construction27/natural-new0/extra5 on32targets motivates fixed20/21bit transfer; no uniform coincidence or scaling model. Prior source-free known target recovery, online row membership, full-horizon constructors; A15 independent retained-row review leaves construction-vector/authenticated execution open. No novelty claim.')
    p['links']=dict(design='design.md',literature='literature.md',prior='../prime_field_a17_execution_20261107/next-leads.md')
    p['literature']=[dict(ref='literature.md; A16 full24/known48 results; A15 independent review; inherited native and target membership sources',provenance='internal',verified_by='Root primary source review2026-11-07 before implementation',claim='Restrict suppression to fully known base and retain full construction/online proof costs; source custody and independent signed execution remain distinct.')]
    p['reporting']['graphs']=['Disjoint candidate first-certificate masks/counts at complete construction, after natural rows and after extra-query prefixes; available Registry rows and independent target-column prefix rank.', 'Matched named target masks, actual geometric queries versus certified logical skips.', 'Separate own full construction, query, assembly and primary algebra vectors; no weighted winner.', 'Causal prefix certificates and every full-reference row consequence; failures/unknown cases retained.']
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
        write_once(args.out,dict(schema='prime-field-a18-root-release/v1',execution_authorized=True,authority='Explicit bounded root release under standing user authorization; no official scientific status transition.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),
            protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,max_attempts=1,**budget,numpy_runtime=runtime_numpy.snapshot(),
            package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True,watchdog_seconds=budget['watchdog_seconds'],absolute_deadline=budget['absolute_deadline'])))


if __name__=='__main__':main()

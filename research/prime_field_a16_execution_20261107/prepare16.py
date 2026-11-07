"""Prospective A16 finite target-effort protocol and one-attempt root release."""
import argparse,copy,json,subprocess,sys,re,importlib.metadata
from datetime import datetime,timezone,timedelta
from pathlib import Path
from deps16 import core
import runtime_numpy
from custody16 import HERE,ROOT,INPUTS,PARAMETERS,bindings,digest,load,write_once,tools
from programs16 import PROGRAMS,descriptors


def make_protocol(commit):
    rules=load(INPUTS);plans=list(descriptors(rules))
    if len(plans)!=1260 or 2*len(plans)!=2520 or sum(d['base_arm']=='hybrid' for _,d in plans)!=576:
        raise ValueError('exact prospective1260/2520/576 census')
    p=load(ROOT/'research/prime_field_a14_execution_20261106/protocol.json')
    p.update(protocol_id='PRIME-FIELD-A16-INDEPENDENT-TARGET-EFFORT-20261107',created='2026-11-07',study_dir=str(HERE.relative_to(ROOT)),
        question='On four fresh matched coefficient curves and32public targets, what named target identities and separately included cold costs result from source-free known48 at independently constructed horizon24 versus cold horizon8 and norm32+known16 helper/source128 horizon8, with norm32 and known32 controls?',
        freeze=dict(status='draft',protocol_sha256=None,commit=None,frozen_at=None,filed_before_affected_data=None),amendments=[])
    instrument=copy.deepcopy(p['arms'][0]['instrument']);instrument.update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()),build=[[sys.executable,'-B',str(HERE.relative_to(ROOT)/'driver16.py')]])
    p['arms']=[dict(id=name,role=role,description=description,instrument=copy.deepcopy(instrument),parameters=copy.deepcopy(PARAMETERS)) for name,role,description in [
        ('partial_known','candidate','1260actual known-unit-substituted joint target membership calls, original norm unknown ordering and full native-unit/raw-row lifting; all-known specialization retains zero remaining base unknowns.'),
        ('joint_reference','reference','1260actual full native sparse joint calls on exactly the same cases, with original-row and public target checks. Neither method is a third information-diagnostic execution.')]]
    p['authors']=['Root implementer and delegated administrative exact-source Coordinator; configured model identity unverified']
    p['claims']=[dict(id='A16-fresh-target-effort',**{'class':'exact_computation'},decided_by=['C-target-effort'],
        text='Finite fresh held-out public target identities and separate paid constructor/collection/algebra vectors, with independent8/24 full-horizon portfolios and actual common batch pairs. No predetermined winner, novelty, calibrated complete-cost/runtime or whole-attack claim.')]
    reasons=dict(aa='Deterministic marked tiny repeat/JSON controls and exact independent constructors/group/matrix checks; no timing comparison or repeated-clock inference.',
        positive='Markedp<=211 complete8/24 branches/all3policies, native lifted target certificates on explicit small3known-atom fixtures; prior/native48 pair baseline controls retained. No fullwidth48/horizon24 toy replay is claimed.',
        negative='Borrowed horizon caches/recipes/future knowledge, retagged ownership, wrong fullworkload predictions, missing/altered output/cost/checkpoints, native admission refusal, row/label/cache caps and failed paid prefixes are retained/rejected. Dense tiny known48 cap refusal remains valid;4096 native limit unchanged.')
    for key,reason in reasons.items():p['controls'][key]['not_applicable_reason']=reason
    p['randomization'].update(arm_order='fixed',
        arm_order_reason='Per curve independently build hybrid16/known32_8/known48_8/known48_24 before targets; prepare norm8/hybrid8/known32_8/known48_8/known48_24, select shared public targets, derive8and24recipes independently/checkfirst8prefix. Process programs in that order; source programs AP0/hash0/AP1/hash1/AP2/hash2, all walk/hash_offset/general; shortprefix1/2/4/8 relations/anchors orsupplied; longprefix24only supplied. Eachcase partial_joint then native sparse_joint; matched information diagnostic after hybrid. Both endpoint engines physically execute. No clock inference.',
        seed_derivation=dict(method='explicit_list',seeds=[0]*2520,nonce=None,note='1260dependent systems/2520actual algebra calls. Four curves/32public target points; source/policy/budget/scope/horizon views are dependent.'),
        instance_sampling=dict(independent_of_arm=True,rule='Four first-eligible fresha2 coefficient curves,2eachF262139/F524287,norm32,28pinnedprior coefficient exclusions,new domain. Eight public canonical-y target hashes/curve after all paid base constructors, no target scalar generation or redraw. Identical first48public label recipe for both known48 programs, separately executed construction/cost; symbolic8recipeprefix matches24 but no shared future tables/caches. Fresh coefficients are not a theorem of independent isogeny classes or decomposition distribution.'))
    p['sample_size']['instances']=1260;p['sample_size']['power']['note']='Exact finite census1260dependent systems/2520actual calls/576separate diagnostics, four fresh curves/32public targets. Fiveprogram contexts/curve include two independent executions of the same known48 mathematical base. No population/p-value inference.'
    p['variable_ledger'].update(independent=[dict(name=name,levels=levels) for name,levels in [
        ('program',[v['id'] for v in PROGRAMS]),('target_horizon',[8,24]),('source_schedule',['ap0','hash0','ap1','hash1','ap2','hash2','known(source-free)']),
        ('target_policy',rules['target_policies']),('target_prefix',[1,2,4,8,24]),('scope',['relations','anchors','supplied']),('solver',['partial_joint','sparse_joint'])]],
        factors=[dict(name='held_out_targets',treatment='fixed',value='Same32public points across programs',how='Newdomain28exclusions; select after independent paid public base constructions; keep overlaps, no rank/yield/cost-based selection.'),
            dict(name='full_horizon_construction',treatment='fixed',value='Independent8/24 fullworkload prediction/tables/caches/registries',how='Checkfirst8symbolicrecipes only; short program cannot use24optimized setup or intermediate knowledge. Long reports24only.'),
            dict(name='pair_builder',treatment='fixed',value='ActualA15batched signed-pair builder for every program',how='Own setup/arrays/tables with independent plain pair/Fp/allocation control; no scalar-equivalent group-call estimates.'),
            dict(name='old_norm_coordinates',treatment='fixed',value='Original prerequisite64projection/signedunknown order',how='Helper cache matches remain supplied old-coordinate equations; no silent dropping or cross-known-base rank comparison.')],
        comparisons=[dict(id='C-target-effort',arms=['partial_known','joint_reference'],design='factorial',
            differs_in=['program','target_horizon','source_schedule','target_policy','target_prefix','scope','solver'],
            threshold='Exact named masks plus separate included vectors. Primary cold program comparisons use partial_joint in both, native joint is the actual same-case control. Known48_24 at24 vs known48_8/hybrid8/norm8/known32_8 at8; retain short-program prefix controls and all adverse/equal/incomparable cases.')],
        aa_not_applicable='Marked deterministic controls and independent exact checks; no timing inference.')
    p['decision_rule'].update(comparison_ids=['C-target-effort'],statistic='Exact named target masks, owned-horizon physical/conditional included vectors and matched old-coordinate information.',
        text='Compare independently cold known48_h24 versus known48_h8 and matched hybrid source128/target8, retaining norm32/known32 controls.192=8*24=128+8*8 is only logical endpoints, not equal cost. Compare target inclusion and actual separate8FpFr+pair/queryallocation vectors and retained logical counters; no weighting/calibrated gain. Only norm8/hybrid8 use old-base Delta with native outside cancellation; source-free certainty is supplied not learned rank. All views dependent.')
    p['measurement'].update(counters=['Separate actualFp/Fr add/sub/mul/inv and EC APIs, constructor prediction/wrapper/cache/sign/query/table/hash counters, explicit pair/query NumPy allocation traffic.',
        'Own four public base constructor executions percurve (hybrid16,known32_8,known48_8,known48_24), prelude/source recipe/source construction, fullhorizon targetP/Q selection/tables/cache and each actually used query; no free future/cross-program cache.',
        'Known-unit substitution, target membership, full native row/unit lifting/public checks, native joint control;576separate original-coordinate outside-cancellation/dense-kernel diagnostics, not extra target solvers.',
        'Physical campaign vectors and nonadditive cold views, selected source/policy/prefix/horizon, bothactualendpointenginecontrols and singleengine references; include pair and query array traffic separately.'],
        record=['Exact source/input/interpreter/NumPy identities and every rejected field/curve/base/target/source/recipe candidate. FreshEC1/base identities and duplicate mathematical48base construction ownership kept distinct.',
            'Full producer output/cost commitments and separate group/constructor/Fp/array/matrix checker receipts, native positive/negative target certificates, failed phase and selection prefixes immediately retained.',
            'Admitted-start actual canonical S3 before generation with PIDbinding; four paused closedcurve gzip/hash/byte checkpoints, one consumed attempt/no restore/retry; child/supervisorCPU/RSS and wall_valid=false.'])
    definitions=dict(target_horizon='Complete independently paid target-constructor planning horizon,8or24; shortprefix views still pay own full8setup.',
        identified_targets='Number of named requested targets determined in this case; repeated source/policy/budget views are dependent.',
        source_rank='Rank of original remaining norm coordinates after declared native supplied units; zero remaining coordinates for source-free all-known.',
        native_source_rank='Native source rank including supplied units, never learned information across known programs.',
        supplied_columns='Declared native unit equations; paid supplied labels rather than learned rank.',native_columns='Original native32/48slots including aliases.',
        base_columns='Remaining old signed norm unknown columns; zero for known-only programs.',outside_rank='Rank of actual eight-target U.',
        delta='Within-case rank([[M,0],[B,U]])-rank(U)-rank(M), after supplied substitution on matching coordinates.',
        after_cancellation_rank='Original-base information after cancelling actual target U; no cross-base rank gain.',
        source_rows='Original native supplied/cache/collected rows.',target_rows='Native target decomposition/available affine equations.',
        decomposition_rows='Distinct-geometric signedthree-term rows.',knowledge_rows='Own paid scope-available affine equalities.')
    for op in ('add','sub','mul','inv'):definitions['fr_'+op]='Actual selected solver Fr '+op+', including substitution/lifting/original verification; internal inversion/pow unexpanded.'
    metric=copy.deepcopy(p['metrics']['primary'][0]);p['metrics']['primary']=[dict(metric,id=name,name=name.replace('_',' '),definition=definition,source='metrics.json rows and analysis.json cells/owned cold vectors') for name,definition in definitions.items()];p['metrics']['secondary']=[]
    p['analysis_plan'].update(script=dict(path='analyze16.py',sha256=digest(HERE/'analyze16.py')))
    p['stopping_rules']=[dict(kind='fixed_n',preregistered=True,rule='Four freshcurves32targets;1260dependent systems2520actual paired native calls576separate diagnostics. No favorable early stop or newdraws.'),
        dict(kind='invalidation',preregistered=True,rule='Native48,joint64,pairs8192,rows4096,labels8192,p<2^32; maximumderivedtargetcache176at8/560at24, actualaliasesallowed.128field/curve/targetcandidates,10000source/basecandidates. Retain prefixes/unknownremaining, no truncation/redraw.'),
        dict(kind='budget',preregistered=True,rule='One existingworker/thread,2GiB,21600CPU/wall seconds,freshabsolute deadline,oneattempt,noautomaticretry/newpaidcapacity.')]
    p['invalidation_rules']=['Absent exact-source/input/runtime/release/lease/deadline or normal real admission/checkpoints/correctness/cost receipts prevents complete-panel status; retain all work.',
        'Program/horizon ownership, fullworkload predictions and recipeprefixes must agree. No first8-from24 control, cross-horizon registry/cache/point-label transfer or unpaid public base prefix.',
        'Every program uses actual batched pair geometry with original native aliases/signs, independently checked arithmetic/allocation and complete group/query/miss truth.',
        'Partial/native joint outcomes agree, full row/unit/public certificates correct; old-base outside cancellation matches dense ranks/kernel action and unchanged original norm basis.',
        'Full producer/cost payloads bind checker receipts, journal bytes, phase conservation and exact checkpoint identities/ordinals/PIDs. Unchecked outputs remain unverified; missing cells remain unknown.']
    p['inadmissible']=['Freshnativecurves/targets before exactpublishedrunnableclosure/prospectivefreeze/currentcanonicalS3/explicitrootrelease/normaladmission.',
        'Target/source/base selection or schedule/guard expansion afterobservingresults; retry/newpaidcapacity under same release.',
        'Reused targets or duplicate48construction called independent draws/freshbases; known labels called learnedrank; conditional views added as separateexecutions.',
        'Equal endpointcounts called equalcost, explicitarraytraffic calledRSS, vectorEC APIzero calledzeromath, primitive/partial vectors called calibrated runtime/completeS/wholeattack or novelty.']
    p['extensions']=dict(model_verified=False,official_status_transition=False,grid='programs16.descriptors:1260systems/2520actualpartial_joint+sparse_joint;576matched separate information diagnostics.',
        horizons='Independent full8/24 target portfolios; symbolic first8recipes match. Own two physical known48 public base executions before targets; same mathematical base identity, separate program costs/provenance.',
        cache_gates={'8':176,'24':560},checkpoint_semantics='Actualadmitted-start/PIDs before generation and four closedcurve checkpoints after allwriters close/losslessgzip. No restart/restore.',
        cold_costs='Own public base/prelude/index/naturalqueries+shared targetgeneration+selected source/recipe+own fullhorizon constructor through chosenprefix+uniqueusedqueries+nativeassembly+selectedsolver. Single endpointengine references remove only otheractualengine replay. Info/oracle/checkers separate; viewsnonadditive.',
        cost_limits='Generation/order/norm selection, hashing/inversion/pow internals, checker/denseatlas, Python/NumPy hidden temporaries/OS/IO/storage notfullycalibrated; inclusive diagnosticresources and invalidsharedhostclocks retained.',
        cloud_policy='One existingworker/thread2GiB21600CPU/walloneattempt,freshdeadline,no newpaidcapacity.',
        proof_status='Producerlocalchecks/hash/S3/sourceadminreadiness nottrustedscientific/replay/executionproof. TypedartifactpinnedPCCcitations remainunverified untilindependentsignedstanding.',
        literature='literature.md:existing affinealphaP+betaQ/known-unit/outside cancellation/signed batching;PKM2016p8rough-costwarning;research-kb unavailable, directsourcefallback, no novelty.')
    p['links']=dict(design='design.md',literature='literature.md',prior='../prime_field_a15_execution_20261107/next-leads.md')
    p['literature']=[dict(ref='literature.md; A14 affine_branch/target_cache/mixed_collection/native_case/cold14; A12 affine_core; A15 pairbuild15/check15',provenance='internal',verified_by='Root primary source/interface review2026-11-07 beforeimplementation',claim='Full-horizon constructor choice changes setup knowledge/cost; independent8/24 controls and existing actual common pair baseline required.'),
        dict(ref='https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf §3.2,p8',provenance='retrieved',verified_by='Carried retainedprimaryPDF reread2026-11-07,SHAa53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b',claim='Mixed field/scalar unit costs explicitlyrough; no completecalibration here.')]
    p['reporting']['graphs']=['Named fresh target masks/recovery by program/horizon/policy/budget with dependent views explicit.',
        'Separate public base/PQ/source/pair/query/algebra vectors and explicit pair/query arrays, no weighted runtime.',
        'Matched old-norm supplied/collected/cancelled-target information, native mask counterexamples and every incomplete/failed prefix.']
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
        if protocol['freeze']['status']!='frozen' or protocol['freeze']['commit']!=args.source_commit or protocol['freeze']['filed_before_affected_data']is not True:
            raise ValueError('prospective exact-source freeze required')
        if any(v['instrument']['commit']!=args.source_commit for v in protocol['arms']):raise ValueError('instrument source differs')
        if subprocess.check_output(['git','show','HEAD:'+str(args.protocol.resolve().relative_to(ROOT))],cwd=ROOT)!=args.protocol.read_bytes():raise ValueError('commit frozen protocol unchanged')
        status=subprocess.run(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,capture_output=True,text=True,check=True)
        if 'last push : current ('not in status.stdout:raise ValueError('current actual canonical checkpoint required')
        checkpoint=(ROOT/'.resume/.last-push').read_text().strip()
        if not re.fullmatch(r'[0-9a-f]{64} \S+ s3://setec-astronomy-artifacts/checkpoints/\S+/',checkpoint):raise ValueError('canonical checkpoint receipt')
        now=datetime.now(timezone.utc)
        write_once(args.out,dict(schema='prime-field-a16-root-release/v1',execution_authorized=True,authority='Explicit root release under standing userauthorization, no officialscientifictransition.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),
            protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,watchdog_seconds=21600,absolute_deadline=(now+timedelta(seconds=21600)).isoformat(),max_attempts=1,
            numpy_runtime=runtime_numpy.snapshot(),package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True)))


if __name__=='__main__':main()

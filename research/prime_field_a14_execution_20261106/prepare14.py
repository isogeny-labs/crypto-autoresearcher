"""Prospective A14 protocol and explicit one-attempt root release."""
import argparse, copy, importlib.metadata, json, re, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from shared import core
import runtime_numpy
from custody14 import HERE, ROOT, INPUTS, PARAMETERS, bindings, digest, write_once, tools, load, descriptors, methods


def make_protocol(commit):
    rules = load(INPUTS)
    plans = list(descriptors(rules))
    if len(plans) != 1248 or sum(len(methods(v)) for _, v in plans) != 2496:
        raise ValueError('exact prospective A14 census')
    p = load(ROOT/'research/prime_field_a13_execution_20261106/protocol.json')
    p.update(protocol_id='PRIME-FIELD-A14-MIXED-KNOWN-HELPERS-20261106', created='2026-11-06',
        study_dir=str(HERE.relative_to(ROOT)),
        question='What original-norm information and named target identities result from adding sixteen independently paid public-log helpers, compared with unchanged norm32 and source-free paid known32/known48 under separate cold construction and algebra costs?',
        freeze=dict(status='draft', protocol_sha256=None, commit=None, frozen_at=None, filed_before_affected_data=None), amendments=[])
    instrument = copy.deepcopy(p['arms'][0]['instrument'])
    instrument.update(commit=commit, binary_sha256=digest(Path(sys.executable).resolve()),
        build=[[sys.executable, '-B', str(HERE.relative_to(ROOT)/'driver14.py')]])
    p['arms'] = [dict(id=name, role=role, description=description, instrument=copy.deepcopy(instrument),
        parameters=dict(PARAMETERS, inputs_sha256=digest(INPUTS))) for name, role, description in [
            ('partial_known', 'candidate', 'Substitute exactly the declared supplied native units, retain original signed norm unknowns, solve eight joint target functionals, lift through all native unit/raw rows;1248 actual calls.'),
            ('joint_reference', 'reference', 'Fully charged native sparse joint solver on the identical native case, including supplied units and original-row/public checks;1248 actual calls.')]]
    p['claims'] = [dict(id='A14-mixed-known-helpers-finite', **{'class':'exact_computation'},
        decided_by=['C-mixed-known-helpers'], text='Producer finite target identities, original-base information and separate included conditional costs. Known-log substitution/cancellation/affine construction are established methods; no novelty, calibrated complete-cost/runtime or whole-attack claim.')]
    p['controls']['aa']['not_applicable_reason'] = 'Tiny deterministic repeated construction, sorted-JSON roundtrips and separately checked public/integer/matrix certificates; no repeated-clock inference.'
    p['controls']['positive']['not_applicable_reason'] = 'Marked p<=211 full four-program collection/branches/native lifted target certificates, independent geometric atlas and dense ranks/kernel action; all-known specialization matches the prior direct solver including Fr counters.'
    p['controls']['negative']['not_applicable_reason'] = 'Altered signs/units/labels/points/provenance/recipes, borrowed caches, outside weights/lifts, missing rows/residuals, cap failures and admission refusal reject. The dense tiny known48 budget3 cap refusal is retained; native4096 limit remains fixed.'
    p['randomization'].update(arm_order='fixed',
        arm_order_reason='Per curve build16/32/48 independently before targets; prepare norm/hybrid/known32/known48 then generate targets once. Process programs in that order, norm/hybrid AP0/hash0/AP1/hash1/AP2/hash2; each walk/hash_offset/general, budgets1/2/4/8 and relations/anchors. Known programs source-free, supplied scope. Each case partial_joint then native sparse_joint. Both scalar and batch physically execute per endpoint. Hybrid information audit follows its paired case; no clock inference.',
        seed_derivation=dict(method='explicit_list', seeds=[0]*2496, nonce=None,
            note='Export instance IDs0..1247 are the fixed descriptors, with two actual algebra arms each; reused source/scope/budget views do not create new targets.'),
        instance_sampling=dict(independent_of_arm=True,
            rule='Four first-eligible fresh curves, two per F262139/F524287,a2,norm32;24old coefficients excluded by pinned A13 rules/generated. Eight public unknown-label canonical-y targets/curve selected after all paid base constructors. Helpers are first16 of the public scalar recipe but separately constructed with their own16-workload portfolio/cache; known32/48 independently execute their own full workloads. Keep helper/norm overlaps without redraw; query each geometric sign class once.'))
    p['sample_size']['instances'] = 1248
    p['sample_size']['power']['note'] = '1248dependent systems/2496actual target-solver calls; norm576,hybrid576,known32=48,known48=48. Four curves/32public target points.576separately metered hybrid-vs-norm information diagnostics are not extra target solvers or independent draws. No population/p-value inference.'
    p['variable_ledger']['independent'] = [dict(name=name, levels=levels) for name, levels in [
        ('base_program', rules['base_arms']), ('source_schedule', ['ap0','hash0','ap1','hash1','ap2','hash2','known(source-free)']),
        ('target_policy', rules['target_policies']), ('target_prefix', rules['target_prefixes']),
        ('knowledge_scope', ['relations','anchors','supplied']), ('solver', ['partial_joint','sparse_joint'])]]
    p['variable_ledger']['factors'] = [
        dict(name='curve_public_targets', treatment='fixed', value='Four curves/32public targets matched across four programs', how='Fresh separated hash domain and24exclusions; no target scalar, rank/yield/cost selection or redraw.'),
        dict(name='query_engines', treatment='fixed', value='Scalar and batch physically execute per endpoint on each program geometry', how='Paid own pair/sign/index setup, same known batch inversion/fallback; one geometric matrix stream. Single-engine cold references subtract the other replay.'),
        dict(name='old_norm_basis', treatment='fixed', value='Original prerequisite64 projection and original signed unknown order', how='Helper cache matches become explicit supplied equations on old coordinates; no dropping/renumbering old unknowns or counting helper slots as unknowns.')]
    p['variable_ledger']['comparisons'] = [dict(id='C-mixed-known-helpers', arms=['partial_known','joint_reference'],
        design='factorial', differs_in=['base_program','source_schedule','target_policy','target_prefix','knowledge_scope','solver'],
        threshold='Exact target identities, outside-corrected original-base information and separate included cold vectors; retain equal, adverse and incomparable results.')]
    p['decision_rule'].update(comparison_ids=['C-mixed-known-helpers'],
        statistic='Exact named target masks and separate cold counters; original-base Delta only for matched norm/hybrid coordinates.',
        text='Compare partial/native joint target outcomes on identical cases. Compare hybrid with matched norm and either source program with each source-free known control; known48 vs known32 separately. Primary cold comparisons use partial_joint in both programs. For matched norm/hybrid attribute supplied cache information before collected rows, then outside-cancelled target rows against the old norm M. No result-selected expansion or unmeasured complete-cost claim.')
    p['measurement']['counters'] = [
        'Separate actual Fp/Fr add/sub/mul/inv, scalar construction/API/hash/sign/lookup/pair/query/copy and explicit NumPy allocation counters.',
        'Own16/32/48 hash-labelled construction portfolios and selected physical workloads; no32/48cache subsidizes16. Norm/hybrid prerequisites/selected source construction and queries; known controls no source work.',
        'Native supplied units/cache matches/collected rows, partial known substitution, arbitrary eight-target membership, full original-row lifting and public scalar checks; native joint control separately charged.',
        '576separate information diagnostics: reference/hybrid substitution, supplied/collected elimination, outside cancellation and native unit lifting; dense audit of rank identity and old kernel action. These are diagnostic overhead, not free solver work.',
        'Physical campaign counters and nonadditive one-program cold references. Select only that source recipe/program/policy; common target generation paid once per cold reference. Include every used nonnatural query once even if physically cached by another branch.']
    p['measurement']['record'] = [
        'Exact source/input/interpreter/NumPy identities, all rejected field/curve/base/target/source candidates and EC1/base identities.',
        'Raw journals and every native input/output/check/branch/information certificate, byte-bound before analysis. Full geometric triple/miss oracles and paid phase records including failures.',
        'Original32 unknown coordinates, explicit supplied cache equations, positive/negative target membership and native certificates; symbolic Q coefficients never imported as P logs.',
        'Four closed-curve gzip roundtrips/canonical checkpoints; one consumed attempt without restart, source unchanged; inclusive child/supervisor CPU/RSS, unisolated wall_valid=false.']
    definitions = dict(identified_targets='Identified requested target units; repeated slots are dependent views of32public points.',
        source_rank='Rank on original remaining norm coordinates after declared native-unit substitution; known32/48 have zero remaining coordinates. Supplied cache matches remain explicit.',
        native_source_rank='Rank of original native supplied+collected source equations; supplied labels never learned rank.',
        supplied_columns='Declared fixed-known native norm/helper or source-free native unit equations.',
        native_columns='Actual32/48 native coefficient slots; helper aliases remain native slots but are queried once geometrically.',
        base_columns='Unchanged original signed norm unknown width; zero for source-free all-known programs.',
        outside_rank='Rank of actual eight-target U.', delta='rank([[M,0],[B,U]])-rank(U)-rank(M) within this case; never cross-base rank gain.',
        after_cancellation_rank='Native joint rank minus U rank and declared known-unit count; original-coordinate base information.',
        source_rows='Native supplied-unit/cache and collected source equations, with provenance retained.',
        target_rows='Native requested-target decomposition and scope-available symbolic construction equations.',
        decomposition_rows='Distinct-geometric-atom signed three-term target equations.', knowledge_rows='Paid symbolic construction equalities available within budget/scope.')
    for op in ('add','sub','mul','inv'): definitions['fr_'+op] = 'Actual selected solver Fr.'+op+', including known substitution/lifting and original/public checks; internal pow/inversion work unexpanded.'
    metric_template = copy.deepcopy(p['metrics']['primary'][0])
    p['metrics']['primary'] = [dict(metric_template, id=name, name=name.replace('_',' '), definition=definition,
        source='metrics.json columns/rows and analysis.json cells/solver_counters') for name, definition in definitions.items()]
    p['analysis_plan']['script'] = dict(path='analyze14.py', sha256=digest(HERE/'analyze14.py'))
    p['stopping_rules'] = [dict(kind='fixed_n', preregistered=True, rule='Four curves/32targets;norm576+hybrid576+known32=48+known48=48 systems;two actual algebra calls each=2496.576separate matched information diagnostics. Continue through early recovery/zero; no retry.'),
        dict(kind='invalidation', preregistered=True, rule='128field/curve/target candidates,10000source/base candidates;native<=48,G<=48,8192signedpairs,4096totalmatrix/retainedrows,8192affinelabels,64jointcolumns,176targetcachepoints/program,p<2^32. Keep every overlap/failure prefix and unknown remaining work; no truncation/redraw.'),
        dict(kind='budget', preregistered=True, rule='One existing worker/thread,2GiB,21600CPU/wall seconds,one attempt,fresh absolute deadline;no automatic retry/new paidcapacity.')]
    p['invalidation_rules'] = [
        'Exact-source/input/runtime mutation, admission/lease/deadline refusal, absent raw/checkpoint/oracle records or invalid public/linear/counter certificates prevents complete-panel status; retain partial work.',
        'Every paid base is fixed before targets and executed independently. Own helper16/known32/known48 caches only; same original norm coordinates and matched public source recipes. No checker/future/other-source/base cache imports.',
        'Helper/cache revelations of old unknowns remain supplied native equations on unchanged old coordinates; no dimension inflation, geometric duplicate triples or redraw.',
        'Partial target results agree with fully charged native joint/dense controls; every certificate lifts to original units/raw rows, including affine RHS and signed native coefficients. Negative membership/residuals retained.',
        'Information diagnostics check complete outside cancellation/native lifting and dense Delta/old-kernel action; supplied first, collected next, cancelled targets last. Known-only base ranks are never compared as information gains.',
        'Both query engines physically execute; single-engine cold views remove replay and preserve actual setup/fallback/dummy/allocation costs. Unexpanded primitives forbid calibrated complete-cost/runtime assertions.']
    p['inadmissible'] = [
        'Fresh native generation before complete published source/inputs, prospective frozen protocol, current actual canonical S3, explicit root release and normal admission.',
        'Free helper prefix from a32/48constructor, source-forced known controls, cache unions/checker logs/future labels or paid knowledge reported as learned rank.',
        'Cross-base Delta, raw rank inflation, reused target slots called independent draws or incomplete vectors called complete calibrated gains.',
        'Retry/restore/new paid capacity or favorable-result-conditioned base/source/target/budget changes under the single attempt.']
    p['extensions'] = dict(model_verified=False, model_identity=None, official_status_transition=False,
        grid='descriptors(rules):1248systems;methods(desc):partial_joint then sparse_joint;2496actual calls. Export partial_known/joint_reference share identical instance IDs.576separate information audits are not target-solver calls.',
        supplied_and_geometry='Original32 unknown order fixed by prerequisite64;16paidhelper native slots substituted, overlaps explicitly supplied on old coordinates. Pair/triple query distinct geometric sign classes; native coefficients/certificates retain all slots.',
        attribution='For each hybrid case, match norm source/policy/budget/scope. Start M0 norm reduced source; add H supplied cache matches, then C hybrid collected source/anchors, then ker(U) target combinations. DeltaVsOld=rank([[M0,0],[H,0],[C,0],[B,U]])-rank(U)-rank(M0). Dense checker retains old kernel actions and native cancellation weights.',
        cold_costs='Own base constructor/prelude/index/natural queries+shared target generation+selected source recipe/construction/query+one target policy through budget+required unique target queries+native assembly+chosen solver. Physical diagnostic/checker work separate. Known controls no source queries. Conditional vectors dependent, never summed as distinct executions.',
        comparisons='Primary partial_joint cold views: norm vs eachknown; hybrid vs matchednorm and eachknown; known48 vs known32, bothengines.5856dependent paired engine comparisons include equal/empty masks. Arithmetic8FpFr plus explicit query allocation vector and allretained logical vectors separate; no rank/cost calibration inference.',
        checkpoint_semantics='Close curve writers, losslessgziproundtrip then paused canonical S3 checkpoint; no hot mutable journal snapshot or native restoration/retry.',
        proof_status='Producer local checks/hash/S3 custody are not trusted signed PCC scientific/replay/execution proof. New quantitative citations require typed artifact-pinned PCC claims and unverified tag absent trusted signed standing.',
        cost_limits='Generation/norm-base selection, hashing/pow/inversion internals, checker/dense atlas, Python/NumPy temporaries/OS/IO not fully calibrated. Separate counters and inclusive diagnostic resources; no complete S/rho/runtime/whole-attack advantage.',
        cloud_policy='One existing localworker/thread2GiB21600CPU/wall one attempt;no new paid capacity. Existing storageauthorization, no secrets in repository.',
        literature='literature.md/current exact components: established known-log substitution, affine alphaP+betaQ, outside cancellation, source/table/batch controls. PKM2016§3.2 rough cost warning. Research-kb unavailable; scoped direct-source fallback, no novelty or corpus-wide absence.')
    p['links'] = dict(design='design.md', controls='controls-refinement.md', literature='literature.md', prior='../prime_field_a13_execution_20261106/next-leads.md')
    p['literature'] = copy.deepcopy(p['literature'])+[dict(ref='research/prime_field_a14_execution_20261106/literature.md; mixed_collection.py; partial_solver.py; information.py', provenance='internal', verified_by='Root source implementation and separate plain-group/dense controls,2026-11-06; final administrative assessment required before release', claim='Exact supplied/native/old-coordinate maps and metered pipeline; established linear algebra, not new scalar symmetry.')]
    p['reporting']['graphs'] = ['Named target recovery by four programs/policy/budget with dependent reuse labelled',
        'Supplied/collected/cancelled-target information on matched old norm coordinates',
        'Separate own construction/source/query/algebra/diagnostic counters, no calibrated complete-cost/runtime claim']
    return p




def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('protocol');a.add_argument('--source-commit',required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--freeze',action='store_true');a.add_argument('--draft-preview',action='store_true')
    a=sub.add_parser('release');a.add_argument('--source-commit',required=True);a.add_argument('--protocol',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--owner',required=True);a.add_argument('--authorize-root',action='store_true',required=True)
    args=p.parse_args();t=tools()
    if args.action=='protocol':
        if args.freeze and args.draft_preview:raise ValueError('draft cannotfreeze')
        if not args.draft_preview:bindings(args.source_commit)
        value=make_protocol(args.source_commit);errs=t.schema_errors(value,'experiment.protocol/v1') or t.lint_protocol(value,HERE)
        if errs:raise ValueError(json.dumps(errs))
        write_once(args.out,value)
        if args.freeze:t.freeze(args.out,args.source_commit,True)
        print(json.dumps(dict(protocol=str(args.out),frozen=args.freeze)))
    else:
        source,inputs=bindings(args.source_commit);protocol=load(args.protocol)
        if protocol['freeze']['status']!='frozen' or protocol['freeze']['filed_before_affected_data']is not True or protocol['freeze']['commit']!=args.source_commit:raise ValueError('prospective exactsourcefreeze required')
        if any(v['instrument']['commit']!=args.source_commit for v in protocol['arms']):raise ValueError('instrument commit')
        if subprocess.check_output(['git','show','HEAD:'+str(args.protocol.resolve().relative_to(ROOT))],cwd=ROOT)!=args.protocol.read_bytes():raise ValueError('commitunchangedprotocol')
        status=subprocess.run(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,capture_output=True,text=True,check=True)
        if 'last push : current ('not in status.stdout:raise ValueError('current actual canonical checkpoint required')
        checkpoint=(ROOT/'.resume/.last-push').read_text().strip()
        if not re.fullmatch(r'[0-9a-f]{64} \S+ s3://setec-astronomy-artifacts/checkpoints/\S+/',checkpoint):raise ValueError('canonical checkpoint receipt')
        now=datetime.now(timezone.utc);write_once(args.out,dict(schema='prime-field-a14-root-release/v1',execution_authorized=True,authority='Explicitrootreleaseunderstandingstandinguserauthorization; noofficialscientifictransition.',owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,memory_bytes=2147483648,watchdog_seconds=21600,absolute_deadline=(now+timedelta(seconds=21600)).isoformat(),max_attempts=1,numpy_runtime=runtime_numpy.snapshot(),package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True)))
if __name__=='__main__':main()

"""Prospective A13 protocol and explicit single-attempt root release."""
import argparse, copy, importlib.metadata, json, re, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from baseline import core
import runtime_numpy
from custody import HERE, ROOT, INPUTS, PARAMETERS, bindings, digest, write_once, tools, load, descriptors, methods

prior = core.solver.module('_a13_prior_protocol', 'research/prime_field_a12_execution_20261106/prepare.py')
DEFS = dict(identified_targets='Identifiable requested target unit columns; dependent slots, not extra draws.',
    source_rank='Within-base supplied/collected M rank; known unit labels are supplied, not learned.',
    outside_rank='Rank of actual eight-target U matrix.',
    delta='Within-base rank([[M,0],[B,U]])-rank(U)-rank(M); never compared across bases.',
    after_cancellation_rank='Within-base joint rank minus U rank.',
    base_columns='Actual original projected norm width or 32 native known columns.',
    source_rows='Actual norm equations or 32 supplied known unit equations.',
    target_rows='Raw target decompositions and scope-available knowledge equations.',
    decomposition_rows='Signed distinct-atom three-term decomposition equations.',
    knowledge_rows='Paid construction equalities available in this scope.',
    fr_add='Actually executed Fr.add in selected solver including certificate/public checks.',
    fr_sub='Actually executed Fr.sub including unit-sign shortcuts/substitution/lifting.',
    fr_mul='Actually executed Fr.mul; no scalar-equivalent calibration.',
    fr_inv='Actually executed Fr.inv; inversion internals not expanded.')


def make_protocol(commit):
    rules = load(INPUTS)
    plans = list(descriptors(rules))
    calls = sum(len(methods(v)) for i, v in plans)
    if len(plans) != 624 or calls != 1248:
        raise ValueError('exact prospective grid')
    p = prior.make_protocol(commit)
    p.update(protocol_id='PRIME-FIELD-A13-PAID-KNOWN-BASE-20261106', created='2026-11-06',
        study_dir=str(HERE.relative_to(ROOT)),
        question='What target identities and separate paid cost vectors result from replacing the native norm base by an independently hash-labelled public-log base, allowing the known arm to skip source learning?',
        freeze=dict(status='draft', protocol_sha256=None, commit=None, frozen_at=None, filed_before_affected_data=None))
    instrument = copy.deepcopy(p['arms'][0]['instrument'])
    instrument.update(commit=commit, binary_sha256=digest(Path(sys.executable).resolve()),
        build=[[sys.executable, '-B', str(HERE.relative_to(ROOT)/'driver.py')]])
    p['arms'] = [dict(id=name, role=role,
        description=description, instrument=copy.deepcopy(instrument),
        parameters=dict(PARAMETERS, inputs_sha256=digest(INPUTS)))
        for name,role,description in [('joint_reference','reference','Sparse joint solver on every base/system;624 actual calls.'),
            ('base_aware','candidate','Norm: separately charged outside-first control; known: direct known-label substitution.624 actual calls, all original-row/public checks.')]]
    p['controls']['aa']['not_applicable_reason'] = 'Tiny repeated charged-base construction and deterministic matrix certificates, scalar/batch point replay, independent integer constructor predictions; no repeated-clock inference.'
    p['controls']['positive']['not_applicable_reason'] = 'Tiny p<=211 full collector/branch/target recovery, public base labels and dense/direct/joint controls; complete native signed-triple and public checks with no outcome-selected inputs.'
    p['controls']['negative']['not_applicable_reason'] = 'Corrupted signs/labels/points/units/draws/policy/future knowledge/source leaks, matrix RHS/weights/residuals, phase/journal/checkpoint receipts and gate failures refuse; retain partial data. Symbolic betaQ is never a known log.'
    p['randomization'].update(arm_order='fixed',
        arm_order_reason='Per curve: build known base before targets, norm source collection then source-free known table/natural queries; norm AP0/hash0/AP1/hash1/AP2/hash2, policies walk/hash_offset/general,budgets1/2/4/8,relations/anchors,joint then outside-first control. Known one branch/policy,budgets1/2/4/8,supplied scope,direct then joint control. Scalar then batch per endpoint; no clock inference.',
        seed_derivation=dict(method='explicit_list', seeds=[0]*calls, nonce=None,
            note='Export instances0..623 enumerate systems, each with two actually executed algebra arms, not independent target draws. Public hash-domain/source seeds and full descriptors frozen separately.'),
        instance_sampling=dict(independent_of_arm=True,
            rule='Four first-eligible coefficient curves, two each F262139/F524287,base32,eight independently hash-selected canonical-y public targets;20prior coefficient models excluded via pinned A12 rules+generated. Known labels hash modulo r with identity and duplicate +/-scalar-class rejection, finite cap10000per atom, no target/yield/rank/cost redraw.'))
    p['sample_size']['instances'] = len(plans)
    p['sample_size']['power']['note'] = '624dependent systems/1248actual solver calls; four curves/32public target points. Two algebra arms on identical system IDs; base/source/scope are explicit within-arm factors and base_aware chooses outside-first on norm and direct substitution on known. Complete descriptor mapping. Reused known baseline is not reexecuted or counted as six target samples. No p-value/population inference.'
    factors = [dict(name='base_program', levels=['norm', 'known']),
        dict(name='source_schedule', levels=['ap0', 'hash0', 'ap1', 'hash1', 'ap2', 'hash2', 'known(source-free)']),
        dict(name='target_policy', levels=rules['target_policies']),
        dict(name='target_prefix', levels=rules['target_prefixes']),
        dict(name='knowledge_scope', levels=['relations', 'anchors', 'supplied']),
        dict(name='solver', levels=['sparse_joint', 'sparse_cancel', 'known_direct'])]
    p['variable_ledger'] = dict(independent=factors,
        factors=[dict(name='curve_public_targets', treatment='fixed', value='Four fresh curves/32target points matched across the two different bases',
            how='Largest-prime rule and first eligible curve/target recipe; no target scalar supplied. Known base constructed before target generation.'),
            dict(name='query_engines', treatment='fixed', value='Scalar replay and shared-denominator batch physically execute per actual endpoint in each base',
            how='Own prepaid sign/index/pair table; exact outputs checked. Only one relation/matrix stream per endpoint. Cold references subtract other engine/control work.')],
        comparisons=[dict(id='C-paid-known-base', arms=['joint_reference','base_aware'],
            differs_in=[v['name'] for v in factors], design='factorial',
            threshold='Exact target masks and separate conditional cold counter vectors; within-base Delta only; every null/adverse outcome retained.')],
        aa_not_applicable='Tiny deterministic controls, no repeated timing comparison.', crosses_map=False)
    p['metrics']['primary'] = [dict(id=k, name=k.replace('_', ' '), unit='objects', kind='exact',
        definition=v, source='metrics.json columns/rows; analysis.json cells[].'+k,
        aggregation='per_row', resolution='1', uncertainty='none_exact') for k, v in DEFS.items()]
    p['measurement'].update(counters=[
        'Separate actual Fp/Fr add/sub/mul/inv, EC group API, hash draws/signs/scans/predictor/copy/query/storage and explicit NumPy allocation traffic.',
        'Known base binary/windows1..8 public-only portfolio from P/paid signs; actual construction/intermediates/canonical signs and independent public scalar checks;32supplied unit equations.',
        'Norm exact original projection/prereq64/selected source128 collector; known no source construction or source queries, own base-derived P cache only.',
        'Executed native-column assembly and direct known-label substitution, arbitrary eight-target U solver, original32unit+rawrow lifting/public checks; sparse joint control separately charged.',
        'Actual both-engine campaign work and conditional cold single-engine references; no double-counting namespaces or shared target generation.'],
        record=['Exact source/input/interpreter/NumPy identities, all field/curve/base/target/source rejection records and EC1 metadata.',
            'Producer bytes flushed before every separately coded plain-group/triple/dense check; full hits/misses and retained failure prefixes.',
            'Every branch label/firstbudget/point-coincidence, direct/joint target mask/residual/original-row certificate, no target scalar or other-base cache.',
            'Four closed-curve lossless encodings and canonical checkpoints, source unchanged after attempt; supervisor/child CPU/RSS, unisolated wall_valid=false.'])
    p['analysis_plan']['script'] = dict(path='analyze.py', sha256=digest(HERE/'analyze.py'))
    p['claims'] = [dict(id='A13-paid-known-base-finite', **{'class': 'exact_computation'},
        decided_by=['C-paid-known-base'], text='Producer finite matched-base coverage and separately charged conditional counter vectors. Public-known-base and aP+bQ are existing controls, no novelty/calibrated/runtime/whole-attack claim.')]
    p['decision_rule'].update(comparison_ids=['C-paid-known-base'],
        statistic='Exact named target masks and included cold vectors; never rank/Delta comparison across point bases.',
        text='Compare source-free known direct with each fixed norm joint program on identical target IDs; retain relations/anchors distinct and known joint control separately. Record all incomparable/zero/adverse results. Known labels supplied, not learned.',
        threshold='No favorable outcome required; exact completion/controls only. Incomplete costs and unsigned producer assertions do not establish complete attack or trusted execution standing.')
    p['stopping_rules'] = [dict(rule='Four curves;norm6source128 schedules,3targetpolicies,4budgets,2scopes,joint+outside-first=1152calls. Known source-free3policies,4budgets,suppliedscope,direct+joint=96calls. Total624systems1248actualcalls,32publictargetdraws,continue through early recovery/zero.', kind='fixed_n', preregistered=True),
        dict(rule='128field/curve/target candidates;10000source/base candidates;32base atoms,4096pairs/retainedrows,8192affinelabels,64jointcolumns,176cachedendpoints perbase, p<2^32. Refuse with retainedprefixes/unknownremainingcells, no truncation/redraw.', kind='invalidation', preregistered=True),
        dict(rule='One existing worker/thread,2GiB,21600CPU/wall seconds,one attempt, fresh absolute deadline in release;no automatic retry/new paidcapacity.', kind='budget', preregistered=True)]
    p['invalidation_rules'] = ['Exact source/input/runtime mutation, failed admission/lease/deadline, missing rows/queries/oracles/receipts or mismatched public/linear/counter certificates invalidates completeness; keep partial work and unknown cells.',
        'Known base chosen independently before targets,32labels explicit. No norm/source/other policy/future or checker scalar caches imported into a cold program. Q-basis coefficients remain symbolic.',
        'Same public targets/recipes, separate base tables/caches; cold known skips source work but may use only its own paid base/P/signs. Shared target generation charged to either cold deployment.',
        'Direct arbitrary-U substitution/lift executes and agrees with sparse joint control/dense membership. Supplied logs never counted as new learned rank; no cross-base Delta/dimension dominance.',
        'Scalar replay physically retained; batch-only cold reference subtracts replay/comparison and keeps paid index/fallback/dummy work. No weighted/runtime inference from incomplete primitives.']
    p['inadmissible'] = ['Fresh scientific generation before published complete source/inputs, frozen prospective protocol,current actual S3,explicit rootrelease and normal admission.',
        'Free legacy H017 construction, forced useless known-source learning, free union/future/otherbase cache, scalar-only assumed cost with no executed evaluator.',
        'Repeating known results as extra native trials or target draws; raw rank inflation/base replacement called fixed-base Delta improvement.',
        'Unexpanded generation/hash/pow/checker/NumPyinternal/Python/OS/IO omitted but complete S/runtime/attack advantage claimed.',
        'Retry/restore/new paid capacity/outcome-conditioned target/base/budget expansion under this single-attempt contract.']
    p['extensions'] = dict(model_verified=False, model_identity=None, official_status_transition=False,
        base_labels='sha256(domain|known-base|EC1_curve_uid|index|counter) mod r; reject0 or repeatedmin(s,(-s modr));construct fixedrawlabels with scalar-only portfolio from0/P/-P; canonicalizepoints andlabels together, hydrate canonical signs afterfullworkload so y does not change scalar-model construction predictions.',
        grid='624systems1248calls; export joint_reference and base_aware arms on same system IDs0..623 in descriptors(rules) order, actual execution methods(desc) order. Full base/source/policy/budget/scope/method mapping in raw and analysis; no synthetic missing-arm rows.',
        cold_costs='Norm original projection and selected AP/hash sourcecache128; known native32 unit labels/no source construction. Own point/PQ caches/tables only. Common target generation reference charged once to either. Source-free known direct48views reused dependently across6norm schedules/2scopes, no extra executes.',
        comparison='Within same curve/policy/budget compare exact targetmasksuperset and nonlarger included counter vectors. Arithmetic8FpFr+explicitqueryallocation vector and allretainedcounter vector separate; never Delta/rank acrossbases or completecost/runtime/wholeattack dominance.',
        cost_limits='Separate actual semantic field/group/logical/copy/allocation vectors; inversion/pow/hash/generation/checker/Python/NumPytemporaries/OS/IO notfully expanded. Inclusive child/supervisor CPU/RSS and unisolatedwall retained. No calibrated S/rho/attack claim.',
        checkpoint_semantics='Close allcurrentcurvewriters, losslessgziproundtrip, pausedcanonicalS3push; no hottar or native retry/restore. Official raw artifact remotes verified separately after completion.',
        proof_status='Typed artifact-pinned PCC claims before new result citation; producerchecks/hash/S3 not trusted signed scientific/replay/execution proof.',
        cloud_policy='One existing localworker/thread2GiB21600CPU/wall1attempt,no new paidresources. Existing storageauthorization,no secrets inrepo.',
        literature='literature.md documents existing H017/formalknownlog,A12collector/solver and retrieved PKM2016§3.2roughcost warning. Research-kb MCP/wrapper unavailable; scoped directsource fallback, no novelty/corpus-wideabsence.')
    p['literature'] = [dict(ref='src/crypto_autoresearcher/index_calculus/factor_base.py:FactorBase.known_log; harvest.py:formal_basis_known_log', provenance='internal', verified_by='root and administrative Coordinator,2026-11-06', claim='Existing known-log base/formal reduction; separate legacy Curve leaves construction uncharged, so execute/count it explicitly here.'),
        dict(ref='research/prime_field_a12_execution_20261106/next-leads.md; source_collection.py; affine_core.py; affine_solver.py; batch_query.py', provenance='internal', verified_by='root and administrative Coordinator,2026-11-06', claim='Strongest implemented same-budget direct collector, arbitrary-U joint solver and executed query baseline; A12 finite measurements producer/unverified under PCC-20261106-7a4122.'),
        dict(ref='https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf §3.2,p8', provenance='retrieved', verified_by='Administrative Coordinator reread retained primary PDF2026-11-06,SHAa53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b', claim='Established generalalphaP+betaQ construction, distinct stages and explicit warning that scalar/Fp unit equality is a rough cost model.')]
    p['links'] = dict(design='design.md', literature='literature.md', prior='../prime_field_a12_execution_20261106/next-leads.md')
    p['reporting']['graphs'] = ['Target identity recovery by base/policy/budget with dependent reuse labelled',
                              'Separate paid base/source/collection/algebra vectors; no cross-base rank gain or calibrated timing claim']
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
        now=datetime.now(timezone.utc);write_once(args.out,dict(schema='prime-field-a13-root-release/v1',execution_authorized=True,authority='Explicitrootreleaseunderstandingstandinguserauthorization; noofficialscientifictransition.',owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,memory_bytes=2147483648,watchdog_seconds=21600,absolute_deadline=(now+timedelta(seconds=21600)).isoformat(),max_attempts=1,numpy_runtime=runtime_numpy.snapshot(),package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True)))
if __name__=='__main__':main()

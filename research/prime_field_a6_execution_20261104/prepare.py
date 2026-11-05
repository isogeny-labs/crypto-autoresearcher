"""Bind/freeze A6 before data; root authorization is an explicit later command."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

from common import HERE, ROOT, NATIVE, INPUTS, PARAMETERS, bindings, digest, git, write_once


def protocol_tools():
    spec = importlib.util.spec_from_file_location('_a6_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    rules=json.loads(INPUTS.read_text())
    expected=dict(schema='prime-field-fresh-source-rules/v1',domain='prime-field-fresh-source-control/20261104/v1',fields=[dict(p=8191,base_size=16),dict(p=65537,base_size=32)],curves_per_field=2,a=2,excluded_curves=[[8191,5009],[8191,7229],[65537,20845],[65537,55325]],maximum_curve_candidates=128,maximum_target_candidates=128,seeds=[0,1,2],sources=64,prefixes=[0,16,64],targets=8,collision_multipliers=64,maximum_scalar_candidates=10000,max_retained_rows=2048,max_pair_entries=4096)
    if rules!=expected or 'cells' in rules:raise ValueError('exact prospective rules only; no generated fixture inputs')
    value=json.loads((ROOT/'research/prime_field_a4_execution_20261030/protocol.json').read_text())
    value.update(protocol_id='PRIME-FIELD-A6-FRESH-SOURCE-CONTROL-20261104',version=1,created='2026-11-04',study_dir=str(HERE.relative_to(ROOT)),
        authors=['Delegated administrative Coordinator and root implementer; configured model unverified'],
        question='On four prospectively generated fresh curves and32new public point targets, how do window versus three fixedhash schedules change relation rank and natural target identifiability, with fixed original-window columns and separately metered per-arm source construction?',
        freeze=dict(status='draft',commit=None,filed_before_affected_data=None,frozen_at=None,protocol_sha256=None))
    template=value['arms'][0];value['arms']=[]
    for arm in ['window','hash0','hash1','hash2']:
        instrument=dict(template['instrument']);instrument.update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()),build=[[sys.executable,'-B',str(NATIVE.relative_to(ROOT)/'driver.py')]])
        value['arms'].append(dict(id=arm,role='reference' if arm=='window' else 'candidate',description='Fresh1..64window source order' if arm=='window' else 'Hash-defined 64 distinct public scalars, seed'+arm[-1],instrument=instrument,parameters={**PARAMETERS,'inputs_sha256':digest(INPUTS)}))
    value['analysis_plan'].update(inputs=['<run>/execution.json','<run>/raw/*.json[.gz]','<run>/raw/*.jsonl[.gz]'],script=dict(path='analyze.py',sha256=digest(HERE/'analyze.py')))
    value['claims']=[dict(id='A6-finite-source-control',text='Exact finite comparison of source schedules on four fresh prospectively selected curves/bases,32new point targets and fixed per-curve original-window projection.',**{'class':'exact_computation'},decided_by=['C-source'])]
    value['decision_rule'].update(text='Report every planned curve/arm/prefix/scope, rank, kernel syndrome, public target certificate, explicit anchor gain and outside-target cancellation Delta. Completion requires separate exact finite checks; no favorable outcome is required.',comparison_ids=['C-source'],threshold='96 complete scope observations plus independent curve/target recipe and all pair/query/affine/certificate checks; all failures retained.')
    value['controls']['aa']=dict(present=False,comparison=None,not_applicable_reason='Freshcurves have no archivednative window. Separate complete triple oracle reconstructs everywindow/hash/target query. Tinysoftware A/A repeats sourcecollector; no noisy clock inference.')
    value['controls']['positive']['not_applicable_reason']='Marked tiny-field software fixture exercises all query and certificate paths; no native outcome selected.'
    value['controls']['negative']['not_applicable_reason']='Software corruptions of schedules, anchors, kernels, target weights, query misses and journal entries must refuse; native misses remain in census.'
    value['randomization'].update(arm_order='fixed',arm_order_reason='window,hash0,hash1,hash2; prefixes0/16/64 and relations/anchors. Shared pair and target work once per curve.',
        seed_derivation=dict(method='explicit_list',seeds=[0]*48+[1]*24+[2]*24,nonce=None,note='24analysis labels per arm; window/hash0seed0,hash1seed1,hash2seed2. Native schedule seeds0/1/2 exact recipes in inputs.json; no yield-conditioned redraw.'),
        instance_sampling=dict(rule='Two firsteligible fresh a2curves perfield8191/65537, explicit fourA4exclusions, base16/32, eight hash-x canonical-y targets percurve; allrecipes frozen beforegeneration. No rank/yield/recoveryselection.',independent_of_arm=True))
    value['sample_size']['instances']=24;value['sample_size']['power']['note']='24paired analysis labels (4curves x3prefixes x2scopes), not24independent curves. Complete finite census on four fresh rule-selected fixtures and three fixedhash seeds; no population effect or p-value estimated.'
    value['sample_size']['preflight_runtime']['measured_on']='21600seconds is a protective local machine watchdog; no new cloud submission or billing forecast.'
    value['variable_ledger']=dict(independent=[dict(name='source_schedule',levels=['window','hash0','hash1','hash2'])],
        factors=[dict(name='fixed_inputs',treatment='fixed',value='Four prospectively generated curves/bases/original-window projections and32new public point targets',how='Rules-onlyinput frozen before affectedgeneration; allcandidates/targets retained; percurveoriginal-window projected columns never shrink.'),
                 dict(name='public_knowledge',treatment='fixed',value='Original1..64 known anchors plus separately recorded schedule anchor equations',how='All64schedule sources public at every prefix; relation-only and anchor-augmented scopes separate.'),
                 dict(name='query_count',treatment='fixed',value='64source blocks per arm, one8targetstream and onepairtable percurve',how='Every bucket/sign and overlap retained/charged; analyze prefixes0/16/64 in two scopes.')],
        comparisons=[dict(id='C-source',arms=['window','hash0','hash1','hash2'],differs_in=['source_schedule'],design='one_factor',threshold='Complete finite paired observations; no rank/recovery stop.')],
        aa_not_applicable='Tiny software deterministic A/A and separate complete oracle; fresh native curves have no archived window replay. No noisy performance claim.',crosses_map=False)
    definitions=dict(source_rows='Source witnesses in this arm prefix, before explicit anchors.',base_columns='Constant percurve projected unknown width after original1..64window; any observedwidth retained.',base_rank='Rank of this relation-only or explicit-anchor system.',base_nullity='Original columns minus this scope rank.',reference_base_rank='Original window relation rank at the same prefix.',stacked_rank_with_window='Rank of this scope plus original window relation rows at same prefix.',rank_gain_over_window='Union rank minus original window relation rank; charge extra window collection when interpreting union.',
        anchor_rank='Rank of explicit schedule public-anchor rows alone.',relation_rank='Rank of collected source rows alone.',anchor_augmented_rank='Rank of relation rows plus explicit anchors.',distinct_equations='Normalized affine equations in this scope.',
        single_targets='Natural single-row functionals satisfying vN=0.',joint_targets='Identifiable target unit columns in the joint system.',early_single_targets='Single targets identified with base nullity positive.',early_joint_targets='Joint targets identified with base uncertainty after target cancellation.',
        target_base_rank_gain='rank([[M,0],[B,U]])-rank(U)-rank(M).',base_rank_after_target_cancellation='Joint rank minus outside target-column rank.')
    definitions.update(construction_scalar_multiplications='64 public source scalar multiplications for this arm; shared across prefix/scope views.',construction_field_multiplications='Fp.field_mul inside this arm construction only; shared prefix/scope view, not complete cold cost.',construction_group_additions='Fp.group_add inside this arm construction only; overlaps Fp primitive counts, never add units.',construction_field_inversions='Fp.field_inv inside this arm construction only; inversion internals unweighted.')
    value['metrics']['primary']=[dict(id=k,name=k.replace('_',' '),unit='objects',kind='exact',definition=v,source='analysis.json cells[].'+k,aggregation='per_row',resolution='1',uncertainty='none_exact') for k,v in definitions.items()]
    value['measurement']['record']=['Complete curve/target generation and independent recipecheck', 'Eacharm source construction with64logical scalar multiplication counters', 'Committed host/source/ownership','Every scalar candidate and complete pair/source/target query journal','Disjoint producer Fp/Fr/group/logical counters; diagnostic clocks','Complete kernels, cancellation and target weight certificates; separately checked arithmetic']
    value['stopping_rules']=[dict(rule='All4fixtures,4schedules,64sources each,8sharedtargets,3prefixes,2scopes; no rank/recovery stop.',kind='fixed_n',preregistered=True),dict(rule='128curve/target candidates,10000counter attempts per scalar,2048source/target rows perstream,4096pairs; refuse retaining prefix, never truncate.',kind='invalidation',preregistered=True),dict(rule='Existing local workstation only; oneprocess/thread2GiB21600sCPU/wall protective watchdog; oneattempt/no retry; no EKS/IsoLab or new paid submission.',kind='budget',preregistered=True)]
    value['invalidation_rules']=['Changed source/input/protocol, fixed generated projection/targets, omitted candidate/query/miss journals or false certificate invalidates completeness.','Missing/failed cells remain explicit unknowns, not zero-rank outcomes.','Shared pair/target work counted once; source overlaps queried in every arm; disjoint prefix phases counted once; no summing overlapping units.']
    value['inadmissible']=['Native collection before exact committed/pushed source, frozen protocol, explicit release and real S3 gate.','Shrinking projected unknowns with new source anchors or importing target labels.','Selecting seeds, inputs or stopping by outcomes.','Interpreting overlap/cumulative clocks as additive cost.']
    value['extensions']=dict(checkpoint_semantics='Real canonical S3 checkpoint and root release mandatory; fresh failure directories, no in-row restore.',model_verified=False,model_identity=None,official_status_transition=False,
        counter_coverage='Producer metered per-arm source construction, shared setup/table/targets and disjoint affine/certificate phases. Generation separately charged with candidate pointtests and selected-field meters. Hash/sort/serialization/OS/verifier internals incomplete.',
        export_unit='96curve/arm/prefix/scope rows from1physicalpanel; 4tables/4targetstreams;16source schedules actually queried. Physical collection counters only window/prefix0/relations percurve; all96algebra phases backend once.',
        target_policy='Qonly;32fresh targets drawn afteradmission by hash-x minimum rationaly, rejectnonrational/duplicatesonly; t1..64diagnostic not targetlabels.',
        verification_scope='Separate complete generation/exclusion/EC1/target recipes, hash-schedules, fixedprojection, signedtripleoracle, allpair/query/anchor/affine/fullkernel/cancellation/weights/public equations; constructioncountercoverage.',
        cloud_policy='No new infrastructure submitted. Existing shared workstation1thread/2GiB; unavailable account telemetry forbids paid submissions. Storage/checkpoint under user-authorized existing bucket.')
    value['reporting']['graphs']=['Per curve schedule ranks and explicit anchor gains at all fixed prefixes; single/joint target recovery and outside-adjusted ranks.']
    value['literature']=[dict(ref='research/prime_field_a5_execution_20261104/RESULTS.md',provenance='internal',verified_by='/root,2026-11-04',claim='A5fixedobservedfixtures motivate prospectivefreshcurves/targets with separatemetering of sourceconstruction; no assumednative outcome.'),dict(ref='https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf sections3.1-3.4',provenance='retrieved',verified_by='/root,2026-11-04; primarypages7-9 reread',claim='Public source combinations and verified base sums, separating precomputation/relation solving/linear algebra and scalar multiplication costs.')]
    value['links']=dict(literature='literature.md',design='design.md',prior_A5='../prime_field_a5_execution_20261104/RESULTS.md')
    value['amendments']=[]

    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action',required=True)
    proto = sub.add_parser('protocol')
    proto.add_argument('--source-commit',required=True)
    proto.add_argument('--out',type=Path,required=True)
    proto.add_argument('--freeze',action='store_true')
    proto.add_argument('--draft-preview',action='store_true')
    release = sub.add_parser('release')
    release.add_argument('--source-commit',required=True)
    release.add_argument('--protocol',type=Path,required=True)
    release.add_argument('--out',type=Path,required=True)
    release.add_argument('--owner',required=True)
    release.add_argument('--authorize-root',action='store_true',required=True)
    args = p.parse_args()
    tools = protocol_tools()
    if args.action == 'protocol':
        if args.freeze and args.draft_preview:
            raise ValueError('a draft preview cannot be frozen')
        if args.out.resolve().parent != HERE:
            raise ValueError('protocol belongs beside its pinned analysis source')
        if not args.draft_preview:
            bindings(args.source_commit)
        value = make_protocol(args.source_commit)
        errors = tools.schema_errors(value,'experiment.protocol/v1') or tools.lint_protocol(value,HERE)
        if errors:
            raise ValueError(json.dumps(errors))
        write_once(args.out,value)
        if args.freeze:
            tools.freeze(args.out,args.source_commit,True)
        print(json.dumps(dict(protocol=str(args.out),frozen=args.freeze)))
    else:
        source,input_map = bindings(args.source_commit)
        protocol = json.loads(args.protocol.read_text())
        if protocol['freeze']['status'] != 'frozen' or protocol['freeze']['filed_before_affected_data'] is not True:
            raise ValueError('prospectively frozen protocol required')
        if protocol['freeze']['commit'] != args.source_commit or any(
                arm['instrument']['commit'] != args.source_commit for arm in protocol['arms']):
            raise ValueError('release source commit differs from frozen protocol instruments')
        errors = tools.schema_errors(protocol,'experiment.protocol/v1') or tools.lint_protocol(protocol,args.protocol.parent)
        if errors:
            raise ValueError(json.dumps(errors))
        relative = str(args.protocol.resolve().relative_to(ROOT))
        if subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT) != args.protocol.read_bytes():
            raise ValueError('protocol must already be committed unchanged')
        check = subprocess.run(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,capture_output=True,text=True,check=True)
        if 'last push : current (' not in check.stdout:
            raise ValueError('a prior actual canonical checkpoint of the current state is required')
        checkpoint = (ROOT/'.resume/.last-push').read_text().strip()
        if not re.fullmatch(r'[0-9a-f]{64} \S+ s3://setec-astronomy-artifacts/checkpoints/\S+/',checkpoint):
            raise ValueError('canonical checkpoint receipt has unexpected shape')
        value = dict(schema='prime-field-a6-root-release/v1',execution_authorized=True,
            authority='Explicit root Phase B release under standing user authorization; no research-state promotion.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=input_map,
            interpreter_sha256=digest(Path(sys.executable).resolve()),protocol_sha256=protocol['freeze']['protocol_sha256'],
            checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,watchdog_seconds=21600,
            package_versions={name:importlib.metadata.version(name) for name in ['python-flint','sympy','jsonschema','PyYAML']},
            issued_utc=datetime.now(timezone.utc).isoformat(),model_verified=False,model_identity=None)
        write_once(args.out,value)
        print(json.dumps(dict(release=str(args.out),owner=args.owner,execution_authorized=True)))


if __name__ == '__main__':
    main()

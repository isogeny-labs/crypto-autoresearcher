"""Prospective certified-query protocol and bounded remaining-window root release."""
import argparse,copy,json,subprocess,sys,re,importlib.metadata,math
from datetime import datetime,timezone,timedelta
from pathlib import Path
from deps21 import core
import runtime_numpy
from custody21 import HERE,ROOT,INPUTS,PARAMETERS,ARMS,bindings,digest,load,write_once,tools,BUDGET_INPUTS


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
    p=load(ROOT/'research/prime_field_a20_execution_20261107/protocol.json')
    p.update(protocol_id='PRIME-FIELD-A21-DIRECT-FORMAL-SUBSTITUTION-20261107',created='2026-11-07',study_dir=str(HERE.relative_to(ROOT)),
        question='On all four immutable A20 formal native cases, how do actual direct formal substitution, auxiliary-first cancellation and full native joint costs compare including mapping, expansion, common-unit substitution, target membership, native lifting and public checks?',
        freeze=dict(status='draft',protocol_sha256=None,commit=None,frozen_at=None,filed_before_affected_data=None),amendments=[])
    instrument=copy.deepcopy(p['arms'][0]['instrument']);instrument.update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()),build=[[sys.executable,'-B',str(HERE.relative_to(ROOT)/'driver21.py')]])
    descriptions=dict(direct_formal='Cold direct signed formal-coordinate expansion and common-unit substitution, projected unit recovery, original-definition/common-unit certificate lifting and original/public checks.',
        aux_cancel_joint='Actually rerun current auxiliary-first solver on the same public native case and preparation, with original/public checks.',
        sparse_joint='Actually rerun current strongest native sparse joint floor on the same public native case, with original/public checks.')
    p['arms']=[dict(id=arm,role='candidate'if arm=='direct_formal'else'reference'if arm=='aux_cancel_joint'else'control_positive',description=descriptions[arm],instrument=copy.deepcopy(instrument),parameters=copy.deepcopy(PARAMETERS))for arm in ARMS]
    p['claims']=[dict(id='A21-conditioned-producer-algebra',**{'class':'exact_computation'},decided_by=['C-direct-formal'],text='Finite conditioned same-input target masks and separate actual primitive/logical vectors. No fresh target/curve holdout, rank-information gain, novelty, clock, weighted or full-attack advantage inferred.')]
    p['links']=dict(design='design.md',literature='literature.md',prior='../prime_field_a20_execution_20261107/next-leads.md')
    p['analysis_plan']['script']=dict(path='analyze21.py',sha256=digest(HERE/'analyze21.py'))
    p['controls']['aa']['not_applicable_reason']='Deterministic same-input arithmetic; no timing inference. Marked p<=211 and synthetic signed/known/native lift controls; no native pilot.'
    p['controls']['positive']['not_applicable_reason']='Actual auxiliary-first and full native joint solvers run cold on ALL four conditioned cases, including every negative target. Independent plain expanded projection/dense/native/public checker; actual small software cases with positive and unresolved targets.'
    p['controls']['negative']['not_applicable_reason']='Refuse changed definitions/signs/common numeric auxiliary labels/projection maps/native weights/counter bindings; admission refuses native execution before release. Partial failed prefixes and all-missing twelve-row export controls retained.'
    p['variable_ledger']=dict(independent=[dict(name='algorithm_execution',levels=ARMS)],factors=[dict(name='native_inputs',treatment='fixed',value='All four immutable A20 formal cases',how='Exact case/preparation hashes; all rows, definitions, original projection and targets unchanged. No checker rows/scalars/certificates input to producer.'),dict(name='cost_scope',treatment='fixed',value='Included algebra plus original/public checking',how='Actual cold mapping/expansion/substitution/elimination/target/native-lift costs; existing unit shortcuts retained. A20 acquisition is shared historical prerequisite, not recollected or free full-attack evidence.')],
        comparisons=[dict(id='C-direct-formal',arms=ARMS,design='one_factor',differs_in=['algorithm_execution'],threshold='Identical requested target outcomes and original/public certificates; report all actual primitive dimensions and failures without weighted winner.')],crosses_map=False,aa_not_applicable=p['controls']['aa']['not_applicable_reason'])
    p['randomization']['arm_order']='fixed';p['randomization']['arm_order_reason']='Per fixed case order: direct_formal, aux_cancel_joint, sparse_joint. Each parses its own public case/preparation and rebuilds cold. Historical outputs loaded checker-only after all actual producers finish.'
    p['randomization']['instance_sampling']=dict(independent_of_arm=True,rule='ALL four A20 formal cases in original order, conditioned on previous observation. No resampling, new target draw, favorable subset, recollection or claim of independence from A20.')
    p['randomization']['seed_derivation'].update(seeds=[0]*12,note='Deterministic four existing cases x three actual method calls. Twelve dependent export rows; no new random replicates.')
    p['sample_size']['instances']=4;p['sample_size']['replicates']=1;p['sample_size']['warmups']=0;p['sample_size']['power']['note']='Exact conditioned four-case census,12actual calls; no new holdout/population inference.'
    p['measurement']['counters']=['Actual Fp/Fr add/sub/mul/inv including original/public checks. Logical mapping/component/native/target/weight scans, unit shortcuts, emitted coefficients and definition-row elisions retained separately. No operation/byte weighting.']
    p['measurement']['record']=['Exact inherited and new source/producer/checker input hashes; pre-output Git/protected source and actual process provenance.','Own public input parse bytes/CPU separately retained per method; actual mapping, expansion, substitution, elimination, membership and native-lift phase counters.','Producer output before independent checker receipt; actual start/complete/failure census, closed case checkpoints, every partial paid prefix and unresolved target.','Original one-worker/thread2GiB cumulative elapsed+all measured CPU reservation/deadline; one consumed attempt/no retry/new capacity.']
    template=copy.deepcopy(p['metrics']['primary'][0]);p['metrics']=dict(primary=[],secondary=[])
    definitions=dict(identified_targets='Requested target unit count, not auxiliary pivots.',identified_mask='Requested target-index bit mask; all eight remain.',system_columns='Actual algorithm matrix width; different native/projected widths are not different learned information.',system_rank='Actual algorithm system rank; not directly compared as old-base gain.')
    definitions.update({field+'_'+op:'Actual '+field.upper()+' '+op+' primitive calls, including certificate/public checks; unweighted partial component vector.'for field in ('fp','fr')for op in ('add','sub','mul','inv')})
    for key,definition in definitions.items():p['metrics']['primary'].append(dict(template,id=key,name=key.replace('_',' '),definition=definition,source='metrics.json rows, native result phases and bound checker receipts'))
    p['decision_rule'].update(comparison_ids=['C-direct-formal'],statistic='Same-input target masks plus separate actual primitive vectors and phase attribution.',threshold='Any semantic disagreement fails the component; cost vectors may improve, worsen or trade dimensions.',text='Compare all three actually cold producer algorithms on all four cases. Charge direct mapping, signed expansion/common-unit substitution, elimination, membership, original definition/common-unit certificate lifting and public verification. Preserve all negative target outcomes. Do not reuse checker expansion or recovered scalars. No weighted/runtime/new-information or whole-attack result inferred.')
    p['stopping_rules']=[dict(kind='fixed_n',preregistered=True,rule='Exactly four immutable conditioned A20 formal cases x three actual cold producer calls=12 calls and12 export rows. No recollection, new targets, redraw, favorable subset, retry or horizon expansion.'),dict(kind='invalidation',preregistered=True,rule='Native48/joint64/rows4096, old norm32/formal16/eight targets unchanged. Source/input/certificate/dense/public/cost binding disagreement fails; preserve all paid prefixes and unknown cells.'),dict(kind='budget',preregistered=True,rule='One existing worker/thread2GiB/one consumed attempt. Original2026-11-07T07:46:38.570520UTC deadline and21600seconds cumulative reserve deduct elapsed original window plus ALL pinned native and measured postprocessing CPU through A20. No deadline reset/new capacity.')]
    p['invalidation_rules']=['Exact source publication, prospective freeze, actual current canonical S3 checkpoint, explicit bounded root release and normal admission/lease/consumed marker required.','No historical checker expansion, cancellation, pivot, recovered scalar or certificate input to any producer. Formal coordinates never numeric auxiliary labels.','All target memberships and original/public certificates, signed expansion/multiplicity/common-unit projection and cost payload bindings must agree. Missing/failed calls unknown, not mathematical negatives.']
    p['inadmissible']=['Unapproved native pilot, widened fields/horizon, favorable case selection or reused consumed release.','Uncharged direct mapping/lifting, checker result as producer input, source/target collection ignored in a full-attack claim, numeric formal labels or auxiliary pivots counted as targets.','Population/fresh-holdout/novelty/scaling/runtime/weighted/whole-attack or independently signed proof claim from these conditioned producer counters.']
    p['extensions']=dict(grid='Four conditioned cases x3actual cold methods=12rows; no new curves/targets/collection.',model_verified=False,official_status_transition=False,proof_status='Producer-unverified/not-covered absent trusted independent proof.',costs='Included algebra and public checks only; A20 acquisition is fixed historical prerequisite, separately retained in A20. Actual parsing bytes/CPU retained outside primitive cost; no isolated wall inference.',ownership='One consumed release/exclusive lease, no retry/newcapacity/originaldeadline unchanged.')
    p['reporting']['graphs']=['Per-case same target masks and actual Fr/Fp vectors for three algorithms, with projection/elimination/native-lift phase attribution. Include every failure and unresolved target.']
    p['literature']=[dict(ref='literature.md; A20 next-leads/results, check_formal20 and inherited native algebra primary sources',provenance='internal',verified_by='Root source read2026-11-07 before implementation',claim='Coordinate substitution and native certificate lifting are existing linear algebra. Checker expansion was unmetered producer work; this tests the actual implementation boundary, without novelty or transfer claims.')]
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
        write_once(args.out,dict(schema='prime-field-a21-root-release/v1',execution_authorized=True,authority='Explicit bounded root release under standing user authorization; no official scientific status transition.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),
            protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,max_attempts=1,**budget,numpy_runtime=runtime_numpy.snapshot(),
            package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True,watchdog_seconds=budget['watchdog_seconds'],absolute_deadline=budget['absolute_deadline'])))


if __name__=='__main__':main()

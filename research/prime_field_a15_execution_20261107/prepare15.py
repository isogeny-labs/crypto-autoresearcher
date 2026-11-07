"""Prospective retained-input pair protocol and explicit one-attempt root release."""
import argparse,copy,json,subprocess,sys,re,importlib.metadata
from datetime import datetime,timezone,timedelta
from pathlib import Path
from deps15 import core
import runtime_numpy
from custody15 import HERE,ROOT,INPUTS,PARAMETERS,bindings,digest,load,write_once,tools


def make_protocol(commit):
    p=load(ROOT/'research/prime_field_a14_execution_20261106/protocol.json')
    p.update(protocol_id='PRIME-FIELD-A15-BATCHED-PAIRS-20261107',created='2026-11-07',study_dir=str(HERE.relative_to(ROOT)),
        question='On all 16 retained A14 geometries and all 8960 retained queries, does an executed shared-denominator/sign-reusing/batched pair builder preserve exact ordered pair, bucket, query and native-row semantics, and what separate actual construction vectors does it incur?',
        freeze=dict(status='draft',protocol_sha256=None,commit=None,frozen_at=None,filed_before_affected_data=None),amendments=[])
    p['authors']=['Root implementer; delegated administrative Coordinator exact-source assessment before release; configured model unverified']
    instrument=copy.deepcopy(p['arms'][0]['instrument']);instrument.update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()),
        build=[[sys.executable,'-B',str(HERE.relative_to(ROOT)/'driver15.py')]])
    p['arms']=[dict(id=method,role=role,description=description,instrument=copy.deepcopy(instrument),parameters=PARAMETERS)
        for method,role,description in [('scalar','reference','Unchanged A14 four-scalar-add ordered pair builder, own sign/query setup and complete retained query replay.'),
            ('batched','candidate','One bounded actual product-tree inverse per base, shared signed slopes and output negations, identical native descriptors/order, own sign/query setup and complete retained query replay.')]]
    p['claims']=[dict(id='A15-pair-component',**{'class':'exact_computation'},decided_by=['C-pair-builder'],
        text='Finite retained-input exact pair/query/native-row equivalence and actual separate Fp/allocation construction vectors. Existing technique, conditioned reuse, no new targets/solvers, calibrated runtime or whole-attack claim.')]
    reasons=dict(aa='Deterministic tiny scalar repetition and canonical JSON roundtrip controls; no repeated timing inference.',
        positive='Marked p<=211 point/orientation/alias/odd-batch/full-triple/hit/miss controls and independent closed-form arithmetic/allocation schedules; both methods execute every retained native query.',
        negative='Duplicate sign classes, zero/order-two/invalid/native-mismatch inputs, native admission refusal, corrupted point/sign/native descriptor/count/allocation/commitment, injected mid-phase and checker rejection retain outputs and refuse completion.')
    for key,reason in reasons.items():p['controls'][key]['not_applicable_reason']=reason
    p['randomization'].update(arm_order='fixed',arm_order_reason='Input order p262139-i0/i1,p524287-i0/i1; each norm,hybrid,known32,known48. Scalar then batched cold per table. Query order AP0/hash0/AP1/hash1/AP2/hash2 sources, natural8, extra cache points. Both signed endpoint query engines execute per endpoint. No clocks compared.',
        seed_derivation=dict(method='explicit_list',seeds=[0]*32,nonce=None,note='16 paired deterministic component instances; no new public-target draw.'),
        instance_sampling=dict(independent_of_arm=True,rule='Every retained A14 program geometry and query without selection, pinned Git/CAS provenance, no new curve/target generation or outcome-conditioned exclusion. Geometric32/48 labels include actual native aliases.'))
    p['sample_size']['instances']=16
    p['sample_size']['power']['note']='16 conditioned retained tables,32 actual builds,17920 actual QueryIndex endpoint replays,35840 scalar/batch endpoint engine calls; no new target solvers or independent draws. Exact finite census, no p-value/population inference.'
    p['variable_ledger'].update(independent=[dict(name='pair_builder',levels=['scalar','batched'])],
        factors=[dict(name='retained_geometry_and_queries',treatment='fixed',value='All 16 retained program geometries and8960 endpoints',how='Committed transcript pins original pairs and complete native row/query/miss and signed-point commitments before affected work.')],
        comparisons=[dict(id='C-pair-builder',arms=['scalar','batched'],design='one_factor',differs_in=['pair_builder'],threshold='Exact pair/native/query semantics and separately retained construction vectors; no scalar weighting, favorable result or calibrated gain required.')],
        aa_not_applicable='Marked deterministic tiny controls; no timing inference.')
    p['decision_rule'].update(comparison_ids=['C-pair-builder'],statistic='Exact ordered pair/native/query commitments and actual Fp/explicit allocation vectors.',
        text='Report each cold construction setup, pair stages and query replay separately. Candidate arithmetic executes; no estimated subtraction from old trace. Retain adverse/zero/incomparable vectors. Exact table parity conditions reuse of old downstream outcomes but is not a new solver execution or new target recovery.')
    p['measurement'].update(counters=['Actual scalar and vector Fp add/sub/mul/inv and EC API calls, setup signs/indices/table insertions, product-tree padding/root inverse/formulas/output negatives.',
        'Explicit pair/query NumPy allocation elements/bytes/copies/conversions, retained row/group checks and engine replays. No estimated EC calls for vector formulas; scalar and candidate actual work separate.',
        'Immediate disjoint phase completion/failure prefixes; complete native records before checker; separate checker/oracle CPU, inclusive child/supervisor CPU/RSS; shared-host wall_valid=false.'],
        record=['Pinned interpreter/NumPy/source/input identities and all16 public snapshots with prior Git/CAS provenance.',
            'All pair/native descriptor output events, retained query/native row/hit/miss outputs and separate plain full-triple/counter checker receipts.',
            'Closed-table lossless gzip/hash/byte receipts, four closed-curve actual canonical S3 checkpoints, one consumed attempt/no retry; all partial failures retained.'])
    metric=copy.deepcopy(p['metrics']['primary'][0])
    names=['build_fp_'+op for op in ('add','sub','mul','inv')]+['ordered_pairs','queries','verified_queries','pair_array_bytes','new_target_solver_calls']
    p['metrics']['primary']=[dict(metric,id=n,name=n.replace('_',' '),definition=('Actual cold construction '+n+'; field/array counters do not calibrate complete cost.' if n.startswith('build_') else n+' in this one retained table/method; query slots dependent and new target solver calls zero.'),source='metrics.json rows and bound outputs/checks',unit='bytes' if n=='pair_array_bytes' else 'objects') for n in names]
    p['metrics']['secondary']=[]
    p['analysis_plan'].update(script=dict(path='analyze15.py',sha256=digest(HERE/'analyze15.py')),
        inputs=['<run>/execution.json','<run>/raw/<table>/*.json[.gz]','<run>/raw/<table>/*.jsonl[.gz]'])
    p['stopping_rules']=[dict(kind='fixed_n',preregistered=True,rule='All16retainedtables,bothactualbuilders,all8960queries/method;32builds17920queries35840endpointenginecalls,zero new target solvers. No early favorable stop.'),
        dict(kind='invalidation',preregistered=True,rule='Native<=48,geometric<=48,pairs<=8192,retainedrows<=4096,p<2^32,finite non-order-two distinct sign classes. Complete input/point/native/sign/counter/commitment parity and custody; retain all partial failures, no redraw.'),
        dict(kind='budget',preregistered=True,rule='One existing worker/thread,2GiB,21600CPU/wall seconds,fresh absolute deadline,one attempt,no retries/new paid capacity.')]
    p['invalidation_rules']=['Exact source/input/interpreter/NumPy/admission/lease/deadline mutation or missing output/check/checkpoint forbids complete-panel status.',
        'Any ordered pair/native sign/bucket/query/miss/row or independently derived arithmetic/allocation schedule mismatch is retained and stops this attempt.',
        'Native preconditions refuse duplicate sign classes/identity/order-two/same-x; no masked zero denominator can silently emit a point.',
        'Outputs and paid phase prefixes precede checker invocation. A checker failure keeps producer outputs unverified; missing rows remain unknown.',
        'Every builder pays own index/sign/input/formula/allocation/table construction and actual query engines; no cross-base/future sharing. Query replay is a correctness control, not an independently selected target experiment.']
    p['inadmissible']=['Native builder/query execution before exact published closure, prospective frozen protocol,current actual canonical S3, explicit root release and normal admission.',
        'New target/curve draws, new solvers, favorable selection, retry, enlarged gates/new paid capacity or result-conditioned batch schedule.',
        'Calling established signed-sum batching novel, explicit allocation traffic peak RSS, fewer inversions calibrated runtime/full-cost gain, or retained target/query views independent recoveries.']
    p['extensions']=dict(model_verified=False,official_status_transition=False,conditioned_reuse=True,new_target_solver_calls=0,
        cloud_policy='Oneexistingworker/thread2GiB21600CPU/wall oneattempt,no new paidcapacity.',
        checkpoint_semantics='All table writers close and gzip roundtrip before four paused canonical curve checkpoints; no restart or restored clock.',
        counter_scope='Exact field-element vector operations plus scalar EC API calls; explicit allocation/conversion/padding/table counters. Inversion/pow internals and Python/NumPy/checker/OS/hash/IO unexpanded, no complete calibration.',
        proof_status='Producer-local checks only, no trusted signed scientific/replay/execution proof. New measured citations need typed artifact-pinned PCC claims and unverified standing until signed review.',
        prior_technique='Production _accel/tails/harvest signed denominator reuse/product-tree inversion and executed A12 query batching, see literature.md; no novelty.')
    p['literature']=[dict(ref='literature.md; production _accel.py/tails.py/harvest.py; A12 batch_query.py; A14 query_index.py/check_query.py',provenance='internal',verified_by='Root primary code review2026-11-07',claim='Established signed arithmetic and actual product-tree schedule, scalar pair construction gap only.'),
        dict(ref='https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf §3.2,p8',provenance='retrieved',verified_by='Retained primary PDF reread2026-11-07 SHAa53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b',claim='Rough cost-model warning; no calibration of this finite component.')]
    p['links']=dict(design='design.md',literature='literature.md',prior='../prime_field_a14_execution_20261106/next-leads.md')
    p['reporting']['graphs']=['Per-table actual scalar/batched cold pair arithmetic vectors','Setup/pair/query costs and explicit array traffic, with retained query parity/census','Failed/missing components retained; no new targets or solvers']
    return p


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    a=sub.add_parser('protocol');a.add_argument('--source-commit',required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--draft-preview',action='store_true');a.add_argument('--freeze',action='store_true')
    a=sub.add_parser('release');a.add_argument('--source-commit',required=True);a.add_argument('--protocol',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--owner',required=True);a.add_argument('--authorize-root',required=True,action='store_true')
    args=parser.parse_args();t=tools()
    if args.action=='protocol':
        if args.freeze and args.draft_preview:raise ValueError('draft cannot freeze')
        if not args.draft_preview:bindings(args.source_commit)
        value=make_protocol(args.source_commit)
        errors=t.schema_errors(value,'experiment.protocol/v1') or t.lint_protocol(value,HERE)
        if errors:raise ValueError(json.dumps(errors))
        write_once(args.out,value)
        if args.freeze:t.freeze(args.out,args.source_commit,True)
        print(json.dumps(dict(protocol=str(args.out),frozen=args.freeze)))
    else:
        source,inputs=bindings(args.source_commit);protocol=load(args.protocol)
        if protocol['freeze']['status']!='frozen' or protocol['freeze']['commit']!=args.source_commit or protocol['freeze']['filed_before_affected_data']is not True:raise ValueError('prospective source freeze required')
        if any(v['instrument']['commit']!=args.source_commit for v in protocol['arms']):raise ValueError('instrument source differs')
        if subprocess.check_output(['git','show','HEAD:'+str(args.protocol.resolve().relative_to(ROOT))],cwd=ROOT)!=args.protocol.read_bytes():raise ValueError('commit protocol unchanged')
        status=subprocess.run(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,capture_output=True,text=True,check=True)
        if 'last push : current (' not in status.stdout:raise ValueError('current actual canonical checkpoint required')
        checkpoint=(ROOT/'.resume/.last-push').read_text().strip()
        if not re.fullmatch(r'[0-9a-f]{64} \S+ s3://setec-astronomy-artifacts/checkpoints/\S+/',checkpoint):raise ValueError('canonical checkpoint receipt')
        now=datetime.now(timezone.utc)
        write_once(args.out,dict(schema='prime-field-a15-root-release/v1',execution_authorized=True,authority='Explicit root release under standing user authorization; no scientific status transition.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),
            protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,watchdog_seconds=21600,absolute_deadline=(now+timedelta(seconds=21600)).isoformat(),max_attempts=1,
            numpy_runtime=runtime_numpy.snapshot(),package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True)))


if __name__=='__main__':main()

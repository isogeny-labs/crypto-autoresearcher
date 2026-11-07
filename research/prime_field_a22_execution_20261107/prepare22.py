"""Prospective certified-query protocol and bounded remaining-window root release."""
import argparse,copy,json,subprocess,sys,re,importlib.metadata,math
from datetime import datetime,timezone,timedelta
from pathlib import Path
from deps22 import core
import runtime_numpy
from custody22 import HERE,ROOT,INPUTS,PARAMETERS,ARMS,bindings,digest,load,write_once,tools,BUDGET_INPUTS


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
    import prepare20
    p=prepare20.make_protocol(commit)
    p.update(protocol_id='PRIME-FIELD-A22-LARGER-FORMAL-TRANSFER-20261107',study_dir=str(HERE.relative_to(ROOT)),
        question='On four fresh20/21-bit curves, how do unchanged norm32/unknown16/formalpair16/known16 collectors compare in old-base information after auxiliary AND target cancellation and independent target recovery, at separate paid construction and algebra costs? Does actual direct formal substitution agree with auxiliary/native controls on every new formal case?')
    baseline={v['id']:v for v in p['arms']};instrument=copy.deepcopy(p['arms'][0]['instrument'])
    instrument.update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()),build=[[sys.executable,'-B',str(HERE.relative_to(ROOT)/'driver22.py')]])
    p['arms']=[]
    for arm in ARMS:
        if arm=='direct_on_formalpair16':
            v=dict(id=arm,role='candidate',description='Actually cold corrected A21 direct formal-coordinate substitution on the SAME own formal native case, with paid mapping, signed expansion/common-unit substitution, target membership, original-definition/common-unit native lifting and original/public checks. No checker expansion/pivots/scalars/certificates or numeric auxiliary labels.')
        else:v=copy.deepcopy(baseline[arm])
        v.update(instrument=copy.deepcopy(instrument),parameters=copy.deepcopy(PARAMETERS));p['arms'].append(v)
    p['claims'][0]['id']='A22-fresh-cancelled-information-and-formal-algebra'
    p['claims'][0]['text']+=' Fresh20/21-bit transfer, including four actually executed direct formal solver calls; no population/scaling or calibrated winner inferred.'
    p['links']['prior']='../prime_field_a21_execution_20261107/next-leads.md'
    p['analysis_plan']['script']=dict(path='analyze22.py',sha256=digest(HERE/'analyze22.py'))
    def prose(v):
        return v.replace('18/19','20/21').replace('32batch','36batch').replace('32actualbatch','36actualbatch').replace('32calls','36calls').replace('32row','36row').replace('44exclusions','48exclusions').replace('44 pinned','48 pinned').replace('A16/A17/A18/A19','A16/A17/A18/A19/A20/A21')
    for key in p['controls']:p['controls'][key]['not_applicable_reason']=prose(p['controls'][key]['not_applicable_reason'])
    p['controls']['positive']['not_applicable_reason']+=' Additional marked p<=211 repeated-archive tests execute direct substitution on all four tiny formal cases, retain actual36row/all-unknown exports and nonadditive cold-view acquisition binding. A21 signed/common-unit/native lift controls are inherited unchanged.'
    p['controls']['negative']['not_applicable_reason']+=' Refuse missing/corrupted direct producer/checker/event bindings, malformed optional JSON and native admission failure; preserve paid prefixes.'
    for value in p['variable_ledger']['independent']:
        if value['name']=='algorithm_execution':value['levels']=ARMS
    p['variable_ledger']['comparisons'][0]['arms']=ARMS
    p['variable_ledger']['comparisons']=[
        dict(id='C-collector-transfer',arms=['norm32','unknown16','formalpair16','known16'],design='one_factor',differs_in=['auxiliary_program'],threshold='Cancelled old-base information and requested target units, with all own program construction costs and nonrecoveries retained.'),
        dict(id='C-formal-algebra-transfer',arms=['formalpair16','joint_on_formalpair16','direct_on_formalpair16'],design='one_factor',differs_in=['algorithm_execution'],threshold='Same formal native input, identical requested outcomes and original/public certificates; separate actual phase vectors, no weighted winner.')]
    p['claims'][0]['decided_by']=['C-collector-transfer','C-formal-algebra-transfer']
    p['decision_rule']['comparison_ids']=['C-collector-transfer','C-formal-algebra-transfer']
    p['randomization']['arm_order_reason']='Per fixed curve: norm32,unknown16,formalpair16,known16 independently cold acquisition; all four auxiliary/prelude builds precede eight independent public target draws. Each case runs actual auxiliary-first then native joint; formal additionally runs actual direct substitution last, before information/expanded checking. No known-target suppression or borrowed caches; same formal case/prerequisite map for its three actual algebra methods.'
    p['randomization']['instance_sampling']['rule']='New domain, ALL48 prior (p,b) exclusions, first eligible a2 curves: two each in F1048573/F2097143. Same first-success formal/unknown/public-known recipes, norm32/prerequisite64/AP0source128/GENERAL8/eight public targets/all64 slots and candidate/row/width/cache caps. No redraw, favorable selection, prefix/horizon/base expansion or target/pool scalar logs. Actual field/generation public checks only after normal admission.'
    p['randomization']['seed_derivation'].update(seeds=[0]*36,note='Four fresh curves/32 public targets,16 dependent native cases and36 actual solver calls/export rows. Nine algorithm arms on four instances; only formal has direct as third solver.')
    p['sample_size']['power']['note']='Exact four-curve fresh20/21-bit census;16cases36actualcalls. No fitted scaling law or population significance.'
    p['measurement']['counters'].append('Four actual direct-formal producer calls: mapping/signed expansion/common-unit substitution/elimination/unit membership/original-definition/common-unit native lift and original/public checks. Retain separate logical scans/unit shortcuts and parsing/interpreter boundaries.')
    p['measurement']['record'].append('Each acquisition executes once physically per program. Its aux/native/direct solver cold views each include that same own acquisition as nonadditive alternative views, never summed as additional executions or borrowed from another program.')
    p['decision_rule']['text']+=' Every formal case also has actual direct21/check21 execution on exactly its own native rows and preparation; require full target mask/scalar/native/public parity. Record all same-case direct/aux/native phase vectors, including tradeoffs; acquisition belongs once in each nonadditive alternative cold view.'
    for value in p['stopping_rules']:value['rule']=prose(value['rule'])
    p['stopping_rules'][0]['rule']='Four fresh20/21-bit curves/32 independent public targets,4own cold programs=16cases;2actualsolvers per case plus4directformal calls=36calls/exportrows,16information diagnostics+4applicableexpanded+4directchecks. No redraw/horizon/base/source-prefix expansion.'
    p['extensions']['grid']='Four curves x nine actual algebra arms=36exportrows;16cases/16information diagnostics,4applicableexpanded checks and4directchecks. Formal has three cold algorithms on same input; other programs two. Dependent views, not36 independent target panels.'
    p['extensions']['direct_algorithm']='Unchanged corrected A21 direct21/check21, all203 inherited source hashes preserved. No checker rows/scalars/pivots/certificates or numericformal labels input to producer.'
    p['extensions']['costs']+=' Each program owns acquisition once physically; alternative direct formal cold view replaces only target algebra. Nonadditive alternative views are not double physical acquisition. All original setup/sign/candidate/query/lifting costs remain, diagnostics and controls separately paid.'
    p['reporting']['graphs'].append('Four fresh formal cases: direct/auxiliary/native exact target masks and phase vectors, with separate per-program acquisition and direct nonadditive cold costs.')
    p['literature'].append(dict(ref='literature.md; A21 next-leads/results/PCC-ea7120 and source4035a93fb750b5c06919b82a2359ef4e909034ba',provenance='internal',verified_by='Root primary code/result read2026-11-07 before implementation',claim='A21 conditioned component has identical26/32target masks, actual primitive/lifting tradeoffs, not a fresh transfer. This fixed new panel tests the transfer boundary without changing base/source/horizon or claiming novelty/scaling/weighted advantage.'))
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
        write_once(args.out,dict(schema='prime-field-a22-root-release/v1',execution_authorized=True,authority='Explicit bounded root release under standing user authorization; no official scientific status transition.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,interpreter_sha256=digest(Path(sys.executable).resolve()),
            protocol_sha256=protocol['freeze']['protocol_sha256'],checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,max_attempts=1,**budget,numpy_runtime=runtime_numpy.snapshot(),
            package_versions={n:importlib.metadata.version(n) for n in ['python-flint','sympy','jsonschema','PyYAML','numpy']},issued_utc=now.isoformat(),model_verified=False,model_identity=None))
        print(json.dumps(dict(release=str(args.out),execution_authorized=True,watchdog_seconds=budget['watchdog_seconds'],absolute_deadline=budget['absolute_deadline'])))


if __name__=='__main__':main()

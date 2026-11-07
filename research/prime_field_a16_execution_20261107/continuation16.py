"""Prospective bounded infrastructure amendment; never reuse the consumed release."""
import argparse,copy,json,math,subprocess,sys,importlib.metadata
from datetime import datetime,timezone
from pathlib import Path
from custody16 import HERE,ROOT,PARAMETERS,bindings,digest,load,write_once,tools
import runtime_numpy

PRIOR=HERE/'runs/a16-target-effort-3d7f9e'
EXTRA_SOURCE=[HERE/'continuation16.py',HERE/'launch_continuation16.py']
EXTRA_INPUT=[HERE/'protocol.json',HERE/'root-release.json',PRIOR/'execution.json',PRIOR/'metrics.json',
             HERE/'validation/git-memory-window-control.json']


def budget():
    release,execution,metrics=[load(p) for p in (HERE/'root-release.json',PRIOR/'execution.json',PRIOR/'metrics.json')]
    if (release['max_attempts']!=1 or execution['release_sha256']!=digest(HERE/'root-release.json') or
        execution['returncode']!=1 or execution['timeout'] or execution['exception'] or not execution['source_unchanged_after'] or
        metrics['verified_systems']!=0 or metrics['observed_completed_solver_calls']!=0 or
        metrics['observed_failed_solver_calls']!=0 or metrics['verified_information_audits']!=0 or (PRIOR/'raw').exists()):
        raise ValueError('continuation only for exact zero-data Git admission failure')
    failure=(PRIOR/'stderr.txt').read_text()
    if 'packfile'in failure and 'cannot be mapped'in failure and 'execution_gate.py'in failure:pass
    else:raise ValueError('different prior failure')
    control=load(HERE/'validation/git-memory-window-control.json')
    if control['address_space_bytes']!=2147483648 or control['records'][0]['returncode']==0 or control['records'][1]['returncode']!=0 or not control['records'][1]['matches_unlimited_reference']:
        raise ValueError('unchanged-memory exact-blob software control missing')
    charged=sum(execution[k] for k in ('cpu_user_seconds','cpu_sys_seconds','supervisor_cpu_user_seconds','supervisor_cpu_sys_seconds'))
    return dict(prior_attempt=str(PRIOR.relative_to(ROOT)),prior_release_sha256=digest(HERE/'root-release.json'),
        original_deadline=release['absolute_deadline'],memory_bytes=2147483648,concurrency=1,threads=1,
        total_cpu_ceiling_seconds=21600,prior_cpu_seconds=charged,remaining_cpu_seconds=21600-math.ceil(charged),
        additional_attempts=1,total_attempts_including_failed_admission=2,automatic_retries=0,new_paid_capacity=False,
        prior_native_data=False,git_config={'core.packedGitWindowSize':'32m','core.packedGitLimit':'128m'})


def exact(commit):
    sources,inputs=bindings(commit)
    for group,paths in [(sources,EXTRA_SOURCE),(inputs,EXTRA_INPUT)]:
        for path in paths:
            name=str(path.relative_to(ROOT));value=digest(path)
            import hashlib
            if hashlib.sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=value:raise ValueError('publish continuation closure: '+name)
            group[name]=value
    return sources,inputs


def protocol(commit):
    value=copy.deepcopy(load(HERE/'protocol.json'));b=budget();value['version']+=1
    value['freeze']=dict(status='draft',protocol_sha256=None,commit=None,frozen_at=None,filed_before_affected_data=None)
    for arm in value['arms']:arm['instrument']['commit']=commit
    value['amendments'].append(dict(id='A16-GIT-MAPPING-3d7f9e',filed='2026-11-07',filed_before_affected_data=True,
        reason='The only prior attempt failed before admission/native data because Git attempted to map a2611822952-bytepack under unchanged2GiB. A marked nonmathematical exactblob control passed using boundedGitwindows under the same limit. Preserve originalattempt/protocol/release and allunknowncases; this is a prospective explicit bounded infrastructure continuation, not a retry of consumed release or favorable scientific selection.',
        changes=['Apply inherited Git config entries plus own32MiB packedGitWindowSize/128MiB packedGitLimit before normal supervisor/gate.',
            'One separately approved additional attempt only, with same original absolute deadline and2GiB/oneworker, cumulative21600CPU seconds less all prior measured child/supervisorcharges. No further retries/newpaidcapacity.',
            'Native144source,scientificinputrules,32publictargetselection,full1260/2520/576census,controls/metrics/checkpoints/allcaps andanalyzer unchanged; no actualscientificdata existedbeforeamendment.'],
        supersedes_fields=['stopping_rules.budget','extensions.cloud_policy']))
    for rule in value['stopping_rules']:
        if rule['kind']=='budget':rule['rule']='One existingworker/thread2GiB; original deadline '+b['original_deadline']+' unchanged, cumulative21600CPU seconds with priorCPU '+str(b['prior_cpu_seconds'])+' charged. One explicit additional attempt after zero-data Git admission failure, newrelease/consumedmarker; twoattemptstotal, zeroautomaticretries, no newpaidcapacity.'
    value['extensions']['cloud_policy']=value['stopping_rules'][-1]['rule'];value['extensions']['infrastructure_continuation']=b
    value['extensions']['prior_outcome']='runs/a16-target-effort-3d7f9e:exit1,0nativegeneration/solvers,all1260unknown; originalimmutable.'
    value['reporting']['graphs'].append('Retained prior zero-data admission failure diagram and source/budget/Git mapping control; report both protocolversions.')
    return value


def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('protocol');a.add_argument('--source-commit',required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--freeze',action='store_true')
    a=s.add_parser('release');a.add_argument('--source-commit',required=True);a.add_argument('--protocol',type=Path,required=True);a.add_argument('--assessment',type=Path,required=True);a.add_argument('--owner',required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--authorize-root',action='store_true',required=True)
    args=p.parse_args();source,inputs=exact(args.source_commit);b=budget();t=tools()
    if datetime.now(timezone.utc)>=datetime.fromisoformat(b['original_deadline']):raise ValueError('original deadline expired; no continuation')
    if args.action=='protocol':
        value=protocol(args.source_commit);errors=t.schema_errors(value,'experiment.protocol/v1') or t.lint_protocol(value,HERE)
        if errors:raise ValueError(json.dumps(errors))
        write_once(args.out,value)
        if args.freeze:t.freeze(args.out,args.source_commit,True)
    else:
        assessment=load(args.assessment);frozen=load(args.protocol)
        if assessment.get('administratively_approvable')is not True or assessment.get('additional_attempts_approved')!=1 or assessment.get('source_commit')!=args.source_commit:
            raise ValueError('explicit exact-source bounded Coordinator continuation assessment required')
        if assessment.get('budget')!=b:raise ValueError('assessment budget differs')
        if frozen['freeze']['status']!='frozen' or frozen['freeze']['commit']!=args.source_commit or frozen['freeze']['filed_before_affected_data']is not True or frozen['extensions']['infrastructure_continuation']!=b:
            raise ValueError('prospective exact bounded amendment required')
        for path in (args.protocol,args.assessment):
            if subprocess.check_output(['git','show','HEAD:'+str(path.resolve().relative_to(ROOT))],cwd=ROOT)!=path.read_bytes():raise ValueError('publish frozen amendment/assessment unchanged')
        status=subprocess.check_output(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,text=True)
        if 'last push : current ('not in status:raise ValueError('current actual canonical checkpoint required')
        prior=load(HERE/'root-release.json');now=datetime.now(timezone.utc)
        value=dict(prior,owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=inputs,
            protocol_sha256=frozen['freeze']['protocol_sha256'],prior_checkpoint=(ROOT/'.resume/.last-push').read_text().strip(),
            absolute_deadline=b['original_deadline'],watchdog_seconds=b['remaining_cpu_seconds'],issued_utc=now.isoformat(),
            authority='Explicit root release under standing user authorization and exact Coordinator bounded infrastructure amendment; original allowance/deadline/cumulative charges preserved.',
            infrastructure_continuation=b,continuation_assessment_sha256=digest(args.assessment),max_attempts=1,
            numpy_runtime=runtime_numpy.snapshot(),package_versions={n:importlib.metadata.version(n) for n in prior['package_versions']},interpreter_sha256=digest(Path(sys.executable).resolve()))
        write_once(args.out,value)
    print(json.dumps(dict(action=args.action,out=str(args.out),budget=b)))


if __name__=='__main__':main()

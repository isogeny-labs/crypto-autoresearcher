"""Prospective local launcher. No candidate import; no launch without exact admission."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import time
import uuid


def sha(p):
    digest = hashlib.sha256()
    with Path(p).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_once(path, value):
    """Durable atomic no-replace publication; reservations survive migration."""
    data=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    tmp=path.parent/('.'+path.name+'.'+uuid.uuid4().hex)
    try:
        with tmp.open('xb') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        os.link(tmp,path)  # fails if final path already exists
        fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if tmp.exists():tmp.unlink()


def command(argv):
    try:
        r=subprocess.run(argv,text=True,capture_output=True,timeout=20)
        return {'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    except BaseException as e:
        return {'argv':argv,'returncode':None,'stdout':(getattr(e,'stdout',None) or b'').decode(errors='replace') if isinstance(getattr(e,'stdout',None),bytes) else (getattr(e,'stdout',None) or ''),'stderr':(getattr(e,'stderr',None) or b'').decode(errors='replace') if isinstance(getattr(e,'stderr',None),bytes) else (getattr(e,'stderr',None) or ''),'error':{'type':type(e).__name__,'message':str(e)}}


def props(observation):
    if observation.get('returncode')!=0:return {}
    return dict(x.split('=',1) for x in observation['stdout'].splitlines() if '=' in x)


def stopped(v):
    return v.get('LoadState')=='not-found' or (v.get('MainPID')=='0' and v.get('ActiveState') in ('inactive','failed') and v.get('SubState') in ('dead','failed'))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--authorization',type=Path,required=True);args=ap.parse_args()
    auth=json.loads(args.authorization.read_text());auth_hash=sha(args.authorization)
    if auth.get('execution_authorized') is not True or auth.get('approved_by')!='coordinator':raise PermissionError('published execution admission missing')
    if auth.get('cloud_authorized') is not False or auth.get('snapshot_terminal') is not True:raise PermissionError('local terminal snapshot required')
    role,index=auth['role'],auth['attempt_index']
    if (role,index) not in [('producer',1),('producer',2),('independent',3)]:raise ValueError('fixed attempt slots')
    repo=Path(auth['repository_root']).resolve();output=(repo/auth['output_path']).resolve();campaign=(repo/auth['campaign_path']).resolve()
    for p in [output,campaign]:
        if not p.is_relative_to(repo/'research/prime_sat_transform_integration_20261103'):raise ValueError('output scope')
    for name,h in auth['launch_files_sha256'].items():
        if sha(repo/name)!=h:raise RuntimeError('launcher drift')
    for group in ['source16_sha256','baseline_sha256','runtime_files_sha256']:
        for name,h in auth['bindings'][group].items():
            if sha(Path(name) if Path(name).is_absolute() else repo/name)!=h:raise RuntimeError('input drift: '+name)
    unit='prime-transform-'+auth['task_id'].lower()+'-'+str(index)
    description='prime-transform-auth-'+auth_hash
    fields=['LoadState','ActiveState','SubState','Result','ExecMainCode','ExecMainStatus','ExecMainPID','MainPID','ControlGroup','CPUQuotaPerSecUSec','MemoryMax','MemorySwapMax','RuntimeMaxUSec','OOMPolicy','Description','InvocationID','User']
    show=['systemctl','show',unit]+['--property='+x for x in fields]
    pre=command(show)
    if props(pre).get('LoadState')!='not-found':raise RuntimeError('unit existence uncertain or existing; do not launch/stop it')
    campaign.mkdir(parents=True,exist_ok=True)
    with (campaign/'owner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        slots=[campaign/('slot-'+str(i)+'.json') for i in (1,2,3) if (campaign/('slot-'+str(i)+'.json')).exists()]
        if len(slots)>=3:raise RuntimeError('attempt ceiling')
        if index==2:
            prior=campaign/'slot-1.terminal.json'
            if not prior.exists() or auth.get('second_attempt_authorized') is not True or sha(prior)!=auth.get('first_terminal_sha256'):raise PermissionError('second attempt not admitted')
        output.mkdir(parents=True,exist_ok=False)
        write_once(campaign/('slot-'+str(index)+'.json'),{'authorization_sha256':auth_hash,'reserved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':role,'index':index,'unit':unit})
        python=auth['bindings']['interpreter'];worker=repo/auth['worker_path']
        argv=['sudo','-n','systemd-run','--quiet','--unit='+unit,'--description='+description,'--property=Type=exec','--property=User='+auth['worker_user'],'--property=Group='+auth['worker_group'],'--property=CPUQuota=100%','--property=MemoryMax=2147483648','--property=MemorySwapMax=0','--property=RuntimeMaxSec=600','--property=TimeoutStopSec=1','--property=KillSignal=SIGKILL','--property=KillMode=control-group','--property=SendSIGKILL=yes','--property=OOMPolicy=stop','--property=RemainAfterExit=yes','--property=WorkingDirectory='+str(repo),'--property=StandardOutput=append:'+str(output/'stdout.log'),'--property=StandardError=append:'+str(output/'stderr.log'),'--setenv=PYTHONDONTWRITEBYTECODE=1','--setenv=OMP_NUM_THREADS=1','--setenv=OPENBLAS_NUM_THREADS=1',python,str(worker),str(args.authorization.resolve()),str(output)]
        states=[];secondary=[];primary=None;owned_invocation=None;terminal_values=None;safe=False;start=time.monotonic();launched=None
        def save(name,value):
            try:write_once(output/name,value)
            except BaseException as e:secondary.append({'phase':'save '+name,'type':type(e).__name__,'message':str(e)})
        save('command.json',{'argv':argv,'authorization_sha256':auth_hash,'preexisting_unit_check':pre,'timeout_includes_imports':True,'cpu_quota_not_affinity':True})
        try:
            if secondary:raise RuntimeError('required command custody failed; worker not launched')
            launched=command(argv);save('launch-result.json',launched)
            state=command(show);states.append(state);v=props(state)
            # A failed/ambiguous creation is never assumed owned merely by unit name.
            if v.get('Description')==description and v.get('InvocationID') and v.get('User')==auth['worker_user']:
                owned_invocation=v['InvocationID']
            if launched['returncode']!=0:raise RuntimeError('creation failed/ambiguous; preserve slot and identity')
            if owned_invocation is None:raise RuntimeError('created-unit identity not established')
            while time.monotonic()-start<605:
                state=command(show);states.append(state);v=props(state)
                if v.get('InvocationID')!=owned_invocation or v.get('Description')!=description:raise RuntimeError('unit identity changed/unknown')
                if v.get('MainPID')=='0' and v.get('SubState') in ('exited','failed','dead'):
                    terminal_values=v;break
                time.sleep(0.2)
            if terminal_values is None:raise TimeoutError('outer watchdog; unit requires owned cleanup')
        except BaseException as e:primary={'type':type(e).__name__,'message':str(e)}
        finally:
            # Each collection operation is isolated; none masks primary or skips owned cleanup.
            try:
                state=command(show);states.append(state);v=props(state)
                if owned_invocation is None and v.get('Description')==description and v.get('InvocationID') and v.get('User')==auth['worker_user']:owned_invocation=v['InvocationID']
                if owned_invocation is not None and v.get('InvocationID')==owned_invocation and v.get('Description')==description:
                    if terminal_values is None and v.get('MainPID')=='0' and v.get('SubState') in ('exited','failed','dead'):terminal_values=v
                    stop=command(['sudo','-n','systemctl','stop',unit]);save('unit-stop.json',stop)
                    after=command(show);states.append(after);save('unit-after-stop.json',after)
                    safe=stop.get('returncode')==0 and stopped(props(after))
                elif props(state).get('LoadState')=='not-found':
                    safe=True  # positive absence; no stop of an unowned name
                else:secondary.append({'phase':'cleanup','message':'unit ownership/state unknown; no blind stop or duplicate launch'})
            except BaseException as e:secondary.append({'phase':'owned cleanup','type':type(e).__name__,'message':str(e)})
            save('systemd-state.json',{'observations':states,'owned_invocation':owned_invocation,'terminal_values':terminal_values,'primary_error':primary,'secondary_errors':secondary.copy()})
            successful_exit=terminal_values is not None and terminal_values.get('Result')=='success' and terminal_values.get('ExecMainCode')=='1' and terminal_values.get('ExecMainStatus')=='0' and terminal_values.get('MainPID')=='0'
            outcome={'role':role,'attempt_index':index,'elapsed_launcher_seconds':time.monotonic()-start,'unit_terminal_observed':terminal_values is not None,'unit_termination_established':safe,'primary_error':primary,'secondary_errors':secondary.copy(),'source_commit':auth['source_commit'],'scientific_status':'complete_unverified' if successful_exit and primary is None and not secondary and (output/'results.json').exists() and not (output/'worker-error.json').exists() else 'incomplete','no_automatic_retry':True}
            save('launcher-preliminary.json',{**outcome,'receipt_scope':'preliminary before raw collection; not authoritative'})
            try:
                with tarfile.open(output/'raw-artifacts.tar','x') as tf:
                    if (output/'raw').exists():tf.add(output/'raw',arcname='raw',recursive=True)
            except BaseException as e:secondary.append({'phase':'raw bundle','type':type(e).__name__,'message':str(e)})
            try:
                files={str(p.relative_to(output)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.rglob('*')) if p.is_file()}
                save('artifact-manifest.json',{'files':files,'missing_results':not (output/'results.json').exists(),'missing_stdout':not (output/'stdout.log').exists(),'missing_stderr':not (output/'stderr.log').exists(),'secondary_errors':secondary.copy()})
            except BaseException as e:secondary.append({'phase':'manifest','type':type(e).__name__,'message':str(e)})
            outcome['secondary_errors']=secondary.copy()
            if secondary or not safe:outcome['scientific_status']='incomplete'
            outcome['receipt_scope']='final after raw collection and artifact manifest'
            try:outcome['artifact_manifest_sha256']=sha(output/'artifact-manifest.json')
            except BaseException as e:
                secondary.append({'phase':'manifest binding','type':type(e).__name__,'message':str(e)});outcome['scientific_status']='incomplete'
            outcome['secondary_errors']=secondary.copy()
            save('launcher-receipt.json',outcome)
            outcome['secondary_errors']=secondary.copy()
            if secondary:outcome['scientific_status']='incomplete'
            try:write_once(campaign/('slot-'+str(index)+'.terminal.json'),outcome)
            except BaseException as e:
                secondary.append({'phase':'terminal receipt','type':type(e).__name__,'message':str(e)});print(json.dumps({'primary':primary,'secondary':secondary,'outcome':outcome}),flush=True)
            if primary or secondary or not safe or not successful_exit or outcome['scientific_status']!='complete_unverified':raise RuntimeError(json.dumps({'primary':primary,'secondary':secondary,'termination_established':safe,'successful_exit':successful_exit}))


if __name__=='__main__':main()

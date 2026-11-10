"""Native trial custody adapter; candidate work exists only in bounded launch.py worker."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile


def digest(p):
    digest = hashlib.sha256()
    with Path(p).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()
def put(p,value):
    with p.open('x') as f:f.write(json.dumps(value,indent=2,allow_nan=False)+'\n')


def main():
    a=argparse.ArgumentParser();a.add_argument('--run-dir',type=Path,required=True);a.add_argument('--config',type=Path);a.add_argument('--check',action='store_true');args=a.parse_args();out=args.run_dir.resolve()
    if args.check:
        summary=json.loads((out/'raw-result.json').read_text());inventory=json.loads((out/'bundle-manifest.json').read_text())
        for n,h in inventory['files'].items():
            p=out/n
            if not p.resolve().is_relative_to(out) or digest(p)!=h:raise RuntimeError('custody digest mismatch')
        if summary['scientific_status']!='complete_unverified' or summary['launcher_returncode']!=0 or not summary['terminal_receipt_present'] or not summary['unit_termination_established']:raise RuntimeError('attempt incomplete; preserve actual failure')
        # Only custody checked here; independent scientific acceptance remains reviewer/Coordinator.
        return
    cfg=json.loads(args.config.read_text());repo=Path(cfg['repository_root']);launch=json.loads((out/'launch.json').read_text());plan=repo/cfg['trial_plan']
    if digest(plan)!=launch['plan_sha256']:raise RuntimeError('native launch plan mismatch')
    frozen=json.loads(plan.read_text())
    if frozen.get('approved_by')!=cfg['approval_decision'] or frozen.get('candidate_only') is True or frozen.get('frozen') is not True:raise PermissionError('approved native plan required')
    if not launch.get('authority') or launch['trial_id']!=cfg['trial_id']:raise PermissionError('native authority missing')
    auth=json.loads((repo/cfg['authorization_template']).read_text())
    if auth['execution_authorized'] is not False:raise RuntimeError('template unexpectedly enabled')
    auth.update(execution_authorized=True,approved_by='coordinator',protocol_freeze=cfg['protocol'],publication_receipt=launch['authority'])
    authpath=out/'attempt-authorization.json';put(authpath,auth)
    # The inner system unit enforces600 seconds before imports. Outer driver only collects receipts.
    proc=subprocess.run([auth['bindings']['interpreter'],str(repo/cfg['launcher']),'--authorization',str(authpath)],check=False)
    actual=repo/auth['output_path'];receipt=actual/'launcher-receipt.json';terminal=repo/auth['campaign_path']/('slot-'+str(auth['attempt_index'])+'.terminal.json')
    body=json.loads(terminal.read_text()) if terminal.exists() else (json.loads(receipt.read_text()) if receipt.exists() else {})
    summary={'scientific_status':body.get('scientific_status','incomplete'),'launcher_returncode':proc.returncode,'launcher_receipt_present':receipt.exists(),'terminal_receipt_present':terminal.exists(),'unit_termination_established':body.get('unit_termination_established') is True,'attack_claimed':False,'acceptance':'unverified; independent review required','missing_results':not (actual/'results.json').exists()}
    put(out/'raw-result.json',summary)
    with tarfile.open(out/'attempt-files.tar','x') as archive:
        if actual.exists():archive.add(actual,arcname='actual-attempt')
        if terminal.exists():archive.add(terminal,arcname='slot-terminal.json')
    put(out/'bundle-manifest.json',{'files':{n:digest(out/n) for n in ['attempt-authorization.json','raw-result.json','attempt-files.tar']}})
    # Native supervisor fills authority/environment/timing schema fields from actual observations.
    put(out/'manifest.yaml',{'run':{'status':'completed' if proc.returncode==0 else 'failed','status_note':'Driver custody completion does not establish software correctness.','result':{'certificate':{'kind':'none'},'summary':summary},'attack_claimed':False}})
    if proc.returncode:raise RuntimeError('bounded attempt failed; actual artifacts retained')

if __name__=='__main__':main()

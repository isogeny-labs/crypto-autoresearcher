"""Immediate producer receipts and paused closed-curve canonical checkpoints."""
from datetime import datetime,timezone
from pathlib import Path
import json,os,subprocess
from custody16 import ROOT,write_once
from streams14 import append,lines,close_encodings


def checkpoint(run,kind,counts):
    now=datetime.now(timezone.utc).isoformat()
    with (ROOT/'.resume/RESUME.md').open('a') as stream:
        stream.write('\nA16 '+kind+' '+now+': '+json.dumps(counts,sort_keys=True)+'. Same one consumed release, no retry; current writers closed before canonical checkpoint.\n')
    p=subprocess.run(['bash','scripts/checkpoint.sh','push'],cwd=ROOT,capture_output=True,text=True)
    receipt=dict(command=['bash','scripts/checkpoint.sh','push'],returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,
        observed_utc=datetime.now(timezone.utc).isoformat(),**counts)
    write_once(Path(run)/('checkpoint-'+kind+'.json'),receipt)
    if p.returncode:raise RuntimeError('actual canonical checkpoint failed: '+p.stderr)
    return receipt


def admitted_start(run,admission):
    child=json.loads((Path(run)/'child.json').read_text())
    return checkpoint(run,'admitted-start',dict(child_pid=os.getpid(),supervisor_pid=child['supervisor_pid'],
        child_process_group=child['child_process_group'],admission_last_push=admission['last_push'],native_curves_generated=0))


def checkpoint_curve(run,cid,cases,curves):
    return checkpoint(run,cid,dict(closed_curve=cid,checked_cases=cases,completed_curves=curves))

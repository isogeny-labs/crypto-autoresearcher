"""Real start/closed-curve checkpoints; never checkpoint open scientific journals."""
from datetime import datetime,timezone
from pathlib import Path
import json,os,subprocess
from custody20 import ROOT,write_once
from streams14 import append,lines,close_encodings


def checkpoint(run,kind,counts):
    with (ROOT/'.resume/RESUME.md').open('a') as stream:
        stream.write('\nA20 '+kind+' '+datetime.now(timezone.utc).isoformat()+': '+json.dumps(counts,sort_keys=True)+'. One consumed attempt, no retry; all scientific writers closed before this checkpoint.\n')
    p=subprocess.run(['bash','scripts/checkpoint.sh','push'],cwd=ROOT,capture_output=True,text=True)
    value=dict(command=['bash','scripts/checkpoint.sh','push'],returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,
        observed_utc=datetime.now(timezone.utc).isoformat(),**counts)
    write_once(Path(run)/('checkpoint-'+kind+'.json'),value)
    if p.returncode:raise RuntimeError('actual canonical checkpoint failed: '+p.stderr)
    return value


def admitted_start(run,admission):
    child=json.loads((Path(run)/'child.json').read_text())
    return checkpoint(run,'admitted-start',dict(child_pid=os.getpid(),child_process_group=child['child_process_group'],
        supervisor_pid=child['supervisor_pid'],admission_last_push=admission['last_push'],native_curves_generated=0))


def checkpoint_curve(run,cid,curves,cases,batches,online):
    return checkpoint(run,cid,dict(closed_curve=cid,completed_curves=curves,checked_cases=cases,
        checked_batch_solver_calls=batches,completed_online_engines=online))

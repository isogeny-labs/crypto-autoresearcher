"""Run bounded question-to-plan-to-answer-to-review campaigns and replay their grading."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time

from . import capability_actor as actors
from . import capability_tasks as tasks
from . import capability_report as reports

REPO = Path(__file__).resolve().parents[2]
STAGES = {'single': ['execute'], 'planned': ['plan','execute'],
          'reviewed': ['plan','execute','review','revise']}


def write_once(path, value):
    with Path(path).open('x') as f:
        json.dump(value,f,indent=2,allow_nan=False)
        f.write('\n')


def schedule(spec):
    """Matched instances and repeat seeds; deterministic randomized arm order."""
    rows=[]
    for task in spec['tasks']:
        for i in range(spec['instances']):
            seed=int(hashlib.sha256(f"{spec['seed']}:{spec['split']}:{task['id']}:{i}".encode()).hexdigest()[:16],16)
            for repeat in range(spec['repeats']):
                arms=list(spec['arms'])
                random.Random(seed+repeat).shuffle(arms)
                rows.extend({'task_id':task['id'],'instance':i,'repeat':repeat,'seed':seed,'arm':a} for a in arms)
    return rows


def valid_stage(stage, artifact):
    if not isinstance(artifact,dict): return False
    if stage == 'plan':
        return (isinstance(artifact.get('steps'),list) and bool(artifact['steps'])
                and all(isinstance(s,str) and s.strip() for s in artifact['steps']))
    if stage == 'review':
        return type(artifact.get('approved')) is bool and isinstance(artifact.get('feedback'),str)
    return True


def token_total(records):
    if any(not all(k in r.get('usage',{}) for k in ('input_tokens','output_tokens')) for r in records):
        return None
    return sum(r['usage']['input_tokens'] + r['usage']['output_tokens'] for r in records)


def run_one(spec, item, directory, actor):
    task=next(t for t in spec['tasks'] if t['id']==item['task_id'])
    public, reference=tasks.instance(task,item['seed'])
    write_once(directory/'input.json',public)
    previous={}; records=[]; answer=None; claimed=False; outcome='completed'
    started=time.monotonic(); budget=spec['budget']
    for stage in STAGES[item['arm']]:
        remaining=budget['wall_seconds']-(time.monotonic()-started)
        if remaining<=0:
            outcome='budget_exhausted';break
        stage_input={'stage':stage,'public':public,'previous':previous}
        write_once(directory/f'{stage}-input.json',stage_input)
        try:
            result=actor(stage,public,previous,seconds=remaining)
        except Exception as exc:
            result={'status':'infrastructure_error','error':f'{type(exc).__name__}: {exc}',
                    'usage':{},'cost_usd':None,'wall_seconds':time.monotonic()-started,
                    'claim_success':False,'artifact':None,'tool_violations':0}
        records.append(result)
        write_once(directory/f'{stage}-result.json',result)
        if result['status']!='completed':
            outcome=result['status'];break
        if not valid_stage(stage,result['artifact']):
            outcome='invalid_output';break
        if stage=='plan': previous['plan']=result['artifact']
        elif stage=='review': previous['review']=result['artifact']
        else:
            answer=result['artifact'];claimed=result['claim_success']
            previous['answer']=answer
    passed=outcome=='completed' and tasks.grade(answer,reference)
    if outcome=='completed' and not passed: outcome='incorrect_answer'
    costs=[r['cost_usd'] for r in records]
    row={**item,'input_sha256':tasks.digest(public),'verified':passed,
         'claimed_success':claimed,'false_success':claimed and not tasks.grade(answer,reference),
         'outcome':outcome,'human_interventions':0,'stages_attempted':len(records),
         'wall_seconds':time.monotonic()-started,
         'total_tokens':token_total(records),
         'cost_usd':sum(costs) if costs and all(c is not None for c in costs) else None,
         'answer':answer}
    write_once(directory/'result.json',row)
    return row


def fingerprint():
    paths=['orchestration/eval/capability_'+suffix+'.py' for suffix in ('tasks','actor','campaign','report')]
    paths += ['orchestration/eval/report.py','tools/experiment_protocol.py','schemas/experiment-protocol.v1.json','schemas/experiment-export.v1.json','agents/coordinator.md','agents/executor.md','agents/validator.md']
    return {name:hashlib.sha256((REPO/name).read_bytes()).hexdigest() for name in paths}


def run(spec, out, *, mode='control', actor=None, model=None, effort='xhigh', protocol=None):
    spec=tasks.validate(spec)
    controls=tasks.controls(spec)
    out=Path(out)
    # Atomic allocation prevents a retry from replacing or duplicating an interrupted campaign.
    out.mkdir(parents=True,exist_ok=False)
    write_once(out/'spec.json',spec)
    metadata={'schema':'autoresearch.capability-run/v1','mode':mode,'spec_sha256':tasks.digest(spec),
              'source_sha256':fingerprint(),'model':model,'reasoning_effort':effort,
              'protocol':protocol,'controls':controls,'schedule':schedule(spec),
              'created_unix':time.time(),'max_sessions':sum(len(STAGES[r['arm']]) for r in schedule(spec)),
              'scope':'supplied-input no-tools campaign; not open-ended discovery',
              'native_version':subprocess.run(['codex','--version'],capture_output=True,text=True,timeout=15).stdout.strip() if mode=='live' and actor is None else None}
    write_once(out/'manifest.json',metadata)
    if protocol is not None:
        write_once(out/'protocol.json',json.loads(Path(protocol['path']).read_text()))
    if actor is None:
        if mode=='live':
            actor=lambda stage,public,previous,seconds: actors.codex(stage,public,previous,
                seconds=seconds,model=model,effort=effort,budget=spec['budget'])
        else:
            actor=lambda stage,public,previous,seconds: actors.scripted(stage,public,previous,corrupt=mode=='negative_control')
    rows=[]
    for index,item in enumerate(metadata['schedule']):
        directory=out/f'trial-{index:04d}';directory.mkdir()
        row=run_one(spec,item,directory,actor)
        rows.append(row)
        print(f"{index+1}/{len(metadata['schedule'])} {item['task_id']} {item['arm']}: {row['outcome']}",flush=True)
    report=reports.write_report(out,spec,rows,mode)
    if protocol is not None:
        export_bundle(out, rows, metadata, protocol)
    seal(out)
    return report


def export_bundle(out, rows, metadata, binding):
    """Bind every attempt, including failures, to the shared experiment export."""
    from tools import experiment_protocol as ep
    protocol=ep.read_json(out/'protocol.json')
    export=ep.export_skeleton(protocol,'protocol.json','manual','capability-'+metadata['spec_sha256'][:16])
    export['producer'].update(runtime='codex',model=metadata['model'])
    analysis=protocol['analysis_plan']['script']
    if analysis is not None:
        path=Path(binding['path']).parent/analysis['path']
        with (out/'analysis.py').open('xb') as f: f.write(path.read_bytes())
        analysis=ep.file_entry(out,'analysis.py','analysis')
    export['analysis'].update(script=analysis,
                              outputs=[ep.file_entry(out,n,'summary') for n in ('report.json','report.md','graph.svg')])
    for arm in export['arms']:
        declared=next(a for a in protocol['arms'] if a['id']==arm['id'])
        arm.update(binary_sha256=declared['instrument']['binary_sha256'],commit=declared['instrument']['commit'])
    for i,row in enumerate(rows):
        status=('succeeded' if row['verified'] else 'timeout' if row['outcome']=='budget_exhausted'
                else 'infra_error' if row['outcome']=='infrastructure_error' else 'failed')
        export['runs'].append(ep.run_row(run_id=f'trial-{i:04d}',arm=row['arm'],
            instance_id=f"{row['task_id']}-{row['instance']}",seed=row['seed'],replicate=row['repeat'],status=status,
            measurements={'counted':{'verified':int(row['verified']),'false_success':int(row['false_success'])},
                          'wall_seconds':row['wall_seconds'],'wall_valid':False},
            isolation={'tier':'L0'}, verification={'status':'verified' if row['verified'] else 'no_claim',
            'verifier':'capability_tasks.grade'},artifacts=[ep.file_entry(out,f'trial-{i:04d}/result.json','raw')]))
    export['flow']=ep.compute_flow(export['runs'])
    export['files']=[ep.file_entry(out,p.relative_to(out).as_posix(),'raw')
                     for p in sorted(out.rglob('*')) if p.is_file()]
    errors=ep.schema_errors(export,'experiment.export/v1') or ep.lint_export(export,protocol,out,True)
    if errors: raise ValueError('export validation failed: '+ '; '.join(errors))
    write_once(out/'export.json',export)


def seal(out):
    hashes={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.rglob('*')) if p.is_file() and p.name!='sha256.json'}
    write_once(out/'sha256.json',hashes)


def replay(out):
    out=Path(out)
    hashes=json.loads((out/'sha256.json').read_text())
    actual={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name!='sha256.json'}
    if actual!=set(hashes): raise ValueError('bundle file inventory differs from seal')
    for name,sha in hashes.items():
        path=out/name
        if path.is_symlink() or not path.resolve().is_relative_to(out.resolve()):
            raise ValueError('unsafe artifact path')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError(f'changed artifact: {name}')
    spec=tasks.load(out/'spec.json');manifest=json.loads((out/'manifest.json').read_text())
    if manifest['spec_sha256']!=tasks.digest(spec) or manifest['schedule']!=schedule(spec):
        raise ValueError('specification or trial schedule mismatch')
    rows=[]
    for index,item in enumerate(manifest['schedule']):
        directory=out/f'trial-{index:04d}'
        row=json.loads((directory/'result.json').read_text())
        task=next(t for t in spec['tasks'] if t['id']==item['task_id'])
        public,reference=tasks.instance(task,item['seed'])
        if any(row[k]!=v for k,v in item.items()) or row['input_sha256']!=tasks.digest(public):
            raise ValueError('trial identity mismatch')
        if json.loads((directory/'input.json').read_text())!=public:
            raise ValueError('input differs from generated instance')
        previous={}; answer=None; claimed=False; records=[]; derived='completed'
        for stage in STAGES[item['arm']]:
            path=directory/f'{stage}-result.json'
            if not path.exists():
                derived='budget_exhausted'; break
            result=json.loads(path.read_text()); records.append(result)
            if json.loads((directory/f'{stage}-input.json').read_text()) != {
                    'stage':stage,'public':public,'previous':previous}:
                raise ValueError('stage input mismatch')
            if result['status']!='completed': derived=result['status']; break
            if not valid_stage(stage,result['artifact']): derived='invalid_output'; break
            if stage=='plan': previous['plan']=result['artifact']
            elif stage=='review': previous['review']=result['artifact']
            else:
                answer=result['artifact'];claimed=result['claim_success'];previous['answer']=answer
        if derived=='completed' and not tasks.grade(answer,reference): derived='incorrect_answer'
        costs=[r['cost_usd'] for r in records]
        cost=sum(costs) if costs and all(c is not None for c in costs) else None
        if (row['answer']!=answer or row['claimed_success']!=claimed or row['outcome']!=derived
                or row['stages_attempted']!=len(records) or row['total_tokens']!=token_total(records)
                or row['cost_usd']!=cost or row['human_interventions']!=0):
            raise ValueError('stage/result reconciliation failed')
        expected=(row['outcome'] in ('completed','incorrect_answer')) and tasks.grade(row['answer'],reference)
        if row['verified']!=expected or row['false_success']!=(row['claimed_success'] and not tasks.grade(row['answer'],reference)):
            raise ValueError('grader replay mismatch')
        rows.append(row)
    report=reports.summarize(spec,rows,mode=manifest['mode'])
    if report!=json.loads((out/'report.json').read_text()): raise ValueError('report recomputation mismatch')
    return {'verified':True,'trials':len(rows),'mode':manifest['mode'],'spec_sha256':tasks.digest(spec)}


def check_protocol(path,spec):
    # Reuse the existing cross-repository preregistration checker.
    from tools import experiment_protocol as ep
    path=Path(path)
    p=ep.read_json(path)
    errors=ep.schema_errors(p,'experiment.protocol/v1')
    if not errors: errors=ep.lint_protocol(p,path.parent)
    if errors: raise ValueError('invalid protocol: '+ '; '.join(errors))
    if p['freeze']['status']!='frozen' or not p['freeze']['filed_before_affected_data']:
        raise ValueError('live evaluation requires a prospectively frozen protocol')
    if p.get('links',{}).get('capability_campaign_sha256')!=tasks.digest(spec):
        raise ValueError('protocol does not bind this campaign specification')
    if p.get('links',{}).get('source_sha256') != tasks.digest(fingerprint()):
        raise ValueError('protocol source hashes do not match this evaluator')
    if {a['id'] for a in p['arms']} != set(spec['arms']):
        raise ValueError('protocol arms do not match campaign')
    if p['sample_size']['instances'] != len(spec['tasks'])*spec['instances'] or p['sample_size']['replicates'] != spec['repeats']:
        raise ValueError('protocol sample counts do not match campaign')
    return {'path':str(path.resolve()),'sha256':p['freeze']['protocol_sha256']}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('validate','control','run'):
        p=sub.add_parser(name);p.add_argument('--spec',required=True)
        if name!='validate': p.add_argument('--out',required=True)
        if name=='control': p.add_argument('--negative',action='store_true')
        if name=='run':
            p.add_argument('--model',required=True);p.add_argument('--effort',default='xhigh',choices=['xhigh','max'])
            p.add_argument('--protocol',required=True);p.add_argument('--max-sessions',type=int,required=True)
    p=sub.add_parser('replay');p.add_argument('directory')
    args=parser.parse_args(argv)
    try:
        if args.command=='replay': print(json.dumps(replay(args.directory)));return 0
        spec=tasks.load(args.spec)
        if args.command=='validate':
            print(json.dumps({'valid':True,'controls':tasks.controls(spec),'trials':len(schedule(spec)),
                              'maximum_sessions':sum(len(STAGES[r['arm']]) for r in schedule(spec))}));return 0
        protocol=None
        if args.command=='run':
            required=sum(len(STAGES[r['arm']]) for r in schedule(spec))
            if args.max_sessions<required: raise ValueError(f'campaign requires {required} sessions, exceeding cap')
            protocol=check_protocol(args.protocol,spec)
            declared=json.loads(Path(args.protocol).read_text())
            if any(a['instrument']['flags'].get('model') != args.model or
                   a['instrument']['flags'].get('reasoning_effort') != args.effort for a in declared['arms']):
                raise ValueError('model or reasoning effort differs from frozen protocol')
            login=subprocess.run(['codex','login','status'],capture_output=True,text=True,timeout=15)
            if login.returncode!=0: raise ValueError('no usable Codex login; no trials launched')
        report=run(spec,args.out,mode=('live' if args.command=='run' else 'negative_control' if args.negative else 'control'),
                   model=getattr(args,'model',None),effort=getattr(args,'effort','xhigh'),protocol=protocol)
        print(reports.markdown(report))
        return 0
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as exc:
        print(f'capability error: {exc}',file=sys.stderr);return 2


if __name__=='__main__': raise SystemExit(main())

"""Conservative AST closure plus an execution audit hook; no subset acceptance."""
from pathlib import Path
import ast,base64,hashlib,sys
NATIVE=('tools/experiment_execution.py','tools/experiment_protocol.py','tools/artifact_store.py','tools/research_dispatch.py','tools/goal_lanes.py','tools/experiment_preapproval.py','tools/newest_experiments.py','tools/check_review_independence.py','tools/validate_ledger.py')
DATA=('schemas/experiment-protocol.v1.json','schemas/experiment-export.v1.json','schemas/experiment-review.v1.json','tools/schema_supersession_registry.yaml','tools/run_supersession_registry.yaml','tools/validate_ledger_baseline.txt','orchestration/research-priority.yaml','orchestration/model-policies.yaml','orchestration/model-bindings.yaml','orchestration/roles.yaml')
V5='harness/classical_ecdlp_controlled_followup_v5/'
NAMES=('driver.py','candidate.py','baseline.py','cohort_adapter.py','export.py','check.py','test_contracts.py','lifecycle.py','observer.py','source_closure.py','public_verify.py','fixtures.json','interface.json','format-contract.json','source-manifest.json','resource-envelope.json')
MATH='harness/classical_ecdlp_controlled_followup/'
MATH_NAMES=('cohort.py','constructor.py','curve.py','engine.py','host/reference.py','host/verify.py')
EVENTS=[]
def reconstruct(repo,here):
 repo=Path(repo).resolve();here=Path(here).resolve();paths={V5+n:here/n for n in NAMES};todo=list(NATIVE)+[MATH+n for n in MATH_NAMES];seen=set();edges=[]
 def resolve(name,source,level=0):
  parts=name.split('.') if name else []
  roots=[repo,repo/'tools',repo/source.parent,repo/'orchestration/adapter',repo/MATH,repo/MATH/'host']
  if level:roots=[repo/source.parent.joinpath(*(['..']*(level-1)))]
  found=[]
  for root in roots:
   stem=root.joinpath(*parts)
   for p in (stem.with_suffix('.py'),stem/'__init__.py'):
    if p.is_file() and p.resolve().is_relative_to(repo):
     found.append(p.resolve().relative_to(repo).as_posix());break
   if found:break
  return found
 while todo:
  rel=todo.pop()
  if rel in seen:continue
  seen.add(rel);p=repo/rel;paths[rel]=p
  tree=ast.parse(p.read_bytes(),filename=rel)
  for node in ast.walk(tree):
   if isinstance(node,ast.Import):imports=[(a.name,0) for a in node.names]
   elif isinstance(node,ast.ImportFrom):imports=[(node.module or '',node.level)] + [((node.module+'.' if node.module else '')+a.name,node.level) for a in node.names if a.name!='*']
   else:continue
   for name,level in imports:
    for target in resolve(name,Path(rel),level):
     edges.append({'source':rel,'import':name,'target':target});todo.append(target)
     parts=Path(target).parts
     for i in range(1,len(parts)):
      init=Path(*parts[:i])/'__init__.py'
      if name.startswith('orchestration.') and (repo/init).is_file():todo.append(init.as_posix())
 for rel in DATA:paths[rel]=repo/rel
 # This assertion independently compares reconstructed native inventory with the
 # externally frozen design, rather than trusting captures' self-reported list.
 import json
 frozen=json.loads((repo/'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/native-closure.json').read_bytes())
 if set(paths)!=set(frozen['future_expected_capture_keyset']):raise ValueError('reconstructed source closure differs: '+repr(sorted(set(paths)^set(frozen['future_expected_capture_keyset']))))
 return paths,edges

def verify_capture(capture,repo,here):
 paths,_=reconstruct(repo,here)
 if set(capture)!=set(paths):raise ValueError('exact source capture key set differs')
 for rel,p in paths.items():
  row=capture[rel];raw=base64.b64decode(row['base64'],validate=True)
  if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256'] or raw!=p.read_bytes():raise ValueError('source capture/publication bytes differ: '+rel)
 return paths

def install(repo,here):
 paths,_=reconstruct(repo,here);allowed={p.resolve() for p in paths.values()};root=Path(repo).resolve();local=Path(here).resolve()
 def hook(event,args):
  if event!='exec':return
  filename=args[0].co_filename
  if not filename or filename.startswith('<'):return
  p=Path(filename).resolve()
  if (p.is_relative_to(root) or p.is_relative_to(local)) and p.suffix=='.py':
   EVENTS.append(str(p))
   if p not in allowed:raise ValueError('undeclared actual repository import: '+str(p))
 sys.addaudithook(hook)
 return {'allowed_keys':sorted(paths),'events':EVENTS}

"""One frozen bounded local proof-computation attempt; no timings or solver cost claims."""
import copy,hashlib,json,os,platform,resource,signal,subprocess,sys
from pathlib import Path
from closure import produce
from replay import replay, read_json
p=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(60,60));signal.alarm(90)
out=Path(sys.argv[1]);out.mkdir(exist_ok=False)
def write(name,x):
    with (out/name).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
write('start.json',{'command':sys.argv,'python':sys.version,'host':platform.node(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip(),'protocol_sha256':hashlib.sha256((p/'protocol.json').read_bytes()).hexdigest(),'source_sha256':{f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in ['closure.py','replay.py','run.py']},'limits':{'cpu_seconds':60,'wall_seconds':90,'address_space_bytes':512*1024**2,'attempts':1,'concurrency':1,'new_cloud_jobs':0,'new_compute_dollars':0},'dataset_admission':False})
a=produce(1);assert a==produce(1);assert replay(a)['lfd_upper']==2
b=produce(2);assert replay(b)['lfd_upper']==2
bad=copy.deepcopy(a);bad['events'][0]['polynomial']=[]
try:replay(bad)
except AssertionError:pass
else:raise RuntimeError('corrupt DAG accepted')
bad=copy.deepcopy(a);bad['events']=bad['events'][:1];bad['rank']=1
try:replay(bad)
except AssertionError:pass
else:raise RuntimeError('incomplete space accepted')
write('controls.json',{'determinism':'pass','known_r1_upper2':'pass','known_r2_upper2':'pass','corrupt_DAG_rejected':True,'incomplete_space_rejected':True})
results=[]
for r in range(1,13):
    cert=produce(r);write('r%d-certificate.json'%r,cert)
    result=replay(read_json(out/('r%d-certificate.json'%r)));write('r%d-result.json'%r,result);results.append(result)
write('summary.json',{'results':results,'completed':len(results),'scope':'exact finite coefficient systems; no general-r or runtime conclusion'})
write('manifest.json',{f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(out.iterdir()) if f.is_file()})
print(json.dumps([{'r':v['r'],'rank':v['rank'],'lfd_lower':v['lfd_lower'],'lfd_upper':v['lfd_upper']} for v in results]))

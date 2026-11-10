"""Single preregistered r6 degree-three computation with complete replay."""
import copy,hashlib,json,platform,resource,signal,subprocess,sys
from pathlib import Path
from closure import produce
from replay import replay,read_json
p=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(60,60));signal.alarm(90)
out=Path(sys.argv[1]);out.mkdir(exist_ok=False)
def write(name,x):
    with (out/name).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
write('start.json',{'command':sys.argv,'python':sys.version,'host':platform.node(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip(),'protocol_sha256_raw':hashlib.sha256((p/'protocol.json').read_bytes()).hexdigest(),'source_sha256':{f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in ['closure.py','replay.py','run.py']},'limits':{'cpu_seconds':60,'wall_seconds':90,'address_space_bytes':512*1024**2,'attempts':1,'concurrency':1,'new_cloud_jobs':0,'new_compute_dollars':0}})
a=produce(1,3);assert a==produce(1,3);assert replay(a)['lfd_upper']==3
old=read_json(p.parent/'no-wrap-w2/attempt-1/r6-certificate.json');old['degree_cap']=2;old['schema']='semaev.bounded-derivation/v1';old_result=replay(old);assert old_result['rank']==71 and old_result['lfd_lower']==3
bad=copy.deepcopy(a);bad['events'][0]['polynomial']=[]
try:replay(bad)
except AssertionError:pass
else:raise RuntimeError('corrupted DAG accepted')
bad=copy.deepcopy(a);bad['events']=bad['events'][:1];bad['rank']=1
try:replay(bad)
except AssertionError:pass
else:raise RuntimeError('incomplete space accepted')
write('controls.json',{'determinism':'pass','r1_cap3_affine_ideal':'pass','existing_r6_cap2_replay':old_result,'corrupt_DAG_rejected':True,'incomplete_space_rejected':True})
cert=produce(6,3);write('r6-certificate.json',cert)
result=replay(read_json(out/'r6-certificate.json'));write('r6-result.json',result)
write('summary.json',{'completed':1,'results':[result],'scope':'one finite r6 cap3 coefficient system; no asymptotic inference'})
write('manifest.json',{f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(out.iterdir()) if f.is_file()})
print(json.dumps(result))

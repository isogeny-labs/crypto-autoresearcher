"""Independent parent/OS launch observations, separately pinned by caller.

Self seals cannot authenticate past processes. The caller must retain this
record outside child custody and pin its digest in a native/root launch or
immutable archive. Replacing that external trust anchor is outside this check.
"""
from pathlib import Path
import datetime,hashlib,json,math,os,time

def os_fact(pid):
 raw=(Path('/proc')/str(pid)/'stat').read_bytes();tail=raw[raw.rfind(b')')+2:].split();argv=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0');argv=[x.decode() for x in argv if x]
 return {'pid':pid,'ppid':int(tail[1]),'start_ticks':int(tail[19]),'state':tail[0].decode(),'argv':argv,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
def capture(proc,argv,input_path,source_map):
 fact=os_fact(proc.pid)
 if fact['ppid']!=os.getpid():raise ValueError('observer parent differs')
 return {'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observer_pid':os.getpid(),'os':fact,'popen_argv':argv,'input_path':str(Path(input_path).resolve()),'input_sha256':hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),'source_sha256':source_map}
def verify(pr,record):
 start=datetime.datetime.fromisoformat(pr['started_at']);observed=datetime.datetime.fromisoformat(record['observed_at']);finish=datetime.datetime.fromisoformat(pr['finished_at'])
 if not start<=observed<=finish:raise ValueError('trusted launch observation differs: start/finish interval')
 pairs={'pid':record['os']['pid'],'parent_pid':record['os']['ppid'],'start_ticks':record['os']['start_ticks'],'argv':record['popen_argv']}
 for k,v in pairs.items():
  if pr.get(k)!=v:raise ValueError('trusted launch observation differs: '+k)
 if pr['input']!={'path':record['input_path'],'sha256':record['input_sha256']} or {k:v['sha256'] for k,v in pr['source_before']['files'].items()}!=record['source_sha256']:raise ValueError('trusted launch input/source differs')
 return True

# Finalized local supervisor custody. The root-custody file is the explicit
# held-fixed trust boundary; it does not authenticate arbitrary replacement of
# that boundary and does not claim hostile-same-UID isolation.
def _d():
 import driver
 return driver
def native_binding(repo,out,plan_path,trial_id,config_path,driver_pid,live=True):
 d=_d();out=Path(out);launch=d.read(out/'launch.json');env=d.read(out/'environment.json');plan=d.read(plan_path);cfg=d.read(config_path)
 trial=next(t for t in plan['trials'] if t['id']==trial_id)
 d.need(d.sha_file(plan_path)==launch['plan_sha256'],'custody native plan hash')
 d.need(trial['run_id']==launch['run_id'] and launch['trial_id']==trial_id,'custody native run/trial')
 d.need([a.replace('{run_dir}',str(out)) for a in trial['argv']]==launch['argv'] and [a.replace('{run_dir}',str(out)) for a in trial['check_argv']]==launch['check_argv'],'custody frozen native argv')
 d.need((out/'command.txt').read_text().strip()==json.dumps(launch['argv']),'custody native command')
 binding=trial['parameters']['config'];d.need(Path(binding['path']).resolve()==Path(config_path).resolve() and binding['sha256']==d.sha_file(config_path),'custody config binding')
 actual=d.source_map(d.snapshot(repo,repo));d.need(actual==cfg['source_sha256']==env['source_sha256'],'custody exact native/config/source')

 if cfg['fixture_only'] is False:
  publication=cfg['source_publication_commit']
  for rel,h in actual.items():d.need(d.sha(d.git(repo,'show',publication+':'+rel))==h,'custody actual source publication: '+rel)
 action=launch['argv'][3];d.need((cfg['fixture_only'] is True and action=='native-fixture') or (cfg['fixture_only'] is False and action=='production'),'custody fixture/production separation')
 d.need(cfg['protocol']['sha256']==d.sha_file(cfg['protocol']['path']),'custody protocol bytes')
 native=os_fact(launch['supervisor_pid']);native.pop('state',None);driver=os_fact(driver_pid) if live else None
 if live:
  d.need(driver['ppid']==native['pid'] and driver['boot_id']==native['boot_id'] and driver['argv']==launch['argv'],'custody live driver/native ancestry/argv')
 return {'native':native,'driver':driver,'driver_pid':driver_pid,'launch':launch,'launch_sha256':d.sha_file(out/'launch.json'),'environment_sha256':d.sha_file(out/'environment.json'),'plan_path':str(Path(plan_path).resolve()),'plan_sha256':d.sha_file(plan_path),'trial_id':trial_id,'run_id':trial['run_id'],'config_path':str(Path(config_path).resolve()),'config_sha256':d.sha_file(config_path),'source_sha256':actual,'source_publication_commit':None if cfg['fixture_only'] else cfg['source_publication_commit'],'fixture_only':cfg['fixture_only'],'context_commit':env['commit'],'experiment_id':plan['experiment_id'],'task_id':plan['task_id'],'approved_by':plan['approved_by'],'interpreter_sha256':d.sha_file(Path(__import__('sys').executable).resolve())}
def _deadline(timeout):
 d=_d();d.need(type(timeout) in (int,float) and math.isfinite(timeout) and timeout>0,'observer IPC positive finite timeout')
 deadline=time.monotonic()+timeout;d.need(math.isfinite(deadline),'observer IPC finite deadline');return deadline
def _remaining(sock,deadline):
 remaining=deadline-time.monotonic()
 if remaining<=0:raise TimeoutError('observer IPC absolute deadline')
 sock.settimeout(remaining)
def _frame_send(sock,obj,deadline):
 d=_d();payload=d.canonical(obj);d.need(len(payload)<=1<<20,'observer IPC framing')
 _remaining(sock,deadline);sock.sendall(payload);_remaining(sock,deadline)
def _send(sock,obj,timeout=5):
 _frame_send(sock,obj,_deadline(timeout))
def _message(sock,obj=None,timeout=5):
 d=_d();deadline=_deadline(timeout)
 if obj is not None:_frame_send(sock,obj,deadline)
 data=bytearray()
 while not data.endswith(b'\n'):
  _remaining(sock,deadline);b=sock.recv(1);d.need(b,'observer IPC closed');data+=b;d.need(len(data)<=1<<20,'observer IPC framing')
 value=d.loads(data);_remaining(sock,deadline);return value
def _quiet_timeout(cfg):
 d=_d();d.need(type(cfg) is dict and type(cfg.get('limits',{})) is dict,'observer frozen limits mapping')
 limits=dict(d.DEFAULT_LIMITS);limits.update(cfg.get('limits',{}));d.limits_check(limits)
 timeout=limits['seconds']+limits['terminate_grace_seconds']+5
 d.need(math.isfinite(timeout) and timeout>0,'observer finite quiet budget');return timeout
class Service:
 def __init__(self,repo,out,plan_path,trial_id,config_path,fault=None):
  import socket,subprocess,sys
  d=_d();self.out=Path(out);self.repo=repo;self.records={};self.finished=False;self.driver_fault=_d().read(config_path).get('driver_fault');self.directory=self.out/'root-custody';self.directory.mkdir()
  self.sock,other=socket.socketpair();self.stdout=(self.directory/'stdout.log').open('xb');self.stderr=(self.directory/'stderr.log').open('xb')
  args=['--serve','--repo-root',str(repo),'--out',str(out),'--plan',str(plan_path),'--trial',trial_id,'--config',str(config_path),'--fd',str(other.fileno()),'--driver-fd',str(self.sock.fileno())]
  if fault:args+=['--fixture-fault',fault]
  argv=d.lifecycle.wrapper_argv(Path(__file__).resolve(),args,2<<30,16<<20)
  self.proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=self.stdout,stderr=self.stderr,pass_fds=(other.fileno(),),close_fds=True,start_new_session=True);other.close()
  d.write(self.directory/'launch.json',{'argv':argv,'pid':self.proc.pid,'parent_pid':os.getpid(),'started_at':d.now()})
  try:
   reply=_message(self.sock);d.need(reply.get('ready') is True,'observer did not become ready')
  except BaseException:
   self.abort();raise
 def observe(self,arm,proc,argv,input_path,ready_path):
  d=_d();reply=_message(self.sock,{'op':'observe','arm':arm,'pid':proc.pid,'argv':argv,'input':str(Path(input_path).resolve()),'ready':str(ready_path)})
  d.need(reply.get('ok') is True,'observer refused launch: '+str(reply));self.records[arm]=reply['record'];return reply['record']
 def closed(self,arm,process_path):
  d=_d();reply=_message(self.sock,{'op':'closed','arm':arm,'process_path':str(process_path)});d.need(reply.get('ok') is True,'observer refused closure')
 def finish(self):
  d=_d();reply=_message(self.sock,{'op':'finish'});d.need(reply.get('finalized') is True,'observer finalization failed');rc=self.proc.wait(timeout=5);d.need(rc==0,'observer nonzero finalization');self.finished=True
  self.sock.close();self.stdout.close();self.stderr.close();d.write(self.directory/'wait.json',{'pid':self.proc.pid,'wait_returned':True,'returncode':rc,'finished_at':d.now()})
 def abort(self):
  import signal,subprocess
  d=_d()
  if self.proc.poll() is None:
   try:os.killpg(self.proc.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   try:self.proc.wait(timeout=.2)
   except subprocess.TimeoutExpired:os.killpg(self.proc.pid,signal.SIGKILL);self.proc.wait()
  self.sock.close();self.stdout.close();self.stderr.close()
  if not (self.directory/'wait.json').exists():d.write(self.directory/'wait.json',{'pid':self.proc.pid,'wait_returned':True,'returncode':self.proc.returncode,'aborted':True,'finished_at':d.now()})
def serve(a):
 import socket,sys,time
 d=_d();d.source_closure.install(a.repo_root,d.HERE);out=Path(a.out);cfg=d.read(a.config);quiet_timeout=_quiet_timeout(cfg);driver_pid=os.getppid();binding=native_binding(a.repo_root,out,a.plan,a.trial,a.config,driver_pid)
 own=os_fact(os.getpid());control_links={os.readlink('/proc/self/fd/'+str(a.fd)),os.readlink('/proc/'+str(driver_pid)+'/fd/'+str(a.driver_fd))}
 sock=socket.socket(fileno=a.fd);observed={};closed={};expected={'candidate','baseline'}|({'generator'} if not cfg['fixture_only'] or cfg.get('fixed_generator') else set())
 d.write(out/'root-custody/start.json',{'binding':binding,'observer':own,'control_socket_links':sorted(control_links),'started_at':d.now()})
 if a.fixture_fault:
  d.need(cfg['fixture_only'],'observer fault only fixedtoy')
  if a.fixture_fault=='start':raise RuntimeError('disclosed observer start failure')
  if a.fixture_fault=='timeout':time.sleep(8)
 _send(sock,{'ready':True})
 while True:
  req=_message(sock,timeout=quiet_timeout);op=req['op']
  if op=='observe':
   if a.fixture_fault=='death':os._exit(7)
   arm=req['arm'];d.need(arm in expected and arm not in observed,'custody duplicate/unknown arm');pid=req['pid'];ready=Path(req['ready']);deadline=time.monotonic()+3
   while not ready.exists() and time.monotonic()<deadline:time.sleep(.005)
   r=d.read(ready);fact=os_fact(pid);d.need(r['pid']==pid and fact['ppid']==driver_pid and fact['state']!='Z','custody worker ready/parent')
   d.need(fact['argv']==req['argv'],'custody actual worker argv');argv=fact['argv'];target='cohort_adapter.py' if arm=='generator' else arm+'.py'
   d.need(argv[2]==str(d.HERE/'lifecycle.py') and '--release-fd' in argv and '--ready-file' in argv and argv[argv.index('--target')+1]==str(d.HERE/target),'custody wrapper/target argv')
   d.need(argv[argv.index('--repo-root')+1]==str(a.repo_root) and argv[argv.index('--input')+1]==req['input'],'custody worker input argv')
   actual=d.source_map(d.snapshot(a.repo_root,a.repo_root));d.need(actual==binding['source_sha256'],'custody launch source changed');x=d.input_check(d.read(req['input']));d.need(x['fixture_only']==cfg['fixture_only'],'custody public fixture state')
   links=[]
   for f in Path('/proc',str(pid),'fd').iterdir():
    try:links.append(os.readlink(f))
    except FileNotFoundError:pass
   d.need(not control_links.intersection(links),'solver inherited observer IPC')
   rec={'arm':arm,'observed_at':d.now(),'observer_pid':os.getpid(),'os':fact,'executable':os.readlink('/proc/'+str(pid)+'/exe'),'popen_argv':fact['argv'],'input_path':req['input'],'input_sha256':d.sha_file(req['input']),'source_sha256':actual,'barrier_ready':r,'service_IPC_absent_from_worker':True}
   observed[arm]=rec
   with (out/'root-custody/observations.jsonl').open('ab') as f:f.write(d.canonical(rec));f.flush();os.fsync(f.fileno())
   _send(sock,{'ok':True,'record':rec})
  elif op=='closed':
   arm=req['arm'];d.need(arm in observed and arm not in closed,'custody closure membership');pr=d.read(req['process_path']);verify(pr,observed[arm]);d.need(not Path('/proc',str(pr['pid'])).exists(),'custody child remains');d.need(pr['termination_ack']=={'wait_returned':True,'returncode':pr['returncode']},'custody driver wait acknowledgment')
   closed[arm]={'process_path':req['process_path'],'process_sha256':d.sha_file(req['process_path']),'driver_reported_wait':pr['termination_ack'],'observer_post_wait_proc_absent':True,'scope':'Actual wait is by direct driver parent; observer absence is not adopted waitpid.'};_send(sock,{'ok':True})
  elif op=='finish':
   if a.fixture_fault=='finalize':raise RuntimeError('disclosed observer finalization failure')
   d.need(set(observed)==set(closed)==expected,'custody missing/extra arms');d.need(d.source_map(d.snapshot(a.repo_root,a.repo_root))==binding['source_sha256'],'custody final source change')
   body={'schema':'controlled-followup-v6.root-custody/v1','state':'finalized','binding':binding,'observer':own,'observations':observed,'closures':closed,'expected_arms':sorted(expected),'finished_at':d.now(),'trust':'Trusted source-pinned root observer FILE held fixed against child reseals; no arbitrary root-boundary replacement authentication or sameUID sandbox.'}
   d.write(out/'root-custody.json',body)
   with (out/'root-custody.json').open('rb') as f:os.fsync(f.fileno())
   d.write(out/'root-custody/seal.json',{'state':'finalized','observer_pid':os.getpid(),'sha256':d.sha_file(out/'root-custody.json'),'bytes':(out/'root-custody.json').stat().st_size});_send(sock,{'finalized':True});sock.close();return
  else:raise ValueError('observer IPC operation')
def load_custody(path,repo,out):
 d=_d();out=Path(out);d.need(Path(path).resolve()==(out/'root-custody.json').resolve(),'fixed native custody path');c=d.read(path);seal=d.read(out/'root-custody/seal.json');wait=d.read(out/'root-custody/wait.json');d.need(c['state']==seal['state']=='finalized' and seal['sha256']==d.sha_file(path) and seal['bytes']==Path(path).stat().st_size,'custody finalization/seal')
 d.need(wait.get('aborted') is not True and wait['wait_returned'] is True and wait['returncode']==0 and wait['pid']==seal['observer_pid']==c['observer']['pid'],'custody observer actual wait')
 b=c['binding'];current=native_binding(repo,out,b['plan_path'],b['trial_id'],b['config_path'],b['driver_pid'],live=False)
 for k in current:
  if k!='driver':d.need(current[k]==b[k],'custody native binding differs: '+k)
 d.need(c['observer']['ppid']==b['driver']['pid'] and b['driver']['ppid']==b['native']['pid'] and c['observer']['boot_id']==b['native']['boot_id'],'custody recorded ancestry')
 cfg=d.read(b['config_path']);expected={'candidate','baseline'}|({'generator'} if not cfg['fixture_only'] or cfg.get('fixed_generator') else set());d.need(set(c['observations'])==set(c['closures'])==set(c['expected_arms'])==expected,'custody launch/closure membership');d.need(len({r['os']['pid'] for r in c['observations'].values()})==len(expected),'custody cloned PID')
 for arm,r in c['observations'].items():
  d.need(r['arm']==arm and r['observer_pid']==c['observer']['pid'] and r['service_IPC_absent_from_worker'] is True and r['source_sha256']==b['source_sha256'],'custody observation source/identity')
  closure=c['closures'][arm]
  d.need(type(closure) is dict and type(closure.get('process_path')) is str,'custody finalized closure structure: '+arm)
  pr=d.read(closure['process_path'])
  d.need(type(closure.get('process_sha256')) is str and d.sha_file(closure['process_path'])==closure['process_sha256'],'custody finalized process SHA mismatch: '+arm)
  recorded=closure.get('driver_reported_wait');actual=pr.get('termination_ack')
  d.need(type(recorded) is dict and set(recorded)=={'wait_returned','returncode'} and recorded['wait_returned'] is True and type(recorded['returncode']) is int,'custody finalized wait structure: '+arm)
  d.need(type(pr.get('returncode')) is int and type(actual) is dict and set(actual)=={'wait_returned','returncode'} and actual['wait_returned'] is True and type(actual['returncode']) is int,'custody current wait structure: '+arm)
  d.need(pr['returncode']==actual['returncode']==recorded['returncode'],'custody finalized wait mismatch: '+arm)
  d.need(closure.get('observer_post_wait_proc_absent') is True,'custody finalized absence acknowledgment: '+arm)
  verify(pr,r)
 return c
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--serve',action='store_true');p.add_argument('--repo-root',required=True);p.add_argument('--out',required=True);p.add_argument('--plan',required=True);p.add_argument('--trial',required=True);p.add_argument('--config',required=True);p.add_argument('--fd',type=int,required=True);p.add_argument('--driver-fd',type=int,required=True);p.add_argument('--fixture-fault');a=p.parse_args();serve(a)

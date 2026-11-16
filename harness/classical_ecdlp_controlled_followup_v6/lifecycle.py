"""Linux fresh interpreter wrapper; no threaded preexec_fn.

Primary docs: frozen lifecycle-references.json PR_SET_PDEATHSIG,
PR_SET_CHILD_SUBREAPER, Python Popen. Install after fork in this fresh
single-threaded interpreter, then recheck expected parent (already-dead race).
PDEATHSIG is cleared by fork/privileged exec/credential changes, preserved by
ordinary exec. Every direct nested process MUST enter this wrapper. It is
not a general hostile descendant sandbox and permits no privileged exec.
"""
import argparse,ctypes,json,os,resource,select,signal,sys,time
from pathlib import Path

def prctl(option,value):
 if sys.platform!='linux':raise RuntimeError('Linux lifecycle required')
 libc=ctypes.CDLL(None,use_errno=True)
 if libc.prctl(option,value,0,0,0)!=0:raise OSError(ctypes.get_errno(),'prctl')
def arm_parent_death(expected_parent):
 prctl(1,signal.SIGKILL)
 if os.getppid()!=expected_parent:raise SystemExit(125)
def subreaper():prctl(36,1)
def wrapper_argv(target,args,memory,file_bytes,parent=None):
 return [sys.executable,'-B',str(Path(__file__).resolve()),'exec','--parent',str(parent or os.getpid()),'--memory',str(memory),'--file-bytes',str(file_bytes),'--target',str(target),'--',*map(str,args)]
def main():
 if sys.argv[1] not in ('exec','probe'):raise ValueError('wrapper action')
 p=argparse.ArgumentParser();p.add_argument('--fixture-startup-delay',type=float,default=0);p.add_argument('--parent',type=int);p.add_argument('--memory',type=int);p.add_argument('--file-bytes',type=int);p.add_argument('--release-fd',type=int);p.add_argument('--ready-file');p.add_argument('--target');p.add_argument('args',nargs=argparse.REMAINDER);a=p.parse_args(sys.argv[2:])
 if a.fixture_startup_delay:
  if sys.argv[1]!='probe' or not 0<a.fixture_startup_delay<=2 or '--fixture-fault' not in a.args:raise ValueError('fixed startup race probe only')
  time.sleep(a.fixture_startup_delay)
 arm_parent_death(a.parent)
 resource.setrlimit(resource.RLIMIT_AS,(a.memory,a.memory));resource.setrlimit(resource.RLIMIT_FSIZE,(a.file_bytes,a.file_bytes))
 if a.release_fd is not None:
  with Path(a.ready_file).open('x') as f:json.dump({'pid':os.getpid(),'parent_pid':os.getppid(),'ready_at':time.time()},f);f.flush();os.fsync(f.fileno())
  if not select.select([a.release_fd],[],[],5)[0] or os.read(a.release_fd,1)!=b'R':raise SystemExit(124)
  os.close(a.release_fd)
 args=a.args[1:] if a.args[:1]==['--'] else a.args
 os.execv(sys.executable,[sys.executable,'-B',a.target,*args])
if __name__=='__main__':main()

"""Enforce the exact bounded infrastructure continuation before normal supervision."""
import hashlib,json,math,os,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]


def main():
    argv=sys.argv[1:]
    def argument(name):return argv[argv.index(name)+1]
    release_path=Path(argument('--release')).resolve();release=json.loads(release_path.read_text());b=release['infrastructure_continuation']
    if (b['additional_attempts']!=1 or b['automatic_retries']!=0 or b['new_paid_capacity'] or
        b['memory_bytes']!=2147483648 or release['memory_bytes']!=b['memory_bytes'] or
        release['absolute_deadline']!=b['original_deadline'] or release['watchdog_seconds']!=b['remaining_cpu_seconds'] or
        release['max_attempts']!=1 or b['total_attempts_including_failed_admission']!=2):raise ValueError('bounded continuation contract')
    prior=ROOT/b['prior_attempt'];old=json.loads((prior/'execution.json').read_text())
    charged=sum(old[k] for k in ('cpu_user_seconds','cpu_sys_seconds','supervisor_cpu_user_seconds','supervisor_cpu_sys_seconds'))
    if (prior/'raw').exists() or old['returncode']!=1 or old['release_sha256']!=b['prior_release_sha256'] or charged!=b['prior_cpu_seconds'] or b['remaining_cpu_seconds']!=21600-math.ceil(charged):raise ValueError('prior charges/outcome differ')
    if datetime.now(timezone.utc)>=datetime.fromisoformat(b['original_deadline']):raise ValueError('original deadline exhausted')
    if not (ROOT/'.resume'/('a16-attempt-'+b['prior_release_sha256']+'.json')).is_file():raise ValueError('prior consumed marker required')
    expected={'core.packedGitWindowSize':'32m','core.packedGitLimit':'128m'}
    if b['git_config']!=expected:raise ValueError('exact Git window contract')
    env=os.environ.copy();count=int(env.get('GIT_CONFIG_COUNT','0'))
    for index,(key,value) in enumerate(expected.items(),count):env['GIT_CONFIG_KEY_'+str(index)]=key;env['GIT_CONFIG_VALUE_'+str(index)]=value
    env['GIT_CONFIG_COUNT']=str(count+len(expected))
    # Preserve inherited identity/config entries. Only read back these public memory settings.
    for key,value in expected.items():
        if subprocess.check_output(['git','config','--get',key],cwd=ROOT,env=env,text=True).strip()!=value:raise ValueError('Git memory configuration not effective')
    if subprocess.check_output(['git','show','HEAD:'+str(release_path.relative_to(ROOT))],cwd=ROOT,env=env)!=release_path.read_bytes():raise ValueError('publish continuation release unchanged')
    interpreter=str(Path(sys.executable).resolve())
    if hashlib.sha256(Path(interpreter).read_bytes()).hexdigest()!=release['interpreter_sha256']:raise ValueError('interpreter differs')
    os.execve(sys.executable,[sys.executable,'-B',str(HERE/'supervise16.py'),*argv],env)


if __name__=='__main__':main()

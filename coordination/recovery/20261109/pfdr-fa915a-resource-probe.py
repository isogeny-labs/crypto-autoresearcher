from pathlib import Path
import subprocess, json, re, datetime
unit='pfdr-resource-probe-fa915a-20261109.scope'
keys=['MemoryMax','CPUQuotaPerSecUSec','RuntimeMaxUSec','TimeoutStopUSec','KillSignal','KillMode','ControlGroup']
raw=subprocess.check_output(['systemctl','--user','show',unit,*['--property='+k for k in keys]],text=True)
props=dict(line.split('=',1) for line in raw.splitlines() if '=' in line)
cg=Path('/sys/fs/cgroup')/props['ControlGroup'].lstrip('/')
memory=(cg/'memory.max').read_text().strip()
cpu=(cg/'cpu.max').read_text().strip()
def seconds(value):
    pattern=r'([0-9.]+)(us|ms|min|s|h|d|w)'
    assert not re.sub(pattern,'',value).strip(),value
    units={'us':1e-6,'ms':.001,'s':1,'min':60,'h':3600,'d':86400,'w':604800}
    return sum(float(n)*units[u] for n,u in re.findall(pattern,value))
quota,period=map(int,cpu.split())
checks={'memory_max':int(memory)==4294967296,'cpu_max':quota==4*period,
        'runtime':seconds(props['RuntimeMaxUSec'])==107570,
        'stop_grace':seconds(props['TimeoutStopUSec'])==30,
        'kill_signal':props['KillSignal']=='2','kill_mode':props['KillMode']=='control-group'}
print(json.dumps({'kind':'non-scientific resource admission probe','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'unit':unit,'properties':props,'memory.max':memory,'cpu.max':cpu,'checks':checks,'passed':all(checks.values()),'scientific_trials':0},indent=2))
raise SystemExit(0 if all(checks.values()) else 1)

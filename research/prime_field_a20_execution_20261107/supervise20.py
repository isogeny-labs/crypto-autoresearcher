"""Own and supervise the admitted independent target-effort CLI; never bypass its gate."""
import argparse
from datetime import datetime, timezone
import fcntl
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
from time import monotonic
import math
from deps20 import core  # bootstrap pinned dependencies before NumPy snapshot
import runtime_numpy

from custody20 import HERE, ROOT, NATIVE, INPUTS, PARAMETERS, bindings, digest, git, write_once


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('protocol', 'release', 'out'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--owner', required=True)
    args = p.parse_args()
    # Bound Git mappings without replacing inherited authentication/config entries.
    count=int(os.environ.get('GIT_CONFIG_COUNT','0'))
    for offset,(key,value) in enumerate((('core.packedGitWindowSize','32m'),('core.packedGitLimit','128m'))):
        os.environ['GIT_CONFIG_KEY_'+str(count+offset)]=key
        os.environ['GIT_CONFIG_VALUE_'+str(count+offset)]=value
    os.environ['GIT_CONFIG_COUNT']=str(count+2)
    parent_start=resource.getrusage(resource.RUSAGE_SELF)
    release = json.loads(args.release.read_text())
    if release.get('owner') != args.owner or release.get('parameters') != PARAMETERS:
        raise ValueError('owner/parameters differ from explicit root release')
    if release.get('execution_authorized') is not True:
        raise ValueError('root execution release is absent')
    if args.out.exists():
        raise ValueError('fresh output directory required')
    protected_before=bindings(release['source_commit'])
    for package, version in release['package_versions'].items():
        if importlib.metadata.version(package) != version:
            raise ValueError('package version differs from release: '+package)
    if runtime_numpy.snapshot()!=release['numpy_runtime']:raise ValueError('NumPy build differs from release')
    if release.get('max_attempts')!=1 or release.get('memory_bytes')!=2147483648:
        raise ValueError('one attempt and fixed two-GiB limit required')
    timeout=min(release['watchdog_seconds'],math.floor((datetime.fromisoformat(release['absolute_deadline'])-datetime.now(timezone.utc)).total_seconds()))
    if timeout<=0:raise ValueError('prospective deadline exhausted')
    # Observe provenance before creating our run directory. These are exact
    # tracked diffs and status, not an execution signature or model attestation.
    provenance=dict(observed_git_head=git('rev-parse','HEAD'),status=git('status','--porcelain'),
        tracked_diff=git('diff','--binary','HEAD'),staged_diff=git('diff','--cached','--binary'),
        source_sha256=protected_before[0],input_sha256=protected_before[1])
    lock_path = ROOT/'.resume/a20-target-effort-owner.lock'
    lock_path.parent.mkdir(exist_ok=True)
    with lock_path.open('a+') as lease:
        fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        marker=ROOT/'.resume'/('a20-attempt-'+digest(args.release)+'.json')
        write_once(marker,dict(release_sha256=digest(args.release),owner=args.owner,started_at=now(),output=str(args.out)))
        args.out.mkdir(parents=True)
        started, start = now(), monotonic()
        ownership = dict(owner=args.owner, supervisor_pid=os.getpid(), started_at=started,
                         protocol=str(args.protocol), protocol_sha256=release['protocol_sha256'],
                         release_sha256=digest(args.release), output=str(args.out.resolve()))
        lease.seek(0); lease.truncate(); lease.write(json.dumps(ownership)+'\n'); lease.flush()
        write_once(args.out/'ownership.json', ownership)
        write_once(args.out/'pre-run-provenance.json',provenance)
        cpu = Path('/proc/cpuinfo').read_text() if Path('/proc/cpuinfo').exists() else ''
        mem = Path('/proc/meminfo').read_text() if Path('/proc/meminfo').exists() else ''
        cpu_model = next((line.split(':', 1)[1].strip() for line in cpu.splitlines() if line.startswith('model name')), None)
        memory_bytes = next((int(line.split()[1])*1024 for line in mem.splitlines() if line.startswith('MemTotal:')), None)
        host = dict(cpu_model=cpu_model, logical_cpus=os.cpu_count(), memory_bytes=memory_bytes,
                    kernel=platform.release(), hypervisor=None, isolation_tier_max=None,
                    python=sys.version, executable_sha256=digest(Path(sys.executable).resolve()),
                    packages=release['package_versions'], numpy_runtime=release['numpy_runtime'], observed_git_head=provenance['observed_git_head'],
                    git_dirty=bool(provenance['status']), source_commit=release['source_commit'])
        write_once(args.out/'host.json', host)
        argv = [sys.executable, '-B', str(NATIVE/'driver20.py'), '--inputs', str(INPUTS),
                '--protocol', str(args.protocol.resolve()), '--release', str(args.release.resolve()),
                '--out', str((args.out/'raw').resolve())]
        env = os.environ.copy()
        env.update(PYTHONPATH=str(ROOT/'src')+':'+str(ROOT), OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        timeout=min(release['watchdog_seconds'],math.floor((datetime.fromisoformat(release['absolute_deadline'])-datetime.now(timezone.utc)).total_seconds()))
        if timeout<=0:raise ValueError('prospective deadline exhausted')
        def constrain():
            resource.setrlimit(resource.RLIMIT_AS, (release['memory_bytes'], release['memory_bytes']))
            resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        timed_out, returncode, exception = False, None, None
        with (args.out/'stdout.txt').open('x') as stdout, (args.out/'stderr.txt').open('x') as stderr:
            child = None
            try:
                child = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                         start_new_session=True, preexec_fn=constrain)
                write_once(args.out/'child.json', dict(supervisor_pid=os.getpid(), child_pid=child.pid,
                                                      child_process_group=child.pid, argv=argv, started_at=now()))
                returncode = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                # No further scientific work after the original absolute deadline.
                os.killpg(child.pid, signal.SIGKILL)
                returncode = child.wait()
            except BaseException as error:
                exception = dict(type=type(error).__name__, reason=str(error))
                if child is not None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
        unchanged = True
        try:
            protected_after=bindings(release['source_commit'])
            if protected_after!=protected_before:raise ValueError('protected source/input hashes changed')
            if runtime_numpy.snapshot()!=release['numpy_runtime']:raise ValueError('NumPy build changed during attempt')
        except Exception as error:
            unchanged = False
            exception = dict(type=type(error).__name__, reason=str(error))
        write_once(args.out/'post-run-provenance.json',dict(observed_git_head=git('rev-parse','HEAD'),
            status=git('status','--porcelain'),tracked_diff=git('diff','--binary','HEAD'),
            staged_diff=git('diff','--cached','--binary'),protected_closure_unchanged=unchanged))
        usage = resource.getrusage(resource.RUSAGE_CHILDREN);parent_usage=resource.getrusage(resource.RUSAGE_SELF)
        write_once(args.out/'execution.json', dict(schema='a20-supervised-execution/v1', owner=args.owner,
            argv=argv, source_commit=release['source_commit'], source_unchanged_after=unchanged,
            protocol=str(args.protocol.resolve()), protocol_sha256=release['protocol_sha256'],
            release_sha256=digest(args.release), observed_git_head=host['observed_git_head'],
            started_at=started, finished_at=now(), diagnostic_wall_seconds=monotonic()-start,
            cpu_user_seconds=usage.ru_utime, cpu_sys_seconds=usage.ru_stime, supervisor_cpu_user_seconds=parent_usage.ru_utime-parent_start.ru_utime,supervisor_cpu_sys_seconds=parent_usage.ru_stime-parent_start.ru_stime,
            max_rss_bytes=usage.ru_maxrss*1024, wall_valid=False,
            returncode=returncode, timeout=timed_out, exception=exception,
            absolute_deadline=release['absolute_deadline'],effective_watchdog_seconds=timeout,model_verified=False, model_identity=None, scientific_promotion=False))
        print(json.dumps(dict(output=str(args.out), returncode=returncode, timeout=timed_out)))
        return 0 if returncode == 0 and unchanged and not timed_out else 1


if __name__ == '__main__':
    sys.exit(main())

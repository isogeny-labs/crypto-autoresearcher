"""Fail-closed external-supervisor/cgroup-v2 gate for a FUTURE admission.

No resource setup, privilege escalation, alternate pool, retries or probes.
Requires an existing authorized empty dedicated cgroup and a separately frozen
native admission verifier. That verifier is a mandatory external dependency,
not implemented or asserted to exist by this source-only task.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time
import types

STARTUP_SECONDS = 5
WORKER_SECONDS = 60
CLEANUP_SECONDS = 5
MEMORY_BYTES = 536870912


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def read_json(path, limit=1048576):
    data = Path(path).read_bytes()
    require(len(data) <= limit, 'JSON input size bound')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def reject(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return data, json.loads(data, object_pairs_hook=pairs, parse_constant=reject)


def digest(path, deadline=None):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while True:
            if deadline is not None:
                require(time.monotonic() < deadline, 'custody/hash deadline')
            data = stream.read(65536)
            if not data:
                break
            result.update(data)
    return result.hexdigest()


def write_receipt(path, value):
    with Path(path).open('xb') as stream:
        stream.write((json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(str(Path(path).parent), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def read_controls(group, pid=None, allow_exited=False):
    """Exact live controller values and singleton membership, never hints."""
    require((group / 'cgroup.type').read_text().strip() == 'domain', 'dedicated domain cgroup required')
    quota, period = (group / 'cpu.max').read_text().split()
    require(quota != 'max' and int(quota) == int(period) and int(period) > 0, 'CPU quota must be one CPU')
    require((group / 'memory.max').read_text().strip() == str(MEMORY_BYTES), 'memory.max must be 512 MiB')
    require((group / 'memory.swap.max').read_text().strip() == '0', 'no-swap controller missing or nonzero')
    require((group / 'memory.oom.group').read_text().strip() == '1', 'whole-worker OOM kill required')
    require((group / 'pids.max').read_text().strip() == '1', 'concurrency must be one process/thread')
    members = [int(v) for v in (group / 'cgroup.procs').read_text().split()]
    require(members == ([] if pid is None else [pid]) or
            (allow_exited and pid is not None and members == []), 'exclusive workload membership')
    require(not any(p.is_dir() for p in group.iterdir()), 'nested workload cgroups forbidden')
    return {'cpu.max': quota + ' ' + period, 'memory.max': MEMORY_BYTES,
            'memory.swap.max': 0, 'memory.oom.group': 1, 'pids.max': 1,
            'cgroup.procs': members}


def stats(group):
    return {name: (group / name).read_text() for name in
            ('memory.events', 'memory.peak', 'cpu.stat', 'cgroup.events')}


def record_wait_status(receipt, wait_status, phase):
    """Record only an actual nonzero-PID waitpid observation, before checks."""
    receipt.update(worker_reaped=True, worker_wait_status_available=True,
                   worker_wait_observed_phase=phase, worker_wait_status_raw=wait_status,
                   worker_wifexited=os.WIFEXITED(wait_status),
                   worker_wifsignaled=os.WIFSIGNALED(wait_status),
                   worker_exit_code=os.WEXITSTATUS(wait_status) if os.WIFEXITED(wait_status) else None,
                   worker_signal=os.WTERMSIG(wait_status) if os.WIFSIGNALED(wait_status) else None)
    if os.WIFSIGNALED(wait_status) and hasattr(os, 'WCOREDUMP'):
        receipt['worker_core_dumped'] = os.WCOREDUMP(wait_status)


def child(gate_read, ready_write, protocol, protocol_sha256, admission):
    """Child blocks before loading any harness/candidate/oracle source."""
    try:
        os.setsid()
        os.write(ready_write, b'R')
        os.close(ready_write)
        release = os.read(gate_read, 1)
        os.close(gate_read)
        if release != b'G':
            os._exit(125)
        # Independent cgroup membership readback by child after parent release.
        group = Path(admission['cgroup_path'])
        read_controls(group, os.getpid())
        expected_membership = '0::' + admission['cgroup_relative_path']
        require(expected_membership in Path('/proc/self/cgroup').read_text().splitlines(), 'child cgroup membership')
        os.environ.clear()
        os.environ.update(protocol['environment'])
        os.chdir(protocol['working_directory'])
        sys.dont_write_bytecode = True
        source = Path(protocol['bindings']['runner']['path']).read_bytes()
        require(hashlib.sha256(source).hexdigest() == protocol['bindings']['runner']['sha256'], 'runner source drift')
        module = types.ModuleType('_scalar_runner_frozen')
        module.__file__ = protocol['bindings']['runner']['path']
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        status = module.run(protocol, {'released_pid': os.getpid(), 'execution_authorized': True,
                                      'protocol_sha256': protocol_sha256,
                                      'native_run_id': admission['native_run_id']})
        os._exit(status)
    except BaseException:
        # Parent captures exit code; no exception becomes a semantic result.
        os._exit(126)


def supervise(args):
    start = time.monotonic()
    startup_deadline = start + STARTUP_SECONDS
    receipt = {'schema': 'prime-scalar.supervisor-terminal/v1', 'status': 'incomplete',
               'released': False, 'worker_seconds_limit': WORKER_SECONDS,
               'startup_seconds_limit': STARTUP_SECONDS, 'cleanup_seconds_limit': CLEANUP_SECONDS,
               'candidate_activity_before_release': 0, 'worker_pid': None,
               'worker_reaped': None, 'worker_wait_status_available': False,
               'worker_wait_status_raw': None, 'worker_wifexited': None,
               'worker_wifsignaled': None, 'worker_exit_code': None, 'worker_signal': None}
    output = Path(args.output).resolve()
    # Unique output path is reserved once, before admission; never overwrite.
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    pid, group, wait_status, gate_write = None, None, None, None
    cleanup_deadline = None
    try:
        require(sys.flags.isolated == 1, 'launch requires isolated interpreter (-I)')
        require(os.geteuid() != 0, 'unprivileged external delegation required')
        protocol_bytes, protocol = read_json(args.protocol)
        protocol_sha = hashlib.sha256(protocol_bytes).hexdigest()
        require(protocol_sha == args.protocol_sha256, 'native-frozen protocol digest')
        require(protocol['schema'] == 'prime-scalar.native-runtime-binding/v1' and
                protocol['execution_authorized'] is True, 'draft is not executable')
        require(Path(protocol['output_directory']).resolve() == output, 'output path binding')
        require(protocol['resources'] == {'wall_seconds': 60, 'cpu': 1, 'memory_mib': 512,
                                        'swap': 0, 'concurrency': 1, 'invocations': 1,
                                        'retries': 0, 'cloud': 0}, 'exact worker budget')
        require(protocol['supervisor_budget'] == {'startup_seconds': 5, 'cleanup_seconds': 5,
                                                'total_seconds': 70, 'cpu': 1, 'memory_mib': 512,
                                                'swap': 0}, 'separate supervisor accounting required')
        require(type(protocol['journal_max_bytes']) is int and 0 < protocol['journal_max_bytes'] <= 134217728,
                'finite journal budget <=128 MiB')
        require(protocol['output_layouts']['extraction'] == 'mapping_v1' and
                protocol['output_layouts']['restriction'] in ('tuple_pair_v1', 'mapping_v1'), 'public output-layout binding required')
        require(protocol['environment'] == {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8',
                                          'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
                                          'MKL_NUM_THREADS': '1'}, 'fixed worker environment')
        require(digest(sys.executable, startup_deadline) == protocol['interpreter_sha256'], 'interpreter digest')
        required_bindings = {'candidate', 'candidate_interface', 'case_spec', 'manifest', 'oracle',
                             'manifest_builder', 'checks', 'runner', 'resource_wrapper'}
        require(set(protocol['bindings']) == required_bindings, 'complete exact source/input bindings')
        for binding in protocol['bindings'].values():
            require(Path(binding['path']).is_absolute(), 'absolute frozen path required')
            require(digest(binding['path'], startup_deadline) == binding['sha256'], 'source/input hash drift')
        require(Path(protocol['bindings']['resource_wrapper']['path']).resolve() == Path(__file__).resolve(), 'wrapper identity')
        require(digest(args.native_verifier, startup_deadline) == args.native_verifier_sha256 == protocol['native_verifier_sha256'], 'native verifier identity')
        # This executable is externally trusted by the frozen launch command.
        # It must validate authoritative native records and atomically consume
        # the one-shot admission. A JSON self-assertion alone is insufficient.
        remaining = startup_deadline - time.monotonic()
        require(remaining > 0, 'startup deadline before native verifier')
        verified = subprocess.run([args.native_verifier, '--admit-once', '--protocol', str(Path(args.protocol).resolve()),
                                   '--protocol-sha256', protocol_sha, '--supervisor-pid', str(os.getpid()),
                                   '--output', str(output)], stdin=subprocess.DEVNULL, capture_output=True,
                                  timeout=remaining, check=True, env=protocol['environment'])
        require(len(verified.stdout) <= 65536 and len(verified.stderr) <= 65536, 'native verifier output bound')
        admission = json.loads(verified.stdout)
        require(admission['schema'] == 'prime-scalar.external-admission/v1' and
                admission['execution_authorized'] is True and admission['one_shot_consumed'] is True and
                admission['protocol_sha256'] == protocol_sha, 'authoritative one-shot approval')
        require(admission['supervisor_pid'] == os.getpid() and admission['owner_uid'] == os.geteuid(), 'admission caller ownership')
        require(admission['supervisor_budget_enforced'] is True and admission['supervisor_outside_worker_cgroup'] is True,
                'external supervisor envelope required')
        require(admission['exclusive_cgroup_delegation_verified'] is True and admission['deadline_enforced_externally'] is True,
                'external exclusive ownership/deadline enforcement required')
        require(type(admission['claim_epoch']) is int and admission['claim_epoch'] > 0 and
                bool(admission['claim_owner']) and bool(admission['native_experiment_id']) and bool(admission['native_run_id']),
                'native claim identifiers required')
        require(admission['claim_expires_unix'] >= time.time() + 65, 'claim must cover worker and custody')
        group = Path(admission['cgroup_path']).resolve()
        require(str(group) == '/sys/fs/cgroup' + admission['cgroup_relative_path'] and
                group != Path('/sys/fs/cgroup'), 'canonical non-root cgroup path')
        require(group.stat().st_uid == os.geteuid(), 'delegated cgroup owner')
        require('0::' + admission['cgroup_relative_path'] not in Path('/proc/self/cgroup').read_text().splitlines(), 'supervisor must survive worker kill')
        receipt.update(native_admission=admission, protocol_sha256=protocol_sha,
                       initial_controls=read_controls(group), initial_resources=stats(group))
        gate_read, gate_write = os.pipe()
        ready_read, ready_write = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(gate_write)
            os.close(ready_read)
            child(gate_read, ready_write, protocol, protocol_sha, admission)
        receipt.update(worker_pid=pid, worker_reaped=False)
        os.close(gate_read)
        os.close(ready_write)
        require(time.monotonic() < startup_deadline, 'startup expired before child readiness')
        ready, _, _ = select.select([ready_read], [], [], startup_deadline - time.monotonic())
        require(bool(ready) and os.read(ready_read, 1) == b'R', 'bounded child handshake')
        os.close(ready_read)
        (group / 'cgroup.procs').write_text(str(pid))
        receipt['release_controls'] = read_controls(group, pid)
        require(time.monotonic() < startup_deadline, 'startup expired before release')
        released_at = time.monotonic()
        deadline = released_at + WORKER_SECONDS
        # Native verifier must arm an independent deadline no later than this
        # absolute monotonic time; a prearmed earlier deadline is permissible.
        require(admission['worker_kill_deadline_monotonic'] <= deadline and
                admission['worker_kill_deadline_monotonic'] > released_at, 'external deadline must already be armed')
        os.write(gate_write, b'G')
        os.close(gate_write)
        gate_write = None
        receipt.update(released=True, worker_pid=pid, released_monotonic=released_at,
                       worker_deadline_monotonic=deadline)
        while True:
            finished, status = os.waitpid(pid, os.WNOHANG)
            if finished:
                wait_status = status
                record_wait_status(receipt, status, 'worker_monitor')
                break
            require(time.monotonic() < deadline, 'worker deadline exceeded')
            # No privilege changes or repairs on a changed live control.
            read_controls(group, pid, allow_exited=True)
            time.sleep(min(0.02, max(0, deadline - time.monotonic())))
        receipt['worker_elapsed_seconds'] = time.monotonic() - released_at
        require(time.monotonic() <= deadline, 'worker finalization missed deadline')
        cleanup_deadline = time.monotonic() + CLEANUP_SECONDS
        require(os.WIFEXITED(wait_status), 'worker killed/signalled')
        read_controls(group)
        _, terminal = read_json(output / 'worker-terminal.json')
        receipt['worker_terminal'] = terminal
        require(terminal['protocol_sha256'] == protocol_sha and terminal['native_run_id'] == admission['native_run_id'], 'worker terminal custody')
        rows = output / 'rows.jsonl'
        require(rows.stat().st_size == terminal['rows_bytes'] and
                digest(rows, cleanup_deadline) == terminal['rows_sha256'], 'durable row hash')
        require(time.monotonic() < cleanup_deadline, 'cleanup deadline')
        if terminal['status'] == 'pass':
            require(receipt['worker_exit_code'] == 0 and terminal['candidate_imports'] == 1 and
                    terminal['attempted_entry_calls'] == terminal['completed_entry_calls'] == 23952 and
                    terminal['base_cases_checked'] == 649, 'terminal acceptance completeness')
            receipt['status'] = 'pass'
        else:
            receipt['status'] = 'fail' if terminal['status'] == 'fail' else 'incomplete'
    except BaseException as error:
        receipt.update(status='incomplete', supervisor_failure={'type': type(error).__name__, 'message': str(error)})
    finally:
        if gate_write is not None:
            os.close(gate_write)
        if cleanup_deadline is None:
            cleanup_deadline = time.monotonic() + CLEANUP_SECONDS
        if pid is not None and wait_status is None:
            receipt['status'] = 'incomplete'
            try:
                if group is not None:
                    (group / 'cgroup.kill').write_text('1')
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except BaseException as error:
                receipt['kill_error'] = type(error).__name__ + ': ' + str(error)
            while time.monotonic() < cleanup_deadline:
                try:
                    finished, status = os.waitpid(pid, os.WNOHANG)
                except ChildProcessError:
                    receipt.update(worker_reaped=None, termination_uncertain=True,
                                   worker_wait_status_unavailable_reason='waitpid reported no waitable child; no status observed')
                    break
                if finished:
                    wait_status = status
                    record_wait_status(receipt, status, 'cleanup')
                    break
                time.sleep(0.01)
            else:
                receipt['termination_uncertain'] = True
        if group is not None:
            try:
                receipt['final_resources'] = stats(group)
                read_controls(group)
            except BaseException as error:
                receipt.update(status='incomplete', final_control_error=str(error))
        receipt['supervisor_elapsed_seconds'] = time.monotonic() - start
        if time.monotonic() >= cleanup_deadline or receipt['supervisor_elapsed_seconds'] >= 70:
            receipt['status'] = 'incomplete'
            receipt['custody_budget_exceeded'] = True
        write_receipt(output / 'supervisor-terminal.json', receipt)
    return 0 if receipt['status'] == 'pass' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', required=True)
    parser.add_argument('--protocol-sha256', required=True)
    parser.add_argument('--native-verifier', required=True)
    parser.add_argument('--native-verifier-sha256', required=True)
    parser.add_argument('--output', required=True)
    return supervise(parser.parse_args())


if __name__ == '__main__':
    raise SystemExit(main())

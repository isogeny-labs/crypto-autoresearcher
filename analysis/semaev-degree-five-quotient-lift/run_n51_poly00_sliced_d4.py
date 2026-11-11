#!/usr/bin/env python3
"""Run one write-once stage of the n51 polynomial00 sliced D4 conversion."""
import argparse
import ast
from decimal import Decimal
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from run_n51_poly00_sliced_w4 import (REPO, budget_readback, committed,
                                      mem_available, parse_utc,
                                      published_revision, sha, utcnow,
                                      write_once)


HERE = Path(__file__).resolve().parent
PLAN = HERE / 'n51-poly00-sliced-d4-plan-001.json'
PROTOCOL = HERE / 'n51-poly00-sliced-d4-protocol-002.json'
OPS = HERE / 'n51-poly00-sliced-d4-admission-001.json'
STAGES = ('project', 'rebase', 'check', 'profile')
MAX_AUTHORIZED_MONTHLY_USD = Decimal('1300')


def limit_name(stage):
    return {'project': 'projection', 'rebase': 'rebase',
            'check': 'checker', 'profile': 'profile'}[stage]


def render(words, values):
    return [values.get(word[1:-1], word) if word.startswith('<') and
            word.endswith('>') else word for word in words]


def static_packet():
    plan = json.loads(PLAN.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    ops = json.loads(OPS.read_text())
    if (plan['schema'] != 'semaev.n51-poly00-sliced-d4-plan/v1' or
            plan['id'] != 'n51-poly00-sliced-d4-001' or
            ops['schema'] != 'semaev.n51-poly00-sliced-d4-admission/v1' or
            ops['plan_sha256'] != sha(PLAN) or
            ops['protocol_file_sha256'] != sha(PROTOCOL) or
            ops['protocol_canonical_sha256'] != plan['protocol_canonical_sha256'] or
            plan['protocol_file_sha256'] != sha(PROTOCOL) or
            protocol['freeze']['status'] != 'frozen' or
            protocol['freeze']['protocol_sha256'] != plan['protocol_canonical_sha256'] or
            ops['runner_sha256'] != sha(__file__)):
        raise RuntimeError('frozen conversion packet mismatch')
    for path in (Path(__file__), PLAN, PROTOCOL, OPS):
        committed(path)
    revision = published_revision(ops['branch'])
    for key, hashkey in (('input_map', 'input_map_sha256'),
                         ('original_checker_stdout', 'original_checker_stdout_sha256'),
                         ('original_plan', 'original_plan_sha256'),
                         ('affine_witness', 'affine_witness_sha256'),
                         ('reused_rebase_binary', 'reused_rebase_binary_sha256'),
                         ('python_binary', 'python_binary_sha256'),
                         ('affine_check_record', 'affine_check_record_sha256')):
        path = Path(plan[key])
        if not path.is_absolute():
            path = REPO / path
        if sha(path) != plan[hashkey]:
            raise RuntimeError('pinned input changed: ' + key)
    if Path(plan['input_map']).stat().st_size != plan['input_map_bytes']:
        raise RuntimeError('input map byte count changed')
    for name, expected in plan['sources'].items():
        if sha(REPO / name) != expected:
            raise RuntimeError('pinned source changed: ' + name)
        committed(REPO / name)
    affine_check = json.loads((REPO / plan['affine_check_record']).read_text())
    if (affine_check['positive_exit_code'] != 0 or
            not affine_check['positive_stdout']['accepted'] or
            affine_check['witness_sha256'] != plan['affine_witness_sha256']):
        raise RuntimeError('affine witness independent check not accepted')
    if (plan['expected_sliced_variables'] != 51 or
            plan['expected_sliced_d4_columns'] != 272052 or
            plan['expected_codimension'] != 45615 or
            plan['expected_projected_bytes'] != 1553961056 or
            plan['limits']['attempts'] != 1 or
            plan['limits']['automatic_retries'] != 0):
        raise RuntimeError('conversion dimensions or attempt limits changed')
    return plan, ops, revision


def stage_paths(root, stage, plan):
    output = {'project': Path(plan['projected_output']),
              'rebase': Path(plan['rebased_output']),
              'check': Path(plan['checker_receipt']),
              'profile': Path(plan['profile_output'])}[stage]
    stdout = output if stage == 'check' else root / (stage + '.stdout.txt')
    return output, stdout, root / (stage + '.stderr.txt'), root / (stage + '.receipt.json')


def prior_stage(plan, stage):
    index = STAGES.index(stage)
    return STAGES[index - 1] if index else None


def verify_prior_publication(plan, stage):
    prior = prior_stage(plan, stage)
    if prior is None:
        return None
    root = Path(plan['output_root'])
    receipt = root / (prior + '.receipt.json')
    if not receipt.exists():
        raise RuntimeError('prior stage receipt missing')
    value = json.loads(receipt.read_text())
    if value['status'] != 'accepted_stage':
        raise RuntimeError('prior stage not accepted')
    if (sha(root / (prior + '.admission.json')) != value['admission_sha256'] or
            sha(root / (prior + '.started.json')) != value['started_sha256']):
        raise RuntimeError('prior stage custody record changed')
    _, prior_stdout, prior_stderr, _ = stage_paths(root, prior, plan)
    if (sha(prior_stdout) != value['stdout_sha256'] or
            sha(prior_stderr) != value['finished']['stderr_sha256']):
        raise RuntimeError('prior stage transcript changed')
    published = REPO / plan['stage_publications'][prior]
    committed(published)
    if published.read_bytes() != receipt.read_bytes():
        raise RuntimeError('prior stage receipt differs from published GitHub bytes')
    if prior in ('project', 'rebase'):
        output = Path(plan['projected_output'] if prior == 'project' else plan['rebased_output'])
        if sha(output) != value['output_sha256']:
            raise RuntimeError('prior stage output digest mismatch')
    if prior == 'check' and sha(Path(plan['checker_receipt'])) != value['stdout_sha256']:
        raise RuntimeError('prior checker stdout digest mismatch')
    return value


def admission(plan, ops, revision, stage):
    if (ops['authorization_status'] != 'authorized' or
            not ops.get('authorization_note') or
            not ops.get('external_jobs_reconciliation')):
        raise RuntimeError('owner authorization or EKS job reconciliation pending')
    monthly = Decimal(str(ops['monthly_cap_usd']))
    other = Decimal(str(ops['other_live_reservations_usd']))
    reserve = Decimal(str(plan['limits']['reserved_usd']))
    if monthly > MAX_AUTHORIZED_MONTHLY_USD or monthly <= 0 or other < 0 or reserve != Decimal('5'):
        raise RuntimeError('unauthorized monthly ceiling or reservation')
    external = ops['external_jobs_reconciliation']
    now = utcnow()
    observed = parse_utc(external['observed_utc'])
    if (external['source'] != 'mcp__isolab_eks' or
            external['active_conflicting_jobs'] or
            not dt.timedelta(0) <= now - observed <= dt.timedelta(minutes=10)):
        raise RuntimeError('EKS job reconciliation stale or conflicting')
    root = Path(plan['output_root'])
    if stage == 'project':
        if root.exists() or not root.parent.is_dir():
            raise RuntimeError('write-once conversion root exists or parent missing')
    elif not root.is_dir():
        raise RuntimeError('conversion root missing')
    prior = verify_prior_publication(plan, stage)
    output, stdout, stderr, receipt = stage_paths(root, stage, plan)
    if receipt.exists() or stdout.exists() or stderr.exists() or output.exists():
        raise RuntimeError('stage already attempted or output exists')
    limits = plan['limits']
    seconds = limits[limit_name(stage) + '_seconds']
    if (now + dt.timedelta(seconds=seconds + 60) > parse_utc(limits['deadline_utc']) or
            limits['total_watchdog_seconds'] != 9000 or
            limits['checkpoint_policy'] != 'none'):
        raise RuntimeError('deadline or total watchdog refuses stage')
    if prior:
        initial = json.loads((root / 'project.started.json').read_text())
        if now + dt.timedelta(seconds=seconds + 60) > (parse_utc(initial['started_utc']) +
                                                         dt.timedelta(seconds=9000)):
            raise RuntimeError('original total watchdog expired')
    memory = mem_available()
    fs = os.statvfs(root.parent)
    disk = fs.f_bavail * fs.f_frsize
    if memory < max(limits[limit_name(stage) + '_as_bytes'], 4294967296) or disk < limits['disk_reserve_bytes']:
        raise RuntimeError('host memory or disk admission refused')
    ps = subprocess.check_output(['ps', '-eo', 'args='], text=True, timeout=15)
    if any(('rebase_selective ' in line or 'slice_trace_certificate.py ' in line or
            'check_trace_slice_certificate.py ' in line)
           for line in ps.splitlines()):
        raise RuntimeError('conflicting local conversion process is live')
    budgets = budget_readback(reserve, other, monthly)
    return {'schema': 'semaev.sliced-d4-stage-admission/v1', 'stage': stage,
            'checked_utc': now.isoformat(), 'source_revision': revision,
            'plan_sha256': sha(PLAN), 'protocol_file_sha256': sha(PROTOCOL),
            'ops_sha256': sha(OPS), 'runner_sha256': sha(__file__),
            'memory_available_bytes': memory, 'disk_available_bytes': disk,
            'budget_readback': budgets, 'prior_receipt_sha256': sha(root / (prior + '.receipt.json')) if prior else None,
            'external_jobs_reconciliation': external}


def command(plan, stage):
    values = {'input_map': plan['input_map'], 'projected_output': plan['projected_output'],
              'rebased_output': plan['rebased_output'], 'profile_output': plan['profile_output'],
              'original_plan': str(REPO / plan['original_plan']),
              'reused_rebase_binary': plan['reused_rebase_binary'],
              'checker_receipt': plan['checker_receipt']}
    if stage != 'project':
        values['projection_sha256'] = sha(Path(plan['projected_output']))
    if stage in ('check', 'profile'):
        values['rebase_sha256'] = sha(Path(plan['rebased_output']))
    if stage == 'profile':
        values['checker_receipt_sha256'] = sha(Path(plan['checker_receipt']))
    key = {'project': 'projection_argv', 'rebase': 'rebase_argv_template',
           'check': 'checker_argv_template', 'profile': 'profile_argv_template'}[stage]
    argv = render(plan[key], values)
    if any(arg.startswith('<') and arg.endswith('>') for arg in argv):
        raise RuntimeError('unresolved command placeholder')
    return ['/usr/bin/prlimit', '--as=' + str(plan['limits'][limit_name(stage) + '_as_bytes']), '--',
            '/usr/bin/timeout', str(plan['limits'][limit_name(stage) + '_seconds'])] + argv


def validate_output(plan, stage, stdout_text):
    data = ast.literal_eval(stdout_text) if stage == 'project' else json.loads(stdout_text)
    if stage == 'project':
        output = Path(plan['projected_output'])
        if (data['variables'] != 51 or data['degree'] != 4 or
                data['columns'] != 272052 or data['codimension'] != 45615 or
                data['certificate_sha256'] != sha(output) or
                output.stat().st_size != plan['expected_projected_bytes']):
            raise ValueError('projection dimensions or digest disagree')
    elif stage == 'rebase':
        output = Path(plan['rebased_output'])
        if (data['variables'] != 51 or data['degree'] != 4 or
                data['columns'] != 272052 or data['codimension'] != 45615 or
                data['triangular'] is not True or data['rebased_sha256'] != sha(output) or
                output.stat().st_size != plan['expected_projected_bytes']):
            raise ValueError('rebase dimensions or digest disagree')
    elif stage == 'check':
        if (data['status'] != 'valid_affine_slice_nonmembership' or
                data['variables'] != 51 or data['degree'] != 4 or
                data['codimension_lower_bound'] != 45615 or
                data['certificate_sha256'] != sha(Path(plan['rebased_output']))):
            raise ValueError('independent checker did not accept named D4 map')
    else:
        output = Path(plan['profile_output'])
        profile = json.loads(output.read_text())
        if (data != profile or data['status'] != 'profiled_checked_slice' or
                data['variables'] != 51 or data['seed_degree'] != 4 or
                data['seed_codimension'] != 45615 or
                data['border_coordinates'] != data['reference_border_coordinates']):
            raise ValueError('profile output disagrees with independent enumeration')
    return data


def run(stage, launch):
    plan, ops, revision = static_packet()
    readback = admission(plan, ops, revision, stage)
    if not launch:
        print(json.dumps(readback, sort_keys=True))
        return
    locks = []
    try:
        for path in ops['locks']:
            stream = Path(path).open('r+')
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                stream.close()
                raise RuntimeError('frontier lock busy: ' + path)
            locks.append(stream)
        readback = admission(plan, ops, revision, stage)
        root = Path(plan['output_root'])
        if stage == 'project':
            root.mkdir(mode=0o700)
        output, stdout_path, stderr_path, receipt_path = stage_paths(root, stage, plan)
        argv = command(plan, stage)
        write_once(root / (stage + '.admission.json'), readback)
        with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
            child = subprocess.Popen(argv, cwd=REPO, stdout=stdout, stderr=stderr,
                                     start_new_session=True)
            try:
                write_once(root / (stage + '.started.json'), {
                    'argv': argv, 'pid': child.pid, 'started_utc': utcnow().isoformat(),
                    'plan_sha256': sha(PLAN)})
            except BaseException:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=10)
                raise
            began = time.monotonic()
            timed_out = False
            try:
                code = child.wait(timeout=plan['limits'][limit_name(stage) + '_seconds'] + 20)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    code = child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    code = child.wait()
        finished = {'returncode': code, 'timed_out': timed_out,
                    'elapsed_seconds': time.monotonic() - began,
                    'stdout_sha256': sha(stdout_path), 'stderr_sha256': sha(stderr_path),
                    'finished_utc': utcnow().isoformat()}
        write_once(root / (stage + '.finished.json'), finished)
        receipt = {'schema': 'semaev.sliced-d4-stage-receipt/v1', 'stage': stage,
                   'status': 'failed', 'finished': finished,
                   'admission_sha256': sha(root / (stage + '.admission.json')),
                   'started_sha256': sha(root / (stage + '.started.json')),
                   'stdout_sha256': finished['stdout_sha256']}
        if code == 0 and not timed_out:
            try:
                result = validate_output(plan, stage, stdout_path.read_text())
                receipt['status'] = 'accepted_stage'
                receipt['result'] = result
                if output != stdout_path:
                    receipt['output_sha256'] = sha(output)
                    receipt['output_bytes'] = output.stat().st_size
            except (OSError, KeyError, TypeError, ValueError) as error:
                receipt['error'] = str(error)
        write_once(receipt_path, receipt)
        print(json.dumps(receipt, sort_keys=True))
    finally:
        for stream in reversed(locks):
            fcntl.flock(stream, fcntl.LOCK_UN)
            stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=STAGES, required=True)
    parser.add_argument('--launch', action='store_true')
    args = parser.parse_args()
    try:
        run(args.stage, args.launch)
    except (OSError, KeyError, TypeError, ValueError, RuntimeError,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        parser.exit(1, 'REFUSED: %s\n' % error)


if __name__ == '__main__':
    main()

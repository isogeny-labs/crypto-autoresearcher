"""UNVALIDATED append-only attempted-work receipts; no execution at import.

Each atomic record is a complete snapshot. A killed writer leaves either a
previous fsynced record or an unlinked temporary file, never a promoted result.
Named metrics are separate units. Exclusive phase deltas are the sum leaves.
"""
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import uuid


def error_record(error, phase):
    return {'phase': phase, 'type': type(error).__name__, 'message': str(error)}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


class AttemptReceipt:
    def __init__(self, directory, bindings, *, attempt_id=None):
        self.directory = Path(directory)
        self.attempt_id = attempt_id or uuid.uuid4().hex
        if not self.attempt_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in self.attempt_id):
            raise ValueError('safe nonempty attempt ID required')
        self.directory = self.directory / self.attempt_id
        # Refuse reuse before solver allocation; errors here have no solver work.
        self.directory.mkdir(parents=True, exist_ok=False)
        self.started = time.monotonic_ns()
        self.stack = []; self.sealed = False; self.sequence = 0
        self.state = {'schema': 'prime-chart-attempt/v1', 'attempt_id': self.attempt_id,
            'bindings': deepcopy(bindings), 'status': 'begun', 'declared_solver_status': None,
            'completion_check_status': 'not_run', 'stop_reason': 'before_solver_initialization',
            'primary_error': None, 'secondary_errors': [], 'phases': [], 'raw_transcript': None,
            'native_statistics': {'availability': 'unknown', 'reason': 'solver not allocated'},
            'cost_coverage': {'complete': False, 'reason': 'attempt in progress',
                              'sum_rule': 'exclusive counters only; never sum inclusive hierarchy'},
            'durability': {'last_durable_sequence': None, 'persistence_errors': []},
            'created_at': datetime.now(timezone.utc).isoformat()}
        self.checkpoint(event='begin')

    def _persist(self):
        self.sequence += 1
        self.state['sequence'] = self.sequence
        self.state['elapsed_ns'] = time.monotonic_ns() - self.started
        self.state['updated_at'] = datetime.now(timezone.utc).isoformat()
        target = self.directory / ('%08d.json' % self.sequence)
        temporary = None
        try:
            payload = deepcopy(self.state)
            # Persist only previously confirmed durability. This event is
            # confirmed in memory/return value after its own directory fsync.
            data = canonical(payload)
            fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=self.directory)
            with os.fdopen(fd, 'wb') as output:
                output.write(data); output.flush(); os.fsync(output.fileno())
            # link is atomic and refuses overwriting an existing immutable event.
            os.link(temporary, target)
            os.unlink(temporary); temporary = None
            directory_fd = os.open(self.directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            self.state['durability']['last_durable_sequence'] = self.sequence
            return {'path': str(target), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
        except BaseException as error:
            failure = error_record(error, 'receipt_persistence')
            self.state['durability']['persistence_errors'].append(failure)
            self.state['secondary_errors'].append(failure)
            # Retain in-memory diagnostics. No durable-success assertion.
            return None
        finally:
            if temporary is not None:
                try:
                    os.unlink(temporary)
                except OSError:
                    pass

    def checkpoint(self, transcript=None, *, event='checkpoint', **fields):
        if self.sealed:
            raise RuntimeError('sealed attempt cannot be changed')
        if transcript is not None:
            self.state['raw_transcript'] = deepcopy(transcript)
            self.state['declared_solver_status'] = transcript.get('status')
            self.state['stop_reason'] = transcript.get('stop_reason')
        self.state.update(deepcopy(fields)); self.state['event'] = event
        return self._persist()

    def secondary(self, error, phase):
        self.state['secondary_errors'].append(error_record(error, phase))

    def failure(self, error, phase):
        record = error_record(error, phase)
        if self.state['primary_error'] is None:
            self.state['primary_error'] = record
        else:
            self.state['secondary_errors'].append(record)
        self.state['status'] = 'interrupted' if isinstance(error, (KeyboardInterrupt, SystemExit)) else 'failed'
        self.state['cost_coverage'] = {'complete': False, 'reason': 'interrupted phase: '+phase,
                                      'sum_rule': 'exclusive counters only'}
        try:
            error.attempt_receipt = self
        except BaseException as attachment:
            self.secondary(attachment, 'attach_failure_receipt')

    @contextmanager
    def phase(self, name, counter_source=None, *, counter_scope=None):
        """Exclusive counters require explicit identical scope IDs when nested.

        Unknown child counters make the parent exclusive arithmetic unknown.
        Distinct nested scope IDs remain separate units and are not subtracted.
        An ambiguous nested source is rejected before its operation starts.
        """
        if self.sealed:
            raise RuntimeError('phase after seal')
        frame = {'name': name, 'start': time.monotonic_ns(), 'children_ns': 0,
                 'children': Counter(), 'counter_source': counter_source, 'scope': counter_scope,
                 'parent': self.stack[-1]['name'] if self.stack else None,
                 'before': None, 'unknown_child': False}
        primary = None; entered = False
        try:
            if counter_source and self.stack and self.stack[-1]['counter_source']:
                if counter_scope is None or self.stack[-1]['scope'] is None:
                    raise ValueError('nested counter sources require explicit scope IDs')
            if counter_source:
                frame['before'] = deepcopy(counter_source())
            self.stack.append(frame); entered = True
            yield
        except BaseException as error:
            primary = error
            self.failure(error, name)
            raise
        finally:
            elapsed = time.monotonic_ns() - frame['start']
            if entered:
                self.stack.pop()
            record = {'name': name, 'parent': frame['parent'], 'counter_scope': counter_scope,
                      'inclusive_elapsed_ns': elapsed, 'exclusive_elapsed_ns': elapsed-frame['children_ns'],
                      'status': 'failed' if primary else 'returned',
                      'counters': {'availability': 'unknown', 'reason': 'no attempted-operation counter source'}}
            try:
                inclusive = None
                if counter_source and frame['before'] is not None:
                    after = counter_source(); before = frame['before']
                    keys = set(before) | set(after)
                    if any(type(after.get(k, 0)) is not int or type(before.get(k, 0)) is not int or
                           after.get(k, 0) < before.get(k, 0) for k in keys):
                        raise ValueError('phase counter reset or noninteger')
                    inclusive = Counter({k: after.get(k, 0)-before.get(k, 0) for k in keys})
                    if frame['unknown_child']:
                        record['counters'] = {'availability': 'unknown', 'inclusive_observed': dict(inclusive),
                            'reason': 'child has unknown counters; exclusive allocation unavailable'}
                    else:
                        exclusive = {k: inclusive[k]-frame['children'][k] for k in set(inclusive) | set(frame['children'])}
                        if any(v < 0 for v in exclusive.values()):
                            raise ValueError('overlapping phase counter accounting')
                        record['counters'] = {'availability': 'available', 'inclusive': dict(inclusive), 'exclusive': exclusive}
                if self.stack:
                    self.stack[-1]['children_ns'] += elapsed
                    if record['counters']['availability'] != 'available':
                        self.stack[-1]['unknown_child'] = True
                    elif inclusive is not None and counter_scope == self.stack[-1]['scope']:
                        self.stack[-1]['children'].update(inclusive)
            except BaseException as secondary:
                self.secondary(secondary, 'phase_finalization:'+name)
                record['counters'] = {'availability': 'unknown', 'reason': 'counter finalization failed'}
                if self.stack:
                    self.stack[-1]['unknown_child'] = True
                if primary is None:
                    self.failure(secondary, 'phase_finalization:'+name)
                    primary = secondary
            self.state['phases'].append(record)
            try:
                self.checkpoint(event='phase_end')
            except BaseException as secondary:
                self.secondary(secondary, 'phase_checkpoint:'+name)
                if primary is None:
                    self.failure(secondary, 'phase_checkpoint:'+name)
                    raise
            # An exception in the body is already propagating. A new finalizer
            # failure must propagate only when the body returned normally.
            if primary is not None and record['status'] == 'returned':
                raise primary

    def seal(self, status, *, completion_check_status='not_run', coverage_complete=False, reason=None):
        if self.sealed:
            raise RuntimeError('attempt already sealed')
        allowed = {'failed', 'interrupted', 'censored', 'invalid_output', 'complete_unverified', 'verified_complete'}
        if status not in allowed:
            raise ValueError('invalid envelope status')
        if self.state['primary_error'] is not None:
            status = self.state['status'] if self.state['status'] in ('failed', 'interrupted') else 'failed'
        if status == 'verified_complete' and (completion_check_status != 'accepted_complete' or
                self.state['declared_solver_status'] != 'complete'):
            raise ValueError('completion requires independent complete checking')
        persistence_failed = bool(self.state['durability']['persistence_errors'])
        unknown_phases = any(p['counters']['availability'] != 'available' for p in self.state['phases'])
        self.state['status'] = status
        self.state['completion_check_status'] = completion_check_status
        self.state['cost_coverage'] = {'complete': bool(coverage_complete and not persistence_failed and not unknown_phases and self.state['primary_error'] is None),
            'reason': reason or 'explicit per-phase attempted-work coverage; unknown phases remain unknown',
            'sum_rule': 'exclusive counters only; different metric units are never summed'}
        receipt = self.checkpoint(event='seal')
        self.sealed = True
        return {'record': receipt, 'state': deepcopy(self.state), 'durable': receipt is not None}

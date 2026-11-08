"""Future gated worker. No CLI and no import-time scientific work.

Only resource_wrapper may call run() after external admission and cgroup gate.
This source has not been imported or executed during authoring.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import types


def frozen_bytes(binding):
    data = Path(binding['path']).read_bytes()
    if hashlib.sha256(data).hexdigest() != binding['sha256']:
        raise RuntimeError('frozen bytes changed: ' + binding['path'])
    return data


def load_module(name, binding):
    """Execute exact hashed bytes once, never accept a cached bytecode file."""
    if name in sys.modules:
        raise RuntimeError('duplicate module load')
    data = frozen_bytes(binding)
    module = types.ModuleType(name)
    module.__file__ = binding['path']
    module.__package__ = ''
    sys.modules[name] = module
    exec(compile(data, binding['path'], 'exec'), module.__dict__)
    return module


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def bad_constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=bad_constant)


class Journal:
    def __init__(self, path, cap):
        self.stream = Path(path).open('xb')
        self.digest = hashlib.sha256()
        self.bytes = 0
        self.cap = cap

    def append(self, record):
        data = (json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
        if self.bytes + len(data) > self.cap:
            raise RuntimeError('journal byte budget exhausted')
        self.stream.write(data)
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.digest.update(data)
        self.bytes += len(data)

    def close(self):
        self.stream.close()


def write_once(path, value):
    with Path(path).open('xb') as stream:
        stream.write((json.dumps(value, sort_keys=True, allow_nan=False) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())


def run(protocol, gate):
    """Gate is inherited from supervisor; standalone/direct invocation refuses."""
    if gate.get('released_pid') != os.getpid() or gate.get('execution_authorized') is not True:
        raise RuntimeError('missing external release')
    output = Path(protocol['output_directory'])
    journal = Journal(output / 'rows.jsonl', protocol['journal_max_bytes'])
    state = {'schema': 'prime-scalar.worker-terminal/v1', 'status': 'incomplete',
             'candidate_imports': 0, 'attempted_entry_calls': 0, 'completed_entry_calls': 0,
             'base_cases_checked': 0, 'protocol_sha256': gate['protocol_sha256'],
             'native_run_id': gate['native_run_id']}
    row, actual, error, expected, before, after = None, None, None, None, None, None
    try:
        bindings = protocol['bindings']
        # Recheck every pinned file before candidate import, after gated release.
        for binding in bindings.values():
            frozen_bytes(binding)
        checks = load_module('_scalar_checks_frozen', bindings['checks'])
        oracle = load_module('_scalar_oracle_frozen', bindings['oracle'])
        manifest = strict_json(frozen_bytes(bindings['manifest']))
        checks.require(manifest['spec_sha256'] == bindings['case_spec']['sha256'], 'manifest/spec binding')
        checks.require(manifest['spec_sha256'] ==
                       '7f68929cedcf12965554d96eefe7b1aeddef82f0f1bb182e6e37113e16d5e9dc', 'locked case specification identity')
        case_spec = strict_json(frozen_bytes(bindings['case_spec']))
        for key, public_path in (
                ('candidate', 'research/prime_sat_scalar_prefix_source_20261107/extractor.py'),
                ('candidate_interface', 'research/prime_sat_scalar_prefix_source_20261107/interface.json')):
            checks.require(bindings[key]['sha256'] == case_spec['source_hashes'][public_path],
                           'published candidate/interface identity')
        checks.manifest_check(manifest)
        interface = strict_json(frozen_bytes(bindings['candidate_interface']))
        counter_names = tuple(interface['counter_semantics'])
        layouts = protocol['output_layouts']
        checks.require(layouts['extraction'] == 'mapping_v1' and
                       layouts['restriction'] in ('mapping_v1', 'tuple_pair_v1'), 'explicit output layouts')
        cases = {case['id']: case for case in manifest['cases']}
        expectations = {}
        for case in manifest['cases']:
            expectations[case['id']] = oracle.expectation(case)
        checks.require(sum(v['full_evaluations'] for v in expectations.values()) ==
                       manifest['counts']['oracle_full_evaluations'], 'exact oracle workload')
        journal.append({'phase': 'preimport', 'manifest_sha256': bindings['manifest']['sha256'],
                        'counts': manifest['counts'], 'output_layouts': layouts})
        state['candidate_imports'] = 1  # Counts attempted imports, including a failed import.
        candidate = load_module('_scalar_candidate_frozen', bindings['candidate'])
        repeated, semantic = {}, {}
        seen_cases = set()
        by_family = {}
        for row in manifest['calls']:
            actual, error, before, after = None, None, None, None
            args = checks.decode(row['arguments'])
            before = checks.snapshot(args)
            expected = None if row['malformed'] else expectations[row['case_id']]
            journal.append({'phase': 'before_call', 'call': row,
                            'expected': 'ValueError exactly' if row['malformed'] else expected})
            actual, error = None, None
            state['attempted_entry_calls'] += 1
            try:
                actual = getattr(candidate, row['api'])(*args)
            except BaseException as caught:
                error = caught
            # Immutability is checked even for an unexpected exception.
            after = checks.snapshot(args)
            checks.require(after == before, 'input mutation', before, after)
            if row['malformed']:
                checks.require(type(error) is ValueError, 'exact malformed rejection', 'ValueError',
                               {'exception': None if error is None else type(error).__name__,
                                'result': checks.snapshot(actual)})
                actual_record = {'exception': 'ValueError', 'message': str(error)}
                normalized = ['ValueError']
            else:
                checks.require(error is None, 'unexpected candidate exception', None,
                               None if error is None else {'type': type(error).__name__, 'message': str(error)})
                actual_record = checks.snapshot(actual)
                normalized = checks.valid_output(row, cases[row['case_id']], expected, actual,
                                                 layouts, counter_names, oracle.evaluate)
            repeat_key = (row['case_id'], row['order'], row['container'], row['api'],
                          json.dumps(row['depth'], sort_keys=True))
            if row['repeat'] == 0:
                checks.require(repeat_key not in repeated, 'duplicate repeat zero')
                repeated[repeat_key] = actual_record
            else:
                checks.require(repeat_key in repeated and repeated[repeat_key] == actual_record,
                               'identical-input repeat equality', repeated.get(repeat_key), actual_record)
            if not row['malformed']:
                semantic_key = (row['case_id'], row['api'], row['depth'])
                if semantic_key in semantic:
                    checks.require(normalized == semantic[semantic_key], 'permutation/container semantics',
                                   semantic[semantic_key], normalized)
                else:
                    semantic[semantic_key] = normalized
                seen_cases.add(row['case_id'])
            # Every realization's full counters retained; never require equal
            # counters across insertion permutations or aggregate them into cost.
            journal.append({'phase': 'completed_call', 'call_id': row['id'], 'case_id': row['case_id'],
                            'family': row['family'], 'actual': actual_record,
                            'semantic': normalized, 'input_unchanged': True})
            state['completed_entry_calls'] += 1
            by_family[row['family']] = by_family.get(row['family'], 0) + 1
        checks.require(state['attempted_entry_calls'] == state['completed_entry_calls'] == 23952 and
                       len(seen_cases) == 649, 'complete acceptance counts')
        state.update(status='pass', base_cases_checked=len(seen_cases), completed_by_family=by_family,
                     claim_scope='exact finite registered software semantics only')
    except BaseException as error:
        try:
            raw_actual = checks.snapshot(actual)
        except BaseException:
            raw_actual = {'unserializable_type': type(actual).__name__}
        state.update(status='fail' if type(error).__name__ == 'Mismatch' else 'incomplete',
                     first_failure={'call': row, 'type': type(error).__name__, 'message': str(error),
                                    'expected': getattr(error, 'expected', None),
                                    'actual': getattr(error, 'actual', None),
                                    'raw_return': raw_actual, 'oracle_expectation': expected,
                                    'input_before': before, 'input_after': after})
        # If journaling itself fails, the separate small terminal record still
        # carries the first failing call; supervisor preserves a killed worker.
        try:
            journal.append({'phase': 'first_failure', **state['first_failure']})
        except BaseException:
            state['failure_row_persisted'] = False
    finally:
        state['rows_sha256'] = journal.digest.hexdigest()
        state['rows_bytes'] = journal.bytes
        journal.close()
        write_once(output / 'worker-terminal.json', state)
    return 0 if state['status'] == 'pass' else 1

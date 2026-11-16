#!/usr/bin/env python3
"""Independent projective equation checker and frozen-prefix post hoc audit.

Imports no solver/candidate arithmetic. Certificate checking is completed and
sealed before either candidate JSONL file is opened. All counts are finite
inventory bookkeeping, not performance measurements.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import time
import traceback


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError('nonfinite JSON number')
    return value


def bad_constant(text):
    raise ValueError('nonfinite JSON constant: ' + text)


def decode(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs_unique,
                      parse_float=finite_float, parse_constant=bad_constant)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_new(path, document):
    raw = (json.dumps(document, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw)
    return {'file': path.name, 'sha256': sha(raw), 'bytes': len(raw)}


def is_prime(n):
    if type(n) is not int or n < 2 or n > 1048576:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


class Projective:
    """Jacobian double/mixed-add, converted once after scalar multiplication."""
    def __init__(self, model, base):
        self.p, self.a, self.b, self.r = (model[k] for k in ('p', 'a', 'b', 'r'))
        if not (is_prime(self.p) and self.p > 3 and is_prime(self.r)):
            raise ValueError('prime domain precondition failed')
        if not all(type(x) is int and 0 <= x < self.p for x in (self.a, self.b)):
            raise ValueError('coefficient canonical range failed')
        if (4 * self.a ** 3 + 27 * self.b ** 2) % self.p == 0:
            raise ValueError('singular curve')
        self.G = self.affine(base, False)
        if self.mul(self.r, self.G) is not None:
            raise ValueError('unreduced rG order equation failed')

    def affine(self, value, allow_identity=True):
        if value is None:
            if allow_identity:
                return None
            raise ValueError('identity not permitted')
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError('invalid point shape')
        x, y = value
        if not all(type(t) is int and 0 <= t < self.p for t in (x, y)):
            raise ValueError('invalid coordinate range/type')
        if (y * y - x * x * x - self.a * x - self.b) % self.p:
            raise ValueError('off-curve point')
        return x, y

    def double(self, P):
        X, Y, Z = P
        p = self.p
        if Z == 0 or Y == 0:
            return 0, 1, 0
        yy, zz = Y * Y % p, Z * Z % p
        s = 4 * X * yy % p
        m = (3 * X * X + self.a * zz * zz) % p
        new_x = (m * m - 2 * s) % p
        return new_x, (m * (s - new_x) - 8 * yy * yy) % p, 2 * Y * Z % p

    def mixed(self, P, Q):
        if Q is None:
            return P
        X, Y, Z = P
        x, y = Q
        p = self.p
        if Z == 0:
            return x, y, 1
        zz = Z * Z % p
        h = (x * zz - X) % p
        delta = (y * zz * Z - Y) % p
        if h == 0:
            return self.double(P) if delta == 0 else (0, 1, 0)
        hh, hhh = h * h % p, h * h * h % p
        v = X * hh % p
        new_x = (delta * delta - hhh - 2 * v) % p
        return new_x, (delta * (v - new_x) - Y * hhh) % p, Z * h % p

    def mul(self, n, point):
        if type(n) is not int or n < 0:
            raise ValueError('scalar must be a nonnegative integer')
        # No n %= r, including when checking rG and rQ.
        result = (0, 1, 0)
        for digit in bin(n)[2:]:
            result = self.double(result)
            if digit == '1':
                result = self.mixed(result, point)
        X, Y, Z = result
        if not Z:
            return None
        zinv = pow(Z, self.p - 2, self.p)
        return X * zinv * zinv % self.p, Y * zinv * zinv * zinv % self.p


def reject(call):
    try:
        call()
    except (ValueError, TypeError):
        return True
    raise ValueError('negative control accepted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--input-manifest', required=True, type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (4 << 30, 4 << 30))
    resource.setrlimit(resource.RLIMIT_CPU, (1800, 1800))
    if hasattr(os, 'sched_getaffinity'):
        os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:2]))
    out = args.out.resolve()
    original_guard = decode((out / 'runtime-guard.json').read_bytes())
    stop = original_guard['monotonic_stop']

    def guard():
        if time.monotonic() >= stop:
            raise TimeoutError('original whole-pipeline watchdog reached')

    manifest_path = args.input_manifest if args.input_manifest.is_absolute() else args.repo_root / args.input_manifest
    inputs = decode(manifest_path.read_bytes())['inputs']
    if len(inputs) != 3:
        raise ValueError('exact three-input binding required')
    public_binding, trace_binding, cell_binding = inputs
    public_raw = Path(public_binding['local_readonly_absolute_path']).read_bytes()
    if len(public_raw) != public_binding['payload_bytes'] or sha(public_raw) != public_binding['payload_sha256']:
        raise ValueError('public payload identity mismatch')
    public = decode(public_raw)
    if public['schema'] != 'controlled-followup-v5.public-input/v1':
        raise ValueError('public schema mismatch')
    groups = public['public']['curves']
    curves, targets, domain_records = {}, {}, []
    for group in groups:
        cid = group['curve_id']
        if cid in curves:
            raise ValueError('duplicate public curve ID')
        curve = Projective(group['model'], group['base'])
        curves[cid] = curve
        for target in group['targets']:
            key = cid, target['target_id']
            if key in targets:
                raise ValueError('duplicate public target ID')
            Q = curve.affine(target['point'], False)
            if curve.mul(curve.r, Q) is not None:
                raise ValueError('unreduced rQ subgroup sanity failed')
            targets[key] = Q
        domain_records.append({'curve_id': cid, **group['model'], 'G': group['base'],
                               'prime_nonsingular_canonical_and_rG_passed': True,
                               'target_ids': [t['target_id'] for t in group['targets']]})
    if len(curves) != 48 or len(targets) != 1536:
        raise ValueError('complete public inventory mismatch')
    del public, public_raw
    guard()
    seal = decode((out / 'certificate-seal.json').read_bytes())
    certificate_payloads = []
    references = {}
    positive_cases = reference_equations = mutation_cases = 0
    for name in ('certificates-A.json', 'certificates-B.json'):
        raw = (out / name).read_bytes()
        if sha(raw) != seal['files'][name]['sha256'] or len(raw) != seal['files'][name]['bytes']:
            raise ValueError('reference seal mismatch')
        certificate_payloads.append(raw)
        doc = decode(raw)
        if doc['public_input_sha256'] != public_binding['payload_sha256']:
            raise ValueError('reference public binding mismatch')
        seen, pass_refs = set(), {}
        for group in doc['curves']:
            cid = group['curve_id']
            if cid in seen or cid not in curves:
                raise ValueError('reference domain join mismatch')
            seen.add(cid)
            curve = curves[cid]
            for tid, x in group['scalars']:
                guard()
                key = cid, tid
                if key not in targets or key in pass_refs or type(x) is not int or not 0 <= x < curve.r:
                    raise ValueError('reference identity/scalar coverage mismatch')
                if curve.mul(x, curve.G) != targets[key]:
                    raise ValueError('reference original equation rejected')
                if curve.mul((x + 1) % curve.r, curve.G) == targets[key]:
                    raise ValueError('reference mutation accepted')
                reject(lambda: canonical_scalar(x + curve.r, curve.r))
                pass_refs[key] = x
                reference_equations += 1
                mutation_cases += 1
        if seen != set(curves) or set(pass_refs) != set(targets):
            raise ValueError('reference inventory incomplete')
        control_ids = set()
        for control in doc['controls']:
            cid = control['curve_id']
            if cid in control_ids or cid not in curves:
                raise ValueError('control domain coverage mismatch')
            control_ids.add(cid)
            curve = curves[cid]
            expected = [0, 1, curve.r - 1, curve.r // 2]
            if [v[0] for v in control['known_scalar_cases']] != expected:
                raise ValueError('control scalar inventory mismatch')
            for planted, Q, solved in control['known_scalar_cases']:
                Q = curve.affine(Q)
                if type(solved) is not int or solved != planted or curve.mul(planted, curve.G) != Q or curve.mul(solved, curve.G) != Q:
                    raise ValueError('independent positive control failed')
                positive_cases += 1
            reject(lambda: curve.affine((0, 0) if curve.b else (0, 1)))
            reject(lambda: curve.affine((curve.p, 0)))
            bad_model = {'p': curve.p, 'a': curve.a, 'b': curve.b, 'r': 2 * curve.r}
            reject(lambda: Projective(bad_model, curve.G))
            if not all(control[k] is True for k in ('offcurve_rejected', 'noncanonical_point_rejected', 'composite_order_rejected')):
                raise ValueError('producer negative-control record disagrees')
        if control_ids != set(curves):
            raise ValueError('missing control domain')
        if references and pass_refs != references:
            raise ValueError('A/A scalar vectors differ')
        references = pass_refs
    if certificate_payloads[0] != certificate_payloads[1]:
        raise ValueError('A/A canonical bytes differ')
    toy = Projective({'p': 17, 'a': 2, 'b': 2, 'r': 19}, [5, 1])
    if toy.mul(2, toy.G) != (6, 3) or toy.mul(3, toy.G) == (6, 3) or toy.mul(2, toy.G) == (6, 14):
        raise ValueError('external known/wrong-target controls failed')
    reject(lambda: toy.affine((0, 0)))
    yzero = Projective({'p': 17, 'a': 1, 'b': 0, 'r': 2}, [0, 0])
    if yzero.mul(2, yzero.G) is not None or yzero.mul(1, yzero.G) != (0, 0):
        raise ValueError('y=0 independent branch control failed')
    reference_proof = {'schema': 'classical.ecdlp.independent-reference-verification/v1',
                       'public_input_sha256': public_binding['payload_sha256'],
                       'checker_source_sha256': sha(Path(__file__).read_bytes()),
                       'domains': domain_records, 'distinct_public_certificates': len(references),
                       'original_equations_checked': reference_equations, 'mutation_rejections': mutation_cases,
                       'known_scalar_positive_checks': positive_cases, 'AA_identical_bytes': True,
                       'all_controls_passed': True, 'all_reference_certificates_verified': True,
                       'candidate_files_opened_before_this_seal': False,
                       'scope': 'Finite reference validity; no performance metrics or candidate recovery rate.'}
    reference_seal = write_new(out / 'reference-verification.json', reference_proof)
    # Only from here are the archived candidate files opened.
    scans, trace_rows = {}, {}

    def scan(binding):
        label = binding['logical_path']
        info = {'records': 0, 'bytes': 0, 'sha256': None, 'malformed': 0, 'tail': 0}
        scans[label] = info
        digest = hashlib.sha256()
        with Path(binding['local_readonly_absolute_path']).open('rb') as stream:
            for line_number, raw in enumerate(stream, 1):
                guard()
                digest.update(raw)
                info['bytes'] += len(raw)
                if not raw.endswith(b'\n'):
                    info['tail'] += 1
                    raise ValueError('unterminated source record: ' + label + ':' + str(line_number))
                try:
                    row = decode(raw)
                except Exception:
                    info['malformed'] += 1
                    raise
                info['records'] += 1
                yield line_number, sha(raw), row
        info['sha256'] = digest.hexdigest()
        if info['sha256'] != binding['payload_sha256'] or info['bytes'] != binding['payload_bytes']:
            raise ValueError('archived candidate payload identity mismatch: ' + label)

    for number, digest, trace in scan(trace_binding):
        if trace['schema'] != 'classical.ecdlp.controlled-followup.trace/v1':
            raise ValueError('trace schema mismatch')
        tid = trace['trace_id']
        if tid in trace_rows:
            raise ValueError('duplicate trace ID')
        trace_rows[tid] = {k: trace[k] for k in ('curve_id', 'target_id', 'base_multiplier', 'target_multiplier', 'target')}
        trace_rows[tid].update(line=number, sha256=digest)
    claimed, cell_ids, distinct, outcomes, field_disagreements = [], set(), set(), {}, []
    word_records = cell_records = mutation_claims = 0

    def audit_scalar(value, context, field, transformed=None):
        nonlocal mutation_claims
        event = {'field': field, 'scalar': value}
        curve = curves[context['curve_id']]
        key = context['curve_id'], context['target_id']
        try:
            canonical_scalar(value, curve.r)
            Q = targets[key]
            original_lhs = curve.mul(value, curve.G)
            event['original_valid'] = original_lhs == Q
            event['reference_scalar_equal'] = value == references[key]
            if event['original_valid']:
                accepted = curve.mul((value + 1) % curve.r, curve.G) == Q
                event['mutation_accepted'] = accepted
                mutation_claims += 1
                if accepted:
                    raise RuntimeError('proves-too-much control failed: candidate witness mutation accepted')
            if transformed is not None:
                k, a, b = transformed
                canonical_scalar(k, curve.r)
                if type(a) is not int or type(b) is not int or not a % curve.r or not b % curve.r:
                    raise ValueError('invalid blinding residues')
                normalized = a * k * pow(b, -1, curve.r) % curve.r
                transformed_lhs = curve.mul(k, curve.mul(a % curve.r, curve.G))
                transformed_rhs = curve.mul(b % curve.r, Q)
                event.update(transformed_scalar=k, derived_normalized_scalar=normalized,
                             normalization_consistent=normalized == value,
                             transformed_valid=transformed_lhs == transformed_rhs)
            valid = event['original_valid'] and event['reference_scalar_equal'] and event.get('normalization_consistent', True) and event.get('transformed_valid', True)
            event['outcome'] = 'valid' if valid else 'invalid'
            if not valid:
                event.update(original_lhs=original_lhs, original_rhs=Q, reference_scalar=references[key])
                if transformed is not None:
                    event.update(transformed_lhs=transformed_lhs, transformed_rhs=transformed_rhs)
            distinct.add((key[0], key[1], value))
        except (ValueError, TypeError) as error:
            event.update(outcome='undefined', reason=str(error))
        outcomes[event['outcome']] = outcomes.get(event['outcome'], 0) + 1
        return event

    for number, digest, cell in scan(cell_binding):
        cell_records += 1
        if cell['schema'] != 'classical.ecdlp.controlled-followup.decoder-cell/v1' or cell['cell_id'] in cell_ids:
            raise ValueError('cell schema/uniqueness mismatch')
        cell_ids.add(cell['cell_id'])
        trace = trace_rows[cell['trace_id']]
        key = trace['curve_id'], trace['target_id']
        if key not in targets or trace['target'] != list(targets[key]):
            raise ValueError('cell/trace/public target join mismatch')
        if not isinstance(cell['words'], list) or not isinstance(cell['recovered_scalars'], list):
            raise ValueError('cell claim-list schema mismatch')
        context = {'cell_id': cell['cell_id'], 'cell_line': number, 'cell_sha256': digest,
                   'trace_id': cell['trace_id'], **trace, 'cell_status': cell['status']}
        events, word_values = [], []
        for index, word in enumerate(cell['words']):
            word_records += 1
            if word['status'] == 'RECOVERED':
                word_values.append(word.get('candidate_scalar'))
                event = audit_scalar(word.get('candidate_scalar'), context, 'word',
                                     (word.get('candidate_scalar_prime'), trace['base_multiplier'], trace['target_multiplier']))
                event['word_index'] = index
                events.append(event)
        if cell['scalar'] is not None:
            events.append(audit_scalar(cell['scalar'], context, 'scalar'))
        for index, value in enumerate(cell['recovered_scalars']):
            event = audit_scalar(value, context, 'recovered_scalars')
            event['array_index'] = index
            events.append(event)
        if events:
            context['events'] = events
            claimed.append(context)
            freeze = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'))
            if {freeze(v) for v in word_values} != {freeze(v) for v in cell['recovered_scalars']} or (cell['scalar'] is not None and freeze(cell['scalar']) not in {freeze(v) for v in word_values}):
                field_disagreements.append({'cell_id': cell['cell_id'], 'word_scalars': word_values,
                                            'scalar': cell['scalar'], 'recovered_scalars': cell['recovered_scalars']})
    audit = {'schema': 'classical.ecdlp.frozen-candidate-reference-audit/v1', 'scans': scans,
             'reference_verification_seal': reference_seal, 'cell_records': cell_records,
             'word_records': word_records, 'claim_outcomes': outcomes, 'claimed_cells': claimed,
             'distinct_curve_target_scalar': [list(v) for v in sorted(distinct)],
             'field_disagreements': field_disagreements, 'dependent_mutation_rejections': mutation_claims,
             'scope': 'All explicit claims in the exact retained R52 prefix, post hoc; dependent fields are not independent samples; no recovery denominator/rate or timing comparison.'}
    audit_seal = write_new(out / 'candidate-audit.json', audit)
    summary = {'schema': 'classical.ecdlp.reference-validation-summary/v1', 'status': 'complete',
               'all_reference_certificates_verified': True, 'distinct_reference_targets': len(references),
               'AA_equal': True, 'all_controls_passed': True, 'candidate_claim_outcomes': outcomes,
               'candidate_distinct_curve_target_scalar': len(distinct),
               'candidate_field_disagreements': len(field_disagreements),
               'input_manifest_sha256': sha(manifest_path.read_bytes()),
               'reference_proof': reference_seal, 'candidate_audit': audit_seal,
               'performance_measurements_admitted': False, 'wall_valid': False}
    write_new(out / 'verification-summary.json', summary)
    print(json.dumps(summary))


def canonical_scalar(value, order):
    if type(value) is not int or not 0 <= value < order:
        raise ValueError('scalar outside canonical integer interval')
    return value


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)

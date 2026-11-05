"""UNVALIDATED generic full-chart bridge; no coordinate 2*s projection shortcut."""
from collections import Counter
from copy import deepcopy
import importlib.util
from pathlib import Path
import re

from .attempt_receipt import AttemptReceipt, error_record
from .transform import ROOT, authenticate_transform, build_transform, composition, digest, require, source_identity, verify_baselines
from .transport import decode_and_check_original
from . import bridge_counted


def _legacy():
    verify_baselines()
    path = ROOT/'research/prime_sat_followup_20261029/encoding.py'
    spec = importlib.util.spec_from_file_location('_transform_coordinate_counter_types', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def convert_range(document):
    """Strict typed conversion; no arbitrary rewriting or coefficient reduction."""
    C = composition().compiler()
    authentication = C.authenticate(document, document['descriptor'], 'range')
    n, p, m = document['n'], document['p'], document['projected_bits']
    require(type(n) is int and n >= 0 and type(p) is int and p > 3 and
            type(m) is int and 0 <= m <= n, 'range ring dimensions')
    counts = Counter(); polys = []
    for polynomial in document['polynomials']:
        require(type(polynomial) is dict, 'canonical polynomial mapping')
        parsed = {}
        for mask, coefficient in polynomial.items():
            counts['monomial_conversions'] += 1
            require(type(mask) is str and re.fullmatch(r'0|[1-9][0-9]*', mask) is not None,
                    'canonical monomial string')
            key = int(mask)
            require(key.bit_length() <= n and type(coefficient) is int and 0 < coefficient < p,
                    'in-ring monomial and nonzero canonical coefficient')
            parsed[key] = coefficient
        polys.append(parsed)
    domain = deepcopy(document['bootstrap_cnf'])
    for clause in domain:
        require(type(clause) is list, 'CNF clause list')
        for literal in clause:
            counts['domain_literal_checks'] += 1
            require(type(literal) is int and 0 < abs(literal) <= n, 'CNF literal range')
    ring = _legacy().CountedRing(n, p)
    return ring, polys, domain, {'document_sha256': digest(document),
                               'authentication': authentication, 'conversion': dict(counts)}


def verify_chart_answer(document, trusted_descriptor, mode, answer, *, attempt=None):
    c = composition()
    def phase(name):
        from contextlib import nullcontext
        return attempt.phase(name) if attempt else nullcontext()
    with phase('verification.transform_authentication'):
        auth = authenticate_transform(document, trusted_descriptor, mode)
        require(auth['status'] == 'applicable', 'nonapplicable transform cannot verify a solve')
        expected = build_transform(trusted_descriptor, mode)
    if mode == 'identity':
        with phase('verification.unchanged_complete_chart'):
            result = c.complete_chart_transcript(expected['original'], trusted_descriptor, answer)
        result = deepcopy(result)
        result['transform_authentication'] = auth
    else:
        rd = expected['range_document']
        with phase('verification.range_completion'):
            completion = c.compiler().complete_transcript(rd, rd['descriptor'], answer, 'range', rd['bootstrap_cnf'])
        decoded = []; failures = []; projections = set()
        if type(answer) is dict and type(answer.get('models')) is list:
            for i, bits in enumerate(answer['models']):
                try:
                    value = decode_and_check_original(document, bits, trusted_descriptor, mode, attempt=attempt)
                    key = tuple(value['projection'])
                    require(key not in projections, 'duplicate reconstructed original coefficient projection')
                    projections.add(key)
                    decoded.append({'model_index': i, 'decoded': value})
                except Exception as error:
                    failures.append({'model_index': i, **error_record(error, 'original_model_verification')})
        checked = completion['checker_result']
        result = {'completion': completion, 'decoded_models': decoded, 'model_failures': failures,
                  'declared_status': answer.get('status') if type(answer) is dict else None,
                  'accepted': bool(checked and checked.get('valid') and not failures),
                  'costs': {'transform_authentication': auth, 'transcript': completion['costs'],
                            'models': [x['decoded']['costs'] for x in decoded]}}
    # The baseline accepts valid partial transcripts; distinguish this explicitly.
    result['verified_complete'] = bool(result['accepted'] and result['declared_status'] == 'complete'
                                       and not result['completion']['gaps'])
    result['projected_original_coefficients'] = [x['decoded']['projection'] for x in result['decoded_models']]
    result['cost_coverage'] = {'complete': False,
        'reason': 'baseline successful-return counts retained; interrupted hidden baseline operations are unknown'}
    return result


def solve_chart(document, trusted_descriptor, mode, limits, strategy, checkpoint, *,
                refuter_mode='baseline', solver_factory=None):
    """checkpoint is a fresh receipt directory or an existing AttemptReceipt.

    No oracle input exists. Explicit native call budgets are not legacy candidate
    budgets. Source-only admission does not authorize invoking this function.
    """
    bindings = {'document_sha256': digest(document), 'descriptor_sha256': digest(trusted_descriptor),
                'operation': mode, 'limits_sha256': digest(limits), 'strategy': strategy,
                'refuter_mode': refuter_mode, 'source_sha256': source_identity(),
                'solver_factory_used': solver_factory is not None}
    attempt = checkpoint if isinstance(checkpoint, AttemptReceipt) else AttemptReceipt(checkpoint, bindings)
    if isinstance(checkpoint, AttemptReceipt):
        require(not attempt.sealed, 'fresh open attempt required')
        attempt.checkpoint(event='chart_bindings', chart_bindings=bindings)
    try:
        with attempt.phase('construction.transform_authentication'):
            auth = authenticate_transform(document, trusted_descriptor, mode)
            require(auth['status'] == 'applicable', 'requested presentation not applicable')
        with attempt.phase('construction.generic_ring'):
            ring, polys, domain, conversion = convert_range(document['range_document'])
        m, n = document['range_document']['projected_bits'], ring.n
        prefix_depths = sorted(set((0, m, n)))
        # The engine owns its counted arithmetic; this parent phase deliberately
        # has no second ring tracker, preventing duplicate charging.
        with attempt.phase('search.native_and_certificates'):
            answer = bridge_counted.solve(ring, polys, domain, m, limits, strategy, prefix_depths,
                refuter_mode=refuter_mode, attempt=attempt, solver_factory=solver_factory)
        attempt.checkpoint(answer, event='search_returned', conversion=conversion)
        verified = verify_chart_answer(document, trusted_descriptor, mode, answer, attempt=attempt)
        if verified['verified_complete']:
            status, checked = 'verified_complete', 'accepted_complete'
        elif not verified['accepted']:
            status, checked = 'invalid_output', 'rejected'
        elif answer['status'] == 'censored':
            status, checked = 'censored', 'accepted_partial'
        else:
            status, checked = 'complete_unverified', 'not_complete'
        attempt.checkpoint(event='verification_returned', verification=verified)
        seal = attempt.seal(status, completion_check_status=checked, coverage_complete=False,
            reason='all returned counts retained; interrupted baseline-only internal counts remain unknown')
        return {'schema': 'prime-chart-solve/v1', 'answer': answer, 'verification': verified,
                'construction': {'authentication': auth, 'conversion': conversion},
                'attempt': seal, 'units': {'sat_calls': 'native solve_limited invocations',
                    'model_checks': 'propagator candidate callbacks', 'accepted_models': 'projected witnesses',
                    'legacy_sat_candidates': 'not used by this engine; retain separately in original comparison'}}
    except BaseException as error:
        try:
            attempt.failure(error, 'chart_solve')
            if not attempt.sealed:
                attempt.seal('failed', coverage_complete=False, reason='exception; partial durable evidence only')
        except BaseException as secondary:
            attempt.secondary(secondary, 'failure_sealing')
        raise

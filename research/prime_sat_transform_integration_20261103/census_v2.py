"""UNVALIDATED versioned census adapter. Only known absent/zero equality changes.

The _verify_semantics body is a scoped textual copy of frozen encoding.verify;
its exact construction, model, projection, limits, certificate, and witness
checks are retained. Raw cost dictionaries are never rewritten.
"""
from collections import Counter
from copy import deepcopy
import json
from .chart_solver import _legacy

METRICS = ('coefficient_additions', 'coefficient_multiplications',
           'evaluation_term_visits', 'restriction_term_visits',
           'membership_transform_subtractions', 'legendre_pow_calls',
           'membership_curve_tests', 'domain_clauses', 'boolean_assignments_visited')
SCHEMA = 'prime-census-costs/v2'


def canonical_costs(raw):
    if type(raw) is not dict or any(type(k) is not str or k not in METRICS for k in raw):
        raise ValueError('closed census metric schema')
    if any(type(v) is not int or v < 0 for v in raw.values()):
        raise ValueError('nonnegative integer census counts; bool is not integer')
    return {key: raw.get(key, 0) for key in METRICS}


def validate_vector(vector):
    if type(vector) is not dict or set(vector) != set(METRICS):
        raise ValueError('canonical vector requires all nine metrics')
    return canonical_costs(vector)


def wire_projections(values):
    if type(values) is not list:
        raise ValueError('projection list required')
    result = []
    for pair in values:
        if type(pair) not in (list, tuple) or len(pair) != 2 or any(type(v) is not int or v < 0 for v in pair):
            raise ValueError('ordered coordinate pair of canonical integers')
        result.append(list(pair))
    return result


def costs_equal(left, right):
    return canonical_costs(left) == canonical_costs(right)


def produce_census(cell, ring, polys, domain):
    result = _legacy().census(cell, ring, polys, domain)
    return {'schema': SCHEMA, 'raw': deepcopy(result), 'canonical_costs': canonical_costs(result['costs'])}


def verify_census_record(record, recomputed):
    if type(record) is not dict or set(record) != {'schema', 'raw', 'canonical_costs'} or record['schema'] != SCHEMA:
        raise ValueError('census v2 envelope')
    if validate_vector(record['canonical_costs']) != canonical_costs(record['raw']['costs']):
        raise AssertionError('stored canonical vector mismatch')
    if (record['raw']['complete_models'] != recomputed['complete_models'] or
            wire_projections(record['raw']['projected_models']) != wire_projections(recomputed['projected_models']) or
            not costs_equal(record['raw']['costs'], recomputed['costs'])):
        raise AssertionError('fresh census mismatch')
    return {'producer_raw': deepcopy(record['raw']['costs']), 'recomputed_raw': deepcopy(recomputed['costs']),
            'canonical_vector': canonical_costs(recomputed['costs'])}


# Delegation keeps each original routine unchanged and avoids module-global patching.
def controls():
    return _legacy().controls()
def reference(cell):
    return _legacy().reference(cell)
def build(cell, arm):
    return _legacy().build(cell, arm)
def census(cell, ring, polys, domain):
    return _legacy().census(cell, ring, polys, domain)
def verify_search(cell, ring, polys, domain, answer, expected):
    return _legacy().verify_search(cell, ring, polys, domain, answer, expected)
def reconstruct(cell, projections):
    return _legacy().reconstruct(cell, projections)


def _verify_arm(row, arm, cfg, refs, counts, raw_pairs):
    ring,polys,domain = build(row["input"],arm["arm"])
    if dict(ring.counts) != arm["construction_cost"]:
        raise AssertionError("construction counters mismatch")
    got = census(row["input"],ring,polys,domain)
    if (got["complete_models"] != arm["census"]["complete_models"]
            or got["projected_models"] != refs
            or got["projected_models"] != [tuple(x) for x in arm["census"]["projected_models"]]
            or not costs_equal(got["costs"], arm["census"]["costs"])):
        raise AssertionError("full assignment census mismatch")
    raw_pairs.append({"cell": row["input"], "arm": arm["arm"],
                      "recomputed_raw": deepcopy(got["costs"]),
                      "producer_raw": deepcopy(arm["census"]["costs"]),
                      "recomputed_vector": canonical_costs(got["costs"]),
                      "producer_vector": canonical_costs(arm["census"]["costs"])})
    events = arm["search"]["costs"]["search_events"]
    if (events.get("sat_candidates",0) > cfg["limits"]["sat_candidates"]
            or events.get("pc_calls",0) > cfg["limits"]["pc_calls"]
            or events.get("sat_candidates",0) < len(arm["search"]["models"])+len(arm["search"]["learned"])):
        raise AssertionError("search budget/counter contradiction")
    verify_search(row["input"],ring,polys,domain,arm["search"],refs)
    witnesses,cost = reconstruct(row["input"],refs)
    s = row["input"]["s"]
    expected_full = sorted(w["x"][0] + (w["x"][1] << s) +
        ((w["lambda"] << (2*s)) if arm["arm"] in ("quadratic","quadratic_aa") else 0)
        for w in witnesses)
    if got["complete_models"] != expected_full:
        raise AssertionError("independent lifted full-model set mismatch")
    if json.dumps(witnesses,sort_keys=True) != json.dumps(arm["witnesses"],sort_keys=True) or cost != arm["reconstruction_cost"]:
        raise AssertionError("witness reconstruction mismatch")
    counts[arm["search"]["status"]] += 1
    counts["certificates"] += len(arm["search"]["learned"])


def _verify_semantics(payload, raw_pairs):
    cfg = payload["config"]
    expected = []
    for curve in cfg["curves"]:
        for s in cfg["digits"]:
            for x in range(curve["p"]):
                ys = [y for y in range(1,curve["p"]) if (y*y-x**3-curve["a"]*x-curve["b"])%curve["p"]==0]
                if ys:
                    expected.append({**curve,"s":s,"target":[x,min(ys)]})
    if [row["input"] for row in payload["cells"]] != expected or not all(payload["controls"].values()) or payload["controls"] != controls():
        raise AssertionError("fixture or control coverage mismatch")
    counts = Counter()
    for row in payload["cells"]:
        refs,_ = reference(row["input"])
        if refs != [tuple(x) for x in row["reference_models"]] or [x["arm"] for x in row["arms"]] != cfg["arms"]:
            raise AssertionError("reference or arm mismatch")
        for arm in row["arms"]:
            _verify_arm(row, arm, cfg, refs, counts, raw_pairs)
    return {"valid":True,"cells":len(expected),"counts":dict(counts)}


def verify(payload):
    raw_pairs = []
    result = _verify_semantics(payload, raw_pairs)
    return {**result, 'census_schema': SCHEMA, 'raw_cost_comparisons': raw_pairs}


def run(config, checkpoint=None):
    """Prospective producer; untouched original run/search, never historical repair."""
    payload = _legacy().run(config, checkpoint)
    vectors = [{'cell': deepcopy(row['input']), 'arm': arm['arm'],
                'raw': deepcopy(arm['census']['costs']),
                'canonical': canonical_costs(arm['census']['costs'])}
               for row in payload['cells'] for arm in row['arms']]
    return {'schema': 'prime-coordinate-census-adapter/v2', 'payload': payload, 'cost_vectors': vectors}


def verify_envelope(envelope):
    if type(envelope) is not dict or set(envelope) != {'schema', 'payload', 'cost_vectors'} or envelope['schema'] != 'prime-coordinate-census-adapter/v2':
        raise ValueError('coordinate v2 envelope')
    expected = [{'cell': deepcopy(row['input']), 'arm': arm['arm'],
                 'raw': deepcopy(arm['census']['costs']),
                 'canonical': canonical_costs(arm['census']['costs'])}
                for row in envelope['payload']['cells'] for arm in row['arms']]
    for item in envelope['cost_vectors']:
        canonical_costs(item['raw'])
        validate_vector(item['canonical'])
    if envelope['cost_vectors'] != expected:
        raise AssertionError('raw/canonical census envelope mismatch')
    return verify(envelope['payload'])

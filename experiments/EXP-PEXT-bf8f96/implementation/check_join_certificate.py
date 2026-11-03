"""Independent complete fixed-control join and adjacent-shard replay.

Software fixtures only. Production shard custody must additionally bind published
cohort/plan/file hashes; these control records are not production receipts.
"""
import argparse
import json
from pathlib import Path
from check_quotient_certificate import Curve, integer, keys, load, require
from check_compact_class_inputs import BasisField
from check_curve_class_certificate import family_models, orbit
from check_structure_certificate import normalize, cocycle, transform

FIXTURES = {'f3-classes': (3, 1), 'f5-classes': (5, 1), 'f27-char3': (3, 3)}


def verify_shards(records, fixture):
    require(fixture in FIXTURES, 'unknown software fixture')
    require(type(records) is list and 1 <= len(records) <= 10000, 'shard list')
    for record in records:
        keys(record, 'schema fixture order field classes structures total start end rows')
        require(record['schema'] == 'pext.join-software-certificate/v1', 'join schema')
        require(record['fixture'] == fixture, 'fixture binding')
        require(record['order'] == 'log-point-coset-transversal/v1', 'ordering version')
    first = records[0]
    f = BasisField(first['field'])
    require((f.p, f.n) == FIXTURES[fixture], 'fixture field')
    structures = (f.size**3-f.size)//(f.p**3-f.p)
    require(integer(first['structures'], 1, 10000) == structures, 'structure index')
    if f.n == 1:
        remaining = set(family_models(f)); models = []
        while remaining:
            model = min(remaining, key=lambda m: (0 if f.p == 3 and m[0] else 1, *(f.log[v] for v in m)))
            models.append(list(model)); remaining -= orbit(f, model)
    else:
        models = [[1, 0, 1]]
    require(type(first['classes']) is list and len(first['classes']) == len(models), 'model coverage')
    plan, offset = [], 0
    for entry, model in zip(first['classes'], models):
        keys(entry, 'model targets offset')
        curve = Curve(f, model)
        require(type(entry['model']) is list and entry['model'] == model, 'class identity')
        for value in entry['model']: f.element(value)
        require(integer(entry['offset'], 0, 10000) == offset, 'class offset')
        doubles = {curve.add(p, p) for p in curve.points}
        uncovered = set(curve.points); targets = []
        while uncovered:
            target = min(uncovered, key=curve.key)
            members = {curve.add(target, d) for d in doubles}
            require(members <= uncovered, 'coset overlap')
            targets.append(target); uncovered -= members
        require(type(entry['targets']) is list, 'target list')
        require([curve.read_point(t) for t in entry['targets']] == targets, 'complete canonical T classes')
        for target in targets:
            plan.append((model, curve, target, offset)); offset += structures
    total = offset
    require(integer(first['total'], 1, 10000) == total, 'total cardinality')
    header = {k: first[k] for k in ('schema', 'fixture', 'order', 'field', 'classes', 'structures', 'total')}
    seen_ranges = set()
    for record in records:
        require(json.dumps({k: record[k] for k in header}, sort_keys=True) == json.dumps(header, sort_keys=True), 'shard plan mismatch')
        start = integer(record['start'], 0, total); end = integer(record['end'], start, total)
        require((start, end) not in seen_ranges, 'duplicate shard range'); seen_ranges.add((start, end))
        require(type(record['rows']) is list and len(record['rows']) == end-start, 'shard row count')
    next_ordinal = 0; matrices = {}; identities = set()
    for record in sorted(records, key=lambda r: (r['start'], r['end'])):
        require(record['start'] == next_ordinal, 'shard gap or overlap')
        for row in record['rows']:
            keys(row, 'ordinal class_index coset_index structure_index model target matrix cocycle original_form transformed_form conjugates')
            require(integer(row['ordinal'], 0, total-1) == next_ordinal, 'row order')
            block, structure = divmod(next_ordinal, structures)
            model, curve, target, _ = plan[block]
            class_index = integer(row['class_index'], 0, len(models)-1)
            require(models[class_index] == model and row['model'] == model, 'row class identity')
            for value in row['model']: f.element(value)
            entry = first['classes'][class_index]
            coset = (next_ordinal-entry['offset'])//structures
            require(integer(row['coset_index'], 0, len(entry['targets'])-1) == coset, 'row coset identity')
            require(curve.read_point(row['target']) == target, 'row target identity')
            require(integer(row['structure_index'], 0, structures-1) == structure, 'row structure identity')
            matrix = normalize(f, row['matrix']); require(matrix == row['matrix'], 'normalized matrix')
            actual = cocycle(f, matrix)
            require(normalize(f, row['cocycle']) == row['cocycle'] == actual, 'cocycle identity')
            if structure not in matrices:
                require(tuple(actual) not in identities, 'repeated projective coset')
                matrices[structure] = matrix; identities.add(tuple(actual))
            else:
                require(matrices[structure] == matrix, 'inconsistent structure order')
            original = curve.quotient_form(target); moved = transform(f, original, matrix)
            for key, wanted in [('original_form', original), ('transformed_form', moved)]:
                require(type(row[key]) is list and len(row[key]) == 5, 'form shape')
                for value in row[key]: f.element(value)
                require(row[key] == wanted, 'literal scalar/form mismatch')
            require(type(row['conjugates']) is list and len(row['conjugates']) == f.n, 'conjugate count')
            current = moved
            for given in row['conjugates']:
                require(type(given) is list and len(given) == 5, 'conjugate shape')
                for value in given: f.element(value)
                require(given == current, 'coefficient conjugation mismatch')
                current = [f.power(v, f.p) for v in current]
            require(current == moved, 'conjugate closure')
            next_ordinal += 1
    require(next_ordinal == total and len(matrices) == structures and len(identities) == structures, 'incomplete join')
    return {'valid': True, 'fixture': fixture, 'classes': len(models), 'T_classes': len(plan),
            'structures': structures, 'rows': total, 'shards': len(records)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificates', nargs='+', type=Path)
    parser.add_argument('--fixture', required=True, choices=FIXTURES)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_shards([load(p) for p in args.certificates], args.fixture), sort_keys=True))
    except (ValueError, TypeError, KeyError, IndexError, OSError) as error:
        parser.exit(2, 'INVALID: '+str(error)+'\n')

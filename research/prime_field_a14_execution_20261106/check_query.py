"""Plain complete geometric triple/pair/miss oracle in native coordinates."""
from collections import defaultdict
from itertools import combinations, product
from shared import check_source


class Oracle:
    def __init__(self, fixture, geometry):
        self.fixture, self.geometry = fixture, geometry
        p, a = fixture['p'], fixture['a']
        points = [tuple(v) for v in geometry['points']]
        signed = {(j, s): q if s == 1 else (q[0], -q[1] % p)
                  for j, q in enumerate(points) for s in (1, -1)}
        self.signed, self.add = signed, lambda a0, b0: check_source.old.add(p, 0, a, a0, b0)
        self.pairs, self.table = [], defaultdict(list)
        for (j, k), signs in product(combinations(range(len(points)), 2), product((1, -1), repeat=2)):
            q = self.add(signed[j, signs[0]], signed[k, signs[1]])
            self.table[q].append(len(self.pairs))
            self.pairs.append(dict(indices=[j, k], native_indices=[geometry['native_indices'][j], geometry['native_indices'][k]],
                signs=list(signs), point=None if q is None else list(q)))
        self.triples = defaultdict(list)
        for indices, signs in product(combinations(range(len(points)), 3), product((1, -1), repeat=3)):
            Q = None
            for j, sign in zip(indices, signs, strict=True):
                Q = self.add(Q, signed[j, sign])
            self.triples[Q].append((tuple(geometry['native_indices'][j] for j in indices), signs))

    def check(self, record, pairs):
        f, geom = self.fixture, self.geometry
        if pairs != self.pairs:
            raise ValueError('geometric pair completeness/native mapping')
        Q = None if record['point'] is None else tuple(record['point'])
        descriptions = []
        for row in record['rows']:
            vector = [0]*len(f['factor_base'])
            for j, sign in zip(row['triple'], row['signs'], strict=True):
                vector[j] = (vector[j]+sign) % f['r']
            if row['coefficients'] != vector or row['source_scalar'] != 0 or row['curve_uid'] != f['uid']:
                raise ValueError('geometric native coefficient encoding')
            descriptions.append((tuple(row['triple']), tuple(row['signs'])))
        if sorted(descriptions) != sorted(self.triples.get(Q, [])):
            raise ValueError('complete geometric distinct-triple oracle')
        expected = []
        for third, sign in product(range(len(geom['points'])), (1, -1)):
            q = self.signed[third, sign]
            wanted = self.add(Q, (q[0], -q[1] % f['p']))
            bucket = self.table.get(wanted, [])
            expected.append(dict(third=third, native_third=geom['native_indices'][third], sign=sign,
                wanted=None if wanted is None else list(wanted), bucket=bucket,
                accepted=[j for j in bucket if self.pairs[j]['indices'][1] < third]))
        if record['trace'] != expected:
            raise ValueError('geometric query/miss/bucket trace')
        return dict(checked=True, geometric_atoms=len(geom['points']), native_width=len(f['factor_base']),
                    rows=len(descriptions), signed_queries=len(expected))

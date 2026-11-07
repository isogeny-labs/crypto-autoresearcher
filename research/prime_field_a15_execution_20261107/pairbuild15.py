"""Executed sign-reusing, shared-denominator pair construction, native order kept.

The scalar control is the unchanged A14 QueryIndex. Candidate pair formulas
operate on actual uint64 arrays and count each evaluated field element. Explicit
array traffic is not an estimate of all NumPy/Python allocation or peak memory.
"""
from collections import defaultdict
from itertools import combinations, product
import numpy as np
from deps15 import QueryIndex, require, batch_query


class PairField(batch_query.VectorField):
    def allocated(self, value):
        self.m.other['pair_array_allocations'] += 1
        self.m.other['pair_array_allocated_bytes'] += value.nbytes
        self.m.other['pair_array_allocated_elements'] += value.size
        return value

    def array(self, value):
        out = self.allocated(np.array(value, dtype=np.uint64))
        self.m.other['pair_integer_to_uint64_elements'] += out.size
        return out


def validate_geometry(fixture, geometry, rules, meter, capability):
    require(rules, fixture, geometry, capability)
    p = fixture['p']
    if type(p) is not int or not 3 <= p < 2**32:
        raise ValueError('pair uint64 field gate')
    if len(geometry['native_indices']) != len(geometry['points']):
        raise ValueError('pair native index count')
    seen = set()
    for point in geometry['points']:
        meter.other['pair_input_points_validated'] += 1
        if (len(point) != 2 or any(type(v) is not int or not 0 <= v < p for v in point)
                or point[1] == 0 or point[0] in seen):
            raise ValueError('pair geometry must contain finite, non-order-two, distinct sign classes')
        seen.add(point[0])
    if (len(set(geometry['native_indices'])) != len(geometry['points']) or
            any(type(j) is not int or not 0 <= j < len(fixture['factor_base']) for j in geometry['native_indices'])):
        raise ValueError('pair representative native slots')
    if any(list(point) != fixture['factor_base'][j]['point'] for point,j in
            zip(geometry['points'],geometry['native_indices'],strict=True)):
        raise ValueError('pair representative/native point disagreement')
    if 2*len(seen)*(len(seen)-1) > rules['max_pair_entries']:
        raise ValueError('pair prospective size gate')


class BatchedPairIndex(QueryIndex):
    def __init__(self, fixture, geometry, rules, meter, event, capability=None):
        require(rules, fixture, geometry, capability)
        self.fixture, self.geometry, self.rules, self.event = fixture, geometry, rules, event
        self.points = [tuple(v) for v in geometry['points']]
        self.native_indices = geometry['native_indices']
        self.pairs, self.table, self.base_index = [], defaultdict(list), {}

        def setup():
            for j, atom in enumerate(fixture['factor_base']):
                self.base_index.setdefault(tuple(atom['point']), []).append(j)
                meter.other['native_base_index_entries'] += 1
            return {(j, sign): q if sign == 1 else meter.neg(q)
                    for j, q in enumerate(self.points) for sign in (1, -1)}

        self.signed = meter.stage('geometric_query_sign_index', setup)
        self.engines = meter.stage('query_engine_index_setup', lambda:
            batch_query.QueryEngines(fixture, self.points, self.signed, meter, event))
        f = PairField(meter)

        def inputs():
            pairs = list(combinations(range(len(self.points)), 2))
            meter.other['pair_index_pairs_materialized'] += len(pairs)
            arrays = [f.array([self.points[index[side]][coordinate] for index in pairs])
                      for side, coordinate in product((0, 1), repeat=2)]
            meter.other['pair_input_coordinate_list_elements'] += 4*len(pairs)
            return pairs, arrays

        indices, arrays = meter.stage('pair_batch_inputs', inputs)
        if not indices:
            return
        Xj, Yj, Xk, Yk = arrays
        denominator = meter.stage('pair_denominators', lambda: f.sub(Xk, Xj))

        def invert():
            # Distinct geometric sign classes preclude zero x-denominators.
            # An unexpected zero refuses the batch, never becomes a dummy point.
            mask = f.allocated(denominator == 0)
            meter.other['pair_zero_denominator_tests'] += len(mask)
            if np.any(mask):
                raise ValueError('unexpected pair zero denominator')
            before = meter.other['query_batch_padding_ones']
            result = batch_query.batch_inverse(denominator, f)
            meter.other['pair_batch_padding_ones'] += meter.other['query_batch_padding_ones']-before
            meter.other['pair_inverse_results'] += len(result)
            return result

        inverse = meter.stage('pair_batch_inversion', invert)

        def formulas():
            summed_x = f.add(Xj, Xk)
            Ynegative = f.sub(0, Yk)
            result = []
            for Y in (Yk, Ynegative):
                slope = f.mul(f.sub(Y, Yj), inverse)
                xx = f.sub(f.mul(slope, slope), summed_x)
                yy = f.sub(f.mul(slope, f.sub(Xj, xx)), Yj)
                result.append((xx, yy))
            return result

        plus, minus = meter.stage('pair_shared_formulas', formulas)
        neg_minus, neg_plus = meter.stage('pair_output_negations', lambda:
            (f.sub(0, minus[1]), f.sub(0, plus[1])))

        def emit():
            for i, (j, k) in enumerate(indices):
                # Exact old (++),(+-),(-+),(--) insertion order.
                for signs, (X, Y) in zip(product((1, -1), repeat=2),
                        (plus, minus, (minus[0], neg_minus), (plus[0], neg_plus)), strict=True):
                    q = int(X[i]), int(Y[i])
                    meter.other['pair_uint64_to_integer_elements'] += 2
                    self.table[q].append(len(self.pairs))
                    self.pairs.append(dict(indices=[j, k],
                        native_indices=[self.native_indices[j], self.native_indices[k]],
                        signs=list(signs), point=list(q)))
                    meter.other['pair_table_insertions'] += 1
                    self.event(dict(kind='geometric_pair', index=len(self.pairs)-1, record=self.pairs[-1]))
                    if len(self.pairs) > rules['max_pair_entries']:
                        raise ValueError('pair actual size gate')

        meter.stage('pair_table_materialization', emit)


def build(method, fixture, geometry, rules, meter, event, capability=None):
    if method not in ('scalar', 'batched'):
        raise ValueError('unknown pair construction method')
    meter.stage('pair_input_validation', lambda:
        validate_geometry(fixture, geometry, rules, meter, capability))
    cls = QueryIndex if method == 'scalar' else BatchedPairIndex
    return cls(fixture, geometry, rules, meter, event, capability)

"""Paid pair/batch index on distinct geometry, emitting native-width rows."""
from collections import defaultdict
from itertools import combinations, product
from shared import core, batch_query
from guards import NATIVE_CAPABILITY, require_fields


def require(rules, fixture, geometry, capability):
    require_fields(rules, fixture, capability)
    if (geometry['native_width'] != len(fixture['factor_base']) or not
        1 <= len(geometry['points']) <= geometry['native_width'] <= 48):
        raise ValueError('query native/geometric width gate')
    if not 0 < rules['max_pair_entries'] <= 8192 or not 0 < rules['max_retained_rows'] <= 4096:
        raise ValueError('query pair/row gate declaration')


class QueryIndex:
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
        self.engines = meter.stage('query_engine_index_setup',
            lambda: batch_query.QueryEngines(fixture, self.points, self.signed, meter, event))

        def pairs():
            for (j, k), signs in product(combinations(range(len(self.points)), 2), product((1, -1), repeat=2)):
                q = meter.e.add(self.signed[j, signs[0]], self.signed[k, signs[1]])
                self.table[q].append(len(self.pairs))
                self.pairs.append(dict(indices=[j, k], native_indices=[self.native_indices[j], self.native_indices[k]],
                    signs=list(signs), point=None if q is None else list(q)))
                meter.other['pair_table_insertions'] += 1
                self.event(dict(kind='geometric_pair', index=len(self.pairs)-1, record=self.pairs[-1]))
                if len(self.pairs) > rules['max_pair_entries']:
                    raise ValueError('geometric pair size gate')

        meter.stage('pair_construction', pairs)

    def query(self, Q, meter, context):
        rows, trace = [], []
        try:
            wanted_points = self.engines.evaluate(Q, meter, context)
            for third, sign in product(range(len(self.points)), (1, -1)):
                wanted = wanted_points[2*third+(sign == -1)]
                bucket, accepted = self.table.get(wanted, []), []
                meter.other['signed_point_queries'] += 1
                meter.other['table_lookups'] += 1
                for index in bucket:
                    pair = self.pairs[index]
                    meter.other['bucket_entries_inspected'] += 1
                    if pair['indices'][1] >= third:
                        continue
                    native = pair['native_indices']+[self.native_indices[third]]
                    signs = pair['signs']+[sign]
                    row = core.old.direct.make_row(self.fixture, 0, native, signs)
                    total = None
                    for j, s in zip(pair['indices']+[third], signs, strict=True):
                        total = meter.e.add(total, self.signed[j, s])
                    if not meter.equal(total, Q):
                        raise ValueError('native geometric row group certificate')
                    rows.append(row)
                    accepted.append(index)
                    meter.other['geometric_relation_certificates'] += 1
                    self.event(dict(kind='geometric_relation', context=context, row=row))
                    if len(rows) > self.rules['max_retained_rows']:
                        raise ValueError('geometric query row gate')
                record = dict(third=third, native_third=self.native_indices[third], sign=sign,
                    wanted=None if wanted is None else list(wanted), bucket=bucket, accepted=accepted)
                trace.append(record)
                self.event(dict(kind='geometric_query', context=context, record=record))
            rows.sort(key=lambda row: (tuple(row['triple']), tuple(row['signs'])))
            return dict(point=None if Q is None else list(Q), rows=rows, trace=trace)
        except BaseException as error:
            self.event(dict(kind='geometric_query_failed', context=context, point=None if Q is None else list(Q),
                partial_rows=rows, partial_trace=trace, error_type=type(error).__name__, error=str(error)))
            raise

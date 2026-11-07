"""Pure geometric target aliases; affine coefficient labels stay with callers."""
from guards import require_fields
from shared import core


class TargetCache:
    def __init__(self, index, natural_records, rules, event, capability=None):
        require_fields(rules, index.fixture, capability)
        if len(natural_records) != rules['targets']:
            raise ValueError('natural target cache census')
        self.index, self.rules, self.event = index, rules, event
        self.base_index, self.engines = index.base_index, index.engines
        self.engine_start = len(index.engines.records)
        self.records, self.lookup = [], {}
        self.meter = core.ProgressMeter(index.fixture, event, dict(kind='shared_target_queries'))

        def seed():
            self.meter.other['shared_public_geometry_index_references'] += 1
            for record in natural_records:
                Q = None if record['point'] is None else tuple(record['point'])
                if Q in self.lookup:
                    raise ValueError('duplicate natural public target')
                new = dict(id=len(self.records), **record, seeded_natural=True,
                           phase_ids=['natural_target_queries'])
                self.lookup[Q] = new['id']
                self.records.append(new)
                self.meter.other['query_cache_seed_points'] += 1
                self.meter.other['seed_relation_references'] += len(record['rows'])
                self.meter.other['seed_trace_references'] += len(record['trace'])

        self.meter.stage('natural_decomposition_cache_seed', seed)

    def request(self, Q, context):
        serial = self.meter.other.get('logical_target_requests', 0)

        def lookup():
            self.meter.other['logical_target_requests'] += 1
            self.meter.other['target_cache_lookups'] += 1
            index = self.lookup.get(Q)
            if index is not None:
                self.meter.other['target_cache_hits'] += 1
            return index

        found = self.meter.stage('target_cache_lookup_'+str(serial), lookup)
        self.event(dict(kind='target_request', context=context, point=None if Q is None else list(Q),
                        cache_hit=found is not None))
        if found is not None:
            return found
        maximum = self.rules['targets']*(1+len(self.rules['target_policies'])*(self.rules['target_queries_per_point']-1))
        if len(self.records) >= maximum:
            raise ValueError('fixed geometric target cache size gate')
        identifier = len(self.records)
        name = 'target_query_'+str(identifier)
        record = dict(id=identifier, point=None if Q is None else list(Q), rows=[], trace=[],
                      seeded_natural=False, phase_ids=[name])
        self.lookup[Q] = identifier
        self.records.append(record)

        def query():
            self.meter.other['target_cache_records_added'] += 1
            value = self.index.query(Q, self.meter, dict(target=True, query_id=identifier))
            record.update(value)

        self.meter.stage(name, query)
        self.event(dict(kind='target_cache_record', record=record))
        return identifier

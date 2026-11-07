"""Paid norm prerequisites, owned helper caches and native source relations.

A16 prepares disjoint program/horizon state; pair construction is the executed
A15 batch builder. Derived from pinned A14 mixed_collection without editing it.
Preparation contains no target generation. Each norm/hybrid program executes
its own prerequisites, geometry and source construction. Source-free known
controls execute only their own paid base/index and natural target queries.
"""
from copy import deepcopy
from hashlib import sha256
import json

from shared import core, batch_query
from guards import require_fields
import geometry
from deps16 import pair_build
import source_construct


class Prepared(dict):
    meter = None


def signed_owned(fixture, records, meter):
    """Close only owned P labels under sign, paying each missing negation."""
    r = fixture['r']
    known = {}
    for item in records:
        scalar = item['scalar']
        point = None if item['point'] is None else tuple(item['point'])
        if type(scalar) is not int or not 0 <= scalar < r:
            raise ValueError('owned scalar encoding')
        meter.other['owned_label_insert_lookups'] += 1
        if scalar in known and known[scalar]['point'] != item['point']:
            raise ValueError('inconsistent owned P label')
        known.setdefault(scalar, dict(point=None if point is None else list(point),
                                      scalar=scalar, origin=item['origin']))
    for scalar, item in list(known.items()):
        if not scalar:
            continue
        opposite_scalar = meter.ring.sub(0, scalar)
        meter.other['owned_opposite_label_lookups'] += 1
        if opposite_scalar in known:
            continue
        point = meter.neg(tuple(item['point']))
        known[opposite_scalar] = dict(point=list(point), scalar=opposite_scalar,
                                      origin=dict(kind='owned_paid_sign', parent=item['origin'], scalar=scalar))
    return [known[scalar] for scalar in sorted(known) if scalar]


def native_cell(original, helper):
    if helper is None:
        return deepcopy(original)
    if helper['public_base_size'] != 16 or len(helper['cell']['fixture']['factor_base']) != 16:
        raise ValueError('hybrid owns exactly its separate paid helper16')
    prior, supplied = original['fixture'], helper['cell']['fixture']
    if any(prior[key] != supplied[key] for key in ('p', 'a', 'b', 'r', 'P', 'ec1')):
        raise ValueError('helper belongs to a different curve')
    fixture = {key: deepcopy(prior[key]) for key in ('p', 'a', 'b', 'r', 'P')}
    fixture['factor_base'] = deepcopy(prior['factor_base'] + supplied['factor_base'])
    fixture['uid'] = sha256(json.dumps(fixture, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    fixture['ec1'] = deepcopy(prior['ec1'])
    return dict(id=original['id'], fixture=fixture)


def prepare(original, rules, helper, event, capability=None):
    """Execute the unchanged prerequisite walk and retain its old unknown order."""
    require_fields(rules, original['fixture'], capability)
    n = len(original['fixture']['factor_base'])
    if n != next(v['base_size'] for v in rules['fields'] if v['p'] == original['fixture']['p']):
        raise ValueError('original norm size differs from declared rules')
    cell = native_cell(original, helper)
    f, r = cell['fixture'], cell['fixture']['r']
    if not 1 <= rules['prerequisite'] < r or len(f['factor_base']) > 48:
        raise ValueError('prerequisite/native size gate')
    meter = core.ProgressMeter(f, event, dict(kind='norm_prelude', helper_size=0 if helper is None else 16))

    def verify():
        for point in [tuple(f['P'])] + [tuple(v['point']) for v in f['factor_base']]:
            if not meter.e.on(point) or meter.e.mul(r, point) is not None:
                raise ValueError('invalid public native point')

    meter.stage('public_setup_verification', verify)

    def prerequisites():
        values = {1: tuple(f['P'])}
        for scalar in range(2, rules['prerequisite'] + 1):
            values[scalar] = meter.e.add(values[scalar-1], tuple(f['P']))
            meter.other['prerequisite_group_adds'] += 1
        return values

    values = meter.stage('prerequisite_walk', prerequisites)
    projection = meter.stage('fixed_norm_projection', lambda: core.old.direct.public_projection(
        dict(fixture=original['fixture'], source_order=list(values)), values, meter))

    def units_and_basis():
        known, basis = [], [None] * projection['U']
        for j, item in enumerate(projection['native_to_projected']):
            meter.other['fixed_projection_entries_read'] += 1
            if item[0] == 'known':
                known.append([j, item[1]])
            else:
                if basis[item[1]] is not None:
                    raise ValueError('original norm has duplicate unknown sign classes')
                basis[item[1]] = [j, item[2]]
        if any(v is None for v in basis):
            raise ValueError('incomplete original norm basis')
        if helper is not None:
            known.extend([n+j, value] for j, value in enumerate(helper['signed_labels']))
        return known, basis

    known, basis = meter.stage('fixed_known_units_and_original_basis', units_and_basis)
    initial = [dict(scalar=s, point=list(q), origin='own_fixed_prerequisite') for s, q in values.items()]
    if helper is not None:
        initial += [dict(scalar=v['scalar'], point=v['point'], origin='own_paid_helper16')
                    for v in helper['knowledge']]
    initial = meter.stage('owned_initial_paid_signs', lambda: signed_owned(f, initial, meter))

    def supplied_information():
        # Knowledge bought by a helper constructor is supplied information even
        # when the matching old atom was not itself selected as a helper.
        available = {tuple(item['point']): item for item in initial}
        result = []
        for j, sign in basis:
            meter.other['supplied_old_coordinate_lookups'] += 1
            item = available.get(tuple(f['factor_base'][j]['point']))
            if item is None:
                continue
            vector = [0]*len(f['factor_base'])
            vector[j] = 1
            result.append(dict(vector=vector, rhs=item['scalar'], kind='supplied_owned_cache_match',
                               witness=dict(native_index=j, paid_label=item)))
            meter.other['supplied_old_coordinate_equations'] += 1
            meter.other['supplied_old_coordinate_coefficients_emitted'] += len(vector)
        return result

    supplied = meter.stage('supplied_old_coordinate_information', supplied_information)
    labels = {} if helper is None else {n+j: value for j, value in enumerate(helper['signed_labels'])}
    geom = meter.stage('native_geometry', lambda: geometry.build(f, n, labels, meter))
    selection = meter.stage('source_schedule_derivation', lambda: core.source.schedules(original, rules, meter, event))
    result = Prepared(program_id=rules['program_id'], target_horizon=rules['target_queries_per_point'], cell=cell, norm_size=n, projection=projection, known=known, basis=basis,
        prerequisites=[dict(scalar=s, point=list(q)) for s, q in values.items()],
        initial=initial, supplied=supplied, geometry=geom, selection=selection, phases=list(meter.phases),
        counters=meter.counters(), complete=True)
    result.meter = meter
    return result


def collect(prepared, target_generation, rules, event, capability=None):
    f = prepared['cell']['fixture']
    require_fields(rules, f, capability)
    if prepared.get('program_id') != rules['program_id'] or prepared.get('target_horizon') != rules['target_queries_per_point']:
        raise ValueError('collection borrowed another horizon preparation')
    meter = core.ProgressMeter(f, event, dict(kind='native_collection'))
    index = pair_build('batched', f, prepared['geometry'], rules, meter, event, capability)
    arms = {}
    schedules = [kind+str(seed) for seed in rules['seeds'] for kind in ('ap', 'hash')]
    for schedule in schedules if prepared['selection']['orders'] else []:
        values = prepared['selection']['orders'][schedule]
        ap = prepared['selection']['ap'].get(schedule)
        stream = source_construct.build(f, rules, prepared['initial'], values,
            'ap' if ap is not None else 'hash', ap, schedule, event, capability)
        rows, query_records = [], []

        def query_sources():
            for source in stream['sources']:
                generic = index.query(tuple(source['point']), stream.meter,
                                      dict(target=False, source_schedule=schedule, scalar=source['scalar']))
                query_records.append(generic)
                for row in generic['rows']:
                    # Cache rows remain public geometry with source_scalar=0.
                    rows.append(dict(row, source_scalar=source['scalar']))
                    if len(rows) > rules['max_retained_rows']:
                        event(dict(kind='source_rows_failed', source_schedule=schedule, partial_rows=rows))
                        raise ValueError('native source retained row size gate')

        stream.meter.stage('source_queries', query_sources)
        knowledge = stream.meter.stage('source_owned_paid_signs', lambda:
            signed_owned(f, [dict(v, origin=dict(kind='source_owned', source_schedule=schedule,
                prefix=v['prefix'], constructor_origin=v['origin'], paid_origin=v.get('paid_origin')))
                for v in stream['knowledge']], stream.meter))
        # The only native source horizon is complete; paid initial labels keep
        # their prefix 0 provenance, all selected constructor discoveries use S.
        original_prefix = {v['scalar']: v['prefix'] for v in stream['knowledge']}
        for item in knowledge:
            item['prefix'] = min(original_prefix.get(item['scalar'], rules['sources']),
                                 original_prefix.get(-item['scalar'] % f['r'], rules['sources']))

        def scan_anchors():
            result = []
            for item in knowledge:
                point = tuple(item['point'])
                stream.meter.other['owned_knowledge_base_lookups'] += 1
                for j in index.base_index.get(point, []):
                    vector = [0]*len(f['factor_base'])
                    vector[j] = 1
                    result.append(dict(coefficients=vector, source_scalar=item['scalar'],
                        prefix=item['prefix'], atom=j, kind='owned_public_scalar_anchor'))
                    stream.meter.other['owned_knowledge_anchor_rows'] += 1
                    stream.meter.other['owned_knowledge_anchor_coefficients_emitted'] += len(vector)
            return result

        anchors = stream.meter.stage('source_native_anchor_index', scan_anchors)
        arms[schedule] = dict(construction=dict(stream), rows=rows, query_records=query_records,
            knowledge=knowledge, anchors=anchors, sources=stream['sources'],
            phases=list(stream.meter.phases), counters=stream.meter.counters())

    def natural_queries():
        return [index.query(tuple(target['point']), meter,
                            dict(target=True, natural=True, index=target['index']))
                for target in target_generation['targets']]

    natural = meter.stage('natural_target_queries', natural_queries)
    result = batch_query.Collected(program_id=rules['program_id'], target_horizon=rules['target_queries_per_point'], complete=True, projection=prepared['projection'],
        selection=prepared['selection'], target_generation=target_generation, natural_records=natural,
        pairs=index.pairs, arms=arms, collection_phases=list(meter.phases),
        collection_counters=meter.counters(), query_engine_setup=index.engines.descriptor,
        query_engine_records=list(index.engines.records))
    result.query_index = index
    return result


def prepare_known(built, rules, event, capability=None):
    f = built['cell']['fixture']
    require_fields(rules, f, capability)
    n = len(f['factor_base'])
    if n not in (32, 48) or built['public_base_size'] != n:
        raise ValueError('source-free control requires its own paid known32/48')
    meter = core.ProgressMeter(f, event, dict(kind='source_free_known_prelude', public_base_size=n))
    initial = meter.stage('owned_initial_paid_signs', lambda: signed_owned(f,
        [dict(scalar=v['scalar'], point=v['point'], origin='own_paid_known'+str(n))
         for v in built['knowledge']], meter))
    geom = meter.stage('native_geometry', lambda: geometry.build(f, 0,
        dict(enumerate(built['signed_labels'])), meter))
    known = [[j, value] for j, value in enumerate(built['signed_labels'])]
    return Prepared(program_id=rules['program_id'], target_horizon=rules['target_queries_per_point'], cell=built['cell'], norm_size=0, projection=None, known=known, basis=[],
        prerequisites=[], initial=initial, supplied=[], geometry=geom,
        selection=dict(orders={}, ap={}, trace=[]),
        phases=list(meter.phases), counters=meter.counters(), complete=True)


def collect_known(prepared, target_generation, rules, event, capability=None):
    # Empty source schedules ensure no discarded source work subsidizes controls.
    result = collect(prepared, target_generation, rules, event, capability)
    result['arms']['known'] = dict(rows=[], anchors=[], sources=[],
        knowledge=[dict(v, prefix=0) for v in prepared['initial']], phases=[], counters={})
    return result

"""Metered old-base information after cancelling symbolic outside columns.

Only norm/hybrid cases on the same original coordinates may be compared.
Supplied cache information precedes collected rows in the attribution order.
This diagnostic executes separate algebra; it is not free target-solver work.
"""
from shared import solver, known_solver
import partial_solver


def compare(norm, norm_prepared, hybrid, hybrid_prepared, meter):
    partial_solver.validate(norm, norm_prepared['known'], norm_prepared['basis'])
    partial_solver.validate(hybrid, hybrid_prepared['known'], hybrid_prepared['basis'])
    if (norm_prepared['basis'] != hybrid_prepared['basis'] or norm['modulus'] != hybrid['modulus']
        or norm['targets'] != hybrid['targets'] or norm['target_count'] != hybrid['target_count']
        or norm_prepared['cell']['fixture']['factor_base'] !=
            hybrid_prepared['cell']['fixture']['factor_base'][:norm['width']]
        or norm['width']+16 != hybrid['width']):
        raise ValueError('old-base attribution requires matched norm/hybrid coordinates and targets')
    start = len(meter.phases)
    old = meter.stage('reference_known_substitution', lambda:
        partial_solver.reduce_case(norm, norm_prepared['known'], norm_prepared['basis'], meter))
    new = meter.stage('hybrid_known_substitution', lambda:
        partial_solver.reduce_case(hybrid, hybrid_prepared['known'], hybrid_prepared['basis'], meter))
    width, nt = old['width'], old['target_count']
    reference, combined = solver.KernelFreeSystem(width, meter), solver.KernelFreeSystem(width, meter)

    def reference_rows():
        for v, b in old['source']:
            reference.add(v, b)
            combined.add(v, b)

    meter.stage('reference_base_elimination', reference_rows)
    ranks = dict(reference=len(combined.pivots))
    origins = hybrid['source_origins'][len(hybrid_prepared['known']):]
    if len(origins) != len(new['source']):
        raise ValueError('hybrid source provenance census')
    groups = dict(supplied=[], collected=[])
    for index, ((v, b), origin) in enumerate(zip(new['source'], origins, strict=True)):
        if origin['kind'] == 'supplied_owned_cache_match': group = 'supplied'
        elif origin['kind'] in ('collected_source', 'constructed_source_anchor'): group = 'collected'
        else: raise ValueError('unclassified supplied/collected information')
        groups[group].append(dict(vector=v, rhs=b, reduced_source_index=index))
    for name, records in groups.items():
        def augment(records=records):
            for item in records:
                item['old_rowspace'] = reference.identify(item['vector'])
                combined.add(item['vector'], item['rhs'])
        meter.stage(name+'_base_elimination', augment)
        ranks[name] = len(combined.pivots)
    outside = solver.OutsideSystem(nt, meter)
    cancellations = []

    def cancel():
        for row in new['target']:
            weights = outside.add_relation(row['outside'])
            if weights is None:
                continue
            vector, rhs, native = [0]*width, 0, [0]*hybrid['width']
            for index, coefficient in weights:
                item, raw = new['target'][index], hybrid['target'][index]
                for j, value in enumerate(item['vector']):
                    if value:
                        vector[j] = meter.ring.add(vector[j], known_solver.product(coefficient, value, meter))
                        meter.other['information_cancellation_support'] += 1
                if item['rhs']:
                    rhs = meter.ring.add(rhs, known_solver.product(coefficient, item['rhs'], meter))
                for j, value in enumerate(raw['vector']):
                    if value:
                        native[j] = meter.ring.add(native[j], known_solver.product(coefficient, value, meter))
                        meter.other['information_native_lift_support'] += 1
            # The native target combination has zero outside coordinates. Unit
            # weights cancel exactly its declared supplied native coordinates.
            units = [meter.ring.sub(0, native[j]) if native[j] else 0
                     for j, value in hybrid_prepared['known']]
            rec = dict(vector=vector, rhs=rhs, original_target_weights=weights,
                supplied_unit_weights=units, old_rowspace=reference.identify(vector))
            cancellations.append(rec)
            combined.add(vector, rhs)
            meter.other['information_cancellation_rows'] += 1
            meter.other['information_unit_weights_emitted'] += len(units)

    meter.stage('outside_elimination_and_native_lifting', cancel)
    ranks['targets_after_cancellation'] = len(combined.pivots)
    phases = meter.phases[start:]
    return dict(reference=reference.summary(), final=combined.summary(), outside=outside.summary(),
        groups=groups, cancellations=cancellations, ranks=ranks,
        increments=dict(supplied=ranks['supplied']-ranks['reference'],
            collected_after_supplied=ranks['collected']-ranks['supplied'],
            targets_after_cancellation=ranks['targets_after_cancellation']-ranks['collected']),
        delta_vs_old=ranks['targets_after_cancellation']-ranks['reference'],
        attribution_order=['reference', 'supplied', 'collected', 'targets_after_cancellation'],
        phases=phases, counters=solver.counters(phases))

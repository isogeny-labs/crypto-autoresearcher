"""Independent scalar truth, full triple/miss oracle and pair count schedule."""
from collections import Counter
from hashlib import sha256
import json
from itertools import combinations, product
from deps15 import Oracle, check_source


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def commitment(value):
    return sha256(canonical(value)).hexdigest()


def tree_shape(size):
    multiplies = pads = 0
    while size > 1:
        odd = size % 2
        pads += odd
        size = (size+odd)//2
        multiplies += 3*size
    return multiplies, pads


def allocation_schedule(count):
    # Four coordinate arrays, denominator, bool mask, sixteen formula arrays,
    # two output negations. Product tree counts forward, padding, reverse copies.
    if not count:
        return dict(pair_array_allocations=4,pair_array_allocated_bytes=0,
            pair_array_allocated_elements=0,pair_integer_to_uint64_elements=0,
            pair_uint64_to_integer_elements=0)
    arrays, words, elements, conversions = 25,23*count+1,24*count+1,4*count+1
    size=count
    while size>1:
        odd=size%2;padded=size+odd;half=padded//2
        arrays+=4+2*odd
        extra=padded+3*half+odd*(1+padded)
        words+=extra;elements+=extra;conversions+=odd
        size=half
    return dict(pair_array_allocations=arrays,pair_array_allocated_bytes=8*words+count,
        pair_array_allocated_elements=elements,pair_integer_to_uint64_elements=conversions,
        pair_uint64_to_integer_elements=8*count)


def check_pairs(fixture, geometry, method, pairs, phases, expected_digest=None):
    p, a = fixture['p'], fixture['a']
    points = [tuple(v) for v in geometry['points']]
    if any((y*y-x*x*x-a*x-fixture['b']) % p for x,y in points):
        raise ValueError('independent pair curve membership')
    expected = []
    for (j,k), signs in product(combinations(range(len(points)), 2), product((1,-1), repeat=2)):
        signed = [(points[t][0], points[t][1]*s % p) for t,s in zip((j,k), signs, strict=True)]
        q = check_source.old.add(p, 0, a, *signed)
        expected.append(dict(indices=[j,k], native_indices=[geometry['native_indices'][j],geometry['native_indices'][k]],
            signs=list(signs),point=None if q is None else list(q)))
    if pairs != expected:
        raise ValueError('independent ordered pair/native/sign parity')
    digest = commitment(pairs)
    if expected_digest is not None and digest != expected_digest:
        raise ValueError('old A14 pair commitment differs')
    fields = ('Fp.field_add','Fp.field_sub','Fp.field_mul','Fp.field_inv','Fp.group_add')
    totals = Counter()
    pair_names = {'pair_construction','pair_batch_inputs','pair_denominators','pair_batch_inversion',
                  'pair_shared_formulas','pair_output_negations','pair_table_materialization'}
    for phase in phases:
        if phase['status'] != 'complete' or phase['wall_valid'] is not False:
            raise ValueError('pair phase incomplete/clock standing')
        if phase['phase'] in pair_names:
            totals.update(phase['counters'])
    construction=Counter()
    for phase in phases:construction.update(phase['counters'])
    count = len(points)*(len(points)-1)//2
    tree, padding = tree_shape(count)
    arithmetic = (dict(zip(fields,(0,28*count,12*count,4*count,4*count),strict=True)) if method=='scalar' else
                  dict(zip(fields,(count,12*count,6*count+tree,int(count>0),0),strict=True)))
    if any(totals.get(key,0)!=value for key,value in arithmetic.items()):
        raise ValueError('independent pair Fp schedule')
    if totals.get('pair_table_insertions',0)!=4*count:
        raise ValueError('pair storage multiplicity')
    if method=='batched' and totals.get('pair_batch_padding_ones',0)!=padding:
        raise ValueError('batch padding schedule')
    if method=='batched':
        for key,value in allocation_schedule(count).items():
            if totals.get(key,0)!=value:raise ValueError('independent pair allocation schedule: '+key)
    full_arithmetic=dict(arithmetic)
    full_arithmetic['Fp.field_sub']+=len(points) # prepaid geometric negatives
    if any(construction.get(key,0)!=value for key,value in full_arithmetic.items()):
        raise ValueError('independent complete construction Fp schedule')
    setup=dict(query_array_allocations=3,query_array_allocated_bytes=24*len(points),
        query_array_allocated_elements=3*len(points),query_integer_to_uint64_elements=3*len(points),
        native_base_index_entries=len(fixture['factor_base']),pair_input_points_validated=len(points),
        point_negations=len(points),query_prepaid_signed_point_references=2*len(points))
    if any(construction.get(key,0)!=value for key,value in setup.items()):
        raise ValueError('independent construction setup schedule')
    return dict(checked=True,ordered_pairs=len(pairs),unordered_pairs=count,
        pairs_sha256=digest,arithmetic=arithmetic,construction_arithmetic=full_arithmetic,
        construction_counters=dict(construction),pair_stage_counters=dict(totals),padding=padding if method=='batched' else 0)


def query_arithmetic(fixture,record,engine_counts):
    counts=Counter()
    for value in engine_counts.values():counts.update(value)
    p,a=fixture['p'],fixture['a']
    for row in record['rows']:
        total=None
        for j,sign in zip(row['triple'],row['signs'],strict=True):
            x,y=fixture['factor_base'][j]['point'];q=x,sign*y%p
            counts['Fp.group_add']+=1
            if total is not None and not (total[0]==x and (total[1]+q[1])%p==0):
                additions,muls,subs=(2,7,5) if total[0]==x else (0,3,7)
                counts.update({'Fp.field_add':additions,'Fp.field_mul':muls,'Fp.field_sub':subs,'Fp.field_inv':1})
            total=check_source.old.add(p,0,a,total,q)
    return {key:counts.get(key,0) for key in ('Fp.field_add','Fp.field_sub','Fp.field_mul','Fp.field_inv','Fp.group_add')}


def check_query(snapshot, query, record, index, oracle):
    oracle.check(record,index.pairs)
    if commitment(record)!=query['expected_record_sha256']:
        raise ValueError('retained A14 native row/query/miss commitment differs')
    if index.engines.records[-1]['points_sha256']!=query['expected_signed_points_sha256']:
        raise ValueError('retained A14 signed query points differ')
    return dict(checked=True,rows=len(record['rows']),signed_queries=len(record['trace']),
                record_sha256=commitment(record))

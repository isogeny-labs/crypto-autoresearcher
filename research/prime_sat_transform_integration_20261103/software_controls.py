"""UNVALIDATED fixed control source. Nothing runs on import.

Invocation requires separate exact-source admission. No CLI auto-runs this suite.
The complete 106 coordinate + 6 coefficient comparison is not implemented by
these smoke controls and remains mandatory downstream.
"""
from collections import Counter
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import signal
import time

from . import attempt_receipt, bridge_counted, census_v2, chart_solver, transform, transport

ROOT = transform.ROOT
PLAN = ROOT/'coordination/prime_sat_transform_source_20261105/downstream-validation-plan.md'
CONTRACT = ROOT/'coordination/prime_sat_full_chart_composition_20261101/fixed-software-contract.json'
LIMITS = {'outer_calls': 16, 'native_conflicts_per_call': 1000,
          'native_decisions_per_call': 10000, 'degree': 2, 'rows': 256, 'pc_calls': 32}


class InjectedFailure(RuntimeError):
    pass


@contextmanager
def patched(obj, name, value):
    old = getattr(obj, name); setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)


class Controls:
    def __init__(self, directory, *, deadline_seconds=600):
        if type(deadline_seconds) is not int or not 0 < deadline_seconds <= 600:
            raise ValueError('fixed software wall cap')
        self.directory = Path(directory)
        self.receipt = attempt_receipt.AttemptReceipt(directory, {'kind': 'software-controls',
            'validation_plan_sha256': transform.hashlib.sha256(PLAN.read_bytes()).hexdigest(),
            'limits': LIMITS, 'wall_seconds': deadline_seconds})
        self.deadline = time.monotonic() + deadline_seconds
        self.records = []; self.native_instances = 0; self.native_calls = 0; self.census_visits = 0

    def check(self, condition, label, **detail):
        self.remaining()
        row = {'label': label, 'accepted': bool(condition), **detail}; self.records.append(row)
        self.receipt.checkpoint(event='control', records=self.records,
             counters={'native_instances': self.native_instances, 'native_calls': self.native_calls,
                       'census_assignments_visited': self.census_visits})
        if not condition:
            raise AssertionError(label)

    def remaining(self):
        if time.monotonic() >= self.deadline:
            raise TimeoutError('fixed software attempt deadline')

    def rejects(self, function, label, *, expected=(ValueError, AssertionError), layer=None):
        self.remaining()
        try:
            function()
        except expected as error:
            self.check(True, label, rejection={'type': type(error).__name__, 'message': str(error)}, layer=layer)
            return error
        self.check(False, label, layer=layer)

    def native_factory(self, **kwargs):
        self.remaining()
        if self.native_instances >= 12:
            raise RuntimeError('twelve native-instance cap')
        self.native_instances += 1
        from pysat.solvers import Cadical195
        native = Cadical195(**kwargs)
        owner = self
        class BoundedNative:
            def __init__(self):
                self.calls = 0
            def __getattr__(self, name):
                return getattr(native, name)
            def solve_limited(self):
                owner.remaining()
                if self.calls >= 16:
                    raise RuntimeError('sixteen calls per instance cap')
                self.calls += 1; owner.native_calls += 1
                return native.solve_limited()
        return BoundedNative()


def _public(fixture, arm, stratum):
    return {key: deepcopy(fixture[key]) for key in ('p', 'a', 'b', 'target', 't', 's')} | {
        'k': len(fixture['points']), 'arm': arm, 'stratum': stratum}


def _witness(fixture):
    c = transform.composition()
    curve = {key: fixture[key] for key in ('p', 'a', 'b')}
    w = c.charts.construct_from_signed_multiset(curve, {'t': fixture['t'], 's': fixture['s']},
                                               fixture['points'], fixture['target'])
    points = sorted(deepcopy(fixture['points'])) + [None]*(5-len(fixture['points']))
    return w, points


def original_regressions(ctx):
    """Execute the unchanged fixed suite; it has no native solver/census calls."""
    c = transform.composition()
    path = ROOT/'research/prime_sat_full_chart_composition_20261101/test_composition.py'
    spec = importlib.util.spec_from_file_location('_transform_original_controls', path)
    module = importlib.util.module_from_spec(spec)
    import sys
    existing = sys.modules.get('composition')
    if existing is not None and Path(existing.__file__).resolve() != Path(c.__file__).resolve():
        raise ImportError('unexpected composition module for original controls')
    sys.modules['composition'] = c
    output = io.StringIO()
    try:
        spec.loader.exec_module(module)
        with redirect_stdout(output):
            module.run()
    finally:
        if existing is None:
            sys.modules.pop('composition', None)
        else:
            sys.modules['composition'] = existing
        ctx.receipt.checkpoint(event='original_regression_raw', original_stdout=output.getvalue(),
                               original_records=deepcopy(getattr(module, 'records', [])))
    result = json.loads(output.getvalue())
    ctx.check(result['chart_documents'] == 135, 'all original 15 x 3 x 3 descriptors', original=result)
    # The unchanged suite also covers all eight nilpotent/eight guard cases,
    # both F1 beta signs, impossible/empty charts, wrapped intervals and mutations.


def boundary_descriptors():
    c = transform.composition()
    return [{'p': 5, 'a': 1, 'b': beta, 'k': 2, 'target': list(target), 't': 0, 's': 1,
             'arm': arm, 'stratum': 'constant'}
            for beta, target in ((1, (0, 1)), (1, (2, 1)), (0, (0, 0)), (0, (2, 0)))
            for arm in c.ARMS]


def source_transport_controls(ctx):
    c = transform.composition()
    for descriptor in boundary_descriptors():
        docs = {mode: transform.build_transform(descriptor, mode) for mode in transform.MODES}
        for mode, doc in docs.items():
            ctx.check(transform.authenticate_transform(doc, descriptor, mode)['status'] == 'applicable',
                      'boundary authentication', descriptor=descriptor, mode=mode)
            if mode == 'identity':
                ctx.check(transform.encoded(doc['source']) == transform.encoded(doc['original']['source']),
                          'identity original source bytes')
            else:
                ctx.check(doc['projections']['transformed'] == ['chart.A1'], 'q remains projected')
                ctx.check(len(doc['row_map']) == len(doc['original']['source']['equations']) +
                          int(mode == 'k2_addrow_A0'), 'every original/appended row mapped')
                ctx.check(all(item['retained'] or item['identically_zero'] for item in doc['row_map']),
                          'only literal zero rows omitted')
            ctx.rejects(lambda doc=doc, mode=mode: transform.build_transform(doc, mode),
                        'already transformed trust root rejected', layer='descriptor')
    contract = json.loads(CONTRACT.read_text())
    for fixture in contract['chart_fixtures']:
        if 'impossible' in fixture['id']:
            continue
        w, points = _witness(fixture)
        stratum = 'zero' if w['B'] == [0] else 'constant' if len(w['B']) == 1 else 'linear'
        for arm in c.ARMS:
            desc = _public(fixture, arm, stratum)
            original = c.construct_assignment(desc, w, points)['assignment']
            for mode in transform.MODES:
                doc = transform.build_transform(desc, mode)
                if doc['status'] == 'not_applicable':
                    ctx.check(mode != 'identity', 'explicit nonapplicability retained', descriptor=desc, mode=mode)
                    continue
                enc = transport.encode_transformed_assignment(doc, original, desc, mode)
                dec = transport.decode_and_check_original(doc, enc['bits'], desc, mode)
                ctx.check(dec['assignment'] == original and dec['recovered'] == points,
                          'complete assignment and signed multiplicity transport', fixture=fixture['id'], arm=arm, mode=mode)
                field_values = [sum(t['coefficient'] * _product(original[n] for n in t['variables'])
                                    for t in row['terms']) % desc['p'] for row in doc['original']['source']['equations']]
                ctx.check(not any(field_values), 'independent original sparse residuals')
                rd = doc['range_document']
                bit_values = [sum(v for mask, v in poly.items() if int(mask) & enc['bits'] == int(mask)) % desc['p']
                              for poly in rd['polynomials']]
                ctx.check(not any(bit_values), 'independent transformed Boolean residuals')
    # Explicitly retain both common-root auxiliary fibers through identity transport.
    f1 = contract['signed_recovery_regressions'][0]
    points = [row['point'] for row in f1['expected_divisor'] for _ in range(row['multiplicity'])]
    f = {'p': f1['p'], 'a': f1['a'], 'b': f1['b'], 't': 0, 's': 0, 'target': None, 'points': points}
    w, padded = _witness(f); desc = _public(f, c.ARMS[2], 'linear')
    doc = transform.build_transform(desc, 'identity'); outputs = []
    for beta in f1['guard_beta_values']:
        original = c.construct_assignment(desc, w, padded, beta)['assignment']
        enc = transport.encode_transformed_assignment(doc, original, desc, 'identity')
        dec = transport.decode_and_check_original(doc, enc['bits'], desc, 'identity')
        ctx.check(dec['recovered'] == padded, 'F1 exact signed multiplicities retained', beta=beta)
        outputs.append(dec)
    ctx.check(outputs[0]['transformed_bits'] != outputs[1]['transformed_bits'] and
              outputs[0]['projection'] == outputs[1]['projection'], 'both beta auxiliary fibers retained')
    return contract


def _product(values):
    result = 1
    for value in values:
        result *= value
    return result


def mutation_controls(ctx, contract):
    c = transform.composition()
    fixture = next(f for f in contract['chart_fixtures'] if f['id'] == 'finite_two_repeat')
    d = _public(fixture, c.ARMS[0], 'constant'); mode = 'k2_addrow_A0'
    doc = transform.build_transform(d, mode)
    transform.authenticate_transform(doc, d, mode)  # positive layer control first
    mutations = [
        ('original_digest', lambda x: x.update(original_sha256='0'*64)),
        ('descriptor_target', lambda x: x['descriptor'].update(target=[0, 1] if d['target'] != [0, 1] else [2, 1])),
        ('N1_index', lambda x: x['appended_row_certificate']['summands'][0].update(index=999)),
        ('N2_index', lambda x: x['appended_row_certificate']['summands'][1].update(index=999)),
        ('multiplier', lambda x: x['appended_row_certificate']['summands'][1].update(coefficient=(2*d['target'][0]+1)%d['p'])),
        ('appended_row', lambda x: x['source']['equations'].pop(next(i for i,r in enumerate(x['source']['equations']) if r['label'].startswith('transform.')))),
        ('nonzero_norm', lambda x: x['source']['equations'].pop(next(i for i,r in enumerate(x['source']['equations']) if r['label'].startswith('norm.') and r['terms']))),
        ('interval_row', lambda x: x['source']['equations'].pop(next(i for i,r in enumerate(x['source']['equations']) if r['label'].startswith('interval.')))),
        ('rationality_row', lambda x: x['source']['equations'].pop(next(i for i,r in enumerate(x['source']['equations']) if r['label'].startswith('rationality.')))),
        ('q_projection', lambda x: x['projections'].update(transformed=[])),
        ('original_order', lambda x: x['projections']['original'].reverse()),
        ('inverse_sign', lambda x: x['inverse_pivot'].update(terms=[{'coefficient':1,'variables':[]}])),
        ('auxiliary_alias', lambda x: x['source']['auxiliaries'].append('chart.A1')),
        ('range_boundary', lambda x: x['range_document']['descriptor'].update(p=d['p']+2)),
        ('bootstrap_cnf', lambda x: x['range_document']['bootstrap_cnf'].append([])),
        ('unknown_operation', lambda x: x.update(operation='unrequested'))]
    for name, mutate in mutations:
        bad = deepcopy(doc); mutate(bad)
        ctx.rejects(lambda bad=bad: transform.authenticate_transform(bad, d, mode),
                    'transform mutation '+name, layer='transform_authentication')
    ctx.rejects(lambda: c.authenticate_chart(doc, d), 'transformed document is not original canonical document', layer='original_authentication')
    # p=7 has actual range recurrence states, independent of the p=5 cohort.
    seven = next(f for f in contract['chart_fixtures'] if f['id'] == 'finite_two_torsion')
    d7 = _public(seven, c.ARMS[0], 'constant'); doc7 = transform.build_transform(d7, 'identity')
    bad = deepcopy(doc7)
    index = next(i for gen in bad['range_document']['generators'] for i in gen['recurrences'])
    bad['range_document']['polynomials'][index] = {'0': 1}
    ctx.rejects(lambda: transform.authenticate_transform(bad, d7, 'identity'), 'changed range recurrence', layer='transform_authentication')
    rd = deepcopy(doc['range_document'])
    rd['polynomials'][0] = {'01': 1}
    ctx.rejects(lambda: chart_solver.convert_range(rd), 'noncanonical monomial-mask conversion', layer='range_authentication')
    w, points = _witness(fixture); assignment = c.construct_assignment(d, w, points)['assignment']
    enc = transport.encode_transformed_assignment(doc, assignment, d, mode)
    partial = {'status': 'censored', 'models': [enc['bits']], 'learned': []}
    good = chart_solver.verify_chart_answer(doc, d, mode, partial)
    ctx.check(good['accepted'] and not good['verified_complete'], 'valid partial transcript never promoted')
    for label, answer in (
        ('missing subtree', {'status':'complete','models':[],'learned':[]}),
        ('duplicate projection', {'status':'censored','models':[enc['bits'],enc['bits']],'learned':[]}),
        ('invalid original alongside valid', {'status':'censored','models':[enc['bits']],'learned':[
            {'depth':0,'prefix':0,'clause':[],'certificate':[]}]})):
        result = chart_solver.verify_chart_answer(doc, d, mode, answer)
        ctx.check(not result['accepted'] and result['completion']['original'] == answer,
                  'certificate negative '+label, result=result)
    changed = dict(assignment); changed['support.u0'] = (changed['support.u0']+1)%d['p']
    # Encoding rejects nonroots. Obtain canonical bits directly for the negative.
    reduced = {name: changed[name] for name in doc['variable_orders']['transformed']}
    rd = doc['range_document']; bits = c.compiler().encode_assignment(rd, reduced, rd['descriptor'], 'range')
    ctx.check(not chart_solver.verify_chart_answer(doc,d,mode,{'status':'censored','models':[bits],'learned':[]})['accepted'],
              'nonroot model rejected by original checks')
    # Final adapter independently checks certificate multipliers and projection clauses.
    adapter = c.compiler().adapter()
    proof = {'depth':0,'prefix':0,'clause':[],'certificate':[{'0':1}]}
    literal = {'status':'complete','models':[],'learned':[proof]}
    ctx.check(adapter.verify_transcript(5,1,1,[{'0':1}],[],literal,aux_bound=None)['valid'], 'literal certificate control')
    for label, mutate in (('multiplier', lambda a:a['learned'][0].update(certificate=[{'0':2}])),
                          ('projection blocker', lambda a:a['learned'][0].update(clause=[1]))):
        bad = deepcopy(literal); mutate(bad)
        ctx.check(not adapter.verify_transcript(5,1,1,[{'0':1}],[],bad,aux_bound=None)['valid'],
                  'final adapter rejects '+label)
    return d, doc, assignment, enc['bits']


class FakeNative:
    """Deterministic error paths; never constructs a native solver."""
    def __init__(self, *, result=None, model=None, stats_error=None, teardown_error=None, **ignored):
        self.result = result; self.model = model; self.stats_error = stats_error
        self.teardown_error = teardown_error; self.deleted = False
    def configure(self, options):
        self.options = options
    def set_phases(self, phases):
        self.phases = phases
    def connect_propagator(self, prop):
        self.prop = prop
    def observe(self, variable):
        return None
    def conf_budget(self, value):
        self.conflicts = value
    def dec_budget(self, value):
        self.decisions = value
    def solve_limited(self):
        return self.result
    def get_model(self):
        return self.model
    def accum_stats(self):
        if self.stats_error:
            raise self.stats_error
        return {'conflicts': 0, 'decisions': 0, 'propagations': 0, 'restarts': 0}
    def delete(self):
        self.deleted = True
        if self.teardown_error:
            raise self.teardown_error


def failure_controls(ctx, descriptor, document, assignment, bits):
    legacy = chart_solver._legacy()
    engine, _, guard = bridge_counted._private_engine('baseline')
    ring = legacy.CountedRing(1, 5)
    prop = engine.PrefixPropagator(ring, [], 1, LIMITS, 'model_only', [0, 1])
    primary = InjectedFailure('arithmetic after counted add')
    def bad_arithmetic():
        ring.add({0:1}, {0:1})
        raise primary
    caught = ctx.rejects(lambda: prop._charge('pc', bad_arithmetic), 'arithmetic finally charged', expected=(InjectedFailure,))
    ctx.check(caught is primary and prop.arithmetic['pc']['coefficient_additions'] > 0,
              'primary arithmetic exception identity and counted delta')
    def child():
        return prop._charge('pc', ring.add, {0:1}, {0:1})
    before = dict(ring.counts); prior = sum(x.get('coefficient_additions',0) for x in prop.arithmetic.values())
    prop._charge('restriction', child)
    after = sum(x.get('coefficient_additions',0) for x in prop.arithmetic.values())
    ctx.check(after-prior == ring.counts['coefficient_additions']-before['coefficient_additions'],
              'nested engine charge counted once')
    pc_failure = InjectedFailure('PC callback')
    def fail_refute(r, *args):
        r.add({0:1},{0:1}); raise pc_failure
    with patched(engine.legacy, 'refute', fail_refute):
        error = ctx.rejects(lambda: prop._try_prefix(0,0,'partial'), 'PC callback exception', expected=(InjectedFailure,))
        ctx.check(error is pc_failure, 'PC primary preserved')
    certificate_failure = InjectedFailure('certificate callback')
    with patched(engine.legacy, 'certificate_check', lambda *a: (_ for _ in ()).throw(certificate_failure)):
        error = ctx.rejects(lambda: prop._record_proof(0,0,[{0:1}],[{0:1}],'partial',{}),
                            'certificate callback exception', expected=(InjectedFailure,))
        ctx.check(error is certificate_failure, 'certificate primary preserved')
    guard()
    for name, kwargs, domain, expected in (
        ('native_model_conversion', {'result':True,'model':[0]}, [], ValueError),
        ('domain_validation', {'result':True,'model':[1]}, [[-1]], AssertionError),
        ('native_statistics', {'result':None,'stats_error':InjectedFailure('stats')}, [], InjectedFailure),
        ('teardown', {'result':None,'teardown_error':InjectedFailure('teardown')}, [], InjectedFailure)):
        receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control': name})
        fake = FakeNative(**kwargs)
        error = ctx.rejects(lambda: engine.solve(legacy.CountedRing(1,5),[],domain,1,LIMITS,'model_only',[0,1],
                                attempt=receipt, solver_factory=lambda **k:fake), name, expected=(expected,))
        ctx.check(fake.deleted and hasattr(error,'partial_transcript'), name+' final partial transcript')
        receipt.seal('failed', reason='fixed injected failure')
    # A model conversion primary wins over both failed statistics and teardown.
    receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control':'secondary_failures'})
    first = InjectedFailure('model accessor primary'); secondary = InjectedFailure('teardown secondary')
    fake = FakeNative(result=True, teardown_error=secondary)
    def bad_model():
        fake.stats_error = InjectedFailure('final stats secondary')
        raise first
    fake.get_model = bad_model
    error = ctx.rejects(lambda:engine.solve(legacy.CountedRing(1,5),[],[],1,LIMITS,'model_only',[0,1],
                     attempt=receipt,solver_factory=lambda **k:fake), 'native secondary ordering', expected=(InjectedFailure,))
    ctx.check(error is first and len(error.secondary_errors) >= 2, 'original native exception wins secondary errors')
    ctx.check(error.partial_transcript['native_stat_availability']['availability']=='unknown', 'unavailable stats explicitly unknown')
    receipt.seal('failed')
    receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control':'limited_response'})
    limited = engine.solve(legacy.CountedRing(1,5),[],[],1,LIMITS,'model_only',[0,1],
                           attempt=receipt,solver_factory=lambda **k:FakeNative())
    ctx.check(limited['status']=='censored' and limited['stop_reason']=='native_limit', 'native limit remains censored')
    receipt.seal('censored')
    checkpoint_error = InjectedFailure('checkpoint writer')
    calls = []
    def checkpoint(answer):
        calls.append(deepcopy(answer)); raise checkpoint_error
    error = ctx.rejects(lambda:engine.solve(legacy.CountedRing(1,5),[],[],1,LIMITS,'model_only',[0,1],checkpoint,
                solver_factory=lambda **k:FakeNative()), 'checkpoint callback failure', expected=(InjectedFailure,))
    ctx.check(error is checkpoint_error and len(calls)>=1, 'checkpoint primary retained')
    c = transform.composition(); C = c.compiler()
    targets = (
        ('transform_authentication', transport, 'authenticate_transform',
         lambda receipt:transport.decode_and_check_original(document,bits,descriptor,'k2_addrow_A0',attempt=receipt)),
        ('original_authentication', c, 'authenticate_chart',
         lambda receipt:transport.decode_and_check_original(document,bits,descriptor,'k2_addrow_A0',attempt=receipt)),
        ('range_decoding', C, 'decode_assignment',
         lambda receipt:transport.decode_and_check_original(document,bits,descriptor,'k2_addrow_A0',attempt=receipt)),
        ('aggregate_residuals', c, '_evaluate',
         lambda receipt:transport.decode_and_check_original(document,bits,descriptor,'k2_addrow_A0',attempt=receipt)),
        ('signed_reconstruction', c, '_recover',
         lambda receipt:transport.decode_and_check_original(document,bits,descriptor,'k2_addrow_A0',attempt=receipt)),
        ('final_transcript', C, 'complete_transcript',
         lambda receipt:chart_solver.verify_chart_answer(document,descriptor,'k2_addrow_A0',
                        {'status':'censored','models':[bits],'learned':[]},attempt=receipt)))
    for name, obj, attr, operation in targets:
        failure = InjectedFailure(name)
        def explode(*args, failure=failure, **kwargs):
            raise failure
        receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control':name})
        with patched(obj, attr, explode):
            error = ctx.rejects(lambda: operation(receipt), name+' injection', expected=(InjectedFailure,))
        ctx.check(error is failure, name+' primary retained')
        receipt.seal('failed')
    counts = Counter(); getter = lambda:dict(counts)
    receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control':'nested_receipt'})
    with receipt.phase('outer', getter, counter_scope='test-counter'):
        counts['ops'] += 1
        with receipt.phase('inner', lambda:dict(counts), counter_scope='test-counter'):
            counts['ops'] += 2
    ctx.check(sum(p['counters']['exclusive'].get('ops',0) for p in receipt.state['phases'])==3,
              'distinct getter objects with same scope charged once')
    before = deepcopy(receipt.state['phases']); receipt.checkpoint(); receipt.checkpoint()
    ctx.check(before==receipt.state['phases'], 'repeated checkpoints do not charge again')
    receipt.seal('censored',coverage_complete=True)
    receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control':'unknown_child'})
    with receipt.phase('outer', getter, counter_scope='test-counter'):
        with receipt.phase('unobservable_child'):
            counts['ops'] += 1
    sealed = receipt.seal('censored',coverage_complete=True)
    ctx.check(not sealed['state']['cost_coverage']['complete'], 'unknown child defeats complete cost coverage')
    receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control':'initial_counter_getter'})
    first = InjectedFailure('initial getter')
    def getter_failure():
        raise first
    def enter_bad_phase():
        with receipt.phase('initial', getter_failure):
            raise AssertionError('unreachable body')
    error = ctx.rejects(enter_bad_phase,'initial counter getter receipt',expected=(InjectedFailure,))
    ctx.check(error is first and receipt.state['primary_error'] is not None, 'initial getter primary recorded')
    receipt.seal('failed')
    receipt = attempt_receipt.AttemptReceipt(ctx.directory, {'control':'persistence_serialization'})
    durable = receipt.state['durability']['last_durable_sequence']
    result = receipt.checkpoint(event='nonserializable', invalid=object())
    ctx.check(result is None and receipt.state['durability']['last_durable_sequence']==durable and
              bool(receipt.state['durability']['persistence_errors']), 'serialization failure preserves last durable receipt')
    receipt.state.pop('invalid')
    sealed = receipt.seal('failed')
    ctx.check(not sealed['state']['cost_coverage']['complete'], 'storage failure never complete cost coverage')


def census_controls(ctx):
    equal = census_v2.costs_equal
    ctx.check(equal({}, {'coefficient_additions':0}), 'known absent equals zero')
    ctx.check(equal({'evaluation_term_visits':4},{'evaluation_term_visits':4}), 'matching nonzero counts')
    ctx.check(not equal({'evaluation_term_visits':4},{'evaluation_term_visits':5}), 'nonzero mismatch rejected')
    for raw in ({'unknown':0},{'coefficient_additions':-1},{'coefficient_additions':True},
                {'coefficient_additions':0.0},{'coefficient_additions':'0'}):
        ctx.rejects(lambda raw=raw:census_v2.canonical_costs(raw), 'closed typed counter schema', layer='census_schema')
    legacy = chart_solver._legacy(); saved = []
    for n, polynomial in ((2,{1:1}),):
        pair = []
        for touched in (False,True):
            ring = legacy.CountedRing(n,5)
            if touched:
                ring.restrict(polynomial,{}); ring.eval(polynomial,0); ring.add({}, {})
            if ctx.census_visits+(1<<n)>64:
                raise RuntimeError('tiny census assignment cap')
            ctx.census_visits += 1<<n
            result = census_v2.produce_census({'s':1},ring,[polynomial],[])
            pair.append(result); saved.append(result)
        ctx.check(census_v2.costs_equal(pair[0]['raw']['costs'],pair[1]['raw']['costs']),
                  'fresh and touched ring same canonical census costs', producer=pair[1],fresh=pair[0])
        census_v2.verify_census_record(pair[1],pair[0]['raw'])
        wire = json.loads(json.dumps(pair[1]))
        census_v2.verify_census_record(wire,pair[0]['raw'])
        for key in ('complete_models','projected_models'):
            bad = deepcopy(pair[1]);bad['raw'][key].append(999 if key=='complete_models' else [999,999])
            ctx.rejects(lambda bad=bad:census_v2.verify_census_record(bad,pair[0]['raw']),
                        'census semantic mutation '+key,layer='census_semantics')
        bad = deepcopy(pair[1]);bad['canonical_costs']['coefficient_additions']=False
        ctx.rejects(lambda:census_v2.verify_census_record(bad,pair[0]['raw']), 'canonical vector bool rejected')
    # Frozen semantic routines are directly challenged without a full cohort run.
    ring = legacy.CountedRing(1,5); cell={'s':1}
    bad_certificate={'status':'censored','models':[],'learned':[
        {'depth':0,'prefix':0,'clause':[],'certificate':[{}]}]}
    ctx.rejects(lambda:legacy.verify_search(cell,ring,[{0:1}],[],bad_certificate,[]),
                'learned certificate mutation survives counter adapter',layer='legacy_verify_search')
    bad_model={'status':'censored','models':[1],'learned':[]}
    ctx.rejects(lambda:legacy.verify_search(cell,ring,[{1:1}],[],bad_model,[]),
                'candidate nonroot mutation survives counter adapter',layer='legacy_verify_search')
    # Six additional fresh n=2 census computations exercise the actual
    # extracted original per-arm verifier, including budgets and witnesses.
    spec={'p':5,'a':1,'b':1,'s':1,'target':[0,1]}
    ring,polys,domain=legacy.build(spec,'quartic')
    construction=dict(ring.counts)
    # This bounded fixture never runs search. Its census is a software oracle
    # only, local to the verifier controls; it cannot supply learned clauses.
    fresh_holder=[]
    original_census=census_v2.census
    def counted_census(cell, current_ring, current_polys, current_domain):
        visits=1<<current_ring.n
        if current_ring.n>3 or ctx.census_visits+visits>64:
            raise RuntimeError('tiny verifier census cap')
        ctx.census_visits+=visits
        result=original_census(cell,current_ring,current_polys,current_domain)
        fresh_holder.append(deepcopy(result))
        return result
    # A producer census is one of these six calls; all later verifier attempts
    # use independent newly built rings, not this object.
    producer=counted_census(spec,ring,polys,domain)
    refs=producer['projected_models'];witnesses,reconstruction=legacy.reconstruct(spec,refs)
    arm={'arm':'quartic','construction_cost':construction,'census':producer,
         'search':{'status':'censored','models':[],'learned':[],
                   'costs':{'search_events':{'sat_candidates':0,'pc_calls':0}}},
         'witnesses':witnesses,'reconstruction_cost':reconstruction}
    cfg={'limits':{'sat_candidates':16,'pc_calls':32}}
    with patched(census_v2,'census',counted_census):
        census_v2._verify_arm({'input':spec},arm,cfg,refs,Counter(),[])
        ctx.check(True,'actual per-arm verifier positive control')
        for label,mutate in (
            ('candidate count',lambda a:a['search']['costs']['search_events'].update(sat_candidates=17)),
            ('witness',lambda a:a['witnesses'].append({'tampered':True})),
            ('learned certificate',lambda a:(a['search']['costs']['search_events'].update(sat_candidates=1),
                a['search']['learned'].append({'depth':0,'prefix':0,'clause':[],'certificate':[]}))),
            ('nonzero cost',lambda a:a['census']['costs'].update(boolean_assignments_visited=999))):
            bad=deepcopy(arm);mutate(bad)
            ctx.rejects(lambda bad=bad:census_v2._verify_arm({'input':spec},bad,cfg,refs,Counter(),[]),
                        'actual per-arm verifier rejects '+label,layer='census_v2_legacy_semantics')
    ctx.check(len(saved)+len(fresh_holder)==8 and ctx.census_visits<=64,
              'all eight tiny census calls within fixed total')


def native_smoke(ctx, contract):
    legacy = chart_solver._legacy(); adapter=transform.composition().compiler().adapter()
    for name, polys in (('unconstrained',[]),('zero',[{1:1}]),('contradiction',[{1:1},{1:1,0:4}])):
        receipt=attempt_receipt.AttemptReceipt(ctx.directory,{'control':'native_'+name,'limits':LIMITS})
        answer=bridge_counted.solve(legacy.CountedRing(1,5),polys,[],1,LIMITS,'model_only',[0,1],
                    refuter_mode='baseline',attempt=receipt,solver_factory=ctx.native_factory)
        serialized=[{str(m):v for m,v in p.items()} for p in polys]
        checked=adapter.verify_transcript(5,1,1,serialized,[],answer,aux_bound=None)
        expected={'unconstrained':[0,1],'zero':[0],'contradiction':[]}[name]
        ctx.check(answer['status']=='complete' and sorted(answer['models'])==expected and checked['valid'],
                  'native sentinel '+name, answer=answer,verification=checked)
        receipt.checkpoint(answer,event='sentinel_checked',verification=checked)
        receipt.seal('verified_complete',completion_check_status='accepted_complete')
    c=transform.composition()
    identity=next(f for f in contract['chart_fixtures'] if f['id']=='identity_zero')
    repeated=next(f for f in contract['chart_fixtures'] if f['id']=='finite_two_repeat')
    for arm in c.ARMS:
        desc=_public(identity,arm,'zero');doc=transform.build_transform(desc,'identity')
        output=chart_solver.solve_chart(doc,desc,'identity',LIMITS,'model_only',ctx.directory,
                                        solver_factory=ctx.native_factory)
        ctx.check(output['verification']['verified_complete'],'native identity chart',arm=arm,result=output)
    for arm in c.ARMS:
        for mode in ('identity','k2_addrow_A0'):
            desc=_public(repeated,arm,'constant');doc=transform.build_transform(desc,mode)
            if doc['status']!='applicable':
                ctx.check(False,'fixed repeated chart dependency unmet; no budget reallocation',arm=arm,mode=mode)
            output=chart_solver.solve_chart(doc,desc,mode,LIMITS,'model_only',ctx.directory,
                                            solver_factory=ctx.native_factory)
            ctx.check(output['verification']['accepted'], 'native repeated chart available models/certificates',
                      arm=arm,mode=mode,result=output)
            ctx.check(output['answer']['status'] in ('complete','censored'), 'native status retained',
                      declared=output['answer']['status'])
    ctx.check(ctx.native_instances==12 and ctx.native_calls<=192,'fixed native allocation retained')


def run_suite(directory, *, run_native=False, admission=None):
    """Later execution entry point; requires an explicit source-bound admission.

    This source-stage package supplies no admission token. The future launcher
    owns attempt count (2 producer + 1 independent), publication and dollar caps.
    """
    if not isinstance(admission, dict) or admission.get('execution_authorized') is not True:
        raise PermissionError('separate exact-source execution admission required')
    expected=transform.source_identity()
    if admission.get('source_sha256')!=expected or (type(admission.get('attempt_index')) is not int or admission['attempt_index'] not in (1,2,3)):
        raise PermissionError('exact source and bounded attempt index required')
    if type(run_native) is not bool:
        raise ValueError('explicit native selection')
    ctx=Controls(directory)
    old_handler=signal.getsignal(signal.SIGALRM)
    def timeout(signum, frame):
        raise TimeoutError('600 second software attempt deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,600)
    try:
        original_regressions(ctx)
        contract=source_transport_controls(ctx)
        d,doc,assignment,bits=mutation_controls(ctx,contract)
        failure_controls(ctx,d,doc,assignment,bits)
        census_controls(ctx)
        if run_native:
            native_smoke(ctx,contract)
        result={'schema':'prime-transform-software-controls/v1','records':ctx.records,
                'native_requested':run_native,'native_instances':ctx.native_instances,
                'native_calls':ctx.native_calls,'census_assignments_visited':ctx.census_visits,
                'complete_fixed_suite':run_native,'original_comparison_completed':False}
        ctx.receipt.checkpoint(event='suite_returned',result=result)
        # A software suite is never a mathematical/SAT completion claim.
        result['receipt']=ctx.receipt.seal('complete_unverified',completion_check_status='software_controls_returned')
        return result
    except BaseException as error:
        try:
            ctx.receipt.failure(error,'software_suite')
            if not ctx.receipt.sealed:
                ctx.receipt.seal('failed',reason='preserve partial controls; no retry or fixture replacement')
        except BaseException as secondary:
            ctx.receipt.secondary(secondary,'suite_failure_sealing')
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_handler)

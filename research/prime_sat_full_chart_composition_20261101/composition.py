"""Public complete-chart composition, fixed k<=5.

No SAT search or coefficient census. Prime p>3 is a caller premise. Named
successful-operation counters are separate units, not total workload costs.
"""
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'research/prime_sat_rationality_software_20261031'))
import rationality as rat
import circuits as ir
import quotient as q
import charts, projectors, signed_recovery, check_chart

ARMS = ('uniform_nilpotent_square', 'stratified_slack_with_nilpotent_zero_B',
        'stratified_guard_with_nilpotent_zero_B')
STRATA = ('zero', 'constant', 'linear')


@lru_cache(None)
def compiler():
    path = ROOT/'research/prime_sat_range_corrected_20261101/compiler.py'
    spec = importlib.util.spec_from_file_location('_full_chart_range', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(ok, message):
    if not ok:
        raise ValueError(message)


def descriptor(raw):
    require(type(raw) is dict and set(raw) == {'p','a','b','k','target','t','s','arm','stratum'}, 'public chart descriptor schema')
    d = deepcopy(raw)
    p = d['p']
    require(type(p) is int and p > 3, 'prime p>3 caller premise')
    for name in ('a','b','t'):
        require(type(d[name]) is int and 0 <= d[name] < p, 'canonical public '+name)
    require((4*d['a']**3+27*d['b']**2) % p != 0, 'nonsingular curve')
    require(type(d['k']) is int and 0 <= d['k'] <= 5, 'arity k0..5')
    require(type(d['s']) is int and 0 <= d['s'] < p.bit_length() and (1 << d['s']) < p, 'interval width')
    require(type(d['arm']) is str and d['arm'] in ARMS, 'public rationality arm')
    require(type(d['stratum']) is str and d['stratum'] in STRATA, 'public B stratum')
    if d['target'] is not None:
        T = d['target']
        require(type(T) is list and len(T) == 2 and all(type(x) is int and 0 <= x < p for x in T), 'canonical affine target')
        require((T[1]*T[1]-T[0]**3-d['a']*T[0]-d['b']) % p == 0, 'target on curve')
    return d


class Source:
    def __init__(self, d):
        self.d = d
        self.p = d['p']
        self.inputs = []
        self.auxiliaries = []
        self.equations = []
        self.blocks = {}
        self.counts = Counter(chart_builder_calls=1)

    def const(self, value):
        return ir.constant(value, self.p)

    def var(self, name, projected=False):
        require(name not in self.inputs+self.auxiliaries, 'unique aggregate variable')
        (self.inputs if projected else self.auxiliaries).append(name)
        self.counts['registered_variables'] += 1
        return ir.variable(name)

    def add(self, *values):
        self.counts['sparse_add_calls'] += 1
        self.counts['sparse_add_input_terms'] += sum(len(x) for x in values)
        return ir.add(self.p, *values)

    def scale(self, value, c):
        self.counts['sparse_scale_calls'] += 1
        self.counts['sparse_scale_input_terms'] += len(value)
        return ir.scale(value, c, self.p)

    def mul(self, a, b):
        self.counts['sparse_multiply_calls'] += 1
        self.counts['sparse_multiply_term_pairs'] += len(a)*len(b)
        return ir.mul(a, b, self.p)

    def pmul(self, a, b):
        self.counts['polynomial_multiply_calls'] += 1
        if not a or not b:
            return []
        result = [{} for _ in range(len(a)+len(b)-1)]
        for i, aa in enumerate(a):
            for j, bb in enumerate(b):
                result[i+j] = self.add(result[i+j], self.mul(aa, bb))
        return result

    def eq(self, label, expression):
        require(type(label) is str and label and all(x['label'] != label for x in self.equations), 'unique nonempty aggregate label')
        require(all(len(m) <= 2 for m in expression), 'aggregate arithmetic must remain quadratic')
        row = {'label':label, 'terms':[{'coefficient':c, 'variables':list(m)} for m,c in sorted(expression.items())]}
        self.equations.append(row)
        self.blocks.setdefault(label.split('.')[0], []).append(label)
        self.counts['equations_emitted'] += 1
        self.counts['terms_emitted'] += len(expression)

    def vector_eq(self, label, *signed_vectors):
        size = max((len(v) for c,v in signed_vectors), default=0)
        for i in range(size):
            self.eq(label+'.coefficient'+str(i), self.add(*[
                self.scale(v[i], c) for c,v in signed_vectors if i < len(v)]))

    def product_mod(self, U, L, R, label, final=False):
        k = len(U)-1
        require(k >= 1 and len(L) == len(R) == k, 'aggregate modular product arity')
        P = [{} for _ in range(k)] if final else [self.var(label+'.P'+str(i)) for i in range(k)]
        Q = [self.var(label+'.Q'+str(i)) for i in range(k-1)]
        self.vector_eq(label, (1,self.pmul(L,R)), (-1,P), (-1,self.pmul(U,Q)))
        return P

    def export(self, spec, kind):
        return {'schema':'prime-full-chart-field/v1','p':self.p,
                'curve':{'a':self.d['a'],'b':self.d['b']}, 'k':self.d['k'],
                'inputs':self.inputs[:], 'projection':self.inputs[:],
                'auxiliaries':self.auxiliaries[:], 'equations':deepcopy(self.equations),
                'metadata':{'chart':deepcopy(spec),'rationality_kind':kind,
                            'blocks':[{'name':name,'equations':labels[:]} for name,labels in self.blocks.items()]},
                'construction_counts':dict(self.counts)}


def _pad_symbolic(poly, length):
    return poly + [{} for _ in range(length-len(poly))]


def _power_chain(S, U, N):
    k = len(U)-1
    if k == 1:
        S.eq('interval.Nzero', N[0])
        return
    N2 = S.product_mod(U,N,N,'interval.N2',k == 2)
    if k == 3:
        S.product_mod(U,N2,N,'interval.N3',True)
    elif k >= 4:
        N4 = S.product_mod(U,N2,N2,'interval.N4',k == 4)
        if k == 5:
            S.product_mod(U,N4,N,'interval.N5',True)


def canonical_chart(public_descriptor):
    d = descriptor(public_descriptor)
    p,k = d['p'],d['k']
    curve = {'p':p,'a':d['a'],'b':d['b']}
    spec = charts.chart_spec(curve,k,d['target'])
    if 'basis' in spec:
        spec['basis'] = [list(x) for x in spec['basis']]
    S = Source(d)
    if not spec['possible'] or k == 0:
        if not spec['possible'] or d['stratum'] != 'zero':
            S.eq('special.impossible', S.const(1))
        return S.export(spec,None)
    A = [{} for _ in range(spec['d']//2+1)]
    B = [{} for _ in range(max(1,(spec['d']-3)//2+1))]
    for index,(kind,i,pole) in enumerate(spec['basis']):
        expression = S.const(1) if index == len(spec['basis'])-1 else S.var('chart.'+kind+str(i),True)
        (A if kind == 'A' else B)[i] = expression
    U = [S.var('support.u'+str(i)) for i in range(k)] + [S.const(1)]
    f = [S.const(x) for x in (d['b'],d['a'],0,1)]
    rhs = U if d['target'] is None else S.pmul([S.const(-d['target'][0]),S.const(1)],U)
    S.vector_eq('norm',(1,S.pmul(A,A)),(-1,S.pmul(f,S.pmul(B,B))),(-spec['c'],rhs))
    if d['target'] is not None:
        x,y = d['target']
        S.eq('sign.target',S.add(*[S.scale(v,pow(x,i,p)) for i,v in enumerate(A)],
                                      *[S.scale(v,-y*pow(x,i,p)) for i,v in enumerate(B)]))
    b0,b1 = _pad_symbolic(B,2)[:2]
    if d['stratum'] == 'zero':
        S.eq('stratum.B0zero',b0);S.eq('stratum.B1zero',b1)
    elif d['stratum'] == 'constant':
        S.eq('stratum.B1zero',b1)
        z = S.var('stratum.inverse')
        S.eq('stratum.nonzero',S.add(S.mul(b0,z),S.const(-1)))
    else:
        z = S.var('stratum.inverse')
        S.eq('stratum.nonzero',S.add(S.mul(b1,z),S.const(-1)))
    e = []
    for j in range(d['s']):
        E = [S.var('interval.e'+str(j)+'.'+str(i)) for i in range(k)]
        Q = [S.var('interval.idem'+str(j)+'.Q'+str(i)) for i in range(k-1)]
        S.vector_eq('interval.idem'+str(j),(1,S.pmul(E,E)),(-1,E),(-1,S.pmul(U,Q)))
        e.append(E)
    N = [{} for _ in range(k)]
    if k == 1:
        N[0] = S.scale(U[0],-1)
    else:
        N[1] = S.const(1)
    N[0] = S.add(N[0],S.const(-d['t']))
    for j,E in enumerate(e):
        N = [S.add(n,S.scale(v,-(1 << j))) for n,v in zip(N,E)]
    _power_chain(S,U,N)
    if d['arm'] == ARMS[0] or d['stratum'] == 'zero':
        kind,degree = 'nilpotent',k
        binding = {'u'+str(i):U[i] for i in range(k)}
    elif d['stratum'] == 'constant':
        kind,degree = 'constant',None
        binding = {'b0':b0}
    else:
        kind,degree = ('guard' if d['arm'] == ARMS[2] else 'slack'),None
        binding = {'A'+str(i):v for i,v in enumerate(_pad_symbolic(A,4))}
        binding.update(b0=b0,b1=b1)
    template = compiler().authenticated().canonical_circuit(
        {'p':p,'curve':{'a':d['a'],'b':d['b']},'kind':kind,'k':degree,'projection':list(binding)})
    S.counts['canonical_component_builder_calls'] += 1
    for name in template['auxiliaries']:
        binding[name] = S.var('rationality.'+name)
    for eq in template['equations']:
        terms = []
        for term in eq['terms']:
            v = S.const(term['coefficient'])
            for name in term['variables']:
                v = S.mul(v,binding[name])
            terms.append(v)
        S.eq('rationality.'+eq['label'],S.add(*terms))
    return S.export(spec,kind)


def compile_chart(public_descriptor):
    d = descriptor(public_descriptor)
    source = canonical_chart(d)
    C = compiler();p = d['p'];w = (p-1).bit_length();h = (p-1).bit_count()-1
    names = source['projection']+source['auxiliaries']
    m = w*len(source['projection']);values = w*len(names);n = values+h*len(names)
    blocks = [{'name':name,'value_bits':list(range(i*w,(i+1)*w)),
               'state_bits':list(range(values+i*h,values+(i+1)*h))} for i,name in enumerate(names)]
    arithmetic,labels,costs = C.substitute_equations(source['equations'],{b['name']:b['value_bits'] for b in blocks},p,n)
    rd = {'p':p,'n':n,'projected_bits':m,'arithmetic':arithmetic,'blocks':blocks}
    compiled = C.compile_range(rd)
    return {'schema':'prime-full-chart-compiled/v1','descriptor':d,'source':source,
            'source_sha256':C.digest(source),'arithmetic_labels':labels,
            'range_document':compiled,'construction_costs':{'chart':deepcopy(source['construction_counts']),
                    'substitution':costs,'range':deepcopy(compiled['construction_costs'])}}


def authenticate_chart(document, trusted_descriptor):
    expected = compile_chart(trusted_descriptor);counts = Counter()
    require(compiler().same(document,expected,counts),'canonical complete-chart content mismatch')
    return {'typed_comparison':dict(counts),'construction':deepcopy(expected['construction_costs'])}


def _evaluate(source, assignment):
    names = source['inputs']+source['auxiliaries'];p = source['p']
    require(type(assignment) is dict and set(assignment) == set(names), 'complete aggregate assignment')
    for name in names:
        require(type(assignment[name]) is int and 0 <= assignment[name] < p, 'canonical aggregate value '+name)
    parsed = [];labels = set();counts = Counter(assignment_values_checked=len(names))
    for row in source['equations']:
        require(type(row) is dict and set(row) == {'label','terms'}, 'aggregate row schema')
        label = row['label'];require(type(label) is str and label and label not in labels, 'aggregate row label')
        labels.add(label);require(type(row['terms']) is list, 'aggregate terms list')
        terms = [];monomials = []
        for term in row['terms']:
            require(type(term) is dict and set(term) == {'coefficient','variables'}, 'aggregate term schema')
            c,v = term['coefficient'],term['variables']
            require(type(c) is int and 0 < c < p, 'nonzero canonical term coefficient')
            require(type(v) is list and all(type(n) is str and n in assignment for n in v), 'declared term variables')
            require(len(v) <= 2 and v == sorted(v), 'canonical quadratic term')
            require(tuple(v) not in monomials, 'unique aggregate monomial')
            monomials.append(tuple(v));terms.append((c,v))
        require(monomials == sorted(monomials), 'canonical monomial order')
        parsed.append((label,terms))
    residuals = []
    for label,terms in parsed:
        total = 0
        for c,v in terms:
            value = c
            for name in v:
                value = value*assignment[name] % p;counts['field_multiplications'] += 1
            total = (total+value) % p;counts['field_additions'] += 1
        residuals.append({'label':label,'value':total})
    counts['equations_evaluated'] = len(residuals)
    return {'status':'valid' if all(r['value'] == 0 for r in residuals) else 'invalid',
            'stage':'arithmetic','residuals':residuals,'costs':dict(counts)}


def check_chart_assignment(document, assignment, trusted_descriptor):
    try:
        auth = authenticate_chart(document,trusted_descriptor)
    except (ValueError,KeyError,TypeError,IndexError) as error:
        return {'status':'invalid','stage':'authentication','obligation':str(error)}
    try:
        result = _evaluate(document['source'],assignment)
    except (ValueError,KeyError,TypeError,IndexError) as error:
        return {'status':'invalid','stage':'assignment','obligation':str(error),'authentication_costs':auth}
    result['authentication_costs'] = auth
    return result


def _qdelta(before):
    return {name:value-before.get(name,0) for name,value in q.EVENTS.items() if value != before.get(name,0)}


def construct_assignment(public_descriptor, checked_chart, recovered_points, optional_beta=None):
    d = descriptor(public_descriptor);source = canonical_chart(d);p,k = d['p'],d['k']
    w = deepcopy(checked_chart);before = dict(q.EVENTS)
    require(w['curve'] == {'p':p,'a':d['a'],'b':d['b']} and w['interval'] == {'t':d['t'],'s':d['s']}, 'supplied public curve/interval binding')
    require(compiler().same(w['target'],d['target'],Counter()) and type(w['k']) is int and w['k'] == k, 'supplied target/arity binding')
    require(check_chart.check_chart(w,recovered_points)['status'] == 'valid', 'original signed chart check')
    B = w['B'];actual = 'zero' if B == [0] else 'constant' if len(B) == 1 else 'linear'
    require(actual == d['stratum'],'supplied witness belongs to declared stratum')
    signed_cost = _qdelta(before);before = dict(q.EVENTS)
    assignment = {}
    if k:
        spec = source['metadata']['chart']
        for kind,i,pole in spec['basis'][:-1]:
            poly = w[kind];assignment['chart.'+kind+str(i)] = poly[i] if i < len(poly) else 0
        U = w['U']['coeffs']
        assignment.update({'support.u'+str(i):U[i] for i in range(k)})
        if actual != 'zero':
            assignment['stratum.inverse'] = q.inv(B[0] if actual == 'constant' else B[1],p)
        for j,E in enumerate(w['e']):
            for i in range(k):
                assignment['interval.e'+str(j)+'.'+str(i)] = E[i] if i < len(E) else 0
            Q = q.exact(q.sub(q.mul(E,E,p),E,p),U,p)
            for i in range(k-1):
                assignment['interval.idem'+str(j)+'.Q'+str(i)] = Q[i] if i < len(Q) else 0
        N = q.rem([(-d['t'])%p,1],U,p)
        for j,E in enumerate(w['e']):
            N = q.sub(N,q.scale(E,1 << j,p),p)
        def product(L,R,label,final=False):
            quotient,remainder = q.divrem(q.mul(L,R,p),U,p)
            for i in range(k-1):
                assignment[label+'.Q'+str(i)] = quotient[i] if i < len(quotient) else 0
            if not final:
                for i in range(k):
                    assignment[label+'.P'+str(i)] = remainder[i] if i < len(remainder) else 0
            return remainder
        if k >= 2:
            N2 = product(N,N,'interval.N2',k == 2)
            if k == 3:
                product(N2,N,'interval.N3',True)
            elif k >= 4:
                N4 = product(N2,N2,'interval.N4',k == 4)
                if k == 5:
                    product(N4,N,'interval.N5',True)
        candidate = rat.construct_auxiliaries_from_checked_chart(w,recovered_points,d['arm'],optional_beta)
        block = candidate['block']
        assignment.update({'rationality.'+name:block['assignment'][name] for name in block['circuit']['auxiliaries']})
    aux_cost = _qdelta(before)
    result = _evaluate(source,assignment)
    require(result['status'] == 'valid','constructed aggregate witness must satisfy every row')
    return {'assignment':assignment,'costs':{'source_construction':source['construction_counts'],
            'original_signed_check':signed_cost,'auxiliary_construction':aux_cost,'aggregate_residuals':result['costs']}}


def encode_chart_counted(document, assignment, trusted_descriptor):
    auth = authenticate_chart(document,trusted_descriptor)
    rd = document['range_document']
    result = compiler().encode_assignment_counted(rd,assignment,rd['descriptor'],'range')
    return {'bits':result['bits'],'costs':{'whole_chart_authentication':auth,'range_encoding':result['costs']}}


def _recover(document, assignment):
    d = document['descriptor'];source = document['source'];p,k = d['p'],d['k'];spec = source['metadata']['chart']
    require(spec['possible'],'impossible pole chart cannot decode as a model')
    if not k:
        A,B,U,e,roots = [1],[0],[1],[],[]
    else:
        A = [0]*(spec['d']//2+1);B = [0]*max(1,(spec['d']-3)//2+1)
        for index,(kind,i,pole) in enumerate(spec['basis']):
            (A if kind == 'A' else B)[i] = 1 if index == len(spec['basis'])-1 else assignment['chart.'+kind+str(i)]
        A,B = q.trim(A),q.trim(B)
        U = [assignment['support.u'+str(i)] for i in range(k)]+[1]
        e = [q.trim([assignment['interval.e'+str(j)+'.'+str(i)] for i in range(k)]) for j in range(d['s'])]
        roots = []
    curve = {'p':p,'a':d['a'],'b':d['b']};modulus = {'p':p,'coeffs':U}
    factors = projectors.recover_interval_factors(modulus,d['t'],d['s'],e)
    kind = source['metadata']['rationality_kind']
    if k and kind == 'nilpotent':
        C = [assignment['rationality.C'+str(i)] for i in range(k)]
        roots = [[x,q.evaluate(C,x,p)] for x,m in factors['factors']]
    elif k and kind in ('guard','slack'):
        alpha = assignment['rationality.alpha']
        if assignment['rationality.c'] == 0:
            roots = [[alpha,assignment['rationality.beta']]]
    w = {'curve':curve,'interval':{'t':d['t'],'s':d['s']},'k':k,'target':deepcopy(d['target']),
         'A':A,'B':B,'U':modulus,'e':e,'root_lifts':roots}
    recovered = signed_recovery.recover_signed_divisor(curve,d['target'],A,B,modulus,factors,roots)
    require(check_chart.check_chart(w,recovered)['status'] == 'valid','unchanged independent signed chart check')
    return w,recovered


def decode_chart_counted(document, bits, trusted_descriptor):
    auth = authenticate_chart(document,trusted_descriptor);rd = document['range_document']
    decoded = compiler().decode_assignment(rd,bits,rd['descriptor'],'range')
    residuals = _evaluate(document['source'],decoded['assignment'])
    require(residuals['status'] == 'valid','decoded arithmetic is not a chart root')
    before = dict(q.EVENTS);w,recovered = _recover(document,decoded['assignment']);recovery = _qdelta(before)
    return {'assignment':decoded['assignment'],'chart':w,'recovered':recovered,
            'projection':[decoded['assignment'][name] for name in document['source']['projection']],
            'costs':{'whole_chart_authentication':auth,'range_decoding':decoded['costs'],
                     'aggregate_residuals':residuals['costs'],'signed_recovery_and_check':recovery}}


def complete_chart_transcript(document, trusted_descriptor, answer):
    auth = authenticate_chart(document,trusted_descriptor);rd = document['range_document']
    result = compiler().complete_transcript(rd,rd['descriptor'],answer,'range',rd['bootstrap_cnf'])
    decoded = [];failures = []
    if type(answer) is dict and type(answer.get('models')) is list:
        for index,bits in enumerate(answer['models']):
            try:
                decoded.append({'model_index':index,'decoded':decode_chart_counted(document,bits,trusted_descriptor)})
            except (ValueError,q.ObligationError,KeyError,TypeError,IndexError) as error:
                failures.append({'model_index':index,'type':type(error).__name__,'message':str(error)})
    return {'completion':result,'decoded_models':decoded,'model_failures':failures,
            'declared_status':answer.get('status') if type(answer) is dict else None,
            'accepted':bool(result['checker_result'] and result['checker_result'].get('valid') and not failures),
            'costs':{'whole_chart_authentication':auth,'transcript':result['costs'],
                     'models':[x['decoded']['costs'] for x in decoded]},
            'failure_cost_boundary':'Failed model decoding is retained but its interrupted-operation counts require outer workload instrumentation.'}

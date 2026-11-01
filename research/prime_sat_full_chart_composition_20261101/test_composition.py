"""Fixed checks. No SAT calls or assignment-space enumeration."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import json
import composition as c

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT/'coordination/prime_sat_full_chart_composition_20261101/fixed-software-contract.json'
records = []
groups = []


def check(actual, expected=True, label='fixed assertion'):
    records.append({'label':label,'expected':expected,'actual':actual})
    if type(actual) is not type(expected) or actual != expected:
        raise AssertionError(label+': '+repr(actual)+' != '+repr(expected))


def rejects(fn,label):
    try:
        fn()
    except (ValueError, c.q.ObligationError):
        check(True,True,label)
    else:
        check(False,True,label)


def field_values(source, assignment):
    result = []
    for row in source['equations']:
        value = 0
        for term in row['terms']:
            product = term['coefficient']
            for name in term['variables']:
                product *= assignment[name]
            value += product
        result.append(value % source['p'])
    return result


def bit_values(document,bits):
    rd = document['range_document']
    return [sum(coefficient for mask,coefficient in poly.items() if (int(mask) & bits) == int(mask)) % rd['p']
            for poly in rd['polynomials']]


def public(f,arm,stratum):
    return {key:deepcopy(f[key]) for key in ('p','a','b','target','t','s')} | {'k':len(f['points']),'arm':arm,'stratum':stratum}


def original(f):
    curve = {key:f[key] for key in ('p','a','b')}
    w = c.charts.construct_from_signed_multiset(curve,{'t':f['t'],'s':f['s']},f['points'],f['target'])
    points = sorted(deepcopy(f['points']))+[None]*(5-len(f['points']))
    check(c.check_chart.check_chart(w,points)['status'],'valid',f['id']+': original signed witness')
    return w,points


def component_check(block):
    source,assignment = block['circuit'],block['assignment']
    expected = {key:deepcopy(source[key]) for key in ('p','curve','kind','k','projection')}
    expected['inputs'] = {name:assignment[name] for name in source['inputs']}
    return c.compiler().authenticated().evaluator.check_assignment(source,assignment,expected)


def run():
    contract = json.loads(CONTRACT.read_text())
    fixtures = contract['chart_fixtures']
    check(len(fixtures),15,'entire chart cohort')
    f = next(x for x in fixtures if x['id'] == 'finite_two_repeat')
    d = public(f,c.ARMS[0],'constant')
    for name,value in [('p',True),('a',True),('b',-1),('k',6),('k',True),('t',5),('s',True),('s',3),('arm','bad'),('stratum','bad'),('target',[0,0]),('target',(0,1))]:
        bad = deepcopy(d);bad[name] = value
        rejects(lambda bad=bad:c.canonical_chart(bad),'malformed public '+name+repr(value))
    bad = deepcopy(d);bad['witness'] = {};rejects(lambda:c.canonical_chart(bad),'no witness descriptor key')
    bad = deepcopy(d);bad.update(a=0,b=0);rejects(lambda:c.canonical_chart(bad),'singular curve')
    groups.append('public_descriptor')

    valid = [];documents = [];impossible = []
    for fixture in fixtures:
        impossible_fixture = 'impossible' in fixture['id']
        if impossible_fixture:
            rejects(lambda fixture=fixture:original(fixture),'impossible original '+fixture['id'])
            witness,points = None,None
        else:
            witness,points = original(fixture)
        for arm in c.ARMS:
            for stratum in c.STRATA:
                desc = public(fixture,arm,stratum);doc = c.compile_chart(desc);source = doc['source']
                documents.append((fixture,desc,doc))
                check(c.compiler().digest(source),doc['source_sha256'],'bound source '+fixture['id']+arm+stratum)
                names = source['inputs']+source['auxiliaries']
                check(len(names),len(set(names)),'injective whole-chart names')
                check(source['projection'],source['inputs'],'ordered coefficient projection')
                check(all(len(term['variables']) <= 2 for row in source['equations'] for term in row['terms']),True,'full aggregate quadratic')
                check(len({r['label'] for r in source['equations']}),len(source['equations']),'unique row labels')
                k,s = desc['k'],desc['s']
                is_regular = source['metadata']['chart']['possible'] and k > 0
                interval_vars = sum(name.startswith('interval.') for name in source['auxiliaries'])
                interval_eqs = sum(row['label'].startswith('interval.') for row in source['equations'])
                if is_regular:
                    ell = {1:0,2:1,3:2,4:2,5:3}[k]
                    expected_vars = s if k == 1 else s*(2*k-1)+(ell-1)*(2*k-1)+(k-1)
                    expected_eqs = s+1 if k == 1 else (s+ell)*(2*k-1)
                    check(interval_vars,expected_vars,'independent interval variable formula')
                    check(interval_eqs,expected_eqs,'independent interval equation formula')
                    expected_projection = ['chart.'+kind+str(i) for kind,i,pole in c.charts.basis(k+int(desc['target'] is not None))[:-1]]
                    check(source['projection'],expected_projection,'pole-basis normalized projection')
                    check([n for n in source['auxiliaries'] if n.startswith('support.')],['support.u'+str(i) for i in range(k)],'lifted U retained')
                if impossible_fixture or (k == 0 and stratum != 'zero'):
                    check(source['projection'],[],'impossible special empty projection')
                    check(doc['range_document']['polynomials'],[{'0':1}],'literal impossible source')
                    impossible.append((desc,doc))
                    continue
                actual = 'zero' if witness['B'] == [0] else 'constant' if len(witness['B']) == 1 else 'linear'
                if actual != stratum:
                    rejects(lambda desc=desc,witness=witness,points=points:c.construct_assignment(desc,witness,points),'wrong supplied stratum; not a completeness proof')
                    continue
                built = c.construct_assignment(desc,witness,points)
                assignment = built['assignment']
                check(field_values(source,assignment),[0]*len(source['equations']),'independent field residuals')
                enc = c.encode_chart_counted(doc,assignment,desc)
                values = bit_values(doc,enc['bits'])
                check(values,[0]*len(values),'independent bit residuals')
                dec = c.decode_chart_counted(doc,enc['bits'],desc)
                check(dec['assignment'],assignment,'all field values roundtrip')
                check(dec['recovered'],points,'exact signed multiplicities roundtrip')
                check(c.check_chart.check_chart(dec['chart'],points)['status'],'valid','unchanged signed checker')
                check(c.compiler().digest(doc),c.compiler().digest(c.compile_chart(desc)),'canonical source independent of witness helper')
                valid.append((fixture,desc,doc,built,enc,dec))
                if k:
                    # U0 occurs linearly in the norm with a public known coefficient.
                    changed = dict(assignment);changed['support.u0'] = (changed['support.u0']+1) % desc['p']
                    expected_norm = [0]*sum(row['label'].startswith('norm.') for row in source['equations'])
                    sign = source['metadata']['chart']['c']
                    if desc['target'] is None:
                        expected_norm[0] = -sign % desc['p']
                    else:
                        expected_norm[0] = sign*desc['target'][0] % desc['p'];expected_norm[1] = -sign % desc['p']
                    residuals = field_values(source,changed)
                    check([v for row,v in zip(source['equations'],residuals) if row['label'].startswith('norm.')],expected_norm,'literal U0 norm perturbation')
                    changed_bits = c.encode_chart_counted(doc,changed,desc)['bits']
                    check(bit_values(doc,changed_bits)[:len(residuals)],residuals,'nonroot field/bit residual identity')
                    rejects(lambda:c.decode_chart_counted(doc,changed_bits,desc),'nonroot decode invalidates result')
                    if desc['target'] is not None:
                        changed = dict(assignment);changed['chart.A0'] = (changed['chart.A0']+1) % desc['p']
                        residuals = field_values(source,changed)
                        check([v for row,v in zip(source['equations'],residuals) if row['label']=='sign.target'],[1],'target sign coefficient one')
    check(len(documents),135,'all fifteen times three arms times three strata')
    check(len(valid),39,'thirteen valid chart fixtures times three arms')
    groups.extend(['canonical_source','normalization','public_strata','norm_and_sign','interval_idempotents',
               'interval_nilpotence','interval_counts','rationality_arms','block_renaming','full_degree',
               'fixed_cohort','known_witness_roundtrip'])

    # Same raw coefficient projection only within the declared chart family.
    for fixture in fixtures:
        names = [doc['source']['projection'] for f,desc,doc in documents if f['id']==fixture['id']]
        check(all(x==names[0] for x in names),True,'common coefficient projection across arms/strata')
    groups.append('projection_boundary')

    identity = next(row for row in valid if row[0]['id']=='identity_zero')
    _,di,doc,_,enc,_ = identity
    check(enc['bits'],0,'identity has empty assignment')
    completed = c.complete_chart_transcript(doc,di,{'status':'complete','models':[0],'learned':[]})
    check(completed['accepted'],True,'identity complete projected singleton certificate')
    check(completed['decoded_models'][0]['decoded']['recovered'],[None]*5,'identity decoded padding')
    absent = c.complete_chart_transcript(doc,di,{'status':'complete','models':[],'learned':[]})
    check(absent['accepted'],False,'identity missing model leaves gap')
    duplicate = c.complete_chart_transcript(doc,di,{'status':'complete','models':[0,0],'learned':[]})
    check(duplicate['accepted'],False,'duplicate projection rejected')
    for desc,doc in impossible:
        raw = {'status':'complete','models':[],'learned':[{'depth':0,'prefix':0,'clause':[],'certificate':[{'0':1}]}]}
        result = c.complete_chart_transcript(doc,desc,raw)
        check(result['accepted'],True,'literal impossible proof')
        check(result['completion']['original'],raw,'original literal proof retained')
        bad = deepcopy(raw);bad['learned'].append({'depth':0,'prefix':0,'clause':[],'certificate':[]})
        rejected = c.complete_chart_transcript(doc,desc,bad)
        check(rejected['accepted'],False,'malformed shadowed original proof retained and rejected')
        check(rejected['completion']['original'],bad,'invalid original record not discarded')
    groups.append('special_charts')

    f1 = contract['signed_recovery_regressions'][0]
    points = [row['point'] for row in f1['expected_divisor'] for _ in range(row['multiplicity'])]
    literal = {'id':'F1','p':f1['p'],'a':f1['a'],'b':f1['b'],'t':0,'s':0,'points':points,'target':None}
    w,points = original(literal);desc = public(literal,c.ARMS[2],'linear');doc = c.compile_chart(desc)
    projections = [];f1_models = []
    for beta in f1['guard_beta_values']:
        built = c.construct_assignment(desc,w,points,beta)
        check(built['assignment']['rationality.beta'],beta,'both literal beta signs retained')
        encoded = c.encode_chart_counted(doc,built['assignment'],desc)
        decoded = c.decode_chart_counted(doc,encoded['bits'],desc)
        check(decoded['recovered'],points,'unbalanced F1 signed divisor')
        projections.append(decoded['projection']);f1_models.append(encoded['bits'])
        wrong = [[0,1]]+[[0,4]]*4
        check(c.check_chart.check_chart(decoded['chart'],wrong)['status'],'invalid','reject swapped F1 multiplicities')
        balanced = [[0,1]]*2+[[0,4]]*2+[None]
        check(c.check_chart.check_chart(decoded['chart'],balanced)['status'],'invalid','reject balanced F1 substitute')
    check(projections[0],projections[1],'both beta signs share normalized coefficient projection')
    check(f1_models[0] != f1_models[1],True,'distinct auxiliary witnesses for F1 beta signs')
    duplicate = c.complete_chart_transcript(doc,desc,{'status':'censored','models':f1_models,'learned':[]})
    check(duplicate['accepted'],False,'different auxiliary models with same coefficient projection rejected')
    check(duplicate['completion']['original']['models'],f1_models,'both original auxiliary witnesses retained')
    check(len(duplicate['decoded_models']),2,'both signed reconstructions retained despite duplicate projection')
    groups.append('F1_regression')

    for fixture in contract['nilpotent_fixtures']:
        block = c.rat.nilpotent_square_block(len(fixture['U'])-1,fixture['p'],fixture['a'],fixture['b'],fixture['U'],fixture['C'])
        result = component_check(block)
        check(result['status']=='valid',fixture['valid'],'retained nilpotent '+fixture['id'])
    for fixture in contract['guard_fixtures']:
        block = c.rat.linear_B_square_block(fixture['p'],1,fixture['F'],'guard',[fixture['c']],[0,1],fixture['beta'])
        for name in ('e','u','beta'):
            block['assignment'][name] = fixture[name]
        check(component_check(block)['status']=='valid',fixture['valid'],'retained guard '+fixture['id'])
    groups.append('nilpotent_and_guard_controls')

    fixture,desc,doc,built,enc,dec = next(row for row in valid if row[0]['id']=='finite_five_characteristic5' and row[1]['arm']==c.ARMS[0])
    for prefix in ('norm.','sign.','interval.','rationality.'):
        bad = deepcopy(doc)
        row = next(r for r in bad['source']['equations'] if r['label'].startswith(prefix))
        row['terms'].append({'coefficient':1,'variables':[]})
        rejects(lambda bad=bad:c.authenticate_chart(bad,desc),'source block mutation '+prefix)
    for mutate in (
        lambda x:x['source']['auxiliaries'].reverse(),
        lambda x:x['source']['projection'].reverse(),
        lambda x:x['source']['metadata']['blocks'].reverse(),
        lambda x:x['range_document']['polynomials'].append({'0':1}),
        lambda x:x['range_document']['blocks'][0]['value_bits'].reverse(),
        lambda x:x['source']['equations'].append({'label':'late','terms':[{'coefficient':True,'variables':[]}]}),
        lambda x:x['source']['equations'][-1].update(label=''),
        lambda x:x['descriptor'].update(stratum='zero'),
    ):
        bad = deepcopy(doc);mutate(bad)
        rejects(lambda bad=bad:c.authenticate_chart(bad,desc),'whole chart late/content mutation')
    bad_assignment = dict(built['assignment']);bad_assignment[next(iter(bad_assignment))] = True
    check(c.check_chart_assignment(doc,bad_assignment,desc)['status'],'invalid','bool field alias rejected')
    bad_assignment = dict(built['assignment']);bad_assignment['extra'] = 0
    check(c.check_chart_assignment(doc,bad_assignment,desc)['status'],'invalid','extra assignment rejected')
    bad_assignment = dict(built['assignment']);bad_assignment[next(iter(bad_assignment))] = desc['p']
    rejects(lambda:c.encode_chart_counted(doc,bad_assignment,desc),'noncanonical field value rejected')
    groups.extend(['authentication','mutation_negatives'])

    # Count full-chart reconstruction independently at the public boundary.
    calls = []
    original_builder = c.canonical_chart
    def observed(d):
        calls.append(deepcopy(d))
        return original_builder(d)
    c.canonical_chart = observed
    try:
        encoded = c.encode_chart_counted(doc,built['assignment'],desc)
        check(len(calls),1,'encode one whole-chart reconstruction')
        calls.clear()
        decoded = c.decode_chart_counted(doc,encoded['bits'],desc)
        check(len(calls),1,'decode one whole-chart reconstruction')
    finally:
        c.canonical_chart = original_builder
    check(encoded['costs']['whole_chart_authentication']['construction']['chart']['chart_builder_calls'],1,'source phase build receipt')
    check(encoded['costs']['range_encoding']['authentication']['construction'],doc['range_document']['construction_costs'],'additional range rebuild charged')
    names = doc['source']['inputs']+doc['source']['auxiliaries'];wbits=(desc['p']-1).bit_length()
    check(encoded['costs']['range_encoding']['reconstruction']['value_bit_writes'],wbits*len(names),'literal value write count')
    check(decoded['costs']['range_decoding']['decoding']['value_bit_reads'],wbits*len(names),'literal value read count')
    retained = deepcopy(doc);encoded['costs']['whole_chart_authentication']['construction']['chart']['chart_builder_calls']=99
    check(c.compiler().digest(doc),c.compiler().digest(retained),'receipt mutation does not alter document')
    check(c.encode_chart_counted(doc,built['assignment'],desc)['costs']['whole_chart_authentication']['construction']['chart']['chart_builder_calls'],1,'receipt mutation does not leak')
    groups.append('costs')

    raw = {'status':'censored','models':[enc['bits']],'learned':[]}
    result = c.complete_chart_transcript(doc,desc,raw)
    check(result['accepted'],True,'valid censored transcript with known model')
    check(result['declared_status'],'censored','censoring preserved')
    check(result['completion']['augmented']['status'],'censored','no completeness promotion')
    check(result['completion']['original'],raw,'all raw transcript content retained')
    incomplete = c.complete_chart_transcript(doc,desc,{'status':'complete','models':[enc['bits']],'learned':[]})
    check(incomplete['accepted'],False,'unproved projected complement remains uncovered')
    f7 = next(row for row in valid if row[0]['p']==7 and row[0]['id']=='finite_two_torsion')
    _,d7,doc7,b7,e7,_ = f7
    state = doc7['range_document']['blocks'][0]['state_bits'][0]
    rejects(lambda:c.decode_chart_counted(doc7,e7['bits'] ^ (1 << state),d7),'wrong recurrence state rejected')
    changed = dict(built['assignment']);changed['support.u0'] = (changed['support.u0']+1)%desc['p']
    nonroot = c.encode_chart_counted(doc,changed,desc)['bits']
    failed = c.complete_chart_transcript(doc,desc,{'status':'censored','models':[nonroot],'learned':[]})
    check(failed['accepted'],False,'failed model invalidates result')
    check(len(failed['model_failures']),1,'failed model retained explicitly')
    check(failed['completion']['original']['models'],[nonroot],'failed original model not silently dropped')
    groups.append('certificate_preservation')
    # Custody is verified by the external frozen-source/checkpoint harness.
    check(CONTRACT.is_file(),True,'prospective canonical contract present')
    check(sorted(groups),sorted(set(x['id'] for x in contract['fixed_checks'])-{'custody'}),'every substantive fixed group covered')
    groups.append('custody')
    print(json.dumps({'schema':'prime-full-chart-fixed-suite/v1','groups':groups,'assertions':len(records),
                      'records':records,'chart_documents':len(documents),'valid_witness_roundtrips':len(valid),
                      'custody_scope':'External harness must bind sources, claim, checkpoint and all attempts.',
                      'scientific_runs':0,'solver_calls':0,'census':False},sort_keys=True))


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        print(json.dumps({'status':'failed','groups_completed':groups,'records':records,'error_type':type(error).__name__,'error':str(error)},sort_keys=True))
        raise

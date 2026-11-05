"""Fixed literal obligations only. No assignment enumeration or SAT calls."""
from copy import deepcopy
import json
from pathlib import Path
import compiler as c

checks = 0
passed = []


def check(value, message='fixed assertion'):
    global checks
    checks += 1
    if not value:
        raise AssertionError(message)


def rejects(fn):
    try:
        fn()
    except ValueError:
        check(True)
    else:
        check(False, 'expected rejection')


def descriptor(p=7, n=4, m=3, blocks=None):
    return {'p': p, 'n': n, 'projected_bits': m, 'arithmetic': [], 'blocks': blocks if blocks is not None else [{'name': 'x', 'value_bits': [0,1,2], 'state_bits': [3] if p == 7 else []}]}


def public(p, kind, k=None, a=0, b=1):
    names = ['u'+str(i) for i in range(k)] if kind == 'nilpotent' else (['b0'] if kind == 'constant' else ['A'+str(i) for i in range(4)]+['b0','b1'])
    return {'p':p,'curve':{'a':a,'b':b},'kind':kind,'k':k,'projection':names}


def verify(doc, answer, domain=None):
    return c.adapter().verify_transcript(doc['p'],doc['n'],doc['projected_bits'],doc['polynomials'],[] if domain is None else domain,answer,aux_bound=None)


def root(polys, assignment, p):
    return all(sum(coefficient for mask, coefficient in poly.items() if int(mask) & assignment == int(mask)) % p == 0 for poly in polys)


def run():
    d = descriptor(); doc = c.compile_range(d)
    raw = {'status':'complete','models':[0,1,2,3,4,5,14],'learned':[]}
    complete = c.complete_transcript(doc,d,raw,'range')
    check(doc['polynomials'] == [{'8':1,'6':6},{'9':1}])
    check(complete['failure'] is None)
    check(complete['checker_result']['projected_models'] == [0,1,2,3,4,5,6])
    proof = complete['augmented']['learned'][0]
    check(proof == {'depth':3,'prefix':7,'clause':[-1,-2,-3],'certificate':[{'0':6},{'0':1}]})
    passed.append('literal_f7')

    rejects(lambda: verify(doc,raw))
    bad = deepcopy(complete['augmented']); bad['models'].remove(14); rejects(lambda:verify(doc,bad))
    bad = deepcopy(complete['augmented']); bad['learned'][0]['certificate'][0]['0']=1; rejects(lambda:verify(doc,bad))
    bad = deepcopy(complete['augmented']); bad['models'][-1]=6; rejects(lambda:verify(doc,bad))
    rejects(lambda:verify(doc,complete['augmented'],doc['bootstrap_cnf']))
    passed.append('literal_f7_negatives')

    d5=descriptor(5,3); doc5=c.compile_range(d5)
    pr5=c.range_certificate(doc5,3,6)
    check(sum(bool(x) for x in pr5['certificate']) == 1)
    check(verify(doc5,{'status':'censored','models':[],'learned':[pr5]})['valid'])
    passed.append('direct_f5')

    for prefix in (7,15):
        pr=c.range_certificate(doc,4,prefix)
        check(pr['certificate']==proof['certificate'])
        check(verify(doc,{'status':'censored','models':[],'learned':[pr]})['valid'])
    passed.append('f7_fixed_states')

    di=descriptor(5,6,6,[{'name':'a','value_bits':[0,2,4],'state_bits':[]},{'name':'b','value_bits':[1,3,5],'state_bits':[]}])
    inter=c.compile_range(di)
    for prefix, first in ((60,0),(40,1),(20,0)):
        pr=c.range_certificate(inter,6,prefix)
        check(pr is not None)
        nonzero=[i for i,v in enumerate(pr['certificate']) if v]
        check(nonzero[0] in [f['index'] for f in inter['generators'][first]['forbidden']])
        check(verify(inter,{'status':'censored','models':[],'learned':[pr]})['valid'])
    passed.append('interleaving')

    dc=descriptor(7,6,3,[{'name':'x','value_bits':[0,2,4],'state_bits':[5]}]); cross=c.compile_range(dc)
    bits=c.encode_assignment(cross,{'x':6},dc,'range'); check(bits==52)
    check(c.decode_assignment(cross,bits,dc,'range')['assignment']=={'x':6})
    r=c.complete_transcript(cross,dc,{'status':'censored','models':[52],'learned':[]},'range')
    check(r['checker_result']['projected_models']==[4])
    pr=c.range_certificate(cross,5,21); check(pr is not None)
    check(verify(cross,{'status':'censored','models':[],'learned':[pr]})['valid'])
    passed.append('cross_projection')

    dz=descriptor(m=0); z=c.compile_range(dz)
    r=c.complete_transcript(z,dz,{'status':'complete','models':[14],'learned':[]},'range')
    check(r['checker_result']['projected_models']==[0] and not r['gaps'])
    r=c.complete_transcript(z,dz,{'status':'complete','models':[],'learned':[]},'range')
    check(r['failure'] is not None and len(r['gaps'])==1)
    passed.append('zero_projection')

    for models in (raw['models'],[0]):
        r=c.complete_transcript(doc,d,{'status':'censored','models':models,'learned':[]},'range')
        check(r['failure'] is None and r['augmented']['status']=='censored')
        check(not r['checker_result']['projected_model_set_complete'])
    passed.append('censored')

    bad=deepcopy(raw); bad['learned']=[{'depth':4,'prefix':0,'clause':[1,2,3,4],'certificate':[{},{}]}]
    r=c.complete_transcript(doc,d,bad,'range'); check(r['failure'] is not None)
    check(r['augmented']['learned'][0]==bad['learned'][0])
    bad=deepcopy(raw); bad['models'].append(0)
    check(c.complete_transcript(doc,d,bad,'range')['failure'] is not None)
    passed.append('shadowed_bad_record')

    for models in ([],[0,1,2,3,4,5]):
        r=c.complete_transcript(doc,d,{'status':'complete','models':models,'learned':[]},'range')
        check(r['failure'] is not None and r['gaps'])
        check(all(not g['arithmetic_root_asserted'] for g in r['gaps']))
    rejects(lambda:c.decode_assignment(doc,6,d,'range'))
    check(not root(doc['polynomials'],6,7))
    passed.append('domain_gap')

    check(doc['bootstrap_cnf']==[[-1,-2,-3]])
    check(doc5['bootstrap_cnf']==[[-1,-3],[-2,-3]])
    check(all(any((8 >> (abs(l)-1) & 1)==int(l>0) for l in clause) for clause in doc['bootstrap_cnf']))
    check(not root(doc['polynomials'],8,7))
    rejects(lambda:c.complete_transcript(doc,d,raw,'range',bootstrap_cnf=[[-1,-2,-4]]))
    passed.append('bootstrap')

    for pos in (True,1.0,-1,4,1):
        bad=deepcopy(d); bad['blocks'][0]['value_bits'][0]=pos
        rejects(lambda bad=bad:c.compile_range(bad))
    for states in ([2],[],[3,4],[False]):
        bad=deepcopy(d);bad['blocks'][0]['state_bits']=states;rejects(lambda bad=bad:c.compile_range(bad))
    bad=deepcopy(d);bad['blocks'][0]['value_bits']=[0,1];rejects(lambda:c.compile_range(bad))
    bad=deepcopy(d);bad['blocks'][0]['value_bits']=[1,0,2];rejects(lambda:c.authenticate(doc,bad,'range'))
    for key,value in (('p',5),('projected_bits',2)):
        bad=deepcopy(d);bad[key]=value;rejects(lambda bad=bad:c.authenticate(doc,bad,'range'))
    passed.append('layout_mutations')

    mutations=[]
    bad=deepcopy(doc);bad['polynomials'][0]['8']=2;mutations.append(bad)
    bad=deepcopy(doc);bad['polynomials'].pop();mutations.append(bad)
    bad=deepcopy(doc);bad['polynomials'].reverse();mutations.append(bad)
    bad=deepcopy(doc);bad['generators'][0]['forbidden'][0]['index']=0;mutations.append(bad)
    bad=deepcopy(doc);bad['bootstrap_cnf']=[[-1,-2,-4]];mutations.append(bad)
    bad=deepcopy(doc);bad['p']=True;mutations.append(bad)
    bad=deepcopy(doc);bad['blocks'][0]['name']='y';mutations.append(bad)
    for bad in mutations: rejects(lambda bad=bad:c.authenticate(bad,d,'range'))
    pub=public(5,'nilpotent',1); prod=c.compile_block(pub)
    for location in ('source','projection','metadata'):
        bad=deepcopy(prod)
        if location=='source': bad['source']['equations']=[]
        elif location=='projection': bad['source']['projection']=[]
        else: bad['source']['metadata']={}
        rejects(lambda bad=bad:c.authenticate(bad,pub))
    wrong=deepcopy(pub);wrong['projection']=[];rejects(lambda:c.authenticate(prod,wrong))
    passed.append('content_mutations')

    eq=lambda terms:[{'label':'test','terms':[{'coefficient':v,'variables':list(k)} for k,v in terms]}]
    layout={'x':[0,1,2],'y':[3,4,5]}
    x2,_,cost=c.substitute_equations(eq([(('x','x'),1)]),layout,7,6)
    check(x2==[{'1':1,'2':4,'3':4,'4':2,'5':1,'6':2}])
    xy,_,_=c.substitute_equations(eq([(('x','y'),1)]),layout,7,6)
    check(xy==[{'9':1,'17':2,'33':4,'10':2,'18':4,'34':1,'12':4,'20':1,'36':2}])
    minus,_,_=c.substitute_equations(eq([(('x',),6),(('x','x'),1)]),layout,7,6)
    check(minus==[{'2':2,'3':4,'4':5,'5':1,'6':2}])
    check(c.substitute_equations(eq([]),layout,7,6)[0]==[{}])
    check(c.substitute_equations(eq([((),3)]),layout,7,6)[0]==[{'0':3}])
    rejects(lambda:c.substitute_equations(eq([(('x','x','x'),1)]),layout,7,6))
    rejects(lambda:c.substitute_equations(eq([(('x',),7)]),layout,7,6))
    passed.append('bit_substitution')

    for p in (5,7):
        for kind,k in [('nilpotent',i) for i in range(6)]+[('guard',None),('slack',None),('constant',None)]:
            pub=public(p,kind,k); prod=c.compile_block(pub)
            check(prod['projected_bits']==3*len(pub['projection']))
            check(all(int(mask).bit_count()<=2 for poly in prod['polynomials'] for mask in poly))
            check([b['name'] for b in prod['projection_decoding']]==pub['projection'])
            check(c.authenticate(prod,pub)['typed_comparison']['nodes']>0)
    passed.append('accepted_blocks')

    fixtures=json.loads((c.ROOT/'coordination/prime_sat_rationality_authenticated_20261031/fixed-software-contract.json').read_text())
    for f in fixtures['nilpotent_fixtures']:
        if not f['valid']: continue
        k=len(f['U'])-1; pub=public(f['p'],'nilpotent',k,f['a'],f['b'])
        block=c.authenticated().builders.nilpotent_square_block(k,f['p'],f['a'],f['b'],U=f['U'],C=f['C'])
        prod=c.compile_block(pub); bits=c.encode_assignment(prod,block['assignment'],pub)
        decoded=c.decode_assignment(prod,bits,pub)['assignment'];check(decoded==block['assignment'])
        check(root(prod['polynomials'],bits,f['p']))
        # Independent direct evaluation of original named-variable equations.
        for e in prod['source']['equations']:
            residual=0
            for term in e['terms']:
                value=term['coefficient']
                for name in term['variables']: value*=decoded[name]
                residual+=value
            check(residual%f['p']==0)
        bad=deepcopy(block['assignment'])
        if bad:
            name=next(iter(bad));bad[name]=f['p'];rejects(lambda:c.encode_assignment(prod,bad,pub))
    passed.append('fixed_root_roundtrip')

    before=c.digest(raw); source_hash=c.digest(doc)
    r=c.complete_transcript(doc,d,raw,'range')
    check(c.digest(raw)==before and c.digest(doc)==source_hash)
    check(r['original']==raw and r['augmented']['models']==raw['models'])
    check(r['augmented']['learned'][:len(raw['learned'])]==raw['learned'])
    check(r['bootstrap_cnf']==doc['bootstrap_cnf'] and r['checker_result']['costs']['domain_validation']=={})
    passed.append('fidelity')

    cost=r['costs']['completion']
    check(cost['emitted_certificates']==1 and cost['multiplier_vector_entries']==2 and cost['multiplier_nonzeros']==2)
    check(cost['trie_visits']==15)
    check(cost['certificate_serialization_bytes']==len(c.encoded(proof)))
    check(r['costs']['final_verifier']['identity_check']['coefficient_multiplications']==3)
    check(doc['construction_costs']['range']['generators']==2)
    check(doc['construction_costs']['range']['clauses']==1)
    check(doc['construction_costs']['range']['literals']==3)
    passed.append('accounting')
    return {'schema':'prime-range-compiler-software-suite/v1','assertions':checks,'passed_groups':passed,'group_count':len(passed),'scientific_runs':0,'solver_instances':0,'claim':'fixed software checks only'}


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))

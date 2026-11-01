"""Independent fixed review. No solver, discovery, coefficient census or benchmark.

Run without arguments to checkpoint, enforce limits, and append one immutable
attempt inside independent-results.json. --suite is the bounded child entry.
Expected algebra and literal normalized charts were written before execution.
"""
import copy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = 'research/prime_sat_full_chart_composition_20261101/composition.py'
CONTRACT = 'coordination/prime_sat_full_chart_composition_20261101/fixed-software-contract.json'
INPUTS = [TARGET,
'research/prime_sat_range_corrected_20261101/compiler.py',
'research/prime_sat_rationality_authenticated_20261031/authenticated.py',
'research/prime_sat_rationality_software_20261031/circuits.py',
'research/prime_sat_rationality_software_20261031/rationality.py',
'research/prime_sat_rationality_software_20261031/checker.py',
'research/prime_sat_shared_signed_chart_20261030/quotient.py',
'research/prime_sat_shared_signed_chart_20261030/charts.py',
'research/prime_sat_shared_signed_chart_20261030/projectors.py',
'research/prime_sat_shared_signed_chart_20261030/signed_recovery.py',
'research/prime_sat_shared_signed_chart_20261030/check_chart.py',
'research/prime_sat_prefix_adapter_20261030/adapter.py',
'research/prime_sat_costbridge_controls_20261029/prefix_cover.py',
'coordination/prime_sat_full_chart_composition_20261101/SOURCE-API.md', CONTRACT,
'coordination/prime_sat_full_chart_composition_20261101/design.md',
'coordination/prime_sat_full_chart_composition_20261101/inference-amendment.yaml',
'coordination/prime_sat_full_chart_composition_20261101/review-plan.yaml',
'coordination/prime_sat_full_chart_composition_20261101/reviewer-brief.md',
'coordination/prime_sat_rationality_software_20261031/fixed-software-contract.json']
PROCEDURAL = ['AGENTS.md', 'ledger/handoffs/TASK-20261101-f834b9.yaml',
'docs/agent-contract-extended.md', 'templates/research-records.md', 'tools/check_review_independence.py']
ARMS = ('uniform_nilpotent_square', 'stratified_slack_with_nilpotent_zero_B', 'stratified_guard_with_nilpotent_zero_B')
STRATA = ('zero', 'constant', 'linear')
# Independently prescribed normalized h=A+B*y. None denotes an impossible chart.
EXPECTED_AB = {
'identity_zero': ([1],[0]), 'finite_zero_impossible': None,
'finite_one': ([0,1],[0]), 'identity_one_impossible': None,
'finite_two_repeat': ([4],[1]), 'identity_two_inverse': ([0,1],[0]),
'finite_three_common': ([0,0,1],[0]), 'identity_three': ([4],[1]),
'finite_four': ([0,4],[0,1]), 'identity_four': ([0,0,1],[0]),
'finite_five_characteristic5': ([2,0,0,1],[3]),
'identity_five_two_torsion': ([3,6],[4,1]),
'wrapped_five_balanced': ([0,0,1,1],[0]),
 'target_outside_interval': ([4,2],[1]), 'finite_two_torsion': ([4,1],[0])}


def stamp(): return datetime.now(timezone.utc).isoformat()
def sha(data): return hashlib.sha256(data).hexdigest()
def encode(x): return json.dumps(x, sort_keys=True, separators=(',',':'), allow_nan=False).encode()
def load_target():
    spec=importlib.util.spec_from_file_location('independent_review_target',ROOT/TARGET)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def trim(a):
    a=list(a) or [0]
    while len(a)>1 and a[-1]==0:a.pop()
    return a

def add(a,b,p):return trim([((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%p for i in range(max(len(a),len(b)))])
def scale(a,c,p):return trim([x*c%p for x in a])
def mul(a,b,p):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]=(c[i+j]+x*y)%p
    return trim(c)
def divrem(a,b,p):
    a=trim(a);out=[0]*max(1,len(a)-len(b)+1)
    while a!=[0] and len(a)>=len(b):
        j=len(a)-len(b);v=a[-1]*pow(b[-1],-1,p)%p;out[j]=v
        a=add(a,[0]*j+scale(b,-v,p),p)
    return trim(out),a
def power(a,n,p):
    v=[1]
    for _ in range(n):v=mul(v,a,p)
    return v

def peval(a,x,p):return sum(c*pow(x,j,p) for j,c in enumerate(a))%p

def field_residuals(source,values):
    # Independent evaluator: no target/component evaluation routine imported.
    p=source['p'];out=[]
    assert set(values)==set(source['inputs']+source['auxiliaries'])
    assert all(type(v) is int and 0<=v<p for v in values.values())
    for row in source['equations']:
        total=0
        for term in row['terms']:
            product=term['coefficient']
            for name in term['variables']:product*=values[name]
            total+=product
        out.append(total%p)
    return out

def bool_residuals(doc,bits):
    rd=doc['range_document'];p=rd['p']
    return [sum(c for mask,c in poly.items() if int(mask)&bits==int(mask))%p for poly in rd['polynomials']]

def independent_boolean_polynomials(source,blocks,p):
    # Coefficient substitution in the Boolean quotient, using Cartesian products.
    byname={b['name']:b['value_bits'] for b in blocks};out=[]
    for row in source['equations']:
        totals=Counter()
        for term in row['terms']:
            choices=[[(1<<position,2**j) for j,position in enumerate(byname[name])] for name in term['variables']]
            for picked in itertools.product(*choices):
                mask=0;coefficient=term['coefficient']
                for bit,weight in picked:mask|=bit;coefficient*=weight
                totals[mask]+=coefficient
        out.append({str(m):c%p for m,c in sorted(totals.items()) if c%p})
    threshold=p-1;ones=[j for j in reversed(range(threshold.bit_length())) if threshold>>j&1]
    for b in blocks:
        state=[b['value_bits'][ones[0]]]+b['state_bits']
        for r in range(1,len(ones)):
            terms=Counter({1<<state[r]:1})
            terms[(1<<state[r-1])|(1<<b['value_bits'][ones[r]])]-=1
            out.append({str(m):c%p for m,c in sorted(terms.items()) if c%p})
        for j in range(threshold.bit_length()):
            if threshold>>j&1:continue
            r=sum(q>j for q in ones)-1
            out.append({str((1<<state[r])|(1<<b['value_bits'][j])):1})
    return out

def independent_prefix_identity(polynomials,certificate,depth,prefix,p):
    total=Counter();zero=((1<<depth)-1)^prefix
    for poly,mult in zip(polynomials,certificate):
        for raw,c in poly.items():
            mask=int(raw)
            if mask&zero:continue
            restricted=mask&~prefix
            for raw_other,v in mult.items():total[restricted|int(raw_other)]+=c*v
    return {m:c%p for m,c in total.items() if c%p}

def own_encode(doc,values):
    bits=0;p=doc['descriptor']['p'];threshold=p-1
    for block in doc['range_document']['blocks']:
        v=values[block['name']]
        for j,pos in enumerate(block['value_bits']):bits|=((v>>j)&1)<<pos
        threshold_ones=[j for j in range(threshold.bit_length()-1,-1,-1) if (threshold>>j)&1]
        prefix=1
        for i,j in enumerate(threshold_ones):
            prefix*=((v>>j)&1)
            if i:bits|=prefix<<block['state_bits'][i-1]
    return bits

class Algebra:
    """Independent sparse polynomial ring; coefficient identities from the contract."""
    def __init__(self,p):self.p=p;self.variables=[];self.rows=[]
    def c(self,x):return {():x%self.p} if x%self.p else {}
    def v(self,n):
        assert n not in self.variables;self.variables.append(n);return {(n,):1}
    def plus(self,*xs):
        out=Counter()
        for x in xs:
            for m,c in x.items():out[m]+=c
        return {m:c%self.p for m,c in out.items() if c%self.p}
    def times(self,a,b):
        out=Counter()
        for m,c in a.items():
            for n,d in b.items():out[tuple(sorted(m+n))]+=c*d
        return {m:c%self.p for m,c in out.items() if c%self.p}
    def neg(self,x):return self.times(x,self.c(-1))
    def difference(self,a,b):return self.plus(a,self.neg(b))
    def convolution(self,a,b):
        out=[{} for _ in range(max(0,len(a)+len(b)-1))]
        for i,x in enumerate(a):
            for j,y in enumerate(b):out[i+j]=self.plus(out[i+j],self.times(x,y))
        return out
    def eq(self,label,x):
        self.rows.append({'label':label,'terms':[{'coefficient':c,'variables':list(m)} for m,c in sorted(x.items())]})
    def coefficient_identity(self,label,left,right):
        for i in range(max(len(left),len(right))):self.eq(label+'.coefficient'+str(i),self.difference(left[i] if i<len(left) else {},right[i] if i<len(right) else {}))
    def vecadd(self,a,b):return [self.plus(a[i] if i<len(a) else {},b[i] if i<len(b) else {}) for i in range(max(len(a),len(b)))]
    def product(self,U,L,R,label,zero=False):
        k=len(U)-1
        P=[{}]*k if zero else [self.v(label+'.P'+str(i)) for i in range(k)]
        Q=[self.v(label+'.Q'+str(i)) for i in range(k-1)]
        self.coefficient_identity(label,self.convolution(L,R),self.vecadd(P,self.convolution(U,Q)))
        return P
    def chain(self,U,D,prefix):
        k=len(U)-1
        if prefix=='interval.':
            names={2:'N2',3:'N3',4:'N4',5:'N5'}
        else:names={2:'D2'+('zero' if k==2 else ''),3:'D3zero',4:'D4'+('zero' if k==4 else ''),5:'D5zero'}
        R2=self.product(U,D,D,prefix+names[2],k==2)
        if k==3:self.product(U,R2,D,prefix+names[3],True)
        if k>=4:
            R4=self.product(U,R2,R2,prefix+names[4],k==4)
            if k==5:self.product(U,R4,D,prefix+names[5],True)

def expected_source(d):
    p,k=d['p'],d['k'];R=Algebra(p);T=d['target'];degree=k+int(T is not None)
    if k==0 or degree==1:
        if T is not None or degree==1 or d['stratum']!='zero':R.eq('special.impossible',R.c(1))
        return [],R.variables,R.rows
    basis=sorted([(2*i,'A',i) for i in range(degree//2+1)]+[(2*i+3,'B',i) for i in range(max(0,(degree-3)//2+1))])
    A=[{}]*(degree//2+1);B=[{}]*max(1,(degree-3)//2+1)
    for pole,kind,i in basis:
        (A if kind=='A' else B)[i]=R.c(1) if pole==degree else R.v('chart.'+kind+str(i))
    inputs=R.variables[:]
    U=[R.v('support.u'+str(i)) for i in range(k)]+[R.c(1)]
    f=[R.c(x) for x in [d['b'],d['a'],0,1]]
    rhs=U if T is None else R.convolution([R.c(-T[0]),R.c(1)],U)
    rhs=[R.times(x,R.c((-1)**degree)) for x in rhs]
    R.coefficient_identity('norm',R.convolution(A,A),R.vecadd(R.convolution(f,R.convolution(B,B)),rhs))
    if T is not None:R.eq('sign.target',R.plus(*[R.times(x,R.c(pow(T[0],i,p))) for i,x in enumerate(A)],*[R.times(x,R.c(-T[1]*pow(T[0],i,p))) for i,x in enumerate(B)]))
    b0=B[0];b1=B[1] if len(B)>1 else {}
    if d['stratum']=='zero':R.eq('stratum.B0zero',b0);R.eq('stratum.B1zero',b1)
    else:
        if d['stratum']=='constant':R.eq('stratum.B1zero',b1)
        z=R.v('stratum.inverse');R.eq('stratum.nonzero',R.plus(R.times(z,b0 if d['stratum']=='constant' else b1),R.c(-1)))
    E=[]
    for j in range(d['s']):
        e=[R.v('interval.e'+str(j)+'.'+str(i)) for i in range(k)];E.append(e)
        Q=[R.v('interval.idem'+str(j)+'.Q'+str(i)) for i in range(k-1)]
        R.coefficient_identity('interval.idem'+str(j),R.convolution(e,e),R.vecadd(e,R.convolution(U,Q)))
    N=[{}]*k
    if k==1:N[0]=R.neg(U[0])
    else:N[1]=R.c(1)
    N[0]=R.plus(N[0],R.c(-d['t']))
    for j,e in enumerate(E):N=[R.plus(x,R.times(y,R.c(-(2**j)))) for x,y in zip(N,e)]
    if k==1:R.eq('interval.Nzero',N[0])
    else:R.chain(U,N,'interval.')
    # Complete rationality identities, independently written without builder imports.
    if d['arm']==ARMS[0] or d['stratum']=='zero':
        C=[R.v('rationality.C'+str(i)) for i in range(k)]
        if k==1:
            v=R.v('rationality.v');F=R.v('rationality.F')
            R.eq('rationality.evaluation.square',R.difference(v,R.times(U[0],U[0])))
            R.eq('rationality.evaluation.cubic',R.plus(F,R.times(U[0],v),R.times(U[0],R.c(d['a'])),R.c(-d['b'])))
            R.eq('rationality.ordinate.square',R.difference(R.times(C[0],C[0]),F))
        else:
            if k==2:
                q=R.v('rationality.f.q');F1=R.v('rationality.f.F1');F0=R.v('rationality.f.F0')
                R.eq('rationality.f.degree2',R.plus(q,U[1]))
                R.eq('rationality.f.degree1',R.plus(F1,U[0],R.times(U[1],q),R.c(-d['a'])))
                R.eq('rationality.f.degree0',R.plus(F0,R.times(U[0],q),R.c(-d['b'])))
                F=[F0,F1]
            elif k==3:F=[R.difference(f[i],U[i]) for i in range(3)]
            else:F=f+[{}]*(k-4)
            W=R.product(U,C,C,'rationality.C2')
            D=[R.difference(x,y) for x,y in zip(W,F)]
            R.chain(U,D,'rationality.')
    elif d['stratum']=='constant':
        z=R.v('rationality.z');R.eq('rationality.constant.inverse',R.plus(R.times(b0,z),R.c(-1)))
    else:
        aa=A+[{}]*(4-len(A))
        z,x,q1,q2,c,v,F=[R.v('rationality.'+n) for n in ('z','alpha','q1','q2','c','v','F')]
        R.eq('rationality.linear.inverse',R.plus(R.times(b1,z),R.c(-1)))
        R.eq('rationality.linear.root',R.plus(R.times(b1,x),b0))
        R.eq('rationality.A.horner1',R.plus(q1,R.neg(R.times(aa[3],x)),R.neg(aa[2])))
        R.eq('rationality.A.horner2',R.plus(q2,R.neg(R.times(q1,x)),R.neg(aa[1])))
        R.eq('rationality.A.value',R.plus(c,R.neg(R.times(q2,x)),R.neg(aa[0])))
        R.eq('rationality.f.square',R.difference(v,R.times(x,x)))
        R.eq('rationality.f.value',R.plus(F,R.neg(R.times(x,v)),R.neg(R.times(x,R.c(d['a']))),R.c(-d['b'])))
        if d['arm']==ARMS[2]:
            e,u,beta=[R.v('rationality.'+n) for n in ('e','u','beta')]
            R.eq('rationality.guard.inverse',R.plus(R.times(c,u),e,R.c(-1)))
            R.eq('rationality.guard.c',R.times(c,e));R.eq('rationality.guard.u',R.times(u,e))
            R.eq('rationality.guard.beta',R.difference(beta,R.times(e,beta)))
            R.eq('rationality.guard.square',R.difference(R.times(beta,beta),R.times(e,F)))
        else:
            beta,u=[R.v('rationality.'+n) for n in ('beta','u')]
            R.eq('rationality.slack.square',R.plus(R.times(beta,beta),R.neg(F),R.neg(R.times(c,u))))
    return inputs,R.variables[len(inputs):],R.rows


def descriptor(f,arm,stratum):return {**{x:f[x] for x in ('p','a','b','target','t','s')},'k':len(f['points']),'arm':arm,'stratum':stratum}

def reject(call):
    try:call()
    except (ValueError,TypeError,KeyError,IndexError) as e:return {'type':type(e).__name__,'message':str(e)}
    raise AssertionError('required rejection did not occur')


def suite():
    resource.setrlimit(resource.RLIMIT_AS,(2147483648,2147483648))
    start=time.monotonic();M=load_target();contract=json.loads((ROOT/CONTRACT).read_text())
    records=[];failures=[];cache={};checks=Counter()
    def record(name,body):
        try:
            value=body();records.append({'id':name,'status':'pass','observation':value})
        except Exception as error:
            failures.append(name);records.append({'id':name,'status':'fail','exception':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()})
    def check_fixture(f,arm,stratum):
        d=descriptor(f,arm,stratum);doc=M.compile_chart(d);source=doc['source'];p=d['p'];k=d['k']
        expected_inputs,expected_aux,expected_rows=expected_source(d)
        assert source['inputs']==source['projection']==expected_inputs
        assert source['auxiliaries']==expected_aux
        assert source['equations']==expected_rows, 'complete symbolic coefficient equations differ from independent derivation'
        names=source['inputs']+source['auxiliaries'];assert len(names)==len(set(names))
        assert all(len(t['variables'])<=2 for e in source['equations'] for t in e['terms'])
        blocks={}
        for row in expected_rows:blocks.setdefault(row['label'].split('.')[0],[]).append(row['label'])
        assert source['metadata']['blocks']==[{'name':a,'equations':b} for a,b in blocks.items()]
        rd=doc['range_document'];w=(p-1).bit_length();h=(p-1).bit_count()-1
        assert rd['projected_bits']==w*len(expected_inputs)
        assert rd['n']==(w+h)*len(names)
        assert rd['blocks']==[{'name':n,'value_bits':list(range(i*w,(i+1)*w)),'state_bits':list(range(w*len(names)+i*h,w*len(names)+(i+1)*h))} for i,n in enumerate(names)]
        assert rd['polynomials']==independent_boolean_polynomials(source,rd['blocks'],p), 'independent complete Boolean substitution and range recurrences'
        ab=EXPECTED_AB[f['id']]
        impossible=ab is None or k==0 and stratum!='zero'
        interval_var=sum(n.startswith('interval.') for n in names)
        interval_eq=sum(r['label'].startswith('interval.') for r in expected_rows)
        if k and ab is not None:
            ell={1:0,2:1,3:2,4:2,5:3}[k]
            expected_counts=(d['s'],d['s']+1) if k==1 else (d['s']*(2*k-1)+(ell-1)*(2*k-1)+(k-1),(d['s']+ell)*(2*k-1))
            assert (interval_var,interval_eq)==expected_counts
        info={'descriptor':d,'source_sha256':sha(encode(source)),'projection':expected_inputs,'auxiliaries':len(expected_aux),'equations':len(expected_rows),'interval_counts':[interval_var,interval_eq]}
        if impossible:
            assert any(row['terms']==[{'coefficient':1,'variables':[]}] for row in expected_rows)
            info['literal_obstruction']=True
            if ab is None:
                info['original_constructor_rejection']=reject(lambda:M.charts.construct_from_signed_multiset({x:f[x] for x in ('p','a','b')},{x:f[x] for x in ('t','s')},f['points'],f['target']))
            # Empty or impossible charts retain the literal obligation.
            return info
        chart=M.charts.construct_from_signed_multiset({x:f[x] for x in ('p','a','b')},{x:f[x] for x in ('t','s')},f['points'],f['target'])
        assert (chart['A'],chart['B'])==ab, 'literal normalized chart expectation'
        U=[1]
        for x,y in f['points']:U=mul(U,[-x%p,1],p)
        assert chart['U']['coeffs']==U
        recovered=sorted(copy.deepcopy(f['points']))+[None]*(5-k)
        assert M.check_chart.check_chart(chart,recovered)['status']=='valid'
        actual='zero' if ab[1]==[0] else 'constant' if len(ab[1])==1 else 'linear'
        before=sha(encode(source))
        if actual!=stratum:
            info['wrong_stratum_rejection']=reject(lambda:M.construct_assignment(d,chart,recovered))
            assert sha(encode(M.canonical_chart(d)))==before
            info['claim']='fixed witness rejection only'
            return info
        built=M.construct_assignment(d,chart,recovered);assignment=built['assignment']
        residuals=field_residuals(source,assignment);assert not any(residuals)
        check=M.check_chart_assignment(doc,assignment,d);assert check['status']=='valid'
        assert [x['value'] for x in check['residuals']]==residuals
        encoded=M.encode_chart_counted(doc,assignment,d);bits=encoded['bits'];assert bits==own_encode(doc,assignment)
        br=bool_residuals(doc,bits);assert not any(br)
        decoded=M.decode_chart_counted(doc,bits,d)
        assert decoded['assignment']==assignment and decoded['recovered']==recovered
        assert (decoded['chart']['A'],decoded['chart']['B'])==ab
        assert decoded['projection']==[assignment[n] for n in expected_inputs]
        assert M.check_chart.check_chart(decoded['chart'],recovered)['status']=='valid'
        # Full source equality after a different, deliberately invalid assignment.
        invalid=dict(assignment)
        if names:invalid[names[0]]=(invalid[names[0]]+1)%p
        if names:
            bad=M.check_chart_assignment(doc,invalid,d)
            assert [x['value'] for x in bad['residuals']]==field_residuals(source,invalid)
            badbits=M.encode_chart_counted(doc,invalid,d)['bits']
            assert bool_residuals(doc,badbits)[:len(residuals)]==field_residuals(source,invalid)
            assert bad['status']=='invalid';reject(lambda:M.decode_chart_counted(doc,badbits,d))
        assert sha(encode(M.canonical_chart(d)))==before
        if k>1:
            N=divrem(add([0,1],[-d['t']%p],p),U,p)[1]
            for j,e in enumerate(chart['e']):N=add(N,scale(e,-2**j,p),p)
            assert divrem(power(N,k,p),U,p)[1]==[0]
            info['membership_N']=N;info['N_nonzero']=N!=[0]
        info.update(valid_roundtrip=True,A=ab[0],B=ab[1],U=U,signed_output=recovered,projection_values=decoded['projection'],field_residuals=residuals,boolean_residual_count=len(br))
        cache[(f['id'],arm)]=(d,doc,chart,recovered,assignment,bits)
        if f['id'] in ('identity_zero','finite_four','identity_five_two_torsion'):info['phase_receipts']={'construction':doc['construction_costs'],'assignment':built['costs'],'encoding':encoded['costs'],'decoding':decoded['costs']}
        return info
    assert len(contract['chart_fixtures'])==15 and len(contract['fixed_checks'])==22
    for f in contract['chart_fixtures']:
        for arm in ARMS:
            for stratum in STRATA:record('chart/'+f['id']+'/'+arm+'/'+stratum,lambda f=f,arm=arm,stratum=stratum:check_fixture(f,arm,stratum))
    def nilpotent(f):
        p=f['p'];U=f['U'];k=len(U)-1;C=f['C'] or [0]
        D=divrem(add(mul(C,C,p),scale([f['b'],f['a'],0,1],-1,p),p),U,p)[1]
        final=divrem(power(D,k,p),U,p)[1];valid=final==[0]
        assert valid==f['valid']
        block=M.rat.nilpotent_square_block(k,p,f['a'],f['b'],U,f['C'])
        r=field_residuals(block['circuit'],block['assignment']);assert (not any(r))==valid
        expected={'p':p,'curve':{'a':f['a'],'b':f['b']},'kind':'nilpotent','k':k,'inputs':{n:block['assignment'][n] for n in block['circuit']['inputs']},'projection':block['circuit']['projection']}
        checked=M.compiler().authenticated().check_authenticated_assignment(block['circuit'],block['assignment'],expected)
        assert (checked['status']=='valid')==valid
        alt=M.rat.nilpotent_square_block(k,p,f['a'],f['b'])
        assert block['circuit']==alt['circuit'],'template cannot depend on numerical U/C'
        if f['id'] in ('repeated_branch','repeated_nonbranch'):assert D!=[0] and valid
        return {'D':D,'D_power_k_mod_U':final,'valid':valid,'independent_residuals':r,'exact_square_would_reject':D!=[0]}
    for f in contract['nilpotent_fixtures']:record('nilpotent/'+f['id'],lambda f=f:nilpotent(f))
    def guard(f):
        p=f['p'];c,F,e,u,beta=[f[n] for n in ('c','F','e','u','beta')]
        r=[(c*u+e-1)%p,c*e%p,u*e%p,(beta-e*beta)%p,(beta*beta-e*F)%p]
        assert (not any(r))==f['valid']
        # alpha=0, b=F; a=1 when F=0 ensures nonsingularity. A is constant c.
        a=1 if F==0 else 0
        block=M.rat.linear_B_square_block(p,a,F,'guard',[c],[0,1],beta)
        block['assignment'].update(e=e,u=u,beta=beta)
        rr=field_residuals(block['circuit'],block['assignment']);assert rr[-5:]==r
        assert block['circuit']==M.rat.linear_B_square_block(p,a,F,'guard')['circuit']
        expected={'p':p,'curve':{'a':a,'b':F},'kind':'guard','k':None,'inputs':{n:block['assignment'][n] for n in block['circuit']['inputs']},'projection':block['circuit']['projection']}
        checked=M.compiler().authenticated().check_authenticated_assignment(block['circuit'],block['assignment'],expected)
        assert (checked['status']=='valid')==f['valid']
        return {'residuals':r,'valid':f['valid']}
    for f in contract['guard_fixtures']:record('guard/'+f['id'],lambda f=f:guard(f))
    def f1():
        points=[[0,1]]*4+[[0,4]]
        chart={'curve':{'p':5,'a':0,'b':1},'interval':{'t':0,'s':0},'k':5,'target':None,'A':[0,4],'B':[0,1],'U':{'p':5,'coeffs':[0]*5+[1]},'e':[],'root_lifts':[[0,1],[0,4]]}
        d={'p':5,'a':0,'b':1,'k':5,'target':None,'t':0,'s':0,'arm':ARMS[2],'stratum':'linear'}
        doc=M.compile_chart(d);rows=[]
        assert M.check_chart.check_chart(chart,points)['status']=='valid'
        for beta in (1,4):
            a=M.construct_assignment(d,chart,points,beta)['assignment'];assert a['rationality.beta']==beta
            assert not any(field_residuals(doc['source'],a))
            bits=M.encode_chart_counted(doc,a,d)['bits'];assert not any(bool_residuals(doc,bits))
            decoded=M.decode_chart_counted(doc,bits,d);assert decoded['recovered']==points
            rows.append({'beta':beta,'projection':decoded['projection'],'signed_output':decoded['recovered']})
        assert rows[0]['projection']==rows[1]['projection']
        bads=[[[0,1]]+[[0,4]]*4,[[0,1]]*3+[[0,4]]*2,[[0,1]]*2+[[0,4]]*3]
        for wrong in bads:
            assert M.check_chart.check_chart(chart,wrong)['status']=='invalid'
            reject(lambda wrong=wrong:M.construct_assignment(d,chart,wrong,1))
        return {'branches':rows,'valuation_derivation':{'common_order':1,'norm_order':5,'residual_excess':3,'residual_ratio_ordinate':1,'multiplicities':[4,1]},'wrong_signed_outputs_rejected':bads}
    record('F1/both_signs_and_false_multiplicities',f1)
    def projections():
        out=[]
        for f in contract['chart_fixtures']:
            if EXPECTED_AB[f['id']] is None:continue
            docs=[cache[(f['id'],a)] for a in ARMS]
            assert len({tuple(d[1]['source']['projection']) for d in docs})==1
            assert len({tuple(d[4][n] for n in d[1]['source']['projection']) for d in docs})==1
            out.append(f['id'])
        return {'same_fixed_coefficient_projections':out,'complete_model_sets_claimed':False,'cross_coordinate_equivalence_claimed':False}
    record('projection/common_coefficients',projections)
    # Typed schema and document mutation controls operate on fixed source, never a search.
    def mutations():
        d,doc,chart,points,a,bits=cache[('finite_four',ARMS[2])];out=[]
        def bad(name,mutate):
            x=copy.deepcopy(doc);mutate(x);out.append({'id':name,'rejection':reject(lambda:M.authenticate_chart(x,d))})
        for label in ('norm.coefficient0','sign.target','interval.idem0.coefficient0','interval.N2.coefficient0','interval.N4.coefficient0','rationality.guard.square'):
            def change(x,label=label):
                row=next(r for r in x['source']['equations'] if r['label']==label);row['terms']=[] if row['terms'] else [{'coefficient':1,'variables':[]}]
                x['source_sha256']=sha(encode(x['source']))
            bad('forged/'+label,change)
        bad('shared_U',lambda x:x['source']['auxiliaries'].__setitem__(0,'support.uBAD'))
        bad('variable_order',lambda x:x['source']['inputs'].reverse())
        bad('metadata',lambda x:x['source']['metadata']['blocks'][0]['equations'].reverse())
        bad('source_hash',lambda x:x.__setitem__('source_sha256','0'*64))
        bad('late_term_bool',lambda x:x['source']['equations'][-1]['terms'][-1].__setitem__('coefficient',True))
        bad('late_terms_dict',lambda x:x['source']['equations'][-1].__setitem__('terms',{}))
        bad('late_range_mask',lambda x:x['range_document']['polynomials'][-1].__setitem__('01',1))
        bad('layout_bool',lambda x:x['range_document']['blocks'][0]['value_bits'].__setitem__(0,False))
        bad('range_data',lambda x:x['range_document']['bootstrap_cnf'].append([]))
        bad('projected_coefficient',lambda x:x['source']['projection'].__setitem__(0,'support.u0'))
        bad('public_descriptor',lambda x:x['descriptor'].__setitem__('t',1))
        # Authenticate against whole trusted descriptor, never generic arithmetic.
        out.append({'id':'generic_descriptor','rejection':reject(lambda:M.authenticate_chart(doc,doc['range_document']['descriptor']))})
        for key,value in [('p',True),('a',False),('b',True),('k',True),('s',False),('t',False),('target',[False,1]),('target',(0,1)),('target',[0,0]),('k',6),('s',3),('arm','unknown'),('stratum','unknown')]:
            x=copy.deepcopy(d);x[key]=value
            out.append({'id':'descriptor/'+key+'/'+repr(value),'rejection':reject(lambda x=x:M.canonical_chart(x))})
        x=copy.deepcopy(d);x.update(a=0,b=0);out.append({'id':'singular','rejection':reject(lambda:M.canonical_chart(x))})
        for key in ('witness','source','projection','arithmetic'):
            x=copy.deepcopy(d);x[key]=[];out.append({'id':'caller_'+key,'rejection':reject(lambda x=x:M.canonical_chart(x))})
        x=copy.deepcopy(d);del x['k'];out.append({'id':'missing_k','rejection':reject(lambda:M.canonical_chart(x))})
        # Assignment is parsed eagerly, even if an earlier arithmetic row fails.
        x=dict(a);x[next(iter(x))]=(x[next(iter(x))]+1)%d['p'];x[list(x)[-1]]=True
        checked=M.check_chart_assignment(doc,x,d);assert checked['stage']=='assignment';out.append({'id':'late_assignment_bool','result':checked})
        x=copy.deepcopy(doc);x['source']['equations'][0]['terms']=[{'coefficient':1,'variables':[]}];x['source']['equations'][-1]['terms']=[{'coefficient':True,'variables':[]}]
        checked=M.check_chart_assignment(x,a,d);assert checked['stage']=='authentication';out.append({'id':'early_obstruction_late_malformed','result':checked})
        for name in ('support.u0','interval.idem0.Q0','interval.N2.Q0','interval.N2.P0','interval.N4.Q0','rationality.q1','chart.A0'):
            x=dict(a);x[name]=(x[name]+1)%d['p'];r=field_residuals(doc['source'],x);assert any(r)
            out.append({'id':'assignment/'+name,'nonzero_labels':[row['label'] for row,v in zip(doc['source']['equations'],r) if v]})
        return out
    record('negative/schema_content_and_arithmetic',mutations)
    def range_negatives():
        d,doc,chart,points,a,bits=cache[('identity_five_two_torsion',ARMS[2])];rd=doc['range_document'];out=[]
        for val in (True,-1,1<<rd['n']):out.append({'case':repr(val),'rejection':reject(lambda val=val:M.decode_chart_counted(doc,val,d))})
        state=rd['blocks'][0]['state_bits'][0]
        out.append({'case':'flipped_state','rejection':reject(lambda:M.decode_chart_counted(doc,bits^(1<<state),d))})
        b=rd['blocks'][0];illegal=bits
        for pos in b['value_bits']:illegal|=1<<pos
        out.append({'case':'value_p','rejection':reject(lambda:M.decode_chart_counted(doc,illegal,d))})
        x=dict(a);x[next(iter(x))]=d['p'];out.append({'case':'encode_p','rejection':reject(lambda:M.encode_chart_counted(doc,x,d))})
        x=dict(a);x[next(iter(x))]=False;out.append({'case':'encode_bool','rejection':reject(lambda:M.encode_chart_counted(doc,x,d))})
        return out
    record('negative/range_and_state',range_negatives)
    def certificates():
        results=[];calls=[];adapter=M.compiler().adapter();original=adapter.verify_transcript
        def spy(*args,**kwargs):
            calls.append({'domain_cnf':args[4],'aux_bound':kwargs.get('aux_bound'),'polynomial_count':len(args[3])});return original(*args,**kwargs)
        adapter.verify_transcript=spy
        try:
            d,doc,chart,points,a,bits=cache[('identity_zero',ARMS[0])]
            for status,models in [('complete',[0]),('censored',[0]),('complete',[]),('censored',[])]:
                answer={'status':status,'models':models,'learned':[],'telemetry':{'original_marker':'retain'}}
                result=M.complete_chart_transcript(doc,d,answer)
                assert result['completion']['original']==answer and result['completion']['augmented']['status']==status
                assert answer==result['completion']['augmented']
                if status=='complete' and not models:assert not result['accepted'] and result['completion']['failure']
                else:assert result['accepted']
                if status=='censored':assert not result['completion']['checker_result']['projected_model_set_complete']
                results.append({'case':'empty_projection/'+status+'/'+str(bool(models)),'answer':answer,'result':result})
            impossible={'p':5,'a':0,'b':1,'k':0,'target':[0,1],'t':0,'s':1,'arm':ARMS[0],'stratum':'zero'}
            impdoc=M.compile_chart(impossible)
            proof={'depth':0,'prefix':0,'clause':[],'certificate':[{'0':1}]}
            for status,learned,models in [('complete',[proof],[]),('complete',[],[]),('censored',[proof],[]),('complete',[proof,{'depth':0,'prefix':0,'clause':[],'certificate':[{'0':True}]}],[]),('censored',[proof],[0])]:
                answer={'status':status,'models':models,'learned':learned};result=M.complete_chart_transcript(impdoc,impossible,answer)
                assert result['completion']['original']==answer
                assert result['completion']['augmented']['learned'][:len(learned)]==learned
                assert result['declared_status']==status
                if not models and learned==[proof]:assert result['accepted']
                else:assert not result['accepted']
                if models:assert result['model_failures'] and not result['decoded_models']
                results.append({'case':'literal_impossible/'+status+'/'+str(len(learned))+'/'+str(len(models)),'answer':answer,'result':result})
            d,doc,chart,points,a,bits=cache[('finite_four',ARMS[2])]
            for status,models in [('censored',[bits]),('complete',[bits]),('censored',[bits,bits]),('censored',[bits,0])]:
                answer={'status':status,'models':models,'learned':[]};result=M.complete_chart_transcript(doc,d,answer)
                assert result['completion']['original']==answer and result['completion']['augmented']['models']==models
                assert result['declared_status']==status
                if status=='censored' and len(models)==1:assert result['accepted']
                else:assert not result['accepted']
                if models[-1]==0:assert [v['model_index'] for v in result['model_failures']]==[1] and result['decoded_models'][0]['model_index']==0
                # Retain all original records; summarized results avoid duplicating large costs.
                results.append({'case':'nonempty/'+status+'/'+str(len(models))+'/'+str(models[-1]==0),'accepted':result['accepted'],'failure':result['completion']['failure'],'model_failures':result['model_failures'],'gaps':result['completion']['gaps'],'original_preserved':True,'failure_cost_boundary':result['failure_cost_boundary']})
        finally:adapter.verify_transcript=original
        assert calls and all(c['domain_cnf']==[] and c['aux_bound'] is None for c in calls)
        return {'cases':results,'final_verifier_calls':calls}
    record('certificate/original_records_status_and_full_cube',certificates)
    def counters():
        d,doc,chart,points,a,bits=cache[('finite_four',ARMS[2])]
        original=M.canonical_chart;calls=[]
        def spy(x):calls.append(copy.deepcopy(x));return original(x)
        M.canonical_chart=spy
        rows=[]
        try:
            for name,call,expected in [
                ('authentication',lambda:M.authenticate_chart(doc,d),1),
                ('encode',lambda:M.encode_chart_counted(doc,a,d),1),
                ('decode',lambda:M.decode_chart_counted(doc,bits,d),1),
                ('construct_assignment',lambda:M.construct_assignment(d,chart,points),1),
                ('transcript_one_model',lambda:M.complete_chart_transcript(doc,d,{'status':'censored','models':[bits],'learned':[]}),2)]:
                before=len(calls);value=call();assert len(calls)-before==expected
                rows.append({'phase':name,'observed_canonical_chart_calls':len(calls)-before,'expected':expected})
            x=copy.deepcopy(doc);x['source_sha256']='x';before=len(calls);err=reject(lambda:M.authenticate_chart(x,d));assert len(calls)-before==1
            rows.append({'phase':'failed_authentication','observed_canonical_chart_calls':1,'error':err,'successful_receipt_returned':False})
        finally:M.canonical_chart=original
        return {'observed_phase_calls':rows,'units':'invocation counts; not full cost or performance','failed_work_costs':'No interrupted inner counts are returned; outer suite records elapsed time and failure.'}
    record('costs/repeated_builds_and_failure_boundary',counters)
    def range_certificate_control():
        d,doc,chart,points,a,bits=cache[('identity_five_two_torsion',ARMS[2])]
        rd=doc['range_document'];proof=M.compiler().range_certificate(rd,3,7)
        assert proof and proof['clause']==[-1,-2,-3]
        assert independent_prefix_identity(rd['polynomials'],proof['certificate'],3,7,7)=={0:1}
        nonzero=[{'index':i,'multiplier':v} for i,v in enumerate(proof['certificate']) if v]
        assert len(nonzero)==2, 'p7 proof must include recurrence telescoping and forbidden generator'
        answer={'status':'censored','models':[],'learned':[proof]}
        result=M.complete_chart_transcript(doc,d,answer)
        assert result['accepted'] and result['completion']['original']==answer
        assert result['completion']['augmented']['learned'][0]==proof
        assert not result['completion']['checker_result']['projected_model_set_complete']
        wrong=copy.deepcopy(proof);i=nonzero[0]['index'];old=wrong['certificate'][i]['0'];wrong['certificate'][i]['0']=old%6+1
        assert independent_prefix_identity(rd['polynomials'],wrong['certificate'],3,7,7)!={0:1}
        bad=M.complete_chart_transcript(doc,d,{'status':'censored','models':[],'learned':[wrong]})
        assert not bad['accepted'] and bad['completion']['original']['learned']==[wrong]
        return {'depth':3,'prefix':7,'nonzero_certificate_multipliers':nonzero,'identity':{'0':1},'accepted_original':True,'rejected_modified_certificate':bad['completion']['failure'],'complete_model_set_asserted':False}
    record('certificate/range_recurrence_identity',range_certificate_control)
    def signed_failure_control():
        d,doc,chart,points,a,bits=cache[('finite_four',ARMS[2])]
        original=M.check_chart.check_chart
        M.check_chart.check_chart=lambda *args,**kwargs:{'status':'invalid','obligation':'reviewer injected signed-check failure'}
        answer={'status':'censored','models':[bits],'learned':[]}
        try:result=M.complete_chart_transcript(doc,d,answer)
        finally:M.check_chart.check_chart=original
        assert result['completion']['checker_result']['valid']
        assert not result['accepted'] and not result['decoded_models']
        assert result['model_failures'][0]['model_index']==0
        assert result['completion']['original']==answer and result['completion']['augmented']['models']==[bits]
        return {'injected_control':True,'arithmetic_certificate_valid':True,'original_model_preserved':True,'model_failures':result['model_failures'],'accepted':result['accepted']}
    record('certificate/explicit_signed_failure_propagation',signed_failure_control)
    def template_alternatives():
        result=[]
        for mode in ('guard','slack'):
            first=M.rat.linear_B_square_block(5,0,1,mode)
            second=M.rat.linear_B_square_block(5,0,1,mode,[1,2,3,4],[3,2],4)
            assert first['circuit']==second['circuit']
            result.append({'kind':mode,'symbolic_equal_under_alternative_A_B_beta':True})
        first=M.rat.constant_B_block({'p':5,'a':0,'b':1},[1])
        second=M.rat.constant_B_block({'p':5,'a':0,'b':1},[4])
        assert first['circuit']==second['circuit']
        return result+[{'kind':'constant','symbolic_equal_under_alternative_B':True}]
    record('source/component_template_alternatives',template_alternatives)
    # Assertions are pass/fail records, not separate statistical observations.
    summary={'records':len(records),'passed':sum(r['status']=='pass' for r in records),'failed':len(failures),'chart_cases':135,'nilpotent_controls':8,'guard_controls':8,'F1_beta_signs':2,'scientific_runs':0,'solver_instances':0,'remote_jobs':0}
    return {'schema':'prime-full-chart-independent-fixed-review/v1','task_id':'TASK-20261101-f834b9','summary':summary,'failures':failures,'records':records,'resource_usage':{'elapsed_seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},'assertion_record_note':'One pass record can contain multiple explicit assertions; counts are not statistical samples or independent replications.'}


def main():
    if sys.argv[1:]==['--suite']:
        try:result=suite();print(json.dumps(result,sort_keys=True));return int(bool(result['failures']))
        except BaseException:
            traceback.print_exc();return 2
    assert len(sys.argv)==1,'only parent controller or bounded --suite child'
    path=OUT/'independent-results.json'
    data=json.loads(path.read_text()) if path.exists() else {'schema':'independent-review-custody/v1','task_id':'TASK-20261101-f834b9','attempts':[],'source_snapshots':{p:(ROOT/p).read_text() for p in INPUTS},'read_inventory':{'substantive':INPUTS,'procedural':PROCEDURAL,'procedural_external':['/var/lib/spot-codex/home/skills/review-evidence/SKILL.md'],'procedural_ranges':{'docs/agent-contract-extended.md':['31-74'],'templates/research-records.md':['801-852']},'forbidden_content_read':False,'checkpoint_may_package_resume_mechanically':True},'runtime':{'requested_policy':'review-adversarial','requested_effort':'xhigh','actual_model_provider_tier_and_effort_authenticated':False,'model_verified':False,'amendment':'coordination/prime_sat_full_chart_composition_20261101/inference-amendment.yaml'}}
    assert len(data['attempts'])<4,'frozen attempt limit'
    attempt={'attempt':len(data['attempts'])+1,'started_at':stamp(),'source_sha256_before':{p:sha((ROOT/p).read_bytes()) for p in INPUTS},'test_sha256':sha(Path(__file__).read_bytes()),'test_snapshot':Path(__file__).read_text(),'environment':{'python':sys.version,'platform':platform.platform(),'PYTHONDONTWRITEBYTECODE':'1'},'suite_timeout_seconds':240,'memory_limit_bytes':2147483648,'checkpoint_command':['bash','scripts/checkpoint.sh','gate']}
    data['attempts'].append(attempt)
    def persist():path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    persist()
    gate_start=time.monotonic()
    gate=subprocess.run(attempt['checkpoint_command'],cwd=ROOT,capture_output=True,text=True)
    attempt['checkpoint']={'returncode':gate.returncode,'stdout':gate.stdout,'stderr':gate.stderr,'elapsed_seconds':time.monotonic()-gate_start,'finished_at':stamp()};persist()
    if gate.returncode:
        attempt['suite_invoked']=False;attempt['finished_at']=stamp();persist();print('Checkpoint refused; suite not invoked.',flush=True);return 3
    command=[sys.executable,'-B',str(Path(__file__).resolve()),'--suite'];attempt['suite_command']=command;attempt['suite_invoked']=True;attempt['suite_started_at']=stamp();persist()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');started=time.monotonic()
    try:
        run=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=240)
        attempt.update(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,timed_out=False)
    except subprocess.TimeoutExpired as error:
        attempt.update(returncode=None,stdout=(error.stdout or b'').decode() if type(error.stdout) is bytes else error.stdout or '',stderr=(error.stderr or b'').decode() if type(error.stderr) is bytes else error.stderr or '',timed_out=True)
    attempt['suite_elapsed_seconds']=time.monotonic()-started;attempt['finished_at']=stamp();attempt['source_sha256_after']={p:sha((ROOT/p).read_bytes()) for p in INPUTS}
    attempt['source_unchanged']=attempt['source_sha256_before']==attempt['source_sha256_after']
    try:attempt['summary']=json.loads(attempt['stdout'])['summary']
    except Exception:attempt['summary']=None
    persist();print(json.dumps({k:attempt[k] for k in ('attempt','returncode','timed_out','summary','source_unchanged','suite_elapsed_seconds')},sort_keys=True),flush=True)
    return attempt['returncode'] if attempt['returncode'] is not None else 124

if __name__=='__main__':raise SystemExit(main())

"""Independent affine construction, cache, equation and prefix checks."""
from collections import defaultdict,Counter
from hashlib import sha256
from itertools import combinations,product
import check_source
old=check_source.old

def hashed(*items):return sha256('|'.join(map(str,items)).encode()).hexdigest()
def canonical(row,r):
    pivot=next((v for v in row if v),None)
    if pivot is None:return None
    inverse=pow(pivot,-1,r);return tuple(v*inverse%r for v in row)
def label_key(alpha,beta,r):
    values=(alpha,*beta);opposite=tuple(-v%r for v in values);return min(values,opposite)

class GroupOracle:
    def __init__(self,fixture,targets):
        self.f=fixture;self.targets=targets;self.p=fixture['p'];self.a=fixture['a'];self.P=tuple(fixture['P']);self.Pcache={0:None};self.Qcache={t['index']:{0:None} for t in targets}
    def add(self,a,b):return old.add(self.p,0,self.a,a,b)
    def Pmultiple(self,k):
        if k not in self.Pcache:self.Pcache[k]=old.multiply(self.p,0,self.a,k,self.P)
        return self.Pcache[k]
    def affine(self,alpha,beta):
        point=self.Pmultiple(alpha)
        for t,k in enumerate(beta):
            if not k:continue
            if k not in self.Qcache[t]:self.Qcache[t][k]=old.multiply(self.p,0,self.a,k,tuple(self.targets[t]['point']))
            point=self.add(point,self.Qcache[t][k])
        return point

def recipes(cell,rules,actual):
    r=cell['fixture']['r'];uid=cell['fixture']['ec1']['curve_uid'];policies={};trace=[]
    for policy in rules['target_policies']:
        bytarget=[]
        for t in range(rules['targets']):
            values=[dict(alpha=0,beta=1)];used={(0,1)}
            for j in range(1,rules['target_queries_per_point']):
                if policy=='walk':values.append(dict(alpha=j,beta=1));continue
                for counter in range(rules['maximum_scalar_candidates']):
                    alpha=(1+int(hashed(rules['domain'],'target-offset',uid,t,j,counter),16)%(r-1)) if policy=='hash_offset' else int(hashed(rules['domain'],'target-alpha',uid,t,j,counter),16)%r
                    beta=1 if policy=='hash_offset' else 1+int(hashed(rules['domain'],'target-beta',uid,t,j,counter),16)%(r-1)
                    selected=(alpha,beta)not in used;trace.append(dict(policy=policy,target_index=t,index=j,counter=counter,alpha=alpha,beta=beta,selected=selected))
                    if selected:values.append(dict(alpha=alpha,beta=beta));used.add((alpha,beta));break
                else:raise ValueError('independent target recipe gate')
            bytarget.append(values)
        policies[policy]=bytarget
    if actual!=dict(policies=policies,trace=trace):raise ValueError('target policy candidate trace')
    return True

class IntegerConstructor:
    def __init__(self,r,known,window,on_new=lambda s,step:None):
        self.r=r;self.known=set(known)|{0};self.window=window;self.tables=[];self.initialized=False;self.calls=0;self.api=0;self.on_new=on_new;self.step=1
    def add(self,a,b):
        self.api+=1;s=(a+b)%self.r
        if s not in self.known:self.calls+=1;self.known.add(s);self.on_new(s,self.step)
        return s
    def initialize(self):
        if self.window:
            left=self.r-1;power=1
            while left:
                digits=[0,power]
                for _ in range(2,min(2**self.window-1,left)+1):digits.append(self.add(digits[-1],power))
                self.tables.append(digits);left//=2**self.window
                if left:
                    for _ in range(self.window):power=self.add(power,power)
        self.initialized=True
    def mul(self,scalar,step=1):
        self.step=step
        if scalar in self.known:return scalar
        if not self.initialized:self.initialize()
        if scalar in self.known:return scalar
        value=0;k=scalar
        if self.window:
            position=0
            while k:
                digit=k%(2**self.window)
                if digit:value=self.add(value,self.tables[position][digit])
                k//=2**self.window;position+=1
        else:
            power=1
            while k:
                if k%2:value=self.add(value,power)
                power=self.add(power,power);k//=2
        if value!=scalar:raise ValueError('integer constructor image')
        return value
    def summary(self):return dict(window=self.window,uncached_ec_adds=self.calls,wrapper_add_calls=self.api,table_entries=sum(map(len,self.tables)),known_labels=len(self.known))

def expected_selection(r,known,work):
    rows=[]
    for window in range(9):
        m=IntegerConstructor(r,known,window)
        for scalar in work:m.mul(scalar)
        rows.append(m.summary())
    return rows,min(rows,key=lambda v:(v['uncached_ec_adds'],v['window']))['window']

def branch(cell,collected,rules,recipe,actual,cache,oracle):
    f=cell['fixture'];r=f['r'];nt=rules['targets'];n=len(f['factor_base']);context=actual['context'];arm=context['source_schedule'];prefix=context['source_prefix'];policy=context['target_policy']
    if actual['recipe']!=recipe:raise ValueError('branch recipe copy')
    initial={0}
    for item in collected['arms'][arm]['knowledge']:
        if item['prefix']<=prefix:initial.add(item['scalar']);initial.add(-item['scalar']%r)
    expected_scalar={('P',s):1 for s in initial if s};expected_labels={};constructors={}
    def label(a,b,step):
        if a or any(b):key=label_key(a,b,r);expected_labels[key]=min(step,expected_labels.get(key,step))
    for s in initial:
        if s:label(s,[0]*nt,1)
    for t in range(nt):b=[0]*nt;b[t]=1;label(0,b,1)
    def discover(basis,s,step):
        expected_scalar[basis,s]=step;b=[0]*nt
        if basis=='P':a=s
        else:a=0;b[int(basis[1:])]=s
        label(a,b,step)
    required=[]
    if policy!='walk':required.append(('P',initial,[recipe[t][j]['alpha'] for j in range(1,rules['target_queries_per_point']) for t in range(nt)]))
    if policy=='general':
        for t in range(nt):
            basis='Q'+str(t);known={0,1,r-1};required.append((basis,known,[recipe[t][j]['beta'] for j in range(1,rules['target_queries_per_point'])]));expected_scalar[basis,1]=1;expected_scalar[basis,r-1]=1
    if set(actual['selections'])!={v[0] for v in required}:raise ValueError('constructor portfolio coverage')
    for basis,known,work in required:
        candidates,window=expected_selection(r,known,work);selection=actual['selections'][basis]
        if selection['candidates']!=candidates or selection['window']!=window:raise ValueError('uncached EC-add constructor policy')
        constructors[basis]=IntegerConstructor(r,known,window,lambda s,step,basis=basis:discover(basis,s,step))
    expected_requests=[]
    for j in range(rules['target_queries_per_point']):
        for t in range(nt):
            rec=recipe[t][j];a,b=rec['alpha'],rec['beta']
            if j and policy!='walk':constructors['P'].mul(a,j+1)
            if j and policy=='general':constructors['Q'+str(t)].mul(b,j+1)
            beta=[0]*nt;beta[t]=b;label(a,beta,j+1);point=oracle.affine(a,beta)
            expected_requests.append(dict(target_index=t,index=j,step=j+1,alpha=a,beta=b,point=None if point is None else list(point)))
    if len(actual['requests'])!=len(expected_requests):raise ValueError('target request count')
    for got,expected in zip(actual['requests'],expected_requests,strict=True):
        if {k:v for k,v in got.items() if k!='query_id'}!=expected:raise ValueError('affine endpoint/offset availability')
        if type(got['query_id'])is not int or not 0<=got['query_id']<len(cache.records) or cache.records[got['query_id']]['point']!=expected['point']:raise ValueError('query alias')
    scalar={}
    for event in actual['scalar_events']:
        key=(event['basis'],event['scalar'])
        if key in scalar:raise ValueError('duplicate scalar basis cache event')
        scalar[key]=event['step'];beta=[0]*nt
        if event['basis']=='P':a=event['scalar']
        else:a=0;beta[int(event['basis'][1:])]=event['scalar']
        point=oracle.affine(a,beta)
        if event['point']!=(None if point is None else list(point)):raise ValueError('false symbolic scalar image')
    if scalar!=expected_scalar:raise ValueError('future/omitted constructor scalar point')
    seen={};buckets=defaultdict(dict);buckets[None][(0,*([0]*nt))]=1
    for item in actual['labels']:
        a=item['alpha'];beta=item['beta'];step=item['budget'];point=oracle.affine(a,beta)
        if len(beta)!=nt or item['point']!=(None if point is None else list(point)):raise ValueError('affine point label equation')
        key=label_key(a,beta,r);seen[key]=min(step,seen.get(key,step));key0=(a,*beta);buckets[point][key0]=min(step,buckets[point].get(key0,step))
        if point is not None:
            opposite=(point[0],-point[1]%f['p']);neg=tuple(-v%r for v in key0);buckets[opposite][neg]=min(step,buckets[opposite].get(neg,step))
    if seen!=expected_labels:raise ValueError('affine label availability/completeness')
    expected_equations={}
    def equation(v,u,b,step):
        key=canonical(v+u+[b],r)
        if key is not None:expected_equations[key]=min(step,expected_equations.get(key,step))
    for point,labels in buckets.items():
        for (left,ls),(right,rs) in combinations(labels.items(),2):equation([0]*n,[(x-y)%r for x,y in zip(left[1:],right[1:],strict=True)],(right[0]-left[0])%r,max(ls,rs))
    for j,atom in enumerate(f['factor_base']):
        for values,step in buckets.get(tuple(atom['point']),{}).items():
            v=[0]*n;v[j]=1;equation(v,[-x%r for x in values[1:]],values[0],step)
    seen_equations={}
    for row in actual['equations']:
        if len(row['coefficients'])!=n or len(row['outside'])!=nt:raise ValueError('knowledge equation width')
        key=canonical(row['coefficients']+row['outside']+[row['rhs']],r)
        if key is None:raise ValueError('tautological retained knowledge row')
        seen_equations[key]=min(row['budget'],seen_equations.get(key,row['budget']))
        witness=row['witness']
        if row['kind']=='base_match':
            label0=witness['label'];sign=witness['sign'];j=witness['atom'];v=[0]*n;v[j]=1
            expected=(v,[-sign*x%r for x in label0['beta']],sign*label0['alpha']%r)
            if (row['coefficients'],row['outside'],row['rhs'])!=expected or label0['budget']>row['budget']:raise ValueError('base-match witness sign/offset')
        elif row['kind']=='point_coincidence':
            left=witness['left'];right=witness['right'];u=[(x-y)%r for x,y in zip(left['beta'],right['beta'],strict=True)];b=(right['alpha']-left['alpha'])%r
            if row['coefficients']!=[0]*n or row['outside']!=u or row['rhs']!=b or left['point']!=right['point'] or max(left['budget'],right['budget'])>row['budget']:raise ValueError('point coincidence witness')
        else:raise ValueError('unknown knowledge equation kind')
    if seen_equations!=expected_equations:raise ValueError('knowledge equation completeness/availability')
    if actual['counters'].get('scalar_uncached_ec_adds',0)!=sum(v.calls for v in constructors.values()) or actual['counters'].get('scalar_wrapper_add_calls',0)!=sum(v.api for v in constructors.values()):raise ValueError('physical constructor prediction')
    counts=Counter()
    for phase in actual['phases']:
        if phase['status']!='complete':raise ValueError('partial affine branch')
        counts.update(phase['counters'])
    if dict(counts)!=actual['counters']:raise ValueError('affine phase conservation')
    if [v['target_prefix'] for v in actual['budgets']]!=rules['target_prefixes']:raise ValueError('target budget coverage')
    for budget in actual['budgets']:
        b=budget['target_prefix']
        if budget['requests']!=nt*b or budget['labels']!=sum(v['budget']<=b for v in actual['labels']) or budget['equations']!=sum(v['budget']<=b for v in actual['equations']):raise ValueError('target prefix accounting')
    return dict(checked=True,labels=len(actual['labels']),knowledge_equations=len(actual['equations']),logical_requests=len(actual['requests']))

def query_cache(cell,collected,cache,triple_oracle):
    f=cell['fixture'];n=len(f['factor_base']);p=f['p'];points=[];table=defaultdict(list)
    for i,pair in enumerate(collected['pairs']):table[None if pair['point']is None else tuple(pair['point'])].append(i)
    for index,record in enumerate(cache.records):
        point=None if record['point']is None else tuple(record['point']);points.append(point)
        if record['id']!=index:raise ValueError('cache record index')
        rows=record['rows'];descriptors=sorted((tuple(v['triple']),tuple(v['signs'])) for v in rows)
        if descriptors!=sorted(triple_oracle.get(point,[])):raise ValueError('complete affine triple oracle')
        for row in rows:
            coefficients=[0]*n
            for j,s in zip(row['triple'],row['signs'],strict=True):coefficients[j]=(coefficients[j]+s)%f['r']
            if row['coefficients']!=coefficients or row['curve_uid']!=f['uid']:raise ValueError('affine triple encoding')
        expected=[]
        for third,sign in product(range(n),(1,-1)):
            atom=f['factor_base'][third]['point'];negative=(atom[0],-sign*atom[1]%p);wanted=old.add(p,0,f['a'],point,negative);bucket=table.get(wanted,[]);accepted=[j for j in bucket if collected['pairs'][j]['indices'][1]<third]
            expected.append(dict(index=index,third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=bucket,accepted=accepted))
        if record['trace']!=expected:raise ValueError('affine query/miss trace')
    if len(points)!=len(set(points)):raise ValueError('duplicate physical cache query')
    actual_new=len(points)-len(collected['target_generation']['targets'])
    if cache.meter.counters().get('target_queries',0)!=actual_new*2*n:raise ValueError('physical target queries inflated')
    return dict(checked=True,physical_cached_points=len(points),new_target_queries=actual_new*2*n)

def expected_case(cell,collected,branch,cache,budget,scope):
    f=cell['fixture'];r=f['r'];projection=collected['projection'];nt=len(collected['target_generation']['targets']);context=branch['context'];arm=context['source_schedule'];prefix=context['source_prefix'];order=collected['selection']['orders'][arm][:prefix]
    source=[v for v in collected['arms'][arm]['rows'] if v['source_scalar']in order]
    if scope=='anchors':source += [v for v in collected['arms'][arm]['anchors'] if v['prefix']<=prefix]
    M=[old.project(row,projection,r) for row in source];target=[]
    for request in branch['requests']:
        if request['step']>budget:continue
        for generic in cache.records[request['query_id']]['rows']:
            v,b=old.project(dict(generic,source_scalar=request['alpha']),projection,r);u=[0]*nt;u[request['target_index']]=-request['beta']%r
            target.append(dict(vector=v,outside=u,rhs=b,kind='decomposition',request=request))
    if scope=='anchors':
        for row in branch['equations']:
            if row['budget']>budget:continue
            v,b=old.project(dict(coefficients=row['coefficients'],source_scalar=row['rhs']),projection,r);target.append(dict(vector=v,outside=row['outside'],rhs=b,kind=row['kind'],witness=row['witness']))
    return dict(width=projection['U'],target_count=nt,modulus=r,source=M,target=target,targets=collected['target_generation']['targets'])

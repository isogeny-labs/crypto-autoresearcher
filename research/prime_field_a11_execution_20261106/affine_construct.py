"""Cache-aware scalar constructors with explicit P or symbolic Q basis labels."""
from crypto_autoresearcher.index_calculus.targets import FixedBaseMultiplier

class ScalarModel:
    def __init__(self,r,known):self.p=r;self.r=r;self.calls=0;self.api_calls=0;self.known={s:(s or None) for s in known};self.known[0]=None
    def add(self,left,right):
        self.api_calls+=1;s=((left or 0)+(right or 0))%self.r
        if s not in self.known:self.calls+=1;self.known[s]=s or None
        return s or None

def binary(curve,scalar,point):
    out=None
    while scalar:
        if scalar&1:out=curve.add(out,point)
        point=curve.add(point,point);scalar>>=1
    return out

def model(r,known,scalars,window):
    m=ScalarModel(r,known);table=None
    if window and any(s not in m.known for s in scalars):table=FixedBaseMultiplier(m,1,r,window=window)
    for s in scalars:
        if s in m.known:continue
        q=binary(m,s,1) if table is None else table.mul(s)
        if q!=(s or None):raise ValueError('scalar-only constructor model')
    return dict(window=window,uncached_ec_adds=m.calls,wrapper_add_calls=m.api_calls,table_entries=0 if table is None else table.entries,known_labels=len(m.known))

def select(r,known,scalars):
    candidates=[model(r,known,scalars,w) for w in range(9)]
    best=min(candidates,key=lambda x:(x['uncached_ec_adds'],x['window']))
    return dict(window=best['window'],candidates=candidates,objective='uncached EC group-add calls; ascendingwindow includingbinary0 on ties',full_horizon=True)

class ScalarCurve:
    """Coefficients are relative to one basis: a coefficient of Q is not log_P Q."""
    def __init__(self,meter,p,r,point,known,on_point,basis):
        self.meter=meter;self.p=p;self.r=r;self.P=point;self.known={0:None};self.labels={None:0};self.on_point=on_point;self.basis=basis
        for scalar,q in known.items():self.remember(q,scalar,'initial_paid_cache')
    def remember(self,q,s,origin):
        s%=self.r;self.meter.other['scalar_cache_insert_lookups']+=1
        if q in self.labels and self.labels[q]!=s:raise ValueError('inconsistent within-basis coefficient')
        if s in self.known:
            if self.known[s]!=q:raise ValueError('inconsistent coefficient image')
            return
        self.labels[q]=s;self.known[s]=q;self.meter.other['scalar_cached_points']+=1
        self.on_point(q,s,self.basis,origin)
    def add(self,left,right):
        f=self.meter.ring;self.meter.other['scalar_wrapper_add_calls']+=1
        if left not in self.labels or right not in self.labels:raise ValueError('unlabelled scalar-basis addition')
        s=f.add(self.labels[left],self.labels[right]);self.meter.other['scalar_add_cache_lookups']+=1
        if s in self.known:self.meter.other['scalar_add_cache_hits']+=1;return self.known[s]
        q=self.meter.e.add(left,right);self.meter.other['scalar_uncached_ec_adds']+=1
        self.remember(q,s,'scalar_constructor_intermediate');return q

class Constructor:
    def __init__(self,curve,selection):self.curve=curve;self.selection=selection;self.table=None;self.initialized=False
    def mul(self,s):
        self.curve.meter.other['scalar_request_cache_lookups']+=1
        if s in self.curve.known:self.curve.meter.other['scalar_request_cache_hits']+=1;return self.curve.known[s]
        if not self.initialized:
            w=self.selection['window']
            if w:self.table=FixedBaseMultiplier(self.curve,self.curve.P,self.curve.r,window=w)
            self.initialized=True
            self.curve.meter.other['post_setup_scalar_cache_lookups']+=1
            if s in self.curve.known:self.curve.meter.other['post_setup_scalar_cache_hits']+=1;return self.curve.known[s]
        return binary(self.curve,s,self.curve.P) if self.table is None else self.table.mul(s)

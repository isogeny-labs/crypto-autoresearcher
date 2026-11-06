"""Public scalar-only constructor portfolio; actual repository positional tables."""
from crypto_autoresearcher.index_calculus.targets import FixedBaseMultiplier

class ScalarModel:
    def __init__(self,r,known):
        self.p=r;self.r=r;self.calls=0;self.known={s:(s or None) for s in known};self.known[0]=None
    def add(self,left,right):
        self.calls+=1;value=((left or 0)+(right or 0))%self.r
        self.known.setdefault(value,value or None)
        return value or None

class LabelledCurve:
    def __init__(self,meter,fixture,original):
        self.meter=meter;self.p=fixture['p'];self.r=fixture['r'];self.P=tuple(fixture['P'])
        self.labels={None:0};self.known={0:None};self.points=[]
        for s,q in original.items():self.remember(q,s,'shared_prerequisite')
    def remember(self,q,s,origin):
        s%=self.r;self.meter.other['known_point_dictionary_lookups']+=1
        if q in self.labels:
            if self.labels[q]!=s:raise ValueError('inconsistent public point labels')
            return
        self.labels[q]=s;self.known[s]=q
        if q is not None:
            self.points.append(dict(point=list(q),scalar=s,origin=origin))
            self.meter.other['labelled_points_stored']+=1
            if hasattr(self.meter,'progress'):self.meter.progress(dict(kind='constructor_point',arm=self.meter.current_arm,prefix=self.meter.current_prefix,record=self.points[-1]))
    def add(self,left,right):
        if left not in self.labels or right not in self.labels:raise ValueError('unlabelled constructor input')
        value=self.meter.e.add(left,right)
        s=self.meter.ring.add(self.labels[left],self.labels[right])
        self.meter.other['constructor_group_add_calls']+=1
        self.remember(value,s,'constructor_intermediate')
        return value

def binary(curve,scalar,point):
    out=None
    while scalar:
        if scalar&1:out=curve.add(out,point)
        point=curve.add(point,point);scalar>>=1
    return out

def evaluate(curve,scalars,window,limit,point):
    table=None if window==0 or all(s in curve.known for s in scalars) else FixedBaseMultiplier(curve,point,limit,window=window)
    for scalar in scalars:
        if scalar in curve.known:continue
        result=binary(curve,scalar,point) if table is None else table.mul(scalar)
        if result!=(scalar or None):raise ValueError('scalar-only constructor prediction failed')
    return 0 if table is None else table.entries

def select(r,known,scalars):
    """Minimize exact group-add API calls; ties binary then smaller window.

    Full horizon public labels only, no coordinates/rank/field costs. These nine
    simulations are charged as policy logical work and CPU, not EC executions.
    """
    records=[]
    for window in range(9):
        model=ScalarModel(r,known);entries=evaluate(model,scalars,window,r,1)
        records.append(dict(window=window,group_add_calls=model.calls,table_entries=entries,known_labels=len(model.known)))
    chosen=min(records,key=lambda v:(v['group_add_calls'],v['window']))
    return dict(window=chosen['window'],candidates=records,objective='group_add API calls, binary then ascending window on ties',full_horizon=True)

class Constructor:
    def __init__(self,curve,window):self.curve=curve;self.window=window;self.table=None;self.initialized=False
    def initialize(self):
        if not self.initialized:
            if self.window:self.table=FixedBaseMultiplier(self.curve,self.curve.P,self.curve.r,window=self.window)
            self.initialized=True
    def mul(self,scalar):
        if scalar in self.curve.known:
            self.curve.meter.other['constructor_scalar_cache_hits']+=1
            return self.curve.known[scalar]
        self.initialize()
        return binary(self.curve,scalar,self.curve.P) if self.table is None else self.table.mul(scalar)

"""Executed scalar and shared-denominator NumPy query arithmetic, fully metered.

Fp counts are semantic operations on each field element actually evaluated by
our vector API, not historical scalar-equivalent decomposition counters. Array
allocation counters track explicit arrays in this program, not NumPy internals.
"""
from collections import Counter
from hashlib import sha256
import json
import numpy as np
from affine_solver import Meter

class Collected(dict):
    """JSON mapping plus explicit transient shared public factor-base index."""
    query_engines=None

class VectorField:
    def __init__(self,meter):self.m=meter;self.p=np.uint64(meter.f.p)
    def allocated(self,v):
        self.m.other['query_array_allocations']+=1;self.m.other['query_array_allocated_bytes']+=v.nbytes;self.m.other['query_array_allocated_elements']+=v.size;return v
    def array(self,v):
        out=self.allocated(np.array(v,dtype=np.uint64));self.m.other['query_integer_to_uint64_elements']+=out.size;return out
    def empty(self,shape):return self.allocated(np.empty(shape,dtype=np.uint64))
    def op(self,kind,a,b):
        shape=np.broadcast_shapes(np.shape(a),np.shape(b));out=self.empty(shape)
        if kind=='mul':np.multiply(a,b,out=out)
        elif kind=='add':np.add(a,b,out=out)
        elif kind=='sub':np.subtract(self.p,b,out=out);np.add(a,out,out=out)
        else:raise ValueError('field operation')
        np.remainder(out,self.p,out=out);self.m.f.counts['field_'+kind]+=out.size
        return out
    def add(self,a,b):return self.op('add',a,b)
    def sub(self,a,b):return self.op('sub',a,b)
    def mul(self,a,b):return self.op('mul',a,b)

def batch_inverse(v,f):
    """Same product-tree schedule as production _accel, including paid padding."""
    if not len(v) or np.any(v==0):raise ValueError('nonempty nonzero batch required')
    levels=[];cur=v
    while len(cur)>1:
        if len(cur)&1:
            one=f.array([1]);cur=f.allocated(np.concatenate([cur,one]));f.m.other['query_batch_padding_ones']+=1
        levels.append(cur);cur=f.mul(cur[0::2],cur[1::2])
    inv=f.array([f.m.f.inv(int(cur[0]))])
    for level in reversed(levels):
        inv=inv[:len(level)//2];out=f.empty(level.shape)
        out[0::2]=f.mul(inv,level[1::2]);out[1::2]=f.mul(inv,level[0::2]);inv=out
    return inv[:len(v)]

class QueryEngines:
    def __init__(self,fixture,base,signed,meter,event):
        self.fixture=fixture;self.base=base;self.signed=signed;self.event=event;self.serial=0;self.records=[];self.n=len(base)
        if not 3<=fixture['p']<2**32 or not base:raise ValueError('uint64 prime-field query gate')
        before=Counter(meter.counters());v=VectorField(meter);self.X=v.array([q[0] for q in base]);self.Y=v.array([q[1] for q in base]);self.Yneg=v.array([signed[i,-1][1] for i in range(self.n)])
        delta=Counter(meter.counters())-before;meter.other.update({'query_batch_index.'+k:v for k,v in delta.items()})
        self.opposite=[signed[i,-s] for i in range(self.n) for s in (1,-1)];meter.other['query_prepaid_signed_point_references']+=2*self.n
        self.descriptor=dict(p=fixture['p'],n=self.n,numpy_version=np.__version__,dtype='uint64',scope='One shared public base index per curve; no target/source scalar knowledge',signed_order='(i,+1),(i,-1)',explicit_array_bytes=self.X.nbytes+self.Y.nbytes+self.Yneg.nbytes)
    def scalar(self,Q,meter):
        result=[]
        for q in self.opposite:result.append(meter.e.add(Q,q));meter.other['query_prepaid_signed_lookups']+=1
        return result
    def batch(self,Q,meter):
        n=self.n;meter.other['query_batch_endpoints']+=1;meter.other['query_batch_signed_results']+=2*n
        if Q is None:
            meter.other['query_identity_endpoint_points']+=2*n;return list(self.opposite),[]
        f=VectorField(meter);xr,yr=map(np.uint64,Q);dx=f.sub(self.X,xr);zero=dx==0;f.allocated(zero);indices=np.flatnonzero(zero);f.allocated(indices)
        meter.other['query_zero_denominator_masks']+=n;meter.other['query_zero_denominator_entries']+=len(indices);dx[zero]=1
        inverse=batch_inverse(dx,f);summed_x=f.add(self.X,xr);by_sign=[]
        for Y in (self.Yneg,self.Y):
            slope=f.mul(f.sub(Y,yr),inverse);xx=f.sub(f.mul(slope,slope),summed_x);yy=f.sub(f.mul(slope,f.sub(xr,xx)),yr)
            points=[(int(x),int(y)) for x,y in zip(xx,yy,strict=True)];meter.other['query_uint64_to_integer_elements']+=2*n;by_sign.append(points)
        for i0 in indices:
            i=int(i0)
            for sign,j in ((1,0),(-1,1)):
                by_sign[j][i]=meter.e.add(Q,self.signed[i,-sign]);meter.other['query_exception_scalar_fallbacks']+=1
        return [by_sign[j][i] for i in range(n) for j in (0,1)],[int(i) for i in indices]
    def evaluate(self,Q,parent,context):
        records={};points={};exception_indices=[]
        try:
            for engine in ('scalar','batch'):
                meter=Meter(self.fixture)
                def run():
                    nonlocal exception_indices
                    if engine=='scalar':return self.scalar(Q,meter)
                    value,exception_indices=self.batch(Q,meter);return value
                try:points[engine]=meter.stage('signed_subtraction_'+engine,run)
                finally:
                    counts=meter.counters();records[engine]=dict(counters=counts,phases=meter.phases)
                    parent.other.update(counts);parent.other.update({'query_'+engine+'.'+k:v for k,v in counts.items()})
            parent.other['query_engine_point_comparisons']+=2*self.n
            if points['scalar']!=points['batch']:raise ValueError('scalar/batch signed point disagreement')
            record=dict(serial=self.serial,point=None if Q is None else list(Q),n=self.n,context=context,engines=records,exception_indices=exception_indices,points_sha256=sha256(json.dumps(points['batch'],separators=(',',':')).encode()).hexdigest(),equal=True)
            self.records.append(record);self.event(dict(kind='query_engines_point',record=record));self.serial+=1;return points['batch']
        except BaseException as error:
            self.event(dict(kind='query_engines_failed',context=context,point=None if Q is None else list(Q),engines=records,partial_points=points,error_type=type(error).__name__,error=str(error)));raise

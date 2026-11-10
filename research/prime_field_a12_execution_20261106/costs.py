"""Separate actual dual-engine work from deployable one-engine counter views."""
from collections import Counter
ENGINES=('scalar','batch')
def select_engine(counters,engine):
    if engine not in ENGINES:raise ValueError('query engine')
    out=Counter(counters)
    for name in ENGINES:
        prefix='query_'+name+'.'
        for key,value in counters.items():
            if key.startswith(prefix):
                bare=key[len(prefix):];out.pop(key,None)
                if name!=engine:out[bare]-=value
    prefix='query_batch_index.'
    for key,value in counters.items():
        if key.startswith(prefix):
            out.pop(key,None)
            if engine=='scalar':out[key[len(prefix):]]-=value
    out.pop('query_engine_point_comparisons',None)
    if any(v<0 for v in out.values()):raise ValueError('engine view exceeds physical work')
    return {k:v for k,v in out.items() if v}

def engine_arithmetic(counters):
    return {engine:{key[len('query_'+engine+'.'):]:value for key,value in counters.items() if key.startswith('query_'+engine+'.')} for engine in ENGINES}

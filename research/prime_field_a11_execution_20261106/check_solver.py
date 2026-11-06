"""Independent dense checks for general-U cancellation, including all negatives."""
from collections import Counter
from affine_solver import module
old=module('_a11_independent_dense','research/prime_field_a10_execution_20261106/check.py')
rank=old.rank

def combine(weights,rows,values,width,r):
    return [sum(a*v[j] for a,v in zip(weights,rows,strict=True))%r for j in range(width)],sum(a*b for a,b in zip(weights,values,strict=True))%r

def member(rec,query,rows,rhs,system,r):
    yes=rank(rows+[query],r)==rank(rows,r)
    residual=list(query)
    for entry in system['echelon']:
        scale=residual[entry['pivot']];residual=[(x-scale*y)%r for x,y in zip(residual,entry['vector'],strict=True)]
    if rec['identifiable']is not yes or rec['residual']!=residual:raise ValueError('dense membership/residual')
    if yes:
        if combine(rec['row_weights'],rows,rhs,len(query),r)!=(query,rec['value']):raise ValueError('functional certificate')
    elif rec['value']is not None or rec['row_weights']is not None:raise ValueError('false negative value')

def check(case,results,fixture=None):
    w=case['width'];nt=case['target_count'];r=case['modulus'];M=[v for v,b in case['source']];bm=[b for v,b in case['source']];B=[v['vector'] for v in case['target']];U=[v['outside'] for v in case['target']];bB=[v['rhs'] for v in case['target']]
    rows=[v+[0]*nt for v in M]+[v+u for v,u in zip(B,U,strict=True)];rhs=bm+bB;rr=rank(rows,r);ur=rank(U,r);mr=rank(M,r)
    if [v['arm'] for v in results]!=['sparse_joint','sparse_cancel']:raise ValueError('solver pair')
    for result in results:
        joint=result['arm']=='sparse_joint'
        if joint:A=rows;b=rhs
        else:
            outer=result['outside'];old.system(outer,U,[0]*len(U),r);C=[];d=[]
            for rec in result['cancellations']:
                sparse=rec['original_target_weights'];weights=[0]*len(U);indices=[]
                for i,a in sparse:
                    if type(i)is not int or not 0<=i<len(U) or type(a)is not int or not 0<a<r:raise ValueError('sparse cancellation encoding')
                    indices.append(i);weights[i]=a
                if indices!=sorted(set(indices)):raise ValueError('duplicate cancellation index')
                if len(weights)!=len(U) or combine(weights,U,[0]*len(U),nt,r)[0]!=[0]*nt:raise ValueError('outside cancellation certificate')
                v,x=combine(weights,B,bB,w,r)
                if (v,x)!=(rec['vector'],rec['rhs']):raise ValueError('base cancellation offset')
                C.append(v);d.append(x)
            if len(C)!=len(U)-ur or rank(M+C,r)!=rr-ur:raise ValueError('complete outside cancellation span')
            A=M+C;b=bm+d
        old.system(result['system'],A,b,r)
        if len(result['recoveries'])!=nt:raise ValueError('target coverage')
        for t,rec in enumerate(result['recoveries']):
            unit=[0]*(w+nt);unit[w+t]=1;yes=rank(rows+[unit],r)==rr
            if rec['target_index']!=t or rec['identifiable']is not yes:raise ValueError('joint target membership')
            if joint:member(rec,unit,A,b,result['system'],r)
            else:
                out=[0]*nt;out[t]=1;member(rec['outer'],out,U,[0]*len(U),result['outside'],r)
                if rec['outer']['identifiable']:
                    v,x=combine(rec['outer']['row_weights'],B,bB,w,r)
                    if (v,x)!=(rec['base_query'],rec['base_rhs']):raise ValueError('outside lifting offset')
                    member(rec,v,A,b,result['system'],r)
                    if rec['scalar']!=((x-rec['value'])%r if yes else None):raise ValueError('target scalar offset')
                elif rec['base_query']is not None or rec['base_rhs']is not None:raise ValueError('fabricated outside query')
            if yes:
                if combine(rec['original_row_weights'],rows,rhs,w+nt,r)!=(unit,rec['scalar']):raise ValueError('original joint certificate')
                if fixture and old.old.multiply(fixture['p'],0,fixture['a'],rec['scalar'],tuple(fixture['P']))!=tuple(case['targets'][t]['point']):raise ValueError('public scalar equation')
            elif rec['scalar']is not None or rec['original_row_weights']is not None:raise ValueError('unresolved scalar')
        totals=Counter()
        for phase in result['phases']:
            if phase['status']!='complete' or phase['wall_valid']is not False or any(type(v)is not int or v<0 for v in phase['counters'].values()):raise ValueError('phase validity')
            totals.update(phase['counters'])
        expected=['joint_matrix_construction' if joint else 'outside_elimination_cancellation','elimination','identification','certificate_lifting','original_row_certificate_verification']+(['public_target_verification'] if fixture else [])
        if [p['phase'] for p in result['phases']]!=expected or dict(totals)!=result['counters']:raise ValueError('phase conservation')
    if [(v['identifiable'],v['scalar']) for v in results[0]['recoveries']]!=[(v['identifiable'],v['scalar']) for v in results[1]['recoveries']]:raise ValueError('solver outcomes differ')
    return dict(checked=True,joint_rank=rr,outside_rank=ur,source_rank=mr,delta=rr-ur-mr,base_rank_after_cancellation=rr-ur,identified=sum(v['identifiable'] for v in results[0]['recoveries']))

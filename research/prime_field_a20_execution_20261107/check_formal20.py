"""Independent expanded-old coefficients and public group equations."""
from deps20 import check_source,solver,commitment


def expand(case,prepared):
    r=case['modulus'];n=prepared['norm_size'];definitions=prepared['formal_definitions'];w=case['width']
    if len(definitions)!=w-n:raise ValueError('exactly one definition for each auxiliary slot')
    signed=[]
    for i,item in enumerate(definitions):
        if item['auxiliary_index']!=i:raise ValueError('formal definition native index')
        if len(item['components'])!=2 or len({v[0]for v in item['components']})!=2:raise ValueError('two distinct old native indices required')
        vector=[0]*n
        for j,s in item['components']:
            if type(j)is not int or not 0<=j<n or type(s)is not int or s not in (-1,1):raise ValueError('formal component encoding')
            vector[j]=(vector[j]+s)%r
        if vector!=item['old_coefficients']:raise ValueError('formal expansion discarded multiplicity/sign')
        signed.append(vector)
    native,rhs=solver.joint_rows(case);rows=[]
    for row in native:
        vector=list(row[:n])
        for coefficient,d in zip(row[n:w],signed,strict=True):
            for j,value in enumerate(d):vector[j]=(vector[j]+coefficient*value)%r
        rows.append(vector+row[w:])
    return rows,rhs


def check(case,prepared,primary,information):
    header=dict(checked=True,input_case_sha256=commitment(case),prepared_sha256=commitment(prepared),
        primary_sha256=commitment(primary),information_sha256=commitment(information),applicable=prepared['auxiliary_role']=='formalpair16')
    if not header['applicable']:
        if prepared['formal_definitions']:raise ValueError('nonformal arm gained definitions')
        return header
    f=prepared['cell']['fixture'];p,r=f['p'],f['r'];n=prepared['norm_size'];nt=case['target_count'];rows,rhs=expand(case,prepared)
    old=[tuple(v['point'])for v in f['factor_base'][:n]]
    seen={min(q,(q[0],-q[1]%p))for q in old}
    for i,item in enumerate(prepared['formal_definitions']):
        point=None
        for j,sign in item['components']:
            q=old[j];q=q if sign==1 else(q[0],-q[1]%p)
            point=check_source.old.add(p,0,f['a'],point,q)
        if point is None:raise ValueError('formal public definition is identity')
        canonical=min(point,(point[0],-point[1]%p))
        if point!=canonical or canonical in seen:raise ValueError('formal public definition sign/old/duplicate class')
        if list(point)!=item['point']or list(point)!=f['factor_base'][n+i]['point']:raise ValueError('formal public native point definition')
        seen.add(canonical)
    points=[tuple(v['point'])for v in f['factor_base'][:n]]+[tuple(v['point'])for v in case['targets']]
    def mul(a,point):
        if a>r//2:point=(point[0],-point[1]%p);a=r-a
        return check_source.old.multiply(p,0,f['a'],a,point)
    for i,(row,value)in enumerate(zip(rows,rhs,strict=True)):
        total=None
        for a,point in zip(row,points,strict=True):
            if a:total=check_source.old.add(p,0,f['a'],total,mul(a,point))
        if total!=mul(value,tuple(f['P'])):raise ValueError('expanded-old public point equation')
    rank=check_source.rank(rows,r)
    if check_source.rank([v+[b]for v,b in zip(rows,rhs,strict=True)],r)!=rank:raise ValueError('expanded affine consistency')
    native,_=solver.joint_rows(case);native_rank=check_source.rank(native,r)
    if native_rank!=rank+len(prepared['formal_definitions']):raise ValueError('expanded/native formal rank bridge')
    masks=[]
    for t in range(nt):
        unit=[0]*(n+nt);unit[n+t]=1;yes=check_source.rank(rows+[unit],r)==rank
        if primary['recoveries'][t]['identifiable']is not yes:raise ValueError('expanded requested-target membership')
        if yes:masks.append(t)
    outer=check_source.rank([v[n:]for v in rows],r)
    common=sum(v[0]=='known'for v in prepared['projection']['native_to_projected'])
    if rank-outer-common!=information['views']['full']['total']['base_rank_after']:raise ValueError('expanded/cancelled old-base information')
    # Definition rows are first after common units and expand to zero. Their
    # identity auxiliary block gives zero old-base information on its own.
    k=len(prepared['known']);size=len(prepared['formal_definitions'])
    if any(any(row)or value for row,value in zip(rows[k:k+size],rhs[k:k+size],strict=True)):raise ValueError('definition-only zero old information')
    return dict(header,expanded_rows=rows,expanded_rhs=rhs,expanded_joint_rank=rank,native_joint_rank=native_rank,
        target_mask=sum(1<<t for t in masks),old_base_rank_after=rank-outer-common,definition_only_auxiliary_rank=size,definition_only_old_base_delta=0,
        public_expanded_rows_checked=len(rows),accepted_definitions_public_checked=size,scope='Independent plain signed old-coefficient/public-point/dense semantic oracle; no extra producer target solver or numeric labels.')

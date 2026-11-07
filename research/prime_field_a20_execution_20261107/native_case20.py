"""Insert one paid definition per auxiliary after common supplied units."""
from deps20 import prior_case,solver


def definition_rows(prepared):
    f=prepared['cell']['fixture'];n=prepared['norm_size'];w=len(f['factor_base']);r=f['r'];rows=[];origins=[]
    for i,item in enumerate(prepared['formal_definitions']):
        if item['auxiliary_index']!=i or len(item['old_coefficients'])!=n or n+i>=w:raise ValueError('formal native definition order/width')
        vector=[(-v)%r for v in item['old_coefficients']]+[int(j==i)for j in range(w-n)]
        rows.append((vector,0));origins.append(dict(kind='formal_definition',auxiliary_index=i,old_components=item['components']))
    return rows,origins


def build(prepared,collected,branch,cache,budget,scope,meter):
    case=prior_case.build(prepared,collected,branch,cache,budget,scope,meter)
    rows,origins=definition_rows(prepared);k=len(prepared['known'])
    if len(case['source'])+len(case['target'])+len(rows)>4096:
        error=ValueError('formal definition matrix size gate');error.partial_case=case;raise error
    case['source'][k:k]=rows;case['source_origins'][k:k]=origins
    meter.other['formal_definition_rows_assembled']+=len(rows);meter.other['matrix_coefficients_copied']+=case['width']*len(rows)
    solver.validate(case);return case


def expected(prepared,collected,branch,cache,budget,scope):
    case=prior_case.expected(prepared,collected,branch,cache,budget,scope)
    n=prepared['norm_size'];w=case['width'];r=case['modulus'];rows=[];origins=[]
    for i,item in enumerate(prepared['formal_definitions']):
        coefficients=[0]*n
        for j,sign in item['components']:coefficients[j]=(coefficients[j]+sign)%r
        if coefficients!=item['old_coefficients']:raise ValueError('independent formal signed old coefficients')
        rows.append(([-v%r for v in coefficients]+[int(j==i)for j in range(w-n)],0))
        origins.append(dict(kind='formal_definition',auxiliary_index=i,old_components=item['components']))
    k=len(prepared['known']);case['source'][k:k]=rows;case['source_origins'][k:k]=origins
    return case

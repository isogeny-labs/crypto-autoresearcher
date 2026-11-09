import resource,signal
resource.setrlimit(resource.RLIMIT_AS,(128*1024**2,128*1024**2))
resource.setrlimit(resource.RLIMIT_CPU,(10,10))
signal.alarm(15)
import json,hashlib
from pathlib import Path
P=Path('/home/ec2-user/crypto-lfd-unbounded-20261109/analysis/semaev-bound-labels-20261109')
B=Path(__file__).parent
ap=P/'finite-selector-controls/retained-control.json'
ep=P/'exact-lfd-controls/complete.json'
raw=ap.read_bytes();expected_raw=ep.read_bytes()
a=json.loads(raw);saved=json.loads(expected_raw)['analysis']
N=a['n_vars']
assert N==4
rows=[]
for row in a['equations']:
 assert row['n_vars']==N
 masks=[int(v,16) for v in row['monomial_masks_hex']]
 assert len(set(masks))==len(masks) and all(0<=v<16 for v in masks)
 rows.append(sum(1<<v for v in masks))
mondegree=[bin(m).count('1') for m in range(16)]
def degree(poly):
 return max((mondegree[m] for m in range(16) if poly>>m&1),default=-1)
def evaluate(poly,assignment):
 return sum(1 for m in range(16) if poly>>m&1 and assignment&m==m)%2
def multiply(poly,var):
 out=0
 for m in range(16):
  if poly>>m&1:out^=1<<(m|(1<<var))
 return out
zeros=[a for a in range(16) if all(evaluate(row,a)==0 for row in rows)]
def enlarge(span,row):
 if row in span:return False
 span.update({v^row for v in tuple(span)})
 assert len(span)<=4096
 return True
observed=[];last=-1
for cap in range(6):
 span={0}
 for row in rows:
  if degree(row)<=cap:enlarge(span,row)
 while True:
  changed=False
  for row in tuple(span):
   if degree(row)<cap:
    for var in range(N):
     if enlarge(span,multiply(row,var)):
      changed=True;break
    if changed:break
  if not changed:break
 # Enumerate the entire ambient polynomial space (at most 65536 functions),
 # independently count its vanishing subspace rather than compute matrix rank.
 monomials=[m for m in range(16) if mondegree[m]<=cap]
 vanishing=0
 for coefficients in range(1<<len(monomials)):
  poly=sum(1<<m for i,m in enumerate(monomials) if coefficients>>i&1)
  if all(evaluate(poly,a)==0 for a in zeros):vanishing+=1
 assert vanishing and vanishing&(vanishing-1)==0
 assert len(span)&(len(span)-1)==0
 rank=len(span).bit_length()-1;ideal=vanishing.bit_length()-1
 missing=rank<ideal
 if missing:last=cap
 result={'cap':cap,'monomial_count':len(monomials),'closure_rank':rank,'ideal_intersection_dimension':ideal,'evaluation_rank':len(monomials)-ideal,'missing_ideal_consequence':missing}
 observed.append(result)
 print(json.dumps(result),flush=True)
assert len(zeros)==saved['zero_count']==4
assert last+1==saved['exact_lfd']==4
for got,want in zip(observed,saved['caps']):
 for key,value in got.items():assert want[key]==value,(key,got,want)
assert len(observed)==len(saved['caps'])==6
receipt={'status':'passed','scope':'single hand-authored software fixture, not production or scientific campaign','method':'explicit set-span saturation and exhaustive vanishing-polynomial count; no reference imports','limits':{'cpu_seconds':10,'wall_seconds':15,'address_space_bytes':128*1024**2,'attempts':1},'retained_sha256':hashlib.sha256(raw).hexdigest(),'comparison_sha256':hashlib.sha256(expected_raw).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'zero_assignments':zeros,'exact_lfd':last+1,'caps':observed,'all_cap_fields_match':True}
with (B/'receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('PASS exact_lfd=4 zero_count=4 all_caps_match',flush=True)

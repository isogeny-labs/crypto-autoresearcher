"""Independent public group equations and exact prepared setup witnesses."""
from pathlib import Path
import json

def need(v,m):
 if not v:raise ValueError(m)
def point(x,c):
 p=c['p'];need(type(x) is list and len(x)==2 and all(type(v) is int and 0<=v<p for v in x),'public point range');x=tuple(x);need((x[1]*x[1]-x[0]**3-c['a']*x[0]-c['b'])%p==0,'public point curve');return x
def add(P,Q,c):
 if P is None:return Q
 if Q is None:return P
 p=c['p'];x,y=P;u,v=Q
 if x==u and (y+v)%p==0:return None
 s=((3*x*x+c['a'])*pow(2*y,-1,p) if P==Q else (v-y)*pow(u-x,-1,p))%p
 z=(s*s-x-u)%p;return z,(s*(x-z)-y)%p
def mul(n,P,c):
 Q=None
 while n:
  if n&1:Q=add(Q,P,c)
  P=add(P,P,c);n>>=1
 return Q
def setup_reason(c,B,alpha):
 p=c['p'];r=c['r']
 if p%4!=3 or r<=2 or r%2==0 or r==p:return 'DOMAIN_UNSUPPORTED'
 if B[1]==0:return 'ZERO_BASE_Y'
 def step(P,Q):
  if P is None or Q is None or (P[0]==Q[0] and (P[1]+Q[1])%p==0):return add(P,Q,c),0
  slope=((3*P[0]*P[0]+c['a'])*pow(2*P[1],-1,p) if P==Q else (Q[1]-P[1])*pow(Q[0]-P[0],-1,p))%p
  return add(P,Q,c),slope
 carry=B;coefficient=0
 for bit in bin(r)[3:]:
  carry,slope=step(carry,carry);coefficient=(2*coefficient+slope)%p
  if bit=='1':carry,slope=step(carry,B);coefficient=(coefficient+slope)%p
 need(carry is None,'public setup declared subgroup');z=(-coefficient*pow(r,-1,p))%p
 if z==0:return 'ZERO_BASE_Z'
 if (1+alpha)*z%p==0:return 'ZERO_ANCHOR'
 return None
def validate_public(public):
 seen=set()
 for row in public['curves']:
  c=row['model'];p=c['p'];r=c['r'];need(p>3 and r>1 and all(p%d for d in range(2,__import__('math').isqrt(p)+1)) and all(r%d for d in range(2,__import__('math').isqrt(r)+1)),'public field/order primes');need((4*c['a']**3+27*c['b']**2)%p!=0,'public singular curve');need(0<=c['a']<p and 0<=c['b']<p,'public canonical model');G=point(row['base'],c);need(mul(r,G,c) is None,'public base subgroup');need(row['curve_id'] not in seen,'public duplicate curve');seen.add(row['curve_id'])
  for t in row['targets']:need(mul(r,point(t['point'],c),c) is None,'public target subgroup')
def verify(public,plan,raw,bsgs):
 validate_public(public);curves={c['curve_id']:c for c in public['curves']};want={(j['curve_id'],j['arm_id']) for j in plan['jobs']};seen=set()
 import framing
 lines=framing.logical_file(Path(raw)/'setups.jsonl').open('rb')
 for line in lines:
  row=json.loads(line);key=(row['curve_id'],row['arm_id']);need(key in want and key not in seen,'public exact setup membership');seen.add(key);c=curves[key[0]];model=c['model'];aid=key[1];circuit=int(aid[7]);a=int(aid.split('.a')[1]);alpha,beta=((1,-4),(-2,-1))[circuit-1]
  need(row['model']==model and row['base']==c['base'],'public exact setup input');need(row['arm']=={'id':aid,'kind':'candidate','alpha':alpha,'beta':beta,'base_multiplier':a},'public exact setup arm');need(point(row['prepared_base'],model)==mul(a,point(c['base'],model),model),'public prepared base equation');need(row['setup_reason']==setup_reason(model,point(row['prepared_base'],model),alpha),'public exact setup reason')
 lines.close();need(seen==want,'public missing setup')
 wanted={(c['curve_id'],t['target_id']):t for c in public['curves'] for t in c['targets']};seen=set()
 for row in bsgs['rows']:
  key=(row['curve_id'],row['target_id']);need(key in wanted and key not in seen,'public exact BSGS target membership');seen.add(key);c=curves[key[0]];a=row['answer'];s=a.get('scalar');need(a.get('status')=='success' and type(s) is int and 1<=s<c['model']['r'],'public scalar range');need(row['point']==wanted[key]['point'],'public exact BSGS target');need(mul(s,point(c['base'],c['model']),c['model'])==point(wanted[key]['point'],c['model']),'public scalar equation')
 need(seen==set(wanted),'public missing BSGS target')
 return {'public_equations_recomputed':True,'setups':len(want),'targets':len(wanted)}

#!/usr/bin/env python3
"""Independent finite witness checker; no producer modules imported.
SEC1 v2 section 2.2.1 / RFC6090 section3 and F.1 affine formulas.
Run once: python verifier.py BUNDLE OUTPUT SCRATCH
The start file predates all setup; caps never reset. No production trial.
"""
import sys,json,time,datetime,hashlib,pathlib,math,resource,collections,platform,traceback
B,O,S=map(pathlib.Path,sys.argv[1:]); START=json.load(open('/workspace/witness-review-start-ba620e.json')); STOP=START['monotonic_stop']
LIMIT=500000; C=collections.Counter(); CACHE={}; GAPS=[]; HASHES=[]; PARSE={}; EVENTS=[]; INV={}; DOMAINS={}; TRACES={}; JOINS=[]
PLAN='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-9576ee/recovery-v3/independent-witness-review/'
PIN='23f44595bd0b6fb4f08b40125d8073d34ded9ea8e6a2ddb5e22edd49edda1a1e'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def guard():
 if time.monotonic()>STOP-100: raise RuntimeError('whole-review deadline reserve reached; no extension')
 if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>4*1024*1024: raise RuntimeError('4GiB RSS cap')
def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d: raise ValueError('duplicate JSON key '+k)
  d[k]=v
 return d
def load(s):
 return json.loads(s.decode('utf-8'),object_pairs_hook=unique,parse_constant=lambda t:(_ for _ in ()).throw(ValueError('nonfinite '+t)))
def h(b):return hashlib.sha256(b).hexdigest()
def small(p):
 x=(B/p).read_bytes();return load(x)
def stream(p):
 st={'records':0,'bytes':0,'lf_complete_records':0,'malformed':[],'tail':None};PARSE[p]=st;dg=hashlib.sha256()
 with open(B/p,'rb') as f:
  for n,line in enumerate(f,1):
   guard();dg.update(line);st['bytes']+=len(line)
   if not line.endswith(b'\n'):
    st['tail']={'line':n,'bytes':len(line),'sha256':h(line)};GAPS.append({'tail':p,**st['tail']});continue
   try:v=load(line)
   except Exception as e:
    g={'line':n,'sha256':h(line),'error':str(e)};st['malformed'].append(g);GAPS.append({'parse':p,**g});raise
   st['records']+=1;st['lf_complete_records']+=1
   yield n,h(line),v
 st['sha256']=dg.hexdigest()
def integer(n):return type(n) is int
def prime(n):
 if not integer(n) or n<2 or n>=2**64: raise ValueError('primality outside deterministic <2^64 bound')
 if n in (2,3,5,7,11,13,17,19,23,29,31,37):return True
 if any(n%p==0 for p in (2,3,5,7,11,13,17,19,23,29,31,37)):return False
 d=n-1;s=0
 while d%2==0:s+=1;d//=2
 for a in (2,325,9375,28178,450775,9780504,1795265022):
  a%=n
  if not a:continue
  x=pow(a,d,n)
  if x in (1,n-1):continue
  for _ in range(s-1):
   x=x*x%n
   if x==n-1:break
  else:return False
 return True
def inv(a,p):
 a%=p;t,nt=0,1;r,nr=p,a
 while nr:
  q=r//nr;t,nt=nt,t-q*nt;r,nr=nr,r-q*nr
 if r!=1:raise ValueError('noninvertible denominator')
 return t%p
def point(P,c):
 p,a,b,_=c
 return isinstance(P,(list,tuple)) and len(P)==2 and all(integer(v) and 0<=v<p for v in P) and (P[1]*P[1]-P[0]**3-a*P[0]-b)%p==0
def add(P,Q,c):
 p,a,_,_=c
 if P is None:return Q
 if Q is None:return P
 x,y=P;u,v=Q
 if x==u and (y+v)%p==0:return None
 m=((3*x*x+a)*inv(2*y,p) if P==Q else (v-y)*inv(u-x,p))%p
 z=(m*m-x-u)%p
 return z,(m*(x-z)-y)%p
def mul(n,P,c,kind):
 guard();C['mul_requests']+=1;C[kind+'_requests']+=1
 key=(c,P,n)
 if key in CACHE:C['mul_cache_hits']+=1;return CACHE[key]
 if C['scalar_multiplications']+C['equation_evaluations']>=LIMIT:raise RuntimeError('500000 total evaluation cap')
 C['scalar_multiplications']+=1;C[kind+'_multiplications']+=1
 if not integer(n) or n<0:raise ValueError('negative/noninteger scalar')
 R=None;T=P;k=n
 while k:
  if k&1:R=add(R,T,c)
  T=add(T,T,c);k>>=1
 CACHE[key]=R;return R
def eq(P,Q,kind):
 guard()
 if C['scalar_multiplications']+C['equation_evaluations']>=LIMIT:raise RuntimeError('500000 total evaluation cap')
 C['equation_evaluations']+=1;C[kind+'_equations']+=1
 return P==Q
def domain(cid,tid):
 key=(cid,tid)
 if key in DOMAINS:C['domain_cache_hits']+=1;return DOMAINS[key]
 cv=CURVES[cid];m=cv['model'];c=tuple(m[k] for k in ('p','a','b','r'));p,a,b,r=c;G=tuple(cv['base']);Q=tuple(TARGETS[key]['point'])
 d={'curve_id':cid,'target_id':tid,'p':p,'a':a,'b':b,'r':r,'G':G,'Q':Q,'prime_method':'deterministic Miller-Rabin fixed seven bases for n<2^64'}
 assert prime(p) and p>3 and prime(r)
 assert all(integer(v) and 0<=v<p for v in (a,b)) and (4*a**3+27*b*b)%p!=0
 assert point(G,c) and point(Q,c)
 d['rG']=mul(r,G,c,'domain');d['rQ']=mul(r,Q,c,'domain')
 assert eq(d['rG'],None,'domain') and eq(d['rQ'],None,'domain')
 d['valid']=True;DOMAINS[key]=d;return d
def claim(x,base,kind,k=None):
 e=dict(base,claim_field=kind,x=x);EVENTS.append(e)
 try:
  d=domain(base['curve_id'],base['target_id']);c=tuple(d[q] for q in ('p','a','b','r'));r=d['r'];G=tuple(d['G']);Q=tuple(d['Q'])
  if not integer(x) or not 0<=x<r:raise ValueError('original scalar not canonical integer in [0,r)')
  lhs=mul(x,G,c,'original');e.update(original_lhs=lhs,original_rhs=Q,original_valid=eq(lhs,Q,'original'))
  if k is not None:
   e['k']=k;a=base['base_multiplier'];b=base['target_multiplier']
   if not integer(k) or not 0<=k<r:raise ValueError('transformed scalar not canonical integer in [0,r)')
   if not integer(a) or not integer(b) or a%r==0 or b%r==0:raise ValueError('invalid/noninvertible blinding')
   normalized=a*k*inv(b,r)%r;e['derived_normalized_x']=normalized;e['normalization_consistent']=x==normalized
   aG=mul(a%r,G,c,'transform_base');bQ=mul(b%r,Q,c,'transform_target');klhs=mul(k,aG,c,'transformed')
   e.update(aG=aG,bQ=bQ,transformed_lhs=klhs,transformed_rhs=bQ,transformed_valid=eq(klhs,bQ,'transformed'))
  e['outcome']='valid' if e['original_valid'] and e.get('transformed_valid',True) and e.get('normalization_consistent',True) else 'invalid'
  if e['original_valid']:
   mutation=(x+1)%r;ml=mul(mutation,G,c,'mutation');mv=eq(ml,Q,'mutation');e.update(mutation_scalar=mutation,mutation_lhs=ml,mutation_rhs=Q,mutation_accepted=mv)
   if mv:GAPS.append({'mutation_accepted':base})
  ik=(base['curve_id'],base['target_id'],x)
  if ik not in INV:INV[ik]={'curve_id':ik[0],'target_id':ik[1],'scalar':x,'G':G,'Q':Q,'original_lhs':lhs,'original_valid':e['original_valid'],'event_indices':[]}
  INV[ik]['event_indices'].append(len(EVENTS)-1)
 except Exception as z:
  if isinstance(z,RuntimeError):raise
  e['outcome']='undefined';e['reason']=str(z);GAPS.append({'undefined_event':len(EVENTS)-1,'reason':str(z)})
 return e
CONTROLS={};CELLCOUNTS=collections.Counter();TRACECOUNTS=collections.Counter();WORDS=collections.Counter();MISMATCH=[];CELLS=[];status='inconclusive';error=None
try:
 planbytes=(B/(PLAN+'review-plan.json')).read_bytes();assert h(planbytes)==PIN
 manifest=small(PLAN+'input-manifest.json');sem=small(PLAN+'witness-field-semantics.json');refs=small(PLAN+'primary-reference-binding.json')
 assert h((B/(PLAN+'primary-reference-binding.json')).read_bytes())=='58735eb49d7081d688f63014a9a3aae4da1f4186268e00b69c5b72ed4f598876'
 for ref in refs['references']:
  data=(B/ref['path']).read_bytes();assert len(data)==ref['bytes'] and h(data)==ref['sha256'];HASHES.append({'path':ref['path'],'bytes':len(data),'sha256':h(data),'matches':True})
 # Source schema fixed in semantic-freeze before any candidate/group equation execution.
 pp=manifest['inputs'][0];raw=(B/pp['logical_path']).read_bytes();public=load(raw);assert len(raw)==pp['payload_bytes'] and h(raw)==pp['payload_sha256'];HASHES.append({'path':pp['logical_path'],'bytes':len(raw),'sha256':h(raw),'matches':True});del raw
 assert public['schema']=='controlled-followup-v5.public-input/v1'
 CURVES={};TARGETS={}
 for cv in public['public']['curves']:
  cid=cv['curve_id'];assert cid not in CURVES;CURVES[cid]=cv
  for t in cv['targets']:
   key=cid,t['target_id'];assert key not in TARGETS;TARGETS[key]=t
 # Ignore public plan expected counts: no denominator is used or reported.
 del public
 for n,sha,t in stream(manifest['inputs'][1]['logical_path']):
  assert t['schema']=='classical.ecdlp.controlled-followup.trace/v1'
  tid=t['trace_id'];assert tid not in TRACES
  TRACES[tid]={q:t[q] for q in ('trace_id','curve_id','target_id','base_multiplier','target_multiplier','target','arm_id')};TRACES[tid].update(source_line=n,source_sha256=sha)
  TRACECOUNTS['records']+=1
 for z in manifest['inputs'][1:2]:
  st=PARSE[z['logical_path']];assert st['bytes']==z['payload_bytes'] and st['sha256']==z['payload_sha256'];HASHES.append({'path':z['logical_path'],'bytes':st['bytes'],'sha256':st['sha256'],'matches':True})
 # Controls before candidate checks, with known external point and wrong target -Q.
 c=(17,2,2,19);g=(5,1);q=(6,3)
 assert prime(17) and prime(19) and point(g,c) and point(q,c) and (4*2**3+27*2**2)%17
 CONTROLS={'positive_2G':mul(2,g,c,'control'),'rG':mul(19,g,c,'control'),'rQ':mul(19,q,c,'control'),'wrong_scalar_3G':mul(3,g,c,'control'),'wrong_target':(6,14),'offcurve_0_0_domain_accepted':point((0,0),c)}
 CONTROLS['pass']=eq(CONTROLS['positive_2G'],q,'control') and eq(CONTROLS['rG'],None,'control') and eq(CONTROLS['rQ'],None,'control') and not eq(CONTROLS['wrong_scalar_3G'],q,'control') and not eq(CONTROLS['positive_2G'],(6,14),'control') and not CONTROLS['offcurve_0_0_domain_accepted']
 assert CONTROLS['pass']
 cellids=set()
 for n,sha,cell in stream(manifest['inputs'][2]['logical_path']):
  assert cell['schema']=='classical.ecdlp.controlled-followup.decoder-cell/v1'
  cellid=cell['cell_id'];assert cellid not in cellids;cellids.add(cellid);CELLCOUNTS['records']+=1;CELLCOUNTS['status_'+cell['status']]+=1
  traceid=cell['trace_id'];t=TRACES.get(traceid)
  if t is None:GAPS.append({'join':'missing trace','cell_id':cellid,'line':n});raise ValueError('cell without trace')
  cid,tid=t['curve_id'],t['target_id'];assert cid in CURVES and (cid,tid) in TARGETS
  if t['target']!=TARGETS[(cid,tid)]['point']:GAPS.append({'join':'trace/public target mismatch','trace':t,'cell_id':cellid});raise ValueError('target mismatch')
  base={'cell_id':cellid,'cell_line':n,'cell_sha256':sha,'trace_id':traceid,'trace_line':t['source_line'],'trace_sha256':t['source_sha256'],'curve_id':cid,'target_id':tid,'base_multiplier':t['base_multiplier'],'target_multiplier':t['target_multiplier'],'cell_status':cell['status']}
  assert isinstance(cell['words'],list) and isinstance(cell['recovered_scalars'],list)
  claimed=[];wi=[]
  for j,w in enumerate(cell['words']):
   WORDS['records']+=1;WORDS['status_'+w['status']]+=1
   if w['status']=='RECOVERED':
    WORDS['explicit_RECOVERED']+=1
    b2=dict(base,word_index=j,word_status=w['status']);e=claim(w.get('candidate_scalar'),b2,'words[].candidate_scalar',w.get('candidate_scalar_prime'));wi.append(len(EVENTS)-1);claimed.append(w.get('candidate_scalar'))
    if w.get('candidate_scalar_prime') is None:e['outcome']='undefined';e['reason']='RECOVERED word missing transformed scalar';GAPS.append({'undefined_event':len(EVENTS)-1,'reason':e['reason']})
  if cell.get('scalar') is not None:
   claim(cell['scalar'],base,'scalar');claimed.append(cell['scalar']);CELLCOUNTS['nonnull_scalar']+=1
  for j,x in enumerate(cell['recovered_scalars']):
   claim(x,dict(base,recovered_scalar_index=j),'recovered_scalars[]');claimed.append(x);CELLCOUNTS['recovered_scalars_values']+=1
  if claimed:
   # Scalar is optional when multiple values exist, but nonnull claims must agree with RECOVERED set.
   wx=[cell['words'][j]['candidate_scalar'] for j in range(len(cell['words'])) if cell['words'][j]['status']=='RECOVERED']
   rs=cell['recovered_scalars'];issues=[]
   if set(wx)!=set(rs):issues.append('RECOVERED words versus recovered_scalars set mismatch')
   if cell['scalar'] is not None and cell['scalar'] not in wx:issues.append('cell scalar absent from RECOVERED words')
   if issues:MISMATCH.append(dict(base,issues=issues,recovered_word_scalars=wx,scalar=cell['scalar'],recovered_scalars=rs))
   CELLS.append(dict(base,word_claim_event_indices=wi,recovered_word_scalars=wx,scalar=cell['scalar'],recovered_scalars=rs,field_issues=issues))
 for z in manifest['inputs'][2:]:
  st=PARSE[z['logical_path']];assert st['bytes']==z['payload_bytes'] and st['sha256']==z['payload_sha256'];HASHES.append({'path':z['logical_path'],'bytes':st['bytes'],'sha256':st['sha256'],'matches':True})
 status='complete' if not GAPS else 'inconclusive'
except Exception as z:
 error={'type':type(z).__name__,'message':str(z),'traceback':traceback.format_exc()};GAPS.append(error)
finally:
 counts=collections.Counter(e['outcome'] for e in EVENTS)
 out={'schema':'independent.finite-witness-checks/v1','task_id':'TASK-20261105-ba620e','status':status,'error':error,'external_plan_sha256':PIN,'self_verifier_sha256':h(pathlib.Path(__file__).read_bytes()),'semantic_freeze':json.load(open(S/'semantic-freeze.json')),'start':START,'arithmetic_finished_utc':now(),'arithmetic_elapsed_seconds':time.monotonic()-START['monotonic_start'],'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'platform':platform.python_version(),'input_hashes':HASHES,'parsing':PARSE,'counts':dict(C),'cap_accounting':{'limit':LIMIT,'actual_total_counted':C['scalar_multiplications']+C['equation_evaluations'],'conservative_rule':'each actual scalar multiply and every equation equality separately counted; cache requests/hits separately reported; no group-add cost used as scalar equation count','whole_wall_seconds_limit':600,'memory_limit_gib':4,'original_fixed_stop':START['utc_stop']},'controls':CONTROLS,'cell_event_counts':dict(CELLCOUNTS),'trace_counts':dict(TRACECOUNTS),'word_event_counts':dict(WORDS),'claim_event_outcomes':dict(counts),'claimed_cells':CELLS,'claim_events':EVENTS,'distinct_finite_inventory':list(INV.values()),'inventory_counts':{'distinct_curve_target_scalar':len(INV),'duplicate_claim_events':sum(len(v['event_indices'])-1 for v in INV.values())},'domains':list(DOMAINS.values()),'mismatches':MISMATCH,'gaps':GAPS,'all_invalid_undefined_events':[i for i,e in enumerate(EVENTS) if e['outcome']!='valid'],'independence':{'producer_arithmetic_imported':False,'read_sibling_reports':False,'prohibited_reads':[]},'canonical_graphs':'No canonical graph inspected: outside allowed bundle. No canonical graph changed; arithmetic finite-witness review only.'}
 (O/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k] for k in ('status','claim_event_outcomes','inventory_counts','counts','cap_accounting','rss_peak_kib','arithmetic_elapsed_seconds','error')}))

"""Compare a frozen public table; no selection predicates or point counting."""
import csv, hashlib, importlib.util, json, re
from pathlib import Path
B=Path(__file__).resolve().parent
R=B.parents[1]
old=R/'research/nist_seed_1997_selection_extension_20261023/external_crosscheck/check.py'
spec=importlib.util.spec_from_file_location('prior_parser',old)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B/'pinned.txt')==m.EXTERNAL_SHA256==sha(B/'current.txt')
ext=m.parse_external((B/'pinned.txt').read_text())
canonical=R/'research/nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/prior-rows.json'
cohort=json.loads(canonical.read_text()); byseed={x['seed_hex'].lower():x for x in cohort}
rawpath=R/'research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json'
raw=json.loads(rawpath.read_text()); sigs={x['curve_uid']:x for x in raw['rows']}
replay=json.loads((B/'replay.json').read_text()); reps={x['curve_uid']:x for x in replay['rows']}
# Parse field and a from the same candidate blocks, without executing source text.
fields={};cur=None
for line in (B/'pinned.txt').read_text().splitlines():
 hit=re.search(r'candidate #(\d+)',line)
 if hit:cur=int(hit[1]);fields[cur]={}
 if cur is None:continue
 if re.match(r'\s*p:',line):
  expr=line.split(':',1)[1].split('(')[0].replace(' ','')
  terms=re.findall(r'[+-]?(?:2\^\d+|1)',expr)
  assert ''.join(terms)==expr
  fields[cur]['p']=sum((-1 if t.startswith('-') else 1)*((1<<int(t.split('^')[1])) if '^' in t else 1) for t in terms)
 if re.match(r'\s*a:',line):fields[cur]['a']=int(line.split(':',1)[1])
 if re.match(r'\s*c:',line):fields[cur]['c']=int(line.split(':',1)[1],16)
rows=[];symbols=0
for ordinal,e in ext.items():
 c=byseed[e['seed_hex'].lower()];uid=c['curve_uid']; p=int(c['p']); n=int(c['n']); b=int(c['b']); cb=int(c['c'])
 assert c['ordinal']==ordinal and fields[ordinal]=={'p':p,'a':-3,'c':cb}
 assert int(e['n_hex'],16)==n and int(e['trace_hex_signed'],16)==p+1-n
 eb=int(e['b_hex'],16)
 assert eb==b or (p.bit_length()==224 and eb==(-b)%p)
 assert (cb*eb*eb+27)%p==0
 t=p+1-n;D=t*t-4*p;r=sigs[uid];M=1;cut=None
 for ell,sign in zip(raw['odd_primes'],r['signature']):
  v=pow(D%ell,(ell-1)//2,ell);s='0' if not v else '+' if v==1 else '-'
  assert sign==s;symbols+=1
  if s=='+':M*=ell
  if cut is None and M*M>16*p:cut=ell
 assert cut==r['cutoff_ell']
 assert set(e['listed_elkies'])=={l for l,s in zip(raw['odd_primes'],r['signature']) if l<100 and s in '+0'}
 assert set(e['listed_atkin'])=={l for l,s in zip(raw['odd_primes'],r['signature']) if l<100 and s=='-'}
 witness=None
 if eb!=b:
  d=2
  while pow(d,(p-1)//2,p)!=p-1:d+=1
  u=pow(d,(p-1)//4,p)
  assert pow(u,4,p)==1 and b*pow(u,6,p)%p==eb
  witness={'nonsquare':d,'u':str(u),'map':'x_new=u^2*x, y_new=u^3*y','u_fourth_mod_p':pow(u,4,p)}
 q=reps[uid]
 rows.append({'name':c['name'],'curve_uid':uid,'seed_hex':c['seed_hex'],'ordinal':ordinal,'field_bits':p.bit_length(),'label':c['label'],'field_match':True,'a_match':True,'c_match':True,'seed_match':True,'order_match':True,'trace_match':True,'b_model':'identical' if eb==b else 'opposite_isomorphic','isomorphism':witness,'source_cutoff':e['reported_cutoff'],'literal_cutoff':q['replay_literal_formula_with_ramified'],'integer_convention_cutoff':q['replay_integer_rule_with_ramified'],'strict_cutoff':cut,'ramified_listed_as_elkies':q['ramified_listed_elkies_under100']})
assert len(rows)==19 and len({r['curve_uid'] for r in rows})==19
missing=[{'name':c['name'],'curve_uid':c['curve_uid']} for c in cohort if c['curve_uid'] not in {r['curve_uid'] for r in rows}]
assert len(missing)==2 and all(x['label']=='published' for x in cohort if x['curve_uid'] in {z['curve_uid'] for z in missing})
out={'status':'PASS','symbols_checked':symbols,'rows':rows,'not_in_external_table':missing,'input_hashes':{str(p.relative_to(R)):sha(p) for p in (canonical,rawpath,old,B/'pinned.txt',B/'current.txt',B/'replay.json')},'scope':'Identity and SEA definition reconciliation only; no predicate search or historical-use claim.'}
(B/'comparison.json').write_text(json.dumps(out,indent=2)+'\n')
with (B/'comparison.csv').open('w') as f:
 keys=['name','curve_uid','seed_hex','ordinal','field_bits','label','b_model','source_cutoff','literal_cutoff','integer_convention_cutoff','strict_cutoff']
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:r[k] for k in keys} for r in rows)
print(json.dumps({'status':'PASS','curves':len(rows),'symbols_checked':symbols,'not_in_external_table':missing,'isomorphisms':[r['name'] for r in rows if r['isomorphism']]}))

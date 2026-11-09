"""Serialize symbolic identities; refuses to overwrite an existing artifact."""
import argparse,json
from pathlib import Path
from constructions import invariant_eliminant,compressed_invariant_eliminant
p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
rows=[]
for k in (2,3):
 f=invariant_eliminant(k); q=compressed_invariant_eliminant(k)
 rows.append({'k':k,'variables':list(map(str,f.gens)), 'degrees':list(map(int,f.degree_list())),
              'total_degree':int(f.total_degree()),'terms':len(f.terms()),'expression':str(f.as_expr()),
              'compressed_variables':list(map(str,q.gens)), 'compressed_degrees':list(map(int,q.degree_list())),
              'compressed_total_degree':int(q.total_degree()),'compressed_expression':str(q.as_expr())})
with a.output.open('x') as out: out.write(json.dumps(rows,indent=2)+'\n')

"""Append fresh A10 curves, public knowledge and all solver certificates to v12."""
import argparse,gzip,hashlib,json,sqlite3,subprocess
from pathlib import Path
from common import load,digest,write_once,ROOT

def code(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def main():
 p=argparse.ArgumentParser()
 for n in ('parent','run','inputs','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
 if a.out.exists():raise ValueError('fresh database required')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();relative=str(Path(__file__).resolve().relative_to(ROOT))
 if hashlib.sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=digest(Path(__file__)):raise ValueError('commit builder first')
 parenthash=digest(a.parent);prior=sqlite3.connect('file:'+str(a.parent.resolve())+'?mode=ro',uri=True);con=sqlite3.connect(a.out)
 before={n:{code(list(row)) for row in prior.execute('SELECT * FROM '+n)} for (n,) in prior.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='metadata'")}
 metadata=prior.execute('SELECT * FROM metadata ORDER BY key').fetchall();prior.backup(con);con.execute('PRAGMA foreign_keys=ON')
 if con.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(code('prime-field-database/v12'),):raise ValueError('v12 parent required')
 con.executescript('''CREATE TABLE ap_holdout_studies(execution_id TEXT PRIMARY KEY REFERENCES executions,source_path TEXT NOT NULL REFERENCES sources,rules_json TEXT NOT NULL,analysis_json TEXT NOT NULL);
 CREATE TABLE ap_holdout_cells(id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES ap_holdout_studies,base_sha256 TEXT NOT NULL REFERENCES bases,source_path TEXT NOT NULL REFERENCES sources);
 CREATE TABLE ap_holdout_schedules(cell_id TEXT NOT NULL REFERENCES ap_holdout_cells,arm TEXT NOT NULL,order_json TEXT NOT NULL,constructor_json TEXT NOT NULL,PRIMARY KEY(cell_id,arm));
 CREATE TABLE ap_holdout_known_points(cell_id TEXT NOT NULL,arm TEXT NOT NULL,point_index INTEGER NOT NULL,knowledge_json TEXT NOT NULL,PRIMARY KEY(cell_id,arm,point_index),FOREIGN KEY(cell_id,arm) REFERENCES ap_holdout_schedules);
 CREATE TABLE ap_holdout_targets(cell_id TEXT NOT NULL REFERENCES ap_holdout_cells,target_index INTEGER NOT NULL,point_json TEXT NOT NULL,PRIMARY KEY(cell_id,target_index));
 CREATE TABLE ap_holdout_cases(execution_id TEXT NOT NULL REFERENCES ap_holdout_studies,instance_id INTEGER NOT NULL,descriptor_json TEXT NOT NULL,case_json TEXT NOT NULL,verification_json TEXT NOT NULL,PRIMARY KEY(execution_id,instance_id));
 CREATE TABLE ap_holdout_solver_arms(execution_id TEXT NOT NULL,instance_id INTEGER NOT NULL,solver TEXT NOT NULL,summary_json TEXT NOT NULL,certificates_json TEXT NOT NULL,PRIMARY KEY(execution_id,instance_id,solver),FOREIGN KEY(execution_id,instance_id) REFERENCES ap_holdout_cases);''')
 def source(path,kind):
  name=str(path.resolve().relative_to(ROOT));expected=(digest(path),path.stat().st_size);old=con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
  if old and old!=expected:raise ValueError('historical source changed')
  con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind));return name
 source(a.parent,'parent_database_v12');source(Path(__file__),'ap_holdout_builder');inputpath=source(a.inputs,'frozen_ap_holdout_rules')
 e=load(a.run/'export.json');execution=load(a.run/'execution.json');analysis=load(a.run/'analysis.json');rules=load(a.inputs);exportpath=source(a.run/'export.json','unified_ap_holdout_export')
 for item in e['files']:
  path=(a.run/item['path']).resolve();path.relative_to(a.run.resolve())
  if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('export file binding')
  source(path,'export_bound_holdout_file')
 eid=str(a.run.resolve().relative_to(ROOT));con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],e['protocol']['sha256'],1,0,code(execution),exportpath));con.execute('INSERT INTO ap_holdout_studies VALUES (?,?,?,?)',(eid,inputpath,code(rules),code(analysis)))
 newcurves=0;newtargets=0;index=0
 for field in rules['fields']:
  for ci in range(rules['curves_per_field']):
   name='p'+str(field['p'])+'-i'+str(ci);path=a.run/'raw'/(name+'.collection.json');path=path if path.is_file() else Path(str(path)+'.gz')
   if path.is_file() and analysis['generation_valid']:
    data=load(path);cell=data['cell'];raw=data['collection'];f=cell['fixture'];uid=f['ec1']['curve_uid'];key=hashlib.sha256(code(dict(schema='ap-holdout-base/v1',curve_uid=uid,atoms=f['factor_base'],projection=cell['projection'])).encode()).hexdigest();cid=eid+':'+name
    con.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',(uid,str(f['p']),str(f['a']),str(f['b']),str(f['r']),code(f['P'])))
    con.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(key,uid,f['uid'],len(f['factor_base']),cell['projection']['U'],'ap-holdout-base/v1:freshnormatoms/fixed1..64projection',str(path.resolve().relative_to(ROOT))))
    con.execute('INSERT INTO ap_holdout_cells VALUES (?,?,?,?)',(cid,eid,key,str(path.resolve().relative_to(ROOT))));newcurves+=1
    for arm,order in raw['selection']['orders'].items():
     rec=raw['arms'][arm];con.execute('INSERT INTO ap_holdout_schedules VALUES (?,?,?,?)',(cid,arm,code(order),code(rec['selection'])))
     for j,point in enumerate(rec['knowledge']):con.execute('INSERT INTO ap_holdout_known_points VALUES (?,?,?,?)',(cid,arm,j,code(point)))
    for target in raw['target_generation']['targets']:con.execute('INSERT INTO ap_holdout_targets VALUES (?,?,?)',(cid,target['index'],code(target['point'])));newtargets+=1
   path=a.run/'raw'/(name+'.json');path=path if path.is_file() else Path(str(path)+'.gz')
   records=[] if not path.is_file() else load(path)['records'];lookup={(v['descriptor']['arm'],v['descriptor']['prefix'],v['descriptor']['scope']):v for v in records}
   for arm in [kind+str(seed) for seed in rules['seeds'] for kind in ('ap','hash')]:
    for prefix in rules['prefixes']:
     for scope in rules['scopes']:
      rec=lookup.get((arm,prefix,scope))
      if rec:
       con.execute('INSERT INTO ap_holdout_cases VALUES (?,?,?,?,?)',(eid,index,code(rec['descriptor']),code(rec['case']),code(rec['verification'])))
       for result in rec['results']:
        summary=next(v for v in analysis['cells'] if v['instance_id']==str(index) and v['arm']==result['arm'])
        con.execute('INSERT INTO ap_holdout_solver_arms VALUES (?,?,?,?,?)',(eid,index,result['arm'],code(summary),code(result)))
      index+=1
 con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v12_metadata',code(metadata)))
 for k,v in [('schema','prime-field-database/v13'),('builder_sha256',digest(Path(__file__))),('schema_sha256',hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest())]:con.execute('UPDATE metadata SET value=? WHERE key=?',(code(v),k))
 preserved={n:rows.issubset({code(list(row)) for row in con.execute('SELECT * FROM '+n)}) for n,rows in before.items()}
 if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('historical rows/FK failure')
 con.commit()
 if con.execute('PRAGMA integrity_check').fetchone()!=('ok',):raise ValueError('database integrity')
 counts={n:con.execute('SELECT COUNT(*) FROM '+n).fetchone()[0] for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")};con.close();prior.close()
 if digest(a.parent)!=parenthash:raise ValueError('parent changed')
 data=a.out.read_bytes();archive=Path(str(a.out)+'.gz')
 with archive.open('xb') as f:f.write(gzip.compress(data,compresslevel=6,mtime=0))
 if gzip.decompress(archive.read_bytes())!=data:raise ValueError('gzip roundtrip')
 (a.out.parent/'.gitignore').write_text('/'+a.out.name+'\n')
 write_once(a.out.parent/'generation-v13.json',dict(schema='prime-field-database-receipt/v13',builder_commit=commit,parent_unchanged=True,parent_sha256=parenthash,integrity_check='ok',foreign_key_findings=[],historical_tables_preserved=preserved,counts=counts,new_native_executions=1,new_independent_curves=newcurves,new_independent_targets=newtargets,panel_complete=analysis['panel_complete'],original=dict(path=str(a.out),sha256=digest(a.out),bytes=len(data)),archive=dict(path=str(archive),sha256=digest(archive),bytes=archive.stat().st_size)))
 print(json.dumps(dict(counts=counts,archive=str(archive))))
if __name__=='__main__':main()

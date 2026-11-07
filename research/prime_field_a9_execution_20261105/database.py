"""Append cold-solver records to v11 without duplicating curves or target draws."""
import argparse,gzip,hashlib,json,sqlite3,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def code(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 p=Path(p)
 if not p.is_file():p=Path(str(p)+'.gz')
 return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
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
 if con.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(code('prime-field-database/v11'),):raise ValueError('v11 parent required')
 con.executescript('''CREATE TABLE functional_solver_studies(execution_id TEXT PRIMARY KEY REFERENCES executions,source_path TEXT NOT NULL REFERENCES sources,rules_json TEXT NOT NULL);
 CREATE TABLE functional_solver_cases(execution_id TEXT NOT NULL REFERENCES functional_solver_studies,instance_id INTEGER NOT NULL,descriptor_json TEXT NOT NULL,case_json TEXT NOT NULL,verification_json TEXT NOT NULL,PRIMARY KEY(execution_id,instance_id));
 CREATE TABLE functional_solver_arms(execution_id TEXT NOT NULL,instance_id INTEGER NOT NULL,solver TEXT NOT NULL,summary_json TEXT NOT NULL,certificates_json TEXT NOT NULL,PRIMARY KEY(execution_id,instance_id,solver),FOREIGN KEY(execution_id,instance_id) REFERENCES functional_solver_cases);''')
 def source(path,kind):
  name=str(path.resolve().relative_to(ROOT));expected=(digest(path),path.stat().st_size);old=con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
  if old and old!=expected:raise ValueError('historical source changed')
  con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind));return name
 source(a.parent,'parent_database_v11');source(Path(__file__),'functional_solver_database_builder');inputpath=source(a.inputs,'frozen_solver_inputs')
 e=load(a.run/'export.json');execution=load(a.run/'execution.json');analysis=load(a.run/'analysis.json');rules=load(a.inputs)
 if not analysis['panel_complete'] or analysis['solver_calls_verified']!=1152:raise ValueError('complete checked panel required')
 exportpath=source(a.run/'export.json','unified_solver_export')
 for item in e['files']:
  path=(a.run/item['path']).resolve();path.relative_to(a.run.resolve())
  if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('export file binding')
  source(path,'export_bound_solver_file')
 eid=str(a.run.resolve().relative_to(ROOT));con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],e['protocol']['sha256'],1,0,code(execution),exportpath));con.execute('INSERT INTO functional_solver_studies VALUES (?,?,?)',(eid,inputpath,code(rules)))
 index=0
 for parent in rules['parent_files']:
  raw=load(a.run/'raw'/(parent['cell_id']+'.json'))
  for rec in raw['records']:
   con.execute('INSERT INTO functional_solver_cases VALUES (?,?,?,?,?)',(eid,index,code(rec['descriptor']),code(rec['case']),code(rec['verification'])))
   for result in rec['results']:
    s=next(v for v in analysis['cells'] if v['instance_id']==str(index) and v['arm']==result['arm'])
    con.execute('INSERT INTO functional_solver_arms VALUES (?,?,?,?,?)',(eid,index,result['arm'],code(s),code(result)))
   index+=1
 if index!=288:raise ValueError('case coverage')
 con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v11_metadata',code(metadata)))
 for k,v in [('schema','prime-field-database/v12'),('builder_sha256',digest(Path(__file__))),('schema_sha256',hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest())]:con.execute('UPDATE metadata SET value=? WHERE key=?',(code(v),k))
 preserved={n:rows.issubset({code(list(row)) for row in con.execute('SELECT * FROM '+n)}) for n,rows in before.items()}
 if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('historical rows or FK failure')
 con.commit();assert con.execute('PRAGMA integrity_check').fetchone()==('ok',);counts={n:con.execute('SELECT COUNT(*) FROM '+n).fetchone()[0] for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")};con.close();prior.close()
 assert digest(a.parent)==parenthash
 data=a.out.read_bytes();archive=Path(str(a.out)+'.gz')
 with archive.open('xb') as f:f.write(gzip.compress(data,compresslevel=6,mtime=0))
 assert gzip.decompress(archive.read_bytes())==data
 (a.out.parent/'.gitignore').write_text('/'+a.out.name+'\n')
 receipt=dict(schema='prime-field-cold-solver-database-receipt/v12',builder_commit=commit,parent_unchanged=True,integrity_check='ok',foreign_key_findings=[],historical_tables_preserved=preserved,counts=counts,sources=[dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size) for p in (a.parent,a.inputs,a.run/'export.json',Path(__file__))],original=dict(path=str(a.out),sha256=digest(a.out),bytes=len(data)),archive=dict(path=str(archive),sha256=digest(archive),bytes=archive.stat().st_size),new_native_executions=0,new_independent_curves=0,new_independent_targets=0)
 with (a.out.parent/'generation-v12.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 print(json.dumps(dict(counts=counts,archive=str(archive))))
if __name__=='__main__':main()

"""Append streamed batched holdouts to v14, preserving every historical row."""
import argparse,gzip,hashlib,json,sqlite3,subprocess,shutil
from pathlib import Path
from common import ROOT,load,digest,write_once
from streaming import lines

def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()

def code(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def main():
 p=argparse.ArgumentParser()
 for n in ('parent','run','inputs','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
 if a.out.exists():raise ValueError('fresh database required')
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();relative=str(Path(__file__).resolve().relative_to(ROOT))
 if hashlib.sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=digest(Path(__file__)):raise ValueError('commit builder first')
 parenthash=digest(a.parent);prior=sqlite3.connect('file:'+str(a.parent.resolve())+'?mode=ro',uri=True);con=sqlite3.connect(a.out)
 before={n:prior.execute('SELECT COUNT(*) FROM '+n).fetchone()[0] for (n,) in prior.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='metadata'")}
 metadata=prior.execute('SELECT * FROM metadata ORDER BY key').fetchall();prior.backup(con);con.execute('PRAGMA foreign_keys=ON');con.execute('PRAGMA temp_store=FILE');con.execute('PRAGMA cache_size=-32768');con.execute('ATTACH DATABASE ? AS parent_snapshot',(str(a.parent.resolve()),))
 if con.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(code('prime-field-database/v14'),):raise ValueError('v14 parent required')
 con.executescript('''CREATE TABLE batch_studies(execution_id TEXT PRIMARY KEY REFERENCES executions,source_path TEXT NOT NULL REFERENCES sources,rules_json TEXT NOT NULL,metrics_json TEXT NOT NULL);
 CREATE TABLE batch_cells(id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES batch_studies,base_sha256 TEXT NOT NULL REFERENCES bases,source_path TEXT NOT NULL REFERENCES sources);
 CREATE TABLE batch_sources(cell_id TEXT NOT NULL REFERENCES batch_cells,arm TEXT NOT NULL,order_json TEXT NOT NULL,constructor_json TEXT NOT NULL,knowledge_json TEXT NOT NULL,PRIMARY KEY(cell_id,arm));
 CREATE TABLE batch_targets(cell_id TEXT NOT NULL REFERENCES batch_cells,target_index INTEGER NOT NULL,point_json TEXT NOT NULL,PRIMARY KEY(cell_id,target_index));
 CREATE TABLE batch_branches(cell_id TEXT NOT NULL REFERENCES batch_cells,branch_key TEXT NOT NULL,branch_json TEXT NOT NULL,PRIMARY KEY(cell_id,branch_key));
 CREATE TABLE batch_labels(cell_id TEXT NOT NULL,branch_key TEXT NOT NULL,label_index INTEGER NOT NULL,label_json TEXT NOT NULL,PRIMARY KEY(cell_id,branch_key,label_index),FOREIGN KEY(cell_id,branch_key) REFERENCES batch_branches);
 CREATE TABLE batch_engine_points(cell_id TEXT NOT NULL REFERENCES batch_cells,serial INTEGER NOT NULL,origin TEXT NOT NULL,record_json TEXT NOT NULL,PRIMARY KEY(cell_id,serial));
 CREATE TABLE batch_queries(cell_id TEXT NOT NULL REFERENCES batch_cells,query_index INTEGER NOT NULL,query_json TEXT NOT NULL,PRIMARY KEY(cell_id,query_index));
 CREATE TABLE batch_cases(execution_id TEXT NOT NULL REFERENCES batch_studies,case_id INTEGER NOT NULL,descriptor_json TEXT NOT NULL,case_json TEXT NOT NULL,verification_json TEXT NOT NULL,PRIMARY KEY(execution_id,case_id));
 CREATE TABLE batch_solver_arms(execution_id TEXT NOT NULL,case_id INTEGER NOT NULL,solver TEXT NOT NULL,summary_json TEXT NOT NULL,certificate_json TEXT NOT NULL,PRIMARY KEY(execution_id,case_id,solver),FOREIGN KEY(execution_id,case_id) REFERENCES batch_cases);''')
 def source(path,kind):
  name=str(path.resolve().relative_to(ROOT));expected=(digest(path),path.stat().st_size);old=con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
  if old and old!=expected:raise ValueError('historical source changed')
  con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind));return name
 source(a.parent,'parent_database_v14');source(Path(__file__),'batch_holdout_builder');inputpath=source(a.inputs,'frozen_batch_rules')
 export=load(a.run/'export.json');execution=load(a.run/'execution.json');metrics=load(a.run/'metrics.json');rules=load(a.inputs);exportpath=source(a.run/'export.json','unified_batch_export')
 for item in export['files']:
  path=(a.run/item['path']).resolve();path.relative_to(a.run.resolve())
  if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('export file binding')
  source(path,'export_bound_batch_file')
 eid=str(a.run.resolve().relative_to(ROOT));con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],export['protocol']['sha256'],1,0,code(execution),exportpath));con.execute('INSERT INTO batch_studies VALUES (?,?,?,?)',(eid,inputpath,code(rules),code(metrics)))
 summaries={v['case_id']:v for v in [dict(zip(metrics['columns'],r,strict=True)) for r in metrics['rows']]};newcurves=0;newtargets=0
 for field in rules['fields']:
  for ci in range(rules['curves_per_field']):
   name='p'+str(field['p'])+'-i'+str(ci);raw=a.run/'raw';path=raw/(name+'.source.json');actual=path if path.is_file() else Path(str(path)+'.gz')
   if not actual.is_file():continue
   data=load(actual);cell=data['cell'];col=data['collection'];f=cell['fixture'];uid=f['ec1']['curve_uid'];key=hashlib.sha256(code(dict(schema='batched-holdout-base/v1',curve_uid=uid,atoms=f['factor_base'],projection=cell['projection'])).encode()).hexdigest();cid=eid+':'+name
   con.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',(uid,str(f['p']),str(f['a']),str(f['b']),str(f['r']),code(f['P'])))
   con.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(key,uid,f['uid'],len(f['factor_base']),cell['projection']['U'],'batched-holdout-base/v1:freshnormatoms/fixedprojection',str(actual.resolve().relative_to(ROOT))))
   con.execute('INSERT INTO batch_cells VALUES (?,?,?,?)',(cid,eid,key,str(actual.resolve().relative_to(ROOT))));newcurves+=1
   for arm,order in col['selection']['orders'].items():
    rec=col['arms'][arm];con.execute('INSERT INTO batch_sources VALUES (?,?,?,?,?)',(cid,arm,code(order),code(rec['selection']),code(rec['knowledge'])))
   for t in col['target_generation']['targets']:con.execute('INSERT INTO batch_targets VALUES (?,?,?)',(cid,t['index'],code(t['point'])));newtargets+=1
   for entry in lines(raw/(name+'.branches.jsonl')):
    branch=entry['branch'];bkey=code(entry['context']);con.execute('INSERT INTO batch_branches VALUES (?,?,?)',(cid,bkey,code(branch)))
    for i,label in enumerate(branch['labels']):con.execute('INSERT INTO batch_labels VALUES (?,?,?,?)',(cid,bkey,i,code(label)))
   for record in col['query_engine_records']:con.execute('INSERT INTO batch_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'source_and_natural',code(record)))
   qpath=raw/(name+'.query-cache.json')
   if qpath.is_file() or Path(str(qpath)+'.gz').is_file():
    cache=load(qpath)
    for record in cache['engine_records']:con.execute('INSERT INTO batch_engine_points VALUES (?,?,?,?)',(cid,record['serial'],'affine_target',code(record)))
    for q in cache['records']:con.execute('INSERT INTO batch_queries VALUES (?,?,?)',(cid,q['id'],code(q)))
   checks=iter(lines(raw/(name+'.case-checks.jsonl')));outputs=iter(lines(raw/(name+'.solver-outputs.jsonl')))
   for item in lines(raw/(name+'.case-inputs.jsonl')):
    idx=item['case_id'];v=next(checks,None)
    if not summaries[idx]['verified']:continue
    if v is None or v['case_id']!=idx:raise ValueError('streamed case/check alignment')
    con.execute('INSERT INTO batch_cases VALUES (?,?,?,?,?)',(eid,idx,code(item['descriptor']),code(item['case']),code(v['verification'])))
    for arm in ('sparse_joint','sparse_cancel'):
     result=next(outputs,None)
     if result is None or result['case_id']!=idx or result['arm']!=arm:raise ValueError('solver stream alignment')
     con.execute('INSERT INTO batch_solver_arms VALUES (?,?,?,?,?)',(eid,idx,arm,code(summaries[idx]),code(result['result'])))
 con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v14_metadata',code(metadata)))
 for k,v in [('schema','prime-field-database/v15'),('builder_sha256',digest(Path(__file__))),('schema_sha256',hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest())]:con.execute('UPDATE metadata SET value=? WHERE key=?',(code(v),k))
 preserved={n:con.execute('SELECT COUNT(*) FROM '+n).fetchone()[0]>=count and con.execute('SELECT 1 FROM (SELECT * FROM parent_snapshot.'+n+' EXCEPT SELECT * FROM main.'+n+') LIMIT 1').fetchone() is None for n,count in before.items()}
 if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('historical rows/FK failure')
 con.commit()
 if con.execute('PRAGMA integrity_check').fetchone()!=('ok',):raise ValueError('database integrity')
 counts={n:con.execute('SELECT COUNT(*) FROM '+n).fetchone()[0] for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")};con.close();prior.close()
 if digest(a.parent)!=parenthash:raise ValueError('parent changed')
 original_sha=digest(a.out);size=a.out.stat().st_size;archive=Path(str(a.out)+'.gz')
 with a.out.open('rb') as source_stream,archive.open('xb') as encoded:
  with gzip.GzipFile(fileobj=encoded,mode='wb',compresslevel=6,mtime=0) as target:shutil.copyfileobj(source_stream,target,1048576)
 checkhash=hashlib.sha256();decoded=0
 with gzip.open(archive,'rb') as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):checkhash.update(chunk);decoded+=len(chunk)
 if checkhash.hexdigest()!=original_sha or decoded!=size:raise ValueError('gzip stream roundtrip')
 (a.out.parent/'.gitignore').write_text('/'+a.out.name+'\n')
 write_once(a.out.parent/'generation-v15.json',dict(schema='prime-field-database-receipt/v15',builder_commit=commit,parent_unchanged=True,parent_sha256=parenthash,integrity_check='ok',foreign_key_findings=[],historical_tables_preserved=preserved,counts=counts,new_native_executions=1,new_independent_curves=newcurves,new_independent_targets=newtargets,panel_complete=metrics['panel_complete'],proof_standing='Producer import/preservation checks only, not signed scientific replay',original=dict(path=str(a.out),sha256=original_sha,bytes=size),archive=dict(path=str(archive),sha256=digest(archive),bytes=archive.stat().st_size)))
 print(json.dumps(dict(counts=counts,archive=str(archive))))
if __name__=='__main__':main()

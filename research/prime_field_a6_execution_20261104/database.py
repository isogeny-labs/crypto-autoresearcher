"""Append source-control schedules/certificates to a read-only v8 backup."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess
ROOT=Path(__file__).resolve().parents[2]
def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def load(p):
    if not p.is_file():p=Path(str(p)+'.gz')
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
SCHEMA='''
CREATE TABLE source_control_cells(id TEXT PRIMARY KEY,execution_id TEXT NOT NULL REFERENCES executions,base_sha256 TEXT NOT NULL REFERENCES bases,source_path TEXT NOT NULL REFERENCES sources);
CREATE TABLE source_control_schedules(cell_id TEXT NOT NULL REFERENCES source_control_cells,arm TEXT NOT NULL,schedule_json TEXT NOT NULL,collision_json TEXT NOT NULL,PRIMARY KEY(cell_id,arm));
CREATE TABLE source_control_rows(cell_id TEXT NOT NULL,arm TEXT NOT NULL,kind TEXT NOT NULL,row_index INTEGER NOT NULL,witness_json TEXT NOT NULL,PRIMARY KEY(cell_id,arm,kind,row_index),FOREIGN KEY(cell_id,arm) REFERENCES source_control_schedules);
CREATE TABLE source_control_targets(cell_id TEXT NOT NULL REFERENCES source_control_cells,target_index INTEGER NOT NULL,point_json TEXT NOT NULL,PRIMARY KEY(cell_id,target_index));
CREATE TABLE source_control_target_rows(cell_id TEXT NOT NULL REFERENCES source_control_cells,row_index INTEGER NOT NULL,target_index INTEGER NOT NULL,witness_json TEXT NOT NULL,PRIMARY KEY(cell_id,row_index),FOREIGN KEY(cell_id,target_index) REFERENCES source_control_targets);
CREATE TABLE source_control_prefixes(cell_id TEXT NOT NULL,arm TEXT NOT NULL,prefix INTEGER NOT NULL,scope TEXT NOT NULL,base_rank INTEGER NOT NULL,base_nullity INTEGER NOT NULL,anchor_gain INTEGER NOT NULL,target_delta INTEGER NOT NULL,summary_json TEXT NOT NULL,certificates_json TEXT NOT NULL,PRIMARY KEY(cell_id,arm,prefix,scope),FOREIGN KEY(cell_id,arm) REFERENCES source_control_schedules);
CREATE VIEW source_control_rank_summary AS SELECT c.curve_uid,c.p,c.b,p.arm,p.prefix,p.scope,p.base_rank,p.base_nullity,p.anchor_gain,p.target_delta FROM source_control_prefixes p JOIN source_control_cells s ON p.cell_id=s.id JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid);
'''
def table_hash(c,name):
    records=sorted(encode(list(row)) for row in c.execute('SELECT * FROM '+name))
    return sha256(('\n'.join(records)+'\n').encode()).hexdigest()

def build(parent,run,inputs,out):
    if out.exists():raise ValueError('fresh v9 database required')
    before=digest(parent);prior=sqlite3.connect('file:'+str(parent.resolve())+'?mode=ro',uri=True)
    historical={name:table_hash(prior,name) for (name,) in prior.execute("SELECT name FROM sqlite_master WHERE type='table'") if name!='metadata'}
    metadata=prior.execute('SELECT * FROM metadata ORDER BY key').fetchall();c=sqlite3.connect(out)
    def source(path,kind):
        name=str(path.resolve().relative_to(ROOT));old=c.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=(digest(path),path.stat().st_size):raise ValueError('historical source bytes differ')
        c.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,digest(path),path.stat().st_size,kind));return name
    try:
        prior.backup(c)
        if c.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(encode('prime-field-database/v8'),):raise ValueError('v8 parent required')
        c.execute('PRAGMA foreign_keys=ON')
        c.execute('CREATE TABLE fresh_source_generations(execution_id TEXT PRIMARY KEY REFERENCES executions,source_path TEXT NOT NULL REFERENCES sources,generation_json TEXT NOT NULL)')
        # Check all inherited table bytes before adding new indexed evidence.
        if any(table_hash(c,name)!=value for name,value in historical.items()):raise ValueError('backup history differs')
        source(parent,'parent_database_v8');source(Path(__file__),'fresh_source_v9_builder');source(inputs,'frozen_source_control_inputs')
        export=load(run/'export.json');execution=load(run/'execution.json');analysis=load(run/'analysis.json');rules=load(inputs)
        if not analysis['panel_complete']:raise ValueError('complete checked source panel required')
        export_path=source(run/'export.json','unified_source_control_export');bound=set()
        for item in export['files']:
            path=(run/item['path']).resolve();path.relative_to(run.resolve())
            if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('export binding differs')
            source(path,'export_bound_source_control_file');bound.add(path)
        eid=str(run.resolve().relative_to(ROOT));c.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],export['protocol']['sha256'],1,0,encode(execution),export_path))
        generated=load(run/'raw/generated.json')
        generation_path=run/'raw/generated.json';generation_path=generation_path if generation_path.is_file() else Path(str(generation_path)+'.gz')
        c.execute('INSERT INTO fresh_source_generations VALUES (?,?,?)',(eid,str(generation_path.resolve().relative_to(ROOT)),encode(generated)))
        summaries={(v['cell_id'],v['arm'],v['prefix'],v['scope']):v for v in analysis['cells']}
        for cell in generated['cells']:
            f=cell['fixture'];uid=f['ec1']['curve_uid'];key=sha256(encode(dict(schema='holdout-base/v1',curve_uid=uid,atoms=f['factor_base'],projection=cell['projection'])).encode()).hexdigest()
            c.execute('INSERT INTO curves VALUES (?,?,?,?,?,?)',(uid,str(f['p']),str(f['a']),str(f['b']),str(f['r']),encode(f['P'])))
            c.execute('INSERT INTO bases VALUES (?,?,?,?,?,?,?)',(key,uid,f['uid'],len(f['factor_base']),cell['projection']['U'],'holdout-base/v1: fresh norm atoms and fixed window public projection',str(generation_path.resolve().relative_to(ROOT))))
            path=run/'raw'/(cell['id']+'.json');path=path if path.is_file() else Path(str(path)+'.gz')
            if path.resolve() not in bound:raise ValueError('unbound source-control result')
            result=load(path);cid=eid+':'+cell['id'];c.execute('INSERT INTO source_control_cells VALUES (?,?,?,?)',(cid,eid,key,str(path.resolve().relative_to(ROOT))))
            for arm,order in result['selection']['schedules'].items():
                c.execute('INSERT INTO source_control_schedules VALUES (?,?,?,?)',(cid,arm,encode(order),encode(result['arms'][arm]['collision_diagnostics'])))
                for kind,rows in [('relation',result['arms'][arm]['rows']),('anchor',result['arms'][arm]['anchor_rows'])]:
                    for i,row in enumerate(rows):c.execute('INSERT INTO source_control_rows VALUES (?,?,?,?,?)',(cid,arm,kind,i,encode(row)))
            for target in result['target_generation']['targets']:c.execute('INSERT INTO source_control_targets VALUES (?,?,?)',(cid,target['index'],encode(target['point'])))
            for i,row in enumerate(result['target_collection']['rows']):c.execute('INSERT INTO source_control_target_rows VALUES (?,?,?,?)',(cid,i,row['target_index'],encode(row)))
            for rec in result['prefixes']:
                s=summaries[cell['id'],rec['arm'],rec['prefix'],rec['scope']]
                if not s['verified']:raise ValueError('unverified scope')
                c.execute('INSERT INTO source_control_prefixes VALUES (?,?,?,?,?,?,?,?,?,?)',(cid,rec['arm'],rec['prefix'],rec['scope'],s['base_rank'],s['base_nullity'],s['anchor_gain'],s['target_base_rank_gain'],encode(s),encode(rec)))
        c.execute('INSERT INTO metadata VALUES (?,?)',('parent_v8_metadata',encode(metadata)))
        for key,value in [('schema','prime-field-database/v9'),('builder_sha256',digest(Path(__file__))),('schema_sha256',sha256(encode(c.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest())]:
            c.execute('UPDATE metadata SET value=? WHERE key=?',(encode(value),key))
        # Historical scientific tables remain byte-equivalent; sources/executions intentionally append.
        preserved={name:table_hash(c,name)==value for name,value in historical.items() if name not in ('sources','executions','curves','bases','source_control_cells','source_control_schedules','source_control_rows','source_control_targets','source_control_target_rows','source_control_prefixes')}
        for name in historical:
            original_rows={encode(list(row)) for row in prior.execute('SELECT * FROM '+name)}
            current_rows={encode(list(row)) for row in c.execute('SELECT * FROM '+name)}
            preserved[name]=original_rows.issubset(current_rows)
        if not all(preserved.values()) or c.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('history or foreign-key failure')
        c.commit()
        if c.execute('PRAGMA integrity_check').fetchone()!=('ok',) or digest(parent)!=before:raise ValueError('integrity/parent bytes differ')
        counts={name:c.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for (name,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
        return counts,preserved
    except BaseException:c.close();out.unlink(missing_ok=True);raise
    finally:prior.close();c.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('parent','run','inputs','out'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True);commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if sha256(subprocess.check_output(['git','show',commit+':'+str(Path(__file__).resolve().relative_to(ROOT))],cwd=ROOT)).hexdigest()!=digest(Path(__file__)):raise ValueError('commit exact database builder first')
    counts,preserved=build(a.parent,a.run,a.inputs,a.out);archive=Path(str(a.out)+'.gz')
    with archive.open('xb') as stream:stream.write(gzip.compress(a.out.read_bytes(),compresslevel=6,mtime=0))
    if gzip.decompress(archive.read_bytes())!=a.out.read_bytes():raise ValueError('gzip roundtrip differs')
    (a.out.parent/'.gitignore').write_text('/'+a.out.name+'\n')
    with (a.out.parent/'generation-v9.json').open('x') as stream:json.dump(dict(schema='prime-field-fresh-source-database-receipt/v9',builder_commit=commit,parent_unchanged=True,integrity_check='ok',foreign_key_findings=[],historical_tables_preserved=preserved,counts=counts,sources=[dict(path=str(path),sha256=digest(path),bytes=path.stat().st_size) for path in (a.parent,a.inputs,a.run/'export.json',Path(__file__))],original=dict(path=str(a.out),sha256=digest(a.out),bytes=a.out.stat().st_size),archive=dict(path=str(archive),sha256=digest(archive),bytes=archive.stat().st_size),new_native_executions=0),stream,indent=2);stream.write('\n')
    print(json.dumps(dict(counts=counts,archive=str(archive))))
if __name__=='__main__':main()

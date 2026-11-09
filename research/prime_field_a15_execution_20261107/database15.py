"""Append measured/partial pair-component records to v17 without new curves."""
import argparse,gzip,hashlib,json,shutil,sqlite3,subprocess
from pathlib import Path
from custody15 import ROOT,INPUTS,load,write_once
from database14 import digest,code
from analyze15 import lines

PRIOR_EXECUTION='research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('parent','run','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.out.exists():raise ValueError('fresh database required')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    relative=str(Path(__file__).resolve().relative_to(ROOT))
    if hashlib.sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest()!=digest(__file__):
        raise ValueError('publish exact database builder before use')
    parent_hash=digest(args.parent);parent=sqlite3.connect('file:'+str(args.parent.resolve())+'?mode=ro',uri=True)
    if parent.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()!=(code('prime-field-database/v17'),):raise ValueError('v17 parent required')
    before={name:parent.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name, in parent.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='metadata'")}
    metadata=parent.execute('SELECT * FROM metadata ORDER BY key').fetchall()
    con=sqlite3.connect(args.out);parent.backup(con)
    con.execute('PRAGMA foreign_keys=ON');con.execute('PRAGMA temp_store=FILE');con.execute('PRAGMA cache_size=-32768')
    con.execute('ATTACH DATABASE ? AS parent_snapshot',(str(args.parent.resolve()),))
    con.executescript('''
      CREATE TABLE pair_component_studies(execution_id TEXT PRIMARY KEY REFERENCES executions,
        inputs_path TEXT NOT NULL REFERENCES sources,inputs_json TEXT NOT NULL,metrics_json TEXT NOT NULL);
      CREATE TABLE pair_component_tables(execution_id TEXT NOT NULL REFERENCES pair_component_studies,
        table_id TEXT NOT NULL,prior_cell_id TEXT NOT NULL REFERENCES paid_base_cells,
        snapshot_path TEXT NOT NULL REFERENCES sources,geometry_json TEXT NOT NULL,
        PRIMARY KEY(execution_id,table_id));
      CREATE TABLE pair_component_builds(execution_id TEXT NOT NULL,table_id TEXT NOT NULL,method TEXT NOT NULL,
        output_json TEXT NOT NULL,check_json TEXT,PRIMARY KEY(execution_id,table_id,method),
        FOREIGN KEY(execution_id,table_id) REFERENCES pair_component_tables);
      CREATE TABLE pair_component_queries(execution_id TEXT NOT NULL,table_id TEXT NOT NULL,method TEXT NOT NULL,
        query_index INTEGER NOT NULL,output_json TEXT NOT NULL,check_json TEXT,
        PRIMARY KEY(execution_id,table_id,method,query_index),
        FOREIGN KEY(execution_id,table_id,method) REFERENCES pair_component_builds);
    ''')
    def source(path,kind):
        path=Path(path);name=str(path.resolve().relative_to(ROOT));expected=digest(path),path.stat().st_size
        old=con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=expected:raise ValueError('historical source changed')
        con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind));return name
    source(args.parent,'parent_database_v17');source(Path(__file__),'pair_component_database_builder')
    input_path=source(INPUTS,'retained_pair_component_inputs')
    export,execution,metrics,rules=[load(path) for path in (args.run/'export.json',args.run/'execution.json',args.run/'metrics.json',INPUTS)]
    export_path=source(args.run/'export.json','pair_component_unified_export')
    for item in export['files']:
        path=(args.run/item['path']).resolve();path.relative_to(args.run.resolve())
        if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('export file binding')
        source(path,'export_bound_pair_component_file')
    eid=str(args.run.resolve().relative_to(ROOT))
    con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],export['protocol']['sha256'],1,0,code(execution),export_path))
    con.execute('INSERT INTO pair_component_studies VALUES (?,?,?,?)',(eid,input_path,code(rules),code(metrics)))
    for item in rules['snapshots']:
        s=load(ROOT/item['path']);cid,arm=item['id'].split('.')
        prior_id=PRIOR_EXECUTION+':'+cid+':'+arm
        row=con.execute('SELECT base_arm FROM paid_base_cells WHERE id=?',(prior_id,)).fetchone()
        if row!=(arm,):raise ValueError('retained A14 base identity absent')
        con.execute('INSERT INTO pair_component_tables VALUES (?,?,?,?,?)',(eid,item['id'],prior_id,
            source(ROOT/item['path'],'retained_public_geometry_query_snapshot'),code(s['geometry'])))
        directory=args.run/'raw'/item['id']
        checks={(x['kind'],x.get('method'),x.get('query_index')):x for x in lines(directory/'checks.jsonl')}
        for output in lines(directory/'outputs.jsonl'):
            if output['kind']=='built':
                check=checks.get(('pair_check',output['method'],None))
                con.execute('INSERT INTO pair_component_builds VALUES (?,?,?,?,?)',(eid,item['id'],output['method'],code(output),code(check) if check else None))
            elif output['kind']=='query':
                check=checks.get(('query_check',output['method'],output['query_index']))
                con.execute('INSERT INTO pair_component_queries VALUES (?,?,?,?,?,?)',(eid,item['id'],output['method'],output['query_index'],code(output),code(check) if check else None))
    con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v17_metadata',code(metadata)))
    schema_hash=hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest()
    for key,value in [('schema','prime-field-database/v18'),('builder_sha256',digest(__file__)),('schema_sha256',schema_hash)]:con.execute('UPDATE metadata SET value=? WHERE key=?',(code(value),key))
    preserved={name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]>=count and
        con.execute('SELECT 1 FROM (SELECT * FROM parent_snapshot.'+name+' EXCEPT SELECT * FROM main.'+name+') LIMIT 1').fetchone()is None for name,count in before.items()}
    if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('historical rows/FK failed')
    con.commit()
    if con.execute('PRAGMA integrity_check').fetchone()!=('ok',):raise ValueError('integrity failed')
    counts={name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name, in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    con.close();parent.close()
    if digest(args.parent)!=parent_hash:raise ValueError('parent bytes changed')
    archive=Path(str(args.out)+'.gz')
    with args.out.open('rb') as inp,archive.open('xb') as encoded:
        with gzip.GzipFile(fileobj=encoded,mode='wb',compresslevel=6,mtime=0) as sink:shutil.copyfileobj(inp,sink,1048576)
    decoded=hashlib.sha256();size=0
    with gzip.open(archive,'rb') as inp:
        for chunk in iter(lambda:inp.read(1048576),b''):decoded.update(chunk);size+=len(chunk)
    if decoded.hexdigest()!=digest(args.out) or size!=args.out.stat().st_size:raise ValueError('gzip roundtrip')
    write_once(args.out.parent/'validation.json',dict(parent_sha256=parent_hash,parent_unchanged=True,historical_tables_preserved=preserved,
        foreign_keys=True,integrity=True,gzip_roundtrip=True,new_curves=0,new_bases=0,new_public_targets=0,new_target_solver_calls=0,
        table_counts=counts,database_sha256=digest(args.out),database_bytes=size,archive_sha256=digest(archive),archive_bytes=archive.stat().st_size))
    (args.out.parent/'.gitignore').write_text('/'+args.out.name+'\n')
    print(json.dumps(dict(database=str(args.out),archive=str(archive),builds=counts['pair_component_builds'],query_calls=counts['pair_component_queries'])))


if __name__=='__main__':main()

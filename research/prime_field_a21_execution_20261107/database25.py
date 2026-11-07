"""Append A21 conditioned algebra contexts to v24, preserving all parent rows."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
from custody21 import ROOT, load, write_once, ARMS


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''): value.update(block)
    return value.hexdigest()


def code(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('parent', 'run', 'inputs', 'out'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists(): raise ValueError('fresh database required')
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    relative = str(Path(__file__).resolve().relative_to(ROOT))
    if hashlib.sha256(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)).hexdigest() != digest(__file__):
        raise ValueError('publish exact database builder before use')
    parent_hash = digest(args.parent)
    parent = sqlite3.connect('file:'+str(args.parent.resolve())+'?mode=ro', uri=True)
    if parent.execute("SELECT value FROM metadata WHERE key='schema'").fetchone() != (code('prime-field-database/v24'),):
        raise ValueError('v24 parent required')
    before = {name: parent.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]
        for name, in parent.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='metadata'")}
    metadata = parent.execute('SELECT * FROM metadata ORDER BY key').fetchall()
    con = sqlite3.connect(args.out)
    parent.backup(con)
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA temp_store=FILE')
    con.execute('PRAGMA cache_size=-32768')
    con.execute('ATTACH DATABASE ? AS parent_snapshot', (str(args.parent.resolve()),))

    con.executescript('''
      CREATE TABLE formal_algebra_studies(execution_id TEXT PRIMARY KEY REFERENCES executions,
        source_path TEXT NOT NULL REFERENCES sources,rules_json TEXT NOT NULL,metrics_json TEXT NOT NULL);
      CREATE TABLE formal_algebra_cases(execution_id TEXT NOT NULL REFERENCES formal_algebra_studies,
        case_index INTEGER NOT NULL,parent_context TEXT NOT NULL REFERENCES auxiliary_pool_programs,
        case_source TEXT NOT NULL REFERENCES sources,preparation_source TEXT NOT NULL REFERENCES sources,
        descriptor_json TEXT NOT NULL,PRIMARY KEY(execution_id,case_index));
      CREATE TABLE formal_algebra_solvers(execution_id TEXT NOT NULL,case_index INTEGER NOT NULL,method TEXT NOT NULL,
        source_path TEXT REFERENCES sources,check_path TEXT REFERENCES sources,result_json TEXT,check_json TEXT,metrics_json TEXT NOT NULL,
        PRIMARY KEY(execution_id,case_index,method),FOREIGN KEY(execution_id,case_index) REFERENCES formal_algebra_cases);
    ''')
    def source(path,kind):
        path=Path(path);name=str(path.resolve().relative_to(ROOT));expected=digest(path),path.stat().st_size
        old=con.execute('SELECT sha256,bytes FROM sources WHERE path=?',(name,)).fetchone()
        if old and old!=expected:raise ValueError('historical source changed')
        con.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)',(name,*expected,kind));return name
    source(args.parent,'parent_database_v24');source(Path(__file__),'conditioned_formal_algebra_database_builder')
    input_path=source(args.inputs,'frozen_conditioned_formal_rules')
    export,execution,metrics,rules=[load(path)for path in (args.run/'export.json',args.run/'execution.json',args.run/'metrics.json',args.inputs)]
    export_path=source(args.run/'export.json','conditioned_formal_unified_export')
    for item in export['files']:
        path=(args.run/item['path']).resolve();path.relative_to(args.run.resolve())
        if digest(path)!=item['sha256']or path.stat().st_size!=item['bytes']:raise ValueError('export file binding')
        source(path,'export_bound_conditioned_formal_file')
    eid=str(args.run.resolve().relative_to(ROOT))
    con.execute('INSERT INTO executions VALUES (?,?,?,?,?,?,?)',(eid,execution['source_commit'],export['protocol']['sha256'],1,0,code(execution),export_path))
    con.execute('INSERT INTO formal_algebra_studies VALUES (?,?,?,?)',(eid,input_path,code(rules),code(metrics)))
    summaries={(v['case_id'],v['method']):v for v in [dict(zip(metrics['columns'],row,strict=True))for row in metrics['rows']]}
    new_curves=new_bases=new_targets=0
    parent_execution='research/prime_field_a20_execution_20261107/runs/a20-formal-pair-c4d124'
    for index,descriptor in enumerate(rules['cases']):
        for group in ('producer','checker_only'):
            for binding in descriptor[group].values():
                path=ROOT/binding['path']
                if digest(path)!=binding['sha256']:raise ValueError('immutable conditioned input changed')
                source(path,'conditioned_'+group+'_input')
        cid=descriptor['cell_id'];parent_context=parent_execution+':'+cid+':formalpair16'
        con.execute('INSERT INTO formal_algebra_cases VALUES (?,?,?,?,?,?)',(eid,index,parent_context,
            descriptor['producer']['case']['path'],descriptor['producer']['prepared']['path'],code(descriptor)))
        for method in ARMS:
            path=args.run/'raw'/(cid+'.'+method+'.json');receipt=args.run/'raw'/(cid+'.'+method+'-check.json')
            result=load(path)if path.is_file()else None;check=load(receipt)if receipt.is_file()else None
            con.execute('INSERT INTO formal_algebra_solvers VALUES (?,?,?,?,?,?,?,?)',(eid,index,method,
                source(path,'conditioned_algebra_producer')if result else None,source(receipt,'conditioned_algebra_checker')if check else None,
                code(result)if result else None,code(check)if check else None,code(summaries[index,method])))
    # All inherited historical metadata stays byte-for-byte in the backup.
    # Store only the three values this version overwrites, plus an immutable
    # parent reference, instead of recursively copying every prior snapshot.
    overwritten=('schema','builder_sha256','schema_sha256')
    parent_metadata=dict(schema='prime-field-parent-metadata-reference/v1',parent_sha256=parent_hash,
        metadata_sha256=hashlib.sha256(code(metadata).encode()).hexdigest(),metadata_rows=len(metadata),
        overwritten_values={k:v for k,v in metadata if k in overwritten},other_values_inherited_unchanged=True)
    metadata_reference=code(parent_metadata)
    con.execute('INSERT INTO metadata VALUES (?,?)',('parent_v24_metadata',metadata_reference))
    schema_hash = hashlib.sha256(code(con.execute('SELECT name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name').fetchall()).encode()).hexdigest()
    for key,value in [('schema','prime-field-database/v25'),('builder_sha256',digest(__file__)),('schema_sha256',schema_hash)]:
        con.execute('UPDATE metadata SET value=? WHERE key=?',(code(value),key))
    reconstructed=dict(con.execute('SELECT key,value FROM metadata'))
    reconstructed.pop('parent_v24_metadata')
    reconstructed.update(parent_metadata['overwritten_values'])
    if reconstructed!=dict(metadata):raise ValueError('historical metadata reconstruction failed')
    metadata_reconstruction_sha256=hashlib.sha256(code(sorted(reconstructed.items())).encode()).hexdigest()
    if metadata_reconstruction_sha256!=parent_metadata['metadata_sha256']:raise ValueError('parent metadata digest reconstruction failed')
    preserved = {name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] >= count and
        con.execute('SELECT 1 FROM (SELECT * FROM parent_snapshot.'+name+' EXCEPT SELECT * FROM main.'+name+') LIMIT 1').fetchone() is None
        for name,count in before.items()}
    if not all(preserved.values()) or con.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('historical rows/foreign keys failed')
    con.commit()
    if con.execute('PRAGMA integrity_check').fetchone() != ('ok',): raise ValueError('database integrity failed')
    counts = {name:con.execute('SELECT COUNT(*) FROM '+name).fetchone()[0]
        for name, in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    con_contexts=con.execute('SELECT COUNT(*) FROM formal_algebra_cases WHERE execution_id=?',(eid,)).fetchone()[0]
    con.close(); parent.close()
    if digest(args.parent) != parent_hash: raise ValueError('parent bytes changed')
    archive = Path(str(args.out)+'.gz')
    with args.out.open('rb') as source_stream,archive.open('xb') as encoded:
        with gzip.GzipFile(fileobj=encoded,mode='wb',compresslevel=6,mtime=0) as target: shutil.copyfileobj(source_stream,target,1048576)
    decoded, size = hashlib.sha256(), 0
    with gzip.open(archive,'rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''): decoded.update(chunk); size += len(chunk)
    if decoded.hexdigest() != digest(args.out) or size != args.out.stat().st_size: raise ValueError('database gzip roundtrip')
    write_once(args.out.parent/'validation.json',dict(parent_sha256=parent_hash,parent_unchanged=True,metadata_reference_schema=parent_metadata['schema'],
        historical_metadata_reconstructs_exactly=True,parent_metadata_sha256=metadata_reconstruction_sha256,
        metadata_reference_bytes=len(metadata_reference.encode()),parent_full_metadata_bytes=len(code(metadata).encode()),
        historical_tables_preserved=preserved,foreign_keys=True,integrity=True,new_curves=new_curves,new_bases=new_bases,
        new_public_targets=new_targets,new_program_contexts=con_contexts,table_counts=counts,database_sha256=digest(args.out),database_bytes=size,
        archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,gzip_roundtrip=True))
    (args.out.parent/'.gitignore').write_text('/'+args.out.name+'\n')
    print(json.dumps(dict(database=str(args.out),archive=str(archive),new_curves=new_curves,new_bases=new_bases,new_public_targets=new_targets)))


if __name__ == '__main__': main()

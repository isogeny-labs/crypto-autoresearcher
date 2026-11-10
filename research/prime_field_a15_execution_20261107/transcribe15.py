"""Copy public A14 geometries/query commitments; performs no group arithmetic."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT/'research/prime_field_a14_execution_20261106/runs/a14-mixed-known-helpers-4bbcf6/raw'
COMMIT = 'e71e73242b04856b230e8f767383eb4ad7ef57ba'

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    provenance = {}
    def load(name):
        p = PRIOR/(name+'.json')
        if not p.is_file(): p=Path(str(p)+'.gz')
        raw=p.read_bytes();relative=str(p.relative_to(ROOT))
        if p.suffix=='.gz':
            manifest_path=p.parent/'.artifacts.json'
            manifest=json.loads(subprocess.check_output(['git','show',COMMIT+':'+str(manifest_path.relative_to(ROOT))],cwd=ROOT))
            item=manifest['files'][p.name] if 'files' in manifest else manifest[p.name]
            if item['sha256']!=digest(raw) or item['bytes']!=len(raw):raise ValueError('archive differs from committed CAS manifest')
            provenance[relative]=dict(sha256=digest(raw),bytes=len(raw),custody='committed CAS manifest',manifest=str(manifest_path.relative_to(ROOT)))
            return json.loads(gzip.decompress(raw))
        committed=subprocess.check_output(['git','show',COMMIT+':'+relative],cwd=ROOT)
        if committed!=raw:raise ValueError('prior Git input differs')
        provenance[relative]=dict(sha256=digest(raw),bytes=len(raw),custody='Git blob')
        return json.loads(raw)
    snapshots=[]
    for cid in ('p262139-i0','p262139-i1','p524287-i0','p524287-i1'):
        for arm in ('norm','hybrid','known32','known48'):
            name=cid+'.'+arm
            prelude=load(name+'.prelude');source=load(name+'.source')['collection'];cache=load(name+'.query-cache')
            f=prelude['cell']['fixture']
            fixture={k:f[k] for k in ('p','a','b','r','uid','P','ec1')}
            fixture['factor_base']=[dict(point=v['point']) for v in f['factor_base']]
            queries=[]
            engine_by_point={canonical(v['point']):v['points_sha256'] for v in source['query_engine_records']+cache['engine_records']}
            def append(record,origin,index):
                value={k:record[k] for k in ('point','rows','trace')}
                queries.append(dict(origin=origin,ordinal=index,point=record['point'],expected_record_sha256=digest(canonical(value)),expected_signed_points_sha256=engine_by_point[canonical(record['point'])]))
            for schedule in ('ap0','hash0','ap1','hash1','ap2','hash2'):
                if schedule in source['arms']:
                    for i,record in enumerate(source['arms'][schedule]['query_records']):append(record,schedule,i)
            for i,record in enumerate(source['natural_records']):append(record,'natural',i)
            for i,record in enumerate(cache['records']):
                if not record['seeded_natural']:append(record,'extra-cache',i)
            expected=944 if arm in ('norm','hybrid') else 176
            if len(queries)!=expected:raise ValueError('retained query census')
            value=dict(id=name,fixture=fixture,geometry=prelude['geometry'],queries=queries,
                prior_ordered_pairs_sha256=digest(canonical(source['pairs'])),prior_query_count=expected)
            path=HERE/(name+'.input.json')
            with path.open('xb') as out:out.write(canonical(value)+b'\n')
            snapshots.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),bytes=path.stat().st_size,id=name,queries=expected,geometric_atoms=len(prelude['geometry']['points']),native_width=len(f['factor_base'])))
    value=dict(schema='a15-retained-public-inputs/v1',prior_commit=COMMIT,prior_native_source='f5ea52dee9706cc6277f02b6358cbd3d733b787c',
        scope='Complete retained A14 geometries/queries, conditioned reuse; transcription only, no new point arithmetic or target solvers.',snapshots=snapshots,provenance=provenance)
    with (HERE/'inputs.json').open('xb') as out:out.write(json.dumps(value,indent=2,sort_keys=True).encode()+b'\n')
    print(json.dumps(dict(snapshots=len(snapshots),queries=sum(x['queries'] for x in snapshots),pairs=sum(2*x['geometric_atoms']*(x['geometric_atoms']-1) for x in snapshots))))

if __name__=='__main__':main()

"""Append-only records and closed-curve lossless custody; no scientific restart."""
import gzip,json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from custody import ROOT,write_once,digest

def append(stream,value):
    data=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n');stream.write(data);stream.flush()
    return dict(sha256=hashlib.sha256(data.encode()).hexdigest(),bytes=len(data.encode()))
def lines(path):
    path=Path(path)
    if not path.is_file():path=Path(str(path)+'.gz')
    if not path.is_file():return
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as f:
        for line in f:
            if line.strip():yield json.loads(line)
def close_encodings(raw,cell_id):
    records=[]
    for path in sorted(Path(raw).glob(cell_id+'*')):
        if not path.is_file() or not (path.suffix=='.jsonl' or path.suffix=='.json' and path.stat().st_size>1048576):continue
        relative=str(path.resolve().relative_to(ROOT))
        if subprocess.run(['git','ls-files','--error-unmatch','--',relative],cwd=ROOT,capture_output=True).returncode==0:raise ValueError('cannot recode committed raw')
        out=Path(str(path)+'.gz');original=digest(path);size=path.stat().st_size
        with path.open('rb') as source,out.open('xb') as encoded:
            with gzip.GzipFile(fileobj=encoded,mode='wb',compresslevel=6,mtime=0) as sink:shutil.copyfileobj(source,sink,1048576)
        h=hashlib.sha256();decoded=0
        with gzip.open(out,'rb') as f:
            for data in iter(lambda:f.read(1048576),b''):h.update(data);decoded+=len(data)
        if h.hexdigest()!=original or decoded!=size:raise ValueError('closed-curve gzip mismatch')
        records.append(dict(original_path=path.name,original_sha256=original,original_bytes=size,archive_path=out.name,archive_sha256=digest(out),archive_bytes=out.stat().st_size,encoding='gzip6mtime0 losslessstreamroundtrip'))
        path.unlink()
    write_once(Path(raw)/(cell_id+'.encodings.json'),dict(files=records));return records

def checkpoint_curve(run,cell_id,cases,curves):
    """Pause after all current writers close, avoiding a tar of growing journals."""
    note=ROOT/'.resume/RESUME.md'
    text=note.read_text();text+='\nA13 closed-curve progress '+datetime.now(timezone.utc).isoformat()+': '+cell_id+', '+str(curves)+'curves/'+str(cases)+'checkedcases; raw '+str(Path(run).resolve().relative_to(ROOT))+'/raw. All writers for this curve closed and losslessly encoded. Native attempt continues within original watchdog; no restart/restore.\n'
    note.write_text(text)
    p=subprocess.run(['bash','scripts/checkpoint.sh','push'],cwd=ROOT,capture_output=True,text=True)
    receipt=dict(command=['bash','scripts/checkpoint.sh','push'],returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,observed_utc=datetime.now(timezone.utc).isoformat(),closed_curve=cell_id,checked_cases=cases,completed_curves=curves)
    write_once(Path(run)/('checkpoint-'+cell_id+'.json'),receipt)
    if p.returncode:raise RuntimeError('closed-curve canonical checkpoint failed: '+p.stderr)
    return receipt

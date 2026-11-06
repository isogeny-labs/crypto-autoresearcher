"""Encode remaining closed A12 failure/generation records before publication."""
import argparse,gzip,hashlib,json,secrets,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);a=p.parse_args();records=[]
 json.loads((a.run/'execution.json').read_text())
 for path in sorted((a.run/'raw').glob('*')):
  if not (path.suffix=='.jsonl' or path.suffix=='.json' and path.stat().st_size>1048576):continue
  if subprocess.run(['git','ls-files','--error-unmatch','--',str(path.resolve().relative_to(ROOT))],cwd=ROOT,capture_output=True).returncode==0:raise ValueError('committed raw must remain unchanged')
  data=path.read_bytes();out=Path(str(path)+'.gz')
  with out.open('xb') as f:f.write(gzip.compress(data,compresslevel=6,mtime=0))
  if gzip.decompress(out.read_bytes())!=data:raise ValueError('roundtrip')
  records.append(dict(original_path=str(path.relative_to(a.run)),original_sha256=hashlib.sha256(data).hexdigest(),original_bytes=len(data),archive_path=str(out.relative_to(a.run)),archive_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),archive_bytes=out.stat().st_size,encoding='gzip6mtime0 losslessroundtrip'));path.unlink()
 out=a.run/'archive-encodings';out.mkdir(exist_ok=True)
 with (out/('part-'+secrets.token_hex(3)+'.json')).open('x') as f:json.dump(records,f,indent=2);f.write('\n')
 print(json.dumps(dict(archived_files=len(records),store_paths=[str(a.run/v['archive_path']) for v in records])))
if __name__=='__main__':main()

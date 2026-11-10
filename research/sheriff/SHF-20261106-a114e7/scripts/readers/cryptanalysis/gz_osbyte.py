"""Count gzip header OS byte (offset 9) over indexed .json.gz archives present on disk.
Usage: python3 -I gz_osbyte.py <fb-archive dir> <index.csv>"""
import csv, collections, os, sys
root, idx = sys.argv[1:3]
c = collections.Counter(); indexed_gz = 0; absent = 0
for r in csv.DictReader(open(idx)):
    if not r['path'].endswith('.json.gz'):
        continue
    indexed_gz += 1
    p = os.path.join(root, r['path'])
    if not os.path.exists(p):
        absent += 1; continue
    c[open(p, 'rb').read(10)[9]] += 1
print({'indexed_json_gz_rows': indexed_gz, 'absent_on_disk': absent, 'os_byte_counts': dict(c)})

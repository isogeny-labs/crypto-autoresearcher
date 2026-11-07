"""Reader's own fb-archive presence/hash check (not fbarchive.py). Every tracked .json.gz/.json.xz under
bases/ must have an index row (path); every git-stored index row's file must exist with matching bytes and
sha256. Usage: python3 -I fbarchive_check.py <fb-archive dir> <index.csv> <tracked_list.txt>"""
import csv, hashlib, os, sys
root, idx, tracked = sys.argv[1:4]
rows = list(csv.DictReader(open(idx)))
paths = {r['path'] for r in rows}
files = [l.strip()[len('experiments/fb-archive/'):] for l in open(tracked) if l.strip().endswith(('.json.gz', '.json.xz')) and '/bases/' in l]
unindexed = sorted(f for f in files if f not in paths)
storage = {}
for r in rows:
    storage[r['storage']] = storage.get(r['storage'], 0) + 1
bad, missing, checked = [], [], 0
for r in rows:
    if r['storage'] != 'git':
        continue
    p = os.path.join(root, r['path'])
    if not os.path.exists(p):
        missing.append(r['path']); continue
    b = open(p, 'rb').read(); checked += 1
    if len(b) != int(r['bytes']) or hashlib.sha256(b).hexdigest() != r['file_sha256']:
        bad.append(r['path'])
print({'index_rows': len(rows), 'storage_counts': storage, 'tracked_archive_files_under_bases': len(files),
       'unindexed_tracked_files': len(unindexed), 'unindexed_sample': unindexed[:5],
       'git_rows_checked': checked, 'git_rows_missing_on_disk': len(missing), 'missing_sample': missing[:5],
       'bytes_or_sha_mismatch': len(bad), 'mismatch_sample': bad[:5]})

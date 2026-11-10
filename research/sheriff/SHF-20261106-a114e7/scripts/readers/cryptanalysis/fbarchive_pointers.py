"""For index rows with storage git whose file is absent: look for an artifacts.manifest/v1 pointer
(.artifacts.json in the file's directory) and compare its sha256/bytes with the index row.
Usage: python3 -I fbarchive_pointers.py <fb-archive dir> <index.csv>"""
import csv, json, os, sys
root, idx = sys.argv[1:3]
res = {'absent': 0, 'pointer_match': 0, 'pointer_mismatch': [], 'no_pointer': []}
for r in csv.DictReader(open(idx)):
    if r['storage'] != 'git':
        continue
    p = os.path.join(root, r['path'])
    if os.path.exists(p):
        continue
    res['absent'] += 1
    man = os.path.join(os.path.dirname(p), '.artifacts.json')
    ent = None
    if os.path.exists(man):
        ent = json.load(open(man)).get('files', {}).get(os.path.basename(p))
    if ent is None:
        res['no_pointer'].append(r['path'])
    elif ent['sha256'] == r['file_sha256'] and int(ent['bytes']) == int(r['bytes']):
        res['pointer_match'] += 1
    else:
        res['pointer_mismatch'].append(r['path'])
print(res)

"""Independent decoder for cryptanalysis:experiments/koblitz-n83-opcounts-20261023 raw stdout.
Reads only the raw per-run stdout files (base64 JSON); writes a flat JSON summary.
Usage: python3 -I decode_runs.py <runs_dir> <out.json>
"""
import base64, json, os, sys
runs_dir, out = sys.argv[1], sys.argv[2]
rows = []
for name in sorted(os.listdir(runs_dir)):
    if not name.endswith('.stdout.txt'):
        continue
    txt = open(os.path.join(runs_dir, name)).read()
    lines = [l for l in txt.splitlines() if l.strip()]
    rec = {'file': name, 'nlines': len(lines), 'other_lines': []}
    for l in lines:
        if l.startswith('raw_b64='):
            rec['decoded'] = json.loads(base64.b64decode(l[len('raw_b64='):]))
        else:
            rec['other_lines'].append(l)
    rows.append(rec)
json.dump(rows, open(out, 'w'), indent=1, sort_keys=True)
print(len(rows), 'stdout files decoded')

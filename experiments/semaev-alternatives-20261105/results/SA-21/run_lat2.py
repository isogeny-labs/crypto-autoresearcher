import json, subprocess, time, sys
cal = {}
for l in open('results/calib.jsonl'):
    r = json.loads(l); cal[(r['fam'], r['k'], r['idx'])] = r
plan = [('E',26,2,3),('W',26,2,3),('E',28,3,2),('W',28,3,2),('E',30,2,1),('W',30,2,1),('E',32,1,0),('W',32,1,0)]
out = open('results/lat.jsonl', 'a')
log = open('results/batches.log', 'a')
for fam, k, nt, t0 in plan:
    arm = 'latW' if fam == 'W' else 'latE'
    for idx in range(3):
        c = cal[(fam, k, idx)]
        if c['B'] == 0:
            out.write(json.dumps(dict(fam=fam, k=k, idx=idx, arm=arm, skipped='no B with F>=3 and recovery>=0.5')) + '\n'); out.flush(); continue
        up = open('/proc/loadavg').read().split()[:3]
        log.write(f"{arm} k={k} idx={idx} B={c['B']} start {time.strftime('%T')} load {' '.join(up)}\n"); log.flush()
        res = subprocess.run(['nice', '-n', '10', './ic', 'curves.txt', fam, str(k), str(idx), arm, str(nt), str(5000 + k * 10 + idx), '-t0', str(t0), '-B', str(c['B']), '-W', '64', '-tmax', '600'], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            r = json.loads(line); r['calib_rate'] = c['rate']; r['calib_F'] = c['F']; out.write(json.dumps(r) + '\n'); out.flush()
log.write('lat done ' + time.strftime('%T') + '\n'); log.close()

# Resume-phase driver (SA-07, resumed run). Same instance generator and formulations as driver.py / sa07.py;
# longer per-instance CPU cap, new seeds, wall-clock budget per invocation so it can run in foreground chunks.
# Skip rule: after 2 consecutive timeouts in increasing B for one (m, bits, form, seed), larger B are not run
# and are recorded as status "skipped" (excluded from fits; listed in the table).
import sys, json, os, random, time
import sa07
m = int(sys.argv[1]); seeds = [int(s) for s in sys.argv[2].split(',')]; tl = float(sys.argv[3])
out = sys.argv[4]; budget = float(sys.argv[5]); bitsl = [int(b) for b in sys.argv[6].split(',')]
Bs = [16, 32, 64, 128, 256] if m == 2 else [4, 8, 16, 32, 64]
done = {}
if os.path.exists(out):
    for l in open(out):
        r = json.loads(l); done[(r['bits'], r['B'], r['form'], r['seed'])] = r['status']
T0 = time.time()
for bits in bitsl:
    for seed in seeds:
        for form in ['vieta', 'raw', 'lll']:
            streak = 0
            for B in Bs:
                key = (bits, B, form, seed)
                if key in done:
                    st = done[key]; streak = streak + 1 if st in ('timelimit', 'skipped') else 0
                    continue
                if time.time() - T0 > budget:
                    print('budget reached'); sys.exit(0)
                p = sa07.make_p(bits, B, seed)
                rng = random.Random(1000 * seed + bits * 7 + B)
                xs, xR = sa07.plant(p, m, B, rng)
                assert sa07.verify(p, m, xs, xR), 'planted solution fails exact check'
                if streak >= 2:
                    r = dict(status='skipped', nodes=None, time=None, prep=0, verified=None, sol=None, planted=xs)
                else:
                    w0 = time.time()
                    try:
                        r = sa07.solve(p, m, B, form, xR, tl, seed, xs)
                    except Exception as e:
                        r = dict(status='error:' + repr(e)[:80], nodes=-1, time=-1, prep=0, verified=None, sol=None, planted=xs)
                    r['wall'] = time.time() - w0
                    streak = streak + 1 if r['status'] == 'timelimit' else 0
                r.update(m=m, bits=bits, B=B, form=form, seed=seed, p=int(p), xR=int(xR), cap=tl, phase='resume')
                open(out, 'a').write(json.dumps(r, default=str) + '\n')
                print(bits, seed, form, B, r['status'], r['nodes'], r.get('time'), flush=True)
print('all done')

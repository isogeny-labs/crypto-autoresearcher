#!/usr/bin/env python3
"""Independent re-implementation of rho_walk_sim.c's walk rules (written from
PROTOCOL.md section 2, not from the C source's code structure) used to check the
C simulator's distribution at a small size. Different PRNG, so agreement is
statistical. Usage: crosscheck.py ARM BITS R TRIALS M"""
import random, sys, math, subprocess, os
WEAK = os.environ.get('WEAK') == '1'

def prime_below(b):
    n = (1 << b) - 1
    def isp(k):
        if k < 2: return False
        i = 2
        while i * i <= k:
            if k % i == 0: return False
            i += 1
        return True
    while not isp(n): n -= 1
    return n

def run(arm, b, r, trials, m, seed=12345):
    n = prime_below(b); half = n // 2; N = (n + 1) // 2
    rnd = random.Random(seed)
    def canon(u): return n - u if u > half else u
    M64 = 2**64 - 1
    def mixc(x):  # the splitmix64 finalizer, as in the C partition (the weak-hash variant is WEAK=1)
        x = (x + 0x9E3779B97F4A7C15) & M64
        x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & M64
        x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & M64
        return x ^ (x >> 31)
    def part(c):
        if WEAK: return ((c * 2654435761 + 40503) ^ (c >> 7)) % 1000003 % r
        return (mixc(c) >> 20) % r
    cap = int(64 * math.sqrt(n)); out = []
    for _ in range(trials):
        t = [rnd.randrange(1, n) for _ in range(r)]
        seen = {}; state = []; ring = []
        for w in range(m):
            while True:
                s = rnd.randrange(0, n if arm == "plain" else N)
                if s not in seen: break
            seen[s] = w; state.append(s); ring.append([s])
        adds = 0; done = False; cens = 0
        while not done:
            for w in range(m):
                s = state[w]; j = part(s)
                if arm == "plain":
                    s2 = (s + t[j]) % n; adds += 1
                else:
                    tries = 1 if arm == "neg0" else 4
                    for k in range(tries):
                        jj = (j + k) % r
                        u = (s + t[jj]) % n; adds += 1
                        s2 = canon(u); fl = u > half
                        if not (fl and part(s2) == jj): break
                    if arm == "neg2":
                        hist = ring[w][-32:]
                        L = 0
                        for kk in range(1, len(hist) + 1):
                            if hist[-kk] == s2: L = kk; break
                        if L:
                            cyc = [s2] + [hist[-d] for d in range(1, L)]
                            best = min(cyc); d = cyc.index(best)
                            adds += (L - d) % L
                            s2 = canon(2 * best % n); adds += 1
                            ring[w] = []
                state[w] = s2; ring[w].append(s2)
                if s2 in seen and seen[s2] != w: done = True; break
                seen.setdefault(s2, w)
                if adds >= cap: done = True; cens = 1; break
        out.append(adds)
    return n, out

if __name__ == "__main__":
    arm, b, r, trials, m = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    n, py = run(arm, b, r, trials, m)
    c = subprocess.run(["/tmp/claude-0/-home-user/01dd893c-0800-598f-b04a-7982c6847a28/scratchpad/rho_walk_sim", arm, str(b), str(r), str(trials), "5", str(m)],
                       capture_output=True, text=True).stdout.splitlines()
    cc = [int(l.split()[1]) for l in c if not l.startswith("#")]
    def stats(x):
        x = sorted(x); mu = sum(x) / len(x); sd = (sum((v - mu) ** 2 for v in x) / (len(x) - 1)) ** .5
        return mu, sd / len(x) ** .5, x[len(x) // 4], x[len(x) // 2], x[3 * len(x) // 4]
    ps, cs = stats(py), stats(cc)
    z = (ps[0] - cs[0]) / math.hypot(ps[1], cs[1])
    print(f"{arm:5s} b={b} r={r:3d} m={m}: python mean {ps[0]:8.1f}±{ps[1]:.1f} quartiles {ps[2:]} | C mean {cs[0]:8.1f}±{cs[1]:.1f} quartiles {cs[2:]} | z={z:+.2f}")

"""Exact checks of the birthday / random-mapping constants in Galbraith ch.14 (Thm 14.1.1, p.287 remarks,
Ex 14.1.2, Ex 14.1.4, Heuristic 14.2.9, Theorem p292-1 (3.093), tail/cycle sqrt(pi N/8)).
Everything here is exact (float64 sums of exact recurrences), no sampling.
X = index of the first repeated sample; P(X>l) = q_l = prod_{j<l}(1-j/N).
For a uniformly random map with uniform start, rho length (#distinct) = X-1, and given rho=l the
cycle length is uniform on 1..l. Validated by brute force over all maps for N<=6 below.
"""
import math, itertools, sys
from fractions import Fraction

def q_list(N):
    q = [1.0]
    for l in range(1, N + 2):
        q.append(q[-1] * (1 - (l - 1) / N))
    return q  # q[l] = P(X > l)

def exact_stats(N):
    q = q_list(N)
    EX = sum(q[:N + 2])
    # rho length distribution P(rho=l) = q[l]*l/N, l=1..N
    Etail = Ecyc = Eep = 0.0
    for l in range(1, N + 1):
        pl = q[l] * l / N
        if pl == 0: continue
        s_ep = 0
        for lam in range(1, l + 1):
            mu = l - lam                      # number of tail (non-cycle) elements
            first = mu + 1                    # 1-based index of first cycle element
            e = lam * max(1, -(-first // lam))
            s_ep += e
        Eep += pl * s_ep / l
        Ecyc += pl * (l + 1) / 2
        Etail += pl * (l - 1) / 2
    return EX, Etail, Ecyc, Eep

def brute(N):
    # all maps, all starts: exact rational expectations
    tot = Fraction(0); tl = Fraction(0); cy = Fraction(0); ep = Fraction(0); cnt = 0
    for f in itertools.product(range(N), repeat=N):
        for s in range(N):
            seq = [s]; seen = {s: 0}
            while True:
                nx = f[seq[-1]]
                if nx in seen:
                    mu = seen[nx]; lam = len(seq) - mu; break
                seen[nx] = len(seq); seq.append(nx)
            # epact: smallest i>=1 with x_{2i}=x_i (1-based)
            def x(i):
                return seq[i - 1] if i - 1 < len(seq) else seq[mu + ((i - 1 - mu) % lam)]
            i = 1
            while x(2 * i) != x(i): i += 1
            tot += len(seq) + 1; tl += mu; cy += lam; ep += i; cnt += 1
    return [float(v / cnt) for v in (tot, tl, cy, ep)]

if __name__ == '__main__':
    print('== brute-force validation of the exact formulas (N<=6) ==')
    for N in range(1, 7):
        b = brute(N); e = exact_stats(N)
        print(N, 'brute', [round(v, 10) for v in b], 'formula', [round(v, 10) for v in e])
        assert all(abs(x - y) < 1e-9 for x, y in zip(b, e))
    print('\n== Thm 14.1.1 bound E[X] < sqrt(pi N/2)+2 ; p.287 E = sqrt(pi N/2)+2/3+O(N^-1/2); Wiener E > sqrt(pi N/2)-0.4 ==')
    worst_gap = 1e9
    for N in list(range(1, 2001)) + [10**4, 10**5, 10**6]:
        q = q_list(N); EX = sum(q[:N + 2]); a = math.sqrt(math.pi * N / 2)
        assert EX < a + 2, N
        assert EX > a - 0.4, N
        worst_gap = min(worst_gap, a + 2 - EX)
        if N in (1, 2, 10, 100, 1000, 10**4, 10**5, 10**6):
            print(f'N={N:8d} E[X]={EX:.6f} sqrt(piN/2)={a:.6f} E-sqrt={EX - a:.6f} (claim +2/3=0.6667)')
    print('min slack of the +2 bound over tested N:', worst_gap)
    print('\n== Wiener lower bound P(X>l) >= exp(-l^2/2N - l^3/6N^2) stated for N>=1000, 0<=l<=2N log N ==')
    for N in (1000, 2000, 10**4):
        q = q_list(N)
        bad = None
        for l in range(0, N + 2):
            lb = math.exp(-l * l / (2 * N) - l ** 3 / (6 * N * N))
            if q[l] < lb * (1 - 1e-12):
                bad = l; break
        print(f'N={N}: first violation at l={bad} (sqrt(2N lnN)={math.sqrt(2*N*math.log(N)):.1f}, 2N lnN={2*N*math.log(N):.0f}); at l=N P=0 but bound={math.exp(-N/2-N/6):.3g}>0')
    print('\n== Ex 14.1.2 / Ex 14.1.4 ==')
    for N in (365, 10**4, 10**6):
        q = q_list(N); med = next(l for l in range(N + 2) if q[l] <= 0.5)
        print(f'N={N}: smallest l with P(collision within l samples)>=1/2 is {med}; sqrt(2 ln2 N)={math.sqrt(2*math.log(2)*N):.2f}')
    q = q_list(365); print('P(shared birthday among 23)=', 1 - q[23], ' among 22=', 1 - q[22])
    print('\n== Heuristic 14.2.9 / Thm p292-1 / tail,cycle sqrt(pi N/8) ==')
    for N in (10**3, 10**4, 10**5):
        EX, Et, Ec, Ee = exact_stats(N)
        a = math.sqrt(math.pi * N / 2)
        print(f'N={N}: E[epact]/sqrt(piN/2)={Ee/a:.5f} (claim 0.8225=zeta(2)/2); 3*E[epact]/sqrt N={3*Ee/math.sqrt(N):.4f} (claim 3.093); '
              f'Algorithm16 walk calls 3e-2 -> {(3*Ee-2)/math.sqrt(N):.4f}; E[tail]/sqrt(piN/8)={Et/math.sqrt(math.pi*N/8):.4f} E[cyc]/sqrt(piN/8)={Ec/math.sqrt(math.pi*N/8):.4f}')
    print('pi^2/12*sqrt(pi/2)*3 =', 3 * math.pi ** 2 / 12 * math.sqrt(math.pi / 2))

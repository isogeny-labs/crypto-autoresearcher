/*
 * rho_walk_sim.c -- counts group additions of an r-adding rho walk on the
 * classes {P, -P} of a cyclic group Z_n (n prime), set-up excluded.
 * See PROTOCOL.md (and its Amendment 1). Counts only; no timing is measured.
 *
 *   rho_walk_sim ARM BITS R TRIALS FAMILY [M]
 *
 * ARM: plain | neg0 | neg1 | neg2 | rm | rm_plain
 * Output (stdout): one line per trial:  trial additions censored
 * First line is a header comment with the parameters and n.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef uint64_t u64;
typedef unsigned __int128 u128;

enum { PLAIN, NEG0, NEG1, NEG2, RM_NEG, RM_PLAIN };
#define W 32            /* cycle-detection window of neg2 */
#define MAXTRIES 4      /* look-ahead retries of neg1 and neg2 */

static inline u64 mix(u64 x) {
    x += 0x9E3779B97F4A7C15ULL;
    x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL;
    x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL;
    return x ^ (x >> 31);
}
static inline u64 sm_next(u64 *s) {
    *s += 0x9E3779B97F4A7C15ULL;
    u64 z = *s;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ---- deterministic Miller-Rabin and the largest prime below 2^b -------- */
static u64 mulmod(u64 a, u64 b, u64 m) { return (u64)((u128)a * b % m); }
static u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1; a %= m;
    while (e) { if (e & 1) r = mulmod(r, a, m); a = mulmod(a, a, m); e >>= 1; }
    return r;
}
static int is_prime(u64 n) {
    if (n < 2) return 0;
    static const u64 bases[] = {2,3,5,7,11,13,17,19,23,29,31,37};
    for (int i = 0; i < 12; i++) { if (n == bases[i]) return 1; if (n % bases[i] == 0) return 0; }
    u64 d = n - 1; int s = 0;
    while ((d & 1) == 0) { d >>= 1; s++; }
    for (int i = 0; i < 12; i++) {
        u64 x = powmod(bases[i], d, n);
        if (x == 1 || x == n - 1) continue;
        int comp = 1;
        for (int j = 1; j < s; j++) { x = mulmod(x, x, n); if (x == n - 1) { comp = 0; break; } }
        if (comp) return 0;
    }
    return 1;
}
static u64 prime_below_pow2(int b) {
    u64 n = (1ULL << b) - 1;
    while (!is_prime(n)) n--;
    return n;
}

/* ---- visited table: open addressing, epoch-stamped, grows on demand ---- */
typedef struct { u64 *key; uint32_t *id, *stamp; u64 cap, count; uint32_t epoch; } Table;
static void tab_alloc(Table *t, u64 cap) {
    t->cap = cap;
    t->key = malloc(cap * sizeof(u64));
    t->id = malloc(cap * sizeof(uint32_t));
    t->stamp = calloc(cap, sizeof(uint32_t));
    t->count = 0;
}
static inline u64 tab_slot(const Table *t, u64 k) { return mix(k ^ 0xABCDEF1234567ULL) & (t->cap - 1); }
static void tab_grow(Table *t) {
    Table n; tab_alloc(&n, t->cap * 2); n.epoch = t->epoch ? t->epoch : 1;
    for (u64 i = 0; i < t->cap; i++) if (t->stamp[i] == t->epoch) {
        u64 s = tab_slot(&n, t->key[i]);
        while (n.stamp[s] == n.epoch) s = (s + 1) & (n.cap - 1);
        n.key[s] = t->key[i]; n.id[s] = t->id[i]; n.stamp[s] = n.epoch; n.count++;
    }
    free(t->key); free(t->id); free(t->stamp); *t = n;
}
/* returns -1 and inserts if absent, else the stored walk id */
static int tab_visit(Table *t, u64 k, uint32_t id) {
    if ((t->count + 1) * 2 > t->cap) tab_grow(t);
    u64 s = tab_slot(t, k);
    while (t->stamp[s] == t->epoch) {
        if (t->key[s] == k) return (int)t->id[s];
        s = (s + 1) & (t->cap - 1);
    }
    t->key[s] = k; t->id[s] = id; t->stamp[s] = t->epoch; t->count++;
    return -1;
}
static void tab_reset(Table *t) { t->epoch++; t->count = 0; }

/* ---- the walk ----------------------------------------------------------- */
typedef struct {
    u64 n, half, N;      /* group order, floor(n/2), number of classes */
    int arm; u64 r;
    u64 *t;              /* jump table */
    u64 salt;            /* random-mapping salt */
} Ctx;

static inline u64 canon(const Ctx *c, u64 u, int *flipped) {
    if (u > c->half) { *flipped = 1; return c->n - u; }
    *flipped = 0; return u;
}
static inline u64 part(const Ctx *c, u64 cls) { return (mix(cls) >> 20) % c->r; }

/* One step of a non-random-mapping walk from class (or point) s.
 * Returns the new state and adds the executed additions to *adds. */
static inline u64 step(const Ctx *c, u64 s, u64 *adds) {
    u64 j = part(c, s);
    if (c->arm == PLAIN) {
        u64 u = s + c->t[j]; if (u >= c->n) u -= c->n;
        (*adds)++; return u;
    }
    int flipped = 0; u64 cls = 0;
    int tries = (c->arm == NEG0) ? 1 : MAXTRIES;
    for (int k = 0; k < tries; k++) {
        u64 jj = (j + k) % c->r;
        u64 u = s + c->t[jj]; if (u >= c->n) u -= c->n;
        (*adds)++;
        cls = canon(c, u, &flipped);
        if (!(flipped && part(c, cls) == jj)) break;   /* not a 2-cycle: accept */
    }
    return cls;
}

typedef struct { u64 ring[W]; int head, cnt; } Ring;   /* last W states of a walk */

/* returns the number of steps back (1..W) at which `cls` already occurred, else 0 */
static int ring_find(const Ring *g, u64 cls) {
    for (int k = 1; k <= g->cnt; k++)
        if (g->ring[(g->head - k + W * 2) % W] == cls) return k;
    return 0;
}
static void ring_push(Ring *g, u64 cls) {
    g->ring[g->head] = cls; g->head = (g->head + 1) % W; if (g->cnt < W) g->cnt++;
}

/* Run one trial. Returns additions; sets *censored. */
static u64 trial(Ctx *c, Table *tab, int M, u64 cap, int *censored,
                 u64 seed, long *escapes) {
    u64 s_rng = seed;
    *censored = 0;
    int is_rm = (c->arm == RM_NEG || c->arm == RM_PLAIN);
    if (!is_rm) for (u64 j = 0; j < c->r; j++) c->t[j] = 1 + sm_next(&s_rng) % (c->n - 1);
    c->salt = sm_next(&s_rng);
    tab_reset(tab);
    u64 *state = malloc(sizeof(u64) * M);
    Ring *rg = calloc(M, sizeof(Ring));
    u64 range = (c->arm == PLAIN || c->arm == RM_PLAIN) ? c->n : c->N;
    for (int w = 0; w < M; w++) {
        for (;;) {
            u64 v = sm_next(&s_rng) % range;
            int fl; if (c->arm == NEG0 || c->arm == NEG1 || c->arm == NEG2) v = canon(c, v % c->n, &fl);
            if (tab_visit(tab, v, (uint32_t)w) < 0) { state[w] = v; break; }
        }
        ring_push(&rg[w], state[w]);
    }
    u64 adds = 0;
    for (;;) {
        for (int w = 0; w < M; w++) {
            u64 cls;
            if (is_rm) {
                cls = mix(state[w] ^ c->salt) % range; adds++;
            } else {
                cls = step(c, state[w], &adds);
                if (c->arm == NEG2) {
                    int L = ring_find(&rg[w], cls);
                    if (L > 0) {                      /* cycle of length L */
                        /* member at offset d steps back (d = 0 is cls itself); pick the smallest class */
                        int bestd = 0; u64 best = cls;
                        for (int d = 1; d < L; d++) {
                            u64 v = rg[w].ring[(rg[w].head - d + W * 2) % W];
                            if (v < best) { best = v; bestd = d; }
                        }
                        adds += (u64)((L - bestd) % L);      /* walk on to that member */
                        int fl; u64 u = best * 2 % c->n;     /* then double it */
                        cls = canon(c, u, &fl); adds++;
                        rg[w].cnt = 0; rg[w].head = 0;
                        (*escapes)++;
                    }
                }
            }
            state[w] = cls;
            ring_push(&rg[w], cls);
            int hit = tab_visit(tab, cls, (uint32_t)w);
            if (hit >= 0 && hit != w) { free(state); free(rg); return adds; }
            if (adds >= cap) { *censored = 1; free(state); free(rg); return adds; }
        }
    }
}

static int arm_of(const char *s) {
    if (!strcmp(s, "plain")) return PLAIN;
    if (!strcmp(s, "neg0")) return NEG0;
    if (!strcmp(s, "neg1")) return NEG1;
    if (!strcmp(s, "neg2")) return NEG2;
    if (!strcmp(s, "rm")) return RM_NEG;
    if (!strcmp(s, "rm_plain")) return RM_PLAIN;
    fprintf(stderr, "unknown arm %s\n", s); exit(2);
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: %s ARM BITS R TRIALS FAMILY [M]\n", argv[0]); return 2; }
    const char *armname = argv[1];
    int arm = arm_of(armname), bits = atoi(argv[2]);
    u64 r = strtoull(argv[3], 0, 10); long trials = atol(argv[4]); int family = atoi(argv[5]);
    int M = argc > 6 ? atoi(argv[6]) : 16;
    Ctx c; memset(&c, 0, sizeof c);
    c.n = prime_below_pow2(bits); c.half = c.n / 2; c.N = (c.n + 1) / 2; c.arm = arm; c.r = r ? r : 1;
    c.t = malloc(sizeof(u64) * (c.r + 1));
    u64 cap = (u64)(64.0 * sqrt((double)c.n));
    Table tab; tab_alloc(&tab, 1ULL << 16); tab.epoch = 1;
    printf("# arm=%s bits=%d n=%llu r=%llu m=%d family=%d trials=%ld cap=%llu\n", armname, bits,
           (unsigned long long)c.n, (unsigned long long)r, M, family, trials, (unsigned long long)cap);
    long escapes = 0;
    for (long k = 0; k < trials; k++) {
        /* seed = splitmix of (arm, bits, r, trial, family): independent of run order and host */
        u64 sd = mix(0x5EEDULL + (u64)arm * 0x100000001B3ULL);
        sd = mix(sd ^ ((u64)bits << 32 | (u64)r)); sd = mix(sd ^ ((u64)family * 0x9E3779B97F4A7C15ULL) ^ (u64)k);
        int cens; u64 a = trial(&c, &tab, M, cap, &cens, sd, &escapes);
        printf("%ld %llu %d\n", k, (unsigned long long)a, cens);
    }
    fprintf(stderr, "arm=%s bits=%d r=%llu escapes=%ld\n", armname, bits, (unsigned long long)r, escapes);
    return 0;
}

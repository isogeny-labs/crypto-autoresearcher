// pext4_census: |E(K)[4]| on the branch-quadruple family y^2 = c prod_{i=1..4} (z - sigma^{a_i} x), K = GF(q^n).
// EXP-PEXT-0b2c75 / H-PEXT-ad0073 (IDEA-20261024-3c71a9; candidate derivation of TASK-20261027-e6b5bf, UNREVIEWED).
//
// For every PGL2(F_q)-orbit of x in K \ F_q (there are (q^n - q)/(q^3 - q) of them) and both coefficient square
// classes c in {1, g} (g a non-square), it builds the pointed Jacobian cubic Y^2 = prod (X - alpha_i),
// alpha_i = -A/(e4 - e_i), A = c prod (e4 - e_i) (derivation.md section 1), and records, from independent code paths:
//   M2  |E(K)[4]| by the published sibling method (cover_census_n.rs four_torsion: x(2P) of every point; verbatim port),
//   M1  |E(K)[4]| = 4 + 4h by the halvability test on the cubic (square differences of the other roots),
//   M3  the law's prediction from the norm-character bits (eps, b_1..b_h, t) via derivation (3.1), (4.2),
//   #E(K) from the cubic and from the quartic model (they must agree), Hasse, the identity chi_K = chi_q o N (4.1).
// Modes (stdout is deterministic JSON lines, wall seconds go to stderr only):
//   family   <p> <f> <n> <S csv> <threads> [validity-only]     q = p^f; S = shift word (a_1..a_4), origin e_4 = sigma^{a_4} x
//   random   <p> <f> <n> <count> <seed> <threads>              negative arm: random 4-subsets of K (any position), both twists
//   (compile: rustc --edition 2021 -O pext4_census.rs)
// The field is GF(p^(f n)) by the sibling's first-primitive-modulus construction (identical to the sibling for f = 1);
// F_q is the subfield {a : a^q = a}.
use std::collections::BTreeMap;

struct Rng(u64);
impl Rng {
    fn new(seed: u64, tag: u64) -> Self { Rng(seed ^ tag.wrapping_mul(0x9E3779B97F4A7C15)) }
    fn next(&mut self) -> u64 { self.0 = self.0.wrapping_add(0x9E3779B97F4A7C15); let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9); z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB); z ^ (z >> 31) }
    fn below(&mut self, n: u32) -> u32 { (self.next() % n as u64) as u32 }
}

// GF(p^d): 0 is zero, e >= 1 is alpha^(e-1). Construction identical to the sibling's Fld::build(q = p, n = d)
// (candidate-by-candidate search; only the exponent table is grown lazily so large fields do not allocate per attempt).
struct Fld { p: u32, qf: u32, nn: u32, size: u32, m: u32, zech: Vec<u32>, el_of: Vec<u32> }
impl Fld {
    fn build(p: u32, f: u32, n: u32) -> Fld {
        let d = f * n; let q = p; let size = p.pow(d); let m = size - 1; let nn = d as usize;
        let digits = |mut i: u32| -> Vec<u32> { let mut v = vec![0; nn]; for k in 0..nn { v[k] = i % q; i /= q; } v };
        let index = |v: &[u32]| -> u32 { let mut i = 0; for k in (0..nn).rev() { i = i * q + v[k]; } i };
        for cand in 0..size { let md = digits(cand);
            for s in 0..q {
                let mut exp_idx: Vec<u32> = Vec::new(); let mut cur = vec![0u32; nn]; cur[0] = 1; let mut ok = true;
                for k in 0..m as usize { let ci = index(&cur); if ci == 0 || (k > 0 && ci == 1) { ok = false; break; } exp_idx.push(ci);
                    let mut nx = vec![0u32; nn]; let top = cur[nn - 1];
                    for i in 0..nn { let sh = if i > 0 { cur[i - 1] } else { 0 }; nx[i] = (sh + (q - md[i]) * top + s * cur[i]) % q; } cur = nx; }
                if !ok || index(&cur) != 1 { continue; }
                let mut el_of = vec![0u32; size as usize];
                for k in 0..m as usize { el_of[exp_idx[k] as usize] = k as u32 + 1; }
                let mut zech = vec![0u32; m as usize];
                for k in 0..m as usize { let mut dv = digits(exp_idx[k]); dv[0] = (dv[0] + 1) % q; zech[k] = el_of[index(&dv) as usize]; }
                return Fld { p, qf: p.pow(f), nn: n, size, m, zech, el_of };
            } }
        panic!("no field");
    }
    #[inline] fn mul(&self, a: u32, b: u32) -> u32 { if a == 0 || b == 0 { 0 } else { let s = a + b - 2; (if s >= self.m { s - self.m } else { s }) + 1 } }
    #[inline] fn inv(&self, a: u32) -> u32 { (self.m - (a - 1)) % self.m + 1 }
    #[inline] fn neg(&self, a: u32) -> u32 { if a == 0 { 0 } else { (a - 1 + self.m / 2) % self.m + 1 } }
    #[inline] fn add(&self, a: u32, b: u32) -> u32 { if a == 0 { return b; } if b == 0 { return a; }
        let dlt = if b >= a { b - a } else { b + self.m - a }; let z = self.zech[dlt as usize]; if z == 0 { 0 } else { let s = a + z - 2; (if s >= self.m { s - self.m } else { s }) + 1 } }
    #[inline] fn sub(&self, a: u32, b: u32) -> u32 { self.add(a, self.neg(b)) }
    #[inline] fn div(&self, a: u32, b: u32) -> u32 { self.mul(a, self.inv(b)) }
    #[inline] fn frobk(&self, a: u32, qk: u64) -> u32 { if a == 0 { 0 } else { (((a - 1) as u64 * qk) % self.m as u64) as u32 + 1 } }
    #[inline] fn frob(&self, a: u32) -> u32 { self.frobk(a, self.qf as u64) }
    #[inline] fn is_sq(&self, a: u32) -> bool { a == 0 || (a - 1) % 2 == 0 }
    fn int(&self, c: i64) -> u32 { self.el_of[c.rem_euclid(self.p as i64) as usize] }
    fn in_fq(&self, a: u32) -> bool { self.frob(a) == a }
    fn qpow(&self, k: u32) -> u64 { let mut r = 1u64; for _ in 0..k { r = r * self.qf as u64 % self.m as u64; } r }
    // chi_K by squares; chi_q of an element of F_q by its logarithm in the subfield (independent of chi_K)
    fn chi_k(&self, a: u32) -> i32 { if a == 0 { 0 } else if self.is_sq(a) { 1 } else { -1 } }
    fn step(&self) -> u32 { self.m / (self.qf - 1) }
    fn chi_q(&self, a: u32) -> i32 { assert!(a != 0 && self.in_fq(a)); let k = (a - 1) / self.step(); if k % 2 == 0 { 1 } else { -1 } }
    fn norm(&self, a: u32) -> u32 { let mut r = 1; for j in 0..self.nn { r = self.mul(r, self.frobk(a, self.qpow(j))); } r }
}

#[derive(Clone, Copy)]
struct Cv { a2: u32, a4: u32, a6: u32 }
fn cubic(f: &Fld, c: &Cv, x: u32) -> u32 { f.add(f.add(f.mul(x, f.mul(x, f.add(x, c.a2))), f.mul(c.a4, x)), c.a6) }
fn dcubic(f: &Fld, c: &Cv, x: u32) -> u32 { f.add(f.add(f.mul(f.int(3), f.mul(x, x)), f.mul(f.int(2), f.mul(c.a2, x))), c.a4) }
fn disc(f: &Fld, c: &Cv) -> u32 { let (b2, b4, b6) = (f.mul(f.int(4), c.a2), f.mul(f.int(2), c.a4), f.mul(f.int(4), c.a6));
    let b8 = f.sub(f.mul(f.int(4), f.mul(c.a2, c.a6)), f.mul(c.a4, c.a4));
    let t1 = f.neg(f.mul(f.mul(b2, b2), b8)); let t2 = f.mul(f.int(8), f.mul(b4, f.mul(b4, b4))); let t3 = f.mul(f.int(27), f.mul(b6, b6)); let t4 = f.mul(f.int(9), f.mul(b2, f.mul(b4, b6)));
    f.add(f.sub(f.sub(t1, t2), t3), t4) }
fn jinv(f: &Fld, c: &Cv) -> u32 { let (b2, b4) = (f.mul(f.int(4), c.a2), f.mul(f.int(2), c.a4)); let c4 = f.sub(f.mul(b2, b2), f.mul(f.int(24), b4)); f.div(f.mul(c4, f.mul(c4, c4)), disc(f, c)) }

struct Res { order: u64, e2: u64, e4: u64 }
// one pass over x in K: #E(K), #E(K)[2], #E(K)[4]. The 4-torsion count is the sibling's method (cover_census_n.rs):
// O, the 2-torsion, and the points P = (x, y), y != 0, with 2P of order 2, x(2P) = f'(x)^2 / (4 f(x)) - a2 - 2x.
fn count(f: &Fld, c: &Cv) -> Res {
    let (mut order, mut roots, mut n4) = (1u64, 0u64, 0u64);
    let four = f.int(4); let two = f.int(2);
    for x in 0..f.size { let v = cubic(f, c, x);
        if v == 0 { order += 1; roots += 1; continue; }
        if !f.is_sq(v) { continue; }
        order += 2;
        let d = dcubic(f, c, x);
        let x2 = f.sub(f.sub(f.div(f.mul(d, d), f.mul(four, v)), c.a2), f.mul(two, x));
        if cubic(f, c, x2) == 0 { n4 += 2; } }
    Res { order, e2: 1 + roots, e4: 1 + roots + n4 }
}
// #C(K) for the smooth model of y^2 = c prod (z - e_i): affine points plus 1 + chi(c) points at infinity
fn quartic_order(f: &Fld, c: u32, e: &[u32; 4]) -> u64 {
    let mut s: i64 = 0;
    for z in 0..f.size { let g = f.mul(c, f.mul(f.mul(f.sub(z, e[0]), f.sub(z, e[1])), f.mul(f.sub(z, e[2]), f.sub(z, e[3])))); s += f.chi_k(g) as i64; }
    (f.size as i64 + s + 1 + f.chi_k(c) as i64) as u64
}

// F_2 rank of the cyclic shifts of the indicator word of S in Z/n and the size of the union: (m, r) of the sibling's genus formula
fn mr_of(s: &[u32], n: u32) -> (u32, u32) {
    let mut vecs: Vec<u32> = Vec::new(); let mut un = 0u32;
    for k in 0..n { let mut v = 0u32; for &a in s { v |= 1 << ((a + k) % n); } vecs.push(v); un |= v; }
    let mut basis: Vec<u32> = Vec::new();
    for mut v in vecs { for b in &basis { if v ^ b < v { v ^= b; } } if v != 0 { basis.push(v); basis.sort_by(|a, b| b.cmp(a)); } }
    (basis.len() as u32, un.count_ones())
}

struct Pgl { m: Vec<[u32; 4]> }
fn pgl2(f: &Fld) -> Pgl {
    let fq: Vec<u32> = (0..f.size).filter(|&a| f.in_fq(a)).collect(); assert_eq!(fq.len() as u32, f.qf);
    let mut out = Vec::new();
    for &a in &fq { for &b in &fq { for &c in &fq { for &d in &fq {
        let first = [a, b, c, d].iter().copied().find(|&v| v != 0).unwrap_or(0); if first != 1 { continue; }
        if f.sub(f.mul(a, d), f.mul(b, c)) == 0 { continue; }
        out.push([a, b, c, d]); } } } }
    assert_eq!(out.len() as u64, (f.qf as u64).pow(3) - f.qf as u64);
    Pgl { m: out }
}
fn orbit_reps(f: &Fld, g: &Pgl) -> Vec<u32> {
    let mut seen = vec![false; f.size as usize]; let mut reps = Vec::new();
    for x in 1..f.size { if f.in_fq(x) || seen[x as usize] { continue; }
        reps.push(x);
        for m in &g.m { let y = f.div(f.add(f.mul(m[0], x), m[1]), f.add(f.mul(m[2], x), m[3])); assert!(!seen[y as usize]); seen[y as usize] = true; } }
    reps
}

fn jstr<T: std::fmt::Display>(v: &[T]) -> String { format!("[{}]", v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")) }


struct Unit { json: String, bad: [u32; 8] }
// bad: 0 M1 != M2, 1 quartic order != cubic order, 2 Hasse, 3 chi_K = chi_q o N (4.1), 4 |E[2]| != 4,
//      5 M2 != law prediction, 6 observed signs != predicted signs (4.2). Slots 5 and 6 are law outcomes.
fn eval_cfg(f: &Fld, e: [u32; 4], c: u32, law: Option<(&[u32], u32)>, prefix: &str) -> Unit {
    let mut bad = [0u32; 8];
    let r = [f.sub(e[3], e[0]), f.sub(e[3], e[1]), f.sub(e[3], e[2])];
    let a_ = f.mul(c, f.mul(r[0], f.mul(r[1], r[2])));
    let al: Vec<u32> = (0..3).map(|i| f.neg(f.div(a_, r[i]))).collect();
    let cv = Cv { a2: f.neg(f.add(al[0], f.add(al[1], al[2]))), a4: f.add(f.mul(al[0], al[1]), f.add(f.mul(al[0], al[2]), f.mul(al[1], al[2]))), a6: f.neg(f.mul(al[0], f.mul(al[1], al[2]))) };
    let rs = count(f, &cv); let oq = quartic_order(f, c, &e);
    let sq = |i: usize, j: usize| f.is_sq(f.sub(al[i], al[j]));
    let w = [sq(0, 1) && sq(0, 2), sq(1, 0) && sq(1, 2), sq(2, 0) && sq(2, 1)];
    let h = w.iter().filter(|&&b| b).count() as u64; let e4m1 = 4 + 4 * h;
    if e4m1 != rs.e4 { bad[0] = 1; }
    if oq != rs.order { bad[1] = 1; }
    let dev = rs.order as i64 - f.size as i64 - 1; if (dev * dev) as u64 > 4 * f.size as u64 { bad[2] = 1; }
    if rs.e2 != 4 { bad[4] = 1; }
    let s_obs: [i32; 3] = [f.chi_k(f.sub(al[0], al[1])), f.chi_k(f.sub(al[0], al[2])), f.chi_k(f.sub(al[1], al[2]))];
    let eps = f.chi_q(f.neg(1)); let t = f.chi_k(c);
    let j = jinv(f, &cv);
    let mut js = format!("{{\"rec\":\"{}\",{}\"t\":{},\"eps\":{}", if law.is_some() { "unit" } else { "rand" }, prefix, t, eps);
    if let Some((s, x)) = law {
        let n = f.nn as i32; let hh = (n - 1) / 2;
        let mut bits = Vec::new();
        for k in 1..=hh { let z = f.sub(x, f.frobk(x, f.qpow(k as u32)));
            let b = f.chi_q(f.norm(z)); if b != f.chi_k(z) { bad[3] = 1; } bits.push(b); }
        let beta = |k: i32| -> i32 { let k = k.rem_euclid(n); if k <= hh { bits[(k - 1) as usize] } else { eps * bits[(n - k - 1) as usize] } };
        let a: Vec<i32> = s.iter().map(|&v| v as i32).collect();
        let s_pred = [t * beta(a[1] - a[0]) * beta(a[3] - a[2]), t * beta(a[2] - a[0]) * beta(a[3] - a[1]), t * beta(a[2] - a[1]) * beta(a[3] - a[0])];
        let hp = (s_pred[0] == 1 && s_pred[1] == 1) as u64 + (eps * s_pred[0] == 1 && s_pred[2] == 1) as u64 + (eps * s_pred[1] == 1 && eps * s_pred[2] == 1) as u64;
        let e4p = 4 + 4 * hp;
        if e4p != rs.e4 { bad[5] = 1; }
        if s_pred != s_obs { bad[6] = 1; }
        js += &format!(",\"bits\":{},\"s_pred\":{},\"E4_pred\":{}", jstr(&bits), jstr(&s_pred), e4p);
    }
    js += &format!(",\"s_obs\":{},\"order\":{},\"order_quartic\":{},\"E2\":{},\"E4\":{},\"E4_M1\":{},\"j\":{},\"j_fq\":{},\"j0\":{},\"j1728\":{}}}",
        jstr(&s_obs), rs.order, oq, rs.e2, rs.e4, e4m1, j, f.in_fq(j), j == 0, j == f.int(1728));
    Unit { json: js, bad }
}

fn par<T: Send, F: Fn(usize) -> T + Sync>(n: usize, threads: usize, body: F) -> Vec<T> {
    let mut out: Vec<Option<T>> = (0..n).map(|_| None).collect();
    let chunk = (n + threads - 1) / threads.max(1);
    std::thread::scope(|sc| { let body = &body;
        let hs: Vec<_> = out.chunks_mut(chunk.max(1)).enumerate().map(|(ci, sl)| sc.spawn(move || { for (k, slot) in sl.iter_mut().enumerate() { *slot = Some(body(ci * chunk + k)); } })).collect();
        for h in hs { h.join().unwrap(); } });
    out.into_iter().map(|o| o.unwrap()).collect()
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let t0 = std::time::Instant::now();
    let mode = a[1].as_str();
    let (p, fdeg, n): (u32, u32, u32) = (a[2].parse().unwrap(), a[3].parse().unwrap(), a[4].parse().unwrap());
    let f = Fld::build(p, fdeg, n); let q = f.qf; let nonsq = 2u32; assert!(!f.is_sq(nonsq));
    eprintln!("field q={} n={} size={} built {:.1}s", q, n, f.size, t0.elapsed().as_secs_f64());
    if mode == "family" {
        let s: Vec<u32> = a[5].split(',').map(|v| v.parse().unwrap()).collect(); assert_eq!(s.len(), 4);
        let threads: usize = a[6].parse().unwrap(); let validity = a.get(7).map(|v| v == "validity-only").unwrap_or(false);
        let (m, r) = mr_of(&s, n); let genus = if m >= 2 { (1u64 << (m - 2)) * (r as u64 - 4) + 1 } else { 0 };
        let g = pgl2(&f); let reps = orbit_reps(&f, &g);
        let expected = (f.size as u64 - q as u64) / ((q as u64).pow(3) - q as u64);
        assert_eq!(reps.len() as u64, expected);
        println!("{{\"rec\":\"field\",\"p\":{},\"f\":{},\"q\":{},\"n\":{},\"size\":{},\"S\":{},\"m\":{},\"r\":{},\"genus\":{},\"orbits\":{},\"orbits_expected\":{},\"units\":{},\"validity_only\":{}}}",
            p, fdeg, q, n, f.size, jstr(&s), m, r, genus, reps.len(), expected, 2 * reps.len(), validity);
        let units = par(2 * reps.len(), threads, |i| { let x = reps[i / 2]; let c = if i % 2 == 0 { 1 } else { nonsq };
            let e = [f.frobk(x, f.qpow(s[0])), f.frobk(x, f.qpow(s[1])), f.frobk(x, f.qpow(s[2])), f.frobk(x, f.qpow(s[3]))];
            eval_cfg(&f, e, c, Some((&s, x)), &format!("\"orbit\":{},\"x\":{},", i / 2, x)) });
        let mut tot = [0u32; 8];
        for u in &units { for k in 0..8 { tot[k] += u.bad[k]; } if !validity { println!("{}", u.json); } }
        let law = if validity { "null".to_string() } else { format!("{{\"e4_vs_law\":{},\"signs_vs_4_2\":{}}}", tot[5], tot[6]) };
        println!("{{\"rec\":\"totals\",\"q\":{},\"n\":{},\"S\":{},\"units\":{},\"m1_m2_mismatch\":{},\"quartic_cubic_order_mismatch\":{},\"hasse_fail\":{},\"chi_norm_identity_mismatch\":{},\"e2_not_4\":{},\"law\":{}}}",
            q, n, jstr(&s), units.len(), tot[0], tot[1], tot[2], tot[3], tot[4], law);
    } else if mode == "random" {
        let count: usize = a[5].parse().unwrap(); let seed: u64 = a[6].parse().unwrap(); let threads: usize = a[7].parse().unwrap();
        let mut rng = Rng::new(seed, 1000 * q as u64 + 10 * n as u64 + 4);
        let mut cfgs: Vec<[u32; 4]> = Vec::new();
        while cfgs.len() < count { let mut e = [0u32; 4]; let mut ok = true;
            for i in 0..4 { e[i] = rng.below(f.size); for j in 0..i { if e[j] == e[i] { ok = false; } } }
            if ok { cfgs.push(e); } }
        println!("{{\"rec\":\"field\",\"p\":{},\"f\":{},\"q\":{},\"n\":{},\"size\":{},\"mode\":\"random\",\"configs\":{},\"seed\":{}}}", p, fdeg, q, n, f.size, count, seed);
        let units = par(2 * count, threads, |i| { let e = cfgs[i / 2]; let c = if i % 2 == 0 { 1 } else { nonsq };
            let orb: Vec<u32> = (0..n).map(|k| f.frobk(e[0], f.qpow(k))).collect();
            let fam = !f.in_fq(e[0]) && e[1..].iter().all(|v| orb.contains(v));
            eval_cfg(&f, e, c, None, &format!("\"cfg\":{},\"e\":{},\"in_family\":{},", i / 2, jstr(&e), fam)) });
        let mut tot = [0u32; 8];
        for u in &units { for k in 0..8 { tot[k] += u.bad[k]; } println!("{}", u.json); }
        println!("{{\"rec\":\"totals\",\"q\":{},\"n\":{},\"units\":{},\"m1_m2_mismatch\":{},\"quartic_cubic_order_mismatch\":{},\"hasse_fail\":{},\"e2_not_4\":{}}}",
            q, n, units.len(), tot[0], tot[1], tot[2], tot[4]);
    } else if mode == "fix" {
        // positive-control helper: invariants of the sibling's curves given by polynomial-basis indices a2:a4:a6 (the fixture's *_idx fields)
        for tr in &a[5..] { let v: Vec<usize> = tr.split(':').map(|x| x.parse().unwrap()).collect();
            let cv = Cv { a2: f.el_of[v[0]], a4: f.el_of[v[1]], a6: f.el_of[v[2]] }; let rs = count(&f, &cv); let j = jinv(&f, &cv);
            println!("{{\"rec\":\"fix\",\"idx\":\"{}\",\"order\":{},\"E2\":{},\"E4\":{},\"j\":{},\"j_fq\":{}}}", tr, rs.order, rs.e2, rs.e4, j, f.in_fq(j)); }
    } else if mode == "mr" {
        // (m, r, genus) of every 4-subset class of Z/n up to rotation (derivation aid: which S are minimal-genus words)
        let mut seen = BTreeMap::new();
        for mask in 0u32..(1 << n) { if mask.count_ones() != 4 { continue; }
            let s: Vec<u32> = (0..n).filter(|b| mask >> b & 1 == 1).collect();
            let canon = (0..n).map(|k| { let mut v: Vec<u32> = s.iter().map(|x| (x + k) % n).collect(); v.sort(); v }).min().unwrap();
            let (m, r) = mr_of(&canon, n); seen.entry(canon).or_insert((m, r)); }
        for (s, (m, r)) in &seen { println!("{{\"rec\":\"mr\",\"n\":{},\"S\":{},\"m\":{},\"r\":{},\"genus\":{}}}", n, jstr(s), m, r, if *m >= 2 { (1u64 << (m - 2)) * (*r as u64 - 4) + 1 } else { 0 }); }
    } else { panic!("mode"); }
    eprintln!("done {:.1}s", t0.elapsed().as_secs_f64());
}

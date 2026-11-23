//! Degree-of-regularity test for PKM chain vs dense Semaev encodings.
//!
//! Generates the same small PKM factor base in two encodings, writes msolve
//! inputs, runs msolve with F4 verbose tracing, and parses the per-round
//! degree to estimate d_reg. Chain arm A: L quadratic Velu equations per
//! point (mL variables). Dense arm B: one degree-2^L minimal polynomial per
//! x variable (m variables). Both use the same S_{m+1} equation.

use serde_json::{json, Value};
use std::fs;
use std::process::Command;
use std::time::Instant;

#[derive(Clone, Copy)]
struct Curve {
    a: u64,
    b: u64,
}

type P = Option<(u64, u64)>;

fn add(a: u64, b: u64, p: u64) -> u64 {
    let s = a + b;
    if s >= p { s - p } else { s }
}
fn sub(a: u64, b: u64, p: u64) -> u64 {
    if a >= b { a - b } else { p - (b - a) }
}
fn mul(a: u64, b: u64, p: u64) -> u64 {
    ((a as u128 * b as u128) % p as u128) as u64
}
fn powmod(mut a: u64, mut e: u64, p: u64) -> u64 {
    let mut r = 1u64;
    a %= p;
    while e > 0 {
        if e & 1 == 1 {
            r = mul(r, a, p);
        }
        a = mul(a, a, p);
        e >>= 1;
    }
    r
}
fn inv(a: u64, p: u64) -> u64 {
    powmod(a, p - 2, p)
}
fn sqrt(a: u64, p: u64) -> Option<u64> {
    if a == 0 {
        return Some(0);
    }
    let r = powmod(a, (p + 1) / 4, p);
    if mul(r, r, p) == a { Some(r) } else { None }
}

fn padd(q1: &P, q2: &P, a: u64, p: u64) -> P {
    let q1 = match q1 { None => return *q2, Some(v) => v };
    let q2 = match q2 { None => return Some(*q1), Some(v) => v };
    if q1.0 == q2.0 {
        if add(q1.1, q2.1, p) == 0 {
            return None;
        }
        let num = add(mul(3, mul(q1.0, q1.0, p), p), a, p);
        let den = mul(2, q1.1, p);
        let lam = mul(num, inv(den, p), p);
        let x3 = sub(sub(mul(lam, lam, p), q1.0, p), q2.0, p);
        return Some((x3, sub(mul(lam, sub(q1.0, x3, p), p), q1.1, p)));
    }
    let lam = mul(sub(q2.1, q1.1, p), inv(sub(q2.0, q1.0, p), p), p);
    let x3 = sub(sub(mul(lam, lam, p), q1.0, p), q2.0, p);
    Some((x3, sub(mul(lam, sub(q1.0, x3, p), p), q1.1, p)))
}

fn pmul(k: u64, q: &P, a: u64, p: u64) -> P {
    let mut acc: P = None;
    for i in (0..64).rev() {
        acc = padd(&acc, &acc, a, p);
        if (k >> i) & 1 == 1 {
            acc = padd(&acc, q, a, p);
        }
    }
    acc
}

fn is_prime(n: u64) -> bool {
    if n < 2 { return false; }
    for &q in &[2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        if n % q == 0 { return n == q; }
    }
    let mut d = n - 1;
    let mut s = 0;
    while d % 2 == 0 { d /= 2; s += 1; }
    for &a in &[2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        let mut x = powmod(a, d, n);
        if x == 1 || x == n - 1 { continue; }
        let mut ok = false;
        for _ in 0..s - 1 {
            x = mul(x, x, n);
            if x == n - 1 { ok = true; break; }
        }
        if !ok { return false; }
    }
    true
}

/// p > 2^(m L), p = 3 mod 4, v2(p+1) >= L+2.
fn find_prime(m: usize, l: usize) -> u64 {
    let bits = (m * l) as u32;
    let min = 1u64 << bits;
    let step = 1u64 << (l + 2);
    let mut k = (min + step) / step;
    loop {
        let p = k * step - 1;
        if p > min && p % 4 == 3 && is_prime(p) {
            return p;
        }
        k += 1;
    }
}

fn build_chain(p: u64, l: usize, seed: u64) -> (Curve, u64, u64, Vec<(u64, u64)>) {
    // find R of exact 2-adic order v2(p+1)
    let v2 = (p + 1).trailing_zeros() as usize;
    assert!(v2 >= l + 2);
    let mut s = seed | 1;
    let r = loop {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        let x = s % p;
        let rhs = add(mul(mul(x, x, p), x, p), x, p);
        if let Some(y) = sqrt(rhs, p) {
            let r0 = pmul((p + 1) >> v2, &Some((x, y)), 1, p);
            if let Some(q) = r0 {
                if pmul(1u64 << (v2 - 1), &Some(q), 1, p).is_some()
                    && pmul(1u64 << v2, &Some(q), 1, p).is_none()
                {
                    break q;
                }
            }
        }
    };
    let k = pmul((p + 1) >> l, &Some(r), 1, p).expect("kernel");
    assert!(pmul(1u64 << (l - 1), &Some(k), 1, p).is_some());
    assert!(pmul(1u64 << l, &Some(k), 1, p).is_none());

    let mut curve = Curve { a: 1, b: 0 };
    let mut kk = Some(k);
    let mut rcur = Some(r);
    let mut steps = Vec::new();
    for i in 0..l {
        let kk0 = kk.expect("kernel alive");
        let k2 = pmul(1u64 << (l - i - 1), &Some(kk0), curve.a, p).expect("2-torsion");
        assert!(k2.1 == 0);
        let x0 = k2.0;
        let t = add(mul(3, mul(x0, x0, p), p), curve.a, p);
        let w = mul(x0, t, p);
        let a2 = sub(curve.a, mul(5, t, p), p);
        let b2 = sub(curve.b, mul(7, w, p), p);
        curve = Curve { a: a2, b: b2 };

        let eval = |q: P| -> P {
            let q = q?;
            if q.0 == x0 { return None; }
            let d = inv(sub(q.0, x0, p), p);
            let x = add(q.0, mul(t, d, p), p);
            let d2 = mul(d, d, p);
            let y = mul(q.1, sub(1, mul(t, d2, p), p), p);
            Some((x, y))
        };
        kk = eval(kk);
        rcur = eval(rcur);
        steps.push((x0, t));
    }
    assert!(kk.is_none());
    let c = rcur.expect("R image finite for subchain");
    let v = {
        let count = 1usize << l;
        let mut pts = Vec::with_capacity(count);
        let mut q = Some(r);
        for _ in 0..count {
            pts.push(q.unwrap().0);
            q = padd(&q, &Some(k), 1, p);
        }
        pts
    };
    (curve, c.0, r.0, steps) // placeholder c replaced below
}

fn v_and_steps(p: u64, l: usize, seed: u64) -> (u64, u64, u64, Vec<u64>, Vec<(u64, u64)>) {
    // repeats the chain build but keeps V; kept separate to keep the code simple
    let v2 = (p + 1).trailing_zeros() as usize;
    let mut s = seed | 1;
    let r = loop {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        let x = s % p;
        let rhs = add(mul(mul(x, x, p), x, p), x, p);
        if let Some(y) = sqrt(rhs, p) {
            let r0 = pmul((p + 1) >> v2, &Some((x, y)), 1, p);
            if let Some(q) = r0 {
                if pmul(1u64 << (v2 - 1), &Some(q), 1, p).is_some()
                    && pmul(1u64 << v2, &Some(q), 1, p).is_none()
                {
                    break q;
                }
            }
        }
    };
    let k = pmul((p + 1) >> l, &Some(r), 1, p).expect("kernel");
    let mut curve = Curve { a: 1, b: 0 };
    let mut kk = Some(k);
    let mut rcur = Some(r);
    let mut steps = Vec::new();
    for i in 0..l {
        let kk0 = kk.expect("kernel");
        let k2 = pmul(1u64 << (l - i - 1), &Some(kk0), curve.a, p).expect("2-torsion");
        let x0 = k2.0;
        let t = add(mul(3, mul(x0, x0, p), p), curve.a, p);
        let w = mul(x0, t, p);
        curve = Curve {
            a: sub(curve.a, mul(5, t, p), p),
            b: sub(curve.b, mul(7, w, p), p),
        };
        let eval = |q: P| -> P {
            let q = q?;
            if q.0 == x0 { return None; }
            let d = inv(sub(q.0, x0, p), p);
            let x = add(q.0, mul(t, d, p), p);
            let d2 = mul(d, d, p);
            let y = mul(q.1, sub(1, mul(t, d2, p), p), p);
            Some((x, y))
        };
        kk = eval(kk);
        rcur = eval(rcur);
        steps.push((x0, t));
    }
    let c = rcur.expect("R image").0;
    let count = 1usize << l;
    let mut v = Vec::with_capacity(count);
    let mut q = Some(r);
    for _ in 0..count {
        v.push(q.unwrap().0);
        q = padd(&q, &Some(k), 1, p);
    }
    (r.0, k.0, c, v, steps)
}

fn poly_from_roots(roots: &[u64], p: u64) -> Vec<u64> {
    let mut c = vec![1u64];
    for &r in roots {
        let mut n = vec![0u64; c.len() + 1];
        for (i, &ci) in c.iter().enumerate() {
            n[i] = sub(n[i], mul(r, ci, p), p);
            n[i + 1] = add(n[i + 1], ci, p);
        }
        c = n;
    }
    c
}

fn dense_poly(c: &[u64], var: &str) -> String {
    let mut terms = Vec::new();
    for (i, &ci) in c.iter().enumerate() {
        if ci == 0 { continue; }
        let t = match i {
            0 => format!("{}", ci),
            1 => format!("{}*{}", ci, var),
            _ => format!("{}*{}^{}", ci, var, i),
        };
        terms.push(t);
    }
    if terms.is_empty() { "0".into() } else { terms.join("+") }
}

// Flat polynomial arithmetic so msolve never sees parentheses.
#[derive(Clone)]
struct Poly {
    p: u64,
    terms: std::collections::HashMap<Vec<u32>, u64>,
}

impl Poly {
    fn zero(p: u64) -> Self { Poly { p, terms: std::collections::HashMap::new() } }
    fn constant(c: u64, p: u64) -> Self {
        let mut t = std::collections::HashMap::new();
        let c = c % p;
        if c != 0 { t.insert(Vec::new(), c); }
        Poly { p, terms: t }
    }
    fn var(i: usize, nvars: usize, p: u64) -> Self {
        let mut e = vec![0u32; nvars];
        e[i] = 1;
        let mut t = std::collections::HashMap::new();
        t.insert(e, 1);
        Poly { p, terms: t }
    }
    fn add_term(&mut self, e: Vec<u32>, c: u64) {
        let c = c % self.p;
        if c == 0 { return; }
        let v = self.terms.entry(e).or_insert(0);
        *v = (*v + c) % self.p;
    }
    fn add(&self, other: &Poly) -> Poly {
        let mut r = self.clone();
        for (e, c) in &other.terms { r.add_term(e.clone(), *c); }
        r
    }
    fn neg(&self) -> Poly {
        let mut r = self.clone();
        for c in r.terms.values_mut() { *c = (self.p - *c) % self.p; }
        r
    }
    fn sub(&self, other: &Poly) -> Poly { self.add(&other.neg()) }
    fn mul(&self, other: &Poly) -> Poly {
        let mut r = Poly::zero(self.p);
        for (e1, c1) in &self.terms {
            for (e2, c2) in &other.terms {
                let mut e = e1.clone();
                if e.len() < e2.len() { e.resize(e2.len(), 0); }
                for (i, x) in e2.iter().enumerate() { e[i] += x; }
                r.add_term(e, mul(*c1, *c2, self.p));
            }
        }
        r
    }
    fn scale(&self, c: u64) -> Poly {
        let mut r = self.clone();
        for v in r.terms.values_mut() { *v = mul(*v, c, self.p); }
        r
    }
    fn render(&self, vars: &[String]) -> String {
        let mut out = Vec::new();
        let mut keys: Vec<&Vec<u32>> = self.terms.keys().filter(|e| self.terms[*e] != 0).collect();
        keys.sort();
        for e in keys {
            let c = self.terms[e];
            let mut factors = Vec::new();
            for (i, &x) in e.iter().enumerate() {
                if x == 1 { factors.push(vars[i].clone()); }
                else if x > 1 { factors.push(format!("{}^{}", vars[i], x)); }
            }
            let mono = factors.join("*");
            let s = if mono.is_empty() { format!("{}", c) }
                else if c == 1 { mono }
                else { format!("{}*{}", c, mono) };
            out.push(s);
        }
        if out.is_empty() { "0".into() } else { out.join("+") }
    }
}

fn s3_poly(v1: &Poly, v2: &Poly, v3: &Poly, a: u64, b: u64, p: u64) -> Poly {
    let v1 = v1.clone();
    let v2 = v2.clone();
    let v3 = v3.clone();
    let one = Poly::constant(1, p);
    let two = Poly::constant(2, p);
    let four = Poly::constant(4, p);
    // (x1-x2)^2 x3^2
    let d = v1.sub(&v2);
    let lhs = d.mul(&d).mul(&v3).mul(&v3);
    // -2 ((x1+x2)(x1 x2 + a) + 2b) x3
    let sum = v1.add(&v2);
    let prod_a = v1.mul(&v2).add(&Poly::constant(a, p));
    let mid = sum.mul(&prod_a).add(&two.scale(b)).mul(&v3).scale(2);
    // (x1 x2 - a)^2 - 4b(x1+x2)
    let pa = v1.mul(&v2).sub(&Poly::constant(a, p));
    let last = pa.mul(&pa).sub(&four.scale(b).mul(&sum));
    let _ = one;
    lhs.sub(&mid).add(&last)
}

fn s3(x1: &str, x2: &str, x3: &str, a: u64, b: u64) -> String {
    format!("(({x1}-{x2})^2*{x3}^2-2*(({x1}+{x2})*({x1}*{x2}+{a})+2*{b})*{x3}+({x1}*{x2}-{a})^2-4*{b}*({x1}+{x2}))")
}

fn write_msolve(path: &str, vars: &[String], p: u64, eqs: &[String]) {
    let body = format!("{}\n{}\n{}\n", vars.join(","), p, eqs.join(",\n"));
    fs::write(path, body).unwrap();
}

fn parse_msolve(text: &str) -> Value {
    let mut rounds = 0usize;
    let mut max_deg = 0u32;
    let mut total_new = 0usize;
    let mut total_zero = 0usize;
    let mut mats = Vec::new();
    for line in text.lines() {
        let tok: Vec<&str> = line.split_whitespace().collect();
        if tok.len() < 4 { continue; }
        let deg = tok[0].parse::<u32>();
        let sel = tok[1].parse::<u32>();
        if deg.is_err() || sel.is_err() { continue; }
        if !line.contains("new") { continue; }
        rounds += 1;
        max_deg = max_deg.max(deg.unwrap());
        // ... "new" then count
        if let Some(pos) = tok.iter().position(|&x| x == "new") {
            if let Some(n) = tok.get(pos + 1).and_then(|x| x.parse::<usize>().ok()) {
                total_new += n;
            }
        }
        if let Some(pos) = tok.iter().position(|&x| x == "zero") {
            if let Some(n) = tok.get(pos + 1).and_then(|x| x.parse::<usize>().ok()) {
                total_zero += n;
            }
        }
        if let Some(pos) = tok.iter().position(|&x| x.contains('x')) {
            mats.push(tok[pos].to_string());
        }
    }
    json!({
        "rounds": rounds,
        "max_deg": if rounds == 0 { Value::Null } else { json!(max_deg) },
        "new": total_new,
        "zero": total_zero,
        "mat": mats,
    })
}

fn run_case(m: usize, l: usize, seed: u64, timeout: u64) -> Value {
    let p = find_prime(m, l);
    let (rx, kx, c, v, steps) = v_and_steps(p, l, seed);
    let a = sub(0, 3, p); // -3
    // deterministic b from seed; ensure nonsingular
    let b = (seed % (p - 1)) + 1;
    // factor base x-values that lift on y^2 = x^3 - 3x + b
    let mut fbx = Vec::new();
    for &x in &v {
        let rhs = add(sub(mul(mul(x, x, p), x, p), mul(3, x, p), p), b, p);
        if sqrt(rhs, p).is_some() { fbx.push(x); }
    }
    // planted m points, deterministic
    let mut s = seed ^ 0x9e3779b97f4a7c15;
    let mut picks = Vec::new();
    for _ in 0..m {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        if fbx.is_empty() { break; }
        let x = fbx[(s as usize) % fbx.len()];
        let y = sqrt(add(sub(mul(mul(x, x, p), x, p), mul(3, x, p), p), b, p), p).unwrap();
        picks.push((x, y));
    }
    let mut t: P = None;
    for &q in &picks {
        t = padd(&t, &Some(q), a, p);
    }
    let tx = t.expect("target").0;

    let mut vars_a: Vec<String> = (1..=m).map(|i| format!("x{}", i)).collect();
    for i in 1..=m {
        for j in 1..l {
            vars_a.push(format!("w{}_{}", i, j));
        }
    }
    let mut vars_b: Vec<String> = (1..=m).map(|i| format!("x{}", i)).collect();
    let mut has_x = false;
    if m == 3 {
        vars_a.push("X".into());
        vars_b.push("X".into());
        has_x = true;
    }

    let idx_a: std::collections::HashMap<String, usize> =
        vars_a.iter().cloned().enumerate().map(|(i, s)| (s, i)).collect();
    let idx_b: std::collections::HashMap<String, usize> =
        vars_b.iter().cloned().enumerate().map(|(i, s)| (s, i)).collect();

    let mut eqs_a = Vec::new();
    let mut eqs_b = Vec::new();
    for i in 1..=m {
        // chain equations
        let mut chain_vars: Vec<String> = vec![format!("x{}", i)];
        for j in 1..l {
            chain_vars.push(format!("w{}_{}", i, j));
        }
        for (j, &(x0, tt)) in steps.iter().enumerate() {
            let u = Poly::var(idx_a[&chain_vars[j]], vars_a.len(), p);
            let vv = if j + 1 < chain_vars.len() {
                Poly::var(idx_a[&chain_vars[j + 1]], vars_a.len(), p)
            } else {
                Poly::constant(c, p)
            };
            // (v-u)(u-x0)-t
            let expr = vv.sub(&u).mul(&u.sub(&Poly::constant(x0, p))).sub(&Poly::constant(tt, p));
            eqs_a.push(expr.render(&vars_a));
        }
        let coeffs = poly_from_roots(&v, p);
        eqs_b.push(dense_poly(&coeffs, &format!("x{}", i)));
    }
    let txpoly = Poly::constant(tx, p);
    if m == 2 {
        let a1 = Poly::var(idx_a["x1"], vars_a.len(), p);
        let a2 = Poly::var(idx_a["x2"], vars_a.len(), p);
        eqs_a.push(s3_poly(&a1, &a2, &txpoly, a, b, p).render(&vars_a));
        let b1 = Poly::var(idx_b["x1"], vars_b.len(), p);
        let b2 = Poly::var(idx_b["x2"], vars_b.len(), p);
        eqs_b.push(s3_poly(&b1, &b2, &txpoly, a, b, p).render(&vars_b));
    } else if m == 3 && has_x {
        let xa = Poly::var(idx_a["X"], vars_a.len(), p);
        let a1 = Poly::var(idx_a["x1"], vars_a.len(), p);
        let a2 = Poly::var(idx_a["x2"], vars_a.len(), p);
        let a3 = Poly::var(idx_a["x3"], vars_a.len(), p);
        eqs_a.push(s3_poly(&a1, &a2, &xa, a, b, p).render(&vars_a));
        eqs_a.push(s3_poly(&a3, &txpoly, &xa, a, b, p).render(&vars_a));

        let xb = Poly::var(idx_b["X"], vars_b.len(), p);
        let b1 = Poly::var(idx_b["x1"], vars_b.len(), p);
        let b2 = Poly::var(idx_b["x2"], vars_b.len(), p);
        let b3 = Poly::var(idx_b["x3"], vars_b.len(), p);
        eqs_b.push(s3_poly(&b1, &b2, &xb, a, b, p).render(&vars_b));
        eqs_b.push(s3_poly(&b3, &txpoly, &xb, a, b, p).render(&vars_b));
    }

    let dir = format!("/Volumes/SSD990/llm/tmp/opencode/dreg-pkm/cases/m{}L{}", m, l);
    fs::create_dir_all(&dir).unwrap();
    let fa = format!("{}/A.ms", dir);
    let fb = format!("{}/B.ms", dir);
    write_msolve(&fa, &vars_a, p, &eqs_a);
    write_msolve(&fb, &vars_b, p, &eqs_b);

    let run = |path: &str| -> Value {
        let t0 = Instant::now();
        let out = Command::new("timeout")
            .arg(timeout.to_string())
            .arg("msolve")
            .arg("-f").arg(path)
            .arg("-v").arg("2")
            .output();
        let secs = t0.elapsed().as_secs_f64();
        match out {
            Ok(o) => {
                let text = format!("{}{}", String::from_utf8_lossy(&o.stdout), String::from_utf8_lossy(&o.stderr));
                let mut v = parse_msolve(&text);
                v["secs"] = json!(secs);
                v["exit"] = json!(o.status.code());
                v["no_solution"] = json!(text.contains("[-1]"));
                v["tail"] = json!(text.lines().rev().take(3).collect::<Vec<_>>().join(" | "));
                v
            }
            Err(e) => json!({"error": e.to_string(), "secs": secs}),
        }
    };
    let ra = run(&fa);
    let rb = run(&fb);
    let da = ra["max_deg"].as_u64();
    let db = rb["max_deg"].as_u64();
    json!({
        "m": m, "L": l, "p": p, "p_bits": 64 - p.leading_zeros(),
        "v2_p_plus_1": (p + 1).trailing_zeros(),
        "V_size": v.len(), "fb_size": fbx.len(),
        "target_x": tx, "R_x": rx, "K_x": kx, "c": c,
        "A": ra, "B": rb,
        "dreg_A": da, "dreg_B": db,
        "dreg_advantage_B_minus_A": match (da, db) { (Some(x), Some(y)) => json!(y as i64 - x as i64), _ => Value::Null },
    })
}

fn main() {
    let mut out = Vec::new();
    let configs = [
        (2usize, 3usize), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
        (3, 3), (3, 4), (3, 5),
    ];
    for &(m, l) in &configs {
        for rep in 0..3u64 {
            let seed = 0x1234_5678_9abc_def0u64
                ^ ((m as u64) << 40)
                ^ ((l as u64) << 8)
                ^ (rep + 1);
            let v = run_case(m, l, seed, 60);
            println!("{}", serde_json::to_string(&v).unwrap());
            out.push(v);
        }
    }
    fs::write(
        "/Volumes/SSD990/llm/tmp/opencode/dreg-pkm/results.json",
        serde_json::to_string_pretty(&out).unwrap(),
    ).unwrap();
}

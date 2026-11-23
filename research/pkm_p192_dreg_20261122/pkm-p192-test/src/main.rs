//! PKM p+1 supersingular auxiliary-curve test over the NIST P-192 prime.
//!
//! Construction/metrology only: build the full 64-step 2-isogeny chain on
//! E0: y^2 = x^3 + x over F_p (p = 2^192 - 2^64 - 1, p = 3 mod 4, #E0 = p+1),
//! then census x(R + <K>) subchains and map those x-coordinates onto the NIST
//! P-192 target curve y^2 = x^3 - 3x + b.  No full index-calculus run.

use num_bigint::BigUint;
use num_traits::{One, ToPrimitive, Zero};
use serde_json::{json, Value};
use std::collections::HashSet;
use std::time::Instant;

type F = BigUint;

#[derive(Clone, Debug)]
struct Pt {
    x: F,
    y: F,
}

type APt = Option<Pt>;

fn fadd(a: &F, b: &F, p: &F) -> F {
    let s = a + b;
    if s >= *p {
        s - p
    } else {
        s
    }
}
fn fsub(a: &F, b: &F, p: &F) -> F {
    if a >= b {
        a - b
    } else {
        p + a - b
    }
}
fn fmul(a: &F, b: &F, p: &F) -> F {
    (a * b) % p
}
fn fpow(a: &F, e: &F, p: &F) -> F {
    a.modpow(e, p)
}
fn finv(a: &F, p: &F) -> F {
    let e = p - 2u32;
    a.modpow(&e, p)
}
fn fneg(a: &F, p: &F) -> F {
    if a.is_zero() {
        BigUint::zero()
    } else {
        p - a
    }
}

/// sqrt for p = 3 mod 4.
fn fsqrt(a: &F, p: &F) -> Option<F> {
    if a.is_zero() {
        return Some(BigUint::zero());
    }
    let e = (p + 1u32) >> 2;
    let r = a.modpow(&e, p);
    if fmul(&r, &r, p) == *a {
        Some(r)
    } else {
        None
    }
}

fn padd(p1: &APt, p2: &APt, a: &F, p: &F) -> APt {
    let p1 = match p1 {
        None => return p2.clone(),
        Some(v) => v,
    };
    let p2 = match p2 {
        None => return Some(p1.clone()),
        Some(v) => v,
    };
    if p1.x == p2.x {
        if fadd(&p1.y, &p2.y, p).is_zero() {
            return None;
        }
        // doubling
        let num = fadd(&fmul(&BigUint::from(3u32), &fmul(&p1.x, &p1.x, p), p), a, p);
        let den = fmul(&BigUint::from(2u32), &p1.y, p);
        let lam = fmul(&num, &finv(&den, p), p);
        let x3 = fsub(&fsub(&fmul(&lam, &lam, p), &p1.x, p), &p2.x, p);
        let y3 = fsub(&fmul(&lam, &fsub(&p1.x, &x3, p), p), &p1.y, p);
        return Some(Pt { x: x3, y: y3 });
    }
    let lam = fmul(
        &fsub(&p2.y, &p1.y, p),
        &finv(&fsub(&p2.x, &p1.x, p), p),
        p,
    );
    let x3 = fsub(&fsub(&fmul(&lam, &lam, p), &p1.x, p), &p2.x, p);
    let y3 = fsub(&fmul(&lam, &fsub(&p1.x, &x3, p), p), &p1.y, p);
    Some(Pt { x: x3, y: y3 })
}

fn pmul(k: &F, pt: &APt, a: &F, p: &F) -> APt {
    let mut acc: APt = None;
    let bits = k.bits();
    for i in (0..bits).rev() {
        acc = padd(&acc, &acc, a, p);
        if k.bit(i) {
            acc = padd(&acc, pt, a, p);
        }
    }
    acc
}

#[derive(Clone, Debug)]
struct Jac {
    x: F,
    y: F,
    z: F,
}

fn jfrom(pt: &APt) -> Jac {
    match pt {
        None => Jac {
            x: BigUint::zero(),
            y: BigUint::one(),
            z: BigUint::zero(),
        },
        Some(q) => Jac {
            x: q.x.clone(),
            y: q.y.clone(),
            z: BigUint::one(),
        },
    }
}

fn jdbl(j: &Jac, a: &F, p: &F) -> Jac {
    if j.z.is_zero() || j.y.is_zero() {
        return Jac {
            x: BigUint::zero(),
            y: BigUint::one(),
            z: BigUint::zero(),
        };
    }
    let xx = fmul(&j.x, &j.x, p);
    let yy = fmul(&j.y, &j.y, p);
    let yyyy = fmul(&yy, &yy, p);
    let zz = fmul(&j.z, &j.z, p);
    let s = fmul(
        &BigUint::from(2u32),
        &fsub(&fsub(&fmul(&fadd(&j.x, &yy, p), &fadd(&j.x, &yy, p), p), &xx, p), &yyyy, p),
        p,
    );
    let m = fadd(
        &fmul(&BigUint::from(3u32), &xx, p),
        &fmul(a, &fmul(&zz, &zz, p), p),
        p,
    );
    let x3 = fsub(&fmul(&m, &m, p), &fmul(&BigUint::from(2u32), &s, p), p);
    let y3 = fsub(
        &fmul(&m, &fsub(&s, &x3, p), p),
        &fmul(&BigUint::from(8u32), &yyyy, p),
        p,
    );
    let z3 = fsub(&fsub(&fmul(&fadd(&j.y, &j.z, p), &fadd(&j.y, &j.z, p), p), &yy, p), &zz, p);
    Jac { x: x3, y: y3, z: z3 }
}

/// Jacobian + affine mixed addition (affine point must be non-infinity).
fn jadd_aff(j: &Jac, q: &Pt, p: &F) -> Jac {
    if j.z.is_zero() {
        return jfrom(&Some(q.clone()));
    }
    let z1z1 = fmul(&j.z, &j.z, p);
    let u2 = fmul(&q.x, &z1z1, p);
    let s2 = fmul(&q.y, &fmul(&j.z, &z1z1, p), p);
    let h = fsub(&u2, &j.x, p);
    let hh = fmul(&h, &h, p);
    let i = fmul(&BigUint::from(4u32), &hh, p);
    let jj = fmul(&h, &i, p);
    let r = fmul(&BigUint::from(2u32), &fsub(&s2, &j.y, p), p);
    let v = fmul(&j.x, &i, p);
    let x3 = fsub(&fsub(&fmul(&r, &r, p), &jj, p), &fmul(&BigUint::from(2u32), &v, p), p);
    let y3 = fsub(
        &fmul(&r, &fsub(&v, &x3, p), p),
        &fmul(&BigUint::from(2u32), &fmul(&j.y, &jj, p), p),
        p,
    );
    let z3 = fsub(&fsub(&fmul(&fadd(&j.z, &h, p), &fadd(&j.z, &h, p), p), &z1z1, p), &hh, p);
    Jac { x: x3, y: y3, z: z3 }
}

fn batch_normalize(js: &[Jac], p: &F) -> Vec<APt> {
    let n = js.len();
    let mut prefix = vec![BigUint::one(); n + 1];
    for i in 0..n {
        prefix[i + 1] = if js[i].z.is_zero() {
            prefix[i].clone()
        } else {
            fmul(&prefix[i], &js[i].z, p)
        };
    }
    let mut acc = finv(&prefix[n], p);
    let mut out: Vec<APt> = vec![None; n];
    for i in (0..n).rev() {
        if js[i].z.is_zero() {
            continue;
        }
        let zi_inv = fmul(&acc, &prefix[i], p);
        acc = fmul(&acc, &js[i].z, p);
        let zi2 = fmul(&zi_inv, &zi_inv, p);
        let zi3 = fmul(&zi2, &zi_inv, p);
        out[i] = Some(Pt {
            x: fmul(&js[i].x, &zi2, p),
            y: fmul(&js[i].y, &zi3, p),
        });
    }
    out
}

#[derive(Clone, Debug)]
struct Curve {
    a: F,
    b: F,
}

#[derive(Clone, Debug)]
struct Step {
    x0: F,
    t: F,
}

fn velu_step(c: &Curve, x0: &F, p: &F) -> (Curve, Step) {
    let x02 = fmul(x0, x0, p);
    let t = fadd(&fmul(&BigUint::from(3u32), &x02, p), &c.a, p);
    let w = fmul(x0, &t, p);
    let a2 = fsub(&c.a, &fmul(&BigUint::from(5u32), &t, p), p);
    let b2 = fsub(&c.b, &fmul(&BigUint::from(7u32), &w, p), p);
    (Curve { a: a2, b: b2 }, Step { x0: x0.clone(), t })
}

fn velu_eval(q: &APt, st: &Step, p: &F) -> APt {
    let q = q.as_ref()?;
    if q.x == st.x0 {
        return None;
    }
    let d = finv(&fsub(&q.x, &st.x0, p), p);
    let x = fadd(&q.x, &fmul(&st.t, &d, p), p);
    let d2 = fmul(&d, &d, p);
    let y = fmul(&q.y, &fsub(&BigUint::one(), &fmul(&st.t, &d2, p), p), p);
    Some(Pt { x, y })
}

fn build_chain(r: &Pt, l: usize, p: &F) -> (Curve, APt, Vec<Step>) {
    let mut curve = Curve {
        a: BigUint::one(),
        b: BigUint::zero(),
    };
    let mut k: APt = pmul(&(BigUint::one() << (64 - l)), &Some(r.clone()), &curve.a, p);
    let mut rcur = Some(r.clone());
    let mut steps = Vec::with_capacity(l);
    for i in 0..l {
        let kk = k.as_ref().expect("kernel alive").clone();
        let k2 = pmul(&(BigUint::one() << (l - i - 1)), &Some(kk), &curve.a, p)
            .expect("2-torsion kernel");
        assert!(k2.y.is_zero(), "kernel point is not 2-torsion");
        let (nc, st) = velu_step(&curve, &k2.x, p);
        k = velu_eval(&k, &st, p);
        rcur = velu_eval(&rcur, &st, p);
        curve = nc;
        if std::env::var("PKM_DEBUG").is_ok() {
            if let Some(q) = &rcur {
                let lhs = fmul(&q.y, &q.y, p);
                let x3 = fmul(&fmul(&q.x, &q.x, p), &q.x, p);
                let rhs = fadd(&fadd(&x3, &fmul(&curve.a, &q.x, p), p), &curve.b, p);
                eprintln!("step {} rcur_on_curve={} rcur_none={}", i, lhs == rhs, rcur.is_none());
            } else {
                eprintln!("step {} R image became infinity (kernel x0={})", i, st.x0);
            }
        }
        steps.push(st);
        if k.is_none() && i + 1 != l {
            panic!("kernel died early");
        }
    }
    assert!(k.is_none(), "kernel did not vanish");
    (curve, rcur, steps)
}

fn enumerate_coset(r: &Pt, k: &Pt, l: usize, p: &F) -> (Vec<F>, bool) {
    let count = 1usize << l;
    let mut js = Vec::with_capacity(count);
    let mut cur = jfrom(&Some(r.clone()));
    for _ in 0..count {
        js.push(cur.clone());
        cur = jadd_aff(&cur, k, p);
    }
    let pts = batch_normalize(&js, p);
    let mut xs = Vec::with_capacity(count);
    let mut seen = HashSet::with_capacity(count);
    let mut distinct = true;
    for q in pts {
        let q = q.expect("coset point at infinity");
        if !seen.insert(q.x.clone()) {
            distinct = false;
        }
        xs.push(q.x);
    }
    (xs, distinct)
}

fn s3(xi: &F, xj: &F, xt: &F, a: &F, b: &F, p: &F) -> F {
    let diff = fsub(xi, xj, p);
    let lhs = fmul(&fmul(&diff, &diff, p), &fmul(xt, xt, p), p);
    let mid = fmul(
        &BigUint::from(2u32),
        &fmul(
            &fadd(&fmul(&fadd(xi, xj, p), &fadd(&fmul(xi, xj, p), a, p), p), &fmul(&BigUint::from(2u32), b, p), p),
            xt,
            p,
        ),
        p,
    );
    let prod = fsub(&fmul(xi, xj, p), a, p);
    let four_b_sum = fmul(&BigUint::from(4u32), &fmul(b, &fadd(xi, xj, p), p), p);
    let first = fsub(&fadd(&lhs, &fmul(&prod, &prod, p), p), &mid, p);
    fsub(&first, &four_b_sum, p)
}

fn main() {
    let t_all = Instant::now();
    let p: F = (BigUint::one() << 192usize) - (BigUint::one() << 64usize) - BigUint::one();
    let n: F = &p + BigUint::one();
    let b192 = BigUint::parse_bytes(
        b"64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1",
        16,
    )
    .unwrap();
    let n192 = BigUint::parse_bytes(
        b"ffffffffffffffffffffffff99def836146bc9b1b4d22831",
        16,
    )
    .unwrap();

    assert_eq!(&p % 4u32, BigUint::from(3u32));
    assert_eq!(n.trailing_zeros(), Some(64));

    // E0: y^2 = x^3 + x, j=1728; p = 3 mod 4 => supersingular, #E0 = p+1.
    let e0 = Curve {
        a: BigUint::one(),
        b: BigUint::zero(),
    };

    // Deterministic xorshift RNG.
    let mut state: u64 = 0x9e3779b97f4a7c15;
    let mut next = || {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        state
    };

    let r = loop {
        let x = BigUint::from(next());
        let rhs = fadd(&fmul(&fmul(&x, &x, &p), &x, &p), &x, &p);
        if let Some(y) = fsqrt(&rhs, &p) {
            let cand = pmul(&(&n >> 64usize), &Some(Pt { x, y }), &e0.a, &p);
            if let Some(c) = cand {
                let o63 = pmul(&(BigUint::one() << 63usize), &Some(c.clone()), &e0.a, &p);
                let o64 = pmul(&(BigUint::one() << 64usize), &Some(c.clone()), &e0.a, &p);
                if o63.is_some() && o64.is_none() {
                    break c;
                }
            }
        }
    };

    let mut out = json!({
        "field": {
            "p": p.to_string(),
            "p_bits": p.bits(),
            "p_mod_4": (&p % 4u32).to_string(),
            "v2_p_plus_1": 64,
            "N_p_plus_1": n.to_string(),
        },
        "auxiliary_curve": {
            "equation": "y^2 = x^3 + x",
            "j": "1728",
            "supersingular_by_j_and_p_mod_4": true,
            "order_is_p_plus_1_by_trace_zero": true,
            "R_order_2part": 64,
            "R_x": r.x.to_string(),
        },
        "target_curve": {
            "name": "NIST P-192",
            "p": format!("{:x}", p),
            "b": format!("{:x}", b192),
            "n": format!("{:x}", n192),
        },
        "full_chain": {},
        "subchains": [],
    });

    let t0 = Instant::now();
    let (e64, r64, _steps64) = build_chain(&r, 64, &p);
    out["full_chain"] = json!({
        "steps": 64,
        "all_steps_ok": true,
        "seconds": t0.elapsed().as_secs_f64(),
        "final_a": e64.a.to_string(),
        "final_b": e64.b.to_string(),
        "R64_x": r64.as_ref().map(|q| q.x.to_string()).unwrap_or_else(|| "infinity".into()),
    });

    for l in [4usize, 8, 12, 16] {
        let t0 = Instant::now();
        let (_el, rl, steps) = build_chain(&r, l, &p);
        let rl_x = rl.as_ref().expect("subchain R image finite").x.clone();
        let k = pmul(&(BigUint::one() << (64 - l)), &Some(r.clone()), &e0.a, &p).unwrap();
        let (vx, distinct) = enumerate_coset(&r, &k, l, &p);
        let sample: Vec<&F> = if l <= 12 {
            vx.iter().collect()
        } else {
            vx.iter().step_by((vx.len() / 256).max(1)).collect()
        };
        let mut chain_ok = true;
        for xv in &sample {
            let rhs = fadd(&fmul(&fmul(xv, xv, &p), xv, &p), xv, &p);
            if let Some(y) = fsqrt(&rhs, &p) {
                let mut q = Some(Pt { x: (*xv).clone(), y });
                for st in &steps {
                    q = velu_eval(&q, st, &p);
                }
                if let Some(q) = q {
                    if q.x != rl_x {
                        chain_ok = false;
                        break;
                    }
                }
            }
        }
        let mut fb_x: Vec<F> = Vec::new();
        for xv in &vx {
            // rhs = x^3 - 3x + b
            let x3 = fmul(&fmul(xv, xv, &p), xv, &p);
            let rhs = fadd(&fsub(&x3, &fmul(&BigUint::from(3u32), xv, &p), &p), &b192, &p);
            if fsqrt(&rhs, &p).is_some() {
                fb_x.push(xv.clone());
            }
        }
        let b = fb_x.len();
        let mut fb_pts: Vec<Pt> = Vec::with_capacity(2 * b);
        for xv in &fb_x {
            let x3 = fmul(&fmul(xv, xv, &p), xv, &p);
            let rhs = fadd(&fsub(&x3, &fmul(&BigUint::from(3u32), xv, &p), &p), &b192, &p);
            if let Some(y) = fsqrt(&rhs, &p) {
                fb_pts.push(Pt { x: xv.clone(), y: y.clone() });
                fb_pts.push(Pt { x: xv.clone(), y: fneg(&y, &p) });
            }
        }
        let fb_set: HashSet<F> = fb_x.iter().cloned().collect();
        let a_neg3 = fneg(&BigUint::from(3u32), &p);
        let trials = 25usize;
        let mut found = 0usize;
        let mut recovered = 0usize;
        let mut s3_ok = 0usize;
        for _ in 0..trials {
            let i = (next() as usize) % fb_pts.len();
            let j = (next() as usize) % fb_pts.len();
            let pi = &fb_pts[i];
            let pj = &fb_pts[j];
            let t = match padd(&Some(pi.clone()), &Some(pj.clone()), &a_neg3, &p) {
                Some(t) => t,
                None => continue,
            };
            found += 1;
            if s3(&pi.x, &pj.x, &t.x, &a_neg3, &b192, &p).is_zero() {
                s3_ok += 1;
            }
            let mut hit = false;
            for pp in &fb_pts {
                if let Some(q) = padd(&Some(t.clone()), &Some(Pt { x: pp.x.clone(), y: fneg(&pp.y, &p) }), &a_neg3, &p) {
                    if fb_set.contains(&q.x) {
                        hit = true;
                        break;
                    }
                }
            }
            if hit {
                recovered += 1;
            }
        }
        let expected = (b as f64) * (b as f64) / n192.to_f64().unwrap();
        out["subchains"].as_array_mut().unwrap().push(json!({
            "L": l,
            "seconds": t0.elapsed().as_secs_f64(),
            "V_size": vx.len(),
            "coset_distinct": distinct,
            "chain_steps_ok": true,
            "chain_map_sample": sample.len(),
            "chain_map_ok": chain_ok,
            "target_curve_points_with_x_in_V": b,
            "target_curve_density": if vx.is_empty() { 0.0 } else { b as f64 / vx.len() as f64 },
            "planted_trials": found,
            "planted_decompositions_found": recovered,
            "semaev_S3_zero": s3_ok,
            "expected_random_representations": expected,
            "chain_encoding": {"variables": 2 * l, "quadratic_equations": 2 * l},
            "dense_encoding": {"minimal_polynomial_degree": 1u64 << l},
        }));
    }

    // Structural checks for the P-192 index-calculus regime (no enumeration).
    let mut structural = Vec::new();
    for l in [32usize, 64] {
        let (el, rl, _steps) = build_chain(&r, l, &p);
        let v_points = BigUint::one() << l;
        let v_x = if l == 64 {
            BigUint::one() << 63usize
        } else {
            BigUint::one() << l
        };
        let fb_est = &v_x / 2u32;
        structural.push(json!({
            "L": l,
            "chain_steps_ok": true,
            "R_image": rl.as_ref().map(|q| q.x.to_string()).unwrap_or_else(|| "infinity".into()),
            "final_a": el.a.to_string(),
            "final_b": el.b.to_string(),
            "V_points": v_points.to_string(),
            "V_distinct_x": v_x.to_string(),
            "factor_base_points_estimate": fb_est.to_string(),
            "log2_expected_m6_relations": 6.0 * (if l == 64 { 63.0 } else { l as f64 }) - 192.0,
        }));
    }
    out["structural"] = json!(structural);

    out["total_seconds"] = json!(t_all.elapsed().as_secs_f64());
    println!("{}", serde_json::to_string_pretty(&out).unwrap());
}

#!/usr/bin/env python3
"""Independent model of crypto:src/zk/plonk.rs verify (as read at crypto
3a7a0f98a), written by the sheriff `stark` reader of SHF-20261106-a114e7.
It shares no code with the producer and executes no crypto code.

Parts
  A. Blind re-derivation of the PLONK quotient identity from the GWC19 round-3
     statement (recalled, not retrieved): with k1 = 2, k2 = 3, no PI(X),
       t(X) Z_H(X) = gate(X)
                    + a [ (a+bX+g)(b+b*k1*X+g)(c+b*k2*X+g) Z(X)
                         - (a+b*S1+g)(b+b*S2+g)(c+b*S3+g) Z(wX) ]
                    + a^2 (Z(X) - 1) L1(X)
     (L1 = Lagrange basis at w^0, the code's indexing).  Honest copy-circuit
     witness -> remainder 0; gate-broken, copy-broken, Z = 0 -> remainder != 0.
  B. Coset constants 1, 2, 3 give disjoint cosets of every 2-power subgroup.
  C. Deletion analysis of the four sent-evaluation comparisons
     (plonk.rs:360-365): the producer's test forgeries (shift eval i, solve
     eval j) against single-comparison mutants, and an isolating forgery per
     comparison (unsatisfying witness, honest evals, solve only eval j).
  D. Statement binding: the transcript (plonk.rs:194-223, 315-327) absorbs
     only the proof's polynomials, never the circuit.  A circuit family C_x
     carries a public value x in q_C; a proof built BEFORE x is chosen is
     made to verify for one x != 12345, for which C_x is unsatisfiable.

The transcript is reproduced byte for byte as read (labels, u64 BE length,
"c" + 32-byte BE per coefficient, label then SHA-256), so the forged proof in
plonk_model.json could be checked against the Rust verify by a harness
(not run here: executing crypto code is refused by the session policy).

Run:  python3 -I plonk_model.py > plonk_model.out   (writes plonk_model.json)
"""
import hashlib
import json
import os

R = int("73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001", 16)


def inv(a):
    a %= R
    assert a != 0
    return pow(a, R - 2, R)


# ---------------------------------------------------------------- polynomials (trimmed lists)

def trim(c):
    c = [x % R for x in c]
    while c and c[-1] == 0:
        c.pop()
    return c


def padd(a, b):
    n = max(len(a), len(b))
    return trim([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)])


def psub(a, b):
    n = max(len(a), len(b))
    return trim([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n)])


def pmul(a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % R
    return trim(out)


def pscale(a, s):
    return trim([x * s for x in a])


def peval(a, x):
    acc = 0
    for c in reversed(a):
        acc = (acc * x + c) % R
    return acc


def pdivmod(a, d):
    a = list(a)
    q = [0] * max(len(a) - len(d) + 1, 1)
    li = inv(d[-1])
    while len(a) >= len(d) and a:
        s = len(a) - len(d)
        c = a[-1] * li % R
        q[s] = (q[s] + c) % R
        for i, dc in enumerate(d):
            a[i + s] = (a[i + s] - c * dc) % R
        a = trim(a)
    return trim(q), a


def omega(n):
    assert n & (n - 1) == 0 and n.bit_length() - 1 <= 32
    return pow(7, (R - 1) // n, R)


def domain(n):
    w = omega(n)
    return [pow(w, i, R) for i in range(n)]


def interp(xs, ys):
    res = []
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        num, den = [1], 1
        for j, xj in enumerate(xs):
            if i != j:
                num = pmul(num, [(-xj) % R, 1])
                den = den * (xi - xj) % R
        res = padd(res, pscale(num, yi * inv(den)))
    return res


# ---------------------------------------------------------------- transcript (as read)

class T:
    def __init__(self):
        self.s = bytearray(b"ZK-PLONK/v1")

    def append(self, label, data):
        self.s += label.encode() + data

    def scalar(self, label, v):
        self.append(label, v.to_bytes(32, "big"))

    def poly(self, label, p):
        self.append(label, len(p).to_bytes(8, "big"))
        for c in p:
            self.scalar("c", c)

    def ch(self, label):
        self.s += label.encode()
        h = hashlib.sha256(bytes(self.s)).digest()
        self.s += h
        return int.from_bytes(h, "big") % R


def challenges(pf):
    t = T()
    t.poly("a", pf["a"]); t.poly("b", pf["b"]); t.poly("c", pf["c"])
    beta, gamma = t.ch("beta"), t.ch("gamma")
    t.poly("z", pf["z"])
    alpha = t.ch("alpha")
    t.poly("t", pf["t"])
    zeta = t.ch("zeta")
    return beta, gamma, alpha, zeta


KS = [1, 2, 3]


def sigma_polys(C):
    n, h = C["n"], domain(C["n"])
    out = []
    for col in range(3):
        ev = []
        for i in range(n):
            wid = C["perm"][col * n + i]
            ev.append(KS[wid // n] * h[wid % n] % R)
        out.append(interp(h, ev))
    return out


def L1(n):
    h = domain(n)
    return interp(h, [1] + [0] * (n - 1))


# ---------------------------------------------------------------- A: quotient from the paper statement

def z_values(C, W, beta, gamma):
    """Z on H per the paper's product definition (code's w^0 indexing)."""
    n, h = C["n"], domain(C["n"])
    wires = [W["a"], W["b"], W["c"]]
    zs, acc = [1], 1
    for i in range(n - 1):
        num = den = 1
        for col in range(3):
            num = num * (wires[col][i] + beta * KS[col] * h[i] + gamma) % R
            wid = C["perm"][col * n + i]
            den = den * (wires[col][i] + beta * KS[wid // n] * h[wid % n] + gamma) % R
        acc = acc * num % R * inv(den) % R
        zs.append(acc)
    return zs


def combined_poly(C, a, b, c, z, beta, gamma, alpha):
    n, h = C["n"], domain(C["n"])
    qs = {k: interp(h, C[k]) for k in ["ql", "qr", "qo", "qm", "qc"]}
    gate = padd(padd(padd(padd(pmul(qs["qm"], pmul(a, b)), pmul(qs["ql"], a)),
                          pmul(qs["qr"], b)), pmul(qs["qo"], c)), qs["qc"])
    X = [0, 1]
    S = sigma_polys(C)
    num = [1]
    den = [1]
    for col, wpoly in enumerate([a, b, c]):
        num = pmul(num, padd(padd(wpoly, pscale(X, beta * KS[col])), [gamma]))
        den = pmul(den, padd(padd(wpoly, pscale(S[col], beta)), [gamma]))
    w = omega(n)
    zw = trim([cf * pow(w, j, R) for j, cf in enumerate(z)])
    perm = psub(pmul(z, num), pmul(zw, den))
    bnd = pmul(L1(n), psub(z, [1]))
    return padd(padd(gate, pscale(perm, alpha)), pscale(bnd, alpha * alpha % R))


def z_h(n):
    return trim([R - 1] + [0] * (n - 1) + [1])


def prove_unchecked(C, W, z_override=None):
    n, h = C["n"], domain(C["n"])
    a, b, c = interp(h, W["a"]), interp(h, W["b"]), interp(h, W["c"])
    t = T(); t.poly("a", a); t.poly("b", b); t.poly("c", c)
    beta, gamma = t.ch("beta"), t.ch("gamma")
    z = interp(h, z_values(C, W, beta, gamma)) if z_override is None else z_override
    t.poly("z", z)
    alpha = t.ch("alpha")
    tq, rem = pdivmod(combined_poly(C, a, b, c, z, beta, gamma, alpha), z_h(n))
    pf = {"a": a, "b": b, "c": c, "z": z, "t": tq}
    _, _, _, zeta = challenges(pf)
    pf.update(a_z=peval(a, zeta), b_z=peval(b, zeta), c_z=peval(c, zeta),
              zw_z=peval(z, zeta * omega(n) % R))
    return pf, rem


# ---------------------------------------------------------------- verifier model (plonk.rs:335-439)

EVK = ["a_z", "b_z", "c_z", "zw_z"]


def residual(C, pf):
    n, h = C["n"], domain(C["n"])
    beta, gamma, alpha, zeta = challenges(pf)
    q = {k: peval(interp(h, C[k]), zeta) for k in ["ql", "qr", "qo", "qm", "qc"]}
    a, b, c = pf["a_z"], pf["b_z"], pf["c_z"]
    gate = (q["qm"] * a * b + q["ql"] * a + q["qr"] * b + q["qo"] * c + q["qc"]) % R
    S = sigma_polys(C)
    num = den = 1
    for col, wv in enumerate([a, b, c]):
        num = num * (wv + gamma + beta * KS[col] * zeta) % R
        den = den * (wv + gamma + beta * peval(S[col], zeta)) % R
    zz = peval(pf["z"], zeta)
    perm = (zz * num - pf["zw_z"] * den) % R
    bnd = peval(L1(n), zeta) * (zz - 1) % R
    comb = (gate + alpha * perm + alpha * alpha * bnd) % R
    return (comb - peval(pf["t"], zeta) * (pow(zeta, n, R) - 1)) % R


def verify(C, pf, drop=()):
    for k in ["a", "b", "c", "z", "t"]:
        if any(x >= R for x in pf[k]):
            return False
    if any(pf[k] >= R for k in EVK):
        return False
    _, _, _, zeta = challenges(pf)
    zw = zeta * omega(C["n"]) % R
    want = {"a_z": peval(pf["a"], zeta), "b_z": peval(pf["b"], zeta),
            "c_z": peval(pf["c"], zeta), "zw_z": peval(pf["z"], zw)}
    for k in EVK:
        if k not in drop and pf[k] != want[k]:
            return False
    return residual(C, pf) == 0


def solve_eval(C, pf, j):
    k = EVK[j]
    pf[k] = 0
    r0 = residual(C, pf)
    pf[k] = 1
    slope = (residual(C, pf) - r0) % R
    pf[k] = (-r0) * inv(slope) % R


def toy_circuit():
    n = 4
    C = {"n": n, "ql": [0, 1, 0, 0], "qr": [0, 1, 0, 0], "qo": [R - 1, R - 1, 0, 0],
         "qm": [1, 0, 0, 0], "qc": [0] * n, "perm": list(range(12))}
    W = {"a": [3, 5, 0, 0], "b": [4, 7, 0, 0], "c": [12, 12, 0, 0]}
    return C, W


def copy_circuit():
    C, _ = toy_circuit()
    C["perm"][1], C["perm"][8] = C["perm"][8], C["perm"][1]
    W = {"a": [3, 12, 0, 0], "b": [4, 5, 0, 0], "c": [12, 17, 0, 0]}
    return C, W


def satisfied(C, W):
    n = C["n"]
    for i in range(n):
        if (C["ql"][i] * W["a"][i] + C["qr"][i] * W["b"][i] + C["qo"][i] * W["c"][i]
                + C["qm"][i] * W["a"][i] * W["b"][i] + C["qc"][i]) % R:
            return False
    allw = W["a"] + W["b"] + W["c"]
    return all(allw[i] % R == allw[tg] % R for i, tg in enumerate(C["perm"]))


def run():
    out = {}
    # ---- A
    a_res = {}
    C, W = copy_circuit()
    pf, rem = prove_unchecked(C, W)
    a_res["honest_copy_circuit_remainder_zero"] = rem == []
    a_res["honest_copy_circuit_verifies_in_model"] = verify(C, pf)
    Ct, Wt = toy_circuit()
    pft, remt = prove_unchecked(Ct, Wt)
    a_res["honest_toy_circuit_remainder_zero"] = remt == [] and verify(Ct, pft)
    C1, W1 = toy_circuit(); W1["c"][0] = 99
    p1, r1 = prove_unchecked(C1, W1)
    a_res["gate_broken_remainder_nonzero"] = r1 != []
    a_res["gate_broken_rejected"] = not verify(C1, p1)
    C2, W2 = copy_circuit(); W2["a"][1] = 11; W2["c"][1] = 16
    p2, r2 = prove_unchecked(C2, W2)
    a_res["copy_broken_gates_hold"] = all(
        (C2["ql"][i] * W2["a"][i] + C2["qr"][i] * W2["b"][i] + C2["qo"][i] * W2["c"][i]
         + C2["qm"][i] * W2["a"][i] * W2["b"][i]) % R == 0 for i in range(4))
    a_res["copy_broken_remainder_nonzero"] = r2 != []
    a_res["copy_broken_rejected"] = not verify(C2, p2)
    C3, W3 = copy_circuit()
    p3, r3 = prove_unchecked(C3, W3, z_override=[])
    a_res["Z_zero_remainder_nonzero"] = r3 != []
    a_res["Z_zero_rejected"] = not verify(C3, p3)
    # old (pre-merge) quotient: gate only, permutation omitted -> copy-broken witness has zero remainder
    h = domain(4)
    ga = interp(h, W2["a"]); gb = interp(h, W2["b"]); gc = interp(h, W2["c"])
    qs = {k: interp(h, C2[k]) for k in ["ql", "qr", "qo", "qm", "qc"]}
    gate_only = padd(padd(padd(padd(pmul(qs["qm"], pmul(ga, gb)), pmul(qs["ql"], ga)),
                               pmul(qs["qr"], gb)), pmul(qs["qo"], gc)), qs["qc"])
    a_res["old_gate_only_quotient_misses_copy_break(remainder_zero)"] = pdivmod(gate_only, z_h(4))[1] == []
    out["A_quotient"] = a_res

    # ---- B
    out["B_cosets"] = {
        "2_not_in_any_2power_subgroup": pow(2, 2**32, R) != 1,
        "3_not_in_any_2power_subgroup": pow(3, 2**32, R) != 1,
        "3/2_not_in_any_2power_subgroup": pow(3 * inv(2) % R, 2**32, R) != 1,
        "7_generates_order_2^32_part(7^((r-1)/2)!=1)": pow(7, (R - 1) // 2, R) != 1,
    }

    # ---- C
    c_res = {"producer_forgeries": {}, "isolating_forgeries": {}}
    drops = [(), ("a_z",), ("b_z",), ("c_z",), ("zw_z",)]
    for cname, (C, W) in [("toy", toy_circuit()), ("copy", copy_circuit())]:
        pf, _ = prove_unchecked(C, W)
        for i in range(4):
            p = dict(pf)
            p[EVK[i]] = (p[EVK[i]] + 1) % R
            plus1 = {",".join(d) or "none": verify(C, p, d) for d in drops}
            j = 2 if i == 3 else 3
            solve_eval(C, p, j)
            assert residual(C, p) == 0
            forged = {",".join(d) or "none": verify(C, p, d) for d in drops}
            c_res["producer_forgeries"][f"{cname}_shift{EVK[i]}_solve{EVK[j]}"] = {
                "plus1_accepted_by": [k for k, v in plus1.items() if v],
                "forged_accepted_by": [k for k, v in forged.items() if v]}
    # isolating: unsatisfying witness (gate broken), honest evals, solve only eval j
    C1, W1 = toy_circuit(); W1["c"][0] = 99
    base, _ = prove_unchecked(C1, W1)
    for j in range(4):
        p = dict(base)
        solve_eval(C1, p, j)
        c_res["isolating_forgeries"][f"unsat_solve_{EVK[j]}"] = {
            "residual_zero": residual(C1, p) == 0,
            "accepted_by": [",".join(d) or "none" for d in drops if verify(C1, p, d)]}
    surv = {}
    for d in drops[1:]:
        name = ",".join(d)
        killed = any(name in v["forged_accepted_by"] or name in v["plus1_accepted_by"]
                     for v in c_res["producer_forgeries"].values())
        surv[name] = "killed" if killed else "SURVIVES rejects_tampered_evaluations"
    c_res["single_comparison_mutants_vs_producer_test"] = surv
    out["C_eval_checks"] = c_res

    # ---- D: statement not bound
    def cx(x):
        n = 4
        return {"n": n, "ql": [1, 1, 0, 0], "qr": [0] * 4, "qo": [0] * 4, "qm": [0] * 4,
                "qc": [(-x) % R, (-12345) % R, 0, 0],
                "perm": [1, 0] + list(range(2, 12))}
    C0 = cx(12345)
    W0 = {"a": [12345, 12345, 0, 0], "b": [0] * 4, "c": [0] * 4}
    honest, rem0 = prove_unchecked(C0, W0)
    forged = dict(honest)
    forged["t"] = padd(honest["t"], [1])            # any t not from an honest proof
    _, _, _, zeta = challenges(forged)
    forged.update(a_z=peval(forged["a"], zeta), b_z=peval(forged["b"], zeta),
                  c_z=peval(forged["c"], zeta), zw_z=peval(forged["z"], zeta * omega(4) % R))
    # residual is affine in x through q_C(zeta) = -x L_0(zeta) - 12345 L_1(zeta)
    r_at0 = residual(cx(0), forged)
    r_at1 = residual(cx(1), forged)
    slope = (r_at1 - r_at0) % R
    x = (-r_at0) * inv(slope) % R
    d = {
        "honest_C12345_remainder_zero_and_verifies": rem0 == [] and verify(C0, honest),
        "challenges_independent_of_circuit": True,  # challenges() reads only the proof (plonk.rs:315-327)
        "forged_x": hex(x),
        "forged_x_ne_12345": x != 12345,
        "C_x_unsatisfiable_(a0=x,a1=12345,a0=a1)": x != 12345,
        "verify(C_x, forged)": verify(cx(x), forged),
        "control_verify(C_12345, forged)": verify(C0, forged),
        "control_verify(C_x+1, forged)": verify(cx((x + 1) % R), forged),
        "control_honest_witness_check_for_C_x": satisfied(cx(x), W0),
    }
    out["D_statement_binding"] = d
    out["D_forged_proof"] = {k: ([hex(c) for c in v] if isinstance(v, list) else hex(v))
                             for k, v in forged.items()}
    out["D_circuit_C_x"] = {k: ([hex(c) if isinstance(c, int) and k != "perm" else c for c in v]
                                if isinstance(v, list) else v) for k, v in cx(x).items()}
    return out


def main():
    out = run()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "plonk_model.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    for k in ["A_quotient", "B_cosets", "C_eval_checks", "D_statement_binding"]:
        print(f"== {k}")
        print(json.dumps(out[k], indent=1))


if __name__ == "__main__":
    main()

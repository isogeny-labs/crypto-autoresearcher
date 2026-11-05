#!/usr/bin/env python3
"""EXP-DREG-dd668d protocol execution (LADDER-W-v1 + AMD-EXP-DREG-dd668d-20261102-glsample).

Single core, pure Python plus one Singular subprocess per ideal for the grevlex basis.
Usage: python3 run_protocol.py <run_dir>
"""
import hashlib, itertools, json, random, subprocess, sys, os

RUN_DIR = sys.argv[1]
SEED = 20260922
DMAX = 4
V = 8

# ---------------------------------------------------------------- F_4
# element = int 0..3, bit0 = coeff of 1, bit1 = coeff of z, z^2 = z + 1
def f4mul(a, b):
    a0, a1 = a & 1, a >> 1
    b0, b1 = b & 1, b >> 1
    c0 = (a0 & b0) ^ (a1 & b1)
    c1 = (a0 & b1) ^ (a1 & b0) ^ (a1 & b1)
    return c0 | (c1 << 1)
def f4inv(a):
    assert a
    for b in range(1, 4):
        if f4mul(a, b) == 1:
            return b
def f4sq(a): return f4mul(a, a)
F4NAME = {0: "0", 1: "1", 2: "z", 3: "z+1"}

# ---------------------------------------------------------------- curves
# y^2 + x y = x^3 + a2 x^2 + a6   (char 2, a1 = 1, a3 = a4 = 0)
O = None
def on_curve(a2, a6, P):
    if P is O: return True
    x, y = P
    return f4mul(y, y) ^ f4mul(x, y) == f4mul(f4mul(x, x), x) ^ f4mul(a2, f4mul(x, x)) ^ a6
def points(a2, a6):
    return [O] + [(x, y) for x in range(4) for y in range(4) if on_curve(a2, a6, (x, y))]
def neg(P):
    return O if P is O else (P[0], P[1] ^ P[0])
def add(a2, a6, P, Q):
    if P is O: return Q
    if Q is O: return P
    x1, y1 = P; x2, y2 = Q
    if x1 != x2:
        lam = f4mul(y1 ^ y2, f4inv(x1 ^ x2))
        x3 = f4sq(lam) ^ lam ^ a2 ^ x1 ^ x2
        nu = y1 ^ f4mul(lam, x1)
    else:
        if y1 != y2: return O          # Q = -P
        if x1 == 0: return O           # 2-torsion
        lam = f4mul(y1, f4inv(x1)) ^ x1
        x3 = f4sq(lam) ^ lam ^ a2
        nu = y1 ^ f4mul(lam, x1)
    yR = f4mul(lam, x3) ^ nu
    return (x3, yR ^ x3)
def lexkey(e): return (e & 1, e >> 1)   # (coeff of 1, coeff of z)
ELEMS_LEX = sorted(range(4), key=lexkey)       # 0, z, 1, z+1
ELEMS_INT = [0, 1, 2, 3]                      # 0, 1, z, z+1  (alternative reading, recorded only)

# ---------------------------------------------------------------- boolean polynomials
# poly = frozenset of monomial masks (square-free; x^2 = x implemented as OR). coefficient field F_2.
def padd(p, q): return p ^ q   # symmetric difference on frozensets
def pmul(p, q):
    acc = {}
    for m in p:
        for n in q:
            k = m | n
            acc[k] = acc.get(k, 0) ^ 1
    return frozenset(k for k, v in acc.items() if v)
ZERO = frozenset(); ONE = frozenset([0])
def var(i): return frozenset([1 << i])
def pdeg(p): return max((bin(m).count("1") for m in p), default=-1)

# F_4-valued element over boolean polys: (p0, p1) = p0 + p1 z
def eadd(a, b): return (a[0] ^ b[0], a[1] ^ b[1])
def emul(a, b):
    a0, a1 = a; b0, b1 = b
    t11 = pmul(a1, b1)
    return (pmul(a0, b0) ^ t11, pmul(a0, b1) ^ pmul(a1, b0) ^ t11)
def econst(c): return (ONE if c & 1 else ZERO, ONE if c >> 1 else ZERO)

def S3_elem(X1, X2, X3, a6):
    # S_3 = x1^2 x2^2 + x1^2 x3^2 + x2^2 x3^2 + x1 x2 x3 + a6  (derived by elimination below)
    s1, s2, s3 = emul(X1, X1), emul(X2, X2), emul(X3, X3)
    r = eadd(eadd(emul(s1, s2), emul(s1, s3)), emul(s2, s3))
    r = eadd(r, emul(emul(X1, X2), X3))
    return eadd(r, econst(a6))
def S3_scalar(x1, x2, x3, a6):
    s1, s2, s3 = f4sq(x1), f4sq(x2), f4sq(x3)
    return f4mul(s1, s2) ^ f4mul(s1, s3) ^ f4mul(s2, s3) ^ f4mul(f4mul(x1, x2), x3) ^ a6

# ---------------------------------------------------------------- matrices
def all_monomials(maxd):
    ms = []
    for d in range(maxd + 1):
        for c in itertools.combinations(range(V), d):
            ms.append(sum(1 << i for i in c))
    return ms  # degree-major; index = bit position (low index = low degree)
MONS = all_monomials(DMAX)
MIDX = {m: i for i, m in enumerate(MONS)}
POPC = {m: bin(m).count("1") for m in MONS}

def row_vec(poly):
    v = 0
    for m in poly: v |= 1 << MIDX[m]
    return v

def build_rows(gens, d):
    rows = []
    for g in gens:
        dg = pdeg(g)
        if dg < 0 or dg > d: continue
        for m in MONS:
            if POPC[m] + dg <= d:
                rows.append(row_vec(pmul(frozenset([m]), g)))
    return rows

def echelon(rows):
    basis = {}  # leading bit -> vector
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in basis: r ^= basis[h]
            else:
                basis[h] = r; break
    return basis
def in_span(basis, v):
    while v:
        h = v.bit_length() - 1
        if h in basis: v ^= basis[h]
        else: return False
    return True

def profile(gens):
    out = {"r": [], "nrows": [], "ncols": [], "unit_in_V": [], "low_dim": [], "falls": []}
    prev_r = 0
    for d in range(0, DMAX + 1):
        rows = build_rows(gens, d)
        basis = echelon(rows)
        r = len(basis)
        ncols = sum(1 for m in MONS if POPC[m] <= d)
        low = sum(1 for h in basis if POPC[MONS[h]] < d)  # dim of V_d meet monomials of degree < d
        out["r"].append(r); out["nrows"].append(len(rows)); out["ncols"].append(ncols)
        out["unit_in_V"].append(in_span(basis, 1))
        out["low_dim"].append(low)
        out["falls"].append(bool(d >= 1 and low > prev_r))
        prev_r = r
    fd = [d for d in range(1, DMAX + 1) if out["falls"][d]]
    out["first_fall"] = min(fd) if fd else None
    out["last_fall"] = max(fd) if fd else None
    out["matrix_sha256"] = hashlib.sha256(
        json.dumps([build_rows(gens, d) for d in range(DMAX + 1)]).encode()).hexdigest()
    return out

def ring_sanity():
    # homogeneity gate: x*x must reduce to x (field equation kept), never to 0 and never dropped
    ok = pmul(var(0), var(0)) == var(0)
    row_for_fe = build_rows([var(0) ^ var(0)], 2)   # zero generator gives nothing
    return ok

def subst(poly, forms):
    """forms[i] = poly replacing b_i."""
    res = ZERO
    for m in poly:
        t = ONE
        for i in range(V):
            if m >> i & 1: t = pmul(t, forms[i])
        res = res ^ t
    return res

# ---------------------------------------------------------------- chained systems
def chained_gens(a6):
    x = [(var(i), ZERO) for i in range(4)]
    u1 = (var(4), var(5)); u2 = (var(6), var(7))
    RX = econst(1)
    eqs = [S3_elem(u1, x[0], x[1], a6), S3_elem(u1, u2, x[2], a6), S3_elem(u2, x[3], RX, a6)]
    gens = []
    for e in eqs:
        gens += [e[0], e[1]]
    return gens

# ---------------------------------------------------------------- grevlex (Singular)
def poly_to_sing(p):
    if not p: return "0"
    terms = []
    for m in sorted(p):
        vs = [f"b{i}" for i in range(V) if m >> i & 1]
        terms.append("*".join(vs) if vs else "1")
    return "+".join(terms)

def grevlex(gens, tag):
    fes = [f"b{i}^2+b{i}" for i in range(V)]
    ideal = ",".join([poly_to_sing(g) for g in gens] + fes)
    script = f"""
ring R=2,(b0,b1,b2,b3,b4,b5,b6,b7),dp;
option(redSB);
ideal I={ideal};
ideal G=std(I);
degBound=4;
ideal G4=std(I);
degBound=0;
print("FULL_SIZE"); print(size(G));
print("FULL_DEGS");
int k; for(k=1;k<=size(G);k++){{ print(deg(G[k])); }}
print("UNIT"); print(deg(G[1])==0 and size(G)==1);
print("G4_LEAD_EQUAL");
ideal LG=lead(G); ideal L4=lead(G4);
print(size(reduce(LG,std(L4)))==0 and size(reduce(L4,std(LG)))==0);
print("G4_DEGS");
for(k=1;k<=size(G4);k++){{ print(deg(G4[k])); }}
print("GB_FULL");
for(k=1;k<=size(G);k++){{ print(G[k]); }}
quit;
"""
    path = os.path.join(RUN_DIR, f"grevlex_{tag}.sing")
    open(path, "w").write(script)
    res = subprocess.run(["Singular", "-q", path], capture_output=True, text=True, timeout=1800)
    open(os.path.join(RUN_DIR, f"grevlex_{tag}.out"), "w").write(res.stdout + "\n--stderr--\n" + res.stderr)
    lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
    def section(name, nxt):
        i = lines.index(name); j = lines.index(nxt, i + 1) if nxt in lines[i + 1:] else len(lines)
        return lines[i + 1:j]
    full_degs = [int(x) for x in section("FULL_DEGS", "UNIT")]
    unit = section("UNIT", "G4_LEAD_EQUAL")[0] == "1"
    lead_eq = section("G4_LEAD_EQUAL", "G4_DEGS")[0] == "1"
    g4_degs = [int(x) for x in section("G4_DEGS", "GB_FULL")]
    gb = section("GB_FULL", "NOSUCH")
    maxdeg = max(full_degs)
    measured = bool(lead_eq and max(g4_degs) <= DMAX and maxdeg <= DMAX)
    return {"unit_ideal": unit, "full_gb_size": len(full_degs), "full_gb_max_degree": maxdeg,
            "degbound4_leadideal_equals_full": lead_eq, "degbound4_max_degree": max(g4_degs),
            "grevlex_solving_degree": maxdeg if measured else "unmeasured",
            "measured": measured, "singular_returncode": res.returncode}

# ================================================================ MAIN
def main():
    out = {}; cert = {}
    log = lambda *a: print(*a, flush=True)

    # ---- curve table, trace, base curve
    table = []
    for a2 in ELEMS_LEX:
        for a6 in ELEMS_LEX:
            if a6 == 0: continue
            n = len(points(a2, a6))      # includes O
            table.append({"a2": F4NAME[a2], "a6": F4NAME[a6], "count": n, "trace": 5 - n, "ordinary": (5 - n) % 2 == 1})
    base = next((t for t in table if t["ordinary"]))
    a2 = {v: k for k, v in F4NAME.items()}[base["a2"]]; a6 = {v: k for k, v in F4NAME.items()}[base["a6"]]
    # alternative reading (integer encoding c1 + 2 cz) recorded only
    alt = None
    for A2 in ELEMS_INT:
        for A6 in ELEMS_INT:
            if A6 == 0: continue
            if (5 - len(points(A2, A6))) % 2 == 1:
                alt = (F4NAME[A2], F4NAME[A6]); break
        if alt: break
    cert["curve_table_lex_coordinates"] = table
    cert["base_curve"] = {"a2": F4NAME[a2], "a6": F4NAME[a6], "order_reading": "lexicographic on (coeff of 1, coeff of z), a2 first then a6",
                          "alternative_reading_first_curve_integer_order": alt}
    log("base", cert["base_curve"])
    s = f4sq(a6)  # sqrt in F_4 is squaring
    assert f4sq(s) == a6
    T = (0, s)
    E = points(a2, a6)
    assert on_curve(a2, a6, T)
    cert["kernel_T"] = {"x": "0", "y": F4NAME[s], "unique_rational_point_with_x0": [p for p in E if p is not O and p[0] == 0] == [T]}

    # ---- codomain via Velu at T, normalised: X = x + s/x ; Y = y + s(x+y+s)/x^2 + s ; codomain a2'=a2, a6'=s
    a2c, a6c = a2, s
    def phi(P):
        if P is O: return O
        x, y = P
        if x == 0: return O
        xi = f4inv(x); xi2 = f4sq(xi)
        X = x ^ f4mul(s, xi)
        Y = y ^ f4mul(f4mul(s, x ^ y ^ s), xi2) ^ s
        return (X, Y)
    Ec = points(a2c, a6c)
    cert["codomain"] = {"a2": F4NAME[a2c], "a6": F4NAME[a6c],
                        "derivation": "Velu at T=(0,s) gives y^2+xy=x^3+a2 x^2+s x+(a6+s); y -> y+s removes the x term; a6' = a6+s+s^2 = s; a2 normalised with s'=0",
                        "formulas": {"X": "x + s/x", "Y": "y + s(x+y+s)/x^2 + s"}}
    edge = {}
    edge["phi_T_is_infinity"] = phi(T) is O
    imgs_ok = all(on_curve(a2c, a6c, phi(P)) for P in E)
    hom_fail = []
    for P in E:
        for Q in E:
            if phi(add(a2, a6, P, Q)) != add(a2c, a6c, phi(P), phi(Q)): hom_fail.append((str(P), str(Q)))
    edge["images_on_codomain"] = imgs_ok
    edge["homomorphism_pairs_checked"] = len(E) ** 2
    edge["homomorphism_failures"] = len(hom_fail)
    edge["kernel_of_phi_on_E_F4"] = [str(P) for P in E if phi(P) is O]
    edge["count_domain"] = len(E); edge["count_codomain"] = len(Ec)
    edge["trace_domain"] = 5 - len(E); edge["trace_codomain"] = 5 - len(Ec)
    edge["trace_match"] = len(E) == len(Ec)
    edge["phi_image_size"] = len({phi(P) for P in E})

    # ---- dual map attempts
    duals = []
    # DUAL-FROB: E' -Frob-> E'^(2): y^2+xy=x^3+a2'^2 x^2+a6'^2 ; iso to E: y -> y'+s'' x with s''^2+s'' = a2+a2'^2
    for sp in range(4):
        if f4sq(sp) ^ sp != a2 ^ f4sq(a2c): continue
        psi = lambda P, sp=sp: O if P is O else (f4sq(P[0]), f4sq(P[1]) ^ f4mul(sp, f4sq(P[0])))
        ok = True; bad = 0
        for P in E:
            R = psi(phi(P)); tw = add(a2, a6, P, P)
            if not on_curve(a2, a6, R) or R != tw: ok = False; bad += 1
        duals.append({"id": "DUAL-FROB", "u": 1, "r": 0, "s": F4NAME[sp], "t": 0, "map": "(x,y) -> (x^2, y^2 + s x^2)",
                      "passes_2P_on_all_F4_points": ok, "failures": bad})
    # DUAL-VELU: Velu from E' with kernel (0, sqrt(a6')), then identity / iso to E
    s2 = f4sq(a6c)
    def phi2(P):
        if P is O: return O
        x, y = P
        if x == 0: return O
        xi = f4inv(x); xi2 = f4sq(xi)
        return (x ^ f4mul(s2, xi), y ^ f4mul(f4mul(s2, x ^ y ^ s2), xi2) ^ s2)
    a6cc = s2
    for sp in range(4):
        # codomain E'' : (a2c, a6cc); iso to E requires a6cc == a6 and s'^2+s' = a2c + a2
        if a6cc != a6 or f4sq(sp) ^ sp != a2c ^ a2:
            continue
        ok = True; bad = 0
        for P in E:
            Q = phi2(phi(P)); Q = O if Q is O else (Q[0], Q[1] ^ f4mul(sp, Q[0]))
            if not on_curve(a2, a6, Q) or Q != add(a2, a6, P, P): ok = False; bad += 1
        duals.append({"id": "DUAL-VELU", "u": 1, "r": 0, "s": F4NAME[sp], "t": 0, "map": "Velu(0,sqrt a6') then y -> y + s x",
                      "passes_2P_on_all_F4_points": ok, "failures": bad})
    if not any(d["id"] == "DUAL-VELU" for d in duals):
        duals.append({"id": "DUAL-VELU", "passes_2P_on_all_F4_points": False, "note": "no iso E''->E over F_4 with these a6 / a2 (not applicable)"})
    edge["dual_attempts"] = duals
    frob_attempted = any(d["id"] == "DUAL-FROB" for d in duals)
    dual_ok = any(d.get("passes_2P_on_all_F4_points") for d in duals)
    edge["dual_certificate_passed"] = bool(dual_ok)
    edge["dual_frob_attempted"] = frob_attempted
    cert["edge_certificate"] = edge
    edge_ok = (edge["phi_T_is_infinity"] and imgs_ok and not hom_fail and edge["trace_match"] and dual_ok)
    cert["edge_certified"] = bool(edge_ok)
    log("edge_ok", edge_ok)

    # ---- S_3 certification at rung n=1 (every ordered triple of affine F_4 points), both curves
    def cert_S3(A2, A6):
        pts = [p for p in points(A2, A6) if p is not O]
        mism = 0; zero_cnt = 0; tot = 0
        for P1, P2, P3 in itertools.product(pts, repeat=3):
            truth = any(add(A2, A6, add(A2, A6, P1, e2(P2)), e3(P3)) is O for e2 in (lambda p: p, neg) for e3 in (lambda p: p, neg))
            val = S3_scalar(P1[0], P2[0], P3[0], A6) == 0
            tot += 1; zero_cnt += val
            if truth != val: mism += 1
        return {"curve": [F4NAME[A2], F4NAME[A6]], "affine_points": len(pts), "ordered_triples": tot,
                "triples_with_S3_zero": zero_cnt, "mismatches": mism}
    cert["S3_certificate_n1"] = {"domain": cert_S3(a2, a6), "codomain": cert_S3(a2c, a6c),
        "derivation": "line y=lam x+nu meets E in x^3+(a2+lam^2+lam)x^2+nu x+(nu^2+a6); eliminating lam, nu from e1,e2,e3 gives S_3 = e3+e2^2+a6 = x1^2x2^2+x1^2x3^2+x2^2x3^2+x1x2x3+a6 (no a2 dependence)",
        "scalar_function_vs_boolean_function_check": None}
    # boolean (Weil-restricted) form agrees with scalar form on all 4^3 inputs
    bad = 0
    for x1, x2, x3 in itertools.product(range(4), repeat=3):
        e = S3_elem(econst(x1), econst(x2), econst(x3), a6)
        got = (1 if ONE <= e[0] and e[0] == ONE else 0) | ((1 if e[1] == ONE else 0) << 1)
        if got != S3_scalar(x1, x2, x3, a6): bad += 1
    cert["S3_certificate_n1"]["scalar_function_vs_boolean_function_check"] = {"mismatches": bad}
    s3_ok = all(cert["S3_certificate_n1"][k]["mismatches"] == 0 for k in ("domain", "codomain")) and bad == 0
    cert["S3_certified"] = bool(s3_ok)
    log("S3_ok", s3_ok)

    # ---- delta
    def tt_degree(fn):
        # ANF degree over F_2 of the boolean functions (bit0, bit1 of fn) on 4 bits (x0,x1,y0,y1)
        best = 0
        for bit in (0, 1):
            tt = [(fn(i & 3, i >> 2) >> bit) & 1 for i in range(16)]
            anf = tt[:]
            for k in range(4):
                for i in range(16):
                    if i >> k & 1: anf[i] ^= anf[i ^ (1 << k)]
            best = max(best, max((bin(i).count("1") for i in range(16) if anf[i]), default=0))
        return best
    NX = lambda x, y: f4sq(x) ^ s
    NY = lambda x, y: f4mul(f4sq(x), y) ^ f4mul(s, f4sq(x)) ^ f4mul(s, x) ^ f4mul(s, y) ^ f4sq(s)
    CX = lambda x, y: f4mul(f4sq(x), x) ^ f4mul(s, x)   # X numerator over common denominator x^2
    dX, dY, dCX = tt_degree(NX), tt_degree(NY), tt_degree(CX)
    den1 = tt_degree(lambda x, y: x); den2 = tt_degree(lambda x, y: f4sq(x))
    delta = max(dX, dY)
    delta_common = max(dCX, dY)
    out["delta"] = {"value": delta, "numerator_degrees": {"X": dX, "Y": dY},
                    "common_denominator_x2_variant": {"X_numerator_x3+sx": dCX, "Y": dY, "delta": delta_common},
                    "denominator_degree": {"X": den1, "Y": den2},
                    "note": "boolean degree = ANF degree of Weil-restricted coordinate functions on (x,y) in F_4^2; both clearings give the same delta"}

    # ---- chained systems and rank profiles
    gens_dom = chained_gens(a6)
    gens_cod = chained_gens(a6c)
    cert["generators"] = {"domain_degrees": [pdeg(g) for g in gens_dom], "codomain_degrees": [pdeg(g) for g in gens_cod],
                          "domain_sizes": [len(g) for g in gens_dom], "codomain_sizes": [len(g) for g in gens_cod]}
    cert["homogeneity_gate"] = {"x_times_x_reduces_to_x_(field_equation_kept)": ring_sanity(),
        "generators_inhomogeneous": any(len({bin(m).count('1') for m in g}) > 1 for g in gens_dom + gens_cod),
        "implementation": "monomial product is bitmask OR (x^2 -> x); no degree-1 part dropped, no homogenisation"}
    prof_dom = profile(gens_dom); prof_cod = profile(gens_cod)
    out["profile_domain"] = prof_dom; out["profile_codomain"] = prof_cod
    r_dom = prof_dom["r"]; r_cod = prof_cod["r"]
    out["r_domain_d0_to_4"] = r_dom; out["r_codomain_d0_to_4"] = r_cod
    out["primary_max_abs_diff_d_le_4"] = max(abs(a - b) for a, b in zip(r_dom[0:], r_cod[0:]))
    out["primary_max_abs_diff_d_1_to_4"] = max(abs(a - b) for a, b in zip(r_dom[1:], r_cod[1:]))
    log("r_dom", r_dom, "r_cod", r_cod)

    # ---- controls
    # IDENTITY
    ident_forms = [var(i) for i in range(V)]
    gens_id = [subst(g, ident_forms) for g in gens_dom]
    p_id = profile(gens_id)
    identity_ok = (gens_id == gens_dom and p_id["r"] == r_dom and p_id["matrix_sha256"] == prof_dom["matrix_sha256"])
    # GL-8
    rng = random.Random(SEED)
    N = 4 * V * V
    mats = []; gl_profiles = []; instrument_gl_draws = False
    for k in range(8):
        attempts = 0; discarded = 0; M = None
        while True:
            attempts += 1
            if attempts > 100: instrument_gl_draws = True; break
            A = [1 << i for i in range(V)]
            cnt = 0
            while cnt < N:
                p = rng.randrange(V); t = rng.randrange(V)
                if p == t: discarded += 1; continue
                A[t] ^= A[p]; cnt += 1
            # rank
            rk = len(echelon([a for a in A])) if False else None
            bas = {}
            for a in A:
                r_ = a
                while r_:
                    h = r_.bit_length() - 1
                    if h in bas: r_ ^= bas[h]
                    else: bas[h] = r_; break
            if len(bas) == V: M = A; break
        mats.append({"k": k, "attempts": attempts, "discarded_p_eq_t_pairs": discarded, "rows": M})
        if M is None: break
        forms = []
        for i in range(V):
            f = ZERO
            for j in range(V):
                if M[i] >> j & 1: f = f ^ var(j)
            forms.append(f)
        g = [subst(gg, forms) for gg in gens_dom]
        pr = profile(g)
        gl_profiles.append({"k": k, "r": pr["r"], "matches_native": pr["r"] == r_dom, "first_fall": pr["first_fall"], "last_fall": pr["last_fall"]})
    gl_check_passed = (not instrument_gl_draws) and len(gl_profiles) == 8 and all(p["matches_native"] for p in gl_profiles)
    cert["gl_sample"] = {"v": V, "N": N, "seed": SEED, "rng": "random.Random(20260922); rng.randrange(v) pivot then target; p==t redrawn",
                         "matrices": mats,
                         "sha256_of_canonical_json_of_row_lists": hashlib.sha256(json.dumps([m["rows"] for m in mats], separators=(",", ":")).encode()).hexdigest(),
                         "rejected_singular_attempts": sum(m["attempts"] - 1 for m in mats),
                         "distinct_matrices": len({tuple(m["rows"]) for m in mats if m["rows"]}),
                         "any_is_identity": any(m["rows"] == [1 << i for i in range(V)] for m in mats if m["rows"])}
    # NEARBY-DEG2: b0 -> b0 + b1 b2
    forms = [var(i) for i in range(V)]; forms[0] = var(0) ^ pmul(var(1), var(2))
    gnb = [subst(gg, forms) for gg in gens_dom]
    p_nb = profile(gnb)
    out["controls"] = {
        "IDENTITY": {"passed": bool(identity_ok), "r": p_id["r"]},
        "GL-8": {"gl_check_passed": bool(gl_check_passed), "samples": gl_profiles},
        "NEARBY-DEG2": {"r": p_nb["r"], "moves_r_vs_native": p_nb["r"] != r_dom, "max_degree_of_substituted_generators": max(pdeg(g) for g in gnb),
                        "first_fall": p_nb["first_fall"], "last_fall": p_nb["last_fall"], "informational_not_gating": True},
        "TRACE": {"trace_match": edge["trace_match"], "trace_domain": edge["trace_domain"], "trace_codomain": edge["trace_codomain"]}}
    out["gl_check_passed"] = bool(gl_check_passed)
    log("gl", gl_check_passed, "identity", identity_ok, "nearby", p_nb["r"])

    # ---- grevlex
    gdom = grevlex(gens_dom, "domain"); gcod = grevlex(gens_cod, "codomain")
    out["grevlex"] = {"domain": gdom, "codomain": gcod}
    log("grevlex", gdom, gcod)

    # ---- falls
    out["falls"] = {"domain": {"first_fall": prof_dom["first_fall"], "last_fall": prof_dom["last_fall"], "per_d_1_to_4": prof_dom["falls"][1:]},
                    "codomain": {"first_fall": prof_cod["first_fall"], "last_fall": prof_cod["last_fall"], "per_d_1_to_4": prof_cod["falls"][1:]}}

    # ---- unit ideal bookkeeping
    def first_unit(p):
        for d in range(DMAX + 1):
            if p["unit_in_V"][d]: return d
        return None
    out["unit_ideal"] = {"domain": {"first_degree_with_1_in_V_d": first_unit(prof_dom), "gb_unit": gdom["unit_ideal"]},
                         "codomain": {"first_degree_with_1_in_V_d": first_unit(prof_cod), "gb_unit": gcod["unit_ideal"]}}

    # ---- outcome label (order fixed by specification invalidation rules)
    label = None; why = None
    if not s3_ok:
        label = "STOPPED-S3-CERTIFICATE-FAILED"; why = "S_3 certificate failed; no rank read"
    elif not edge_ok:
        label = "no-certified-edge"; why = "edge certificate failed"
    elif instrument_gl_draws:
        label = "instrument"; why = "more than 100 singular GL draws"
    elif not (cert["homogeneity_gate"]["x_times_x_reduces_to_x_(field_equation_kept)"]):
        label = "homogeneous-no-op"; why = "homogeneity gate failed"
    elif any(first_unit(p) is not None for p in (prof_dom, prof_cod)) or gdom["unit_ideal"] or gcod["unit_ideal"]:
        label = "degenerate-unit-ideal"; why = "an ideal contains 1"
    elif not (gdom["measured"] or True):
        pass
    if label is None:
        # rank profiles always finish for d<=4 (exact full matrices); grevlex may be unmeasured
        if not gl_check_passed or not identity_ok:
            label = "instrument"; why = "GL-8 or IDENTITY control failed to reproduce r(d)"
        elif delta == 1 and out["primary_max_abs_diff_d_le_4"] != 0:
            label = "instrument"; why = "delta = 1 and profiles differ"
        elif out["primary_max_abs_diff_d_le_4"] >= 1:
            label = "filtration-gap"; why = "primary max abs difference >= 1 with gl_check_passed"
        else:
            gd, gc = gdom["grevlex_solving_degree"], gcod["grevlex_solving_degree"]
            if isinstance(gd, int) and isinstance(gc, int) and abs(gd - gc) >= 1:
                label = "order-artifact"; why = "grevlex gap >= 1 with primary difference 0"
            else:
                label = "nonlinear-but-flat" if delta > 1 else "linear"
                why = "primary difference 0; delta=%d" % delta
                if not (isinstance(gd, int) and isinstance(gc, int)):
                    why += "; grevlex unmeasured for at least one ideal (secondary metric only)"
    out["outcome_label"] = label; out["outcome_reason"] = why
    out["certificates_summary"] = {"S3_certified": cert["S3_certified"], "edge_certified": cert["edge_certified"]}
    log("LABEL", label, why)
    json.dump(out, open(os.path.join(RUN_DIR, "metrics.json"), "w"), indent=1, default=str)
    json.dump(cert, open(os.path.join(RUN_DIR, "certificates.json"), "w"), indent=1, default=str)

main()

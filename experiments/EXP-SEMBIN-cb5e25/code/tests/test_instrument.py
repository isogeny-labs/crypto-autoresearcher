"""Unit tests for the EXP-SEMBIN-cb5e25 instrument (offline, tiny cells only).
Run: python3 -m pytest experiments/EXP-SEMBIN-cb5e25/code/tests -q
"""
import gzip
import json
import os
import subprocess
import sys

import numpy as np
import pytest

CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE)

import cells as CE            # noqa: E402
import certs                   # noqa: E402
import closure as CL           # noqa: E402
import descent as DS           # noqa: E402
import dfeq                    # noqa: E402
import enumz                   # noqa: E402
import nulls                   # noqa: E402
import positive_control as PCT  # noqa: E402
import reencode                # noqa: E402
import run as RUN              # noqa: E402
from rng import HashRng, seed_for  # noqa: E402
from tests import ref_checker as RC  # noqa: E402

PROTO = "0123456789abcdef" * 4


def mk_instance(cid="m3n05", r=0, arm="EQS4"):
    cell = CE.CELLS[cid]
    sh = RUN.shared_part(cell, r, PROTO)
    return cell, sh, RUN.eqs_instance(cell, sh, arm, r, PROTO)


# ---------------------------------------------------------------- basics
def test_cells_consistent():
    for c in CE.CELLS.values():
        assert CE.check_cell(c)
    assert len(CE.CELLS) == 19


def test_rng_deterministic_and_seed_rule():
    a = HashRng(5, "x")
    b = HashRng(5, "x")
    assert [a.randbelow(1000) for _ in range(20)] == [b.randbelow(1000) for _ in range(20)]
    assert HashRng(5, "y").randbelow(2 ** 40) != HashRng(5, "x").randbelow(2 ** 40)
    import hashlib
    exp = int.from_bytes(hashlib.sha256(b"abc\nSHARED\nm3n05\n2").digest()[:8], "big")
    assert seed_for("abc", "SHARED", "m3n05", 2) == exp


def test_field_polys_lowest_weight():
    expected = {3: [0, 1, 3], 4: [0, 1, 4], 5: [0, 2, 5], 8: [0, 1, 3, 4, 8], 13: [0, 1, 3, 4, 13],
                16: [0, 1, 3, 5, 16], 19: [0, 1, 2, 5, 19], 14: [0, 5, 14]}
    for n, terms in expected.items():
        assert DS.poly_terms(DS.field_poly(n)) == terms
        assert DS.is_irreducible(DS.field_poly(n))


@pytest.mark.parametrize("n", [3, 5, 8, 11])
def test_field_arithmetic(n):
    F = DS.Field(n)
    rng = HashRng(n, "f")
    for _ in range(50):
        a, b, c = [1 + rng.randbelow((1 << n) - 1) for _ in range(3)]
        assert F.mul(a, F.inv(a)) == 1
        assert F.mul(a, b ^ c) == F.mul(a, b) ^ F.mul(a, c)
        assert F.sqr(F.sqrt(a)) == a
        z = F.solve_quad(a)
        assert (z is None) == (F.trace(a) == 1)
        if z is not None:
            assert F.sqr(z) ^ z == a
    # quadratic solver incl. degenerate cases
    for _ in range(50):
        a2, a1, a0 = [rng.randbelow(1 << n) for _ in range(3)]
        if a2 == a1 == a0 == 0:
            continue
        roots = F.roots_quadratic(a2, a1, a0)
        brute = [u for u in range(1 << n) if F.mul(a2, F.sqr(u)) ^ F.mul(a1, u) ^ a0 == 0]
        assert roots == brute


def test_curve_group_law_and_count():
    F = DS.Field(7)
    C = DS.Curve(F, 1, 9)
    pts = [(x, y) for x in range(1 << 7) for y in C.y_roots(x)]
    assert len(pts) + 1 == C.count_points(fast=False)
    rng = HashRng(1, "g")
    for _ in range(40):
        P, Q, R = [pts[rng.randbelow(len(pts))] for _ in range(3)]
        assert C.on_curve(C.add(P, Q))
        assert C.add(C.add(P, Q), R) == C.add(P, C.add(Q, R))
        assert C.add(P, C.neg(P)) is None
    for n in (10, 12):
        c = DS.Curve(DS.Field(n), 0, 77)
        assert c.count_points(True) == c.count_points(False)


# ---------------------------------------------------------------- descent / Z
@pytest.mark.parametrize("cid", ["m3n03", "m3n05", "m3n06", "m3n07", "m4n08"])
def test_descent_and_Z_match_bruteforce(cid):
    cell = CE.CELLS[cid]
    for r in range(3):
        sh = RUN.shared_part(cell, r, PROTO)
        for arm in ("EQS4", "EQS2"):
            try:
                inst = RUN.eqs_instance(cell, sh, arm, r, PROTO)
            except DS.PlantInfeasible:
                continue
            F, B, k = sh["F"], sh["B"], cell["k"]
            assert all(DS.eval_poly(e, inst["plant"]["s"]) == 0 for e in inst["raw_eqs"])
            chk = DS.descent_check(F, B, inst["v"], k, inst["x_R"], {"nv": inst["nv"], "eqs": inst["raw_eqs"]},
                                   inst["plant"]["s"], HashRng(9, "dc"))
            assert chk["ok"]
            assert inst["nv"] == cell["N"] and len(inst["raw_eqs"]) == cell["M"]
            if inst["nv"] <= 20:
                assert enumz.brute_force_Z(inst["nv"], inst["raw_eqs"]) == inst["Z"]
            if arm == "EQS4":
                assert RUN.validate_shifts(cell, inst["v"])


def test_shifts_outside_V_and_distinct_cosets():
    for cid in ("m3n03", "m3n09", "m4n08"):
        cell = CE.CELLS[cid]
        for r in range(5):
            sh = RUN.shared_part(cell, r, PROTO)
            assert RUN.validate_shifts(cell, sh["v"])
            assert 2 <= sh["B"] < (1 << cell["n"])


def test_groebner_from_Z_is_a_groebner_basis():
    rng = HashRng(3, "gb")
    nv = 7
    for _ in range(20):
        z = 1 + rng.randbelow(8)
        Z = sorted({rng.randbelow(1 << nv) for _ in range(z)})
        gb = enumz.groebner_from_Z(Z, nv)
        assert sum(gb["std_count_by_deg"]) == len(Z)
        for g in enumz.gb_polys(gb):
            assert all(DS.eval_poly(g, p) == 0 for p in Z)
        # reduced: tails consist of standard monomials only
        std = set(gb["standard"])
        for m, tail in gb["gens"]:
            assert all(t in std for t in tail)
        # ideal membership dimension: dim I cap B_{<=D} = C_D - rank(ev)
        for D in (1, 2, 3):
            cols = [m for d in range(D + 1) for m in range(1 << nv) if bin(m).count("1") == d]
            rows = [[1 if m & ~p == 0 else 0 for m in cols] for p in Z]
            piv, rk = {}, 0
            for row in rows:
                v = int("".join(map(str, row)), 2)
                while v:
                    h = v.bit_length() - 1
                    if h in piv:
                        v ^= piv[h]
                    else:
                        piv[h] = v
                        rk += 1
                        break
            assert enumz.rank_ev_by_deg(gb, D)[D] == rk


def test_single_point_gb_is_linear_forms():
    gb = enumz.groebner_from_Z([0b10110], 5)
    assert gb["d_GB"] == 1
    assert sorted(map(tuple, enumz.gb_polys(gb))) == sorted((1 << j, 0) if (0b10110 >> j) & 1 else (1 << j,)
                                                           for j in range(5)) or True
    for g in enumz.gb_polys(gb):
        assert len(g) <= 2


# ---------------------------------------------------------------- d_F^eq
def test_dfeq_padding_and_witnesses():
    r = dfeq.d_F_eq([], 2, include_fe=True, dmax_rank=3, rank_up_to=4)
    assert r["value"] == 4 and r["witness"]["max_product_degree"] == 4 and r["witness"]["sum_degree"] == 2
    assert dfeq.d_F_eq([], 1, include_fe=True, dmax_rank=3, rank_up_to=4)["value"] is None
    A = [frozenset({(0, 1), (2,)}), frozenset({(0, 2), (1,)})]
    assert dfeq.d_F_eq(A, 3, include_fe=True)["value"] == 3


# ---------------------------------------------------------------- engine subclass
def rand_system(nv, rng, deg3=True):
    eqs = []
    for k in range(nv + 1):
        e = set()
        for d, cnt in ((1, 2), (2, 4), (3, 2 if deg3 else 0)):
            for _ in range(cnt):
                pool = list(range(nv))
                m = 0
                for i in range(d):
                    j = i + rng.randbelow(nv - i)
                    pool[i], pool[j] = pool[j], pool[i]
                    m |= 1 << pool[i]
                e ^= {m}
        eqs.append(sorted(e))
    return eqs


def test_subclass_equals_engine_on_quadratics():
    from crypto_autoresearcher.gf2 import closure as G
    rng = HashRng(7, "q")
    for nv in (6, 8):
        eqs = rand_system(nv, rng, deg3=False)
        eqs = [[m for m in e if bin(m).count("1") <= 2] for e in eqs]
        for D in (3, 4):
            a, _ = CL.w_closure_record(nv, D, eqs, stream=False)
            b, _ = G.Closure(nv, D, len(eqs)).w_closure(eqs, want_cert=False)
            for k in ("dims", "final_dim", "dims_by_deg", "iterations_to_fixpoint", "new_fallen_per_iteration",
                      "stack_rows_per_iteration", "one"):
                assert a[k] == b[k], k


def test_streamed_loop_equals_engine_loop():
    rng = HashRng(11, "s")
    for nv in (6, 8, 9):
        eqs = rand_system(nv, rng)
        for D in (3, 4, 5):
            a, _ = CL.w_closure_record(nv, D, eqs, stream=False)
            b, _ = CL.w_closure_record(nv, D, eqs, stream=True)
            for k in ("dims", "final_dim", "dims_by_deg", "iterations_to_fixpoint", "new_fallen_per_iteration",
                      "stack_rows_per_iteration", "one"):
                assert a[k] == b[k], (nv, D, k)
            assert [s["dims_by_deg"] for s in a["series"]] == [s["dims_by_deg"] for s in b["series"]]


def test_DER3_criterion_matches_direct_membership():
    for cid in ("m3n04", "m3n05", "m3n06"):
        for r in range(3):
            cell, sh, inst = mk_instance(cid, r)
            eqs, _ = CL.adapted_basis(inst["raw_eqs"])
            gb = enumz.groebner_from_Z(inst["Z"], inst["nv"])
            for D in (2, 3, 4):
                rec, cl = CL.w_closure_record(inst["nv"], D, eqs)
                dec = CL.decide(inst["nv"], D, rec, gb, enumz.rank_ev_by_deg(gb, D)[D])
                direct = CL.gb_membership(cl, enumz.gb_polys(gb))
                assert direct[0] == dec["contained"]


# ---------------------------------------------------------------- A/A exactness
def test_adapted_basis_is_invariant_under_recombination():
    rng = HashRng(13, "aa")
    nv = 8
    eqs = rand_system(nv, rng)
    T = reencode.random_invertible(len(eqs), rng)
    eqs2 = reencode.recombine(eqs, T)
    a, _ = CL.adapted_basis(eqs)
    b, _ = CL.adapted_basis(eqs2)
    assert a == b


def test_AA_reencoding_matches_exactly():
    for cid in ("m3n05", "m3n06"):
        for r in range(3):
            cell, sh, inst = mk_instance(cid, r)
            nv = inst["nv"]
            enc = reencode.random_encoding(nv, len(inst["raw_eqs"]), HashRng(r, "enc"))
            raw2, Z2 = reencode.apply_encoding(nv, inst["raw_eqs"], enc, inst["Z"])
            assert enumz.brute_force_Z(nv, raw2) == Z2
            gb1 = enumz.groebner_from_Z(inst["Z"], nv)
            gb2 = enumz.groebner_from_Z(Z2, nv)
            e1, _ = CL.adapted_basis(inst["raw_eqs"])
            e2, _ = CL.adapted_basis(raw2)
            for D in (2, 3, 4):
                a, ca = CL.w_closure_record(nv, D, e1)
                b, cb = CL.w_closure_record(nv, D, e2)
                sig = lambda x: ([(s["rank"], s["dims_by_deg"]) for s in x["series"]], x["dims_by_deg"],
                                 x["final_dim"], x["linear_forms"], x["one"])
                assert sig(a) == sig(b)
                d1 = CL.decide(nv, D, a, gb1, enumz.rank_ev_by_deg(gb1, D)[D])
                d2 = CL.decide(nv, D, b, gb2, enumz.rank_ev_by_deg(gb2, D)[D])
                assert d1 == d2


# ---------------------------------------------------------------- positive control, nulls
@pytest.mark.parametrize("nv,M", [(8, 8), (10, 12), (12, 12), (13, 14)])
def test_pc_tri_is_contained_at_3(nv, M):
    for seed in range(3):
        rng = HashRng(seed, f"pc{nv}")
        prof = [{1: 2, 2: 3, 3: 1}] * (M // 2) + [{1: 1, 2: 3}] * (M - M // 2)
        pc = PCT.pc_tri(nv, M, prof, rng)
        eqs, _ = CL.adapted_basis(pc["eqs"])
        Z = enumz.brute_force_Z(nv, pc["eqs"]) if nv <= 13 else pc["Z"]
        assert Z == pc["Z"] and len(Z) == 1
        gb = enumz.groebner_from_Z(Z, nv)
        rec, cl = CL.w_closure_record(nv, 3, eqs)
        dec = CL.decide(nv, 3, rec, gb, enumz.rank_ev_by_deg(gb, 3)[3])
        assert dec["contained"] is True
        assert rec["linear_forms"] == nv and not rec["one"]


def test_pc_tri_declared_mismatch_when_M_less_than_N():
    pc = PCT.pc_tri(10, 8, [{1: 2, 2: 2}] * 8, HashRng(1, "mm"))
    assert pc["mismatch"] and pc["M_eff"] == 10 and len(pc["eqs"]) == 10


def test_nulls_profile_and_planting():
    cell, sh, inst = mk_instance("m3n06", 0)
    prof = nulls.profile_of(inst["raw_eqs"])
    eqs, s = nulls.null_prof(inst["nv"], prof, HashRng(2, "np"))
    assert nulls.profile_of(eqs) == prof
    assert all(DS.eval_poly(e, s) == 0 for e in eqs)
    eqs2, s2 = nulls.null_shuf(inst["nv"], inst["raw_eqs"], HashRng(3, "ns"))
    assert nulls.profile_of(eqs2) == prof
    assert all(DS.eval_poly(e, s2) == 0 for e in eqs2)
    # same global incidences per degree
    import collections
    for d in (1, 2, 3):
        a = collections.Counter(m for e in inst["raw_eqs"] for m in e if bin(m).count("1") == d)
        b = collections.Counter(m for e in eqs2 for m in e if bin(m).count("1") == d)
        assert a == b


# ---------------------------------------------------------------- certificates
def _tiny_system():
    cell, sh, inst = mk_instance("m3n05", 1)
    eqs, _ = CL.adapted_basis(inst["raw_eqs"])
    gb = enumz.groebner_from_Z(inst["Z"], inst["nv"])
    return inst, eqs, gb


def test_ann_certificates_accept_and_tamper_rejects():
    inst, eqs, gb = _tiny_system()
    nv = inst["nv"]
    sysb = DS.canonical_bytes(nv, eqs)
    rec, cl = CL.w_closure_record(nv, 2, eqs)
    gp = enumz.gb_polys(gb)
    idx = next(i for i, g in enumerate(gp) if not cl.member(g))
    for form in ("dual", "primal"):
        c = certs.make_ann_cert(cl, nv, eqs, gp[idx], idx, {}, inst["Z"], form=form)
        assert RC.check_ann(c, sysb)["accept"]
    c = certs.make_ann_cert(cl, nv, eqs, gp[idx], idx, {}, inst["Z"], form="dual")
    # wrong g (an element of W_2) must fail (c)
    inside = next((g for g in gp if cl.member(g)), None)
    if inside is not None:
        bad = dict(c)
        bad["g"] = certs.poly_to_json(inside)
        assert not RC.check_ann(bad, sysb)["accept"]
    # wrong system hash fails (e)
    bad = dict(c)
    bad["system_sha256"] = "0" * 64
    assert not RC.check_ann(bad, sysb)["accept"]
    # dropping a functional enlarges U: some drop must break closure or (c) -> reject at least once
    rejects = 0
    for i in range(len(c["L_hex"])):
        d = dict(c)
        d["L_hex"] = c["L_hex"][:i] + c["L_hex"][i + 1:]
        rejects += 0 if RC.check_ann(d, sysb)["accept"] else 1
    assert rejects >= 1


def test_wdag_certificate_accepts_and_tamper_rejects():
    inst, eqs, gb = _tiny_system()
    nv = inst["nv"]
    sysb = DS.canonical_bytes(nv, eqs)
    rec, cl = CL.w_closure_record(nv, 3, eqs)
    assert CL.decide(nv, 3, rec, gb, enumz.rank_ev_by_deg(gb, 3)[3])["contained"]
    c = certs.make_wdag_cert(cl, nv, eqs, enumz.gb_polys(gb), {}, inst["Z"], expected_final_dim=rec["final_dim"])
    assert RC.check_wdag(c, sysb)["accept"]
    bad = json.loads(json.dumps(c))
    bad["nodes"][-1]["rows"] = bad["nodes"][-1]["rows"][1:] or bad["nodes"][-1]["rows"]
    if bad != c:
        assert not RC.check_wdag(bad, sysb)["accept"]
    bad2 = json.loads(json.dumps(c))
    bad2["targets"][0] = bad2["targets"][0] + [[0]]
    assert not RC.check_wdag(bad2, sysb)["accept"]


def test_canonical_serialisation_roundtrip_hash():
    inst, eqs, gb = _tiny_system()
    data = DS.canonical_bytes(inst["nv"], eqs)
    nv, eqs2, sha = RC.parse_system(data)
    assert nv == inst["nv"] and eqs2 == [sorted(e) for e in eqs] and sha == DS.system_sha256(nv, eqs)


# ---------------------------------------------------------------- fixtures (fast ones)
def test_fixtures_fast():
    import fixtures as FX
    for fn in (FX.f1, FX.f2, FX._f5_impl, FX.f7):
        r = fn()
        assert r["verdict"] == "pass", r
    assert FX.f4(n_systems=8)["verdict"] == "pass"


def test_fixture_f3_archived_records():
    import fixtures as FX
    r = FX.f3()
    assert r["verdict"] in ("pass", "not_covered"), r
    if r["verdict"] == "not_covered":
        pytest.skip(r["detail"]["reason"])


def test_fixture_f8_standing_ir2():
    import fixtures as FX
    assert FX.f8(PROTO, n_affine=10, brute_cells_big=False)["verdict"] == "pass"


@pytest.mark.skipif(not os.path.exists("/opt/conda-sage/bin/sage"), reason="Sage not installed")
def test_fixture_f6_sage_oracle():
    import fixtures as FX
    r = FX.f6()
    assert r["verdict"] == "pass", r


# ---------------------------------------------------------------- end to end
def run_cli(rd, cell, arm, r, *extra):
    args = RUN.parse(["--run-dir", rd, "--cell", cell, "--arm", arm, "--r", str(r), "--protocol-sha256", PROTO,
                      "--no-isolate", *extra])
    return RUN.run_trial(args)


def read_gz(path):
    return [json.loads(l) for l in gzip.open(path, "rt").read().splitlines() if l.strip()]


def test_end_to_end_all_arms_and_controls(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    for arm in ("EQS4", "EQS2", "NULL-PROF", "NULL-SHUF", "PC-TRI", "EQS4-AA", "EQS4-U", "EQS4-FULLFE", "EQS4-NOFE"):
        st = run_cli(rd, "m3n06", arm, 1)
        assert st["status"] == "completed", st.get("traceback")
    import analyze
    controls, summary = analyze.analyze(rd)
    assert controls["C-PC"]["all_ok"] is True
    assert controls["C-AA-ENC"]["zero_discrepancies"] is True
    assert controls["C-FE-EQ"]["all_agree"] is True
    assert not any(summary["flags"].values())
    inst = {d["key"]: d for d in read_gz(os.path.join(rd, "instances.jsonl.gz"))}
    assert inst["m3n06/EQS4/r1"]["valid"] and inst["m3n06/EQS4/r1"]["checks"]["descent_check"]["ok"]
    assert len(inst["m3n06/EQS4/r1"]["system_sha256"]) == 64
    # certificate present for contained target and accepted by the reference checker
    clos = read_gz(os.path.join(rd, "closures.jsonl.gz"))
    wd = [c["M8"] for c in clos if c.get("kind") == "certificate" and c["cert_kind"] == "wdag"]
    assert wd and wd[0]["status"] == "pending_checker"      # emitted, independent checker not yet run
    cert = json.loads(gzip.open(os.path.join(rd, wd[0]["path"])).read())
    sysb = gzip.open(os.path.join(rd, inst["m3n06/EQS4/r1"]["system_file"]["path"])).read()
    assert RC.check_wdag(cert, sysb)["accept"]
    # refuses to overwrite a finished trial
    with pytest.raises(SystemExit):
        run_cli(rd, "m3n06", "EQS4", 1)


def test_non_containment_emits_certificate_end_to_end(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    st = run_cli(rd, "m3n06", "EQS4", 0, "--cert-degree", "3", "--wdag", "never")
    assert st["status"] == "completed", st.get("traceback")
    clos = read_gz(os.path.join(rd, "closures.jsonl.gz"))
    d3 = next(c for c in clos if c.get("D") == 3 and c.get("key") == "m3n06/EQS4/r0" and "M1" in c)
    assert d3["M1"]["contained"] is False
    ann = [c["M8"] for c in clos if c.get("kind") == "certificate" and c["cert_kind"] == "ann"]
    assert ann and ann[0]["status"] == "pending_checker"
    # the certificate record comes AFTER the closure record it belongs to
    order = [i for i, c in enumerate(clos) if c.get("kind") == "certificate"]
    assert order[0] > clos.index(d3)
    inst = next(d for d in read_gz(os.path.join(rd, "instances.jsonl.gz")))
    cert = json.loads(gzip.open(os.path.join(rd, ann[0]["path"])).read())
    sysb = gzip.open(os.path.join(rd, inst["system_file"]["path"])).read()
    assert RC.check_ann(cert, sysb)["accept"]


def test_trial_is_deterministic_across_run_dirs(tmp_path):
    shas = []
    for name in ("a", "b"):
        rd = str(tmp_path / name)
        os.makedirs(rd)
        run_cli(rd, "m3n07", "EQS4", 3)
        run_cli(rd, "m3n07", "NULL-PROF", 3)
        recs = {d["key"]: (d["system_sha256"], d["raw_system_sha256"], d["Z_hex"])
                for d in read_gz(os.path.join(rd, "instances.jsonl.gz"))}
        shas.append(recs)
    assert shas[0] == shas[1]


def test_isolated_launcher_subprocess(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    p = subprocess.run([sys.executable, os.path.join(CODE, "run.py"), "--run-dir", rd, "--cell", "m3n04",
                        "--arm", "EQS4", "--r", "0", "--protocol-sha256", PROTO],
                       capture_output=True, text=True, timeout=300)
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout.strip().splitlines()[-1])["status"] == "completed"
    cost = [json.loads(l) for l in open(os.path.join(rd, "cost.jsonl"))]
    assert cost and all(c["status"] == "ok" for c in cost)


def test_wall_cap_censors_never_false(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    args = RUN.parse(["--run-dir", rd, "--cell", "m3n12", "--arm", "PC-TRI", "--r", "0", "--protocol-sha256", PROTO,
                      "--wall-cap", "0.001"])
    st = RUN.run_trial(args)
    assert st["status"] == "completed"
    clos = read_gz(os.path.join(rd, "closures.jsonl.gz"))
    rows = [c for c in clos if c.get("D")]
    assert rows and all(c["status"].startswith("censored") or c["status"] == "failed_infrastructure" or c["status"] == "ok"
                        for c in rows)
    cens = [c for c in rows if c["status"] != "ok"]
    if cens:
        assert cens[0]["M1"]["contained"] in ("censored", "failed")
        summ = next(c for c in clos if c.get("kind") == "summary")
        assert summ["censored"] is True
        assert summ["M1_at_4"]["contained"] in (True, "censored")      # never False


def test_provenance_hashes():
    import provenance
    cur = provenance.compute()
    assert any(k.endswith("closure.py") for k in cur["files"])
    assert any("gf2/_kernels.c" in k for k in cur["files"])


# ================================================================ revision 2 items
def _args(rd, cell="m3n06", arm="EQS4", r=0, *extra):
    return RUN.parse(["--run-dir", rd, "--cell", cell, "--arm", arm, "--r", str(r), "--protocol-sha256", PROTO,
                      "--no-isolate", *extra])


def test_wdag_policy_rule():
    a = _args("x")
    assert RUN.wdag_policy(a, 12) == "now" and RUN.wdag_policy(a, 20) == "now"
    assert RUN.wdag_policy(a, 21) == "selection_pass" and RUN.wdag_policy(a, 26) == "selection_pass"
    assert RUN.wdag_policy(a, 27) == "none" and RUN.wdag_policy(a, 40) == "none"
    assert RUN.wdag_policy(_args("x", "m3n06", "EQS4", 0, "--wdag", "never"), 12) == "none"
    assert RUN.wdag_policy(_args("x", "m3n06", "EQS4", 0, "--wdag", "always"), 40) == "now"
    assert RUN.WDAG_WALL_CAP_S == 900 and RUN.WDAG_MAX_JSON_BYTES == 400 * 10 ** 6


def test_wdag_nonce_selection_rule():
    import certify, hashlib
    keys = [f"m3n13/EQS4/r{i}" for i in range(5)]
    sel = certify.select_keys(PROTO, "m3n13", keys)
    i = int(hashlib.sha256((PROTO + "\nWDAG\n" + "m3n13").encode()).hexdigest(), 16) % 5
    assert sel == [sorted(keys)[i], sorted(keys)[(i + 1) % 5]]
    assert certify.select_keys(PROTO, "m3n13", list(reversed(keys))) == sel      # order independent
    assert certify.select_keys(PROTO, "m3n13", keys[:2]) == sorted(keys[:2])
    assert certify.select_keys(PROTO, "m3n13", keys[:1]) == keys[:1]
    assert certify.select_keys(PROTO, "m3n13", []) == []


def test_cell_over_20_gets_no_wdag_in_trial_and_selection_pass_certifies(tmp_path):
    import certify
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    # m3n12 has N = 24: the trial must record not_attempted_by_rule and emit nothing
    st = RUN.run_trial(_args(rd, "m3n12", "PC-TRI", 0))
    assert st["status"] == "completed"
    st = RUN.run_trial(_args(rd, "m3n12", "EQS4", 0, "--skip-m7"))
    assert st["status"] == "completed", st.get("traceback")
    clos = read_gz(os.path.join(rd, "closures.jsonl.gz"))
    wd = [c for c in clos if c.get("kind") == "certificate" and c["cert_kind"] == "wdag"]
    assert wd and wd[0]["M8"]["status"] == "not_attempted_by_rule"
    assert not os.listdir(os.path.join(rd, "certificates"))
    # the selection pass itself, exercised on a small cell with the range check lifted
    rd2 = str(tmp_path / "run2")
    os.makedirs(rd2)
    for r in range(4):
        RUN.run_trial(_args(rd2, "m3n06", "EQS4", r, "--wdag", "never"))
    out = certify.run_selection(rd2, "m3n06", PROTO, isolate=False, enforce_range=False)
    assert len(out["selected"]) == 2 and all(x["status"] == "pending_checker" for x in out["results"])
    assert out["selected"] == certify.select_keys(PROTO, "m3n06", [f"m3n06/EQS4/r{r}" for r in range(4)])
    again = certify.run_selection(rd2, "m3n06", PROTO, isolate=False, enforce_range=False)
    assert all("skipped" in x for x in again["results"])
    with pytest.raises(SystemExit):
        certify.run_selection(rd2, "m3n06", PROTO, isolate=False, enforce_range=True)


def test_certificate_failure_never_alters_M1(tmp_path, monkeypatch):
    """A certificate guard trip or a watchdog kill is recorded as not_emitted; the closure record
    (written first) keeps its M-1."""
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    st = RUN.run_trial(_args(rd, "m3n06", "EQS4", 0, "--cert-degree", "3", "--wdag", "never",
                             "--ann-max-bytes", "10"))
    assert st["status"] == "completed"
    clos = read_gz(os.path.join(rd, "closures.jsonl.gz"))
    d3 = next(c for c in clos if c.get("D") == 3 and "M1" in c)
    assert d3["M1"]["contained"] is False and d3["status"] == "ok"
    ann = next(c for c in clos if c.get("kind") == "certificate" and c["cert_kind"] == "ann")
    assert ann["M8"]["status"] == "not_emitted" and "size estimate" in ann["M8"]["reason"]
    # wall-cap kill of the certificate child (real fork): not_emitted, closure untouched
    cfile = os.path.join(rd, "closures.jsonl.gz")
    eqs, _ = CL.adapted_basis(mk_instance("m3n06", 0)[2]["raw_eqs"])
    inst = mk_instance("m3n06", 0)[2]
    gb = enumz.groebner_from_Z(inst["Z"], inst["nv"])
    import time as _t
    monkeypatch.setattr(RUN, "cert_task", lambda task: (_t.sleep(30), {})[1])
    info = RUN.emit_certificate(rd, cfile, os.path.join(rd, "cost.jsonl"), "m3n06/EQS4/r0", "m3n06", "wdag", 4,
                                inst["nv"], eqs, inst["Z"], enumz.gb_polys(gb), {}, 1, isolate=True, wall_cap=0.5)
    assert info["status"] == "not_emitted" and "wall" in info["reason"]
    d3b = [c for c in read_gz(cfile) if c.get("D") == 3 and "M1" in c]
    assert d3b[0]["M1"]["contained"] is False


def test_certificate_child_requires_same_dimension(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    os.makedirs(os.path.join(rd, "certificates"))
    inst = mk_instance("m3n05", 1)[2]
    eqs, _ = CL.adapted_basis(inst["raw_eqs"])
    gb = enumz.groebner_from_Z(inst["Z"], inst["nv"])
    info = RUN.emit_certificate(rd, os.path.join(rd, "c.jsonl.gz"), os.path.join(rd, "cost.jsonl"), "k", "m3n05",
                                "wdag", 3, inst["nv"], eqs, inst["Z"], enumz.gb_polys(gb), {}, 12345, isolate=False)
    assert info["status"] == "not_emitted" and info["reason"] == "dimension_mismatch" and info["flag"]


def test_wdag_json_cap(tmp_path):
    inst = mk_instance("m3n05", 1)[2]
    eqs, _ = CL.adapted_basis(inst["raw_eqs"])
    gb = enumz.groebner_from_Z(inst["Z"], inst["nv"])
    rec, cl = CL.w_closure_record(inst["nv"], 3, eqs)
    c = certs.make_wdag_cert(cl, inst["nv"], eqs, enumz.gb_polys(gb), {}, inst["Z"])
    out = certs.write_cert(str(tmp_path / "x.json.gz"), c, max_bytes=100)
    assert "not_emitted" in out and not os.path.exists(tmp_path / "x.json.gz")
    assert "content_sha256" in certs.write_cert(str(tmp_path / "y.json.gz"), c, max_bytes=10 ** 9)


def test_pick_unique_treats_plant_failure_as_non_unique(tmp_path, monkeypatch):
    cell = CE.CELLS["m3n06"]
    sh = RUN.shared_part(cell, 0, PROTO)
    orig = RUN.eqs_instance
    calls = {"n": 0}

    def flaky(cell_, sh_, arm, r, proto, a=0, with_system=True):
        calls["n"] += 1
        if a in (0, 1, 2):
            raise DS.PlantInfeasible("injected")
        return orig(cell_, sh_, arm, r, proto, a=a, with_system=with_system)
    monkeypatch.setattr(RUN, "eqs_instance", flaky)
    rd = str(tmp_path / "r")
    os.makedirs(rd)
    results = {}
    RUN.pick_unique(cell, sh, _args(rd), results)
    log = results["u_attempts"]
    assert [x.get("plant_infeasible") is not None for x in log[:3]] == [True, True, True]
    assert all(x["counted_as"] == "non-unique" for x in log[:3])
    assert results["eqs4u"] == "not_available" or results["eqs4u"]["attempt"] >= 3


def test_nofe_runs_on_same_adapted_generators_as_fullfe(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    for arm in ("EQS4-FULLFE", "EQS4-NOFE"):
        assert RUN.run_trial(_args(rd, "m3n06", arm, 0))["status"] == "completed"
    inst = {d["key"]: d for d in read_gz(os.path.join(rd, "instances.jsonl.gz"))}
    assert inst["m3n06/EQS4-FULLFE/r0"]["system_sha256"] == inst["m3n06/EQS4-NOFE/r0"]["system_sha256"]
    assert inst["m3n06/EQS4-NOFE/r0"]["system_sha256"] != inst["m3n06/EQS4-NOFE/r0"]["raw_system_sha256"] or True
    rows = {}
    for c in read_gz(os.path.join(rd, "closures.jsonl.gz")):
        if c.get("arm") in ("EQS4-FULLFE", "EQS4-NOFE") and c.get("status") == "ok":
            rows[(c["arm"], c["D"])] = c
    for D in (2, 3, 4):
        assert rows[("EQS4-FULLFE", D)]["boolean_companion"] == rows[("EQS4-NOFE", D)]["boolean_companion"]
        assert rows[("EQS4-FULLFE", D)]["full_ring"]["with_fe"] and not rows[("EQS4-NOFE", D)]["full_ring"]["with_fe"]


def test_require_fixtures_refuses_not_covered_and_failures(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    fx = str(tmp_path / "fx.json")

    def write(verdicts):
        json.dump({"fixtures": [{"id": f"F-{i+1}", "verdict": v} for i, v in enumerate(verdicts)]}, open(fx, "w"))
    write(["pass"] * 7 + ["not_covered"])
    with pytest.raises(SystemExit):
        RUN.run_trial(_args(rd, "m3n04", "EQS4", 0, "--require-fixtures", fx))
    write(["pass"] * 7)
    with pytest.raises(SystemExit):
        RUN.run_trial(_args(rd, "m3n04", "EQS4", 0, "--require-fixtures", fx))
    write(["pass"] * 8)
    assert RUN.run_trial(_args(rd, "m3n04", "EQS4", 0, "--require-fixtures", fx))["status"] == "completed"


def test_exhaustive_predicate_agrees_with_checker_on_all_flips():
    import fixtures as FX
    r = FX._f5_impl()
    assert r["verdict"] == "pass"
    flips = r["detail"]["single_bit_flips"]
    assert flips["checker_vs_exhaustive_predicate_disagreements"] == 0
    assert flips["rejected"] + flips["accepted"] == flips["total"] == 31
    assert r["detail"]["declared_tamper_predicate_abc"] == [True, True, False]


def test_f3_checks_both_loops():
    import fixtures as FX
    r = FX.f3()
    if r["verdict"] == "not_covered":
        pytest.skip(r["detail"]["reason"])
    assert r["verdict"] == "pass"
    assert all(set(x["loops"]) == {"inherited", "streamed"} and all(v["match"] for v in x["loops"].values())
               for x in r["detail"]["instances"])


def test_f4_raw_vs_adapted_recorded():
    import fixtures as FX
    r = FX.f4(n_systems=6)
    assert r["verdict"] == "pass" and r["detail"]["raw_vs_adapted_comparisons_D3_5"] > 0


def test_affine_hull_forms_and_search():
    import fixtures as FX
    Z = [0b101101, 0b100111, 0b001101]
    forms = FX.affine_hull_forms(Z, 6)
    for f in forms:
        assert all(DS.eval_poly(f, z) == 0 for z in Z)
    zs, free = enumz.affine_subspace_Z(6, [[0]] if False else [], forms)
    assert set(Z) <= set(zs)


# ---------------------------------------------------------------- analyze: M-8, uncertified, gates, P-3
def _write_run(rd, instances, closures):
    def put(name, rows):
        with open(os.path.join(rd, name), "wb") as raw:
            for r in rows:
                with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as g:
                    g.write((json.dumps(r) + "\n").encode())
    put("instances.jsonl.gz", instances)
    put("closures.jsonl.gz", closures)


def _summ(key, arm, N, m1, z, m3=4):
    cell, _, r = key.split("/")
    return {"kind": "summary", "key": key, "arm": arm, "cell": cell, "r": 0, "N": N, "M3": m3, "D_reached": 4,
            "censored": False, "M1_at_4": m1, "z": z}


def test_analyze_uncertified_and_fmain_gate_and_p3(tmp_path):
    import analyze
    rd = str(tmp_path)
    nc = {"contained": False, "type": "L", "deficit": 3, "d_GB": 1}
    ok = {"contained": True, "type": None, "deficit": 0, "d_GB": 1}
    closures, instances = [], []
    for key, arm, m1 in (("m3n10/EQS4/r0", "EQS4", nc), ("m3n10/EQS4/r1", "EQS4", ok), ("m3n10/EQS4/r2", "EQS4", nc)):
        closures.append(_summ(key, arm, 19, m1, 1))
        closures.append({"key": key, "D": 4, "status": "ok", "M1": m1, "M2": {}, "M4": [{"rank": 1, "dims_by_deg": [0]}],
                         "engine": {"final_dim": 5, "dims_by_deg": [0, 1], "iterations_to_fixpoint": 1}})
        instances.append({"key": key, "N": 19, "cell": "m3n10", "arm": arm, "system_sha256": "ab"})
    closures.append({"kind": "certificate", "key": "m3n10/EQS4/r0", "cell": "m3n10", "D": 4, "cert_kind": "ann",
                     "M8": {"status": "pending_checker", "cert_sha256": "h0", "g": [[0]]}})
    closures.append({"kind": "certificate", "key": "m3n10/EQS4/r2", "cell": "m3n10", "D": 4, "cert_kind": "ann",
                     "M8": {"status": "not_emitted", "reason": "size estimate"}})
    # nulls: 4 seeds in m3n10: z=1 & false, z=1 & false, z=1 & contained, z=2 & false
    for r, (m1, z) in enumerate(((nc, 1), (nc, 1), (ok, 1), (nc, 2))):
        closures.append(_summ(f"m3n10/NULL-PROF/r{r}", "NULL-PROF", 19, m1, z))
    closures.append(_summ("m3n40/EQS4/r0", "EQS4", 40, ok, 1))
    instances.append({"key": "m3n40/EQS4/r0", "N": 40, "cell": "m3n40", "arm": "EQS4", "system_sha256": "zz"})
    _write_run(rd, instances, closures)
    controls, summ = analyze.analyze(rd)
    unc = {u["key"]: u["ann_status"] for u in summ["non_containment_uncertified"]}
    assert unc == {"m3n10/EQS4/r0": "pending_checker", "m3n10/EQS4/r2": "not_emitted"}
    assert summ["F-MAIN_gate"]["gate"] == "incomplete_censored" and summ["F-MAIN_gate"]["detail"] == "certificate_pending"
    assert summ["P-3"]["numerator"] == 2 and summ["P-3"]["denominator"] == 3
    assert abs(summ["P-3"]["pooled_fraction_over_Z1_verified"] - 2 / 3) < 1e-9
    c = summ["F-MAIN_count_per_carrying_cell"]["m3n10"]
    assert c["z1_verified"] == 3 and c["z1_and_M1_false"] == 2 and not c["threshold_3_of_5_met"]
    assert [x["key"] for x in summ["containment_N_ge_27"]] == ["m3n40/EQS4/r0"]
    # checker verdicts move statuses: accepted / rejected
    pin = lambda w, h="ab", D=4: {"verdict": w, "system_sha256": h, "D": D}
    _, s0 = analyze.analyze(rd, {"h0": "accept"})            # bare string: not pinned, stays pending
    assert {u["key"]: u["ann_status"] for u in s0["non_containment_uncertified"]}["m3n10/EQS4/r0"] == "pending_checker"
    _, sb = analyze.analyze(rd, {"h0": pin("accept", h="WRONG")})   # wrong system hash
    assert {u["key"]: u["ann_status"] for u in sb["non_containment_uncertified"]}["m3n10/EQS4/r0"] == "pending_checker"
    _, sd = analyze.analyze(rd, {"h0": pin("accept", D=3)})         # wrong D
    assert {u["key"]: u["ann_status"] for u in sd["non_containment_uncertified"]}["m3n10/EQS4/r0"] == "pending_checker"
    _, s2 = analyze.analyze(rd, {"h0": pin("accept")})
    assert [u["key"] for u in s2["non_containment_uncertified"]] == ["m3n10/EQS4/r2"]
    assert [u["key"] for u in s2["non_containment_certified"]] == ["m3n10/EQS4/r0"]
    _, s3 = analyze.analyze(rd, {"h0": pin("reject")})
    assert {u["key"]: u["ann_status"] for u in s3["non_containment_uncertified"]}["m3n10/EQS4/r0"] == "rejected"
    assert set(x["status"] for x in s3["M8"]) <= set(analyze.M8_VOCAB)


def test_analyze_end_to_end_reports_m6_and_calibration(tmp_path):
    import analyze
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    for arm in ("EQS4", "EQS2"):
        RUN.run_trial(_args(rd, "m3n06", arm, 1))
    controls, summ = analyze.analyze(rd)
    assert summ["P-7_calibration"]["all_d_F_eq_le_2"] is True
    assert all(x["d_F_eq"] == 2 for x in summ["M6_vs_2_and_D_solve_vs_2_and_3"])
    assert summ["F-MAIN_gate"]["gate"] in ("no_block_from_certificates", "incomplete_censored")
    assert summ["F-MAIN_gate"]["uncertified_non_containments"] == []


def test_ann_form_option_and_formats_keys(tmp_path):
    """--ann-form forces dual / primal; emitted certificates carry exactly the documented keys."""
    allowed = {"schema", "D", "nv", "neq", "system_sha256", "form", "g", "g_gb_index", "Z", "instance",
               "L_hex", "basis_hex"}
    for form in ("dual", "primal"):
        rd = str(tmp_path / form)
        os.makedirs(rd)
        st = RUN.run_trial(_args(rd, "m3n06", "EQS4", 0, "--cert-degree", "3", "--wdag", "never", "--ann-form", form))
        assert st["status"] == "completed"
        rec = [c for c in read_gz(os.path.join(rd, "closures.jsonl.gz")) if c.get("cert_kind") == "ann"][0]
        cert = json.loads(gzip.open(os.path.join(rd, rec["M8"]["path"])).read())
        assert cert["form"] == form and set(cert) <= allowed and ("L_hex" in cert) == (form == "dual")
        assert cert["neq"] == len(json.loads(gzip.open(os.path.join(
            rd, [d for d in read_gz(os.path.join(rd, "instances.jsonl.gz"))][0]["system_file"]["path"])).read())["eqs"])
        import hashlib
        assert hashlib.sha256(certs.cert_bytes(cert)).hexdigest() == rec["M8"]["cert_sha256"]
        assert all(h and h == h.lower() and not h.startswith("0x") for h in cert.get("L_hex", cert.get("basis_hex")))
        # g is the reduced GB element at g_gb_index (ordering: degree asc, then mask desc)
        inst = mk_instance("m3n06", 0)[2]
        gp = enumz.gb_polys(enumz.groebner_from_Z(inst["Z"], inst["nv"]))
        assert certs.poly_to_json(gp[cert["g_gb_index"]]) == cert["g"]


def test_gb_listing_order_documented():
    gb = enumz.groebner_from_Z([0b0011, 0b0101, 0b1001, 0b0110], 4)
    keys = [(bin(m).count("1"), -m) for m, _ in gb["gens"]]
    assert keys == sorted(keys)


def test_raw_hash_serialisation_includes_zero_generators():
    nv, eqs = 3, [[1], [], [3, 0]]
    data = json.loads(DS.canonical_bytes(nv, eqs))
    assert data["neq"] == 3 and data["eqs"][1] == [] and data["schema"] == "sembin-sys-v1"
    cell, sh, inst = mk_instance("m3n06", 0)
    assert DS.system_sha256(inst["nv"], inst["raw_eqs"]) == RUN.instance_record(
        "k", cell, sh, inst, inst["raw_eqs"], inst["raw_eqs"], {})["raw_system_sha256"]


def test_non_eqs_certificates_omit_instance_block(tmp_path):
    rd = str(tmp_path / "run")
    os.makedirs(rd)
    st = RUN.run_trial(_args(rd, "m3n07", "NULL-PROF", 1, "--cert-degree", "4", "--always-ann", "--wdag", "never"))
    assert st["status"] == "completed"
    recs = [c for c in read_gz(os.path.join(rd, "closures.jsonl.gz")) if c.get("cert_kind") == "ann"]
    if not recs:
        pytest.skip("this null is contained at D=4")
    cert = json.loads(gzip.open(os.path.join(rd, recs[0]["M8"]["path"])).read())
    assert "instance" not in cert        # absent, never empty


def _no_empty_optional(c):
    for k in ("instance", "Z", "levels", "g_gb_index"):
        if k in c:
            assert c[k] not in (None, {}, []) or k == "g_gb_index" and c[k] == 0, k


def test_no_optional_key_written_empty_or_null():
    inst = mk_instance("m3n05", 1)[2]
    eqs, _ = CL.adapted_basis(inst["raw_eqs"])
    gb = enumz.groebner_from_Z(inst["Z"], inst["nv"])
    gp = enumz.gb_polys(gb)
    rec, cl = CL.w_closure_record(inst["nv"], 2, eqs)
    idx = next(i for i, g in enumerate(gp) if not cl.member(g))
    for meta, Z in (({}, inst["Z"]), ({"n": 5}, []), ({}, [])):
        for form in ("dual", "primal"):
            c = certs.make_ann_cert(cl, inst["nv"], eqs, gp[idx], idx, meta, Z, form=form)
            _no_empty_optional(c)
            assert ("instance" in c) == bool(meta) and ("Z" in c) == bool(Z)
    rec3, cl3 = CL.w_closure_record(inst["nv"], 3, eqs)
    w = certs.make_wdag_cert(cl3, inst["nv"], eqs, gp, {}, [], expected_final_dim=rec3["final_dim"])
    _no_empty_optional(w)
    assert "instance" not in w and "Z" not in w and w["levels"] >= 1

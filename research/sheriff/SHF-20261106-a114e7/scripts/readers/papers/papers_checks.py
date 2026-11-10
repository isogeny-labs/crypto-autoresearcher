#!/usr/bin/env python3
"""Independent checks for reader `papers` (joint PPX), sheriff case SHF-20261106-a114e7.

Runs nothing from the audited repositories. Reads git blobs of isogeny-labs/crypto
with `git show <rev>:<path>` (data only) and recomputes numbers with its own code.

Usage: python3 -I papers_checks.py /home/user/crypto > papers_checks.out
Writes papers_checks.json next to this script.
"""
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

CRYPTO = sys.argv[1] if len(sys.argv) > 1 else "/home/user/crypto"
OUT = {}
FAILS = []


def git_show(rev, path):
    r = subprocess.run(["git", "-c", "gc.auto=0", "-C", CRYPTO, "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def check(name, claimed, derived):
    """Compare a producer's claimed value with an independent derivation."""
    ok = claimed == derived
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: claimed={claimed!r} derived={derived!r}")
    return ok


# ---------------------------------------------------------------- sieve (own)
def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


def is_prime(n):
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for q in small:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


print("=== A. P4 blind re-derivation: primes p = 1 (mod 6), p <= 5000 ===")
P5000 = primes_upto(5000)
n_1mod6 = sum(1 for p in P5000 if p % 6 == 1)
n_all = len(P5000)
n_forprime_7 = sum(1 for p in P5000 if p >= 7)
first_last = [p for p in P5000 if p % 6 == 1]
A = {
    "count_p_1mod6_le_5000": n_1mod6,
    "count_all_primes_le_5000": n_all,
    "count_primes_7_to_5000": n_forprime_7,
    "first_last": [first_last[0], first_last[-1]],
}
OUT["A_p4"] = A
okA = all([
    check("tex:444 'all 330 primes p=1 mod 6 with 7<=p<=5000'", 330, n_1mod6),
    check("tex:444 'of the 669 primes p<=5000'", 669, n_all),
    check("count.txt 'primes visited by forprime 666'", 666, n_forprime_7),
    check("count.txt 'first 7, last 4999'", [7, 4999], A["first_last"]),
])

print("=== B. Second blind number: structural_completeness.tex:411-414, 447-448 ===")
P1000 = [p for p in P5000 if p <= 1000]
n_1mod6_1000 = sum(1 for p in P1000 if p % 6 == 1)
# norm form 4p = 73 + 3k^2, p prime, 7 <= p <= 5000
ks = []
for k in range(1, 200):
    num = 73 + 3 * k * k
    if num % 4:
        continue
    p = num // 4
    if p > 5000:
        break
    if p >= 7 and is_prime(p):
        ks.append((k, p))
OUT["B_second_number"] = {"count_p_1mod6_le_1000": n_1mod6_1000, "norm_form_k_p": ks}
okB = all([
    check("tex:414 '80 primes in that range' (p=1 mod 6, p<=1000)", 80, n_1mod6_1000),
    check("tex:447-448 '11 primes ... 4p = 73+3k^2, k in {1,5,9,11,21,25,31,35,41,55,65}'",
          [1, 5, 9, 11, 21, 25, 31, 35, 41, 55, 65], [k for k, _ in ks]),
    check("tex:440 CM-73 set contains the k<=11 norm-form primes", [19, 37, 79, 109],
          [p for k, p in ks if k <= 11]),
    check("tex:461 'norm-form prime p = 349'", True, 349 in [p for _, p in ks]),
])

print("=== C. LLL note numbers (abstract, sec. 3 and the PPN-2 footnote) ===")
# Group orders: standard values (SEC 2 / FIPS 186-4 / RFC 5639), recalled; cross-checked by
# string equality against crypto:src/ecc/curve_zoo.rs and src/cryptanalysis/p256_structural.rs.
ORD = {
    "secp256k1": int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16),
    "P-256": int("FFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551", 16),
    "brainpoolP256r1": int("A9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7", 16),
    "P-384": int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973", 16),
    "brainpoolP384r1": int("8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565", 16),
    "P-521": int("1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409", 16),
}
F64MAX = (2 ** 53 - 1) * 2 ** 971
assert F64MAX == int(sys.float_info.max)
C = {"orders_prime": {k: is_prime(v) for k, v in ORD.items()}}
C["n4_gt_f64max"] = {k: v ** 4 > F64MAX for k, v in ORD.items()}
C["log2_f64max"] = math.log2(F64MAX)
C["log2_n_secp256k1_minus_n_P256"] = math.log2(ORD["secp256k1"] - ORD["P-256"])
fac = Fraction(ORD["P-256"] ** 4, F64MAX)
C["P256_n4_over_f64max_log2_of_1_minus"] = math.log2(1 - float(fac))
n = ORD["P-521"]
d = n * n
max_bits = d.bit_length()
scale = max_bits - 500
extra = max(0, d.bit_length() - 1020)
shifted = d >> extra                              # big_to_f64_scaled: shift right (truncates)
v_rn = float(shifted)                             # Python int->float is correctly rounded
diag_rn = Fraction(v_rn) * Fraction(2) ** (extra - scale)
top53 = shifted >> (shifted.bit_length() - 53) << (shifted.bit_length() - 53)  # truncating conversion
diag_tr = Fraction(top53) * Fraction(2) ** (extra - scale)
C.update({
    "P521_n2_bits": max_bits, "scale_shift": scale, "extra_shift": extra,
    "diag_round_nearest_is_2^500": diag_rn == 2 ** 500,
    "diag_truncating_equals_2^500(1-2^-53)": diag_tr == Fraction(2 ** 500) * (1 - Fraction(1, 2 ** 53)),
    "truncation_residual_log2": math.log2(2 ** 500 - diag_tr),
})
OUT["C_lll"] = {k: (str(v) if isinstance(v, Fraction) else v) for k, v in C.items()}
okC = all([
    check("all six orders prime", True, all(C["orders_prime"].values())),
    check("abstract: n^4 > f64::MAX for secp256k1", True, C["n4_gt_f64max"]["secp256k1"]),
    check("sec.3: P-256 n^4 below f64::MAX", False, C["n4_gt_f64max"]["P-256"]),
    check("sec.3: brainpoolP256r1 n^4 below f64::MAX", False, C["n4_gt_f64max"]["brainpoolP256r1"]),
    check("abstract: every 384-bit curve overflows (P-384)", True, C["n4_gt_f64max"]["P-384"]),
    check("abstract: every 384-bit curve overflows (brainpoolP384r1)", True, C["n4_gt_f64max"]["brainpoolP384r1"]),
    check("analysis 10 corr.3: f64::MAX ~ 2^1024 (rounded log2)", 1024, round(C["log2_f64max"])),
    check("analysis 10 corr.3: n(secp256k1)-n(P-256) ~ 2^224.0 (1 dp)", 224.0, round(C["log2_n_secp256k1_minus_n_P256"], 1)),
    check("analysis 10 corr.3: P-256 n^4 below by factor ~1-2^-30 (rounded)", -30, round(C["P256_n4_over_f64max_log2_of_1_minus"])),
    check("note footnote: scaled conversion truncates 22 low bits", 22, extra),
    check("note correction: P-521 diagonal rounds to exactly 2^500", True, C["diag_round_nearest_is_2^500"]),
    check("note footnote: truncating conversion gives 2^500(1-2^-53)", True, C["diag_truncating_equals_2^500(1-2^-53)"]),
    check("note footnote: truncation residual 2^447", 447.0, C["truncation_residual_log2"]),
])

print("=== D. Proves-too-much: the same check on values known to be wrong must FAIL ===")
D = {
    "withdrawn_621": check("CONTROL tex(old) '621 primes'", 621, n_1mod6),
    "off_by_one_331": check("CONTROL '331 primes'", 331, n_1mod6),
    "wrong_81": check("CONTROL '81 primes <= 1000'", 81, n_1mod6_1000),
    "wrong_k_list": check("CONTROL k list missing 65", [1, 5, 9, 11, 21, 25, 31, 35, 41, 55],
                          [k for k, _ in ks]),
    "P256_overflows": check("CONTROL 'P-256 n^4 > f64::MAX' (the withdrawn curve-specificity inverse)",
                            True, C["n4_gt_f64max"]["P-256"]),
    "trunc_exact": check("CONTROL 'truncating conversion also gives exactly 2^500'", True,
                         diag_tr == 2 ** 500),
    "old_2^1023": check("CONTROL analysis(old) f64::MAX ~ 2^1023", 1023, round(C["log2_f64max"])),
    "old_2^192": check("CONTROL analysis(old) difference ~2^192", 192.0, round(C["log2_n_secp256k1_minus_n_P256"], 1)),
}
OUT["D_controls_all_failed"] = not any(D.values())
print(f"  controls: {sum(1 for v in D.values() if not v)}/{len(D)} failed as required")

print("=== E. PPN-3: Reproducibility LOC table (tex:977-994) ===")
TABLE = [("audit.gp", 235, "yes"), ("cl_o_horizontal.gp", 203, "yes"),
         ("structural_invariants.gp", 292, "yes"), ("vfcg_experiment.gp", 254, "yes"),
         ("vfcg_variants.gp", 284, "yes"), ("howe_gluing_test.gp", 260, "yes"),
         ("howe_explicit_cover.gp", 201, "yes"), ("cover_complexity.gp", 165, "yes"),
         ("supersingular_reductions.gp", 171, "yes"), ("p256_comparison.gp", 283, "yes"),
         ("multi_curve_audit.gp", 239, "yes"), ("curve_audit_template.gp", 204, "no"),
         ("generate_cm_curve.gp", 80, "no"), ("glv_hnp_phase1.gp", 176, "yes"),
         ("fp3_obstruction_secp256k1.gp", 200, "no"), ("igusa_f43_howe.gp", 58, "no")]
E = {"rows": []}
okE = True
for rev in ("57fa35852", "HEAD"):
    tot = 0
    for f, loc, exp in TABLE:
        b = git_show(rev, f"secp256k1_cm_audit/{f}")
        wc = b.count(b"\n") if b is not None else None
        stem = "vfcg" if f == "vfcg_experiment.gp" else f[:-3]
        has_exp = git_show(rev, f"secp256k1_cm_audit/{stem}_output.expected.txt") is not None
        tot += wc or 0
        E["rows"].append({"rev": rev, "file": f, "tex_loc": loc, "wc_l": wc,
                          "tex_expected": exp, "expected_exists": has_exp})
        if rev == "57fa35852":
            okE &= check(f"{rev} {f} LOC", loc, wc)
            okE &= check(f"{rev} {f} expected output", exp == "yes", has_exp)
    E[f"total_{rev}"] = tot
okE &= check("tex:994 Total 3305 (sum of files at 57fa35852)", 3305, E["total_57fa35852"])
okE &= check("tex:994 Total 3305 == sum of the tex rows", 3305, sum(l for _, l, _ in TABLE))
okE &= check("HEAD total equals 57fa35852 total", E["total_57fa35852"], E["total_HEAD"])
b = git_show("57fa35852", "tests/curve_audit.rs")
okE &= check("tex:1008 tests/curve_audit.rs 568 lines at 57fa35852", 568, b.count(b"\n") if b else None)
md_rows = [235, 203, 292, 254, 284, 260, 165, 171, 283, 239]
okE &= check("md twin 10.1 Total 2386 == sum of its rows", 2386, sum(md_rows))
OUT["E_loc"] = E

print("=== F. P3/P-N4: twist l-rank lemma instance counts, own j=0 point counting ===")


def counts_j0(p):
    chi = [0] * p
    for x in range(1, p):
        chi[x * x % p] = 1
    chi = [0] + [1 if chi[v] else -1 for v in range(1, p)]
    cubes = [x * x * x % p for x in range(p)]
    res = {}
    for b in range(1, p):
        s = 0
        for c in cubes:
            s += chi[(c + b) % p]
        res[b] = p + 1 + s
    return res


inst = []   # (l, p, b, nE, nEt, ordinary, r)
for p in [q for q in primes_upto(499) if q >= 5]:
    cnt = counts_j0(p)
    ordinary = p % 3 == 1
    for b, nE in cnt.items():
        nEt = 2 * p + 2 - nE
        for l in (3, 5, 7, 11, 13):
            if l in (11, 13) and not ordinary:
                continue
            r = p % l
            if r == 0:
                continue
            if nE % l == 0:
                inst.append((l, p, b, nE, nEt, ordinary, r))


def summarize(rows):
    hyp = [x for x in rows if x[6] != x[0] - 1]
    exc = [x for x in rows if x[6] == x[0] - 1]
    return {
        "total": len(rows),
        "ordinary": sum(1 for x in rows if x[5]),
        "supersingular": sum(1 for x in rows if not x[5]),
        "hyp": len(hyp), "hyp_ordinary": sum(1 for x in hyp if x[5]),
        "hyp_violations": sum(1 for x in hyp if x[4] % x[0] == 0),
        "excl": len(exc), "excl_ordinary": sum(1 for x in exc if x[5]),
        "excl_l_div_Et": sum(1 for x in exc if x[4] % x[0] == 0),
        "distinct_l_p_nE": len({(x[0], x[1], x[3]) for x in rows}),
        "distinct_l_p_nE_hyp_ordinary": len({(x[0], x[1], x[3]) for x in hyp if x[5]}),
        "skipped_r0_l7_p7": None,
    }


s357 = summarize([x for x in inst if x[0] in (3, 5, 7)])
s1113 = summarize([x for x in inst if x[0] in (11, 13)])
sall = summarize(inst)
l11 = summarize([x for x in inst if x[0] == 11])
l13 = summarize([x for x in inst if x[0] == 13])
# the r = 0 instance the tex says both scripts skip
c7 = counts_j0(7)
s357["skipped_r0_l7_p7"] = [(7, 7, b, nE) for b, nE in c7.items() if nE % 7 == 0]
classes = {}
for x in inst:
    if x[6] != x[0] - 1:
        classes.setdefault(x[0], set()).add(x[6])
OUT["F_p3"] = {"l357": s357, "l1113": s1113, "all": sall, "l11": l11, "l13": l13,
               "hyp_classes_with_instances": {k: sorted(v) for k, v in classes.items()}}
okF = all([
    check("tex:376 24,476 instances (l in {3,5,7})", 24476, s357["total"]),
    check("tex:377 8,734 ordinary", 8734, s357["ordinary"]),
    check("tex:377 15,742 supersingular", 15742, s357["supersingular"]),
    check("tex:378 8,156 in hypothesis classes, all ordinary", (8156, 8156), (s357["hyp"], s357["hyp_ordinary"])),
    check("tex:379 none has l | #E^t (hyp)", 0, s357["hyp_violations"]),
    check("tex:383-384 16,320 excluded (578 ordinary), all l | #E^t", (16320, 578, 16320),
          (s357["excl"], s357["excl_ordinary"], s357["excl_l_div_Et"])),
    check("tex:381-382 hypothesis classes with instances", {3: [1], 5: [1], 7: [1, 2, 3, 4, 5], 11: [1], 13: list(range(1, 12))},
          OUT["F_p3"]["hyp_classes_with_instances"]),
    check("tex:372-373 skipped r=0 instance (7,7,5) with #E=7", [(7, 7, 5, 7)], s357["skipped_r0_l7_p7"]),
    check("tex:387 1,802 instances l in {11,13}", 1802, s1113["total"]),
    check("tex:388 l=11 r=1 198", 198, l11["hyp"]),
    check("tex:390 l=13 1,510 hyp, 94 at r=12 all l|#E^t", (1510, 94, 94), (l13["hyp"], l13["excl"], l13["excl_l_div_Et"])),
    check("tex:391 total 26,278", 26278, sall["total"]),
    check("tex:392 10,536 ordinary", 10536, sall["ordinary"]),
    check("tex:392-393 9,864 ordinary hyp, 0 violations", (9864, 0), (sall["hyp_ordinary"], sall["hyp_violations"])),
    check("tex:394 336 distinct (l,p,#E)", 336, sall["distinct_l_p_nE"]),
    check("tex:394 249 distinct in hyp (ordinary)", 249, sall["distinct_l_p_nE_hyp_ordinary"]),
    check("tex:395 292 distinct (l in {3,5,7})", 292, s357["distinct_l_p_nE"]),
    check("tex:395-396 209 distinct hyp (l in {3,5,7})", 209, s357["distinct_l_p_nE_hyp_ordinary"]),
])

print("=== G. secp256k1 residues (tex:359-360, 400-402) ===")
P = 2 ** 256 - 2 ** 32 - 977
res = {l: P % l for l in (3, 5, 7, 11, 13)}
okG = all([
    check("tex:359-360 p mod {3,5,7,11,13}", {3: 1, 5: 3, 7: 1, 11: 7, 13: 5}, res),
    check("tex:400-401 p != l-1 mod l for odd primes l <= 29", True,
          all(P % l != l - 1 for l in (3, 5, 7, 11, 13, 17, 19, 23, 29))),
    check("tex:727 p = 1 mod 6", 1, P % 6),
    check("abstract: x^3+7 irreducible over F_p (-7 not a cube)", True, pow((-7) % P, (P - 1) // 3, P) != 1),
])

print("=== H. LLL re-run table (tex:197-205) recounted from the committed logs ===")
import re
H = {}
lines = []
for f in ("research/lll_degeneracy_rerun_20261016/logs/probes.log",
          "research/lll_degeneracy_rerun_20261016/logs/p521_hp.log"):
    lines += git_show("HEAD", f).decode("utf-8").splitlines()
pat = re.compile(r"^(\S+?)(\[(f64|HP)\])?\s+k_bits=(\d+)\s+m=\s*(\d+).*?d_seed=(0x[0-9A-F]+)(?:\s+k_seed=(0x[0-9A-F]+))?\s+→\s+(✓|✗)")
for ln in lines:
    m = pat.search(ln)
    if not m:
        continue
    curve, _, arith, kb, mm, ds, ks_, ok = m.groups()
    key = (curve, "fixed" if arith == "HP" else "f64", int(kb))
    e = H.setdefault(key, {"runs": 0, "ok": 0, "distinct": set(), "distinct_ok": set()})
    e["runs"] += 1
    e["distinct"].add(ds)
    if ok == "✓":
        e["ok"] += 1
        e["distinct_ok"].add(ds)
TAB = {("secp192k1", "f64", 144): (2, 2, 3, 3), ("secp224k1", "f64", 168): (2, 2, 3, 3),
       ("secp256k1", "f64", 192): (3, 3, 6, 6), ("P-256", "f64", 192): (3, 3, 6, 6),
       ("brainpoolP256r1", "f64", 192): (1, 1, 1, 1), ("P-384", "f64", 288): (3, 3, 4, 4),
       ("brainpoolP384r1", "f64", 288): (3, 3, 4, 4), ("P-521", "f64", 384): (0, 3, 0, 4),
       ("P-521", "fixed", 384): (3, 3, 3, 3)}
okH = True
for k, v in TAB.items():
    e = H.get(k, {"runs": 0, "ok": 0, "distinct": set(), "distinct_ok": set()})
    got = (len(e["distinct_ok"]), len(e["distinct"]), e["ok"], e["runs"])
    okH &= check(f"rerun {k} (rec/distinct, rec/runs)", v, got)
okH &= check("no log row outside the table", set(TAB), set(H))
OUT["H_lll_rerun"] = {str(k): {"runs": v["runs"], "ok": v["ok"], "distinct": sorted(v["distinct"])} for k, v in H.items()}

OUT["summary"] = {"A_p4": okA, "B_second": okB, "C_lll": okC, "D_controls_all_failed": OUT["D_controls_all_failed"],
                  "E_loc": okE, "F_p3": okF, "G_secp": okG, "H_rerun": okH}
print("=== SUMMARY ===")
print(json.dumps(OUT["summary"], indent=1))
Path(__file__).with_name("papers_checks.json").write_text(json.dumps(OUT, indent=1, default=list))

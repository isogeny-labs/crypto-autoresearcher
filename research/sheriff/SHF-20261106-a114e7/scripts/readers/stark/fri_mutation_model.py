#!/usr/bin/env python3
"""Independent toy-field model of the FRI gates of crypto:src/zk/stark.rs
fri_check (as read at crypto 3a7a0f98a) and the stark_v2 depth gate, with a
mutation matrix.  Written by the sheriff `stark` reader of SHF-20261106-a114e7.
It shares no code with the producer and does not execute any crypto code.

What it models (oracle / IOP level: a Merkle opening is modelled as reading
the committed table, so the Opening gate never fires for these provers):

  gate order (as in check_gated + fri_check):
    depth  : len(layer_roots) == log2 n + 1                 -> "Shape"
    shape  : folds <= log2 L                               -> "FriShape"
    final  : last root == root(beta copies of final_const)  -> "FinalLayer"
    per query, per layer k < folds:
      fold_int : layer k+1 opened value == fold(layer k pair, alpha_k)
      fold_last: fold(layer folds-1 pair, alpha) == final_const
      (both return "Fold" in the producer's FriReject, so a test cannot
       tell them apart)

Field: Goldilocks p = 2^64 - 2^32 + 1 (two-adicity 32, generator 7).  The
coset shift is 7 (a generator, so outside every 2-power subgroup).

Run:  python3 -I fri_mutation_model.py  > fri_mutation_model.out
It also writes fri_mutation_model.json next to itself.
"""
import hashlib
import json
import math
import os
import random

P = 2**64 - 2**32 + 1
GEN = 7


def inv(a):
    return pow(a % P, P - 2, P)


def root_of_unity(order):
    assert (P - 1) % order == 0
    w = pow(GEN, (P - 1) // order, P)
    assert pow(w, order, P) == 1 and (order == 1 or pow(w, order // 2, P) != 1)
    return w


def coset(L, shift=GEN):
    w = root_of_unity(L)
    return [shift * pow(w, i, P) % P for i in range(L)]


def poly_eval(coeffs, x):
    acc = 0
    for c in reversed(coeffs):
        acc = (acc * x + c) % P
    return acc


def H(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p)
    return h.digest()


def table_root(table):
    return H(b"layer", b"".join(v.to_bytes(8, "big") for v in table))


def draw(transcript):
    h = H(bytes(transcript))
    transcript.extend(h)
    return int.from_bytes(h, "big") % P


def fold_pair(fx, fnx, x, alpha):
    """Producer's formula (stark.rs:613-616): ((f(x)+f(-x)) + a*(f(x)-f(-x))*x^-1)/2."""
    s = (fx + fnx) % P
    d = (fx - fnx) % P
    return (s + alpha * d % P * inv(x)) % P * inv(2) % P


def fold_layer(table, domain, alpha):
    half = len(table) // 2
    nxt = [fold_pair(table[i], table[i + half], domain[i], alpha) for i in range(half)]
    nd = [domain[i] * domain[i] % P for i in range(half)]
    return nxt, nd


# ---------------------------------------------------------------- prover

def commit(table0, domain0, final_size, transcript0, tamper=None):
    """Honest FRI commit (fri_commit_to), then an optional tamper of the
    layer tables with roots re-committed and the transcript re-derived
    (fri_from_layers + fri_transcript_after), like the producer's knobs."""
    t = bytearray(transcript0)
    layers, domains, roots = [list(table0)], [list(domain0)], [table_root(table0)]
    while len(layers[-1]) > final_size:
        t.extend(roots[-1])
        a = draw(t)
        nxt, nd = fold_layer(layers[-1], domains[-1], a)
        layers.append(nxt)
        domains.append(nd)
        roots.append(table_root(nxt))
    if tamper is not None:
        layers = tamper(layers)
        roots = [table_root(l) for l in layers]
    final_const = layers[-1][0]
    return {"layers": layers, "roots": roots, "final_const": final_const}


def transcript_after(transcript0, roots, final_const):
    t = bytearray(transcript0)
    for r in roots[:-1]:
        t.extend(r)
        draw(t)
    t.extend(b"fri_final" + roots[-1] + final_const.to_bytes(8, "big"))
    return t


def positions(t, q, L):
    out = []
    for j in range(q):
        t.extend(j.to_bytes(8, "big"))
        h = H(bytes(t))
        t.extend(h)
        out.append(int.from_bytes(h, "big") % L)
    return out


def open_queries(fri, pos_list):
    """fri_query: (main, sibling) value at each layer < folds."""
    out = []
    for p0 in pos_list:
        pos, ops = p0, []
        for k in range(len(fri["layers"]) - 1):
            lay = fri["layers"][k]
            half = len(lay) // 2
            pm = pos % len(lay)
            ps = pm + half if pm < half else pm - half
            ops.append((pm, lay[pm], ps, lay[ps]))
            pos = min(pm, ps)
        out.append((p0, ops))
    return out


# ---------------------------------------------------------------- verifier

def verify(fri, queries, domain0, n, transcript0, q,
           depth_gate=True, final_check=True, fold_int=True, fold_last=True):
    L = len(domain0)
    roots = fri["roots"]
    if depth_gate and len(roots) != int(math.log2(n)) + 1:
        return "Shape"
    folds = len(roots) - 1
    if folds > int(math.log2(L)):
        return "FriShape"
    fc = fri["final_const"]
    if final_check and roots[folds] != table_root([fc] * (L >> folds)):
        return "FinalLayer"
    # caller: query positions from the transcript after the commitment
    pos_exp = positions(transcript_after(transcript0, roots, fc), q, L)
    if [p for p, _ in queries] != pos_exp:
        return "Deep(positions)"
    t = bytearray(transcript0)
    alphas = []
    for r in roots[:folds]:
        t.extend(r)
        alphas.append(draw(t))
    for p0, ops in queries:
        if len(ops) != folds:
            return "FriShape"
        size, x, pos = L, domain0[p0], p0
        for k, (pm, vm, ps, vs) in enumerate(ops):
            half = size // 2
            sib = pos + half if pos < half else pos - half
            # Opening gate (oracle model): the value is the committed one.
            if pm != pos or ps != sib or fri["layers"][k][pm] != vm or fri["layers"][k][ps] != vs:
                return "Opening"
            folded = fold_pair(vm, vs, x, alphas[k])
            if k + 1 < len(ops):
                if fold_int and ops[k + 1][1] != folded:
                    return "Fold"
            else:
                if fold_last and folded != fc:
                    return "Fold"
            x = x * x % P
            if pos >= half:
                pos -= half
            size = half
    return "accept"


# ---------------------------------------------------------------- scenarios

def run():
    rng = random.Random(20261106)
    n, beta, q = 8, 4, 20
    L = n * beta
    dom = coset(L)
    t0 = b"toy-fri/statement"
    low = [rng.randrange(P) for _ in range(n)]          # degree < n
    low_tab = [poly_eval(low, x) for x in dom]
    high = [rng.randrange(P) for _ in range(L)]          # degree L-1: models a false statement's D
    high_tab = [poly_eval(high, x) for x in dom]

    def zero_tail(layers):
        return [layers[0]] + [[0] * len(l) for l in layers[1:]]

    def shift_layer1(layers):
        return [l if k != 1 else [(v + 1) % P for v in l] for k, l in enumerate(layers)]

    def const_final(layers):
        return layers[:-1] + [[12345] * len(layers[-1])]

    def build(table, final_size, tamper=None):
        fri = commit(table, dom, final_size, t0, tamper)
        pos = positions(transcript_after(t0, fri["roots"], fri["final_const"]), q, L)
        return fri, open_queries(fri, pos)

    scenarios = {
        # name: (proof, expected first gate of the full verifier, in producer tests?)
        "H_honest_low_degree": (build(low_tab, beta), "accept", "positive tests"),
        "F0_honest_fold_of_false_D": (build(high_tab, beta), "FinalLayer",
                                      "rejects_deep_quotient_not_low_degree: Fri(FinalLayer)"),
        "F1_zero_tail": (build(high_tab, beta, zero_tail), "Fold",
                         "rejects_fri_fold_inconsistency (part 1): Fri(Fold)"),
        "F2_shift_layer1_true_stmt": (build(low_tab, beta, shift_layer1), "Fold",
                                      "rejects_fri_fold_inconsistency (part 2): Fri(Fold)"),
        "F3_honest_folds_const_final": (build(high_tab, beta, const_final), "Fold",
                                        "NOT in producer tests (isolates the last-layer fold branch)"),
        "F4_overfold_to_1": (build(high_tab, 1), "Shape",
                             "rejects_over_folded_fri_at_depth_gate: Shape (size 1)"),
        "F5_overfold_to_beta_half": (build(high_tab, beta // 2), "Shape",
                                     "rejects_over_folded_fri_at_depth_gate: Shape (size beta/2)"),
    }
    mutants = {
        "none": {},
        "no_depth_gate": {"depth_gate": False},
        "no_final_layer_root_check": {"final_check": False},
        "no_fold_intermediate": {"fold_int": False},
        "no_fold_last": {"fold_last": False},
        "no_fold_both": {"fold_int": False, "fold_last": False},
    }
    matrix = {}
    for sname, ((fri, qs), expect, where) in scenarios.items():
        matrix[sname] = {"expected_full": expect, "producer_test": where, "by_mutant": {}}
        for mname, kw in mutants.items():
            matrix[sname]["by_mutant"][mname] = verify(fri, qs, dom, n, t0, q, **kw)
    # Producer's assertions modelled: the test analogues and their asserted outcome.
    test_scen = ["H_honest_low_degree", "F0_honest_fold_of_false_D", "F1_zero_tail",
                 "F2_shift_layer1_true_stmt", "F4_overfold_to_1", "F5_overfold_to_beta_half"]
    killed = {}
    for mname in mutants:
        fails = [s for s in test_scen
                 if matrix[s]["by_mutant"][mname] != matrix[s]["expected_full"]]
        killed[mname] = fails
    # Extra control from the producer test: check_gated(depth_gate=false) on the size-1
    # proof returns Ok, and on the honest false proof returns Fri(FinalLayer).
    depth_off_control = {
        "F4_overfold_to_1_depth_off": matrix["F4_overfold_to_1"]["by_mutant"]["no_depth_gate"],
        "F0_depth_off": matrix["F0_honest_fold_of_false_D"]["by_mutant"]["no_depth_gate"],
    }

    # ---------------- blind re-derivation: fold formula and depth count
    alpha = rng.randrange(P)
    fcoef = [rng.randrange(P) for _ in range(n)]
    fe, fo = fcoef[0::2], fcoef[1::2]
    ok_formula = True
    ok_stated = True
    for x in dom[: L // 2]:
        fx, fnx = poly_eval(fcoef, x), poly_eval(fcoef, (-x) % P)
        x2 = x * x % P
        want = (poly_eval(fe, x2) + alpha * poly_eval(fo, x2)) % P
        stated = ((fx + fnx) * inv(2) + alpha * (fx - fnx) % P * inv(2 * x)) % P
        ok_formula &= fold_pair(fx, fnx, x, alpha) == want
        ok_stated &= stated == want
    depth = {}
    for (nn, bb) in [(4, 4), (8, 2), (8, 4), (16, 8), (32, 2)]:
        LL = nn * bb
        d = coset(LL)
        res = {}
        for label, deg in [("deg_n_minus_1", nn - 1), ("deg_n", nn)]:
            c = [rng.randrange(P) for _ in range(deg + 1)]
            tab = [poly_eval(c, x) for x in d]
            dd = list(d)
            const_after = None
            for k in range(int(math.log2(LL)) + 1):
                if len(set(tab)) == 1:
                    const_after = k
                    break
                tab, dd = fold_layer(tab, dd, rng.randrange(P))
            res[label] = const_after
        depth[f"n={nn},beta={bb}"] = {
            "folds_to_constant": res,
            "rederived_layer_roots": int(math.log2(nn)) + 1,
            "final_layer_size": LL >> int(math.log2(nn)),
            "producer_gate_n.trailing_zeros()+1": (nn & -nn).bit_length() - 1 + 1,
        }
    # any table folds to one value with log2 L folds (why final_size < beta is dangerous)
    any_tab_one = len(build(high_tab, 1)[0]["layers"][-1]) == 1

    # ---------------- epsilon_field arithmetic (stark_v2.rs:100-115)
    r = int("73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001", 16)
    lr = math.log2(r)
    worst = None
    for logn in range(1, 32):
        for logb in range(1, 33 - logn):
            nn, LL = 2**logn, 2**(logn + logb)
            k = nn
            e = (k + 1) / 2**lr + (2 * nn + k) / (2**lr - nn - LL) + (5 + logn) * LL / 2**lr
            e2 = (k + 1) / 2**lr + (2 * nn + k) / (2**lr - nn - LL) + (5 + logn) * LL**2 / 2**lr
            if worst is None or e > worst[0]:
                worst = (e, e2, logn, logb)
    eps = {"log2_r": round(lr, 3), "worst_eps_field_log2_L_over_r": round(math.log2(worst[0]), 2),
           "same_point_L2_over_r_log2": round(math.log2(worst[1]), 2),
           "at_log2n_log2beta": [worst[2], worst[3]]}

    out = {
        "field": "Goldilocks 2^64-2^32+1", "n": n, "beta": beta, "q": q,
        "matrix": matrix, "producer_test_assertions_failing_per_mutant": killed,
        "depth_gate_off_controls": depth_off_control,
        "rederivation": {
            "producer_fold_equals_fe(x^2)+alpha*fo(x^2)": ok_formula,
            "stated_formula_(f(x)+f(-x))/2+alpha(f(x)-f(-x))/(2x)_equals_same": ok_stated,
            "depth": depth,
            "any_table_folds_to_one_value_at_final_size_1": any_tab_one,
        },
        "eps_field": eps,
    }
    return out


def main():
    out = run()
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "fri_mutation_model.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    m = out["matrix"]
    muts = list(next(iter(m.values()))["by_mutant"].keys())
    print("FRI mutation matrix (first gate fired; 'accept' = verifier accepts)")
    print("scenario".ljust(30) + "".join(x[:14].ljust(16) for x in muts))
    for s, row in m.items():
        print(s.ljust(30) + "".join(row["by_mutant"][x].ljust(16) for x in muts))
    print()
    for s, row in m.items():
        print(f"{s}: expected(full)={row['expected_full']}  producer test: {row['producer_test']}")
    print()
    print("Producer-test assertions that FAIL under each mutant (empty = mutant SURVIVES the tests):")
    for k, v in out["producer_test_assertions_failing_per_mutant"].items():
        print(f"  {k}: {v if v else 'SURVIVES'}")
    print("depth-gate-off controls:", out["depth_gate_off_controls"])
    print()
    print("Re-derivation:", json.dumps(out["rederivation"], indent=1))
    print("eps_field:", out["eps_field"])


if __name__ == "__main__":
    main()

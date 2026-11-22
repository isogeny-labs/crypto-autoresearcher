"""analyze.py — render results.json into markdown tables for RESULTS.md."""
import json
import math

R = json.load(open("results.json"))
F = R["frozen"]

print("frozen:", F["frozen_utc"])
print("\n== setup ==")
seen = set()
for c in R["cells"]:
    key = (c["bits"], c["seed"], c["arm"])
    if key in seen:
        continue
    seen.add(key)
    print(f"| bits {c['bits']} | p={c['p']} | a={c['a']}, b={c['b']} "
          f"| #E={c['nE']} = {c['cofactor']}·{c['n']} | arm {c['arm']} N={c['N']} "
          f"| |B_raw|={c['abs_B_raw']} |B_G|={c['abs_B']} | nT={c['nT']} |")

print("\n== dictionary + rates ==")
hdr = ("curve,p,arm,m,|B|,nT,frac_dec,lambda,naive,poisson,"
       "frac/naive,frac/pois,mean_r,mean_r/lambda,dict,hook-literal,converse")
print(hdr)
dict_tot = dict_pass = hook_tot = hook_hit = 0
viol_tot = hit_tot = expl_tot = 0
for c in R["cells"]:
    if "m" not in c:
        continue                     # charter rows handled in section 3
    m = c["m"]
    b = c["abs_B"]
    n = c["n"]
    lam = b ** m / n
    naive = min(1.0, lam)
    pois = 1 - math.exp(-lam / math.factorial(m))
    frac = c["frac_dec"]
    dp, dt = c["dict_pass"], c["dict_tot"]
    ht, hh = c["hook_tot"], c["hook_hit"]
    if m != 5:
        dict_tot += dp
        dict_pass = dict_tot - (dict_tot - dp)
    conv = c.get("converse")
    cstr = ""
    if conv:
        hit_tot += conv["hits"]
        expl_tot += conv["explained"]
        viol_tot += conv["violations"]
        cstr = f"{conv['explained']}/{conv['hits']} explained, viol {conv['violations']}"
    print(f"p={c['p']} arm={c['arm']} m={m}: b={b} nT={c['nT']} "
          f"frac={frac:.4f} lam={lam:.3g} naive={naive:.3g} pois={pois:.3g} "
          f"frac/naive={(frac/naive if naive else 0):.3f} "
          f"frac/pois={(frac/pois if pois else 0):.3f} "
          f"mean_r={c['mean_r']:.2f} r/lam={(c['mean_r']/lam if lam else 0):.3f} "
          f"dict {dp}/{dt} hook {hh}/{ht} conv[{cstr}] wit_bad={c.get('wit_bad')}")
# overall dictionary pass: recompute cleanly
main_cells = [c for c in R["cells"] if "m" in c]
dict_pass = sum(c["dict_pass"] for c in main_cells)
dict_tot = sum(c["dict_tot"] for c in main_cells)
hook_hit = sum(c["hook_hit"] for c in main_cells)
hook_tot = sum(c["hook_tot"] for c in main_cells)
print(f"\nDICTIONARY overall: {dict_pass}/{dict_tot} pass")
print(f"HOOK-LITERAL control (phi(+Q), d=6 distinct cols): {hook_hit}/{hook_tot} hits")
print(f"CONVERSE: hits {hit_tot}, explained {expl_tot}, violations {viol_tot}")

print("\n== charter: x-window vs generic sets ==")
main = {}
for c in R["cells"]:
    if "m" in c:
        for m in ([c["m"]] if "charter" not in c else []):
            main[(c["p"], c["arm"], c["m"])] = c
for c in R["cells"]:
    ch = c.get("charter")
    if not ch:
        continue
    ref = main[(c["p"], c["arm"], ch["m"])]
    print(f"p={c['p']} arm={c['arm']} m={ch['m']} b={c['abs_B']}: "
          f"x-window frac={ref['frac_dec']:.4f} mean_r={ref['mean_r']:.2f} | "
          f"{ch['kind']} frac={ch['frac_dec']:.4f} mean_r={ch['mean_r']:.2f} "
          f"| dict {ch['dict_pass']}/{ch['dict_tot']}")
import json, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
pub = json.load(open("instances.json"))
rows = []
for g in pub["groups"]:
    p, N, B = int(g["p"]), int(g["N"]), g["B"]
    rho = math.sqrt(math.pi * N / 4); rho_plain = math.sqrt(math.pi * N / 2)
    ic_fixed = 4 * B ** 2                       # linear-algebra term m*B^2, m=4
    coef = math.factorial(4) / 2 ** 4           # 1.5
    Tstar = (rho - ic_fixed) / (coef * p / B ** 3)   # break-even oracle cost (group ops) vs matched rho
    nbase = B / 2                               # x-values on curve
    exp_extra = (nbase ** 4 / 24) * 8 / (N / 2) # expected x-quadruples decomposing a random x_R (heuristic)
    vieta_vol = 4*B * 6*B**2 * 4*B**3 * B**4
    rows.append(dict(log2p=g["log2p"], p=str(p), N=str(N), B=B, log2B=math.log2(B), rho_steps_pi_N_over_4=rho, log2_rho=math.log2(rho),
        rho_plain_pi_N_over_2=rho_plain, p_quarter=p ** .25, generic_mitm_T_B2=B ** 2, break_even_T=Tstar, log2_break_even_T=math.log2(Tstar),
        log_ratio_T_over_p14=math.log(Tstar, p) - 0.25, hit_prob_random_target=exp_extra, vieta_box_volume_over_p=vieta_vol / p))
json.dump(rows, open("rho_reference.json", "w"), indent=1)
print("| log2 p | N | B | rho steps sqrt(pi N/4) | log2 rho | plain sqrt(pi N/2) | p^(1/4) | generic MITM T=B^2 | break-even T* | hit prob per random R | Vieta box vol / p |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['log2p']} | {r['N']} | {r['B']} | {r['rho_steps_pi_N_over_4']:.4g} | {r['log2_rho']:.2f} | {r['rho_plain_pi_N_over_2']:.4g} | {r['p_quarter']:.4g} | {r['generic_mitm_T_B2']:.4g} | {r['break_even_T']:.4g} | {r['hit_prob_random_target']:.3g} | {r['vieta_box_volume_over_p']:.3g} |")
fig, ax = plt.subplots(figsize=(6.4, 4.2))
k = [r["log2p"] for r in rows]
ax.plot(k, [r["log2_rho"] for r in rows], "o-", label="matched rho  sqrt(pi N/4)")
ax.plot(k, [math.log2(r["p_quarter"]) for r in rows], "s--", label="p^(1/4)  (target scale)")
ax.plot(k, [math.log2(r["break_even_T"]) for r in rows], "^-", label="break-even oracle cost T*")
ax.plot(k, [math.log2(r["generic_mitm_T_B2"]) for r in rows], "d:", label="generic 4-SUM MITM  B^2")
ax.set_xlabel("log2 p"); ax.set_ylabel("log2 (group operations)"); ax.legend(fontsize=8); ax.grid(alpha=.3)
ax.set_title("SA-15 reference: oracle cost needed at B=p^(1/5), m=4")
fig.tight_layout(); fig.savefig("fig_reference.png", dpi=140)

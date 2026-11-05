#!/usr/bin/env python3
"""Read pinned BSGS inputs, independently check the curve, and exercise controls."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

REV = "7c028ce9ccdec6c1ee7d4c2b3b60120ed3dcbd9e"
ROOT = Path(__file__).resolve().parents[4]
BASE = "examples/runbooks/toy-ecdlp-bsgs/"
FILES = ("README.md", "curve.json", "solve.py", "check.py", "trial-plan.json", "runbook.yaml")


def pinned(name):
    return subprocess.check_output(["git", "show", f"{REV}:{BASE}{name}"], cwd=ROOT)


def prime(n):
    if n < 2:
        return False
    return all(n % d for d in range(2, math.isqrt(n) + 1))


def ec_add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u and (y + v) % p == 0:
        return None
    slope = ((3*x*x + a) * pow(2*y, p-2, p) if P == Q
             else (v-y) * pow(u-x, p-2, p)) % p
    X = (slope*slope-x-u) % p
    return X, (slope*(x-X)-y) % p


def ec_mul(k, P, p, a):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, p, a)
        P = ec_add(P, P, p, a)
        k >>= 1
    return R


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {"exit": p.returncode, "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip().splitlines()[-1] if p.stderr else ""}


def main():
    data = {name: pinned(name) for name in FILES}
    curve = json.loads(data["curve.json"])
    plan = json.loads(data["trial-plan.json"])
    p, a, b, n = (curve[k] for k in ("p", "a", "b", "n"))
    G = tuple(curve["G"])
    point_count = 1
    for x in range(p):
        rhs = (x*x*x + a*x + b) % p
        point_count += 1 if rhs == 0 else 2 if pow(rhs, (p-1)//2, p) == 1 else 0
    result = {"source_commit": REV,
              "source_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in data.items()},
              "curve": {"p_prime_trial_division": prime(p), "n_prime_trial_division": prime(n),
                        "discriminant_nonzero": (4*a*a*a + 27*b*b) % p != 0,
                        "discriminant_mod_p": (-16*(4*a*a*a + 27*b*b)) % p,
                        "G_on_curve": (G[1]*G[1]-G[0]**3-a*G[0]-b) % p == 0,
                        "G_nonidentity": True, "point_count_legendre": point_count,
                        "nG_identity_independent_flt": ec_mul(n, G, p, a) is None,
                        "m": math.isqrt(n-1)+1,
                        "m_squared": (math.isqrt(n-1)+1)**2}}
    result["plan_binding"] = {
        "frozen": plan["frozen"],
        "source_hashes_match": all(plan["source_sha256"][BASE+name] == result["source_sha256"][name]
                                   for name in ("curve.json", "solve.py", "check.py")),
        "readme_hash_matches": plan["specification_sha256"] == result["source_sha256"]["README.md"],
        "seed_derivation_matches": all(
            int(t["argv"][t["argv"].index("--seed")+1]) ==
            int(hashlib.sha256(f"toy-ecdlp-bsgs/seed/{i}".encode()).hexdigest()[:8],16)
            for i,t in enumerate(plan["trials"][:12],1)),
        "trial_count": len(plan["trials"]),
        "all_check_argv_match": all(
            t["check_argv"][-2:] == [t["argv"][t["argv"].index("--mode")+1],
                                  t["argv"][t["argv"].index("--seed")+1] if "--seed" in t["argv"] else
                                  t["argv"][t["argv"].index("--k")+1] if "--k" in t["argv"] else "none"]
            for t in plan["trials"])}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name, raw in data.items():
            (tmp/name).write_bytes(raw)
        spec = importlib.util.spec_from_file_location("pinned_solve", tmp/"solve.py")
        solver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(solver)
        spec = importlib.util.spec_from_file_location("pinned_check", tmp/"check.py")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        E = checker.Curve(p,a,b)
        control_points = [None,G,(G[0],(-G[1])%p),ec_mul(2,G,p,a),ec_mul(n-1,G,p,a)]
        result["arithmetic_crosscheck"] = []
        for P in control_points:
            for Q in control_points:
                got = solver.add(P,Q,p,a)
                ref = ec_add(P,Q,p,a)
                projP = (0,1,0) if P is None else (*P,1)
                projQ = (0,1,0) if Q is None else (*Q,1)
                projective = E.to_affine(E.add(projP,projQ))
                result["arithmetic_crosscheck"].append(got == ref == projective)
        trials = []
        for trial in plan["trials"]:
            argv = list(trial["argv"])
            mode = argv[argv.index("--mode")+1]
            value = (argv[argv.index("--seed")+1] if "--seed" in argv else
                     argv[argv.index("--k")+1] if "--k" in argv else "none")
            folder = tmp/trial["id"]
            folder.mkdir()
            cmd = [sys.executable,str(tmp/"solve.py"),"--trial-id",trial["id"],"--mode",mode,
                   "--curve",str(tmp/"curve.json"),"--run-dir",str(folder)]
            if mode == "search":
                cmd.extend(["--seed",value])
            elif mode == "known-k":
                cmd.extend(["--k",value])
            execution = run(cmd)
            check = run([sys.executable,str(tmp/"check.py"),str(folder),str(tmp/"curve.json"),mode,value])
            raw = json.loads((folder/"raw-result.json").read_text()) if (folder/"raw-result.json").exists() else None
            trials.append({"id":trial["id"],"mode":mode,"value":value,"solver_exit":execution["exit"],
                           "checker_exit":check["exit"],"checker_stdout":check["stdout"],
                           "status":raw.get("status") if raw else None,
                           "k_found":raw.get("k_found") if raw else None,
                           "counts":{k:raw.get(k) for k in ("m","baby_steps","giant_steps","group_ops","setup_ops")} if raw else None})
            if trial["id"] == "c-known-k":
                control = folder
                original = raw
        result["frozen_trials"] = trials
        def mutate(label, changes):
            raw = dict(original)
            raw.update(changes)
            (control/"raw-result.json").write_text(json.dumps(raw))
            verdict = run([sys.executable,str(tmp/"check.py"),str(control),str(tmp/"curve.json"),"known-k","123456"])
            return {"control":label,"checker_exit":verdict["exit"],"checker_stdout":verdict["stdout"]}
        result["forged_controls"] = [
            mutate("group_ops_plus_one", {"group_ops":original["group_ops"]+1}),
            mutate("giant_steps_plus_one_and_matching_group_ops",
                   {"giant_steps":original["giant_steps"]+1,"group_ops":original["group_ops"]+1}),
            mutate("fabricated_setup_ops", {"setup_ops":987654}),
            mutate("fabricated_valid_counts_and_result", {"setup_ops":987654,"elapsed_ms":0,"verified":True})]
        synthetic = {"schema":"example.toy_ecdlp_bsgs.result.v1", "trial_id":"synthetic",
            "mode":"known-k", "seed":None,"k_input":123456,
            "curve":{key:curve[key] for key in ("p","a","b","n","G")},
            "Q":list(ec_mul(123456,G,p,a)),"status":"solved","k_found":123456,"verified":True,
            "m":1024,"baby_steps":1024,"giant_steps":123456//1024+1,
            "group_ops":1024+123456//1024+1,"setup_ops":987654,"elapsed_ms":0}
        synthetic_dir=tmp/"synthetic-no-solver"
        synthetic_dir.mkdir()
        (synthetic_dir/"raw-result.json").write_text(json.dumps(synthetic))
        (synthetic_dir/"manifest.yaml").write_text("trial_id: synthetic\nstatus: solved\n")
        verdict=run([sys.executable,str(tmp/"check.py"),str(synthetic_dir),str(tmp/"curve.json"),"known-k","123456"])
        result["forged_controls"].append({"control":"synthetic_no_solver_execution",
            "checker_exit":verdict["exit"],"checker_stdout":verdict["stdout"]})
        for k in (0,1,1023,1024,1025,n-1,n):
            folder = tmp/f"boundary-{k}"
            folder.mkdir()
            execution=run([sys.executable,str(tmp/"solve.py"),"--trial-id",f"boundary-{k}",
                           "--mode","known-k","--k",str(k),"--curve",str(tmp/"curve.json"),
                           "--run-dir",str(folder)])
            raw=json.loads((folder/"raw-result.json").read_text()) if (folder/"raw-result.json").exists() else None
            check=run([sys.executable,str(tmp/"check.py"),str(folder),str(tmp/"curve.json"),"known-k",str(k)]) if raw else None
            result.setdefault("boundary_controls",[]).append({"k":k,"solver_exit":execution["exit"],
                "solver_stderr":execution["stderr"],"status":raw.get("status") if raw else None,
                "k_found":raw.get("k_found") if raw else None,"checker_exit":check["exit"] if check else None})
        # Search a tiny nonsingular composite-order curve for an outside-subgroup point.
        outside = None
        for aa in range(17):
            for bb in range(17):
                if (4*aa**3+27*bb**2)%17 == 0:
                    continue
                points=[(x,y) for x in range(17) for y in range(17) if (y*y-x*x*x-aa*x-bb)%17 == 0]
                for g in points:
                    subgroup={None}
                    R=None
                    for order in range(1,len(points)+2):
                        R=ec_add(R,g,17,aa)
                        if R is None:
                            break
                        subgroup.add(R)
                    if order < len(points)+1:
                        q=next((q for q in points if q not in subgroup),None)
                        if q is not None:
                            found, counts=solver.bsgs(g,q,order,17,aa)
                            outside={"p":17,"a":aa,"b":bb,"group_order":len(points)+1,
                                     "G":g,"G_order":order,"Q":q,"Q_on_curve":True,
                                     "Q_outside_subgroup":True,"bsgs_found":found,"counts":counts}
                            break
                if outside: break
            if outside: break
        result["outside_subgroup_control"] = outside
        # Count actual affine add invocations in BSGS, independent of reported metadata.
        Q=ec_mul(123456,G,p,a)
        old_add=solver.add
        calls=[]
        def counted_add(P,Q,p,a):
            calls.append(1)
            return old_add(P,Q,p,a)
        solver.add=counted_add
        found,counts=solver.bsgs(G,Q,n,p,a)
        result["count_trace_known_k"]={"found":found,"actual_add_invocations":len(calls),
            "reported_group_ops_plus_setup_ops":counts["baby_steps"]+counts["giant_steps"]+counts["setup_ops"],
            "reported_giant_steps":counts["giant_steps"],"actual_giant_add_invocations":counts["giant_steps"]-1}
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

# Exact W3 for the original n50 polynomial03 system

For the fixed `fresh-n50-poly-03` original system, an independent Python closure calculation found

\[\dim W_3(F)=8,130,\qquad \dim B_{\le3}=20,876,\qquad
  \operatorname{codim}W_3(F)=12,746,\qquad 1\notin W_3(F).\]

The [source](verify_n50_poly03_d3_rank.py) constructs the 50 quadratic Boolean equations directly from
\(S_3(X,Y,z)=a_6+(zX)^2+(zY)^2+(XY)^2+zXY\), using the exact named field modulus, target and 25-element polynomial basis. It then computes the degree-three closure with Python integer rows and a low-pivot multiplication queue. This is independent of the native closure and quotient-lift implementations. The queue terminates after 196 distinct low pivots; Proposition 1.8 of the [theorem dossier](../semaev-m2-last-fall-degree/theorem-dossier.md) proves that this termination gives the exact closure. A three-variable ideal and contradictory-ideal control passed before the named run.

The direct equations contain 19,042 masks across 50 equations. A separate cross-check compared every mask against the existing checker’s Möbius-interpolation descent and found exact equality ([record](validation/n50-poly03-independent-w3-001/equations-crosscheck.json), SHA-256 `789e23a90aff1f7c15522704ad85f59847ce79abfcab46db1f0ba9a72e381b53`).

The retained 33,568,640-byte D3 map has SHA-256 `d5e27dbe345b6a5f3100f41d6be1df4702be2de0a52b07dbfec3907d5425a94d`. The separate `cert_check.py` accepted it at D=3: 20,876 monomials, onto dimension 12,746, all generators killed, closed kernel, and nonzero image of one. Thus `W3` is contained in its kernel. The kernel has dimension `20,876-12,746=8,130`, matching the independent exact rank, so **the retained D3 seed kernel equals W3** for this named input.

Both read-only checks used pushed source revision `356c4f8d4cec72db3cc086948c3ae0b81e4490be`, one attempt each, a 600-second wall and CPU cap, and a 4 GiB address-space cap. The independent rank check exited zero in 2.234 seconds; the certificate check exited zero in 0.670 seconds. The write-once [rank started](validation/n50-poly03-independent-w3-001/started.json), [rank stdout](validation/n50-poly03-independent-w3-001/stdout.txt), [rank finished](validation/n50-poly03-independent-w3-001/finished.json), [certificate started](validation/n50-poly03-independent-w3-001/certificate-check.started.json), [certificate stdout](validation/n50-poly03-independent-w3-001/certificate-check.stdout.txt), and [certificate finished](validation/n50-poly03-independent-w3-001/certificate-check.finished.json) records preserve commands, hashes, timeouts and outcomes. Both stderr files are empty and are retained beside them.

This closes the independent D3 seed exactness premise for a source-audited D3-to-D4 quotient lift. It does not by itself prove that the retained D4 seed is exact W4: that requires a check that its lift reached the Proposition 1.9 fixed point, or an independent direct W4 rank of 212,547. It does not decide W5 or establish an LFD-six lower bound.

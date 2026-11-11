# Exact W3 for the original n51 polynomial00 system

For the fixed six-solution candidate `fresh-n51-poly-00`, the independently constructed Boolean equations and direct closure calculation give

\[\dim W_3(F)=10,970,\qquad \dim B_{\le3}=23,479,\qquad
  \operatorname{codim}W_3(F)=12,509,\qquad 1\notin W_3(F).\]

The [source](verify_n51_poly00_d3_rank.py) directly expands the binary Semaev formula at the named 26-element polynomial basis, using Python field multiplication and the Python-integer degree-three closure routine. It shares no native closure or quotient-lift code. The closure queue processed 254 distinct low pivots; Proposition 1.8 of the [theorem dossier](../semaev-m2-last-fall-degree/theorem-dossier.md) proves exactness at termination. The direct equations contain 18,011 masks across 51 equations. A separate cross-check matched every mask against the existing checker's Möbius-interpolation descent ([record](validation/n51-poly00-independent-w3-001/equations-crosscheck.json), SHA-256 `46a8a4a3384362b9cbfae3d0c7f7fd81062cc966818ddf7b9c08c259389d7470`).

The retained 37,002,936-byte D3 quotient map has SHA-256 `2b1b26fe59b2a5489dfd666b9753344943a14f19af41fe90835d1d80b1a7fd5c`. The independent `cert_check.py` accepted it: 23,479 monomials, onto dimension 12,509, all generators killed, closed kernel, and nonzero image of one. Therefore W3 is contained in its kernel. The kernel dimension `23,479-12,509=10,970` equals the independent exact rank, proving **the retained D3 seed kernel equals W3** for this named original input.

Both read-only checks used pushed revision `2692c601518b9d0a28de39d400be4507d2a92b2f`, one attempt each, a 600-second wall and CPU cap, and a 4 GiB address-space cap. The direct rank check exited zero in 3.185 seconds; the certificate check exited zero in 0.763 seconds. The exact commands, source/input hashes, stdout, empty stderr and terminal receipts are in [validation/n51-poly00-independent-w3-001](validation/n51-poly00-independent-w3-001/).

This establishes the exact D3 seed premise for a D3-to-D4 lift audit on the n51 six-solution target. It does not prove that the accepted 45,615-coordinate D4 kernel is exact W4, that its solution evaluations factor through that kernel, or that a seventh D5 quotient direction exists. Those are separate proof gates for an LFD-six lower bound.

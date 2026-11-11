# Checked affine slice of the n51 six-solution original system

For the named original `fresh-n51-poly-00` instance, the trace identity of Theorem 2.1(c) is exactly

\[
\ell_0=1+a_0+b_0.
\]

The [source](derive_n51_poly00_affine_span.py) computed `Tr(a6/z^2)=1` and `Tr(v_i)=1` only for the first polynomial-basis vector `v_0=1`. It then found an explicit XOR of **26 original coordinate generators** equal to this three-term affine polynomial. The indices are in the [witness](validation/n51-poly00-affine-witness-001.json), SHA-256 `c37ca7f727b716acac28463f2db58126588e994a71eb6a66c8c18015f0273985`. The direct formula's full original-system equations are saved as [n51-poly00-original-independent.sys](validation/n51-poly00-original-independent.sys), SHA-256 `dd7a724b4161da605952808c373eeeb2a904fe7aae65699b932f19bf2585674b`.

The separate [checker](check_n47_affine_witness.py) rebuilt every generator by the independent `cert_check.py` Möbius descent, matched the saved input equation sets, and checked that the witness XOR equals `1+a_0+b_0`. It accepted with exit 0. Changing the witness's constant bit to zero made the checker reject it with exit 1. The exact source and input hashes, checker output, commands and mutation result are in the [readback](validation/n51-poly00-affine-check-001.json), SHA-256 `bac9a21eab9934cba83ebdb6fc279011f895f8f4dcc9fe609e2e64c1c5ef211b`. The witness generator was pushed at revision `c8bb9ae0db` before these outputs were produced.

Because `1+a_0+b_0` belongs to the span of the original generators, every Boolean solution satisfies `b_0=a_0+1`; restriction to that 51-variable slice gives a bijection of zero sets and therefore retains the exact count **six**. Proposition 2.5b of the theorem dossier identifies the bounded closures under this internal affine slice and transfers a separately checked degree-five quotient back to the original system with the **same quotient dimension**. In particular, a checked sliced D5 quotient of dimension at least seven would prove original-system LFD at least six by Proposition 1.4.

This is a proved slice relation and independent finite check, not a projected D4 map or D5 run. The retained original 45,615-coordinate D4 map still needs bounded projection, unit-representative rebase, independent acceptance and an actual D5 memory profile before a sliced producer is proposed. The relation itself does not lower the original D5 envelope numerically without that profile.

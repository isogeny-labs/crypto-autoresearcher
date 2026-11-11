# Affine rank of the n51 polynomial-00 original generators

The saved 52-variable, 51-generator system has one known affine combination,
`1+a_0+b_0`, checked in `N51-POLY00-AFFINE-SLICE-WITNESS.md`. Its quadratic
coefficient matrix over GF(2) has rank exactly **50**. The explicit
[50-by-50 minor](validation/n51-poly00-quadratic-minor-001.json) lists 50
generator indices and 50 quadratic monomial masks. Its SHA-256 is
`107e2f11efcab9c693c8d39a922d2b75628cbd5bdf3175ae348585514188ace4`.

The [checker](check_n51_poly00_affine_rank.py) reads the pinned original
`.sys` (SHA-256
`dd7a724b4161da605952808c373eeeb2a904fe7aae65699b932f19bf2585674b`),
checks the saved generator XOR is exactly `1+a_0+b_0`, and independently
computes the minor's rank. It returned
`unique_affine_generator_relation`, quadratic rank 50, minor order 50,
and affine kernel dimension 1. Replacing one minor column by the valid
quadratic mask `0x3` made the checker reject a singular minor with exit 1;
duplicating one column was also rejected with exit 1. A displayed nonzero affine combination gives
quadratic rank at most 50; the nonsingular minor gives rank at least 50.
Hence the *only* affine polynomial in the linear span of these 51 generators
is a scalar multiple of `1+a_0+b_0`.

This closes a narrow target-selection question: a second independent affine
slice cannot be obtained by another XOR of the original coordinate
generators. The [quotient-map affine check](check_n51_poly00_affine_quotient_rank.py)
then read the retained D3 and D4 maps, verified their full SHA-256 digests,
and found affine image rank **52 of 53** in both. The machine-readable
[readback](validation/n51-poly00-affine-quotient-rank-001.json) has SHA-256
`4047852458abe1eec083d542fba46a0ec4424baa84255a9bf0f7be93bdd14a7c`.
The sole affine kernel basis vector in each map is again `1+a_0+b_0`.

The D3 map has already been proved to have kernel exactly W3 by an
independent direct closure rank and certificate check
(`N51-POLY00-W3-EXACTNESS.md`), so this proves there is no additional affine
relation in W3. The accepted D4 quotient map has a kernel *containing* W4;
exact W4 is still conditional, but containment suffices here: its
one-dimensional affine kernel bounds the affine part of W4 from above,
while the displayed relation bounds it from below. Thus no second affine
slice can be justified by an affine relation in W4 either. This does not
exclude one appearing first in W5, and gives no degree-five quotient or
LFD-six bound. The next direct route for this six-solution target is
the already frozen D4 projection/rebase and D5 profile, once its separate
spending and admission gates are met.

Replay:

```sh
python3 analysis/semaev-degree-five-quotient-lift/check_n51_poly00_affine_rank.py \
  analysis/semaev-degree-five-quotient-lift/validation/n51-poly00-original-independent.sys \
  analysis/semaev-degree-five-quotient-lift/validation/n51-poly00-affine-witness-001.json \
  analysis/semaev-degree-five-quotient-lift/validation/n51-poly00-quadratic-minor-001.json

python3 analysis/semaev-degree-five-quotient-lift/check_n51_poly00_affine_quotient_rank.py \
  /home/ec2-user/fall-degree-data-20261029/n50n51-cascade-local-001/fresh-n51-poly-00-D5-cascade01/attempt-001/degree3.bin \
  --degree 3
python3 analysis/semaev-degree-five-quotient-lift/check_n51_poly00_affine_quotient_rank.py \
  /home/ec2-user/fall-degree-data-20261029/n50n51-bounded-d4-concurrent-001/fresh-n51-poly-00-D5-cascade01-bounded-D4-001/attempt-001/degree4.bin \
  --degree 4
```

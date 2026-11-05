# Draft known-result entries (NOT filed)

Not filed in `crypto-autoresearcher`: these are unreviewed claims from one session, KR ids must come from
`tools/allocate_id.py` (not run), source refs must be `KN-LIT-*` entries with a `verification_state`, and
status changes belong to the Coordinator under AGENTS.md. Target path:
`knowledge/frontiers/ecdlp/index-calculus/KR-IC-<allocated>.yaml`. Fields follow the schema of
`KR-IC-401ebf.yaml`.

## Draft A (replaces withdrawn KR-2): counting-algorithm crossover is encoding-independent

```yaml
id: KR-IC-<allocate>
area: index-calculus
kind: known_negative
status: proven        # necessary-condition argument at unit constants; real constants measured separately
title: Subexponential #k-CNF counting cannot beat rho for hashed-factor-base ECDL below l about 2^254
claim: >-
  Let a relation oracle count solutions of a Boolean network with N variables in time 2^(N/sqrt(log2 N)),
  all hidden constants set to 1, as m-slot hashed-factor-base index calculus (Akshima et al. v0.2) uses it.
  Beating rho (2^(l/2)) needs per-attempt exponent below (1/2 - 1/m) l, since about 2^(l/m) relations are
  needed. Encodings with full l-bit coordinate unknowns have N >= m l, so the condition forces
  sqrt(log2(m l)) > 2 m^2/(m-2), minimised at m = 4 with log2(4 l) > 256, i.e. l > 2^254. Index-valued
  unknowns do not escape: one vertex for the group law pads to s ~ l^(10/9) edges (E ~ 0.6 l, above 0.5 l) or
  is accessed by evaluation only (2^l evaluations); split vertices carry l-bit partial sums and return to
  N >= m l. Measured constants make it worse: the compiled prime-field network has 1,500-3,100 variables per
  bit per slot, giving counting exponent 1,500-5,500 times rho's at l = 40..131 (m = 2..4). The proof's own
  size floors (Bochum/OpenAI: networks >= 2^(2^17), u0 = 0 below; Kintali N0 >= 2^(3*10^7); Anthropic n > 10^10,000) mean ECCp-131 networks (654,523
  variables, 2 slots) run the exact-summation fallback.
setting: {field: prime, slots: 2..4}
sources:
  - {ref: KN-LIT-<bochum, to be created>, locator: "Thm 4, Lemmas 1, 11, 13, footnote 4", verification_state: full_text_read}
  - {ref: KN-LIT-caa51d, locator: "App. D.1 / D.4.2 (u0 = floor(b/2^17))", verification_state: full_text_read}
forecloses:
  - re-encoding the hashed-factor-base network (index unknowns, x-only Semaev, other arithmetic) to beat rho below l ~ 2^254
  - tensor-contraction counting for point decomposition at 40-131 bits
internal:
  - {ref: LEAD-ICB-decomposition-encoding-and-sat, relation: extends, note: "obstruction survives the Fourier encoding that escapes the Tseitin-count argument"}
  - {ref: cryptanalysis/docs/hashed-ecdl-audit-20261029/README.md, relation: rederived, note: "crossover at log2 b = 256 under unit constants"}
open: []
dominated_by: null
added: '2026-10-31'
superseded_by: null
```

## Draft B: leading-form degree of regularity is presentation-dependent

(Unchanged from `REVIEW.md` addendum A1. Applies to the adjacent `prime_sat_*` thread, not to the hashed
tensor algorithm. Only the weaker `d_reg <= G+1` is currently recorded, in DEC-20261029-0857a9.)

## Draft C: odd-s grouped theorem (reviewer-derived, outside accepted scope of DEC-20261029-0857a9)

(Statement and proof sketch in `REVIEW.md` addendum A2: d_reg(F_grouped, raw) = s+2 for odd s >= 3,
d_reg(F_bit) = s + (s+1)/2 + 1, gap floor(s/2); hand-checked at s = 3. Not re-read against the producer's
`grouped-proof.md`.)

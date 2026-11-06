# Hecke/CM class points and Prym: prioritization, lead entries, Q-attachment design

Date: 2026-11-06. Status: draft for owner review. Nothing here is committed or run.

## 0. Evidence status

| Claim in the brief | Found in repos? |
| --- | --- |
| D79 support-eight collector: rank 39, 40 logs replayed, 25-35 sources (median 28) | **Not found** (searched crypto, crypto-autoresearcher, cryptanalysis `origin/main` at last fetch; crypto fetch did not complete) |
| Support-seven: rank 39 in 3 of 8 classes | Not found |
| Query-order holdout, -12.87% probes | Not found (the only "12.87" hit is unrelated, `speedup-search-followup-20261006`) |
| Prym: 4,587,520 attempts, 97/67 witnesses -> 13/9 equations, ranks 13/15 and 9/15 | Not found |
| Hecke/CM relations on X_0(11) with finite rank | **Found, adjacent**: `cryptanalysis` `experiments/ecdlp-hecke-d39-holdout-20261026/RESULT.md` (D_K=-39, f=6, X_0(11)/F_367, 64 class points, 48 verified Hecke relations, rank 40, Atkin-Lehner rank 52; labelled exploratory, not an independent holdout) |
| Earlier verdict on this family | **Found**: crypto-autoresearcher `docs/reports/ecdlp-special-structure-leads-20261031/family-C-lifting.md` C4: Hecke/Atkin-Lehner relation sources tried on X_0(11)/F_367 with "no IC advantage"; evidence under `LEAD-ICP-lattice-ic-relation-construction` (open_blocked) |

Everything below that depends on the D79 / Prym numbers is **conditional on those records**. Please point me at the branch or PR holding them before any of it is quoted.

## 1. Prioritization

1. **Hecke/CM class points: keep, focused and exploratory.** Full-rank finite relation sets on X_0(11) are measured, not conjectural (the D39 record is the verified neighbour). Exploratory because there is no target attachment and no end-to-end cost.
2. **Prym-assisted: below Hecke/CM, diagnostic only.** Duplication is explained exactly, the matrices determine no individual atom log, and attaching a prescribed Q is missing. No further compute until a Q-attachment mechanism is proposed.
3. **Neither is a solver claim.** No arbitrary-target prime-field solver, no P-256/secp256k1 applicability. Per the success criterion, report the gap to matched rho as distance remaining, not pass/fail.
4. **Prior-art caveat the brief omits.** The special-structure survey already rates Hecke relation sources on X_0(11)/F_367 as "no IC advantage". The new work must say what it changes against that verdict (known-log points with subgroup projection, a rank-completion collector), or it duplicates a closed lead.

## 2. Atlas entries to propose (not yet filed)

Run `python3 tools/lead_atlas.py --match` first; the atlas is 128 paths behind its 2026-10-29 review, so fold the delta before filing.

- **LEAD-ICP-hecke-cm-class-point-rank-completion** (proposed `open_next_step`)
  - Object: CM class-point sets on X_0(11) with anchored, subgroup-projected known logs; rank-completion collector; query-order reduction.
  - Evidence: D79 records (unlocated) and D39 control (found).
  - Obstruction: no costed map from arbitrary public Q to the known-log points; `candidate_id` and `target_online_ms` deliberately unset.
  - Next action: the Q-attachment experiment in section 3.
  - Relation: sub-lead of, or distinct from, `LEAD-ICP-lattice-ic-relation-construction`; decide after reading its record.
- **LEAD-ICP-prym-witness-relation-diversity** (proposed `open_blocked`)
  - Object: Prym-assisted witnesses on two toy curves.
  - Evidence: 97 and 67 accepted witnesses reducing to 13 and 9 distinct equations (unlocated).
  - Obstruction: duplication explained; no atom log identified; Q not attached.
  - Next action: none until a Q-attachment idea exists.

## 3. Q-attachment experiment (design sketch, class: comparison, needs `controlled-experiment` protocol before data)

**Question.** Given a public target Q in a prime-order subgroup G, can Q be expressed through the known-log class points at a cost that, added to setup and collection, can be priced against matched rho?

**Arms (same instrument, interleaved, derived seeds):**
- A: Hecke/CM collector + candidate attachment step (to be specified by the proposer; the brief leaves it open).
- B: matched Pollard rho at the same group size.
- C: A/A repeat of A for the noise floor.
- Positive control: a target Q constructed as a known combination of class points, so the detector must succeed.
- Negative control: Q drawn uniformly from G with no relation to the class points.

**Costs charged (all arms, rho included, at 0 / 0.1 / 1 GAE per unnamed native op, AGENTS.md section 5a):**
- setup: CM discriminant search, curve and class-point construction, anchoring;
- collection: sources per class (report median and range), probes;
- linear algebra for the rank-39 system;
- attachment: `target_online_ms` and any per-Q work, set only once measured.

**Outputs.** Gap to matched rho per row across the pricing band; rank ordering reported only where it holds across the whole band. Visuals per `research-visuals`; leaderboard and `benchmarks/` rows only after a `VALIDATION.json` with replay certificate, validator report and matched-rho reference.

**Pre-requisites not met in this session:** Conductor task, `.resume/RESUME.md` checkpoint to S3, isolab-eks route frozen by the experiment director, task card relayed to the mechanical executor. This container has about 300 MB free and cannot build or run.

## 4. Open items

- Locate the D79, support-seven, query-order and Prym records.
- Complete the `crypto` fetch (it was killed by the disk limit) and re-run the searches.
- Fold the atlas delta, then file the two leads.

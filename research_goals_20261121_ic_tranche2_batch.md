# Research Goals 2026-11-21 — Tranche 2: four more index-calculus blind spots, two metrology gates

**Date anchor:** 2026-11-21

**Status:** Planning record. Five proposals and two proposed governance gates.
**Nothing here is evidence.** No experiment is claimed complete except the
G32-001 pilot marked as such. All proposals are subject to NoveltyGate
(G30-028) and to the two gates proposed in §3, which this batch argues should
exist precisely because G31 produced two false claims that survived drafting.

**Provenance:** operator question "what else" (2026-11-21), answered against
the G30 program, G31 batch, `knowledge/`, and the corpus index. Screening
method is the same as the G31 batch §0: claim of "ignored" tested by grep, not
by memory.

---

## 0. Screening performed

| Idea | Corpus | Program | Verdict |
|---|---|---|---|
| Parametrized / preimage factor bases | Partially: McGuire–Mueller (`eprint 2017/1262`) describes Petit–Kosters–Messeng as *"the first working case for curves defined over prime fields"* (F_{4206593}, 4975 s/GB). The PKM paper itself is **not** in the corpus. | No goal tests a parametrized base; G30-010's battery tests "geometries" but no membership-by-algebraic-condition arm. | Unstaffed, with a real literature data point unreproduced |
| Isogeny-graph smoothness via Deuring | Deuring-correspondence literature abundant (e.g. `KN-LIT-075`, `KN-LIT-5078`); none framed as index calculus with a small-degree isogeny factor base | G30-019 (walk collisions), G30-020 (transfer boundary) — adjacent, not this framing | Unframed |
| Sign / Kummer bookkeeping (2^m) | Symmetrized-variant literature exists (`faugere_huot_joux_renault_vitse_2014_symmetrized`); Kummer-line arithmetic standard in implementation | No goal audits whether density/cost statements charge sign resolution | Unstaffed metrology |
| One-pass sumset / "GPU sieve" | — | Nothing closes it | Unclosed, cheap |
| Target-side large primes / list decomposition | Large-prime variation in corpus (`KN-LIT-164`) for hyperelliptic | G31-003 covers coordinate-side large primes only | Half-covered |

**Not claimed as a discovery:** `CLM-ECDLP-BLIND-DESCENT` is campaign-critical,
status `not_attempted`, and no G30/G31 goal staffs it (the G30 file says so
itself). It is listed here only so that the tranche record does not read as if
the descent gap had been overlooked twice.

---

## G32-001: Parametrized (preimage-defined) factor bases — reproduce the only working prime-field case, then measure the degree question

**Cluster:** 04 FACTORBASE / 02 GROEBER. **Type:** reproduction + measurement.
**Depends on:** G30-004 (a real d_reg backend — the blocker), G30-025.
**Gates:** a scoped statement about whether algebraic membership changes the
solving degree at fixed base size (feeds KN-OPEN-002).

**The construction.** A factor base can be defined by an *algebraic membership
condition* rather than an order condition: fix a low-degree rational map
f : P¹ → P¹ and a small target set T ⊂ P¹, and let

  B(f, T) = { P ∈ E(F_p) : f(x(P)) ∈ T },   |B| ≈ deg(f)·|T|.

Membership is then one low-degree equation in x, so the decomposition system
S_{m+1}(x₁…x_m, x_Q) = 0 is solved *together with* the constraints
f(x_i) ∈ T — a system with structure, in contrast to the window base whose
constraint is a set-membership predicate with no algebraic content. The claimed
payoff is not a larger base but a cheaper *solver*: the system can be reduced
modulo the low-degree membership relations before elimination. This is the
idea McGuire–Mueller attributes to Petit–Kosters–Messeng, and the program has
never reproduced or refuted it.

**WP0 (mandatory, blocking):** obtain and read the PKM paper — the exact map,
target-set and system must come from the source, not from this description.
The description above is a reconstruction and is labelled as such.

**WP1 (feasible without Sage):** toy measurement of the *sumset* side. For
f(x) = x^d with d ∈ {2, 3} and T a small set of d-th powers, build B(f,T) at
|B| ∈ {12, 20, 30} and compare, at equal |B| and on the same targets:
(a) decomposition density, against the |B|^m/(m!·#G) prediction;
(b) sumset structure |B+B|, |2B|, against a **negation-matched** random base
(the G31-001 replication's null — not the uniform null);
(c) the window base at the same size. This isolates whether algebraic
membership creates non-generic sumset structure at all.

**WP2 (blocked on G30-004):** solving-degree comparison. For each T-tuple,
reduce S_{m+1} modulo the membership relations and measure first-fall degree
and true solving degree against a support-matched semi-regular null. **This is
the question that decides the idea**, and it cannot be answered with sympy at
toy scale in reasonable time; it requires the F4/F5 backend G30-004 was
supposed to commission.

**Falsification:** if WP1 shows pullback bases are statistically ordinary
against the negation-matched null *and* WP2 shows no solving-degree deficit at
equal |B|, the idea is closed with a certificate that also explains the PKM
data point as a small-scale artefact of its own parameter range. If WP2 shows a
deficit, that is a KN-OPEN-002 finding independent of whether any attack
follows.

**Pilot outcome (2026-11-21, WP1 only, unreviewed):** see §4.

---

## G32-002: Isogeny-graph smoothness via Deuring — the only other smoothness notion on E(F_p)

**Cluster:** 07 TRANSFER / 08 BARRIERS. **Type:** speculative probe whose
expected output is a closure certificate. **Depends on:** G30-019, G30-020.

**The idea.** Height gives one ordering on E(F_p)'s lifts (G31-002). The
Deuring correspondence gives a second structure: E(F_p) is (up to the usual
caveats) the class group of a maximal order in B_{p,∞}, and "smooth" would mean
a product of small-prime-degree isogenies. Relation search becomes path
decomposition in the ℓ-isogeny graph, with a factor base of small-degree
isogenies and linear algebra over the class group.

**Why it is probably closed, stated up front.** The class-group action *is* the
DLP; short paths are the isogeny-path problem, believed hard at ~p^{1/2}
(meet-in-the-middle), and G30-019 already measures the non-backtracking
collision exponent against that baseline. So the expected outcome is negative.
The reason to staff it anyway is that it is the only *structurally different*
notion of smoothness available over a prime field, and a negative stated as a
theorem-shaped closure ("no factor base of bounded-degree isogenies yields
relation density above X") is durable, whereas the current situation is a gap
in the taxonomy.

**Scope / kill:** toy ℓ-isogeny graphs at 12–20 bits (G30-019 machinery);
measure whether the set of compositions of ≤ m small-prime isogenies covers
enough of the class group to admit relations at fixed m, against a
degree-matched random walk null. Kill if coverage matches random-walk coverage
at every tested m, or if the required m grows with p faster than log p.

**Novelty screen:** the isogeny-path / Deuring literature is large and adjacent
(including SIDH-attack literature on path finding); the claim screened is only
"index calculus with an isogeny factor base", and the screen must confirm that
no such framing already exists before this is filed as anything but a closure.

---

## G32-003: Sign / Kummer bookkeeping — make the 2^m factor explicit in every density and cost statement

**Cluster:** 01 BASELINE (metrology). **Type:** audit + instrument.

**The issue.** x-coordinates determine points only up to sign. Every relation
density formula of the form |B|^m/(m!·#G) silently assumes the signs work out.
In practice either (i) the solver returns x-tuples and the 2^m sign assignments
must be searched, (ii) the relation is taken in the Kummer line E/± and the
linear system is over a double cover with a consistency condition, or (iii) the
base is chosen with one representative per ±-orbit and the count is halved.
Each choice changes the relation count by a factor in [1, 2^m] and the
linear-algebra size by up to 2.

**Deliverable:** for each relation engine in the 05 RELATIONS cluster
(G30-013, G30-015, G31-003's arm), state which convention it uses, whether its
density formula charges the sign search, and the corrected factor. Then add a
mandatory field to the experiment contract: `sign_convention` ∈ {full, kummer,
one_rep} with the corresponding density multiplier. This is a G30-001-level
correction, not a new attack.

**Kill:** if the audit finds every engine already charges it, the goal reduces
to the contract field and closes in one pass.

---

## G32-004: No one-pass sieving — any full-sumset method costs Ω(p)

**Cluster:** 08 BARRIERS. **Type:** two-paragraph closure.

**Statement.** For any base B ⊆ G of size N and any m ≥ 1, computing the
complete m-fold sumset (or the full decomposition table for all targets)
requires Ω(p) work: the sumset lives in a group of order ~p and a cyclic
convolution over it costs Ω(p log p) with FFT and Ω(p) information-theoretically
in the dense representation. Hence "build the entire relation table on a GPU"
is dominated by rho by a factor ~p^{1/2}, unconditionally, for every base and
every m.

**Why it matters:** this idea recurs whenever relation search gets expensive,
and a one-paragraph lemma with the information-theoretic argument kills it
before a budget is spent. **Caveat to state:** the bound applies to computing
the *whole* table; sparse/structured convolution that computes only the needed
slice is not covered and would be a genuine result.

---

## G32-005: Target-side large primes / list decomposition

**Cluster:** 05 RELATIONS. **Type:** counting-law extension. **Depends on:** G31-003, G30-014.

**The issue.** G31-003 varies the *coordinate* side (two factors above the
window). The dual is to allow the target to be missed by a small error:
decompose Q − T for T in a small error set E (points of small order, or a second
window around Q). Density multiplies by |E|.

**Scope.** Extend the B1 enumerator calculus with the error-set term; measure on
the G31-003 ladder; state the trade-off honestly (|E| multiplies density and
also multiplies descent work, since each target needs |E| attempts). Charge both.

**Kill:** if the charged ratio never falls below 1, close as counting-law
completeness rather than as a separate engine.

---

## 3. Two proposed governance gates (the durable output of this tranche)

G31 produced two false claims that survived drafting and were caught only by
doing the work: the "S₄ unpublished" novelty claim (S₆ is the published record)
and the "unconditional" characteristic-0 barrier (the free-solver fallacy).
Both are process failures, and both are cheap to gate.

**Gate A — computation-of-record.** Before any "first / unpublished / largest"
language, the screen must find the *largest recorded object of that kind*, not
merely search for the specific claimed object. Precedent for how to word the
record: "largest computed X is Y (source)". One search, per claim.

**Gate B — null exchangeability.** Every experiment contract that compares a
structured object against a random control must state the structured object's
invariances and require the control to share them. G31-001 is the worked
example: x-window bases are negation-closed, the uniform null was not, and the
resulting bias was 0.7–6.1 pp in the false-negative direction — large enough to
manufacture an entire "alive" signal and to suppress a real one.

Both gates are proposed as additions to the G30-001 metrology standard, not as
research goals; they need a Coordinator decision, not an experiment.

---

## 4. G32-001 pilot outcome (WP1 only)

**Executed 2026-11-21.** Script and raw results:
`notes/g32-001-pullback-pilot-20261121/` (`pilot.py`, `pilot_results.json`).
Setup: p ∈ {4099, 8191, 12289, 16381}, one curve per prime, base size matched
to **exactly N = 24** for every family, 400 random targets shared across
families, decomposition-tuple counts computed exactly by iterated convolution
(m = 3, 4). Families: window, pullback with f = x², pullback with f = x² + c,
random negation-closed, plus a uniform random contrast.

| p | family | m3 mean/λ | m3 rate | 1−e^{−λ} | m4 mean/λ | \|B+B\| | \|B+B+B\| | pair max | pairs at O |
|---|---|---|---|---|---|---|---|---|---|
| 4099 | window | 0.995 | 0.438 | 0.963 | 1.113 | 279 | 1820 | 24 | 24 |
| 4099 | pullback x² | 0.980 | 0.417 | 0.963 | 0.972 | 285 | 1848 | 24 | 24 |
| 4099 | pullback x²+c | 1.115 | 0.470 | 0.963 | 0.975 | 283 | 1837 | 24 | 24 |
| 4099 | rand neg-closed | 0.983 | 0.410 | 0.963 | 1.026 | 277 | 1822 | 24 | 24 |
| 4099 | uniform **contrast** | 0.923 | 0.455 | 0.963 | 0.991 | 295 | 1999 | **6** | **0** |
| 8191 | window | 1.155 | 0.260 | 0.816 | 0.995 | 287 | 2083 | 24 | 24 |
| 8191 | pullback x² | 0.976 | 0.247 | 0.816 | 1.102 | 281 | 2000 | 24 | 24 |
| 8191 | pullback x²+c | 1.077 | 0.273 | 0.816 | 1.005 | 283 | 2024 | 24 | 24 |
| 8191 | rand neg-closed | 0.938 | 0.255 | 0.816 | 0.970 | 283 | 2064 | 24 | 24 |
| 12289 | window | 0.986 | 0.165 | 0.673 | 0.980 | 289 | 2206 | 24 | 24 |
| 12289 | pullback x² | 1.261 | 0.190 | 0.673 | 0.981 | 289 | 2118 | 24 | 24 |
| 12289 | pullback x²+c | 1.008 | 0.170 | 0.673 | 1.002 | 289 | 2190 | 24 | 24 |
| 12289 | rand neg-closed | 0.794 | 0.155 | 0.673 | 0.976 | 285 | 2084 | 24 | 24 |
| 16381 | window | 0.998 | 0.125 | 0.572 | 1.025 | 289 | 2193 | 24 | 24 |
| 16381 | pullback x² | 0.848 | 0.133 | 0.572 | 1.040 | 289 | 2230 | 24 | 24 |
| 16381 | pullback x²+c | 0.989 | 0.122 | 0.572 | 1.001 | 285 | 2192 | 24 | 24 |
| 16381 | rand neg-closed | 1.201 | 0.122 | 0.572 | 0.883 | 279 | 1986 | 24 | 24 |

**Findings.**

- **No family-specific density or sumset structure.** Across all four primes,
  m3 mean/λ spans 0.79–1.26 for the negation-closed families with no
  consistent ordering (window is highest at one prime, lowest at another);
  |B+B| spans 277–289 and |B+B+B| 1986–2230 for all of them. The pullback
  bases are **ordinary** at tested size and power.
- **The negation diagnostic reproduces the G31-001 mechanism exactly**, and
  this is the most transferable row of the table: every negation-closed family
  has pair-max = |B| = 24, all concentrated at O (24 pairs at O), while the
  uniform contrast has pair-max 4–6 and **zero** pairs at O. Two bases of
  identical size and identical density can therefore differ by a factor ~4 in
  pair concentration, purely from ±-closure. Any yield comparison that does not
  match this invariant is measuring the null, not the base.
- **What this does not establish.** The deciding question for parametrized
  bases is the *solver* side (WP2): whether the low-degree membership
  relations reduce the degree of regularity at fixed |B|. Density being generic
  is exactly what one expects if the solver is the only channel for an
  advantage, so this pilot neither supports nor refutes the idea.
- **Power.** N = 24, 400 targets, four curves, no pre-registered MDE — a
  ~10% density effect would be visible, a ~3–5% one would not. This is a
  pilot; it must not be cited as a test.

**Honest verdict:** WP1 says "algebraic membership buys nothing on the counting
side", which was foreseeable from the dimension count and is now measured
rather than assumed. WP2 remains the open question and remains blocked on
G30-004.

---

## 5. Sequencing

1. **G32-003** (sign audit) — cheap, pure metrology, corrects every other cost
   statement.
2. **G32-004** (Ω(p) closure) — two paragraphs, closes a recurring idea.
3. **G32-005** (target-side errors) — completes G31-003's counting law.
4. **G32-001 WP2** — blocked on G30-004; schedule when the backend lands.
5. **G32-002** — last: speculative, and its value is the closure certificate.

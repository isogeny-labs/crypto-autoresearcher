# Proposed next assumption-boundary tranche

Status: **triage only**.  None of the rows below is a finding, a literature
refutation, a protocol vulnerability, or a discharged formal target.  Before a
row becomes a target, its primary source and exact quantifiers must be frozen
and the purported inference must be shown to occur in the source being audited.

The ranking combines consequence, availability of a small Lean countermodel,
and risk of accidentally attacking a claim the cited literature does not make.

| Rank | Candidate | Finite attack and repair | Scope boundary / source gate |
| ---: | --- | --- | --- |
| 1 | `ZK-SEPARATION` | An always-accept verifier with a fixed transcript separates completeness and simulability from soundness or knowledge soundness.  Repair by defining and proving the four games separately. | Does not show any deployed protocol unsound or prove a composition theorem.  Freeze the exact ZK, soundness, and proof-of-knowledge definitions used by the protocol first. |
| 2 | `SCHNORR-GROUP-SCALAR-BRIDGE` | In additive `ZMod 6`, `G = 2` has nontrivial scalar kernel, so a group equality cannot be cancelled back to unique scalars.  Repair with exact subgroup order, membership, and injectivity of `a |-> a*G`. | Does not supply a forking theorem, extractor runtime, ROM/QROM theorem, or encoding check.  Re-read Schnorr/Pointcheval--Stern and the concrete group's subgroup requirements. |
| 3 | `FS-TRANSCRIPT-ENCODING` | Raw concatenation aliases `("ab","c")` and `("a","bc")`; absent protocol tags permit an encoding-level cross-protocol alias.  Repair with canonical fixed-width or length-prefixed fields, fixed order, public-input binding, and domain tags; prove encoder injectivity or a decode/encode law. | Does not exhibit a hash collision or implementation bug and does not establish ROM security.  Bind the statement to a concrete Fiat--Shamir serialization specification. |
| 4 | `KZG-TOXIC-WASTE` | In a scalarized verification equation, known trapdoor `tau` permits a proof scalar of the form `(c-y)/(tau-z)` when the denominator is nonzero.  Repair requires hidden/discarded trapdoor, degree-bounded SRS, subgroup/pairing correctness, and the precise binding assumption/game. | Does not break honestly generated KZG or recover `tau`.  Freeze signs, pairing orientation, and the exact q-SDH-style statement from the KZG primary source (`KN-LIT-3122`) before formalization. |
| 5 | `SURVIVAL-TAIL-EXPECTATION` | Almost-surely finite stopping time with tail `Pr[T>n]=1/(n+1)` still has divergent expectation.  Repair by proving the truncated tail-sum identity, its limiting/integrability step, and then a geometric upper tail from an explicit lower hazard; account for per-attempt cost separately. | Does not show that xedni has the required conditional hazard, independence, or real-cost bound.  Bind to JKSST's exact repetition/runtime wording and a probability API/reference. |
| 6 | `POLLARD-RHO-RANDOM-MAP` | Constant, identity, and single-cycle maps on the same finite set have incompatible collision/cycle behavior.  Repair by sampling an actual random map or imposing a precise mixing model, then separately proving that a collision yields a usable nonzero relation. | Does not invalidate Pollard rho or diagnose a concrete partition walk.  Re-read Pollard and random-mapping/Markov sources (`KN-LIT-369623`). |
| 7 | `FINITE-ROM-FORKING-LOSS` | A finite adversary that succeeds only for one distinguished oracle answer has positive one-run success but zero success on every distinct-challenge replay.  Repair needs an oracle table, query index, fixed tape/prefix, reprogram point, distinctness, abort accounting, and exact loss. | Does not show Fiat--Shamir insecure or transfer to QROM.  Freeze the precise Pointcheval--Stern or later tight/corrected forking lemma and constants. |
| 8 | `GGM-TRANSPARENT-ENCODING` | Encoding `ZMod q` elements by their scalars makes discrete logs readable, showing why arbitrary representations are outside a generic-group lower bound.  Repair with the random injective encoding and permitted group/equality oracles, followed by the exact query bound. | Does not imply real curve encodings leak logs or contradict Shoup.  Re-read Shoup 1997 (`KN-LIT-011`) before fixing the model. |
| 9 | `AGM-REPRESENTATION-PREMISE` | An opaque external/hash-to-group source may return a group element without a coefficient vector relative to prior handles; an ordinary interface accepts it while a strict algebraic interface cannot certify it.  Repair by requiring and checking representations for every produced element. | This is a model-interface test, not an AGM counterexample or protocol attack.  Re-read Fuchsbauer--Kiltz--Loss (`KN-LIT-6945`) and critique/instantiation work first. |
| 10 | `QROM-REPROGRAMMING-BOUNDARY` | Measuring a superposition oracle query changes a later phase-sensitive experiment, so classical observe/replay/reprogram steps cannot simply be copied.  Repair by defining the oracle channel and invoking a precise measure-and-reprogram or one-way-to-hiding theorem with its loss. | Does not prove a quantum attack or an impossibility result.  New primary-source retrieval is required before any exact target is frozen. |

## Recommended order

The next formal tranche should be ranks 1--5.  The first three have tiny
countermodels and close common proof-interface gaps.  The KZG row is
high-consequence but must wait for an exact primary equation.  The survival
row directly extends the one-shot target without pretending that its hazard
premise has been proved for xedni.

Ranks 6--7 should follow a reusable finite probability/oracle-game library.
Ranks 8--10 are valuable model-boundary controls, but their source-fidelity
risk is high enough that no “disproof” label is justified before primary-source
freeze and adversarial semantic review.

Runners-up for later source freeze are `HASH-TO-FIELD-MOD-BIAS`,
`ECDLP-RANDOM-SELF-REDUCTION`, and `PLONK-DENOMINATOR-ZERO`.

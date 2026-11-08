# Semaev decomposition certificate: independent fidelity review

Claim: `THM-SEMAEV-FALL1-LEMMA-3`. Reviewed source commit:
`6a0eb9665191e35690b4ff5ebd91c63561e09ec4`. Named declaration:
`CryptoResearch.Semaev.decidable_validDecomposition` in
`formal/CryptoResearch/Semaev/Certificate.lean` (SHA-256
`aa022e4829eefc2cbe9ac05cbeb39f81e9e3eaa8147e2e41e9d718f11976bd89`).
The target specification and dependency pins are in `input-bindings.json`.

## Scoped result

The blind reviewer independently derived the finite decision procedure and
exact iff predicate from the mathematical card. The source reviewer found the
Lean declaration faithful to the **typed nonsingular-point** predicate, and
the raw-coordinate lemma faithful to `K × K` inputs under `W.IsElliptic`.
The archived hosted sweep's exact-target receipt and all 122 reviewed input
bindings pass the machine reviewer's consistency checks. A fresh forced hosted
Lean run is in progress as [run 42446577502](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42446577502);
its outcome must be read back before assigning a fresh machine pass.

The operational interpretation that the theorem already independently checks
serialized producer certificates needs revision. The reviewed module does not
bind the input bytes, concrete field, curve, spanning family, tuple, and target
to the Lean arguments or execute a corresponding checker on the bound record.
These are six separately stated bridge obligations in the J2 report, not a
counterexample to the mathematical theorem. The type `W.Point` also restricts
affine points to nonsingular points; prose about all equation points on a
potentially singular curve needs that qualification.

| Claim boundary | Machine status | Semantic fidelity | Review outcome |
| --- | --- | --- | --- |
| Typed finite decomposition over the declared span and Mathlib point group | Historical exact-target receipt consistent; fresh run pending | Faithful at nonsingular-point scope (J1, J2) | Inconclusive pending fresh machine evidence and independence repair |
| Raw `K × K` coordinates under `W.IsElliptic` | Source inspected; fresh raw controls pending | Faithful at typed-field boundary (J2) | Inconclusive pending controls |
| Serialized producer record or native verifier | No checked input interpretation or refinement | Partial; bridges B1–B6 absent (J2) | Needs revision |

No hypothesis or official evidence status changes in this technical packet.

## Review custody and controls

The prospective plan, blind card, input bindings, and four `TASK-*` handoffs
were committed and pushed before dispatch. J1, J2, and J3 ran in separate
sessions and sealed their reports in distinct directories under `reviews/`.
J1 read only the isolated blind card as a mathematical source; it derived the
empty-basis and empty-tuple rules and a 72-case F5 scratch control table (14
accepted, 58 rejected, zero mismatches). J2 matched six pinned source files and
five pinned Mathlib files and identified the missing bridges. J3 matched 122
input-binding rows, authenticated the archived hosted artifact by GitHub digest,
and passed 13 receipt rejection controls. J3 also showed that an internally
consistent synthetic receipt can pass receipt validation: the validator checks
consistency, not execution authenticity. The current-head PR #3173 formal
workspace check was a scope no-op; its green label is not a Semaev build.

The planned independence checker failed on the frozen plan/report formats:
the plan names full joint labels while J2/J3 attestations claim short labels,
J1's attestation is JSON rather than the YAML block it discovers, and
`blind_rederivation.blind_from` is a scalar rather than a list of protected
producer paths. The failed output is retained in `independence-check.txt`.
Sealed reviewer files and the prospective plan were not edited after dispatch.
This procedural defect prevents a `validated_scoped` outcome for this round;
a new prospective review round with checker-compatible bindings is needed.

The ten-entry archived `verifier_inputs` map omits the imported
`orchestration/fast_yaml.py` helper. J3 pinned that file separately. A complete
transitive software-input claim needs the helper and external YAML parser
dependency included in the binding mechanism. This is a verifier-custody
repair task; it is not evidence that the named theorem was falsely accepted.

## Next construction

Define a record interpretation contract from serialized bytes to field,
curve, ellipticity, span family, tuple, and target; prove or check the decode
bridge and run the instantiated Lean predicate on a pinned sample record.
Repair the verifier-input closure and run a new prospective independence round
with exact joint labels and protected-path list. Reconcile the forced hosted
Lean run, then publish its actual build and axiom evidence as an addendum.

The editable [evidence-boundary diagram](evidence-boundary.svg) shows the
theorem's proved scope and the missing record bridge. Reviewer reports and
attestations are archived in `reviews/` without altering their seals. J3's
complete 192-file scratch packet is preserved as
`reviews/TASK-20261108-5ef48a-full.tar.gz` in the configured
content-addressed store (SHA-256
`1d80d063fe47d345725a27f48bfb186d288c629ac0c21badffaf059514d00396`);
hydrate it with `python3 tools/artifacts/artifacts.py pull` for that path,
then extract it with `tar -xzf` into a fresh directory before checking its
`seal.json`. The directly browsable J3 report, attestation, input audit, and
receipt controls are copied beside the bundle, byte for byte.

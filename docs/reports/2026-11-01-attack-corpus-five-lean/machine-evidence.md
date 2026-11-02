# Exact machine evidence

## Corrected proof snapshot

- GitHub Actions run:
  [`41365419446`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41365419446)
- Checked head: `0e096a9d9889c5eb7f74e4142cb55b0cdde1f2bf`
- Proof correction commit: `37cc75cfebb30c7582e90e3b632d3454ff5804dc`
- Formal-workspace job:
  [`125024485951`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41365419446/job/125024485951)
- Job interval: 2026-11-02 00:07:23Z--00:31:17Z
- Result: `success`

GitHub's immutable job metadata records `success` for every substantive proof
step:

1. materialize every target source document;
2. generate the workspace root;
3. prefetch the pinned proof toolchains;
4. restore the pinned Mathlib dependencies;
5. verify installed dependency source pins before the proof checks;
6. build the full `formal/` workspace;
7. run `tools/verify_formal_targets.py`, which checks every discharged target,
   rejects forbidden constructs, runs the project axiom audit, and confirms
   the requested named declaration was audited;
8. verify dependency pins again after the proof checks; and
9. upload the formal verification receipts.

The receipt artifact is `formal-verification-receipts`, artifact ID
`13108010573`, 1,359,941 bytes, created 2026-11-02 00:30:56Z and retained
through 2027-01-31. Its API download URL is tied to the run above.

The five final source hashes checked by the correction plan are:

| module | SHA-256 |
| --- | --- |
| `ModAlias.lean` | `81353b007ec158f8383504d7614717551eaa477197ef7d925fe06ff2d52f1420` |
| `AdaptiveBatching.lean` | `4c6feaa0109a6b8b27e8f009db08973c3fc634e1a13daa5f80832f370b17a656` |
| `PolynomialFunctionAlias.lean` | `2f75204ec9aa9269f21bedd1d38f34ed44b6451eba46d0928ae461367662ae10` |
| `SubgroupMembership.lean` | `ee33d018fead344b4b3509e1d1677bb8ebefea17c9834c1a930fcf69092e6d69` |
| `SchnorrSpecialSoundness.lean` | `7bdb4110e6e04cff5356bd3f1e9d5e4d92eaa4e6c746efad8a1cc22d38a5c1b8` |

The later merge of `origin/main` retained these bytes; the modular conflict
resolution was proxy-compiled and re-hashed to the same value.

## Initial snapshot control

The preceding exact run
[`41364641004`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41364641004)
checked the initial producer head `b60c0cec87293255f46e9f95e8ec1afef49f2e17`.
Its available log names all five frozen declarations and ends with
`OK: 107 target(s) machine-verified`. It also records clean matching dependency
revisions before and after proof checking. That run is only a control for the
superseded initial proof bytes; the corrected run above is the authoritative
result for this packet.

## Local controls and trust limits

- Lean/Mathlib 4.34.1 proxy elaboration passed for all five final modules;
  `PolynomialFunctionAlias.lean` emitted one `unnecessarySimpa` style warning.
- Final focused target/verifier tests passed 340/340 after merging current
  `main` (the pre-merge correction round passed 337/337).
- All five frozen target manifests validated, the generated root was current,
  and the scoped forbidden-token scan was empty.
- The authoritative toolchain is the repository pin
  `leanprover/lean4:v4.35.0`, with Mathlib
  `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`; the proxy is not substituted
  for it.
- Actions logs and artifacts redirect to an Azure blob endpoint that returns
  `Forbidden` from this execution environment. Consequently this packet cites
  the GitHub run/job/artifact metadata and successful step conclusions; it
  does not claim to have downloaded or independently hashed the corrected
  receipt ZIP.
- The repository's dependency receipt explicitly limits itself to Git source
  custody; ignored build products retain Lean/Lake binary trust. No independent
  kernel implementation rechecked the result.

---
name: scheme
description: "Assess proposed cryptographic schemes and their security games, reductions, distributions and honest-party algorithms. Use for EUF-CMA, SUF-CMA, IND-CPA/CCA, AKE or EndRing construction obligations and recipient-lift questions. Use design-experiment for a trial contract and formal for proof artifacts."
---

# Scheme obligations

Read `docs/scheme-construction-contract.md` and `templates/scheme-construction-contract.yaml`. Follow the host's six obligations rather than inventing a second security template.

1. Specify the primitive, exact game, adversary/oracle model, key/message distributions and public auxiliary data.
2. Audit efficient honest-party algorithms, correctness, actual-message/key recovery and rejection behavior. A projection or invariant is not a complete encryption/decryption construction.
3. For each security claim name the assumption, reduction direction, simulation obligations and advantage loss. Check that the assumption covers the actual generated distribution.
4. Track separation, recipient lift, endpoint lift, completeness and distribution hardening as separate obligations where applicable. Do not discharge one using a differently typed interface.
5. Distinguish a proof, toy check, hypothesis, missing algorithm and named intermediate assumption. Keep conjectural constructions out of deployment/security claims.
6. Return the obligation table and concrete construction-or-obstruction step. Use formal for a supplied proof target and review-evidence for independent scientific review; avoid manufacturing a secure scheme from a filled template.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.

## Default challenge research loop

Research goals use [the default challenge research loop](../../../docs/challenge-research-loop.md). Preserve the frozen problem, candidate, evidence and review pointers relevant to this skill. Work within its existing role; findings guide the next attempt, and a worker completion alone is not scientific acceptance.

For goal-level boundary work, `autoresearch campaign frontier --goal <GOAL-ID>`
shows the fixed comparison domain, reviewed points, remaining gap and next test.
Carry those references; keep measured, modeled and unresolved claims distinct.

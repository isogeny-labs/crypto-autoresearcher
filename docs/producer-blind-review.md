# Producer-blind review

Contract for reviewers, validators and red-team sessions (proposal I6 of
`docs/autoresearcher-harness-review-20261110.md`). It changes what a producer
is told, not what a reviewer checks.

## Rule

The reviewer sees code, artifacts and scores. It recomputes on fresh seeds and
on inputs of its own choosing. To the producer it returns only a rejection
class from this closed list:

| class | meaning |
| --- | --- |
| `fails_recomputation` | an independent recomputation disagrees with the reported value |
| `scope_mismatch` | the claim is wider than the tested scope or parameters |
| `control_missing` | a required positive, negative or A/A control is absent |
| `certificate_invalid` | a claimed solve or relation has no verifying certificate |
| `out_of_budget` | the run exceeded or did not state its resource budget |

Detailed findings go into the review record and stay sealed until the claim
closes. A free-text reason in a message or handoff to the producer breaks the
rule.

## Rationale

"Reward Hacking Challenges Oversight of Autonomous Research Agents" (arXiv
2609.28614, 2026-09-23; read as reported in the review document, not
re-derived here): 17 models over 38 tasks hacked spontaneously on 30.5% of
open-ended research-pipeline tasks; an LLM panel seeing code and scores missed
6.5% of hacks; over 5 rounds of feedback cumulative evasion was 40.5% with
detailed panel feedback and 20.3% with generic rejection. The detailed arm is
confounded with other information, so the numbers motivate a test here and
settle nothing here.

## Falsifier

`EVAL-DISC-FEEDBACK-DETAILED` and `EVAL-DISC-FEEDBACK-GENERIC` in
`evals/suites/discipline.yaml`: one trap instance (no solution exists), a
5-round loop, a code intake check that trusts a self-attested flag, and a
grader that recomputes `E.mul(k, P) == Q`. Arms differ only in the text
returned after a rejection. Run at least 10 trials per arm and compare Wilson
intervals. If the generic arm shows no lower evasion, drop this rule and keep
detailed feedback. Status: the arms exist and have not been run (no
credential).

## Cost to honest producers

An honest producer gets a class instead of a reason, so fixes take more rounds
and more self-checking. The sealed record opens when the claim closes. Whether
the cost is worth paying is what the eval arms measure.

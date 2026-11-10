# RBS-ICPERF-e2a5c2: S02 stop diagnosis (main session, 2026-11-06T22:15Z)

## What happened (from committed files on origin/claude/c1-run-20261106, commit b0d984b99)
- S01-probe passed. S02 T1 (RUN-ICPERF-c7f69e) ran launch_eks.sh once. stderr.log:
  "An error occurred (InvalidInputException) when calling the BatchGetBuilds operation: Invalid build ID provided"
  "duplicate check failed (codebuild batch-get-builds)". raw-result.json: submitted false, outcome_class other,
  refusal duplicate_check_failed (wrapper exit 4: "the duplicate check itself failed (nothing submitted)").
- Supervisor exit 3; session stopped; T2 (RUN-ICPERF-6f784c) not_run. runbook.py verify: VERIFY OK.
- Nothing submitted, no CodeBuild build, no EKS job, USD 0 spent. Read-only checks at 22:12Z:
  s3://isolab-results-104186811093-us-east-2/runs/{ic-c1-dg-s1-20261106, ic-c1-dg-s2-20261106, -r2 of both}/ have 0 objects;
  the s1 request object inputs/requests/21728056...dec.json does not exist.

## Root cause (reproduced read-only)
launch_eks.sh line 174: `aws codebuild list-builds-for-project ... --max-items 100 --query 'ids[]' --output text`.
With aws-cli 1.46.2, --max-items appends the pagination token to text output; with >100 builds it prints
100 ids plus the token "None". Reproduced: 101 words, the extra one "None". batch-get-builds then rejects "None".
--dry-run makes no AWS call, so neither S01 nor any dry run exercised this path.

## Proposed fix (c1-fix/launch_eks.patch; fixed file sha256 in c1-fix/SHA256)
- --no-paginate instead of --max-items 100 (one page, at most 100 ids, the same set as before);
- keep only tokens matching ^<project>:[0-9a-f-]+$;
- refuse 4 if the listing printed something but no build id survived.

## Tests of the fix (read-only AWS; extracted duplicate-check block with a stub refuse())
- original block, s1 key: exit 4, same InvalidInputException (reproduces the stop);
- fixed block, s1 key: "no existing prefix, request object or build ... submitting once", exit 0;
- fixed CodeBuild branch only, key of the newest existing build: REFUSE 3 duplicate (positive control), exit 3;
- fixed CodeBuild branch only, s1 key: exit 0. bash -n OK.

## Consequences for bound bytes
launch_eks.sh sha256 130164868a... is bound only by experiments/EXP-ICPERF-127dbd/runbook.yaml and trial-plan.json
(car). The crypto protocol (v2, 9844f78d...) and AMENDMENT-1 do not bind it. A new runbook sha256 follows, so a new
approval and a new runbook session are required (the stopped session is never reopened).

## Questions for the Coordinator
1. Classification of RBS-ICPERF-e2a5c2 (proposal: implementation_error before submission, not host loss; no record opened; no spend).
2. Which requests the new session uses. The first-attempt requests were never submitted (no S3 object, no build).
   Proposal: first-attempt request-s1/s2, keeping the frozen -r2 requests for the protocol's one host-loss rerun.
3. Budget gate lines unchanged (S1 1.86216, S2 1.86216; actual spend so far 0).
4. Owner gate: the owner's go-ahead (2026-11-06T22:05Z, "/ic-autolab go") covers "S1, S2 and any -r2" (protocol section 11).
5. Fresh ids reserved: see ids.txt.

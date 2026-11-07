Archived outputs of implementation/tests/test_locator.sh (final run). RESULTS.txt is the case table (every check: expected and observed).
Per case: cases/<id>/fx = the fixture (launcher result.json and build.json, the fake bucket's receipt and pod files); wrap-v3b/ and wrap-v3a/ = the wrapper run
(stdout, stderr, aws.log of every fake-aws call, rec/raw-result.json, rec/manifest.yaml, rec/job/locator/); reconcile*/ = the reconcile_run.sh run (out/reconcile-result.json,
out/check_job.stdout, out/object-list.txt, out/locator/). Left out to keep the tree small: records.jsonl (10,800 lines of {} in every synthetic session), the
download copies (artifacts/), the script copies under impl/ and checkout/, the request copy, and, for the negative cases, the pod files that the case does not change.
The test regenerates every omitted file: bash implementation/tests/test_locator.sh OUTDIR [REAL_CHECKOUT].

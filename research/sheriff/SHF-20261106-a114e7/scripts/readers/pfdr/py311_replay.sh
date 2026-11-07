#!/usr/bin/env bash
# Own 3.11 replay driver (sheriff SHF-20261106-a114e7, reader pfdr). Not the producer's replay.sh.
# usage: py311_replay.sh <python> <scratch_root> <out_base> <trial_id> <run_id>
# scratch_root = git archive 48bd193a (implementation, plan, spec, runbook) + git archive HEAD (runs/).
# Runs the recorded command (command.txt argv) with argv[0] replaced and --run-dir in out_base.
set -uo pipefail
PY=$1; ROOT=$2; OUT=$3; TRIAL=$4; RUN=$5
U=$OUT/$TRIAL/$RUN; rm -rf "$OUT/$TRIAL"; mkdir -p "$OUT/$TRIAL"
cd "$ROOT"
"$PY" -c 'import sys,json;print(json.dumps({"version":sys.version,"executable":sys.executable}))' > "$OUT/$TRIAL/interp.json"
"$PY" experiments/EXP-PFDR-bb0d26/implementation/run.py trial --run-dir "$U" --run-id "$RUN" --trial-id "$TRIAL" \
  --plan experiments/EXP-PFDR-bb0d26/trial-plan.json > "$OUT/$TRIAL/stdout.log" 2> "$OUT/$TRIAL/stderr.log"
echo $? > "$OUT/$TRIAL/run.rc"
"$PY" experiments/EXP-PFDR-bb0d26/implementation/check.py "$U" experiments/EXP-PFDR-bb0d26/trial-plan.json "$TRIAL" \
  > "$OUT/$TRIAL/check.stdout.log" 2> "$OUT/$TRIAL/check.stderr.log"
echo $? > "$OUT/$TRIAL/check.rc"
echo "$TRIAL $RUN run.rc=$(cat $OUT/$TRIAL/run.rc) check.rc=$(cat $OUT/$TRIAL/check.rc)"

#!/usr/bin/env bash
# Claude Code hook for tools/benchrec.py (benchmark records: data in S3,
# metadata in Git, progress report regenerated). Byte-identical in crypto,
# crypto-autoresearcher and cryptanalysis (lab contract, section 7).
#
#   PreToolUse  Bash  a benchmark launcher: refuse it unless it runs under an
#                     open record (tools/benchrec.py run, or BENCHREC=<record>
#                     in the command). A command that is not a benchmark opts
#                     out with BENCHREC_SKIP=<reason>.
#   PreToolUse  Bash  git push / gh pr create: refuse while a record opened
#                     here is not closed, a record is incomplete, or the
#                     progress report is stale (tools/benchrec.py gate).
#   Stop              list records still open, so a session does not end
#                     with an unrecorded run.
set -uo pipefail

input="$(cat)"
field() { printf '%s' "$input" | python3 -c '
import json, sys
d = json.load(sys.stdin)
for k in sys.argv[1].split("."):
    d = d.get(k) if isinstance(d, dict) else None
print("" if d is None else d)' "$1"; }

event="$(field hook_event_name)"
cwd="$(field cwd)"

# Commands that measure. Narrower than the checkpoint hook's launcher list on
# purpose: this one asks for a record, which costs a few commands to fill.
BENCH_RE='\becbench\b|\bperfindex\b|perf_ipc|\bperf +stat\b|callgrind|\bhyperfine\b|cargo +bench\b|isolated_bench|calibrated_tier1_bench|tier1_calibrator|tools/profile\.sh|task_card\.py +run|\bautolab\b|\bicms\b|scripts/[A-Za-z0-9_./-]*bench[A-Za-z0-9_.-]*|bench\.py +run|ic_target[a-z_]*benchmark|gf2_bench|\bmake +bench\b|ca_bench'
PUSH_RE='(^|[;&|( ]|\$\()git +push\b|\bgh +pr +create\b'

case "$event" in
  PreToolUse)
    cmd="$(field tool_input.command)"
    [[ "$cmd" == *BENCHREC_SKIP=* ]] && exit 0
    root="$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null)" || exit 0
    [ -f "$root/tools/benchrec.py" ] || exit 0
    if printf '%s' "$cmd" | grep -qE "$BENCH_RE"; then
      if printf '%s' "$cmd" | grep -qE 'tools/benchrec\.py +run\b'; then exit 0; fi
      rec="$(printf '%s' "$cmd" | sed -n 's/.*BENCHREC=\([^ ;&|]*\).*/\1/p' | head -1)"
      if [ -z "$rec" ]; then
        cat >&2 <<EOF
Benchmark without a record. Every benchmark run leaves a bench.record/v1 file in Git
(raw data hashed, S3 location, metrics in the shared units) and regenerates the progress
report. Open one, then run the launcher under it:

  python3 tools/benchrec.py init --slug <slug> --problem <problem-key> [--curve <uid>]
  python3 tools/benchrec.py run <record> -- <this command>
  python3 tools/benchrec.py add-raw <record> <raw files...>
  python3 tools/benchrec.py metric <record> --name <n> --value <v> --unit <S|gae|ir_per_op|...>
  python3 tools/benchrec.py close <record> --status measured --report <pdf> --summary "..."

(If this command is not a benchmark, prefix it with BENCHREC_SKIP=<reason>.)
EOF
        exit 2
      fi
      if [ ! -f "$root/$rec" ] && [ ! -f "$rec" ]; then
        echo "BENCHREC=$rec names no record file (python3 tools/benchrec.py init ...)." >&2
        exit 2
      fi
      exit 0
    fi
    if printf '%s' "$cmd" | grep -qE "$PUSH_RE"; then
      if ! out="$(cd "$root" && python3 tools/benchrec.py gate 2>&1)"; then
        printf '%s\n' "$out" >&2
        echo "Push refused: close every benchmark record opened here and regenerate the progress report (python3 tools/benchrec.py report). A push that carries no benchmark work may use BENCHREC_SKIP=<reason>." >&2
        exit 2
      fi
    fi
    exit 0
    ;;
  Stop)
    root="$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null)" || exit 0
    [ -f "$root/tools/benchrec.py" ] || exit 0
    [ -s "$root/.benchrec/open.jsonl" ] || exit 0
    echo "Benchmark records still open (close them with tools/benchrec.py close before the session ends):"
    (cd "$root" && python3 tools/benchrec.py open) || true
    exit 0
    ;;
esac
exit 0

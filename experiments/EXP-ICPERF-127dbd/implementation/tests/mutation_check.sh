#!/usr/bin/env bash
# Mutation check of the C1 locator, reconciler and launch wrapper (TASK-20261107-d07e94 E-4).
# For each mutation of tests/mutate.py (one check of K-1, K-2, K-4, K-5, K-6 or K-7 removed), it builds a mutated copy of the three
# scripts and runs the whole of tests/rt_regression.sh against it. A mutation is CAUGHT when at least one case differs from its
# expected outcome, SURVIVED when none does. It also runs the unmutated scripts as the baseline (must show 0 differing cases).
# usage: env -i HOME="$HOME" TMPDIR=<tmp> PATH=<dir holding only the fake aws>:/usr/bin:/bin bash mutation_check.sh OUTDIR [JOBS [NAME_REGEX]]
# Exit status: the number of mutations that survived and are not subsumed (plus 100 if the baseline has a differing case).
set -u
TESTS=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
IMPL=$(cd "$TESTS/.." && pwd)
one() { # one NAME OUT : build the mutant, run the suite, write one result line (runs as `bash mutation_check.sh --one NAME OUT`, so no function is exported into the suite's environment)
  local n=$1 d="$2/m/$1" edit nd failing verdict
  rm -rf "$d"; mkdir -p "$d"
  if [[ $n == BASELINE ]]; then mkdir -p "$d/impl"; cp "$IMPL"/{launch_eks.sh,locate_results.sh,reconcile_run.sh} "$d/impl/"; edit="none"
  else edit=$(python3 -I "$TESTS/mutate.py" apply "$n" "$IMPL" "$d/impl" 2>&1) || { printf '%s\tERROR\t-\t-\t%s\n' "$n" "$edit" > "$d/result.tsv"; return; }; fi
  for f in "$d"/impl/*.sh; do bash -n "$f" || { printf '%s\tERROR\t-\t-\tmutant does not parse: %s\n' "$n" "$f" > "$d/result.tsv"; return; }; done
  bash "$TESTS/rt_regression.sh" "$d/out" "$d/impl" v3c > "$d/suite.log" 2>&1
  nd=$?
  failing=$(awk -F'\t' 'NR > 1 && $7 == "FAIL" {print $1}' "$d/out/rt-results.tsv" 2>/dev/null | head -12 | tr '\n' ' ')
  verdict=CAUGHT; [[ $nd -eq 0 ]] && verdict=SURVIVED
  [[ $n == BASELINE ]] && { verdict=BASELINE-CLEAN; [[ $nd -eq 0 ]] || verdict=BASELINE-DIRTY; }
  printf '%s\t%s\t%s differing case(s)\t%s\t%s\n' "$n" "$verdict" "$nd" "${failing:-none}" "$edit" > "$d/result.tsv"
}
if [[ ${1:-} == --one ]]; then one "$2" "$3"; exit 0; fi
OUT=${1:?usage: mutation_check.sh OUTDIR [JOBS [NAME_REGEX]]}; JOBS=${2:-3}; ONLY=${3:-.}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
[[ $(env | grep -c '^AWS_') == 0 ]] || { echo "REFUSED: AWS_* variables present" >&2; exit 99; }
names=$(python3 -I "$TESTS/mutate.py" list | cut -f1 | grep -E -- "$ONLY")
printf '%s\n' BASELINE $names | xargs -P "$JOBS" -I{} bash "${BASH_SOURCE[0]}" --one {} "$OUT"
printf 'mutation\tverdict\tdiffering\tfailing_cases(first 12)\tedit\n' > "$OUT/mutation-results.tsv"
for n in BASELINE $names; do cat "$OUT/m/$n/result.tsv"; done >> "$OUT/mutation-results.tsv"
# A check that another check subsumes (removing it alone changes no outcome because the second check refuses the same inputs with the same
# exit status) is reported SUBSUMED when the mutant that removes the pair is CAUGHT: K2-nonempty is subsumed by K2-entries (which also requires a
# pod entry); the type test of `verify` is subsumed by the equality with the container exit code plus the raw spelling test (K4-raw).
declare -A SUBSUMED_BY=( [K2-nonempty]=K2-nonempty-and-entries [K4-type]=K4-verify )
for n in "${!SUBSUMED_BY[@]}"; do
  p=${SUBSUMED_BY[$n]}
  if [[ $(awk -F'\t' -v n="$n" '$1 == n {print $2}' "$OUT/mutation-results.tsv") == SURVIVED && $(awk -F'\t' -v p="$p" '$1 == p {print $2}' "$OUT/mutation-results.tsv") == CAUGHT ]]; then
    awk -F'\t' -v OFS='\t' -v n="$n" -v p="$p" '$1 == n {$2 = "SUBSUMED(by " p ")"} {print}' "$OUT/mutation-results.tsv" > "$OUT/mutation-results.tsv.t" && mv "$OUT/mutation-results.tsv.t" "$OUT/mutation-results.tsv"
  fi
done
cat "$OUT/mutation-results.tsv"
surv=$(awk -F'\t' '$2 == "SURVIVED" || $2 == "ERROR" {c++} END {print c+0}' "$OUT/mutation-results.tsv")
dirty=$(awk -F'\t' '$2 == "BASELINE-DIRTY" {c++} END {print c+0}' "$OUT/mutation-results.tsv")
echo "== mutations: $(printf '%s\n' $names | wc -l); caught $(awk -F'\t' '$2 == "CAUGHT" {c++} END {print c+0}' "$OUT/mutation-results.tsv"); subsumed $(awk -F'\t' '$2 ~ /^SUBSUMED/ {c++} END {print c+0}' "$OUT/mutation-results.tsv"); survived or errored $surv; baseline dirty $dirty"
exit $((surv + dirty * 100))

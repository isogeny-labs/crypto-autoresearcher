#!/usr/bin/env bash
# Text checks for reader `papers` (SHF-20261106-a114e7). Reads git blobs and files only;
# executes nothing from the audited repositories.
# Usage: CHECKPOINT_SKIP=audit BENCHREC_SKIP=audit bash text_checks.sh > text_checks.out 2>&1
set -u
C=/home/user/crypto
A=/home/user/crypto-autoresearcher
g() { git -c gc.auto=0 -C "$C" "$@"; }
show() { g show "HEAD:$1"; }
sec() { printf '\n===== %s\n' "$*"; }

sec "heads"
echo "crypto $(g rev-parse HEAD)"; echo "car $(git -C $A rev-parse HEAD)"

sec "P1/P-N1/P-N2: LLL note withdrawals and table (tex lines)"
grep -n "curve-specific\|withdraw\|not isolated\|catastrophic\|Recovered / distinct\|0 / 3\|3 / 3" $C/papers/lll-degeneracy-note/lll_degeneracy_note.tex
for f in papers/lll-degeneracy-note/lll_degeneracy_note.tex papers/lll-degeneracy-note/lll_degeneracy_note.pdf; do echo "$f last: $(g log -1 --format='%h %cI' -- $f)"; done
pdftotext $C/papers/lll-degeneracy-note/lll_degeneracy_note.pdf - | grep -c "PPN-2" | sed 's/^/LLL PDF mentions PPN-2 footnote: /'

sec "PPN-2: analysis note section 10 correction"
show research/notes/lattice-hnp/RESEARCH_LLL_GS_ANALYSIS.md | grep -n "Correction (2026-10-28\|2^1024\|2^224\|1 − 2^-30\|withdrawn\|0.4.8"
grep -n 'name = "num-bigint"' -A1 $C/Cargo.lock
sed -n 442,454p $C/src/cryptanalysis/lattice.rs

sec "P3/P4/P5/P-N4: structural-completeness tex"
grep -n "330 primes\|669 primes\|621\|16\\\\,562\|24\\\\,476\|336 and 249\|292 and\|skip \$r = 0\|hypothesis classes that\|argued by case\|standing assumptions\|bounded" $C/papers/structural-completeness/structural_completeness.tex | head -20
echo "--- distinct-check counts in the cited recount/ outputs (expect none):"
grep -n -w "336\|249\|292\|209" $C/papers/structural-completeness/recount/*.txt || echo "none"
for f in structural_completeness.tex structural_completeness.pdf abstract.txt README.md recount/README.md; do echo "$f last: $(g log -1 --format='%h %cI' -- papers/structural-completeness/$f)"; done
pdftotext $C/papers/structural-completeness/structural_completeness.pdf - | grep -n "3305\|330 primes\|machine-checked" | head

sec "PPN-3 residual: abstract.txt companion-artefact lines vs paper"
grep -n "PARI/GP scripts\|Rust integration test\|baseline" $C/papers/structural-completeness/abstract.txt
sed -n 964,969p $C/papers/structural-completeness/structural_completeness.tex
sed -n 1007,1009p $C/papers/structural-completeness/structural_completeness.tex
for c in $(g log --format=%h -- tests/curve_audit.rs); do echo "tests/curve_audit.rs at $c: $(g show $c:tests/curve_audit.rs 2>/dev/null | wc -l) lines ($(g log -1 --format=%ad --date=short $c))"; done

sec "P-N5: recount README provenance and regenerated output"
sed -n 5,16p $C/papers/structural-completeness/recount/README.md
sed -n 62,64p $C/papers/structural-completeness/recount/exp_zdoubleprime_lemma_extended.txt
grep -c "16562" $C/papers/structural-completeness/recount/*.txt

sec "P-N6/PPN-4: Markdown twin and intro sentence"
show research/notes/cm-isogeny/PAPER_STRUCTURAL_COMPLETENESS.md | grep -n "argued\|proof sketches\|unconditional\|rigorously\|mechanically\|machine-checked" | head
sed -n 146,153p $C/papers/structural-completeness/structural_completeness.tex
grep -n "Prove a structural\|^\\\\begin{proof}" $C/papers/structural-completeness/structural_completeness.tex

sec "P6: semaev paper cites its run"
grep -n "nolinkurl{experiments/EXP-SMON-e5cbe6" $A/papers/semaev-conservation-specialization/paper.tex
git -C $A ls-tree --name-only -r HEAD experiments/EXP-SMON-e5cbe6/runs/RUN-SMON-e5cbe6-001/

sec "PPN-1: conductor-gap banner"
show research/conductor_gap_cm_pairs_20261010/README.md | sed -n 1,11p

sec "PPN-7: commit-pinned generic.rs citations"
for f in README.md PROTOCOL.md lean/README.md lean/GenericInvariance.lean; do show research/conductor_gap_cm_pairs_20261010/$f | grep -n "line 309 at commit 57fa35852" | sed "s#^#$f:#"; done
echo "57fa35852:309 -> $(g show 57fa35852:src/cryptanalysis/ecbench/generic.rs | sed -n 309p)"
echo "11aa00591:275 -> $(g show 11aa00591:src/cryptanalysis/ecbench/generic.rs | sed -n 275p)"
echo "HEAD: $(grep -n 'mix(g.key(&pos))' $C/src/cryptanalysis/ecbench/generic.rs)"

sec "P-N7: tree-split wording"
show research/ic_tree_split_structured_v_20261011/RESULTS.md | sed -n 52,58p
show research/ic_tree_split_structured_v_20261011/reports/run-20261011T2105Z/report.typ | sed -n 29p | cut -c1-400

sec "E1/E1-R: audit.rs never_finalised and records_bound"
grep -n "pub fn never_finalised\|session.status == \"running\"\|let killed = \|records_bound: Some(\|!killed && session.records_sha256\|NEVER_FINALISED: &str\|fn a_killed_session\|fn a_finalised_interrupted" $C/src/cryptanalysis/ecbench/audit.rs

sec "E2/PPN-6: ecbench.yml triggers and enumeration"
sed -n 41,53p $C/.github/workflows/ecbench.yml
grep -n "git ls-tree -r --name-only HEAD | sed\|ecbench.session/v1\|ecbench_replay != 'false'\|github.event_name == 'workflow_dispatch' || github.event_name == 'schedule'" $C/.github/workflows/ecbench.yml | head -20

sec "PPN-6 residual: ci-scope rules vs .artifacts.json"
sed -n 70,79p $C/.github/scripts/ci-scope.mjs
grep -n "artifacts" $C/.github/scripts/ci-scope.mjs || echo "ci-scope.mjs never mentions .artifacts.json"
grep -n "diff-filter=AM\|def cmd_check" <(show tools/artifacts/artifacts.py)

sec "PPN-5: audit script reads records_bound"
sed -n 162,171p $C/.github/scripts/ecbench-audit-sessions.sh
sed -n 184,203p $C/.github/scripts/ecbench-audit-sessions.sh

sec "SES-1: the two records and any correction"
git -C $A show HEAD:experiments/EXP-SGCP-EMBED-002/development-result-v1.md | sed -n 8p
git -C $A show HEAD:ledger/evidence/EV-ICINV-8afb64.yaml | sed -n 58p
git -C $A log -1 --format='%h %ad' --date=short -- experiments/EXP-SGCP-EMBED-002/development-result-v1.md ledger/evidence/EV-ICINV-8afb64.yaml
echo "corrections naming SES-1 or 'verified execution':"; rg -l -i "SES-1|verified execution" $A/ledger/corrections || echo none

sec "New-claim scan: Cheon sentence and its source"
grep -n "beats rho from 24 bits" $C/papers/ecdlp-index-calculus-treatise/sections/prog_prime.tex
show research/torsion_auxiliary_inputs_20260918/RESULTS.md | grep -n "| 24 |\|| 28 |" | grep -i "cheon" | cut -c1-200
echo "treatise prog_prime.tex added since 2026-10-28: $(g log --since=2026-10-28 --format=%h -- papers/ecdlp-index-calculus-treatise/sections/prog_prime.tex | tr '\n' ' ')"

sec "New-claim scan: 'verified executions' in papers"
rg -n -i "verified execution" $C/papers $A/papers | cut -c1-200
show benchmarks/README.md | grep -n "1,088/1,088" | cut -c1-260

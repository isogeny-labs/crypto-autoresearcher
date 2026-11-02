#!/bin/bash
# SessionStart hook: make a fresh container able to run this repo's checks.
#
# Two things are wrong with a default clone here, and both cost a whole session
# to rediscover:
#
#   1. `sympy` and `pytest` are declared (pyproject.toml, requirements-dev.txt)
#      but absent, so `make check-harness` and `make test` fail on import
#      before running anything real.
#   2. The clone is SHALLOW. tools/research_dispatch.py verifies archive
#      receipts against commit reachability, and history the clone never
#      fetched reads as an unreachable commit -- which the portfolio sweep
#      reports as `needs_repair`. That is not a research result and not
#      repository corruption; it is a missing object. It once put 26 of 46
#      active goals in that bucket, leaving the harness nothing to dispatch.
#
# In the web container it also starts a cairn node and runs aburan28/crypto's
# scripts/cloud-setup.sh for the rest of the toolchain, SageMath 10.9 included
# (the last block below).
#
# Idempotent, non-interactive, and never fatal: a session that starts with a
# degraded environment is better than one that does not start.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}" || exit 0

# Sparse checkout (docs/sparse-checkout.md). A full checkout is ~9 GB, 7 GB of
# it run archives and reference bundles an execution session never reads, and
# it leaves too little disk for SageMath. In the web container cloud-setup.sh
# (last block) applies the harness profile by default;
# CRYPTO_AR_SPARSE_PROFILE=full keeps the checkout full for the ledger sweeps
# the Coordinator skills run, which refuse a sparse checkout. Elsewhere it
# stays opt-in: CRYPTO_AR_SPARSE_PROFILE=harness here; `disable` undoes it.
if [ -n "${CRYPTO_AR_SPARSE_PROFILE:-}" ] && [ "$CRYPTO_AR_SPARSE_PROFILE" != full ]; then
    python3 tools/sparse_checkout.py apply "$CRYPTO_AR_SPARSE_PROFILE" >&2 \
        || echo "session-start: sparse profile '$CRYPTO_AR_SPARSE_PROFILE' not applied; checkout stays full" >&2
elif [ "${CLAUDE_CODE_REMOTE:-}" != "true" ] \
    && [ "$(git config --bool core.sparseCheckout 2>/dev/null)" != "true" ] \
    && [ "$(df -Pk . 2>/dev/null | awk 'NR==2{print $4}')" -lt 20971520 ] 2>/dev/null; then
    echo "session-start: <20GiB free with a full checkout; 'python3 tools/sparse_checkout.py apply harness' frees ~7GB for run sessions" >&2
fi

# The declared toolchain. Small and slow-moving on purpose -- a run record has
# to stay reproducible years from now (see requirements-agent.txt).
python3 -m pip install -q --disable-pip-version-check -r requirements-dev.txt \
    || echo "session-start: dependency install failed; run 'pip install -r requirements-dev.txt'" >&2

# Deepen the clone so archive verification sees real history. Only adds
# objects: it rewrites nothing and touches no working tree. Commits and trees
# only: reachability needs no old file contents, and a plain --unshallow pulled
# every blob of all ~1,300 branches. Old blobs arrive on demand if read.
if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
    echo "session-start: shallow clone, fetching history (commits and trees) for archive verification" >&2
    python3 tools/sparse_checkout.py deepen >&2 \
        || echo "session-start: unshallow failed; goal_portfolio_health.py retries it, and warns while it is shallow" >&2
fi

# The merge-hygiene pre-commit hook. CI is the backstop, not the gate: a new
# contributor's workflows sit in "awaiting approval" and did not run at all on
# the two PRs that corrupted nine records (Makefile `hooks`).
# PR-scoped vs origin/main: absolute, it refuses every commit in the repo while
# any record anywhere is unparseable, including ones this commit never touched.
if mkdir -p .git/hooks 2>/dev/null; then
    printf '#!/bin/sh\nif git rev-parse --verify -q origin/main >/dev/null; then\n  exec python3 tools/check_merge_hygiene.py --base origin/main\nfi\nexec python3 tools/check_merge_hygiene.py\n' > .git/hooks/pre-commit \
        && chmod +x .git/hooks/pre-commit
fi

# A cairn node joined to the published seed nodes, kept up for the session
# (scripts/cairn-node.sh, shared with crypto, cryptanalysis and
# ml-cryptanalysis). Its own ports (9100/9180) and data directory, so the
# per-session `cairn run` that tools/cairn_mcp.sh starts on 9000/8080 is
# unaffected; that one also gets the `ui`-feature binary it needs from here.
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
    scripts/cairn-node.sh ensure || true
fi

# The rest of the research toolchain: aburan28/crypto's scripts/cloud-setup.sh
# (docs/cloud-setup.md there). It applies the harness sparse profile to this
# checkout and to a crypto checkout next to it, then runs
# scripts/setup-workstation.sh: system libraries and PARI/GP, Rust/Go/Node/uv,
# conductor, the codex and opencode CLIs, aws and kubectl, git/gh sign-in as
# the GitHub service account when GH_APP_* or GH_SERVICE_TOKEN is set as an
# environment secret, a cryptanalysis checkout next to this one, per-repo
# virtualenvs, and SageMath 10.9 when 4 GiB are free. Its lean conda-forge
# build (sagelib + maxima) goes to /opt/conda-sage with the `sage -python`
# shim that frozen trial-plan argv uses. That is workspace tooling only: it
# does NOT satisfy a frozen experiment's runtime-lock admission (a
# Coordinator-pinned, hash-verified sandbox; see AGENTS.md and each
# experiment's dependencies.json/linux-runtime-lock.json). cairn (above) and
# crypto's control plane are skipped.
# Fetched at a pinned commit, not main, so a session never runs a script nobody
# reviewed; bump CRYPTO_SETUP_REF to take a newer one. It skips what is
# installed, so a cached container only re-checks. Its output goes to a log.
# CRYPTO_WORKSTATION_SETUP=0 turns it off and CRYPTO_SETUP_CLONE lists the
# repositories to clone (default cryptanalysis).
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ] && [ "${CRYPTO_WORKSTATION_SETUP:-1}" != 0 ]; then
    setup_ref="${CRYPTO_SETUP_REF:-0a621d718eed400eabf5fa863ead48383f1ba999}"
    setup_dir="$HOME/.cache/workstation-setup/$setup_ref/scripts"
    setup_log="$HOME/.local/state/workspace-tools/autoresearcher-setup.log"
    mkdir -p "$setup_dir" "$(dirname "$setup_log")"
    # cloud-setup.sh runs setup-workstation.sh from its own directory, which
    # runs isolab-agent.sh from there too.
    for f in cloud-setup.sh setup-workstation.sh isolab-agent.sh; do
        [ -s "$setup_dir/$f" ] && continue
        curl -fsSL --max-time 30 \
            "https://raw.githubusercontent.com/aburan28/crypto/$setup_ref/scripts/$f" \
            -o "$setup_dir/$f.tmp" && mv "$setup_dir/$f.tmp" "$setup_dir/$f" \
            || echo "session-start: could not fetch $f at $setup_ref" >&2
    done
    if [ -s "$setup_dir/cloud-setup.sh" ] && [ -s "$setup_dir/setup-workstation.sh" ]; then
        if WORKSPACE="$(dirname "$PWD")" CLONE_REPOS="${CRYPTO_SETUP_CLONE-cryptanalysis}" \
            SETUP_SKIP=cairn bash "$setup_dir/cloud-setup.sh" >>"$setup_log" 2>&1; then
            echo "session-start: cloud setup ran (log: $setup_log)" >&2
        else
            echo "session-start: cloud setup failed (log: $setup_log)" >&2
        fi
    else
        echo "session-start: skipping cloud setup; its scripts did not download" >&2
    fi
fi

exit 0

# What this program has already tried against ECDLP, and whether anything
# changed in the four repositories since the atlas was last reviewed
# (knowledge/leads/ecdlp/README.md). Hook stdout becomes session context, so a
# fresh clone starts by knowing whether everything has already been examined.
# Never fatal.
python3 tools/lead_atlas.py --brief 2>/dev/null || true

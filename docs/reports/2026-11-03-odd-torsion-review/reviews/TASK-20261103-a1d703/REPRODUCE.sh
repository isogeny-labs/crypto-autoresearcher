#!/usr/bin/env bash
set -euo pipefail
# Run from a fresh output directory; retain old downloads rather than overwrite.
gh run download 41494797344 --repo isogeny-labs/crypto-autoresearcher --name formal-verification-receipts --dir receipts
gh run download 41494797344 --repo isogeny-labs/crypto-autoresearcher --name lean-controls --dir lean-controls
gh run view 41494797344 --repo isogeny-labs/crypto-autoresearcher --json databaseId,headSha,conclusion,status,workflowName,createdAt,updatedAt,url,jobs > run-metadata.json
gh run view 41494797344 --repo isogeny-labs/crypto-autoresearcher --log > run.log
gh api repos/isogeny-labs/crypto-autoresearcher/actions/runs/41494797344 > run-api.json
gh api repos/isogeny-labs/crypto-autoresearcher/actions/runs/41494797344/artifacts > artifacts-metadata.json
# The adjacent check_j3.py uses retained raw/ data and exact Git objects.
# python3 /path/to/check_j3.py /path/to/review/worktree

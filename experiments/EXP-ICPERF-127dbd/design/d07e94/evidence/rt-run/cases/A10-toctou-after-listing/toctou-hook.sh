set -e
: "${FAKE_S3_ROOT:?the hook needs FAKE_S3_ROOT}"
mkdir -p "$FAKE_S3_ROOT/runs/ic-c1-dg-s1-20261106/0bbbbbbb-1111-2222-3333-555555555555"; echo late > "$FAKE_S3_ROOT/runs/ic-c1-dg-s1-20261106/0bbbbbbb-1111-2222-3333-555555555555/job-exit.json"
pd="$FAKE_S3_ROOT/runs/ic-c1-dg-s1-20261106/5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7"; echo '{"placed":"between listing and download"}' > "$pd/session/late.json"
(cd "$pd" && find . -type f ! -name SHA256SUMS | sed 's|^\./||' | LC_ALL=C sort | xargs -d '\n' sha256sum) > "$pd/SHA256SUMS"

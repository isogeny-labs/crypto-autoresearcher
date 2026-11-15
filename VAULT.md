# Research vault

Every tracked file in this repository is stored in Git as **AES-256-SIV**
authenticated ciphertext. The working tree is plaintext only while the vault is
unlocked with the deployment secret `KEY`.

This is a Git content filter, not a normal repository. Read this before cloning
or running anything.

## What stays plaintext (bootstrap set)

GitHub parses workflows before any step can execute, and Git needs attributes
to select a filter, so these paths are deliberately **not** encrypted:

- `.gitattributes` at every depth, and root `.gitignore`
- `.github/**` (workflows, composite actions, CI scripts)
- `.artifacts/**` and `**/.artifacts.json` (artifact-store config and manifests read via `git show` in CI)
- `tools/vault/**` (the decryptor and the bulk encryptor)
- `.codex/environments/**` (worktree setup, readable before unlock)
- `VAULT.md`

Everything else, including `AGENTS.md`, `docs/`, source, the ledger and
coordination records, is ciphertext in the object store.

## Local use

The Python interpreter must support an empty AES-SIV encrypt/decrypt roundtrip.
Use a `cryptography>=46` wheel linked to OpenSSL 3.5 or newer. Importing
`cryptography` alone does not establish this capability; older backends reject
valid authenticated empty files. CI probes the roundtrip before choosing its
interpreter. Unlock reports an actionable dependency error and never accepts
an empty ciphertext without authenticating it.

```sh
export KEY=...                     # or keep `export KEY=...` in ~/.zshrc
python3 tools/vault/vaultctl.py setup --codex
python3 tools/vault/vaultctl.py unlock
git status                          # clean: plaintext cleans back to ciphertext
```

Codex's checked-in `.codex/environments/environment.toml` runs `unlock` as
its worktree setup script. Select **Research vault** as the project's local
environment, or run `setup --codex` to select a persistent copy in Git’s
common directory (including this worktree’s override). The selected copy survives
worktree removal. Setup also installs the filter under the common Git directory
so filter commands survive worktree removal. This configuration must remain plaintext so Codex can read it
before setup. Existing branches predating this fix must first incorporate it.

`unlock` decrypts only ciphertext already present on disk, resumes interrupted
unlocks, and preserves plaintext edits, staged changes, symlinks and LFS files.
The legacy `--force` option no longer discards plaintext edits. It authenticates
empty encrypted files too. Nested `.gitattributes` are bootstrap text because
Git reads index attributes before checkout and before any setup script can run.

A fresh clone has ciphertext on disk until `unlock` runs. If `KEY` is missing,
Git fails closed: it never stores plaintext and never reports success.

To lock again, remove the plaintext checkout and restore it later with
`vaultctl.py unlock`:

```sh
python3 tools/vault/vaultctl.py status
```

## CI

Every workflow runs an **Unlock research vault** step immediately after
`actions/checkout`. It reads `secrets.KEY`, derives the key in memory, writes a
`0600` key file for later Git commands, and checks the tree back out through the
smudge filter. The key is never echoed, printed, or written to a log; the step
runs with `set +x`.

Fork pull requests do not receive repository secrets, so the unlock step fails
closed rather than running on ciphertext. See
[`docs/security/git-vault.md`](docs/security/git-vault.md) for the full contract.

## Limits

- Deterministic encryption reveals equality of plaintexts between files. This is
  required for stable `git status`/deduplication.
- Git LFS object payloads live on the LFS server and are **not** covered by this
  filter; only their pointer files are in Git.
- Encryption is applied to commits made after the rollout. Pre-rollout Git
  history still contains plaintext blobs until the history rewrite in
  `docs/security/git-vault.md` is executed.

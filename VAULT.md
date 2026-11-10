# Research vault

Every tracked file in this repository is stored in Git as **AES-256-SIV**
authenticated ciphertext. The working tree is plaintext only while the vault is
unlocked with the deployment secret `KEY`.

This is a Git content filter, not a normal repository. Read this before cloning
or running anything.

## What stays plaintext (bootstrap set)

GitHub parses workflows before any step can execute, and Git needs attributes
to select a filter, so these paths are deliberately **not** encrypted:

- `.gitattributes`, `.gitignore`
- `.github/**` (workflows, composite actions, CI scripts)
- `.artifacts/**` and `**/.artifacts.json` (artifact-store config and manifests read via `git show` in CI)
- `tools/vault/**` (the decryptor and the bulk encryptor)
- `VAULT.md`

Everything else, including `AGENTS.md`, `docs/`, source, the ledger and
coordination records, is ciphertext in the object store.

## Local use

```sh
export KEY=...                     # or keep `export KEY=...` in ~/.zshrc
python3 tools/vault/vaultctl.py setup
python3 tools/vault/vaultctl.py unlock
git status                          # clean: plaintext cleans back to ciphertext
```

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

# J1 attestation format correction

The initial attestation represented `sources_read` as a list of mappings with `path` and `sha256`. The independence checker requires a list of path strings. The corrected attestation uses the same sole source path as a string and records its unchanged SHA-256 under `source_hashes`. The report and verdict are unchanged. The original attestation and seal are preserved byte for byte in `initial/`.

Initial seal values:

- `report.md`: `5181973c4a314ebca5548e93dd0cd80c10d7b826afa703d99ddda1d44657cdcc`
- `initial/review_attestation.yaml`: `51e6fef124e2408adb5d058ce10b5fe1a415292a2d1c99bf7a24ef572d2ccda6`
- `initial/SHA256SUMS`: `9679d2358f2d174381f65cda430c36717c6092e92e4ed4deda51a3e8b9f19755`

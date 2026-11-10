#!/usr/bin/env python3
"""Materialise a non-git scratch copy of a crypto-autoresearcher commit for
tools/validate_ledger.py, which refuses the sparse audit checkout.

Sheriff case SHF-20261106-a114e7, ledger reader. Independent script; writes
only under OUT (a scratch directory) and never into the repository.

Every tracked path of COMMIT is created in OUT:
  * a regular file whose blob equals the blob of the same path in a LINK tree
    (the audit worktree at origin/main, or an earlier scratch tree) is a
    hardlink to it (no disk cost; read-only use only);
  * otherwise the blob is written from git when it is a text record
    (.yaml/.yml/.json/.jsonl/.md/.txt/.csv/.py/.toml/.cfg/.ini) under 1 MiB,
    or any blob under 64 KiB;
  * every other blob becomes an EMPTY placeholder, listed in
    OUT.placeholders.txt, so existence checks behave as in a full checkout
    and any check reading its bytes can be traced to a placeholder.
Symlinks are recreated from their blob. Gitlinks are skipped (listed).
"""
import os
import subprocess
import sys

TEXT = (".yaml", ".yml", ".json", ".jsonl", ".md", ".txt", ".csv", ".py",
        ".toml", ".cfg", ".ini")
REAL_TEXT_MAX = 1 << 20
REAL_ANY_MAX = 64 << 10


def ls_tree(repo, commit):
    out = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "-z", "-l", commit],
                         check=True, capture_output=True).stdout
    entries = {}
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, blob, size = meta.split()
        entries[path.decode()] = (mode.decode(), typ.decode(), blob.decode(),
                                  int(size) if size != b"-" else -1)
    return entries


def main():
    repo, commit, out = sys.argv[1], sys.argv[2], sys.argv[3]
    links = sys.argv[4:]          # pairs: LINKDIR LINKCOMMIT
    os.makedirs(out, exist_ok=False)
    tree = ls_tree(repo, commit)
    link_maps = []
    for i in range(0, len(links), 2):
        ldir, lcommit = links[i], links[i + 1]
        lmap = ls_tree(repo, lcommit)
        # Only trust a link file whose on-disk bytes are the committed blob:
        # for the audit worktree, exclude paths git reports as modified.
        dirty = set()
        if os.path.isdir(os.path.join(ldir, ".git")) or os.path.isfile(os.path.join(ldir, ".git")):
            st = subprocess.run(["git", "-C", ldir, "status", "--porcelain=v1", "-z", "-uno"],
                                check=True, capture_output=True).stdout
            for rec in st.split(b"\0"):
                if len(rec) > 3:
                    dirty.add(rec[3:].decode())
        link_maps.append((ldir, lmap, dirty))
    to_write, placeholders, gitlinks = [], [], []
    linked = 0
    for path, (mode, typ, blob, size) in tree.items():
        dest = os.path.join(out, path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if typ == "commit":
            gitlinks.append(path)
            continue
        if mode == "120000":
            target = subprocess.run(["git", "-C", repo, "cat-file", "blob", blob],
                                    check=True, capture_output=True).stdout
            os.symlink(target, dest)
            continue
        done = False
        for ldir, lmap, dirty in link_maps:
            ent = lmap.get(path)
            src = os.path.join(ldir, path)
            if (ent and ent[2] == blob and path not in dirty and os.path.isfile(src)
                    and not os.path.islink(src)
                    and (os.path.getsize(src) == size or ldir == out)):
                try:
                    os.link(src, dest)
                    linked += 1
                    done = True
                    break
                except OSError:
                    pass
        if done:
            continue
        if (path.endswith(TEXT) and size < REAL_TEXT_MAX) or size < REAL_ANY_MAX:
            to_write.append((path, blob))
        else:
            open(dest, "wb").close()
            placeholders.append(path)
    # Stream blobs through one cat-file process.
    proc = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for path, blob in to_write:
        proc.stdin.write(blob.encode() + b"\n")
        proc.stdin.flush()
        header = proc.stdout.readline().split()
        n = int(header[2])
        data = proc.stdout.read(n)
        proc.stdout.read(1)
        with open(os.path.join(out, path), "wb") as fh:
            fh.write(data)
    proc.stdin.close()
    proc.wait()
    with open(out.rstrip("/") + ".placeholders.txt", "w") as fh:
        fh.write("\n".join(sorted(placeholders)) + "\n")
    print(f"commit {commit}: {len(tree)} entries; hardlinked {linked}; written {len(to_write)}; "
          f"placeholders {len(placeholders)}; gitlinks skipped {len(gitlinks)} {gitlinks[:5]}")


if __name__ == "__main__":
    main()

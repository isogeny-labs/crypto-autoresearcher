#!/usr/bin/env python3
"""Three command steps of the EXP-SEMBIN-cb5e25 runbook (probe steps and one copy), kept in one bound file
because tools/runbook.py cannot lint an argv token longer than 255 characters.

    step_helpers.py probe --out F --experiment-dir D --sage PATH --meminfo PATH
    step_helpers.py blob --store-module tools/artifact_store.py --out F
    step_helpers.py copy --src F --dst F --out F

probe: records interpreter major version, cores, 1-minute load, free bytes at D, whether PATH exists,
       MemAvailable in kB, and the CRYPTO_AR_BLOBSTORE value, as JSON at --out.
blob:  store_from_env().put then .get of a fixed byte string; records uri, sha256, length, match as JSON.
copy:  copies --src to --dst, failing if --dst exists; records both sha256 values as JSON at --out.
Each subcommand exits 0 only after writing --out; any exception exits nonzero. Nothing here reads a result.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import sys
import tempfile

PAYLOAD = b"EXP-SEMBIN-cb5e25 blob store round trip\n"


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def probe(a):
    meminfo = dict(line.split(":", 1) for line in open(a.meminfo))
    out = {"cpus": os.cpu_count(), "py": sys.version_info[0], "load": os.getloadavg()[0],
           "disk_free": shutil.disk_usage(a.experiment_dir).free, "sage": os.path.exists(a.sage),
           "mem_kb": int(meminfo["MemAvailable"].split()[0]),
           "blobstore": os.environ.get("CRYPTO_AR_BLOBSTORE")}
    json.dump(out, open(a.out, "w"))


def blob(a):
    spec = importlib.util.spec_from_file_location("artifact_store", a.store_module)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["artifact_store"] = mod
    spec.loader.exec_module(mod)
    store = mod.store_from_env()
    work = pathlib.Path(tempfile.mkdtemp())
    source = work / "in.bin"
    source.write_bytes(PAYLOAD)
    digest = hashlib.sha256(PAYLOAD).hexdigest()
    uri = store.put(source, digest)
    target = work / "out.bin"
    store.get(uri, target)
    json.dump({"uri": uri, "sha256": digest, "length": len(PAYLOAD), "match": target.read_bytes() == PAYLOAD},
              open(a.out, "w"))


def copy(a):
    with open(a.src, "rb") as s, open(a.dst, "xb") as d:
        shutil.copyfileobj(s, d)
    json.dump({"source_sha256": sha256_file(a.src), "copy_sha256": sha256_file(a.dst)}, open(a.out, "w"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("--out", required=True)
    p.add_argument("--experiment-dir", required=True)
    p.add_argument("--sage", required=True)
    p.add_argument("--meminfo", required=True)
    p.set_defaults(fn=probe)
    p = sub.add_parser("blob")
    p.add_argument("--store-module", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(fn=blob)
    p = sub.add_parser("copy")
    p.add_argument("--src", required=True)
    p.add_argument("--dst", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(fn=copy)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

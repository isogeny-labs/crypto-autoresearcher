#!/usr/bin/env python3
"""Transport and identity check of one downloaded C1 job (PROTOCOL section 18, revision 6).

usage: python3 -I check_job.py DOWNLOAD_DIR --request REQUEST.json [--launcher-result RESULT.json]

DOWNLOAD_DIR   the job's results prefix as downloaded (SHA256SUMS, job-exit.json, ...).
--request      the frozen request that was submitted; its job name and embedded spec are the
               expected values.
--launcher-result  the launcher's result.json (default: DOWNLOAD_DIR/../launcher/result.json);
               the task image digest is read from its `build`, because the downloaded files do
               not carry it.

Checks (each prints PASS or FAIL):
  sums        SHA256SUMS lists only safe relative paths, every listed file exists with the listed
              sha256 (the bytes are hashed, never parsed), and no unlisted file is present;
  job_exit    job-exit.json exit_code in {0, 42, 43} and job_name equals the request's job name;
  binary      binary.sha256 and build-info.json carry the pinned ecbench sha256;
  source      build-info.json source_revision equals the pinned commit;
  image       the launcher result's build.image_uri equals the pinned image, and its build equals
              the request's build and build-info, and its job_name equals the request's (the job's
              exit is judged only from job-exit.json);
  l2_gate     l2-gate.json is present (its content is not read);
  spec        input-spec.json and session/spec.json equal the request's embedded spec
              (canonical JSON);
  records     session/records.jsonl has as many lines as the spec plans executions
              (curves x targets_per_curve x (warmup + rounds) x arms); the lines are counted,
              never parsed.
It does not open records.jsonl except to hash it, reads no arm data and computes no ratio.
Exit 0 only if every check passes; 1 otherwise; 2 for a usage error.
"""
import hashlib, json, os, sys

PIN_ECBENCH = "73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01"
PIN_COMMIT = "ea8e9ef71c3c82027dd9e01535302725519c3fca"
PIN_IMAGE = ("104186811093.dkr.ecr.us-east-2.amazonaws.com/isolab/tasks@sha256:"
             "3c4ad8bf8ee1bd1fdc327cb4c0e2597a1fc5ef1cdd889aa21e1b1294bdd22914")
ACCEPTED_EXIT = (0, 42, 43)
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (": " + detail) if detail else ""))
    return bool(ok)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def main(argv):
    args = argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__, file=sys.stderr); return 2
    d = args[0]; req_path = None; launcher = None
    i = 1
    while i < len(args):
        if args[i] == "--request" and i + 1 < len(args):
            req_path = args[i + 1]; i += 2
        elif args[i] == "--launcher-result" and i + 1 < len(args):
            launcher = args[i + 1]; i += 2
        else:
            print("unknown argument %r" % args[i], file=sys.stderr); return 2
    if not os.path.isdir(d) or not req_path or not os.path.isfile(req_path):
        print("usage: check_job.py DOWNLOAD_DIR --request REQUEST.json [--launcher-result RESULT.json]", file=sys.stderr)
        return 2
    request = load(req_path)
    if not isinstance(request, dict) or "job" not in request:
        print("request is not an isolab.eks.request/v1 document", file=sys.stderr); return 2
    job = request["job"]
    if launcher is None:
        launcher = os.path.join(os.path.dirname(os.path.abspath(d.rstrip("/"))), "launcher", "result.json")

    # sums
    sums_path = os.path.join(d, "SHA256SUMS")
    listed = {}
    ok_sums = os.path.isfile(sums_path)
    problems = []
    if ok_sums:
        with open(sums_path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("  ", 1)
                if len(parts) != 2 or len(parts[0]) != 64 or any(c not in "0123456789abcdef" for c in parts[0]):
                    problems.append("line %d malformed" % n); continue
                rel = parts[1]
                if rel.startswith("/") or ".." in rel.split("/") or rel == "":
                    problems.append("unsafe path %r" % rel); continue
                listed[rel] = parts[0]
        for rel, want in listed.items():
            p = os.path.join(d, rel)
            if not os.path.isfile(p):
                problems.append("missing %s" % rel)
            elif sha256_file(p) != want:
                problems.append("hash mismatch %s" % rel)
        present = set()
        for root, _, files in os.walk(d):
            for f in files:
                present.add(os.path.relpath(os.path.join(root, f), d))
        extra = sorted(present - set(listed) - {"SHA256SUMS"})
        if extra:
            problems.append("unlisted files: %s" % ", ".join(extra[:5]))
        if not listed:
            problems.append("empty SHA256SUMS")
    else:
        problems.append("SHA256SUMS absent")
    check("sums", ok_sums and not problems, "%d files listed" % len(listed) if not problems else "; ".join(problems[:5]))

    # job-exit
    je = load(os.path.join(d, "job-exit.json"))
    code = je.get("exit_code") if isinstance(je, dict) else None
    check("job_exit", isinstance(code, int) and not isinstance(code, bool) and code in ACCEPTED_EXIT
          and je.get("job_name") == job.get("job_name"),
          "exit_code=%r job_name=%r expected %r" % (code, je.get("job_name") if isinstance(je, dict) else None, job.get("job_name")))

    # binary
    bline = ""
    try:
        with open(os.path.join(d, "binary.sha256"), encoding="utf-8") as fh:
            bline = fh.read().split()[0]
    except (OSError, IndexError):
        pass
    bi = load(os.path.join(d, "build-info.json")) or {}
    check("binary", bline == PIN_ECBENCH and bi.get("ecbench_sha256") == PIN_ECBENCH,
          "binary.sha256=%s build-info=%s" % (bline[:12], str(bi.get("ecbench_sha256"))[:12]))
    check("source", bi.get("source_revision") == PIN_COMMIT, "build-info source_revision=%s" % bi.get("source_revision"))

    # image
    lr = load(launcher)
    build = lr.get("build") if isinstance(lr, dict) else None
    ok_img = (isinstance(build, dict) and build.get("image_uri") == PIN_IMAGE and build.get("source_revision") == PIN_COMMIT
              and build.get("ecbench_sha256") == PIN_ECBENCH and build == job.get("build")
              and lr.get("job_name") == job.get("job_name") and bi.get("source_revision") == build.get("source_revision"))
    check("image", ok_img, "launcher result %s: image_uri %s" % (launcher, (build or {}).get("image_uri", "absent")[-20:] if isinstance(build, dict) else "unreadable"))

    check("l2_gate", os.path.isfile(os.path.join(d, "l2-gate.json")), "present" if os.path.isfile(os.path.join(d, "l2-gate.json")) else "absent")

    # spec
    frozen = job.get("spec")
    a = load(os.path.join(d, "input-spec.json"))
    b = load(os.path.join(d, "session", "spec.json"))
    check("spec", isinstance(frozen, dict) and a is not None and b is not None and canon(a) == canon(frozen) and canon(b) == canon(frozen),
          "input-spec %s, session/spec %s the request spec" % ("equals" if a is not None and canon(a) == canon(frozen) else "differs from",
                                                           "equals" if b is not None and canon(b) == canon(frozen) else "differs from"))
    # records: newline count only, equal to the planned executions of the request's spec
    planned = None
    try:
        planned = (len(frozen["workloads"]["curves"]) * frozen["workloads"]["targets_per_curve"]
                   * (frozen["measurement"]["warmup"] + frozen["measurement"]["rounds"]) * len(frozen["arms"]))
    except (KeyError, TypeError):
        pass
    lines = None
    rp = os.path.join(d, "session", "records.jsonl")
    if os.path.isfile(rp):
        lines = 0; last = b"\n"
        with open(rp, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                lines += block.count(b"\n"); last = block[-1:]
        if last != b"\n":
            lines += 1
    check("records", planned is not None and lines == planned, "%s lines, %s planned executions" % (lines, planned))
    ok = all(c[1] for c in CHECKS)
    print("CHECK_JOB_%s" % ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

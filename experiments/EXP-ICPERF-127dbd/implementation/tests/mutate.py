#!/usr/bin/env python3
"""Mutation helper of tests/mutation_check.sh (TASK-20261107-d07e94 E-4; extended by TASK-20261107-5f7d2b V-7).

usage: python3 -I mutate.py list
       python3 -I mutate.py apply NAME SRC_IMPL_DIR DEST_IMPL_DIR

`apply` copies launch_eks.sh, locate_results.sh, reconcile_run.sh of SRC_IMPL_DIR to DEST_IMPL_DIR and removes ONE check from one of
them, naming the control (K-1 .. K-7) it belongs to. Every mutation is a text edit that must match exactly once, so a rename of a
check in the scripts makes this helper fail loudly instead of silently testing nothing.
"""
import pathlib
import re
import shutil
import sys

L, R, LAUNCH = "locate_results.sh", "reconcile_run.sh", "launch_eks.sh"


def drop_or(tag):
    """Neutralise `|| { ...; exit N; } # [TAG]` on the line that carries the tag (the check still runs, its refusal does not)."""
    return ("re", r"\|\| \{[^\n]*\} # \[" + re.escape(tag) + r"\]", "|| true # [" + tag + "]")


MUTATIONS = {
    # name: (control, file, edit)
    "K1-uri":              ("K-1", L, drop_or("K1-uri")),
    "K1-poduid":           ("K-1", L, drop_or("K1-poduid")),
    "K1-class":            ("K-1", LAUNCH, ("re", r"if \[\[ \$loc_rc == 24 && \$class != deadline_hit \]\]; then class=other; fi # \[K1-class\]", ": # [K1-class]")),
    "K2-nonempty":         ("K-2", L, drop_or("K2-nonempty")),
    "K2-nexttoken":        ("K-2", L, drop_or("K2-nexttoken")),
    "K2-keys":             ("K-2", L, drop_or("K2-keys")),
    "K2-entries":          ("K-2", L, drop_or("K2-entries")),
    "K2-listing":          ("K-2", L, drop_or("K2-listing")),
    "K2-objects":          ("K-2", L, ("re", r"\[\[ -z \$diffs \]\] \|\| \{[^\n]*\} # \[K2-objects\]", ": # [K2-objects]")),
    "K2-nonempty-and-entries": ("K-2", L, [drop_or("K2-nonempty"), drop_or("K2-entries")]),
    "K2-pin-status":       ("K-2", L, drop_or("K2-pin-status")),
    "K2-pin-objects":      ("K-2", L, drop_or("K2-pin-objects")),
    "K2-pin-lastmodified": ("K-2", L, drop_or("K2-pin-lastmodified")),
    "K2-pin-podlm":        ("K-2", L, drop_or("K2-pin-podlm")),
    "K2-wrapper-objects":  ("K-2", LAUNCH, ("re", r"else objects_check=false; located_ok=no; fi # \[K2-wrapper-objects\]", "else objects_check=false; fi # [K2-wrapper-objects]")),
    "K2-wrapper-dl":       ("K-2", LAUNCH, ("re", r"\[\[ \$dl_rc == 0 \]\] \|\| located_ok=no # \[K2-wrapper-dl\]", ": # [K2-wrapper-dl]")),
    "K4-type":             ("K-4", L, ("re", r'\(if \(\$j\.exit_code \| type\) == "number" and \(\$j\.exit_code \| tojson \| test\("\^\(0\|42\|43\)\$"\)\) and \$j\.exit_code == \$l\.pod_exit_code',
                                       '(if $j.exit_code == $l.pod_exit_code')),
    "K4-raw":              ("K-4", L, drop_or("K4-raw")),
    "K4-wrapper":          ("K-4", LAUNCH, ("re", r"if jq -e '\(\.exit_code \| type\)[^\n]*\\\n[^\n]*# \[K4-wrapper\]\n(\s*)job_exit_code=\$\(jq -r '\.exit_code \| tojson'",
                                            "if true; then # [K4-wrapper]\n\\1job_exit_code=$(jq -r '.exit_code // empty'")),
    "K4-verify":           ("K-4", L, [("re", r'\(if \(\$j\.exit_code \| type\) == "number" and \(\$j\.exit_code \| tojson \| test\("\^\(0\|42\|43\)\$"\)\) and \$j\.exit_code == \$l\.pod_exit_code',
                                       '(if $j.exit_code == $l.pod_exit_code'), drop_or("K4-raw")]),
    "K5-trap":             ("K-5", LAUNCH, ("re", r"trap 'post_crash \$LINENO' ERR", ": # K5-trap removed")),
    "K6-receipt-uuid":     ("K-6", L, drop_or("K6-receipt-uuid")),
    "K6-launcher-id":      ("K-6", L, drop_or("K6-launcher-id")),
    "K6-poduid":           ("K-6", L, drop_or("K6-poduid")),
    "K6-restart":          ("K-6", L, drop_or("K6-restart")),
    "K7-out-runs":         ("K-7", R, ("re", r"case \"/\$out/\$out_real/\" in \*/runs/\*\) echo [^\n]*\[K7-out-runs\]", ": # [K7-out-runs]")),
    "K7-out-root":         ("K-7", R, drop_or("K7-out-root")),
    "K7-endpoint":         ("K-7", R, ("re", r'\[\[ \$k7_n == AWS_ENDPOINT_URL\* \]\] && \{ echo [^\n]*exit 2; \}', ":")),
    "K7-version":          ("K-7", R, ("re", r'\[\[ \$\{k7_v%% \*\} == "\$K7_PIN_AWS_CLI" \]\] \|\| ', "")),
    "K7-config":           ("K-7", R, ("re", r"for k7_e in \$k7_cfg; do", "for k7_e in ; do")),
    "K7-allowlist":        ("K-7", R, ("re", r'\[\[ -z \$k7_extra \]\] \|\| \{', "[[ -z $k7_extra ]] || { :; } || {")),
    "K7-launch-config":    ("K-7", LAUNCH, ("re", r"for k7_e in \$k7_cfg; do", "for k7_e in ; do")),
}


# ---- v3d (TASK-20261107-5f7d2b): one mutant per new check of the K-7 prologue, in each of the two scripts that carry it (suffix -R reconcile_run.sh, -L launch_eks.sh)
V3D_TAGS = ["const-preset", "const-value", "cred-id", "cred-secret", "proxy-pair", "proxy-shape", "noproxy-pair", "noproxy-shape",
            "ca-needs-proxy", "ca-entry", "ca-realpath", "ca-file", "ca-sha"]
V3D_CFG = ["ca_bundle", "role_arn", "source_profile", "credential_source", "web_identity_token_file", "sso_session", "sso_start_url"]
for _suffix, _file in (("R", R), ("L", LAUNCH)):
    for _tag in V3D_TAGS:
        MUTATIONS[f"V3d-{_tag}-{_suffix}"] = ("K-7/v3d", _file, drop_or("K7-" + _tag))
    for _nm in V3D_CFG:   # one entry name removed from K7_CFG_NAMES
        MUTATIONS[f"V3d-cfg-{_nm}-{_suffix}"] = ("K-7/v3d", _file, ("re", r"(K7_CFG_NAMES=\([^)\n]*?) " + _nm + r"(?=[ )])", r"\1"))
    MUTATIONS[f"V3d-status-{_suffix}"] = ("K-7/v3d", _file, ("re", r' transport=\[\$\{k7_t# \}\] proxy=\$k7_px no_proxy=\$k7_np ca_bundle=\$k7_ca ca_bundle_sha256=\$k7_casha"', '"'))
    MUTATIONS[f"V3d-transport-pass-{_suffix}"] = ("K-7/v3d", _file, ("re", r'"\$\{K7_CRED_VARS\[@\]\}" "\$\{K7_TRANSPORT_VARS\[@\]\}"; do', '"${K7_CRED_VARS[@]}"; do'))
    MUTATIONS[f"V3d-transport-allowlist-{_suffix}"] = ("K-7/v3d", _file, ("re", r'\$\{K7_CRED_VARS\[\*\]\} \$\{K7_TRANSPORT_VARS\[\*\]\} "', '${K7_CRED_VARS[*]} "'))
    MUTATIONS[f"V3d-const-metadata-{_suffix}"] = ("K-7/v3d", _file, ("re", r"K7_CONSTS=\(AWS_EC2_METADATA_DISABLED=true PYTHONNOUSERSITE=1\)", "K7_CONSTS=(PYTHONNOUSERSITE=1)"))
    MUTATIONS[f"V3d-const-pyuser-{_suffix}"] = ("K-7/v3d", _file, ("re", r"K7_CONSTS=\(AWS_EC2_METADATA_DISABLED=true PYTHONNOUSERSITE=1\)", "K7_CONSTS=(AWS_EC2_METADATA_DISABLED=true)"))


def apply(name, src, dest):
    control, fname, edit = MUTATIONS[name]
    edits = edit if isinstance(edit, list) else [edit]
    src, dest = pathlib.Path(src), pathlib.Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for f in (LAUNCH, L, R):
        shutil.copy2(src / f, dest / f)
    text = (dest / fname).read_text(encoding="utf-8")
    for kind, pat, rep in edits:
        new, n = re.subn(pat, rep, text, flags=re.DOTALL if "K4-wrapper" in name else 0)
        if n != 1:
            sys.exit(f"mutate: {name}: the pattern matched {n} times in {fname}, not once")
        if new == text:
            sys.exit(f"mutate: {name}: the edit changed nothing")
        text = new
    (dest / fname).write_text(text, encoding="utf-8")
    print(f"{name} ({control}) edited {fname}: {len(edits)} match(es), one each")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "list":
        for k, (c, f, _) in MUTATIONS.items():
            print(f"{k}\t{c}\t{f}")
    elif len(sys.argv) == 5 and sys.argv[1] == "apply":
        apply(*sys.argv[2:])
    else:
        sys.exit(__doc__)

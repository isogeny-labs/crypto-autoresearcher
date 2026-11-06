"""Post-merge runs never report under a pre-merge check name.

A `pull_request_target: closed` run checks out main after the merge, and GitHub
attributes its check runs to the PR head SHA. Under the same job name, its
success replaced the head's failed pre-merge result in the PR rollup: PR #3056
merged with `lab-parity` failed, and post-merge run 42149730300 then read green
on the same head (sheriff case SHF-20261106-a114e7, CIX-2;
problems/post-merge-checks-mask-pre-merge-state.md). Every job of such a
workflow therefore carries the `post-merge / ` prefix on that event only, so
the pre-merge names (and the contexts the ruleset requires) are unchanged.
"""
from pathlib import Path
import re

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "${{ github.event_name == 'pull_request_target' && 'post-merge / ' || '' }}"


def post_merge_workflows():
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        doc = yaml.safe_load(path.read_text())
        on = doc.get(True, doc.get("on"))
        target = on.get("pull_request_target") if isinstance(on, dict) else None
        if isinstance(on, dict) and "pull_request_target" in on \
                and "closed" in ((target or {}).get("types") or []):
            yield path, doc


WORKFLOWS = list(post_merge_workflows())


def test_the_post_merge_workflows_are_found():
    names = {path.name for path, _ in WORKFLOWS}
    assert {"validate.yml", "lab-parity.yml", "lean-verification.yml",
            "progress-fidelity.yml"} <= names


@pytest.mark.parametrize("path,doc", WORKFLOWS, ids=[p.name for p, _ in WORKFLOWS])
def test_every_post_merge_job_has_a_distinct_check_name(path, doc):
    for job_id, job in doc["jobs"].items():
        name = job.get("name")
        assert isinstance(name, str) and name.startswith(PREFIX), (path.name, job_id)
        pre_merge = name[len(PREFIX):]
        assert "post-merge" not in pre_merge and "pull_request_target" not in pre_merge
        # The pull_request (pre-merge) name is the job id, or the job id with
        # its matrix values, exactly as GitHub names an unnamed job; or the
        # name the job already had.
        matrix = (job.get("strategy") or {}).get("matrix") or {}
        keys = [k for k in matrix if k not in ("include", "exclude")]
        default = job_id + (" (" + ", ".join("${{ matrix.%s }}" % k for k in keys) + ")" if keys else "")
        assert pre_merge == default or pre_merge in KEPT_NAMES, (path.name, job_id, pre_merge)


# Names jobs had before CIX-2; the pull_request name must stay exactly this.
KEPT_NAMES = {"formal workspace (lake build + axiom audit)", "harness-tests (${{ matrix.shard }}/4)"}


def test_required_pre_merge_contexts_keep_their_names():
    by_file = {path.name: doc for path, doc in WORKFLOWS}
    expected = {("validate.yml", "ledger-and-harness"): "ledger-and-harness",
                ("validate.yml", "merge-hygiene"): "merge-hygiene",
                ("progress-fidelity.yml", "progress-fidelity"): "progress-fidelity",
                ("lean-verification.yml", "formal-workspace"): "formal workspace (lake build + axiom audit)",
                ("lab-parity.yml", "parity"): "parity"}
    for (file, job), pre_merge in expected.items():
        name = by_file[file]["jobs"][job]["name"]
        assert name == PREFIX + pre_merge
        rendered_pr = name.replace(PREFIX, "")
        rendered_post = name.replace(PREFIX, "post-merge / ")
        assert rendered_pr == pre_merge and rendered_post != pre_merge


def test_the_prefix_is_an_expression_on_the_event_name_only():
    assert re.fullmatch(r"\$\{\{ github\.event_name == 'pull_request_target' && 'post-merge / ' \|\| '' \}\}",
                        PREFIX)


def test_the_validate_post_merge_ledger_still_compares_against_base():
    """Keep the #2805 fix: a merged PR's ledger is compared with its base."""
    text = (ROOT / ".github/workflows/validate.yml").read_text()
    assert ('[ "${{ github.event_name }}" = pull_request_target ]' in text
            and 'BASE_WORKTREE="$RUNNER_TEMP/validate-base-ledger"' in text)

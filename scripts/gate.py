"""Trusted tag/exact-SHA release gate using read-only GitHub metadata. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: api — line 46
# parameter: endpoint — line 46
# variable: result — line 48
# definition: successful_run — line 60
# parameter: commit — line 61
# parameter: repository — line 61
# parameter: response — line 61
# parameter: workflow — line 61
# variable: runs — line 66
# variable: ids — line 69
# variable: run — line 70
# parameter: run — line 93
# variable: latest — line 93
# definition: main — line 99
# variable: repository — line 101
# variable: reference — line 102
# variable: commit — line 103
# variable: version — line 106
# variable: policy — line 107
# variable: tag — line 108
# variable: branch — line 109
# variable: checked — line 114
# variable: workflow — line 115
# variable: response — line 116
# variable: alerts — line 120
# variable: output — line 127
# variable: stream — line 128
# END CODE MAP

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delivery.io import Rejected
from delivery.verify import REPOSITORY, TrustPolicy


def api(endpoint: str) -> dict[str, object] | list[object]:
    """Read one bounded GitHub metadata response through the existing workflow CLI token."""
    result = subprocess.run(
        ["gh", "api", "--method", "GET", endpoint],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if len(result.stdout) > 2 * 1024 * 1024:
        raise Rejected("metadata response exceeds limit")
    return json.loads(result.stdout)


def successful_run(
    response: object, repository: str, commit: str, workflow: str
) -> dict[str, object]:
    """Require returned run identities as well as query filters; never fall back past a new failure."""
    if not isinstance(response, dict) or not isinstance(response.get("workflow_runs"), list):
        raise Rejected("workflow run metadata is malformed")
    runs = response["workflow_runs"]
    if not runs:
        raise Rejected(f"exact source commit requires successful {workflow}")
    ids: set[int] = set()
    for run in runs:
        if (
            not isinstance(run, dict)
            or type(run.get("id")) is not int
            or not 1 <= run["id"] <= 2**63 - 1
        ):
            raise Rejected("workflow run identity is malformed")
        if run["id"] in ids:
            raise Rejected("duplicate workflow run identity")
        ids.add(run["id"])
        if (
            run.get("head_sha") != commit
            or run.get("head_branch") != "main"
            or run.get("event") != "push"
            or run.get("path")
            not in {
                f".github/workflows/{workflow}",
                f".github/workflows/{workflow}@main",
                f".github/workflows/{workflow}@refs/heads/main",
            }
            or run.get("html_url") != f"https://github.com/{repository}/actions/runs/{run['id']}"
        ):
            raise Rejected("workflow run does not match the independent main/source identity")
    latest = max(runs, key=lambda run: run["id"])
    if latest.get("status") != "completed" or latest.get("conclusion") != "success":
        raise Rejected(f"exact source commit requires successful {workflow}")
    return {"workflow": workflow, "id": latest["id"], "url": latest["html_url"]}


def main() -> int:
    """Allow only a matching versioned tag at main's exact successful CI/CodeQL source commit."""
    repository = os.environ["GITHUB_REPOSITORY"]
    reference = os.environ["GITHUB_REF"]
    commit = os.environ["GITHUB_SHA"]
    if repository != REPOSITORY or not reference.startswith("refs/tags/v"):
        raise Rejected("release dispatch must use a versioned tag in the intended repository")
    version = reference.removeprefix("refs/tags/v")
    policy = TrustPolicy(repository, commit, version)
    tag = api(f"repos/{repository}/git/ref/tags/v{version}")
    branch = api(f"repos/{repository}/git/ref/heads/main")
    if tag["object"] != branch["object"]:
        raise Rejected("release tag must be a lightweight tag on current main")
    if tag["object"]["sha"] != policy.commit:
        raise Rejected("tag SHA does not match the workflow context")
    checked = []
    for workflow in ("ci.yml", "codeql.yml"):
        response = api(
            f"repos/{repository}/actions/workflows/{workflow}/runs?head_sha={commit}&branch=main&event=push&per_page=100"
        )
        checked.append(successful_run(response, repository, commit, workflow))
    alerts = api(
        f"repos/{repository}/code-scanning/alerts?state=open&ref=refs/heads/main&per_page=100"
    )
    if not isinstance(alerts, list) or alerts:
        raise Rejected(
            "open code-scanning findings block release; analysis completion alone is not clearance"
        )
    output = Path(os.environ["GITHUB_OUTPUT"])
    with output.open("a", encoding="utf-8") as stream:
        stream.write(f"version={policy.version}\ncommit={policy.commit}\n")
    print(
        json.dumps(
            {
                "status": "release-gate-passed",
                "source": policy.commit,
                "checks": checked,
                "open_code_scanning_alerts": 0,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

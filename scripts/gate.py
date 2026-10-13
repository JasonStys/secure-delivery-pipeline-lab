"""Trusted tag/exact-SHA release gate using read-only GitHub metadata. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: api — line 38
# parameter: endpoint — line 38
# variable: result — line 40
# definition: main — line 48
# variable: repository — line 50
# variable: reference — line 51
# variable: commit — line 52
# variable: version — line 55
# variable: policy — line 56
# variable: tag — line 57
# variable: branch — line 58
# variable: checked — line 63
# variable: workflow — line 64
# variable: response — line 65
# parameter: item — line 68
# variable: runs — line 68
# variable: alerts — line 72
# variable: output — line 79
# variable: stream — line 80
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
        ["gh", "api", endpoint], check=True, capture_output=True, text=True, timeout=30
    )
    if len(result.stdout) > 2 * 1024 * 1024:
        raise Rejected("metadata response exceeds limit")
    return json.loads(result.stdout)


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
            f"repos/{repository}/actions/workflows/{workflow}/runs?head_sha={commit}&event=push&per_page=100"
        )
        runs = sorted(response["workflow_runs"], key=lambda item: item["id"], reverse=True)
        if not runs or runs[0]["status"] != "completed" or runs[0]["conclusion"] != "success":
            raise Rejected(f"exact source commit requires successful {workflow}")
        checked.append({"workflow": workflow, "id": runs[0]["id"], "url": runs[0]["html_url"]})
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

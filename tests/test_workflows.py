"""Workflow privilege, pinning, source gating and storage regressions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 42
# definition: test_code_map_self_reference — line 45
# variable: source — line 47
# variable: generated — line 48
# definition: test_sbom_standard_schema — line 52
# parameter: policy — line 52
# variable: document — line 60
# definition: test_workflow_security_contract — line 64
# variable: path — line 66
# variable: text — line 67
# variable: document — line 68
# variable: job — line 72
# variable: step — line 73
# variable: release — line 79
# variable: path — line 85
# definition: test_scanner_pins — line 89
# variable: lock — line 91
# variable: tool — line 93
# definition: test_exact_source_release_gate — line 102
# parameter: failure — line 103
# parameter: monkeypatch — line 103
# parameter: tmp_path — line 103
# variable: obj — line 115
# variable: tag — line 116
# variable: runs — line 117
# END CODE MAP

import json
import re
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from delivery.io import Rejected
from scripts.code_map import mapped
from scripts.gate import main as gate_main

ROOT = Path(__file__).resolve().parents[1]


def test_code_map_self_reference() -> None:
    """Generator marker string literals must not be mistaken for real header boundaries."""
    source = (ROOT / "scripts/code_map.py").read_text(encoding="utf-8")
    generated = mapped(source)
    assert mapped(generated) == generated


def test_sbom_standard_schema(policy: object) -> None:
    """Validate the actual emitted SBOM against CycloneDX's bundled JSON 1.6 schema."""
    from cyclonedx.schema import SchemaVersion
    from cyclonedx.validation.json import JsonStrictValidator

    from delivery.build import sbom
    from delivery.verify import REPOSITORY, TrustPolicy

    document = sbom(TrustPolicy(REPOSITORY, "a" * 40, "1.0.0"))
    assert JsonStrictValidator(SchemaVersion.V1_6).validate_str(json.dumps(document)) is None


def test_workflow_security_contract() -> None:
    """No mutable actions, privileged PR triggers, artifact uploads or persisted Git credentials."""
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        document = yaml.load(text, Loader=yaml.BaseLoader)
        assert "pull_request_target" not in document["on"]
        assert "workflow_run" not in document["on"]
        assert document["permissions"] == {"contents": "read"}
        for job in document["jobs"].values():
            for step in job.get("steps", []):
                if "uses" in step:
                    assert re.fullmatch(r"[\w./-]+@[a-f0-9]{40}", step["uses"])
                    assert "upload-artifact" not in step["uses"]
                    if step["uses"].startswith("actions/checkout@"):
                        assert step["with"]["persist-credentials"] == "false"
    release = yaml.load(
        (ROOT / ".github/workflows/release.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert set(release["on"]) == {"workflow_dispatch"}
    assert release["jobs"]["release"]["needs"] == "gate"
    assert release["jobs"]["release"]["permissions"]["id-token"] == "write"
    for path in ("ci.yml", "codeql.yml"):
        assert "id-token:" not in (ROOT / ".github/workflows" / path).read_text()


def test_scanner_pins() -> None:
    """Tools come from named official repositories with versioned URLs and full SHA256 pins."""
    lock = json.loads((ROOT / "tools.lock.json").read_text())
    assert set(lock["tools"]) == {"trivy", "gitleaks", "actionlint"}
    for tool in lock["tools"].values():
        assert tool["url"].startswith("https://github.com/")
        assert f"/releases/download/v{tool['version']}/" in tool["url"]
        assert re.fullmatch(r"[a-f0-9]{64}", tool["sha256"])


@pytest.mark.parametrize(
    "failure", [None, "repo", "branch", "tag", "sha", "ci", "pending", "missing"]
)
def test_exact_source_release_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str | None
) -> None:
    """A tag may publish only the exact successful current-main source and intended workflow."""
    monkeypatch.setenv(
        "GITHUB_REPOSITORY",
        "other/repo" if failure == "repo" else "JasonStys/secure-delivery-pipeline-lab",
    )
    monkeypatch.setenv(
        "GITHUB_REF", "refs/heads/main" if failure == "branch" else "refs/tags/v1.0.0"
    )
    monkeypatch.setenv("GITHUB_SHA", "b" * 40 if failure == "sha" else "a" * 40)
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "output"))
    obj = {"sha": "a" * 40, "type": "commit"}
    tag = {"object": {"sha": "b" * 40, "type": "commit"} if failure == "tag" else obj}
    runs = (
        []
        if failure == "missing"
        else [
            {
                "id": 1,
                "status": "in_progress" if failure == "pending" else "completed",
                "conclusion": "failure" if failure == "ci" else "success",
                "html_url": "https://github.com/example/run",
            }
        ]
    )
    with patch(
        "scripts.gate.api",
        side_effect=[tag, {"object": obj}, {"workflow_runs": runs}, {"workflow_runs": runs}],
    ):
        if failure:
            with pytest.raises(Rejected):
                gate_main()
        else:
            assert gate_main() == 0
            assert "commit=" + "a" * 40 in (tmp_path / "output").read_text()

"""Workflow privilege, pinning, source gating and storage regressions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 48
# definition: test_code_map_self_reference — line 51
# variable: source — line 53
# variable: generated — line 54
# definition: test_sbom_standard_schema — line 58
# parameter: policy — line 58
# variable: document — line 66
# definition: test_workflow_security_contract — line 70
# variable: path — line 72
# variable: text — line 73
# variable: document — line 74
# variable: job — line 78
# variable: step — line 79
# variable: release — line 85
# variable: path — line 91
# definition: test_sbom_attester_identity_contract — line 95
# variable: policy — line 100
# variable: document — line 101
# variable: serial — line 102
# variable: field — line 106
# definition: test_scanner_pins — line 111
# variable: lock — line 113
# variable: tool — line 115
# definition: test_exact_source_release_gate — line 124
# parameter: failure — line 125
# parameter: monkeypatch — line 125
# parameter: tmp_path — line 125
# variable: obj — line 137
# variable: tag — line 138
# variable: runs — line 139
# END CODE MAP

import json
import re
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

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


def test_sbom_attester_identity_contract() -> None:
    """The pinned attester requires a serial UUID, stable per source and different per identity."""
    from delivery.build import sbom
    from delivery.verify import REPOSITORY, TrustPolicy

    policy = TrustPolicy(REPOSITORY, "a" * 40, "1.0.1")
    document = sbom(policy)
    serial = document["serialNumber"]
    assert serial.startswith("urn:uuid:")
    assert UUID(serial.removeprefix("urn:uuid:")).version == 5
    assert document == sbom(policy)
    assert all(document[field] for field in ("bomFormat", "serialNumber", "specVersion"))
    assert serial != sbom(TrustPolicy(REPOSITORY, "b" * 40, "1.0.1"))["serialNumber"]
    assert serial != sbom(TrustPolicy(REPOSITORY, "a" * 40, "1.0.2"))["serialNumber"]


def test_scanner_pins() -> None:
    """Tools come from named official repositories with versioned URLs and full SHA256 pins."""
    lock = json.loads((ROOT / "tools.lock.json").read_text())
    assert set(lock["tools"]) == {"trivy", "gitleaks", "actionlint"}
    for tool in lock["tools"].values():
        assert tool["url"].startswith("https://github.com/")
        assert f"/releases/download/v{tool['version']}/" in tool["url"]
        assert re.fullmatch(r"[a-f0-9]{64}", tool["sha256"])


@pytest.mark.parametrize(
    "failure", [None, "repo", "branch", "tag", "sha", "ci", "pending", "missing", "alerts"]
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
        side_effect=[
            tag,
            {"object": obj},
            {"workflow_runs": runs},
            {"workflow_runs": runs},
            [{"number": 1}] if failure == "alerts" else [],
        ],
    ):
        if failure:
            with pytest.raises(Rejected):
                gate_main()
        else:
            assert gate_main() == 0
            assert "commit=" + "a" * 40 in (tmp_path / "output").read_text()

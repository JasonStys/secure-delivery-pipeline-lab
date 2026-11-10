"""Workflow privilege, pinning, source gating and storage regressions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 86
# definition: workflow_run — line 89
# parameter: changes — line 89
# parameter: workflow — line 89
# variable: result — line 91
# definition: test_code_map_self_reference — line 108
# variable: source — line 110
# variable: generated — line 111
# definition: test_sbom_standard_schema — line 115
# parameter: policy — line 115
# variable: document — line 123
# definition: test_workflow_security_contract — line 127
# variable: path — line 129
# variable: text — line 130
# variable: document — line 131
# variable: job — line 135
# variable: step — line 136
# variable: release — line 142
# variable: path — line 148
# definition: test_sbom_attester_identity_contract — line 152
# variable: policy — line 157
# variable: document — line 158
# variable: serial — line 159
# variable: field — line 163
# definition: test_scanner_pins — line 168
# variable: lock — line 170
# variable: tool — line 172
# definition: test_exact_source_release_gate — line 181
# parameter: failure — line 182
# parameter: monkeypatch — line 182
# parameter: tmp_path — line 182
# variable: obj — line 194
# variable: tag — line 195
# definition: test_release_run_identity_rejection — line 245
# parameter: changes — line 245
# definition: test_release_run_shape_rejection — line 268
# parameter: response — line 268
# definition: test_release_gate_uses_newest_attempt_without_fallback — line 274
# variable: latest — line 276
# variable: runs — line 277
# variable: selected — line 285
# variable: suffix — line 292
# definition: test_updated_release_lifecycle_with_external_signature_oracle_only — line 305
# parameter: monkeypatch — line 306
# parameter: release — line 306
# parameter: tmp_path — line 306
# parameter: with_baseline — line 306
# variable: current — line 312
# variable: baseline_policy — line 313
# variable: baseline — line 314
# variable: trusted — line 316
# variable: directory — line 320
# variable: identity — line 320
# variable: path — line 321
# definition: external_verifier — line 324
# parameter: identity — line 324
# parameter: path — line 324
# variable: native — line 339
# variable: result — line 341
# variable: case — line 347
# variable: call — line 349
# definition: test_release_version_metadata_and_notes_agree — line 357
# variable: metadata — line 361
# END CODE MAP

import hashlib
import json
import re
import subprocess
import tomllib
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

import pytest
import yaml

from delivery.io import Rejected
from scripts.code_map import mapped
from scripts.gate import main as gate_main
from scripts.gate import successful_run
from scripts.release_smoke import exercise, require_case

ROOT = Path(__file__).resolve().parents[1]


def workflow_run(workflow: str = "ci.yml", **changes: object) -> dict[str, object]:
    """Construct independent public GitHub metadata, including all trust-critical fields."""
    result = {
        "id": 1,
        "head_sha": "a" * 40,
        "head_branch": "main",
        "event": "push",
        "path": f".github/workflows/{workflow}",
        "status": "completed",
        "conclusion": "success",
        **changes,
    }
    result.setdefault(
        "html_url",
        f"https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/{result['id']}",
    )
    return result


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
    with patch(
        "scripts.gate.api",
        side_effect=[
            tag,
            {"object": obj},
            {
                "workflow_runs": []
                if failure == "missing"
                else [
                    workflow_run(
                        status="in_progress" if failure == "pending" else "completed",
                        conclusion="failure" if failure == "ci" else "success",
                    )
                ]
            },
            {"workflow_runs": [workflow_run("codeql.yml")]},
            [{"number": 1}] if failure == "alerts" else [],
        ],
    ):
        if failure:
            with pytest.raises(Rejected):
                gate_main()
        else:
            assert gate_main() == 0
            assert "commit=" + "a" * 40 in (tmp_path / "output").read_text()


@pytest.mark.parametrize(
    "changes",
    [
        {"head_sha": "b" * 40},
        {"head_branch": "feature/review"},
        {"event": "pull_request"},
        {"path": ".github/workflows/other.yml"},
        {"path": ".github/workflows/ci.yml@feature/review"},
        {"html_url": "https://github.com/Other/repo/actions/runs/1"},
        {
            "html_url": "https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/1?x=1"
        },
        {"id": True},
        {"id": 0},
        {"id": -1},
        {"id": 2**63},
        {"id": "1"},
        {"status": "in_progress"},
        {"conclusion": "failure"},
        {"conclusion": "skipped"},
    ],
)
def test_release_run_identity_rejection(changes: dict[str, object]) -> None:
    """A successful-looking response from another branch, source, event or workflow never clears release."""
    with pytest.raises(Rejected):
        successful_run(
            {"workflow_runs": [workflow_run(**changes)]},
            "JasonStys/secure-delivery-pipeline-lab",
            "a" * 40,
            "ci.yml",
        )


@pytest.mark.parametrize(
    "response",
    [
        None,
        [],
        {},
        {"workflow_runs": None},
        {"workflow_runs": []},
        {"workflow_runs": [None]},
        {"workflow_runs": [workflow_run(), workflow_run()]},
    ],
)
def test_release_run_shape_rejection(response: object) -> None:
    """Missing, malformed or duplicate run identity cannot become a successful metadata gate."""
    with pytest.raises(Rejected):
        successful_run(response, "JasonStys/secure-delivery-pipeline-lab", "a" * 40, "ci.yml")


def test_release_gate_uses_newest_attempt_without_fallback() -> None:
    """An older success cannot hide a newer failed/pending run; input order has no authority."""
    for latest in [workflow_run(id=2, conclusion="failure"), workflow_run(id=2, status="queued")]:
        for runs in [[workflow_run(), latest], [latest, workflow_run()]]:
            with pytest.raises(Rejected):
                successful_run(
                    {"workflow_runs": runs},
                    "JasonStys/secure-delivery-pipeline-lab",
                    "a" * 40,
                    "ci.yml",
                )
    selected = successful_run(
        {"workflow_runs": [workflow_run(id=2), workflow_run(conclusion="failure")]},
        "JasonStys/secure-delivery-pipeline-lab",
        "a" * 40,
        "ci.yml",
    )
    assert selected["id"] == 2
    for suffix in ["@main", "@refs/heads/main"]:
        assert (
            successful_run(
                {"workflow_runs": [workflow_run(path=".github/workflows/ci.yml" + suffix)]},
                "JasonStys/secure-delivery-pipeline-lab",
                "a" * 40,
                "ci.yml",
            )["id"]
            == 1
        )


@pytest.mark.parametrize("with_baseline", [False, True])
def test_updated_release_lifecycle_with_external_signature_oracle_only(
    release: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, with_baseline: bool
) -> None:
    """Unit-fixture trust only: run real staged zipapps, impact, receipt/retry/rollback and negative controls."""
    from delivery.build import build_release
    from delivery.verify import REPOSITORY, WORKFLOW, TrustPolicy

    current = TrustPolicy(REPOSITORY, "a" * 40, "1.0.0")
    baseline_policy = TrustPolicy(REPOSITORY, "b" * 40, "0.9.0")
    baseline = tmp_path / "baseline"
    build_release(ROOT, baseline, baseline_policy, {"fixture": "baseline"})
    trusted = {
        (identity.commit, identity.version, path.name): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for directory, identity in [(release, current), (baseline, baseline_policy)]
        for path in directory.iterdir()
    }

    def external_verifier(path: Path, identity: TrustPolicy) -> None:
        """Model only external attestation using separately captured fixture hashes and exact identity."""
        if (
            identity.repository != REPOSITORY
            or identity.workflow != WORKFLOW
            or trusted.get((identity.commit, identity.version, path.name))
            != hashlib.sha256(path.read_bytes()).hexdigest()
        ):
            raise Rejected("fictional unit signature oracle rejected changed identity/bytes")

    monkeypatch.setenv("GH_TOKEN", "never-forward-workflow-credential-fixture")
    monkeypatch.setenv("GITHUB_TOKEN", "never-forward-second-credential-fixture")
    with (
        patch("delivery.verify.verify_attestation", side_effect=external_verifier),
        patch("scripts.release_smoke.verify_attestation", side_effect=external_verifier),
        patch("scripts.release_smoke.subprocess.run", wraps=subprocess.run) as native,
    ):
        result = exercise(release, current, (baseline, baseline_policy) if with_baseline else None)
    assert result["passed"] is True
    assert result["baseline"] == (
        {"commit": "b" * 40, "version": "0.9.0"} if with_baseline else None
    )
    assert len(result["cases"]) == (19 if with_baseline else 14)
    assert all(case["passed"] is True for case in result["cases"])
    assert native.call_count >= (7 if with_baseline else 5)
    for call in native.call_args_list:
        assert call.args[0][1] == "-I"
        assert "GH_TOKEN" not in call.kwargs["env"]
        assert "GITHUB_TOKEN" not in call.kwargs["env"]
    with pytest.raises(RuntimeError, match="Release acceptance failed"):
        require_case("independent false control", False)


def test_release_version_metadata_and_notes_agree() -> None:
    """An advertised package version must match runtime metadata and an authored release-note file."""
    from delivery import __version__

    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert metadata["project"]["version"] == __version__
    assert (ROOT / f"docs/releases/v{__version__}.md").is_file()

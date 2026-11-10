"""Workflow privilege, pinning, source gating and storage regressions. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 99
# definition: workflow_run — line 102
# parameter: changes — line 102
# parameter: workflow — line 102
# variable: result — line 104
# definition: test_code_map_self_reference — line 121
# variable: source — line 123
# variable: generated — line 124
# definition: test_sbom_standard_schema — line 128
# parameter: policy — line 128
# variable: document — line 136
# definition: test_workflow_security_contract — line 140
# variable: path — line 142
# variable: text — line 143
# variable: document — line 144
# variable: job — line 148
# variable: step — line 149
# variable: release — line 155
# variable: path — line 161
# definition: test_sbom_attester_identity_contract — line 165
# variable: policy — line 170
# variable: document — line 171
# variable: serial — line 172
# variable: field — line 176
# definition: test_scanner_pins — line 181
# variable: lock — line 183
# variable: tool — line 185
# definition: test_exact_source_release_gate — line 194
# parameter: failure — line 195
# parameter: monkeypatch — line 195
# parameter: tmp_path — line 195
# variable: obj — line 207
# variable: tag — line 208
# definition: test_release_run_identity_rejection — line 258
# parameter: changes — line 258
# definition: test_release_run_shape_rejection — line 281
# parameter: response — line 281
# definition: test_release_gate_uses_newest_attempt_without_fallback — line 287
# variable: latest — line 289
# variable: runs — line 290
# variable: selected — line 298
# variable: suffix — line 305
# definition: test_updated_release_lifecycle_with_external_signature_oracle_only — line 318
# parameter: monkeypatch — line 319
# parameter: release — line 319
# parameter: tmp_path — line 319
# parameter: with_baseline — line 319
# variable: current — line 325
# variable: baseline_policy — line 326
# variable: baseline — line 327
# variable: trusted — line 329
# variable: directory — line 333
# variable: identity — line 333
# variable: path — line 334
# definition: external_verifier — line 337
# parameter: identity — line 337
# parameter: path — line 337
# variable: original_temporary_directory — line 349
# definition: aliased_temporary_directory — line 353
# parameter: args — line 353
# parameter: kwargs — line 353
# variable: directory — line 355
# variable: owned — line 356
# definition: canonical_export — line 363
# parameter: document — line 363
# parameter: output — line 363
# variable: native — line 376
# variable: result — line 378
# variable: case — line 384
# variable: call — line 386
# definition: test_release_version_metadata_and_notes_agree — line 394
# variable: metadata — line 398
# END CODE MAP

import hashlib
import json
import re
import subprocess
import tempfile
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
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
    original_temporary_directory = tempfile.TemporaryDirectory
    from delivery.impact import export as actual_export

    @contextmanager
    def aliased_temporary_directory(*args: Any, **kwargs: Any) -> Iterator[str]:
        """Return a noncanonical spelling of the owned smoke root on every OS, without changing its owner."""
        with original_temporary_directory(*args, **kwargs) as directory:
            owned = Path(directory)
            yield (
                str(owned / ".." / owned.name)
                if kwargs.get("prefix") == "delivery-live-smoke-"
                else directory
            )

    def canonical_export(document: dict[str, Any], output: Path) -> None:
        """Assert the independent path oracle before invoking the unchanged strict real export."""
        assert output == output.resolve()
        actual_export(document, output)

    with (
        patch("delivery.verify.verify_attestation", side_effect=external_verifier),
        patch("scripts.release_smoke.verify_attestation", side_effect=external_verifier),
        patch(
            "scripts.release_smoke.tempfile.TemporaryDirectory",
            side_effect=aliased_temporary_directory,
        ),
        patch("scripts.release_smoke.export", side_effect=canonical_export),
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

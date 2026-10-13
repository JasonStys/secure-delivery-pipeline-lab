"""Reproducibility, evidence gates, real zipapp smoke and atomic rollback. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_reproducible_application — line 79
# parameter: policy — line 79
# variable: root — line 81
# variable: document — line 83
# definition: test_real_zipapp — line 88
# parameter: policy — line 88
# parameter: release — line 88
# variable: payload — line 90
# variable: root — line 92
# variable: result — line 93
# definition: test_build_refuses_existing_output — line 102
# parameter: policy — line 102
# parameter: release — line 102
# definition: test_evidence_gate — line 111
# parameter: failure — line 111
# parameter: tmp_path — line 111
# variable: benchmark — line 113
# variable: coverage — line 113
# variable: junit — line 113
# variable: name — line 114
# definition: test_promotion_and_rollback — line 133
# parameter: policy — line 133
# parameter: release — line 133
# parameter: tmp_path — line 133
# variable: root — line 135
# variable: later — line 136
# variable: second — line 137
# variable: verifier — line 139
# variable: first — line 140
# variable: newer — line 143
# variable: rolled_back — line 145
# definition: test_failed_health_and_identity_preserve_active — line 151
# parameter: policy — line 152
# parameter: release — line 152
# parameter: tmp_path — line 152
# variable: root — line 155
# variable: original — line 158
# definition: test_rollback_target_and_tamper — line 176
# parameter: policy — line 176
# parameter: release — line 176
# parameter: tmp_path — line 176
# variable: root — line 178
# definition: test_owned_root_boundaries — line 187
# parameter: tmp_path — line 187
# variable: root — line 189
# variable: clean — line 195
# definition: test_health_failures — line 214
# parameter: failure — line 214
# parameter: policy — line 214
# parameter: release — line 214
# variable: error — line 216
# variable: result — line 217
# definition: test_cli — line 227
# parameter: capsys — line 228
# parameter: policy — line 228
# parameter: release — line 228
# parameter: tmp_path — line 228
# variable: arguments — line 231
# END CODE MAP

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from delivery.__main__ import main
from delivery.build import application_bytes, build_release, sbom
from delivery.build import test_evidence as evidence_from_tests
from delivery.deploy import deployment_lock, health_check, owned_root, promote, rollback, state
from delivery.io import Rejected, canonical, read_bytes
from delivery.verify import TrustPolicy


def test_reproducible_application(policy: TrustPolicy) -> None:
    """Same source/identity produces byte-identical payloads and an explicit SBOM scope."""
    root = Path(__file__).resolve().parents[1]
    assert application_bytes(root, policy) == application_bytes(root, policy)
    document = sbom(policy)
    assert document["components"] == []
    assert "supplied separately" in document["metadata"]["properties"][0]["value"]


def test_real_zipapp(release: Path, policy: TrustPolicy) -> None:
    """Execute the authored unsigned fixture directly; this is not a signature claim."""
    payload = release / f"release-probe-{policy.version}.pyz"
    health_check(payload)
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-I", str(payload), "--input", str(root / "examples/inventory.json")],
        check=True,
        text=True,
        capture_output=True,
    )
    assert json.loads(result.stdout)["inventory_value_usd"] == "1727.40"


def test_build_refuses_existing_output(release: Path, policy: TrustPolicy) -> None:
    """A rebuild cannot silently overwrite previously recorded evidence or release bytes."""
    with pytest.raises(Rejected):
        build_release(Path(__file__).resolve().parents[1], release, policy, {})


@pytest.mark.parametrize(
    "failure", [None, "tests", "coverage", "performance", "malformed", "skipped"]
)
def test_evidence_gate(tmp_path: Path, failure: str | None) -> None:
    """Release evidence must represent real all-passing results, not arbitrary success labels."""
    junit, coverage, benchmark = [
        tmp_path / name for name in ("junit.xml", "coverage.json", "benchmark.json")
    ]
    junit.write_text(
        f'<testsuites><testsuite tests="4" failures="{1 if failure == "tests" else 0}" skipped="{1 if failure == "skipped" else 0}"/></testsuites>',
        encoding="utf-8",
    )
    coverage.write_bytes(
        canonical({"totals": {"percent_covered": 70 if failure == "coverage" else 95}})
    )
    benchmark.write_bytes(canonical({"schema": 1, "passed": failure != "performance"}))
    if failure == "malformed":
        junit.write_text("broken XML", encoding="utf-8")
    if failure:
        with pytest.raises(Rejected):
            evidence_from_tests(junit, coverage, benchmark)
    else:
        assert evidence_from_tests(junit, coverage, benchmark)["tests"]["tests"] == 4


def test_promotion_and_rollback(tmp_path: Path, release: Path, policy: TrustPolicy) -> None:
    """Fake only signature service: real staged bytes, health, slots and atomic pointers run."""
    root = tmp_path / "lab"
    later = TrustPolicy(policy.repository, "b" * 40, policy.version)
    second = tmp_path / "second"
    build_release(Path(__file__).resolve().parents[1], second, later, {"fixture": True})
    with patch("delivery.verify.verify_attestation") as verifier:
        first = promote(release, root, policy)
        assert first["previous"] is None
        assert promote(release, root, policy) == first
        newer = promote(second, root, later)
        assert newer["previous"] == first["active"]
        rolled_back = rollback(root, policy)
        assert rolled_back["active"] == first["active"]
        assert rolled_back["previous"] == newer["active"]
        assert verifier.call_count >= 16


def test_failed_health_and_identity_preserve_active(
    tmp_path: Path, release: Path, policy: TrustPolicy
) -> None:
    """Broken health or unavailable authentication cannot replace the last known-good pointer."""
    root = tmp_path / "lab"
    with patch("delivery.verify.verify_attestation"):
        promote(release, root, policy)
    original = read_bytes(root / "active.json")
    with (
        patch(
            "delivery.verify.verify_attestation", side_effect=Rejected("fixture verifier outage")
        ),
        pytest.raises(Rejected),
    ):
        promote(release, root, policy)
    with (
        patch("delivery.verify.verify_attestation"),
        patch("delivery.deploy.health_check", side_effect=Rejected("fixture health failure")),
        pytest.raises(Rejected),
    ):
        promote(release, root, policy)
    assert read_bytes(root / "active.json") == original
    assert not list((root / "slots").glob(".stage-*"))


def test_rollback_target_and_tamper(tmp_path: Path, release: Path, policy: TrustPolicy) -> None:
    """No implicit downgrade: rollback requires the explicit previous identity and intact bytes."""
    root = tmp_path / "lab"
    with patch("delivery.verify.verify_attestation"):
        promote(release, root, policy)
    with pytest.raises(Rejected):
        rollback(root, policy)
    with pytest.raises(Rejected):
        promote(release, root, policy, expected_previous="changed")


def test_owned_root_boundaries(tmp_path: Path) -> None:
    """Existing unrelated directories, unexpected files and corrupt pointers are preserved."""
    root = tmp_path / "unrelated"
    root.mkdir()
    (root / "important.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(Rejected):
        owned_root(root)
    assert (root / "important.txt").read_text() == "keep"
    clean = owned_root(tmp_path / "lab")
    with deployment_lock(clean), pytest.raises(Rejected), deployment_lock(clean):
        pass
    (clean / "active.json").write_bytes(
        canonical({"schema": 1, "active": "../outside", "previous": None})
    )
    with pytest.raises(Rejected):
        state(clean)
    (clean / "active.json").write_bytes(
        canonical({"schema": True, "active": None, "previous": None})
    )
    with pytest.raises(Rejected):
        state(clean)
    (clean / "extra").write_bytes(b"fixture")
    with pytest.raises(Rejected):
        owned_root(clean)


@pytest.mark.parametrize("failure", ["nonzero", "json", "timeout"])
def test_health_failures(release: Path, policy: TrustPolicy, failure: str) -> None:
    """Health exceptions, malformed output and nonzero exits are not promotion success."""
    error = subprocess.TimeoutExpired("probe", 15) if failure == "timeout" else None
    result = subprocess.CompletedProcess(
        [], 1 if failure == "nonzero" else 0, stdout="invalid" if failure == "json" else "{}"
    )
    with (
        patch("delivery.deploy.subprocess.run", return_value=result, side_effect=error),
        pytest.raises(Rejected),
    ):
        health_check(release / f"release-probe-{policy.version}.pyz")


def test_cli(
    release: Path, policy: TrustPolicy, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Expose integrity-only wording and authenticated commands without a bypass flag."""
    arguments = [
        "--directory",
        str(release),
        "--version",
        policy.version,
        "--commit",
        policy.commit,
    ]
    assert main(["preflight", *arguments]) == 0
    assert "not-authenticated" in capsys.readouterr().out
    with patch("delivery.verify.verify_attestation"):
        assert main(["verify", *arguments]) == 0
        assert main(["promote", *arguments, "--root", str(tmp_path / "lab")]) == 0
    assert main(["rollback", *arguments, "--root", str(tmp_path / "lab")]) == 2
    assert main(["verify", "--version", "bad", "--commit", policy.commit]) == 2
    with pytest.raises(SystemExit):
        main(["verify", "--version", policy.version, "--commit", policy.commit])
    with pytest.raises(SystemExit):
        main(["rollback", "--version", policy.version, "--commit", policy.commit])

"""Verified byte review and atomic bounded receipt workflows. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: newer — line 96
# parameter: policy — line 96
# parameter: tmp_path — line 96
# variable: later — line 98
# variable: directory — line 99
# definition: test_verified_impact_without_execution — line 104
# parameter: policy — line 105
# parameter: release — line 105
# parameter: tmp_path — line 105
# variable: candidate — line 108
# variable: later — line 108
# variable: root — line 109
# variable: before — line 112
# variable: verifier — line 114
# variable: health — line 115
# variable: result — line 117
# variable: changes — line 120
# variable: row — line 120
# variable: row — line 124
# definition: test_impact_authentication_and_active_identity_fail_closed — line 132
# parameter: policy — line 133
# parameter: release — line 133
# parameter: tmp_path — line 133
# variable: candidate — line 136
# variable: later — line 136
# variable: root — line 137
# variable: before — line 143
# definition: test_atomic_receipt_and_rollback — line 160
# parameter: policy — line 160
# parameter: release — line 160
# parameter: tmp_path — line 160
# variable: candidate — line 162
# variable: later — line 162
# variable: root — line 163
# variable: first — line 165
# variable: second — line 172
# variable: final — line 173
# definition: test_write_failure_preserves_both_pointer_and_receipts — line 180
# parameter: policy — line 181
# parameter: release — line 181
# parameter: tmp_path — line 181
# variable: candidate — line 184
# variable: later — line 184
# variable: root — line 185
# variable: before — line 188
# definition: fail_pointer — line 190
# parameter: data — line 190
# parameter: path — line 190
# definition: test_bounded_retention_and_legacy_migration — line 206
# parameter: policy — line 207
# parameter: release — line 207
# parameter: tmp_path — line 207
# variable: old_slot — line 210
# variable: previous — line 211
# variable: number — line 212
# variable: identity — line 213
# variable: previous — line 214
# variable: root — line 225
# variable: migrated — line 231
# definition: test_corrupt_receipts_rejected — line 254
# parameter: bad — line 254
# parameter: policy — line 254
# parameter: release — line 254
# variable: result — line 256
# variable: rows — line 265
# variable: row — line 266
# variable: rows — line 268
# definition: test_actual_impact_cli — line 297
# parameter: capsys — line 298
# parameter: policy — line 298
# parameter: release — line 298
# parameter: tmp_path — line 298
# variable: candidate — line 301
# variable: later — line 301
# variable: root — line 302
# END CODE MAP

import copy
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from delivery.__main__ import main
from delivery.build import build_release
from delivery.deploy import promote, rollback, state
from delivery.impact import export, review
from delivery.io import Rejected, atomic_write, canonical, read_bytes
from delivery.receipts import committed, validate
from delivery.verify import TrustPolicy


def newer(tmp_path: Path, policy: TrustPolicy) -> tuple[Path, TrustPolicy]:
    """Build an independently selected fictional second identity; its unsigned status is explicit."""
    later = TrustPolicy(policy.repository, "b" * 40, "1.0.1")
    directory = tmp_path / "candidate"
    build_release(Path(__file__).resolve().parents[1], directory, later, {"fixture": "later"})
    return directory, later


def test_verified_impact_without_execution(
    release: Path, policy: TrustPolicy, tmp_path: Path
) -> None:
    """Mock only the external signature service; authenticate every staged asset and never execute in review."""
    candidate, later = newer(tmp_path, policy)
    root = tmp_path / "lab"
    with patch("delivery.verify.verify_attestation"):
        promote(release, root, policy)
    before = read_bytes(root / "active.json")
    with (
        patch("delivery.verify.verify_attestation") as verifier,
        patch("delivery.deploy.health_check") as health,
    ):
        result = review(candidate, root, later, policy)
        assert verifier.call_count == 8
        health.assert_not_called()
    changes = {row["name"]: row["change"] for row in result["members"]}
    assert changes["BUILD.json"] == "changed"
    assert changes["delivery/probe.py"] == "unchanged"
    assert result["candidate_identity"]["commit"] == "b" * 40
    assert [row["changed"] for row in result["assets"]] == [True, True, True]
    assert read_bytes(root / "active.json") == before
    export(result, tmp_path / "impact")
    assert "Jason Stys" in (tmp_path / "impact/impact.html").read_text()
    with pytest.raises(OSError):
        export(result, tmp_path / "impact")


def test_impact_authentication_and_active_identity_fail_closed(
    release: Path, policy: TrustPolicy, tmp_path: Path
) -> None:
    """Integrity-only or caller-mismatched current policy never becomes a verified comparison."""
    candidate, later = newer(tmp_path, policy)
    root = tmp_path / "lab"
    with pytest.raises(Rejected):
        review(candidate, root, later, policy)
    assert not root.exists()
    with patch("delivery.verify.verify_attestation"):
        promote(release, root, policy)
    before = read_bytes(root / "active.json")
    with pytest.raises(Rejected):
        review(candidate, root, later, later)
    with (
        patch(
            "delivery.verify.verify_attestation",
            side_effect=Rejected("fixture service unavailable"),
        ),
        pytest.raises(Rejected),
    ):
        review(candidate, root, later, policy)
    (candidate / "validation.json").write_bytes(b"tampered")
    with pytest.raises(Rejected):
        review(candidate, root, later, policy)
    assert read_bytes(root / "active.json") == before


def test_atomic_receipt_and_rollback(release: Path, policy: TrustPolicy, tmp_path: Path) -> None:
    """Successful transitions commit exact trust context with the pointer; replays do not create extra receipts."""
    candidate, later = newer(tmp_path, policy)
    root = tmp_path / "lab"
    with patch("delivery.verify.verify_attestation"):
        first = promote(
            release, root, policy, operator="Fictional release engineer", change_ref="CHG-101"
        )
        assert first["schema"] == 2 and len(first["receipts"]) == 1
        assert first["receipts"][0]["change_ref"] == "CHG-101"
        assert first["receipts"][0]["identity"]["commit"] == policy.commit
        assert promote(release, root, policy) == first
        second = promote(candidate, root, later)
        final = rollback(root, policy, operator="Fictional recovery engineer", change_ref="INC-102")
    assert len(second["receipts"]) == 2 and len(final["receipts"]) == 3
    assert final["receipts"][-1]["action"] == "rollback"
    assert final["receipts"][-1]["operator"] == "Fictional recovery engineer"
    assert state(root) == final


def test_write_failure_preserves_both_pointer_and_receipts(
    release: Path, policy: TrustPolicy, tmp_path: Path
) -> None:
    """A failed final commit never records success separately or damages the old active state."""
    candidate, later = newer(tmp_path, policy)
    root = tmp_path / "lab"
    with patch("delivery.verify.verify_attestation"):
        promote(release, root, policy)
    before = read_bytes(root / "active.json")

    def fail_pointer(path: Path, data: bytes) -> None:
        """Inject only the commit-write failure, retaining real staged-copy and verification operations."""
        if path.name == "active.json":
            raise OSError("fixture storage failure")
        atomic_write(path, data)

    with (
        patch("delivery.verify.verify_attestation"),
        patch("delivery.deploy.atomic_write", side_effect=fail_pointer),
        pytest.raises(OSError),
    ):
        promote(candidate, root, later)
    assert read_bytes(root / "active.json") == before
    assert len(state(root)["receipts"]) == 1


def test_bounded_retention_and_legacy_migration(
    release: Path, policy: TrustPolicy, tmp_path: Path
) -> None:
    """Atomic schema2 keeps the newest20 transitions; legacy schema1 gains only honest new history."""
    old_slot = f"v1.0.0-{'c' * 40}"
    previous = {"schema": 1, "active": old_slot, "previous": None}
    for number in range(1, 26):
        identity = TrustPolicy(policy.repository, f"{number:040x}", policy.version)
        previous = committed(
            previous,
            f"v{identity.version}-{identity.commit}",
            identity,
            release,
            "promote",
            "fixture",
            "CHG-1",
        )
    assert len(previous["receipts"]) == 20
    assert previous["receipts"][0]["sequence"] == 6 and previous["receipts"][-1]["sequence"] == 25
    root = tmp_path / "lab"
    with patch("delivery.verify.verify_attestation"):
        promote(release, root, policy)
        (root / "active.json").write_bytes(
            canonical({"schema": 1, "active": old_slot, "previous": None})
        )
        migrated = promote(release, root, policy)
    assert len(migrated["receipts"]) == 1
    assert migrated["receipts"][0]["from"] == old_slot


@pytest.mark.parametrize(
    "bad",
    [
        "bound",
        "fields",
        "sequence",
        "action",
        "health",
        "slot",
        "identity",
        "digest",
        "context",
        "timestamp",
        "calendar",
        "chain",
        "pointer",
    ],
)
def test_corrupt_receipts_rejected(release: Path, policy: TrustPolicy, bad: str) -> None:
    """Private state is untrusted metadata; malformed history is never silently reset or used as trust."""
    result = committed(
        {"active": None},
        f"v{policy.version}-{policy.commit}",
        policy,
        release,
        "promote",
        "fixture",
        "CHG-1",
    )
    rows = copy.deepcopy(result["receipts"])
    row = rows[0]
    if bad == "bound":
        rows = []
    elif bad == "fields":
        row["extra"] = "x"
    elif bad == "sequence":
        row["sequence"] = True
    elif bad == "action":
        row["action"] = "deploy-anything"
    elif bad == "health":
        row["health"] = "unknown"
    elif bad == "slot":
        row["to"] = "../outside"
    elif bad == "identity":
        row["identity"] = {}
    elif bad == "digest":
        row["manifest_sha256"] = "x"
    elif bad == "context":
        row["operator"] = "   "
    elif bad == "timestamp":
        row["verified_at"] = "today"
    elif bad == "calendar":
        row["verified_at"] = "2026-02-30T00:00:00Z"
    elif bad == "chain":
        rows.append(copy.deepcopy(row))
    else:
        row["from"] = f"v1.0.0-{'d' * 40}"
    with pytest.raises(Rejected):
        validate(rows, result["active"], result["previous"])


def test_actual_impact_cli(
    release: Path, policy: TrustPolicy, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The release engineer can produce impact evidence with independently supplied current/candidate trust."""
    candidate, later = newer(tmp_path, policy)
    root = tmp_path / "lab"
    with patch("delivery.verify.verify_attestation"):
        promote(release, root, policy)
        assert (
            main(
                [
                    "impact",
                    "--directory",
                    str(candidate),
                    "--root",
                    str(root),
                    "--commit",
                    later.commit,
                    "--version",
                    later.version,
                    "--active-commit",
                    policy.commit,
                    "--active-version",
                    policy.version,
                    "--out",
                    str(tmp_path / "review"),
                ]
            )
            == 0
        )
    assert json.loads(capsys.readouterr().out)["kind"] == "authenticated_release_impact"
    with pytest.raises(SystemExit):
        main(
            [
                "impact",
                "--directory",
                str(candidate),
                "--root",
                str(root),
                "--commit",
                later.commit,
                "--version",
                later.version,
            ]
        )

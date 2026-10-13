"""Fail-closed release and GitHub identity verification. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: REPOSITORY — line 64
# variable: WORKFLOW — line 65
# definition: TrustPolicy — line 69
# variable: repository — line 72
# variable: commit — line 73
# variable: version — line 74
# variable: workflow — line 75
# definition: __post_init__ — line 77
# parameter: self — line 77
# definition: names — line 91
# parameter: self — line 91
# definition: inspect_payload — line 96
# parameter: path — line 96
# variable: archive — line 99
# variable: entries — line 100
# variable: expected — line 101
# variable: entry — line 109
# variable: total — line 111
# variable: entry — line 112
# variable: total — line 113
# definition: preflight — line 124
# parameter: directory — line 124
# parameter: policy — line 124
# variable: actual_names — line 128
# variable: path — line 128
# variable: manifest — line 131
# variable: source — line 134
# variable: assets — line 146
# variable: seen — line 149
# variable: asset — line 150
# variable: digest — line 153
# variable: name — line 153
# variable: size — line 153
# variable: data — line 163
# definition: verify_attestation — line 171
# parameter: path — line 171
# parameter: policy — line 171
# variable: executable — line 173
# variable: command — line 176
# variable: result — line 198
# definition: verify_release — line 205
# parameter: directory — line 205
# parameter: policy — line 205
# variable: manifest — line 207
# variable: name — line 208
# END CODE MAP

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from delivery.io import Rejected, load_json, read_bytes

REPOSITORY = "JasonStys/secure-delivery-pipeline-lab"
WORKFLOW = ".github/workflows/release.yml"


@dataclass(frozen=True)
class TrustPolicy:
    """Independent caller-selected repository, exact commit, tag version and workflow."""

    repository: str
    commit: str
    version: str
    workflow: str = WORKFLOW

    def __post_init__(self) -> None:
        """Validate every field before any path construction or external process call."""
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repository):
            raise Rejected("invalid trusted repository")
        if not re.fullmatch(r"[0-9a-f]{40}", self.commit):
            raise Rejected("expected an independently obtained full commit SHA")
        if not re.fullmatch(
            r"(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})", self.version
        ):
            raise Rejected("expected a stable three-part release version")
        if not re.fullmatch(r"\.github/workflows/[a-z][a-z0-9-]*\.yml", self.workflow):
            raise Rejected("invalid trusted workflow")

    @property
    def names(self) -> set[str]:
        """Return the exact release-asset allowlist for this version."""
        return {f"release-probe-{self.version}.pyz", "sbom.cdx.json", "validation.json"}


def inspect_payload(path: Path) -> None:
    """Reject malformed, extra-member, linked, encrypted, or oversized zip applications."""
    try:
        with zipfile.ZipFile(BytesIO(read_bytes(path))) as archive:
            entries = archive.infolist()
            expected = {
                "__main__.py",
                "delivery/__init__.py",
                "delivery/io.py",
                "delivery/probe.py",
                "LICENSE",
                "BUILD.json",
            }
            if len(entries) != len(expected) or {entry.filename for entry in entries} != expected:
                raise Rejected("unexpected application archive contents")
            total = 0
            for entry in entries:
                total += entry.file_size
                if entry.flag_bits & 1 or entry.external_attr >> 16 & 0o170000 not in (0, 0o100000):
                    raise Rejected("unsupported archive member")
                if entry.file_size > 512 * 1024 or total > 1024 * 1024:
                    raise Rejected("expanded application size exceeds limit")
                if len(archive.read(entry)) != entry.file_size:
                    raise Rejected("archive member changed")
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        raise Rejected("invalid application archive") from error


def preflight(directory: Path, policy: TrustPolicy) -> dict[str, Any]:
    """Check structure and hashes only; this is NOT authentication or permission to run."""
    if directory.is_symlink() or directory.is_junction() or not directory.is_dir():
        raise Rejected("release directory must be a regular directory")
    actual_names = {path.name for path in directory.iterdir()}
    if actual_names != policy.names | {"release.json"}:
        raise Rejected("release directory does not match the asset allowlist")
    manifest = load_json(directory / "release.json", 64 * 1024)
    if not isinstance(manifest, dict) or set(manifest) != {"schema", "version", "source", "assets"}:
        raise Rejected("unexpected manifest fields")
    source = {
        "repository": policy.repository,
        "commit": policy.commit,
        "ref": f"refs/tags/v{policy.version}",
    }
    if (
        type(manifest["schema"]) is not int
        or manifest["schema"] != 1
        or manifest["version"] != policy.version
        or manifest["source"] != source
    ):
        raise Rejected("manifest does not match the independent trust policy")
    assets = manifest["assets"]
    if not isinstance(assets, list) or len(assets) != 3:
        raise Rejected("expected exactly three release assets")
    seen: set[str] = set()
    for asset in assets:
        if not isinstance(asset, dict) or set(asset) != {"name", "size", "sha256"}:
            raise Rejected("invalid asset record")
        name, size, digest = asset["name"], asset["size"], asset["sha256"]
        if not isinstance(name, str) or name not in policy.names or name in seen:
            raise Rejected("unapproved or duplicate asset name")
        if (
            type(size) is not int
            or not 1 <= size <= 2 * 1024 * 1024
            or not isinstance(digest, str)
            or not re.fullmatch(r"[a-f0-9]{64}", digest)
        ):
            raise Rejected("invalid asset size or digest")
        data = read_bytes(directory / name)
        if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
            raise Rejected("asset integrity mismatch")
        seen.add(name)
    inspect_payload(directory / f"release-probe-{policy.version}.pyz")
    return manifest


def verify_attestation(path: Path, policy: TrustPolicy) -> None:
    """Require GitHub CLI's cryptographic verification under an exact signer/source policy."""
    executable = shutil.which("gh")
    if executable is None:
        raise Rejected("GitHub CLI is required; there is no checksum-only fallback")
    command = [
        executable,
        "attestation",
        "verify",
        str(path.resolve()),
        "--hostname",
        "github.com",
        "--repo",
        policy.repository,
        "--signer-workflow",
        f"{policy.repository}/{policy.workflow}",
        "--signer-digest",
        policy.commit,
        "--source-digest",
        policy.commit,
        "--source-ref",
        f"refs/tags/v{policy.version}",
        "--deny-self-hosted-runners",
        "--predicate-type",
        "https://slsa.dev/provenance/v1",
    ]
    try:
        result = subprocess.run(command, capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Rejected("provenance verification unavailable; release not accepted") from error
    if result.returncode != 0:
        raise Rejected("release provenance or trusted identity was rejected")


def verify_release(directory: Path, policy: TrustPolicy) -> dict[str, Any]:
    """Authenticate the manifest and every asset; never infer trust from their own claims."""
    manifest = preflight(directory, policy)
    for name in ["release.json", *sorted(policy.names)]:
        verify_attestation(directory / name, policy)
    return manifest

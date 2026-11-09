"""Authenticate staged candidate/current assets before nonexecuting impact review. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: stage — line 62
# parameter: output — line 62
# parameter: policy — line 62
# parameter: source — line 62
# variable: name — line 66
# definition: members — line 71
# parameter: directory — line 71
# parameter: policy — line 71
# variable: archive — line 73
# variable: name — line 74
# definition: review — line 77
# parameter: active_policy — line 78
# parameter: candidate — line 78
# parameter: candidate_policy — line 78
# parameter: root — line 78
# variable: root — line 81
# variable: temporary — line 82
# variable: staging — line 83
# variable: current — line 85
# variable: expected — line 86
# variable: before — line 89
# variable: after — line 90
# variable: old_members — line 91
# variable: new_members — line 92
# variable: roles — line 93
# variable: new_name — line 94
# variable: old_name — line 94
# variable: role — line 94
# variable: asset — line 103
# variable: old — line 103
# variable: asset — line 104
# variable: new — line 104
# variable: name — line 141
# definition: export — line 147
# parameter: output — line 147
# parameter: result — line 147
# variable: absolute — line 149
# variable: part — line 150
# variable: text — line 152
# variable: rows — line 153
# variable: row — line 155
# variable: page — line 157
# END CODE MAP

from __future__ import annotations

import hashlib
import html
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from delivery.deploy import deployment_lock, owned_root, state
from delivery.io import Rejected, atomic_write, canonical, read_bytes
from delivery.verify import TrustPolicy, preflight, verify_release


def stage(source: Path, output: Path, policy: TrustPolicy) -> dict[str, Any]:
    """Copy exact allowlisted bytes and authenticate the private snapshot; do not execute the payload."""
    preflight(source, policy)
    output.mkdir(mode=0o700)
    for name in ("release.json", *sorted(policy.names)):
        atomic_write(output / name, read_bytes(source / name))
    return verify_release(output, policy)


def members(directory: Path, policy: TrustPolicy) -> dict[str, str]:
    """Hash already-authenticated bounded archive members without extraction, import or execution."""
    with zipfile.ZipFile(directory / f"release-probe-{policy.version}.pyz") as archive:
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}


def review(
    candidate: Path, root: Path, candidate_policy: TrustPolicy, active_policy: TrustPolicy
) -> dict[str, Any]:
    """Compare exact authenticated asset/member hashes against a caller-trusted currently active slot."""
    root = owned_root(root, initialize=False)
    with tempfile.TemporaryDirectory(prefix="delivery-impact-") as temporary:
        staging = Path(temporary)
        with deployment_lock(root):
            current = state(root)
            expected = f"v{active_policy.version}-{active_policy.commit}"
            if current["active"] != expected:
                raise Rejected("independent active trust policy does not match the active pointer")
            before = stage(root / "slots" / expected, staging / "active", active_policy)
            after = stage(candidate, staging / "candidate", candidate_policy)
        old_members = members(staging / "active", active_policy)
        new_members = members(staging / "candidate", candidate_policy)
        roles = []
        for role, old_name, new_name in (
            (
                "application",
                f"release-probe-{active_policy.version}.pyz",
                f"release-probe-{candidate_policy.version}.pyz",
            ),
            ("sbom", "sbom.cdx.json", "sbom.cdx.json"),
            ("validation", "validation.json", "validation.json"),
        ):
            old = next(asset for asset in before["assets"] if asset["name"] == old_name)
            new = next(asset for asset in after["assets"] if asset["name"] == new_name)
            roles.append(
                {
                    "role": role,
                    "before_sha256": old["sha256"],
                    "after_sha256": new["sha256"],
                    "size_delta_bytes": new["size"] - old["size"],
                    "changed": old["sha256"] != new["sha256"],
                }
            )
        return {
            "schema": 1,
            "kind": "authenticated_release_impact",
            "author": "Jason Stys",
            "active_identity": asdict(active_policy),
            "candidate_identity": asdict(candidate_policy),
            "observed_active_slot": current["active"],
            "active_manifest_sha256": hashlib.sha256(
                read_bytes(staging / "active/release.json")
            ).hexdigest(),
            "candidate_manifest_sha256": hashlib.sha256(
                read_bytes(staging / "candidate/release.json")
            ).hexdigest(),
            "assets": roles,
            "members": [
                {
                    "name": name,
                    "before_sha256": old_members.get(name),
                    "after_sha256": new_members.get(name),
                    "change": "added"
                    if name not in old_members
                    else "removed"
                    if name not in new_members
                    else "changed"
                    if old_members[name] != new_members[name]
                    else "unchanged",
                }
                for name in sorted(old_members.keys() | new_members.keys())
            ],
            "scope": "Both staged bundles authenticated under independently supplied exact policies. No execution, health check or deployment. Hash changes identify content differences, not compatibility or security. Pointer may change after review.",
        }


def export(result: dict[str, Any], output: Path) -> None:
    """Write a new private local impact bundle with escaped HTML and no remote dependencies."""
    absolute = output.absolute()
    if any(part.is_symlink() or part.is_junction() for part in (absolute, *absolute.parents)):
        raise Rejected("linked impact output refused")
    text = canonical(result).decode()
    rows = "".join(
        f"<tr><td>{html.escape(row['name'])}</td><td>{row['change']}</td></tr>"
        for row in result["members"]
    )
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; base-uri 'none'; form-action 'none'\">"
        "<title>Authenticated release impact — Jason Stys</title><main><h1>Verified candidate / active impact</h1>"
        "<p>Created by Jason Stys. Authenticated bytes; not compatibility approval or deployment.</p>"
        "<table><caption>Application member changes</caption><thead><tr><th>Member</th><th>Change</th></tr></thead><tbody>"
        + rows
        + "</tbody></table><details><summary>Exact identities, asset sizes and hashes</summary><pre>"
        + html.escape(text)
        + "</pre></details></main></html>"
    )
    absolute.mkdir(mode=0o700)
    (absolute / "impact.json").write_bytes(canonical(result))
    (absolute / "impact.html").write_text(page, encoding="utf-8")

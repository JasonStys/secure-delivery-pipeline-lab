"""Reproducible allowlisted zipapp, scoped SBOM, and evidence builder by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: application_bytes — line 65
# parameter: policy — line 65
# parameter: root — line 65
# variable: files — line 67
# variable: name — line 69
# variable: output — line 75
# variable: archive — line 76
# variable: data — line 77
# variable: name — line 77
# variable: entry — line 78
# definition: sbom — line 85
# parameter: policy — line 85
# variable: component — line 87
# definition: test_evidence — line 116
# parameter: benchmark — line 116
# parameter: coverage — line 116
# parameter: junit — line 116
# variable: xml — line 119
# variable: suites — line 120
# variable: counts — line 123
# variable: suite — line 124
# variable: name — line 125
# variable: name — line 128
# variable: percent — line 131
# variable: performance — line 132
# definition: build_release — line 148
# parameter: evidence — line 148
# parameter: output — line 148
# parameter: policy — line 148
# parameter: root — line 148
# variable: data — line 153
# variable: assets — line 158
# variable: content — line 159
# variable: name — line 159
# variable: manifest — line 164
# definition: main — line 178
# variable: parser — line 180
# variable: arguments — line 187
# variable: root — line 188
# variable: policy — line 189
# variable: metadata — line 190
# variable: current — line 191
# variable: dirty — line 194
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tomllib
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

from delivery.io import Rejected, atomic_write, canonical, load_json, read_bytes
from delivery.verify import REPOSITORY, TrustPolicy, preflight


def application_bytes(root: Path, policy: TrustPolicy) -> bytes:
    """Build identical ZIP_STORED bytes from an explicit six-file source allowlist."""
    files = {
        name: read_bytes(root / name)
        for name in ["delivery/__init__.py", "delivery/io.py", "delivery/probe.py", "LICENSE"]
    }
    files["__main__.py"] = b"from delivery.probe import main\nraise SystemExit(main())\n"
    files["BUILD.json"] = canonical(
        {"version": policy.version, "commit": policy.commit, "repository": policy.repository}
    )
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    return output.getvalue()


def sbom(policy: TrustPolicy) -> dict[str, Any]:
    """Describe the shipped application only; do not claim to inventory an external OS/Python."""
    component = {
        "type": "application",
        "name": "release-probe",
        "version": policy.version,
        "bom-ref": "release-probe",
        "purl": f"pkg:generic/JasonStys/release-probe@{policy.version}",
        "licenses": [{"license": {"id": "MIT"}}],
        "externalReferences": [
            {"type": "vcs", "url": f"https://github.com/{policy.repository}/tree/{policy.commit}"}
        ],
    }
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "component": component,
            "properties": [
                {
                    "name": "lab:scope",
                    "value": "Dependency-free zipapp only; Python >=3.12 and operating system supplied separately",
                }
            ],
        },
        "components": [],
        "dependencies": [{"ref": "release-probe", "dependsOn": []}],
    }


def test_evidence(junit: Path, coverage: Path, benchmark: Path) -> dict[str, Any]:
    """Accept actual all-passing JUnit, branch coverage >=85%, and passing performance gates."""
    try:
        xml = ET.fromstring(read_bytes(junit))
        suites = [xml] if xml.tag == "testsuite" else list(xml.findall("testsuite"))
        if not suites:
            raise Rejected("missing test suites")
        counts = {
            name: sum(int(suite.get(name, "0")) for suite in suites)
            for name in ("tests", "failures", "errors", "skipped")
        }
        if counts["tests"] < 1 or any(
            counts[name] != 0 for name in ("failures", "errors", "skipped")
        ):
            raise Rejected("release requires passing tests without skipped cases")
        percent = load_json(coverage)["totals"]["percent_covered"]
        performance = load_json(benchmark)
        if type(percent) not in (int, float) or not 85 <= percent <= 100:
            raise Rejected("release coverage gate failed")
        if performance["passed"] is not True or performance["schema"] != 1:
            raise Rejected("release performance gate failed")
        return {
            "schema": 1,
            "tests": counts,
            "coverage_percent": round(percent, 3),
            "benchmark": performance,
            "scope": "Current release job's Python tests and benchmark; external security jobs gated separately",
        }
    except (ET.ParseError, KeyError, TypeError, ValueError) as error:
        raise Rejected("test evidence is malformed or failed") from error


def build_release(root: Path, output: Path, policy: TrustPolicy, evidence: dict[str, Any]) -> None:
    """Create a new empty directory's assets; refuse accidental overwrites or extra contents."""
    if output.exists() and (output.is_symlink() or output.is_junction() or any(output.iterdir())):
        raise Rejected("build output must be a new or empty regular directory")
    output.mkdir(parents=True, exist_ok=True)
    data = {
        f"release-probe-{policy.version}.pyz": application_bytes(root, policy),
        "sbom.cdx.json": canonical(sbom(policy)),
        "validation.json": canonical(evidence),
    }
    assets = []
    for name, content in sorted(data.items()):
        atomic_write(output / name, content)
        assets.append(
            {"name": name, "size": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        )
    manifest = {
        "schema": 1,
        "version": policy.version,
        "source": {
            "repository": policy.repository,
            "commit": policy.commit,
            "ref": f"refs/tags/v{policy.version}",
        },
        "assets": assets,
    }
    atomic_write(output / "release.json", canonical(manifest))
    preflight(output, policy)


def main() -> int:
    """Build from the current clean tracked source commit and supplied real test evidence."""
    parser = argparse.ArgumentParser(description="Reproducible release builder by Jason Stys")
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--junit", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    arguments = parser.parse_args()
    root = Path.cwd()
    policy = TrustPolicy(REPOSITORY, arguments.commit, arguments.version)
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    current = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if dirty or current != policy.commit or metadata["project"]["version"] != policy.version:
        raise Rejected("release requires the exact clean versioned source commit")
    build_release(
        root,
        arguments.out,
        policy,
        test_evidence(arguments.junit, arguments.coverage, arguments.benchmark),
    )
    print(
        json.dumps(
            {
                "status": "built-not-yet-authenticated",
                "version": policy.version,
                "commit": policy.commit,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

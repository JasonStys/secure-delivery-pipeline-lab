"""Live cryptographic acceptance/rejection and real promotion tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: reject_case — line 50
# parameter: name — line 50
# parameter: operation — line 50
# definition: exercise — line 59
# parameter: directory — line 59
# parameter: policy — line 59
# variable: results — line 62
# variable: temporary — line 65
# variable: root — line 66
# variable: deployed — line 67
# variable: tampered — line 74
# variable: payload — line 76
# variable: manifest — line 81
# variable: asset — line 82
# variable: wrong — line 97
# variable: name — line 113
# variable: unexpected — line 113
# parameter: candidate — line 117
# variable: item — line 127
# definition: main — line 133
# variable: parser — line 135
# variable: arguments — line 140
# variable: report — line 141
# variable: content — line 146
# variable: summary — line 148
# variable: stream — line 149
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delivery.deploy import promote, state
from delivery.io import Rejected, atomic_write, canonical, load_json, read_bytes
from delivery.verify import REPOSITORY, TrustPolicy, verify_attestation, verify_release


def reject_case(name: str, operation: Callable[[], object]) -> dict[str, object]:
    """A negative scenario succeeds only when the real verifier raises a rejection."""
    try:
        operation()
    except Rejected:
        return {"case": name, "passed": True}
    raise RuntimeError(f"Security boundary failed: {name} was accepted")


def exercise(directory: Path, policy: TrustPolicy) -> dict[str, object]:
    """Use live GitHub attestations, never mocked crypto, in a disposable lab root."""
    verify_release(directory, policy)
    results: list[dict[str, object]] = [
        {"case": "authentic manifest and every asset", "passed": True}
    ]
    with tempfile.TemporaryDirectory(prefix="delivery-live-smoke-") as temporary:
        root = Path(temporary)
        deployed = promote(directory, root / "lab", policy)
        results.append(
            {
                "case": "verified staged promotion and actual probe health",
                "passed": deployed["active"] is not None,
            }
        )
        tampered = root / "tampered"
        shutil.copytree(directory, tampered)
        payload = tampered / f"release-probe-{policy.version}.pyz"
        payload.write_bytes(read_bytes(payload) + b"\nTAMPERED-FIXTURE\n")
        results.append(
            reject_case("changed payload digest", lambda: verify_release(tampered, policy))
        )
        manifest = load_json(tampered / "release.json")
        for asset in manifest["assets"]:
            if asset["name"] == payload.name:
                asset["sha256"] = hashlib.sha256(read_bytes(payload)).hexdigest()
                asset["size"] = payload.stat().st_size
        atomic_write(tampered / "release.json", canonical(manifest))
        results.append(
            reject_case(
                "payload and matching rewritten manifest", lambda: verify_release(tampered, policy)
            )
        )
        results.append(
            reject_case("tampered promotion", lambda: promote(tampered, root / "lab", policy))
        )
        if state(root / "lab") != deployed:
            raise RuntimeError("tampered candidate changed the active pointer")
        wrong = [
            (
                "wrong repository",
                TrustPolicy(
                    "JasonStys/industrial-edge-digital-twin", policy.commit, policy.version
                ),
            ),
            (
                "wrong signing workflow",
                TrustPolicy(
                    policy.repository, policy.commit, policy.version, ".github/workflows/ci.yml"
                ),
            ),
            ("wrong source commit", TrustPolicy(policy.repository, "0" * 40, policy.version)),
            ("wrong source tag", TrustPolicy(policy.repository, policy.commit, "999999.0.0")),
        ]
        for name, unexpected in wrong:
            results.append(
                reject_case(
                    name,
                    lambda candidate=unexpected: verify_attestation(
                        directory / "release.json", candidate
                    ),
                )
            )
    return {
        "schema": 1,
        "repository": policy.repository,
        "commit": policy.commit,
        "version": policy.version,
        "passed": all(item["passed"] for item in results),
        "cases": results,
        "scope": "Live online GitHub cryptographic verification and disposable authenticated promotion; no production deployment",
    }


def main() -> int:
    """Write actual public-safe verification results; a failed scenario aborts publication."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    report = exercise(
        arguments.directory, TrustPolicy(REPOSITORY, arguments.commit, arguments.version)
    )
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(arguments.out, canonical(report))
    content = json.dumps(report, indent=2)
    print(content)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(summary).open("a", encoding="utf-8") as stream:
            stream.write("## Live cryptographic release checks\n\n```json\n" + content + "\n```\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

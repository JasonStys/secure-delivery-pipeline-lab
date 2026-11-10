"""Live cryptographic acceptance/rejection and real promotion tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: reject_case — line 87
# parameter: name — line 87
# parameter: operation — line 87
# definition: require_case — line 96
# parameter: condition — line 96
# parameter: name — line 96
# definition: probe_cases — line 103
# parameter: policy — line 103
# parameter: slot — line 103
# parameter: temporary — line 103
# variable: environment — line 105
# variable: name — line 107
# variable: value — line 107
# variable: cases — line 110
# variable: content — line 111
# variable: expected_code — line 111
# variable: expected_output — line 111
# variable: label — line 111
# variable: fixture — line 135
# variable: result — line 137
# variable: passed — line 151
# variable: passed — line 153
# variable: passed — line 155
# definition: exercise — line 160
# parameter: baseline — line 161
# parameter: directory — line 161
# parameter: policy — line 161
# variable: results — line 165
# variable: temporary — line 168
# variable: root — line 171
# variable: lab — line 172
# variable: baseline_directory — line 174
# variable: baseline_policy — line 174
# variable: prior — line 176
# variable: original_pointer — line 183
# variable: impact — line 184
# variable: row — line 193
# variable: deployed — line 205
# variable: receipt — line 214
# variable: committed_pointer — line 225
# variable: retried — line 226
# variable: deployed — line 237
# variable: committed_pointer — line 249
# variable: tampered — line 262
# variable: payload — line 264
# variable: manifest — line 269
# variable: asset — line 270
# variable: wrong — line 283
# variable: name — line 299
# variable: unexpected — line 299
# parameter: candidate — line 303
# variable: item — line 313
# definition: main — line 322
# variable: parser — line 324
# variable: arguments — line 332
# variable: baseline_fields — line 333
# variable: baseline — line 342
# variable: report — line 350
# variable: content — line 355
# variable: summary — line 357
# variable: stream — line 358
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delivery.deploy import promote, rollback, state
from delivery.impact import export, review
from delivery.io import Rejected, atomic_write, canonical, load_json, read_bytes
from delivery.verify import REPOSITORY, TrustPolicy, verify_attestation, verify_release


def reject_case(name: str, operation: Callable[[], object]) -> dict[str, object]:
    """A negative scenario succeeds only when the real verifier raises a rejection."""
    try:
        operation()
    except Rejected:
        return {"case": name, "passed": True}
    raise RuntimeError(f"Security boundary failed: {name} was accepted")


def require_case(name: str, condition: bool) -> dict[str, object]:
    """Make observed native/receipt failures abort publication rather than merely print a label."""
    if not condition:
        raise RuntimeError(f"Release acceptance failed: {name}")
    return {"case": name, "passed": True}


def probe_cases(slot: Path, policy: TrustPolicy, temporary: Path) -> list[dict[str, object]]:
    """Run only the already-authenticated staged probe, without inheriting workflow credentials."""
    environment = {
        name: value
        for name, value in os.environ.items()
        if name in {"PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "LANG"}
    }
    cases = []
    for label, content, expected_code, expected_output in [
        (
            "native exact-cents two-SKU inventory",
            canonical(
                [
                    {"id": "DEMO_A", "units": 3, "unit_price_usd": "0.10"},
                    {"id": "DEMO_B", "units": 2, "unit_price_usd": "1.25"},
                ]
            ),
            0,
            {"products": 2, "units": 5, "inventory_value_usd": "2.80"},
        ),
        (
            "native malformed price rejection",
            canonical(
                [
                    {"id": "DEMO", "units": 1, "unit_price_usd": "NaN"},
                ]
            ),
            2,
            None,
        ),
        ("native over-limit file rejection", b" " * (1024 * 1024 + 1), 2, None),
    ]:
        fixture = temporary / f"probe-{len(cases)}.json"
        fixture.write_bytes(content)
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                str(slot / f"release-probe-{policy.version}.pyz"),
                "--input",
                str(fixture),
            ],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        passed = result.returncode == expected_code
        if expected_output is not None:
            passed = passed and json.loads(result.stdout) == expected_output
        else:
            passed = passed and result.stdout == "" and "Probe rejected the input" in result.stderr
        cases.append(require_case(label, passed))
    return cases


def exercise(
    directory: Path, policy: TrustPolicy, baseline: tuple[Path, TrustPolicy] | None = None
) -> dict[str, object]:
    """Use live GitHub attestations, never mocked crypto, in a disposable lab root."""
    verify_release(directory, policy)
    results: list[dict[str, object]] = [
        {"case": "authentic manifest and every asset", "passed": True}
    ]
    with tempfile.TemporaryDirectory(prefix="delivery-live-smoke-") as temporary:
        # Canonicalize only this newly created owned root; macOS aliases /var to /private/var.
        # The public export boundary continues to reject arbitrary caller-supplied linked paths.
        root = Path(temporary).resolve(strict=True)
        lab = root / "lab"
        if baseline:
            baseline_directory, baseline_policy = baseline
            verify_release(baseline_directory, baseline_policy)
            prior = promote(
                baseline_directory,
                lab,
                baseline_policy,
                operator="release-smoke",
                change_ref="baseline-authentication",
            )
            original_pointer = read_bytes(lab / "active.json")
            impact = review(directory, lab, policy, baseline_policy)
            export(impact, root / "impact")
            results.append(
                require_case(
                    "authenticated baseline/current nonexecuting impact",
                    impact["active_identity"]["commit"] == baseline_policy.commit
                    and impact["candidate_identity"]["commit"] == policy.commit
                    and impact["candidate_manifest_sha256"]
                    == hashlib.sha256(read_bytes(directory / "release.json")).hexdigest()
                    and all(row["changed"] for row in impact["assets"])
                    and read_bytes(lab / "active.json") == original_pointer
                    and load_json(root / "impact/impact.json") == impact,
                )
            )
            results.append(
                require_case(
                    "baseline promotion records asserted receipt",
                    prior["receipts"][-1]["identity"]["commit"] == baseline_policy.commit
                    and prior["receipts"][-1]["operator"] == "release-smoke",
                )
            )
        deployed = promote(
            directory, lab, policy, operator="release-smoke", change_ref="candidate-authentication"
        )
        results.append(
            {
                "case": "verified staged promotion and actual probe health",
                "passed": deployed["active"] is not None,
            }
        )
        receipt = deployed["receipts"][-1]
        results.append(
            require_case(
                "candidate identity and manifest bound to committed receipt",
                receipt["identity"]["commit"] == policy.commit
                and receipt["manifest_sha256"]
                == hashlib.sha256(read_bytes(directory / "release.json")).hexdigest()
                and receipt["health"] == "passed"
                and receipt["change_ref"] == "candidate-authentication",
            )
        )
        committed_pointer = read_bytes(lab / "active.json")
        retried = promote(
            directory, lab, policy, operator="release-smoke", change_ref="idempotent-retry"
        )
        results.append(
            require_case(
                "authenticated retry preserves pointer and receipt bytes",
                retried == deployed and read_bytes(lab / "active.json") == committed_pointer,
            )
        )
        results.extend(probe_cases(lab / "slots" / deployed["active"], policy, root))
        if baseline:
            deployed = rollback(
                lab, baseline[1], operator="release-smoke", change_ref="explicit-baseline-rollback"
            )
            results.append(
                require_case(
                    "actual separately authenticated baseline rollback",
                    deployed["active"] == prior["active"]
                    and deployed["receipts"][-1]["action"] == "rollback"
                    and deployed["receipts"][-1]["sequence"] == 3
                    and len(deployed["receipts"]) == 3,
                )
            )
            committed_pointer = read_bytes(lab / "active.json")
            results.append(
                reject_case(
                    "wrong independently selected active impact identity",
                    lambda: review(directory, lab, policy, policy),
                )
            )
            results.append(
                require_case(
                    "failed impact preserves pointer and receipt bytes",
                    read_bytes(lab / "active.json") == committed_pointer,
                )
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
        results.append(reject_case("tampered promotion", lambda: promote(tampered, lab, policy)))
        if state(lab) != deployed:
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
        "baseline": None
        if baseline is None
        else {"commit": baseline[1].commit, "version": baseline[1].version},
        "scope": "Live online GitHub cryptographic verification, actual staged authored inventory-probe execution, nonexecuting impact and local asserted receipts; no installer, production deployment or signed receipt claim",
    }


def main() -> int:
    """Write actual public-safe verification results; a failed scenario aborts publication."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--baseline-directory", type=Path)
    parser.add_argument("--baseline-commit")
    parser.add_argument("--baseline-version")
    arguments = parser.parse_args()
    baseline_fields = (
        arguments.baseline_directory,
        arguments.baseline_commit,
        arguments.baseline_version,
    )
    if any(baseline_fields) and not all(baseline_fields):
        parser.error(
            "baseline requires directory, independently selected commit and version together"
        )
    baseline = (
        None
        if not all(baseline_fields)
        else (
            arguments.baseline_directory,
            TrustPolicy(REPOSITORY, arguments.baseline_commit, arguments.baseline_version),
        )
    )
    report = exercise(
        arguments.directory, TrustPolicy(REPOSITORY, arguments.commit, arguments.version), baseline
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

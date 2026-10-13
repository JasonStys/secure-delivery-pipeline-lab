# Validation 1.0.1

Author: Jason Stys. Date: 2026-10-13. Status: local and hosted CI evidence collected; publication and live cryptographic verification pending.

## Observed local evidence

Windows, Python 3.14.6: 95 pytest cases passed, no skips; deterministic 100-example monetary property test included. Combined statement/branch coverage 91.58% (gate >=85%); statement coverage 92.25%, branch coverage 89.58%. Ruff lint/format and strict mypy for seven delivery modules passed. The actual SBOM passed the official CycloneDX JSON 1.6 schema validator and deterministic UUID/attester-identity regression. Real authored zipapp input/health and staged fixture rollback executed; external signature service was mocked only in offline unit/integration cases. All 18 authored Python code maps are current; the README indexes every tracked file.

10,000 inventory records, 30 actual iterations on the local Windows host for 1.0.1: p50 23.237 ms, p95 29.723 ms; 430,343 rows/sec at p50; 655,576 peak traced bytes. Gate: p95 <1000 ms and traced peak <8 MiB. These are host-specific observations, not universal throughput promises.

Full hash-locked development dependency audit: no known vulnerabilities found on the review date. No suppressions. Local Gitleaks inspected all three pre-release commits and found no leaks; hosted security checks also inspect the complete available repository history.

## Hosted CI

Prior candidate source: `aa1c45cd286efe5d35181ac5105ea594f575a9e4`. Corrected 1.0.1 source evidence will be recorded after its own CI and release run.

[Validate 38436012607](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38436012607) passed all six jobs:

| Job | Observed result |
|---|---|
| Ubuntu, Python 3.12 | 94 tests passed, 91.56% combined coverage; quality/performance gates passed. |
| Ubuntu, Python 3.14 | Quality, tests, coverage and performance gates passed. |
| Windows, Python 3.14 | Quality, tests, coverage and performance gates passed. |
| macOS, Python 3.14 | Quality, tests, coverage and performance gates passed. |
| Security | Hash-locked dependency audit, Gitleaks, Trivy filesystem/configuration, actionlint and ShellCheck passed. |
| Container | Real restricted image health/input runs and HIGH/CRITICAL vulnerability gate passed; image SBOM generated on the runner. |

The Ubuntu/Python 3.12 job measured p50 19.408 ms and p95 19.631 ms for the same 10,000-row/30-iteration benchmark. These are distinct from the local Windows measurements.

[CodeQL 38436012572](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38436012572) passed. The original scanner-permission alert is `fixed`, not dismissed; zero open alerts were independently observed before release dispatch. Security results describe the scanners' findings on the review date, not proof of no unknown vulnerabilities.

## Live release evidence still pending

Keyless attestations, live wrong-identity/tamper cases and independent published-download verification will be recorded here after they actually run. This report deliberately does not substitute offline mocks for successful signature verification.

## Storage

Before CI: account billing meter 0.5 GB /0.5 GB included (100%); retained artifact bytes across 60 repositories 570,245,535; separate cache bytes 6,821,397,559. Total billable usage after discounts shown as $0. This repository has no artifact/cache-upload steps. No existing artifacts/runs, retention settings or billing settings were deleted/changed.

## Repairs during implementation

First public CI source `615374d734499fbf5fd3ae7c959c0f3e1c515c45`: [Validate 38435377421](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38435377421) passed all four Python/OS lanes and the security-scanner job, but the actual Debian image gate rejected 88 HIGH and 3 CRITICAL known vulnerabilities. [CodeQL 38435377409](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38435377409) completed and correctly reported a world-readable scanner-file permission. Neither was ignored: scanner binaries became owner-only, the unused Debian package surface was replaced with a smaller patched Alpine runtime, pip was removed from the image, and the release gate now also requires zero open CodeQL findings. No vulnerable image/release was published. The original failure remains visible.

[Release 38436866253](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38436866253) passed all nine real cryptographic checks and attested the report, then rejected the application/SBOM binding because the pinned attester requires `serialNumber` even though the CycloneDX 1.6 schema makes it optional. No release was published. Add deterministic UUIDv5 serial identity and a schema/attester regression; retain failed `v1.0.0` unchanged and create corrected `v1.0.1` only after its own gates pass.

Initial cross-platform type checking treated the Unix lock branch as reachable on Windows; use explicit `sys.platform` guards so each real platform checks its own locking API. The line-map generator initially confused its own marker string literal with a header; anchor markers to whole comment lines and add an idempotence regression. The official SBOM validator's optional JSON validation extra was explicitly added and hash-locked. The dependency lock was regenerated with pip included and hash-pinned. No test/coverage budget was lowered.

One restricted local test invocation could not create the execution sandbox's temporary fixture directory (58 setup errors; tests never reached their assertions). Its JUnit/coverage were retained separately in ignored local artifacts. Running the same tests with ordinary temporary-directory access passed all 95 cases; no product check or test was disabled.

## Limitations

See the threat model and test plan. No production host, arbitrary malware sandbox, externally audited certification, guaranteed filesystem power-loss durability or prior signed public rollback predecessor. Docker Desktop was left unchanged; actual container validation is delegated to this repo's GitHub-hosted job.

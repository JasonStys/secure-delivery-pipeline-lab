# Validation 1.0.0

Author: Jason Stys. Date: 2026-10-13. Status: local evidence collected; GitHub CI, publication and live cryptographic verification pending.

## Observed local evidence

Windows, Python 3.14.6: 93 pytest cases passed, no skips; deterministic 100-example monetary property test included. Branch-inclusive delivery coverage 91.56% (gate >=85%). Ruff lint/format and strict mypy for seven delivery modules passed. The actual SBOM passed the official CycloneDX JSON 1.6 schema validator. Real authored zipapp input/health and staged fixture rollback executed; external signature service was mocked only in offline unit/integration cases.

10,000 inventory records, 30 actual iterations: p50 18.608 ms, p95 23.943 ms; 537,410 rows/sec at p50; 655,576 peak traced bytes. Gate: p95 <1000 ms and traced peak <8 MiB. These are host-specific observations, not universal throughput promises.

Full hash-locked development dependency audit: no known vulnerabilities found on the review date. No suppressions. Scanner findings and actual image checks remain pending until hosted CI completes.

## External evidence still pending

Source SHA, four hosted Python/OS quality lanes, history secret/configuration/workflow/image/static scans, CodeQL, release keyless attestations, live wrong-identity/tamper cases and independent published-download verification will be recorded here after they actually run. This report deliberately does not substitute offline mocks for successful signature verification.

## Storage

Before CI: account billing meter 0.5 GB /0.5 GB included (100%); retained artifact bytes across 60 repositories 570,245,535; separate cache bytes 6,821,397,559. Total billable usage after discounts shown as $0. This repository has no artifact/cache-upload steps. No existing artifacts/runs, retention settings or billing settings were deleted/changed.

## Repairs during implementation

First public CI source `615374d734499fbf5fd3ae7c959c0f3e1c515c45`: [Validate 38435377421](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38435377421) passed all four Python/OS lanes and the security-scanner job, but the actual Debian image gate rejected 88 HIGH and 3 CRITICAL known vulnerabilities. [CodeQL 38435377409](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38435377409) completed and correctly reported a world-readable scanner-file permission. Neither was ignored: scanner binaries became owner-only, the unused Debian package surface was replaced with a smaller patched Alpine runtime, pip was removed from the image, and the release gate now also requires zero open CodeQL findings. No vulnerable image/release was published. The original failure remains visible.

Initial cross-platform type checking treated the Unix lock branch as reachable on Windows; use explicit `sys.platform` guards so each real platform checks its own locking API. The line-map generator initially confused its own marker string literal with a header; anchor markers to whole comment lines and add an idempotence regression. The official SBOM validator's optional JSON validation extra was explicitly added and hash-locked. The dependency lock was regenerated with pip included and hash-pinned. No test/coverage budget was lowered.

## Limitations

See the threat model and test plan. No production host, arbitrary malware sandbox, externally audited certification, guaranteed filesystem power-loss durability or prior signed public rollback predecessor. Docker Desktop was left unchanged; actual container validation is delegated to this repo's GitHub-hosted job.

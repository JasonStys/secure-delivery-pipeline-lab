# Validation 1.0.1

Author: Jason Stys. Date: 2026-10-13. Status: passed local/hosted validation, published release, live cryptographic checks and independent Windows download/promotion verification.

## Observed local evidence

Windows, Python 3.14.6: 95 pytest cases passed, no skips; deterministic 100-example monetary property test included. Combined statement/branch coverage 91.58% (gate >=85%); statement coverage 92.25%, branch coverage 89.58%. Ruff lint/format and strict mypy for seven delivery modules passed. The actual SBOM passed the official CycloneDX JSON 1.6 schema validator and deterministic UUID/attester-identity regression. Real authored zipapp input/health and staged fixture rollback executed; external signature service was mocked only in offline unit/integration cases. All 18 authored Python code maps are current; the README indexes every tracked file.

10,000 inventory records, 30 actual iterations on the local Windows host for 1.0.1: p50 23.237 ms, p95 29.723 ms; 430,343 rows/sec at p50; 655,576 peak traced bytes. Gate: p95 <1000 ms and traced peak <8 MiB. These are host-specific observations, not universal throughput promises.

Full hash-locked development dependency audit: no known vulnerabilities found on the review date. No suppressions. Local Gitleaks inspected all four release-source commits and found no leaks; hosted security checks also inspect the complete available repository history. All 46 tracked files have README guide entries.

## Hosted CI

Published `v1.0.1` source: `6e6dc95ce47d4f7dfdf019ccd84db8bdd83f8828`. This identity was obtained from the remote tag independently of the downloaded manifest. Later documentation-only commits do not alter the release identity or assets; they rerun the same main-branch checks.

[Validate 38437799609](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38437799609) passed all six jobs. Counts/coverage below were read from each actual job's log, not extrapolated from the local test count:

| Job | Observed result |
|---|---|
| Ubuntu, Python 3.12 | 95 tests passed in 4.71 seconds, 91.58% combined coverage; quality/performance gates passed. |
| Ubuntu, Python 3.14 | 95 tests passed in 2.01 seconds, 91.58% combined coverage; quality/performance gates passed. |
| Windows, Python 3.14 | 95 tests passed in 4.68 seconds, 91.58% combined coverage; quality/performance gates passed. |
| macOS, Python 3.14 | 95 tests passed in 3.20 seconds, 91.58% combined coverage; quality/performance gates passed. |
| Security | Hash-locked dependency audit, Gitleaks, Trivy filesystem/configuration, actionlint and ShellCheck passed. |
| Container | Real restricted image health/input runs and HIGH/CRITICAL vulnerability gate passed; image SBOM generated on the runner. |

[CodeQL 38437799457](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38437799457) passed. The original scanner-permission alert is `fixed`, not dismissed; zero open alerts were independently observed and required by the release gate. Security results describe the scanners' findings on the review date, not proof of no unknown vulnerabilities.

## Published release and live cryptographic evidence

[Verified release 38438010345](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38438010345) passed both jobs and every publication step. [Public release v1.0.1](https://github.com/JasonStys/secure-delivery-pipeline-lab/releases/tag/v1.0.1) was published at `2026-10-13T17:23:10Z` after the gates passed, not manually released around a failure.

The release's actual `validation.json` records 95 passing tests, zero errors/failures/skips, 91.579% combined coverage, Python 3.14.8 on Linux, and a 10,000-row/30-iteration benchmark: p50 14.471 ms, p95 15.327 ms, 691,032 rows/sec at p50 and 655,576 peak traced bytes. Timing evidence intentionally differs between hosts/runs; only the authored application/SBOM build bytes are deterministic for a given identity.

Actual online verification passed **nine scenarios**, on the GitHub-hosted Linux release job and independently on this Windows PC against freshly downloaded public assets:

1. Authentic manifest and every asset accepted under exact repository/workflow/source/tag policy.
2. Authenticated staged promotion and real probe health passed.
3. Changed payload rejected by digest validation.
4. Changed payload plus recomputed matching manifest rejected by cryptographic verification.
5. Tampered promotion rejected; old active pointer unchanged.
6. Wrong repository rejected.
7. Wrong signing workflow rejected.
8. Wrong source commit rejected.
9. Wrong source tag rejected.

No signature service was mocked in these runs. `gh attestation verify` also independently accepted the application's CycloneDX SBOM-binding predicate and the separate `live-verification.json` report's provenance under the same exact identity constraints.

### Independent public download

Public asset sizes and SHA256 digests matched the freshly downloaded bytes:

| Asset | Bytes | SHA256 |
|---|---:|---|
| `release-probe-1.0.1.pyz` | 9,660 | `396a690741e043986a3f72b94078dcb7283889435bf255e0ecdd0df9b918e227` |
| `release.json` | 533 | `c2380d31bdf92412fa9030f2982d05f41c8e0426b7dee9b3b03d95038ef38683` |
| `sbom.cdx.json` | 677 | `80c2e3f9f89c6a0aa2b5748847523f33b3bca1d2d32b4aaffffc5119b01536ab` |
| `validation.json` | 443 | `426955c270d5620747c8b84a7713843f98a867228c758dbe0c47b7a8a664b146` |
| Separate `live-verification.json` report | 751 | `15d7f0cbd666b1667eb669186773d6ee38bafa1040065278cee8f0d509416f05` |

Two independent local Windows builds had identical application bytes and matched the published Linux build digest above; the local SBOM also matched the published SBOM. Release evidence/manifest may legitimately differ when benchmark evidence changes. Digests are explanatory integrity evidence, not substitutes for cryptographic authentication.

The documented `delivery verify` CLI returned `authenticated`. A real `delivery promote` into this repo's ignored disposable `lab-state/release-1.0.1` selected `v1.0.1-6e6dc95ce47d4f7dfdf019ccd84db8bdd83f8828`. Running the authenticated active zipapp with the synthetic inventory returned exactly 3 products, 46 units and USD 1727.40. No service or other application was installed/modified. The local Windows live-test report and downloaded bundle remain in ignored local evidence directories, not in source history.

## Storage

Before CI: account billing meter 0.5 GB /0.5 GB included (100%); retained artifact bytes across 60 repositories 570,245,535; separate cache bytes 6,821,397,559. Total billable usage after discounts shown as $0. This repository has no artifact/cache-upload steps. No existing artifacts/runs, retention settings or billing settings were deleted/changed.

Fresh account-wide read at `2026-10-13T17:21:18.953427Z`: 61 repositories after creation; retained artifact bytes still 570,245,535 and separate cache bytes still 6,821,397,559. Billing UI refreshed during this release showed the same 100% included-storage meter and $0 total billable usage after discounts. This new repo's artifact API returned zero retained artifacts/bytes; its cache API returned zero saved caches/bytes. Public Release assets and attestations are not counted here as Actions artifacts. Cleanup would require fresh approval; none occurred.

## Repairs during implementation

First public CI source `615374d734499fbf5fd3ae7c959c0f3e1c515c45`: [Validate 38435377421](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38435377421) passed all four Python/OS lanes and the security-scanner job, but the actual Debian image gate rejected 88 HIGH and 3 CRITICAL known vulnerabilities. [CodeQL 38435377409](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38435377409) completed and correctly reported a world-readable scanner-file permission. Neither was ignored: scanner binaries became owner-only, the unused Debian package surface was replaced with a smaller patched Alpine runtime, pip was removed from the image, and the release gate now also requires zero open CodeQL findings. No vulnerable image/release was published. The original failure remains visible.

After those repairs, prior candidate `aa1c45cd286efe5d35181ac5105ea594f575a9e4` passed [Validate 38436012607](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38436012607) and [CodeQL 38436012572](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38436012572), with 94 tests and 91.56% combined coverage. The following failure identified a separate consumer compatibility contract, not a bypass of those checks.

[Release 38436866253](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/38436866253) passed all nine real cryptographic checks and attested the report, then rejected the application/SBOM binding because the pinned attester requires `serialNumber` even though the CycloneDX 1.6 schema makes it optional. No release was published. Deterministic UUIDv5 serial identity and a schema/attester regression were added; failed `v1.0.0` remains unchanged and corrected `v1.0.1` was published only after its own gates passed.

Initial cross-platform type checking treated the Unix lock branch as reachable on Windows; use explicit `sys.platform` guards so each real platform checks its own locking API. The line-map generator initially confused its own marker string literal with a header; anchor markers to whole comment lines and add an idempotence regression. The official SBOM validator's optional JSON validation extra was explicitly added and hash-locked. The dependency lock was regenerated with pip included and hash-pinned. No test/coverage budget was lowered.

One restricted local test invocation could not create the execution sandbox's temporary fixture directory (58 setup errors; tests never reached their assertions). Its JUnit/coverage were retained separately in ignored local artifacts. Running the same tests with ordinary temporary-directory access passed all 95 cases; no product check or test was disabled.

## Limitations

See the threat model and test plan. No production host, arbitrary malware sandbox, externally audited certification, guaranteed filesystem power-loss durability or prior signed public rollback predecessor. Docker Desktop was left unchanged; actual container validation is delegated to this repo's GitHub-hosted job.

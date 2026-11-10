# Release refresh validation — 2026-11-09

Created by Jason Stys. Scope: source version 1.1.0, portable signed inventory example and the trusted source-side delivery manager. This is not a desktop installer or production deployment.

## Why refresh

The retained public 1.0.1 tag resolves to `6e6dc95ce47d4f7dfdf019ccd84db8bdd83f8828`. It predates the accepted source's authenticated candidate/active review and atomic bounded receipts. Those management features remain source code; the six-member zipapp intentionally remains a small inventory probe. No prior tag or asset is replaced.

## Local executed checks

- Windows / Python 3.14.6, repository-specific environment installed from the unchanged complete hash lock; `pip check` and the full development-graph advisory audit passed with no known vulnerabilities and no ignores.
- **140 pytest cases passed with no skips**, including existing tamper, pointer atomicity, 25-transition/newest20 receipt retention and rollback tests. Combined delivery-module statement/branch coverage is **93.05%**, retaining the 85% minimum; receipts remain 100% covered. This denominator excludes release scripts and external cryptographic infrastructure.
- New gate controls reject returned foreign source/branch/event/workflow/URL, malformed/duplicate/out-of-range IDs and newer failed/unfinished runs; an older success never clears a newer failure. Version metadata and authored release notes must agree.
- Local lifecycle tests use an independent captured-fixture-hash oracle **only for external attestation**. They execute real staged zipapps, compare/report exact active/candidate content, preserve pointer bytes during review, check asserted receipts and idempotent retry, run exact `2.80 USD / 5 units / 2 products`, malformed-price and oversized-file controls, and explicitly roll back. Both optional-baseline paths are exercised (14/19 observed cases). These are unsigned unit fixtures, not genuine GitHub signatures.
- Every staged probe invocation uses isolated Python and a bounded credential-free environment. Dummy workflow credentials are asserted absent from each actual child process. A false native acceptance control raises instead of printing a passing label.
- Ruff lint/format, strict delivery-module mypy and generated source maps passed. Thirty real 10,000-row probe benchmark iterations measured p50 **15.881 ms**, p95 **17.173 ms**, traced peak **655,576 bytes**, within unchanged 1,000ms/8MiB limits. These are host observations, not signature latency or deployment capacity guarantees.

## Separate publication acceptance

The first hosted PR run found a genuine harness portability error on macOS: 139 tests passed, but the new smoke's owned `/var/folders/...` temporary spelling crossed a system alias and was correctly rejected by the existing strict impact-export guard. [Failed job evidence](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/runs/42744499938/job/129593255718) is retained. The repair canonicalizes only the newly created private smoke root before deriving output paths; it does not relax caller-path symlink/junction refusal. An independent noncanonical temporary-path oracle now exercises this on every OS, including Windows, and the full 140 local cases pass. The corrected macOS hosted gate remains required; this was a source harness defect, not an Actions-storage fault.

The tag-only workflow requires exact current-main Validate and CodeQL success plus no open code-scanning findings. It rebuilds the clean exact version/source and attests the allowlisted output. Its expanded **unmocked** live smoke requires all 19 cases: authenticate the independently pinned retained baseline and candidate; review without deployment; inspect committed manifest/identity receipts; preserve state on retry; execute bounded inventory/invalid-input controls; explicitly authenticate rollback; and retain all original tamper/wrong identity rejection gates.

This source report does not claim that a future tag, hosted container job, live cryptographic run or new public download already passed. Their completed run records and independently verified public assets establish those separate results. No local Docker repair, persistent service installation, real cloud/device mutation or credential publication occurred. Receipt operator/change strings are local assertions, not signed audit records or authenticated human identity. Checksums/preflight still provide integrity only; there is no authentication bypass.

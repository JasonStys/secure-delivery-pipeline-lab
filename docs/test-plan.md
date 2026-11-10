# Risk-based test strategy

Author: Jason Stys. Date: 2026-10-13.

## Test layers

| Layer | Cases and boundary | Acceptance |
|---|---|---|
| Unit/schema | Exact inventory fields, cents, limits, duplicate keys/IDs, booleans, JSON encodings, missing files | All valid fixtures accepted; all invalid fixtures rejected. |
| Property-based | 100 deterministic unit/price combinations plus exact integer-cent oracle | No arithmetic mismatch; examples are not counted as separate pytest test cases. |
| Packaging | Same-source bytes, allowlisted members, malformed/duplicate/link/oversized ZIPs | Byte identical for identical inputs; invalid archives rejected without extraction. |
| Trust-policy unit | Exact GH argv, missing CLI, timeout/nonzero, independent identity | Fail closed; no shell use/checksum-only fallback. Mocked signature service is explicitly unit scope. |
| Deployment integration | Real authored zipapp, private staging, OS locks, pointer update, health/outage failure, fixture rollback | Correct output and old-state preservation. Signature service alone mocked in offline integration cases. |
| Workflow contracts | SHA pins, least privilege, no privileged fork trigger, exact-SHA/tag green gates, no uploads | No bypass trigger or publication credential in PR/test workflows. |
| Platform CI | Ubuntu Python 3.12/3.14, Windows 3.14, macOS 3.14 | All cases pass; branch-inclusive delivery coverage >=85%. |
| Measured performance | 30 actual 10,000-record runs, traced memory | p95 <1000 ms, traced peak <8 MiB; actual host/version recorded. These are broad regression budgets, not guaranteed user latency. |
| Security tooling | Dependency audit, Gitleaks history scan, Trivy configuration/filesystem/image, CodeQL extended, actionlint/ShellCheck | No unsuppressed known HIGH/CRITICAL gate finding; all analysis jobs complete successfully. Unknown risks remain. |
| Real container | Actual digest-pinned image, read-only/no-network/non-root/dropped capabilities/resource limits | Health and synthetic inventory output correct; no local Docker modification. |
| Live signed release | Actual GH trust verification of independently pinned baseline/current assets, nonexecuting impact, actual staged inventory/invalid/oversized controls, receipts/retry/explicit rollback and original tamper/wrong identity cases | All 19 cases pass with the baseline; every negative scenario rejects before publication. |

Generated evidence is actual JUnit XML, coverage JSON, benchmark JSON and live signature-check JSON. CI summaries never fabricate a success when inputs are missing/failed. Published release validation describes its own source/job; platform/security jobs are separately gated and linked.

## Not claimed/test gaps

No production cloud availability/load/SLA, malicious native-code containment, multi-user account isolation, comprehensive filesystem power-loss testing, external penetration test or certification. Windows final-link refusal is tested without privileged symlink creation; Linux also uses a genuine filesystem symlink. OS-specific lock branches are exercised by their respective real CI operating systems. First-version rollback originally used unsigned fixture identities plus mocked external verification; release 1.1.0 additionally requires actual authentication of the retained 1.0.1 baseline. Local unit lifecycle tests still fake only the external signature service and do not establish live provenance.

Returned workflow-run metadata is validated independently of REST query filters: full source SHA, main branch, push event, exact workflow path and same-repository run URL/positive 64-bit ID. Missing/duplicate/foreign metadata and newer failed or unfinished runs block publication. Token-shaped fixture strings prove no workflow credential is inherited by staged probe processes. A false native acceptance control must raise rather than produce a green report.

All test input is fictional; no real account password, signing key, customer log, classified information or third-party target is needed.

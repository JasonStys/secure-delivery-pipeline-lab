# Secure Delivery Pipeline Lab handbook

By Jason Stys.

Build, authenticate and review a small inventory probe before promoting its exact bytes into a lab deployment slot. The trusted source verifier checks the expected signer, source and payload; staged health checks and explicit rollback make delivery failures reviewable without deploying to a real service.

Review authenticated candidate/active changes and retain atomic deployment receipts. The 1.1.0 signed inventory-probe example adds exact-source release gates and a real 19-case verification, promotion, invalid-input and separately trusted rollback journey.

Connects cryptographic provenance to an exercised change-and-recovery workflow while keeping the small downloadable example distinct from its trusted source-side manager.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |
| [validation-review.docx](reports/validation-review.docx) | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits. |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions, and the workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [operations review](operations-review.md)
- [release checklist](release-checklist.md)
- [releases/v1.0.0](releases/v1.0.0.md)
- [releases/v1.0.1](releases/v1.0.1.md)
- [releases/v1.1.0](releases/v1.1.0.md)
- [runbook](runbook.md)

### Design and contracts

- [architecture](architecture.md)
- [contracts](contracts.md)
- [research](research.md)

### Security and validation

- [security](security.md)
- [test plan](test-plan.md)

## Historical results and reproduction

The reviewed source is [`e37b189fa604bb0d6951e4a926d20ed9606298a1`](https://github.com/JasonStys/secure-delivery-pipeline-lab/tree/e37b189fa604bb0d6951e4a926d20ed9606298a1). The observed functional workflow baseline is `e37b189fa604bb0d6951e4a926d20ed9606298a1`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/release-refresh-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- The dependency-free inventory probe is a bounded Python zip application; the reviewed verification and promotion manager is separate source, not a desktop installer or production deployment service.
- Impact hashes establish changed bytes, not compatibility or a complete security review. Local receipt aliases are operator assertions, not authenticated human identity or signed audit records.
- Verification requires the official GitHub CLI, independently selected source/version and actual attestation checks; checksum or preflight success alone is insufficient.
- The synthetic release exercise does not establish production readiness, operational availability or operating-system code signing.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.

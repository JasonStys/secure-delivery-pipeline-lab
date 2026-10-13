# Scoped release checklist

Author: Jason Stys. Date: 2026-10-13. Target: public educational release and disposable lab promotion; no production environment or on-call team exists.

## Before release

- Review changed source against `docs/security.md`; resolve correctness/security issues and stale code maps.
- Confirm local lint, format, types, all tests, coverage and performance gates.
- Confirm current Actions artifact bytes and available billing quota; warn about full storage. No cleanup, retention or billing mutation without fresh approval.
- Require exact source commit's Validate and CodeQL runs to succeed, including real three-OS/container/security checks.
- Confirm runtime metadata/tag/release-note versions agree and only synthetic public-safe files are packaged.
- Confirm documented rollback behavior and failure evidence; first public version has no older signed public predecessor.

## Release

- Create a new lightweight tag at the exact green main commit and manually dispatch the tag's reviewed workflow.
- Rebuild/retest; inspect scoped SBOM/evidence; create keyless attestations.
- Require live valid-provenance acceptance and every wrong-identity/tamper case to reject.
- Publish only after those gates; never manually bypass a failed gate or rewrite a published tag.

## After release

- Download the public bundle independently and verify all four assets against independently selected tag/SHA/workflow.
- Exercise real local staged promotion and synthetic inventory behavior; preserve signed release identity separately from later documentation commits.
- Update validation/case study with actual results, run links, measured performance and limitations.
- Observe latest main CI and report Actions storage again. No artifact/cache upload is part of this repo.

## Rollback/rejection triggers

Wrong identity, digest/structure mismatch, verifier unavailable/timeout, health result mismatch, lock conflict or malformed state means no candidate activation. Keep the old pointer. Explicit rollback is only to a reauthenticated previous identity. There is no forced downgrade or automatic data deletion.

Not applicable: production traffic monitoring, database migration, hosted feature flags, public user-account operation, installer notarization or cloud spend. Do not mark these as tested merely because the checklist names them.

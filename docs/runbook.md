# Operator and user runbook

Created by Jason Stys. Operate only this repo's authored synthetic application in disposable local roots; never copy production credentials or datasets into this lab.

## Source and release use

Follow README setup and obtain the tag's source SHA independently on GitHub. Clone/review the verifier source, install official GitHub CLI, and download only the four allowed bundle files into a fresh directory. Use `verify` before any payload execution. Missing credentials/network or wrong identity is a rejection, not a request to bypass verification.

If successful, run `promote` with a new disposable `--root`. `active.json` identifies the current immutable slot. The promotion self-test is the actual zipapp process, not a mocked health response. To inspect the application on your own reviewed release, execute the authenticated slot's `.pyz` with `--input examples/inventory.json`; do not execute a candidate which failed verification.

## Rollback

After at least two successful distinct source/version promotions, independently obtain the previous release's version and full source SHA:

```text
python -m delivery rollback --root lab-state --version PREVIOUS_VERSION --commit INDEPENDENT_PREVIOUS_SOURCE_SHA
```

The requested target must match `previous`, then its staged bytes are freshly authenticated and health-checked. A rollback intentionally moves back to that explicitly selected identity; the former active slot becomes previous. If verification is offline, corrupted or the target changed concurrently, keep the current release and investigate. No forced or unauthenticated rollback is provided.

The first public release has no older public version to downgrade to. Unit integration tests exercise two distinct authored fixture identities and real payload execution with only the external signature service mocked; live release tests authenticate real published identity separately. Do not mislabel those fixtures as actual signed previous releases.

## Maintainer release

1. Review source/threat model and run the local gates. Update metadata/source version and release notes together.
2. Push main, observe exact-SHA Validate and CodeQL success. Check Actions storage; ask separately before any cleanup. This repo performs no artifact/cache uploads.
3. Create a **new lightweight version tag** on the exact successful current-main commit; push only that tag. Never rewrite a published tag.
4. Dispatch `release.yml` using that tag as workflow ref. Its read-only gate refuses main-branch dispatch, mismatched tag/main/context SHA, missing checks, pending checks or failed checks.
5. The privileged hosted job rebuilds, remeasures, attests, and performs live negative verification. Only then does it create a draft and publish the release. Failed jobs may leave a draft; inspect it, preserve evidence, and do not publish a failed build manually.
6. Independently download and verify the published assets, inspect run summaries, and update the dated validation/case study. A documentation-only commit has its own CI identity; do not imply it changes a previous signed release's source.

No approval-gated GitHub Environment is automatically configured. Repository maintainers control dispatch; configuring stronger branch/environment approval controls is a separate deliberate account administration action.

## Failure recovery

| Symptom | Safe response |
|---|---|
| CLI unavailable/offline | Install/restore official CLI connectivity through normal user-managed setup; leave active release unchanged. |
| Manifest/hash/signature mismatch | Preserve failed evidence privately; redownload from the expected release and verify the independent SHA. Never recompute hashes as a substitute for signatures. |
| Health failure | Pointer is not advanced. Inspect authored probe logs and the candidate's source; do not disable the health gate. |
| Lock contention | Another local operation owns the root. Wait for it to finish or investigate its process; do not delete lock files to bypass OS locking. |
| Process crash before pointer swap | Existing pointer remains the intended selection. An unreferenced slot may remain; verify state and independently authenticate before reuse. No automatic deletion. |
| Corrupt state or marker | Stop. Preserve the directory and create a separate new disposable root; do not guess a production path or recursively clear data. |
| Security scanner finding | Reproduce and remediate the source/dependency/base image; do not add blanket ignores or rerun until a finding disappears. |

## Help/contact

README contains commands and file responsibilities; `docs/contracts.md` describes validation messages and scope. Jason Stys's GitHub/LinkedIn links are in README. Open non-sensitive issues with synthetic reproductions only. Public repos/run logs are not private support channels.

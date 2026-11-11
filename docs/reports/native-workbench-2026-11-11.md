# Native offline workbench validation — 2026-11-11

Author: Jason Stys. This report describes source/candidate validation, not a completed release, installation, desktop shortcut or hosted-main claim.

## Implemented user workflow

Review real inventory JSON with the original exact-cent summarizer, or inspect an authorized four-asset release with the original bounded preflight. The GUI deliberately never executes incoming applications or substitutes matching hashes for authenticated provenance.

The compiled consumer checks warehouse USD1727.40, exact USD0.30, zero and high-value totals, both unsigned integrity results with authentication/signature/execution explicitly false, an actual selected inventory and an actual selected four-asset directory. It also tests exact export, rejected invalid input without history loss, cancel/confirm deletion and an unchanged two-launch bundle history.

## Measured local scope

- Initial authored-source suite at `ca9815f91e875795032e04ae3dea8cfc611fc3d8` before the separately documented runner-policy tests: 217 passed, 3 explicit platform/capability skips; combined statement/branch coverage 94.16%, above the original 85% floor. No original coverage exclusions or floor reduction was added. The skips are one POSIX-only FIFO case and two symbolic-link fixtures the current Windows token cannot create. Actual NTFS hardlink cases pass locally; real FIFO/symbolic-link cases remain a hosted Linux obligation.
- Strict Ruff, format and mypy checks retain the original modules. Meaningful unit cases exercise exact domain results, invalid input, bounded source reads, NTFS hardlinks, fixed mutable-file/sidecar admission, persistent history and actual GUI handler behavior. Source tests are distinct from compiled acceptance.
- A dirty-source development candidate already passed 8 original-engine workflows and two normal native launches with unchanged bundle history. The coherent clean-source build and exact hosted PR/main checks must be observed separately; the dirty prototype is not release evidence.
- The new Windows Actions job builds the actual one-file application using pinned CPython 3.14.10 and the complete hash-locked graph, audits packaging dependencies, and runs the unchanged full compiled consumer. It uploads no application packages, profiles, screenshots, private receipts or caches to Actions storage. Original security, cross-platform, real-container/cluster and release gates remain in place.

## Security and interpretation

Offline integrity review is not provenance authentication, malware analysis, signing or deployment. The prepared ZIP is inert, unsigned synthetic data with a fictional source identity; it is never run. Published 1.1.0 signed-example assets remain historical immutable downloads; the new portable GUI is a separate 1.2.0 candidate until independently released. Existing authenticated deployment APIs and their tests are retained.

Profiles and chosen paths are sensitive plaintext for a trusted OS owner. Static alias/hardlink checks are not same-user adversary isolation. No live host, cloud, cluster or operational deployment was accessed by this native test. Docker Desktop and normal account profiles were unchanged. PyInstaller resource hashes and source metadata are integrity/diagnostic bindings, not Authenticode signing, malware certification or a legal/compliance opinion.

See [native usage and profile lifecycle](../native-application.md). Historical reports remain dated at their original source identities.

[Subsequent setup-only runner correction and expanded local suite](runner-network-2026-11-11.md). No runtime/oracle/floor reduction was made.

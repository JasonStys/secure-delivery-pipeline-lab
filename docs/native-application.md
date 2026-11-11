# Secure Delivery Offline Workbench: native application

Created by Jason Stys · [Source and contact](https://github.com/JasonStys) · [Professional profile](https://www.linkedin.com/in/jason-stys-31b30b351/).

Review real inventory JSON with the original exact-cent summarizer, or inspect an authorized four-asset release with the original bounded preflight. The GUI deliberately never executes incoming applications or substitutes matching hashes for authenticated provenance.

## Launch and use

The reviewed Windows portable candidate is `SecureDeliveryPipelineLab.exe`. It bundles CPython 3.14.10, Tcl/Tk 9.0.4, the complete authored GUI and original dependency notices; it requires no separately installed Python, Node, terminal setup, default password or background service. It is a portable application, not an NSIS installer or a signed vendor application. Release/download availability must be verified separately; a source build is not a published download.

1. Choose **Review authorized inventory JSON**, select your authorized inventory file, and run analysis. Stock IDs must be unique; units are bounded integers and USD prices are exact two-decimal strings. Inspect each contribution, the original product/unit counts and exact total.
2. For release review, choose **Preflight an authorized four-asset release** and select its exact directory. Enter independently expected repository, full source SHA, stable version and signer workflow. The original preflight checks manifest identity, hashes, sizes and six ZIP members.
3. Read the persistent **provenance is NOT authenticated** banner and the integrity-only result. Workflow identity is merely an expectation here; it has not been cryptographically checked. Even rewritten matching manifests can pass integrity checks. Use the original authenticated `verify`, `impact`, `promote` and `rollback` CLI for their separately trusted purposes.
4. Prepared scenarios populate the same editable controls: realistic warehouse stock, three ten-cent units, zero stock, bounded high-value stock and two explicitly unsigned release-data cases. No real signature, CI result or attestation is fabricated.
5. Select a result for complete evidence; search/filter the view without changing original denominators. Export exact JSON to a new file. Saved reviews reopen durably; deleting a review requires confirmation. Exit retains ownership until the worker has finished.

## Local data and ownership

The default durable profile is outside the executable and repository: the OS-local application-data directory, then `SecureDeliveryPipelineLab`. An explicitly selected `--profile` remains available; the original CLI paths and data contracts are unchanged. The profile stores sensitive reports, selected paths and saved evidence in owner-local plaintext. There is no multiuser login or encryption claim. Keep it in an OS-protected directory and use only files you are authorized to review.

Before creating/opening SQLite, the app checks lexical ancestors and all fixed database, marker, lock and journal/WAL/SHM files for aliases, nonregular files and multiple links. Ordinary owned recovery sidecars are preserved. An exclusive owner lock prevents a second normal app from adopting the same profile. These static checks do not defend against a malicious process already running as the same OS user. No profile is reset, migrated to a different schema, or automatically deleted on failure.

Inputs use bounded stable descriptor reads, duplicate-safe JSON/closed original parsers and finite evidence/history limits. Export creates a new regular file and refuses overwrite. The native Help and licenses controls work without network access. No telemetry, advertisements, provider keys, HTTP server, plugins, shell eval or arbitrary executable path is introduced. A busy Quit keeps the owner window and lock until the exact worker finishes; no normal-success forced kill is used.

## Build and validate

From a dedicated environment using the reviewed Windows CPython 3.14.10 runtime:

```text
python -m pip install --require-hashes -r requirements-dev.lock -r requirements-native.lock
python -m pip check
python scripts/build_native.py
python scripts/test_native_app.py
```

The build binds the full source SHA, honest dirty flag, actual Python DLL, complete original notices and allowlisted public resources. The consumer runs the actual frozen executable with a minimal system-only environment, drives the same Tk widgets/handlers/mainloop with an explicitly synthetic profile, captures two real screens, exports, normally exits and restarts. CI refuses dirty-source proof and verifies both known frozen PIDs/bootloaders have exited. No external service is adopted and no native artifact/cache upload is added.

The compiled consumer checks warehouse USD1727.40, exact USD0.30, zero and high-value totals, both unsigned integrity results with authentication/signature/execution explicitly false, an actual selected inventory and an actual selected four-asset directory. It also tests exact export, rejected invalid input without history loss, cancel/confirm deletion and an unchanged two-launch bundle history.

## Scope and evidence

Offline integrity review is not provenance authentication, malware analysis, signing or deployment. The prepared ZIP is inert, unsigned synthetic data with a fictional source identity; it is never run. Published 1.1.0 signed-example assets remain historical immutable downloads; the new portable GUI is a separate 1.2.0 candidate until independently released. Existing authenticated deployment APIs and their tests are retained.

[Dated local validation and limits](reports/native-workbench-2026-11-11.md). Existing Office guides and older reports retain their recorded source baselines and measurements; they are not rewritten as evidence of this candidate.

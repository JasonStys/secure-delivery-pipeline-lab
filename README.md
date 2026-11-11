# Secure Delivery Pipeline Lab

Created by **Jason Stys** — [GitHub](https://github.com/JasonStys) · [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/).

[![Validate](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/codeql.yml)

A working DevSecOps reference that builds a small application, gates its release on tests and security checks, creates keyless GitHub provenance, and rejects altered or incorrectly signed downloads before lab deployment.

[Release 1.1.0 assets and checks](https://github.com/JasonStys/secure-delivery-pipeline-lab/releases/tag/v1.1.0) · [Current source validation](docs/reports/release-refresh-2026-11-09.md). The refreshed workflow authenticates the retained 1.0.1 baseline, reviews the new candidate, exercises real staged inventory/invalid-input behavior, verifies asserted receipts and retry, and explicitly rolls back. Publication requires every live cryptographic case to pass. [Earlier 1.0.1 measured evidence](docs/reports/validation-1.0.1.md) describes that older source, not these changes.

The shipped signed-example application remains a dependency-free inventory CLI using exact cents. The new offline workbench exposes its actual inventory and bounded preflight engines with practical review controls. The portfolio evidence is the **delivery system**, its trust boundaries, and its measured adversarial tests—not a collection of scanner screenshots.

The downloadable zipapp contains only the six-member inventory probe. Verification, impact review and deployment management run from this repository's trusted reviewed source. That signed-example zipapp is distinct from the new offline portable GUI; neither installs a background service. Local receipt aliases are not signed attestations or authenticated human identities.

## Native offline workbench

**Secure Delivery Offline Workbench 1.2.0** adds real native file/configuration controls, original-engine analysis, searchable findings, full evidence, exact export and durable review history. Prepared scenarios run inside this same application. [Usage, profile privacy and complete compiled-app test](docs/native-application.md) · [Dated candidate validation](docs/reports/native-workbench-2026-11-11.md).

Review real inventory JSON with the original exact-cent summarizer, or inspect an authorized four-asset release with the original bounded preflight. The GUI deliberately never executes incoming applications or substitutes matching hashes for authenticated provenance. The portable Windows recipe bundles the patched runtime; no separately installed Python/Node or baked password is needed. Publication and installation are separate review steps, not implied by a source badge.

## What works

- **Reproducible application:** explicit six-file zipapp allowlist, fixed ZIP metadata, deterministic payload bytes for the same source/commit/version, no embedded secrets or development dependencies.
- **Layered validation:** Windows/macOS/Linux tests, Python 3.12/3.14 lanes, property-based monetary checks, lint/format/types, branch-inclusive coverage >=85%, performance budgets, workflow contract tests, dependency audit, Gitleaks, Trivy, actionlint, ShellCheck and CodeQL.
- **Restricted container:** digest-pinned Python image, fixed non-root UID, real CI runs with no network, read-only filesystem, dropped capabilities, resource limits and no-new-privileges. Developer Docker Desktop is not required or changed.
- **Scoped SBOM:** CycloneDX inventory of the shipped dependency-free application; the separately supplied interpreter/OS are explicitly outside this zipapp SBOM. CI scans the actual container OS and generates an additional image SBOM on its runner.
- **Keyless release provenance:** GitHub attestations for the release manifest and each shipped asset, using an ephemeral GitHub workflow identity rather than a stored private signing key.
- **Independent trust policy:** consumers specify repository, exact source SHA, stable tag and signing workflow. Verification checks these identities using GitHub CLI; a manifest's own identity claims are not a trust anchor.
- **Fail-closed promotion:** copy candidate bytes into an owned staging directory, authenticate those exact bytes, run the fixed health probe, then atomically change the active-slot pointer. Failed verification/health leaves the old pointer unchanged.
- **Explicit rollback:** reauthenticate a caller-selected previous version and source commit. No implicit downgrade, checksum-only deployment, or production/cloud mutation.
- **[Verified impact and operational receipts](docs/operations-review.md):** authenticate candidate and current active bytes before a nonexecuting member/asset comparison; atomically commit pointers with the newest20 successful transition receipts and asserted operator/change context.
- **Live adversarial release checks:** actual GitHub verification rejects changed payloads, rewritten matching manifests, wrong repositories, workflows, source commits and tags before publication.

This is an educational deployment lab, **not a production platform, a malware sandbox, a certification, or a claim of a particular SLSA assurance level**. [Threat model and limitations](docs/security.md).

## Quick start: source demonstration

Requires Python >=3.12. No package installation is needed to run the application itself.

```text
git clone https://github.com/JasonStys/secure-delivery-pipeline-lab.git
cd secure-delivery-pipeline-lab
python -m delivery.probe --input examples/inventory.json
```

Expected synthetic result:

```json
{"inventory_value_usd":"1727.40","products":3,"units":46}
```

This runs source you have elected to trust; it does not prove download provenance. For authenticated release use, follow the next section.

## Verify a published download

Install [official GitHub CLI](https://cli.github.com/) and obtain the desired **full source SHA independently** from the release/tag on GitHub. A release manifest is not an independent source of trust. GitHub CLI may require its normal user-managed authentication; never paste tokens into this repo.

From a reviewed source checkout:

```text
gh release download v1.1.0 --repo JasonStys/secure-delivery-pipeline-lab --dir out/download --pattern release.json --pattern release-probe-1.1.0.pyz --pattern sbom.cdx.json --pattern validation.json
python -m delivery verify --directory out/download --version 1.1.0 --commit FULL_INDEPENDENT_SOURCE_SHA
```

The four-file allowlist is intentional. `live-verification.json` is a separate release-job report and is not part of this deployment bundle.

Do **not** run the downloaded zipapp before verification. A successful result is `{"status":"authenticated"}`. Offline/network/identity failures reject the release; there is no unsafe fallback. GitHub CLI, the operating system, and the verifier source must themselves be trusted.

For a disposable local deployment:

```text
python -m delivery promote --directory out/download --root lab-state --version 1.1.0 --commit FULL_INDEPENDENT_SOURCE_SHA
```

Use a new empty directory or a directory already marked by this lab. Existing unrelated data is not overwritten. Promotion runs only this authored, authenticated application's fixed self-test. It does not install a service or change your other apps.

`preflight` is available for debugging structure/hashes, but its output says **integrity-only-not-authenticated**; it must never be substituted for `verify` or `promote`.

[Full commands, recovery and rollback](docs/runbook.md) · [Manifest/API contracts](docs/contracts.md).

## Validate locally

Create a repo-specific virtual environment and install the complete hash lock:

```text
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-dev.lock
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe scripts/code_map.py --check
.\.venv\Scripts\python.exe -m pytest --cov --cov-report=json:artifacts/coverage.json --junitxml=artifacts/junit.xml
.\.venv\Scripts\python.exe scripts/benchmark.py
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
bash scripts/validate.sh
```

Scanner binaries are individually hash-pinned in `tools.lock.json`; their installer targets hosted **Linux amd64 CI**, not arbitrary operating systems. CI handles real container/secret/static/security checks; no Docker Desktop repair is necessary.

All generated local results live under ignored `artifacts/`. CI puts public-safe results in run summaries/logs. There is **no Actions artifact-upload step or cache-save step**. Release assets use GitHub Releases, separate from Actions artifact storage. Never upload private inputs or credentials as evidence.

## Documentation and file guide

Every authored Python file has a generated exact-line map of definitions, parameters and assigned variables, plus function/class contracts. Run `python scripts/code_map.py` after formatting; CI rejects stale maps.

| File | Responsibility |
|---|---|
| `delivery/desktop.py` | Real native Tk controls, retained worker/owner lifecycle, results, history and support. |
| `delivery/desktop_project.py` | Original exact-cent inventory and four-asset integrity preflight adapter; no authentication bypass or execution. |
| `delivery/desktop_io.py` | Closed bounded JSON and stable regular-descriptor input/export contracts. |
| `delivery/desktop_state.py` | Owned durable SQLite history, immutable bundles and pre-initialization fixed-file admission. |
| `delivery/inputs.py` | Bounded authorized source reads with descriptor identity and nonblocking special-file refusal. |
| `scripts/build_native.py` | Actual patched-runtime one-file build and public resource/source identity binding. |
| `scripts/native_common.py` | Collect actual Python/Tcl-Tk/freezer notices and generate authored icon. |
| `scripts/native_entry.py` | Complete native executable entry point and explicit synthetic acceptance option. |
| `scripts/native_acceptance.py` | Actual widgets, independent eight-workflow oracles and durable reopen journey. |
| `scripts/test_native_app.py` | Minimal-environment actual EXE, runtime/source identity and normal two-process completion proof. |
| `docs/reports/runner-network-2026-11-11.md` | Actual setup DNS observations, bounded signed-mirror acquisition and explicit interpretation limits. |
| `scripts/check_tk_runtime.py` | Actual selected-Python native imports and loaded Tcl requirement; no display/install fallback. |
| `tests/test_tk_runtime.py` | Real isolated native interpreter plus loader/query/version and actual workflow negative controls. |
| `tests/test_desktop_gui.py` | Real GUI handlers, busy close and durable review controls. |
| `tests/test_desktop_project.py` | Exact money, genuine unsigned preflight and independent wrong-identity/tamper refusals. |
| `tests/test_desktop_io.py` | Strict JSON and bounded regular descriptor/export edge cases. |
| `tests/test_desktop_state.py` | Owned SQLite transactions, history and immutable bundle semantics. |
| `tests/test_native_inputs.py` | Actual stable-source file identity/limits, platform FIFO and negative cases. |
| `tests/test_profile_admission.py` | Real fixed database/sidecar hardlink and profile alias admission fixtures. |
| `requirements-native.lock` | Complete exact hash-locked portable freezing tools. |
| `docs/native-application.md` | Native application purpose, controls, privacy, build and trust boundaries. |
| `docs/reports/native-workbench-2026-11-11.md` | Dated local candidate evidence and distinct release/hosted limits. |
| `docs/releases/v1.2.0.md` | Offline workbench candidate scope, separate from authenticated signed-example assets. |
| `delivery/__init__.py` | Authored runtime version; no runtime dependencies. |
| `delivery/__main__.py` | Explicit trust-policy CLI: preflight, verify, impact, promote, rollback. |
| `delivery/io.py` | Bounded regular-file reads, duplicate-safe JSON and atomic replacement. |
| `delivery/probe.py` | Exact-cent synthetic inventory application and health self-test. |
| `delivery/verify.py` | Asset/ZIP allowlists, digest checks and exact GitHub signer/source verification. |
| `delivery/build.py` | Reproducible zipapp, scoped CycloneDX SBOM, real-evidence gate and manifest. |
| `delivery/deploy.py` | Owned disposable roots, OS locks, immutable slots, health gates and rollback. |
| `delivery/impact.py` | Full staged authentication of current/candidate bundles, nonexecuting asset/member review and inert exports. |
| `delivery/receipts.py` | Bounded successful transition history validated and committed atomically with pointers. |
| `scripts/validate.sh` | Fail-fast Bash quality/test/performance entry point. |
| `scripts/code_map.py` | Generate/check exact source-header symbol line locations. |
| `scripts/benchmark.py` | Actual 10,000-record timing/throughput/memory measurements and budgets. |
| `scripts/tools.py` | Verify official scanner download hashes before installing one allowlisted binary. |
| `scripts/gate.py` | Check tag/current-main identity and exact-SHA Validate/CodeQL success. |
| `scripts/summary.py` | Honest job summaries from real JUnit, coverage and benchmark files. |
| `scripts/release_smoke.py` | Live cryptographic identity/tamper rejection and actual staged promotion. |
| `tests/conftest.py` | Disposable unsigned fixtures and deterministic property-test settings. |
| `tests/test_probe.py` | Schema, money arithmetic, generated inputs and probe CLI regressions. |
| `tests/test_boundaries.py` | Malformed JSON/files/archives/manifests, tampering and verifier failure paths. |
| `tests/test_delivery.py` | Byte reproducibility, evidence gates, real zipapp health, pointers and rollback. |
| `tests/test_operations.py` | Exact active/candidate verification, no-execution review, bounded receipts, legacy migration and atomic failure preservation. |
| `tests/test_workflows.py` | Permission/action-pin/storage contracts and exact-source release-gate scenarios. |
| `examples/inventory.json` | Three fictional stock records; no customer or employer data. |
| `Dockerfile` | Digest-pinned, dependency-free, non-root container demonstration. |
| `.dockerignore` | Explicit container build-context allowlist. |
| `pyproject.toml` | Runtime metadata and lint/type/coverage/test settings. |
| `requirements-dev.in` | Reviewed direct development tool versions, including pip. |
| `requirements-dev.lock` | Complete transitive development dependency versions and archive hashes. |
| `tools.lock.json` | Official Linux scanner versions, download URLs and SHA256 pins. |
| `.github/workflows/ci.yml` | Four quality lanes, security scanners and real restricted-container tests. |
| `.github/workflows/codeql.yml` | Hosted Python security-extended code scanning. |
| `.github/workflows/release.yml` | Tag-only exact-source gate, rebuild, attest, live checks and draft publication. |
| `.gitattributes` | Stable LF text normalization and binary declarations. |
| `.gitignore` | Exclude environments, generated evidence, runtime state and credential files. |
| `LICENSE` | MIT terms and Jason Stys attribution. |
| `SECURITY.md` | Safe reporting route and supported-scope pointers. |
| `CONTRIBUTING.md` | Review/testing expectations and documentation-map maintenance. |
| `README.md` | Project overview, features, examples and complete file guide. |
| `docs/architecture.md` | Accepted ADR, trust flow, alternatives and complexity tradeoffs. |
| `docs/security.md` | Threat model, mitigations, residual risks and educational control mapping. |
| `docs/contracts.md` | Inventory, manifests, trust policy, zipapp, state and exit-code contracts. |
| `docs/runbook.md` | User/operator workflows, rollback, outages and safe recovery. |
| `docs/operations-review.md` | Authenticated impact workflow, schema-2 successful receipts, migration and identity limits. |
| `docs/reports/operations-2026-11-09.md` | Local 114-test workflow evidence, atomic failure/retention results and CI-discovered dependency repair. |
| `docs/test-plan.md` | Risk-based unit/property/integration/live-release strategy and honest scope. |
| `docs/research.md` | Primary-source design references and pinned tool/image review. |
| `docs/case-study.md` | Employer-facing problem, implementation decisions and evidence links. |
| `docs/release-checklist.md` | Customized pre/post-release readiness and rollback triggers. |
| `docs/reports/validation-1.0.1.md` | Dated measured results, run links, source identity and known limitations. |
| `docs/releases/v1.0.0.md` | Historical failed candidate; tag preserved without publishing. |
| `docs/releases/v1.0.1.md` | Corrected public release scope and verification instructions. |
| `docs/releases/v1.1.0.md` | Refreshed signed example, independent baseline trust and expanded actual release acceptance. |
| `docs/reports/release-refresh-2026-11-09.md` | New source validation, release-gate identity controls and honest live-publication limits. |
| `docs/handbook.md` | Organized usage/design/security/test documentation entry point. |
| `docs/reports/project-guide.docx` | Reviewed Word project guide at the recorded source baseline. |
| `docs/reports/validation-review.docx` | Reviewed Word test evidence, exact baseline and limitations. |
| `docs/reports/validation-evidence.xlsx` | Filterable workflow/test-source evidence Tables and outcome formulas. |
| `docs/reports/publications.json` | Publication byte identities, visual review scope and immutable source metadata. |
| `docs/reports/documentation-refresh-2026-11-09.md` | Completed edition review, package checks and separate integration-CI scope. |

## What this demonstrates

DevSecOps delivery engineering, least-privilege workflow design, supply-chain verification, security regression testing, reproducible packaging, Linux containers, cross-platform Python/Bash automation, operational recovery and clear engineering evidence.

Future extensions could add an approved hosted deployment or a reusable isolated builder. They are not silently implied by this lab and would need their own threat model and tests.

## Documentation editions

Start with the [organized handbook](docs/handbook.md) for current usage, design, security and test guidance. Reviewed downloadable editions: [project-guide.docx](docs/reports/project-guide.docx) · [validation-review.docx](docs/reports/validation-review.docx) · [validation-evidence.xlsx](docs/reports/validation-evidence.xlsx).

[Publication identities and source scope](docs/reports/publications.json) · [Documentation validation record](docs/reports/documentation-refresh-2026-11-09.md). Historical results retain their own tested revision and date.

## Disposable-runner network boundary

[Observed setup failures and signed APT acquisition hardening](docs/reports/runner-network-2026-11-11.md). Source/core/native assertions remain mandatory; mirror selection is not a proven DNS repair or permission to bypass unavailable dependencies.

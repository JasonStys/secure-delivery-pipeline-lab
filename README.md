# Secure Delivery Pipeline Lab

Created by **Jason Stys** — [GitHub](https://github.com/JasonStys) · [LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/).

[![Validate](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions/workflows/codeql.yml)

A working DevSecOps reference that builds a small application, gates its release on tests and security checks, creates keyless GitHub provenance, and rejects altered or incorrectly signed downloads before lab deployment.

[Download verified release v1.0.1](https://github.com/JasonStys/secure-delivery-pipeline-lab/releases/tag/v1.0.1) · [Measured validation and security evidence](docs/reports/validation-1.0.1.md). Published-source checks: 95 tests on all four OS/Python lanes, 91.58% combined statement/branch coverage, nine live cryptographic scenarios on hosted Linux and independently on Windows. Follow the verification instructions below before executing a downloaded package.

The application is deliberately modest: a dependency-free inventory CLI using exact cents. The portfolio evidence is the **delivery system**, its trust boundaries, and its measured adversarial tests—not a collection of scanner screenshots.

## What works

- **Reproducible application:** explicit six-file zipapp allowlist, fixed ZIP metadata, deterministic payload bytes for the same source/commit/version, no embedded secrets or development dependencies.
- **Layered validation:** Windows/macOS/Linux tests, Python 3.12/3.14 lanes, property-based monetary checks, lint/format/types, branch-inclusive coverage >=85%, performance budgets, workflow contract tests, dependency audit, Gitleaks, Trivy, actionlint, ShellCheck and CodeQL.
- **Restricted container:** digest-pinned Python image, fixed non-root UID, real CI runs with no network, read-only filesystem, dropped capabilities, resource limits and no-new-privileges. Developer Docker Desktop is not required or changed.
- **Scoped SBOM:** CycloneDX inventory of the shipped dependency-free application; the separately supplied interpreter/OS are explicitly outside this zipapp SBOM. CI scans the actual container OS and generates an additional image SBOM on its runner.
- **Keyless release provenance:** GitHub attestations for the release manifest and each shipped asset, using an ephemeral GitHub workflow identity rather than a stored private signing key.
- **Independent trust policy:** consumers specify repository, exact source SHA, stable tag and signing workflow. Verification checks these identities using GitHub CLI; a manifest's own identity claims are not a trust anchor.
- **Fail-closed promotion:** copy candidate bytes into an owned staging directory, authenticate those exact bytes, run the fixed health probe, then atomically change the active-slot pointer. Failed verification/health leaves the old pointer unchanged.
- **Explicit rollback:** reauthenticate a caller-selected previous version and source commit. No implicit downgrade, checksum-only deployment, or production/cloud mutation.
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
gh release download v1.0.1 --repo JasonStys/secure-delivery-pipeline-lab --dir out/download --pattern release.json --pattern release-probe-1.0.1.pyz --pattern sbom.cdx.json --pattern validation.json
python -m delivery verify --directory out/download --version 1.0.1 --commit FULL_INDEPENDENT_SOURCE_SHA
```

The four-file allowlist is intentional. `live-verification.json` is a separate release-job report and is not part of this deployment bundle.

Do **not** run the downloaded zipapp before verification. A successful result is `{"status":"authenticated"}`. Offline/network/identity failures reject the release; there is no unsafe fallback. GitHub CLI, the operating system, and the verifier source must themselves be trusted.

For a disposable local deployment:

```text
python -m delivery promote --directory out/download --root lab-state --version 1.0.1 --commit FULL_INDEPENDENT_SOURCE_SHA
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
| `delivery/__init__.py` | Authored runtime version; no runtime dependencies. |
| `delivery/__main__.py` | Explicit trust-policy CLI: preflight, verify, promote, rollback. |
| `delivery/io.py` | Bounded regular-file reads, duplicate-safe JSON and atomic replacement. |
| `delivery/probe.py` | Exact-cent synthetic inventory application and health self-test. |
| `delivery/verify.py` | Asset/ZIP allowlists, digest checks and exact GitHub signer/source verification. |
| `delivery/build.py` | Reproducible zipapp, scoped CycloneDX SBOM, real-evidence gate and manifest. |
| `delivery/deploy.py` | Owned disposable roots, OS locks, immutable slots, health gates and rollback. |
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
| `docs/test-plan.md` | Risk-based unit/property/integration/live-release strategy and honest scope. |
| `docs/research.md` | Primary-source design references and pinned tool/image review. |
| `docs/case-study.md` | Employer-facing problem, implementation decisions and evidence links. |
| `docs/release-checklist.md` | Customized pre/post-release readiness and rollback triggers. |
| `docs/reports/validation-1.0.1.md` | Dated measured results, run links, source identity and known limitations. |
| `docs/releases/v1.0.0.md` | Historical failed candidate; tag preserved without publishing. |
| `docs/releases/v1.0.1.md` | Corrected public release scope and verification instructions. |

## What this demonstrates

DevSecOps delivery engineering, least-privilege workflow design, supply-chain verification, security regression testing, reproducible packaging, Linux containers, cross-platform Python/Bash automation, operational recovery and clear engineering evidence.

Future extensions could add an approved hosted deployment or a reusable isolated builder. They are not silently implied by this lab and would need their own threat model and tests.

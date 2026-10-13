# Threat model and security review

Author: Jason Stys. Reviewed: 2026-10-13. This is an educational lab, not an authorization to operate or certification.

## Assets and boundaries

Protect source identity, release bytes, meaningful validation evidence, workflow token scope and the last known-good disposable deployment pointer. Public examples contain fictional inventory only. No private keys, user credentials, private datasets or cloud-account secrets are required or published.

Untrusted boundaries include downloaded manifests/assets, local input JSON, mutable deployment state and external metadata/verification availability. Trusted foundations include reviewed verifier/source, Python/OS, official GitHub CLI, pinned actions/scanners, GitHub's workflow identity/attestation services, and the independently selected source policy.

| Threat | Implemented boundary | Evidence |
|---|---|---|
| Changed payload | Bounded SHA256/size comparison plus standard provenance verification | Unit tamper case and live release smoke. |
| Payload and hashes both replaced | Authenticate the manifest and each asset, not just checksums | Live rewritten-manifest rejection. |
| Wrong producer/workflow/commit/tag | CLI repository, signer workflow/digest, source digest/ref and hosted-runner constraints | Policy tests and live wrong-identity cases. |
| Path traversal/ZIP links/bombs | Exact filenames/member count, regular-file checks, size/expansion limits; no extraction | Malformed/archive/resource tests. |
| JSON ambiguity | Duplicate keys, non-finite values, bad encoding and oversized documents rejected | Parser regressions. |
| Verify-then-copy substitution | Copy to staging before authentication and health execution | Real staging/deployment tests. |
| Broken candidate or verifier outage | Nonzero/timeout/error means rejection; old active pointer untouched | Failure injection and active-state assertions. |
| Concurrent promotion | Nonblocking OS advisory lock and pointer replacement | Lock contention test on real OS lanes. |
| Accidental unrelated data overwrite | Exact lab marker, new/empty initialization, file allowlist; no broad cleanup | Unrelated-directory preservation test. |
| Fork code obtaining publication credentials | Read-only PR workflows; no `pull_request_target` or `workflow_run` build elevation | Workflow contract tests. |
| Mutable action/tool/base image | Full action SHAs, official binary SHA256 pins, image digest, pip archive hashes | Contracts and actual hash-checking installs. |
| Vulnerable development/runtime packages | Full dependency audit, Trivy filesystem/image gates, CodeQL, Gitleaks | Separate CI jobs; no suppressions. |

## Residual risks and nonclaims

- A trusted maintainer or compromised GitHub/workflow/toolchain can produce malicious signed software. Provenance identifies an origin; it does not prove that software is harmless. Require source review and independent trust selection.
- GitHub CLI and its authentication/trust roots are externally supplied. Network/verifier outages block new verification/promotion/rollback. They do not activate an unsigned fallback.
- This authored probe's health check is not a sandbox for arbitrary malware. `-I`, a small environment, fixed argv and timeouts reduce accidental interference, not all OS capabilities. Do not generalize the executor to untrusted programs.
- Local administrator/same-user interference, compromised parent directories, hard links, hostile filesystems, malicious inherited OS tooling and guaranteed power-loss durability are not fully defended. Put disposable state in a trusted user-owned location; this is not a multi-user service.
- The zipapp SBOM explicitly excludes the externally supplied Python interpreter/OS. The actual container is scanned separately; no scanner proves absence of unknown vulnerabilities.
- Resource bounds apply to this small format, not arbitrary binaries or every archive format. The probe is a CLI, not an internet-facing server.
- A local receipt/state pointer is not a signature. Rollback always requires independent previous-release identity and fresh authentication. Evidence-only reports are not permission to execute software.
- GitHub Releases are not automatically declared immutable by this code. Exact SHA/workflow/tag verification detects identity changes; published tags/assets must not be rewritten by operators.

## Educational control mapping

NIST SSDF 1.1 PS.1/PS.2: source protection/provenance and release integrity. PW.7/PW.8: analysis and executable verification. RV.1: dependency/static/security findings and remediation. The mapping describes selected practices, not complete SSDF adoption, FedRAMP compliance, FIPS validation, or a SLSA level.

## Review outcome

The implementation separates integrity-only checks from authentication, uses existing cryptographic verification, never constructs shell commands from manifest data, and retains old deployment state on gate failure. Function and variable locations are indexed in source headers. Pending external CI/live verification results are recorded as pending until actually observed in the validation report.

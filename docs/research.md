# Primary-source design references

Reviewed 2026-10-13. Author: Jason Stys. Standards are design references, not certification claims.

- [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations): public-repository availability, keyless provenance, permissions and consumer verification. The reviewed docs use `actions/attest` v4; the implementation pins its full commit.
- [GitHub secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use): action pinning, untrusted workflow code, credentials and injection boundaries.
- [GitHub CLI attestation verify](https://cli.github.com/manual/gh_attestation_verify): independent repository/workflow/source constraints, online verification and trusted-builder limitations. Local CLI 2.97.0 help was inspected rather than guessing supported flags.
- [Pinned attester SBOM parser](https://github.com/actions/attest/blob/1e69f48acb82d1966a394da916b4c1698aa569d6/src/sbom.ts): the CycloneDX detector requires `serialNumber` as well as format/version. Schema validation alone missed this consumer contract; the corrected builder emits deterministic UUIDv5 identity and tests it.
- [SLSA specification 1.2](https://slsa.dev/spec/v1.2/): supply-chain provenance/trust concepts. This lab does not assert Build L3 or any other assurance level.
- [NIST SSDF](https://csrc.nist.gov/projects/ssdf): selected source/release protection, software verification and vulnerability-response practices.
- [CycloneDX JSON specification](https://cyclonedx.org/docs/1.6/json/): scoped application inventory, component identities and dependencies. The external interpreter/OS are not silently omitted under a universal SBOM claim.
- [Python zipapp](https://docs.python.org/3/library/zipapp.html), [zipfile](https://docs.python.org/3/library/zipfile.html), [subprocess](https://docs.python.org/3/library/subprocess.html): inspect archives without extraction, fixed command arrays, timeouts and executable packaging.
- [Gitleaks](https://github.com/gitleaks/gitleaks), [Trivy](https://github.com/aquasecurity/trivy), [actionlint](https://github.com/rhysd/actionlint): scanner scope and official release assets. Installer checks pinned hashes before running binaries.

Official GitHub API refs/assets were inspected on the review date: checkout `d23441a48e516b6c34aea4fa41551a30e30af803`, setup-python `ece7cb06caefa5fff74198d8649806c4678c61a1`, attest `1e69f48acb82d1966a394da916b4c1698aa569d6`, CodeQL `24c54180a607b1449ed407dd24f251e4e9147c8d`. Scanner versions/hashes are in `tools.lock.json`.

The initial official Python 3.14.6-slim candidate was pinned, but its real Trivy image gate found 88 HIGH and 3 CRITICAL Debian findings, including unnecessary OS packages. It was not released. The smaller official Python 3.14.6-alpine OCI index was resolved without starting Docker Desktop: `sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92`. The image applies signed upstream APK security updates and removes unneeded pip. The base is pinned, but upstream patched package resolution can change across build dates; byte-reproducibility claims apply to the zipapp, not to all container bytes. Every actual image is still audited without advisory exclusions.

PyPI versions are explicit and transitive development archives hash-locked. `requirements-dev.lock` is generated with pip-tools 7.6.2 and `--allow-unsafe` so pip itself is pinned. Runtime has no external packages. Re-review pins and security findings before future releases, without overwriting already published release assets.

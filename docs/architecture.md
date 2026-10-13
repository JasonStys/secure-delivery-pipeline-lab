# ADR-001: Verified, dependency-free lab delivery

Status: Accepted. Date: 2026-10-13. Implementation author: Jason Stys.

## Context

The portfolio needs executable DevSecOps evidence without paid hosting, stored signing keys, repairing the developer's Docker Desktop, or consuming the account's full Actions artifact allowance. A consumer must distinguish integrity from authenticated producer identity. A failed candidate must not destroy the previous good deployment.

## Decision

Use Python for bounded parsing, deterministic packaging, orchestration and cross-platform tests; Bash for a small fail-fast CI entry point; YAML for pinned workflow definitions; a restricted Linux container for an actual runtime check. Do not add unrelated languages merely to inflate language counts.

GitHub's standard keyless attestations and official CLI implement signature/trust verification. The consumer independently supplies repository, full commit SHA, stable version/tag and workflow. The custom code performs schema/hash/size/ZIP validation and calls the established verifier with explicit policy. It does not implement a signature algorithm or trust an unsigned manifest as proof of authenticity.

```text
reviewed source -> read-only CI/security gates -> explicit green tag dispatch
  -> rebuild + actual measurements -> deterministic payload + SBOM + evidence
  -> GitHub keyless provenance -> live adversarial verification -> public release

consumer's independent identity policy + downloaded bytes
  -> owned staging copy -> structure/hashes -> cryptographic identity verification
  -> fixed authored health probe -> immutable slot -> atomic active pointer
```

The release job has signing/publication permissions only after a read-only gate. The same trusted authored release job currently builds and signs; it is **not** a separately isolated reusable trusted builder and no SLSA level is claimed. A malicious maintainer/workflow dependency or compromised GitHub account is a residual risk.

## Options considered

| Option | Benefits | Costs/risks |
|---|---|---|
| Checksums only | Simple offline integrity checks | Attacker can replace both payload and hashes; rejected as a deployment trust mechanism. |
| Custom private-key signing service | Independent key management possible | New key custody/rotation/service burden; unnecessary for this scoped portfolio lab. |
| GitHub keyless attestations | Standard verifier, ephemeral identity, source/workflow binding | Online trust service and trusted CLI dependencies; GitHub/workflow compromise remains relevant. Selected. |
| Full hosted Kubernetes platform | Real service rollout semantics | Hosting costs and a much larger threat model; deferred to a dedicated platform repo. |

## Complexity and performance

Inventory validation is O(n) time/O(n) unique-ID space for at most 10,000 rows. Money uses integer cents after validated decimal conversion, not binary floating point. Release hashing and staging are O(B), bounded by three assets of at most 2 MiB each plus a 64 KiB manifest. ZIP expansion is capped at 1 MiB across six regular allowlisted members; nothing is extracted during verification.

Promotion/rollback serializes only one disposable root with an OS advisory lock. Same-directory atomic pointer replacement avoids an intermediate partially written state. Files and pointers are flushed; directory-fsync/power-loss guarantees across every filesystem are not claimed. Orphan immutable slots can remain after a process crash; they are not silently activated or automatically deleted.

## Consequences

No third-party application runtime dependencies, public backend, user accounts, permanent signing secret, arbitrary command hook or production mutation. Verification needs an online GitHub CLI trust path. Tests differentiate mocked verifier-policy unit tests from actual published-release signature tests. New versions can reuse the mechanism, but their source SHA/tag remains an explicit trust decision.

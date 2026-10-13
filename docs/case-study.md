# Case study: a release pipeline that can reject its own altered output

Built by Jason Stys for a software/DevSecOps/cybersecurity portfolio. This is an independently authored educational reference, not a production customer engagement or military deployment.

## Problem

A green unit-test badge does not establish who produced a download or what code it came from. A checksum can detect accidental damage, but an attacker can change the software and recompute the checksum. Operations also need a failed candidate not to replace their last known-good build.

## Implementation

Use a deliberately small exact-cent inventory CLI so the delivery boundary is understandable. Generate deterministic package bytes, a scoped SBOM and actual measured test evidence. Require exact-SHA platform/security checks before signing and publishing a tagged build. Authenticate downloads with standard GitHub keyless provenance under independently chosen source/workflow policy.

Copy into owned staging before verification, run a real fixed health probe only after authentication, and change an atomic active-slot pointer rather than rewriting an in-use application. Previous slots are retained; rollback also reauthenticates explicit identity.

## Evidence

[Dated validation report](reports/validation-1.0.0.md) distinguishes local tests, real hosted OS/container jobs and actual signature rejection checks. [Actions](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions) shows runs, including any failed attempts. [Releases](https://github.com/JasonStys/secure-delivery-pipeline-lab/releases) contains application, SBOM and public-safe evidence.

## Engineering judgment

The implementation avoids a custom signature scheme, dependency-heavy demo service, arbitrary untrusted-code executor, production credentials or misleading compliance badge. It states online trust/OS/workflow compromise limits. CI summaries preserve useful evidence without uploading artifacts into the account's full Actions storage quota.

This demonstrates trust-boundary reasoning, automated release controls, practical Python/Bash, cross-platform systems testing, reproducibility, performance measurement and operational recovery. It does not replace job-specific qualifications or demonstrate years of professional production experience by itself.

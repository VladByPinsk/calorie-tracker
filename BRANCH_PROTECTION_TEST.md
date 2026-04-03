# Branch Protection Test

This branch verifies that GitHub branch protection is working correctly.
It also contains the complete initial project setup (see full scope below).

## Branch protection checks

- Direct pushes to `main` are blocked ✅
- Pull Requests are the only way to merge into `main` ✅
- CI must pass before merge is allowed ✅
- Owner approval is required ✅

## Full scope of changes in this PR

This PR is larger than a typical branch-protection test — it includes the
complete initial project setup:

- Gradle 9.4.1 + Java 26 (Amazon Corretto) toolchain
- Spring Boot 4.0.0 + Spring Cloud 2025.0.0 + Spring AI 1.0.0
- All 8 microservices + 2 infrastructure services (stub scaffolding)
- Web scaffold (React 19 + Vite + TypeScript + Vitest + ESLint 9)
- Mobile scaffold (React Native 0.76 + Expo 52 + TypeScript + ESLint 9)
- GitHub Actions CI with path-based job filtering (`dorny/paths-filter`)
- Single `CI` aggregator status check so skipped jobs don't block merges
- Branch protection scripts (`setup-branch-protection.sh`)

_This branch can be merged after the PR is reviewed._

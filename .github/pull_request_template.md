## Summary
<!-- What does this PR do? Link the Jira/GitHub issue it resolves. -->
Closes #

## Affected service(s)
<!-- Tick all that apply -->
- [ ] `api-gateway`
- [ ] `auth-service`
- [ ] `user-service`
- [ ] `food-service`
- [ ] `diary-service`
- [ ] `ai-service`
- [ ] `analytics-service`
- [ ] `notification-service`
- [ ] `web` (React)
- [ ] `mobile` (Expo)
- [ ] `infrastructure` / DevOps

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Refactor / tech debt
- [ ] Infrastructure / DevOps
- [ ] Documentation

## How to test
<!-- Steps for the reviewer / Copilot to understand what was verified -->
1.
2.

## Checklist
- [ ] Tests added / updated (unit `*Test.java` and/or integration `*IT.java`)
- [ ] All CI checks pass (Checkstyle · JaCoCo ≥ 70 % · Trivy · CodeQL)
- [ ] No secrets or credentials committed
- [ ] Flyway migration added (if DB schema changed)
- [ ] Both `en` and `ru` i18n keys added (if UI strings changed)
- [ ] Spec / docs updated (`CALORIE_NUTRITION_TRACKER_SPEC.md`) if API contract changed
- [ ] RFC 7807 error shape used on any new REST endpoint
- [ ] Kafka event payload includes `eventId`, `occurredAt`, `userId` (if event added)
- [ ] Docker Compose works locally (`docker compose up`)
- [ ] New environment variables documented (`.env.example` or Config Server)

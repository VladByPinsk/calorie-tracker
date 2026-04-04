# GitHub Copilot — Pull Request Instructions

> This file covers two concerns:
>   1. **PR creation** — how Copilot should generate or complete a PR description.
>   2. **PR review** — what Copilot should check when reviewing code.
>
> Applied automatically when Copilot interacts with any PR targeting `main`.

---

## Part 1 — Creating a Pull Request

### Title convention
```
<type>(<scope>): <imperative summary, ≤ 72 chars>
```
- **type**: `feat` · `fix` · `chore` · `refactor` · `test` · `docs` · `perf` · `ci`
- **scope**: the affected microservice or layer
  (`auth-service`, `food-service`, `ci`, `web`, `mobile`, `infra`, …)
- Append `!` after scope for breaking changes: `feat(api-gateway)!: …`

Examples:
```
feat(diary-service): add water intake goal endpoint
fix(food-service): correct cosine similarity distance operator
chore(ci): pin Trivy to 0.70.0
feat(auth-service)!: replace HS256 with RS256 JWT signing
```

### Description template Copilot should fill in
```markdown
## Summary
<one sentence: what and why>

## Affected service(s)
<comma-separated list, e.g. diary-service, api-gateway>

## Type of change
<feature | bug | breaking-change | refactor | devops | docs>

## How to test
1. <step>
2. <step>

## Checklist
- [ ] Tests added / updated
- [ ] All CI checks pass
- [ ] No secrets committed
- [ ] Flyway migration added (if schema changed)
- [ ] en + ru i18n keys added (if UI strings changed)
- [ ] Spec updated (if API contract changed)
- [ ] RFC 7807 error shape on any new REST endpoint
- [ ] Kafka event has eventId, occurredAt, userId (if event added)
```

### Labels Copilot should suggest based on the diff

| Files changed | Labels to suggest |
|---|---|
| `services/api-gateway/**` | `service: api-gateway`, `layer: backend` |
| `services/auth-service/**` | `service: auth-service`, `domain: auth`, `layer: backend` |
| `services/user-service/**` | `service: user-service`, `layer: backend` |
| `services/food-service/**` | `service: food-service`, `layer: backend` |
| `services/diary-service/**` | `service: diary-service`, `layer: backend` |
| `services/ai-service/**` | `service: ai-service`, `domain: ai`, `layer: backend` |
| `services/analytics-service/**` | `service: analytics-service`, `layer: backend` |
| `services/notification-service/**` | `service: notification-service`, `layer: backend` |
| `infrastructure/**` | `service: infrastructure`, `layer: infra` |
| `web/**` | `layer: frontend` |
| `mobile/**` | `layer: mobile` |
| `.github/workflows/**`, `docker/**` | `type: devops`, `layer: infra` |
| `**/db/migration/V*.sql` | `domain: database` |
| `**/kafka/**`, `**/events/**` | `domain: kafka` |
| `web/public/locales/**`, `mobile/i18n/**` | `domain: i18n` |
| `**/security/**`, `**/jwt/**` | `domain: auth`, `type: security` |
| `**/*Test.java`, `**/*IT.java` | `type: test` |
| `**/*.md` only | `type: docs` |
| `**/build.gradle.kts`, `**/package.json` | `type: dependencies` |

Size labels (`size: XS/S/M/L/XL`) are applied automatically by the labeler workflow — do not suggest these manually.

---

## Part 2 — Reviewing a Pull Request

---

## Part 2 — Reviewing a Pull Request

> Focus on correctness, security, and project conventions — not style
> (Checkstyle / ESLint enforce style in CI).

### 🔴 Must Block — Security & Data Safety
- Hardcoded secrets, tokens, passwords, or API keys anywhere in the diff.
- SQL built by string concatenation (SQL injection risk) — only parameterised
  queries / Spring Data JPA are allowed.
- JWT validation bypassed or Actuator endpoints exposed without protection.
- User input accepted without Bean Validation (`@Valid`, `@NotNull`, `@Size`, etc.).
- File uploads missing MIME-type or size validation.
- Sensitive data (PII, tokens) logged at any level.
- `@Transactional` missing on service methods that write to the database.

### 🔴 Must Block — Correctness
- Kafka consumer without idempotency guard (duplicate `eventId` not handled).
- Missing `@Rollback` / transaction boundary around multi-step writes.
- Race conditions in concurrent diary or analytics updates.
- Flyway migration absent when an `@Entity` field or table structure changed
  (look for `@Column`, `@Table`, `addColumn`, `createTable` changes without
  a corresponding `V<n>__*.sql` in `src/main/resources/db/migration/`).
- Flyway migration that drops or renames a column without a transitional step
  (backward-incompatible schema change).

### 🟡 Should Fix — Quality & Conventions
- `@Autowired` on a field — suggest constructor injection instead.
- Manual DTO ↔ entity mapping — suggest MapStruct.
- Missing unit or integration test for a new public method or endpoint.
- New REST endpoint without RFC 7807 error response shape.
- New Kafka event payload missing `eventId`, `occurredAt`, or `userId`.
- Directly calling Ollama from any service other than `ai-service`.
- Line over 100 characters (Google Java Style limit).
- `any` type in TypeScript files.
- Hardcoded English UI string in JSX/TSX without a corresponding `useTranslation()` call.
  Both `en` and `ru` keys must be present in `public/locales/`.

### 🟡 Should Fix — Observability
- New service endpoint or Kafka consumer missing a Micrometer metric or log statement.
- Exception swallowed with an empty `catch` block.
- AI service call (`ai-service` / Ollama) without a timeout or fallback.

### 🟢 Suggest — Performance
- N+1 query pattern — suggest `JOIN FETCH` or a batch query.
- Large collection returned without pagination (`Page<T>` preferred).
- Missing Redis cache on frequently-read, rarely-changed data (food catalogue, user goals).
- Synchronous inter-service call that could be made async via Kafka.

---

## Checklist Copilot Should Verify on Every PR

| # | Check | How to verify |
|---|---|---|
| 1 | No secrets committed | Grep diff for `password =`, `secret =`, `token =`, `key =` literals |
| 2 | Flyway migration present (if entity changed) | Entity diff vs. migration files |
| 3 | Tests added or updated | Look for `*Test.java` / `*IT.java` additions alongside changed classes |
| 4 | JaCoCo threshold still met | CI runs `jacocoTestCoverageVerification` at 70 % |
| 5 | i18n keys added in both locales | `public/locales/en/` and `public/locales/ru/` parity |
| 6 | RFC 7807 error format on new endpoints | `ProblemDetail` return type or `@ExceptionHandler` present |
| 7 | Kafka payload has required fields | `eventId`, `occurredAt`, `userId` in event record/class |
| 8 | Docker Compose still works | Mention in comment if a new environment variable was added |
| 9 | CalVer / no manual version bump | Versioning is automatic — warn if someone edits `version =` in build files |
| 10 | Spec / API contract updated | If a REST endpoint signature changed, `CALORIE_NUTRITION_TRACKER_SPEC.md` should be updated |

---

## Per-Service Guidance

### `auth-service`
- Passwords must be hashed with BCrypt — never stored in plaintext.
- JWT claims must include `userId`, `roles`, `iat`, `exp`.
- MFA flows (TOTP) must validate the time window — do not widen the window > 1 step.

### `api-gateway`
- Route changes must preserve the `/api/v1/<service>/` prefix convention.
- Rate-limiting rules (Bucket4j) should be reviewed if touched — loosening limits needs justification.

### `food-service`
- pgvector queries must use cosine similarity (`<=>`) — not Euclidean (`<->`).
- External API calls (Open Food Facts, barcode lookup) must have a circuit breaker.

### `ai-service`
- Prompt templates must not allow user input to escape into system-level instructions
  (prompt injection guard).
- All Ollama calls need a configurable timeout and a graceful fallback response.

### `diary-service`
- Calorie / macro totals must be re-calculated server-side — never trust client-sent totals.

### `analytics-service`
- Aggregation queries must use read replicas or materialised views for large datasets.

### `notification-service`
- Push/email must respect `user.notificationsEnabled` flag before sending.

---

## Tone & Format

- Be specific: quote the file path and line when flagging an issue.
- Separate blocking issues (🔴) from suggestions (🟡 🟢) clearly.
- If a pattern is correct but could be improved, phrase it as a suggestion, not a demand.
- Do not comment on auto-generated files (`*MapperImpl.java`, Flyway checksums, lock files).
- Do not comment on formatting — Checkstyle and ESLint handle that in CI.




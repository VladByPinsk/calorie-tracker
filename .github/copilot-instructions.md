# GitHub Copilot — Repository Instructions

> These instructions are automatically applied to every Copilot Chat session
> opened in this repository. Keep them up-to-date as the project evolves.

---

## Project Overview

**Calorie & Nutrition Tracker** — a full-stack, microservice-based application for
tracking food intake, macros, hydration, weight and AI-powered meal recognition.

Supports **English 🇬🇧 and Russian 🇷🇺** throughout — UI, food names, API responses,
and AI-generated content.

---

## Tech Stack

### Backend (Java)
| Layer | Technology |
|---|---|
| Language | Java 26 (Amazon Corretto) |
| Framework | Spring Boot 4.0, Spring Cloud 2025.0.0 |
| Build | Gradle 8 with Kotlin DSL (`build.gradle.kts`) |
| API Gateway | Spring Cloud Gateway (port 8080) |
| Auth | JWT (JJWT 0.12.x), MFA via TOTP, OAuth2 |
| Messaging | Apache Kafka (event bus) |
| Database | PostgreSQL (per-service), Flyway migrations |
| Cache | Redis |
| Object store | MinIO (food photos, avatars) |
| Service discovery | Eureka |
| Config | Spring Cloud Config Server |
| AI | Ollama (self-hosted), Spring AI, pgvector |
| Observability | Micrometer, Prometheus, Grafana, Zipkin |
| Code style | Google Java Style (Checkstyle 10.21.1) |
| Coverage | JaCoCo ≥ 70 % line coverage (enforced in CI) |
| Mapping | MapStruct 1.6.3 |
| Boilerplate | Lombok 1.18.40 |

### Frontend
| Layer | Technology |
|---|---|
| Web | React 19, TypeScript, Bootstrap 5, Vite |
| Mobile | React Native, Expo (iOS-first) |
| i18n | i18next — `public/locales/en/` and `public/locales/ru/` |

### DevOps
| Concern | Tool |
|---|---|
| Versioning | CalVer `YYYY.MM.N` (e.g. `2026.04.1`) |
| Container registry | GHCR (GitHub Container Registry) |
| Image build | Jib (no Docker daemon required) |
| Security scanning | Trivy (FS + container images), CodeQL, dependency-review |
| SBOM | syft → CycloneDX JSON + SPDX JSON, attached to every release |

---

## Microservice Map

| Service | Port | Responsibility |
|---|---|---|
| `api-gateway` | 8080 | Routing, JWT validation, rate limiting (Bucket4j), CORS |
| `auth-service` | 8081 | Registration, login, JWT issuance, MFA, OAuth2 |
| `user-service` | 8082 | User profile, goals, TDEE, weight log |
| `food-service` | 8083 | Food database, barcode lookup, pgvector semantic search |
| `diary-service` | 8084 | Daily food diary, meal entries, water intake |
| `ai-service` | 8085 | Ollama RAG pipeline, photo recognition, NL parsing |
| `analytics-service` | 8086 | Calorie trends, streaks, macro analysis |
| `notification-service` | 8087 | Push notifications, email, SSE |
| `eureka-server` | 8761 | Service registry |
| `config-server` | 8888 | Centralised configuration |

---

## Coding Conventions

### Java
- Follow **Google Java Style** — enforced by Checkstyle. Max line length: 100 chars.
- Use **Lombok** (`@Data`, `@Builder`, `@RequiredArgsConstructor`, etc.) — never write
  boilerplate getters/setters by hand.
- Use **MapStruct** for DTO ↔ entity mapping — never map by hand in service layer.
- All new classes must have unit tests. Minimum line coverage: **70 %** (JaCoCo gate in CI).
- Prefer `record` for immutable DTOs/value objects (Java 16+).
- Use constructor injection — never `@Autowired` on fields.
- Service layer must be `@Transactional` at the method level where appropriate.
- Exceptions: use a custom hierarchy extending `RuntimeException`; catch at the
  controller/advice layer only.
- All public API endpoints must be documented (at minimum: summary + error codes).

### Database
- **Every schema change requires a Flyway migration** in
  `src/main/resources/db/migration/V<n>__<description>.sql`.
- Migrations must be **backward-compatible** (additive: add columns/tables, never drop
  or rename without a transitional migration).
- Use `BIGSERIAL` / `UUID` primary keys consistently per service convention.
- Index foreign keys and any column used in `WHERE` clauses.

### Kafka Events
- Topic naming: `<domain>.<entity>.<event>` in kebab-case
  (e.g. `food.entry.logged`, `user.profile.updated`).
- Event payloads are JSON. Always include `eventId` (UUID), `occurredAt` (ISO-8601),
  and `userId` fields.
- Consumers must be idempotent — use `eventId` to deduplicate.
- Define schemas as Java records in a shared `events` package.

### REST API
- Base path per service: `/api/v1/<resource>` (plural noun).
- Use standard HTTP verbs: `GET`, `POST`, `PUT`/`PATCH`, `DELETE`.
- Error responses follow RFC 7807 Problem Details:
  ```json
  { "type": "...", "title": "...", "status": 400, "detail": "...", "instance": "..." }
  ```
- Paginated list endpoints return `Page<T>` (Spring Data) with `page`, `size`,
  `totalElements`, `totalPages`.
- All timestamps in UTC ISO-8601 (`2026-04-04T12:00:00Z`).

### Frontend (React / TypeScript)
- Strict TypeScript (`"strict": true`) — no `any`.
- Components: functional only, no class components.
- State management: React Query for server state, Zustand for client state.
- i18n: always use `useTranslation()` — never hardcode English strings in JSX.
  Add both `en` and `ru` keys for every new UI string.
- File naming: `PascalCase` for components, `camelCase` for utilities/hooks.

### Mobile (React Native / Expo)
- Use Expo Router for navigation.
- Shared logic with web via hooks — avoid duplicating business logic.
- All i18n keys must exist in both `en` and `ru` namespaces.

---

## Security Rules

- **Never** commit secrets, tokens, passwords, or private keys. Use GitHub Secrets /
  environment variables.
- JWT tokens must be validated in `api-gateway` before routing to downstream services.
- All user-facing inputs must be validated with Bean Validation (`@Valid`, `@NotNull`,
  `@Size`, etc.).
- SQL: use Spring Data JPA / parameterised queries only — never string concatenation.
- File uploads (food photos): validate MIME type and size in MinIO upload handler.
- Actuator endpoints must NOT be exposed publicly — secure behind internal network or
  add `management.endpoints.web.exposure.include` to only safe endpoints.

---

## Testing Guidelines

| Layer | Tool | Minimum |
|---|---|---|
| Unit tests | JUnit 5 + Mockito | All service classes |
| Integration tests | `@SpringBootTest` + Testcontainers (Postgres, Redis, Kafka) | All repositories + controllers |
| Coverage gate | JaCoCo | ≥ 70 % line coverage per module |

- Use `@DataJpaTest` for repository tests (lighter than full context).
- Use `MockMvc` for controller tests.
- Testcontainers images are managed via the `testcontainers-bom`.
- Test class naming: `<ClassName>Test` (unit), `<ClassName>IT` (integration).

---

## AI Service Notes

- All Ollama calls go through `ai-service` — other services must NOT call Ollama directly.
- Models in use: `gemma3:12b` (text/NL), `qwen3-vl:8b` (vision/food photos),
  `nomic-embed-text` (embeddings).
- RAG pipeline: embed user query → pgvector similarity search on food-service DB →
  context-augmented prompt → Ollama.
- AI responses must respect `user.preferredLanguage` (en / ru).
- Always handle AI timeout/failure gracefully — return a degraded response, never crash.

---

## CalVer & Release

- Versions follow `YYYY.MM.N` (e.g. `2026.04.3`).
- Every merge to `main` automatically creates a new CalVer tag and GitHub Release.
- Docker images are pushed to GHCR tagged `YYYY.MM.N` **and** `latest`.
- To roll back production, use the **Rollback** workflow (Actions → Rollback).

---

## Pull Request Guidelines

When generating or suggesting a pull request description, always follow this structure:

### Title format
```
<type>(<scope>): <short imperative summary>
```
Examples:
- `feat(food-service): add barcode lookup endpoint`
- `fix(diary-service): recalculate macros after entry deletion`
- `chore(ci): upgrade Trivy to 0.70.0`
- `feat(auth-service)!: migrate JWT signing to RS256`  ← breaking change uses `!`

Valid types: `feat` · `fix` · `chore` · `refactor` · `test` · `docs` · `perf` · `ci`

### Description must include
1. **Summary** — one sentence explaining *what* and *why*.
2. **Affected service(s)** — which microservice(s) are changed.
3. **Type of change** — feature / bug / breaking / refactor / devops / docs.
4. **How to test** — concrete steps so reviewer can verify the change locally.
5. **Checklist** — pulled from the PR template; all applicable boxes ticked.

### Label hints for Copilot to suggest
Copilot should recommend adding these labels based on the diff:

| Diff contains | Suggest label |
|---|---|
| New `@RestController` method | `type: feature`, `layer: backend` |
| `**/db/migration/V*.sql` | `domain: database` |
| `**/kafka/**`, `**/events/**` | `domain: kafka` |
| `services/ai-service/**` | `domain: ai`, `service: ai-service` |
| `web/public/locales/**` | `domain: i18n` |
| `services/auth-service/**`, `**/security/**` | `domain: auth`, `type: security` |
| `**/Dockerfile`, `.github/workflows/**` | `type: devops`, `layer: infra` |
| `**/*Test.java`, `**/*IT.java` | `type: test` |
| `**/*.md` only | `type: docs` |

### Breaking change checklist (append when `!` in title or `BREAKING CHANGE` in body)
- [ ] `CALORIE_NUTRITION_TRACKER_SPEC.md` API section updated
- [ ] All downstream services updated to use new contract
- [ ] Flyway migration is backward-compatible or a transitional migration is included
- [ ] API version bumped (`/api/v1/` → `/api/v2/`) if endpoint signature changed

---

## What Copilot Should Always Do

1. Suggest Flyway migrations when any entity field or table changes.
2. Suggest both `en` and `ru` i18n keys when adding frontend strings.
3. Prefer `record` for DTOs, `@Builder` for entities.
4. Include a test for every new public method / endpoint suggestion.
5. Validate inputs with Bean Validation annotations.
6. Avoid `@Autowired` field injection — always suggest constructor injection.
7. When suggesting Kafka producers/consumers, include the idempotency guard.
8. When adding a new REST endpoint, include the RFC 7807 error response shape.
9. Follow Google Java Style — max 100 chars per line, braces on same line.
10. Never suggest hardcoded credentials or disable security checks.



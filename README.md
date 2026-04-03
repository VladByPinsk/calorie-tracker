# 🥗 Calorie & Nutrition Tracker

> Full-stack microservice calorie & nutrition tracking app with self-hosted AI — no external API costs.

[![CI](https://github.com/VladByPinsk/calorie-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/VladByPinsk/calorie-tracker/actions/workflows/ci.yml)
[![Java](https://img.shields.io/badge/Amazon_Corretto-26-FF9900?logo=amazon-aws)](https://aws.amazon.com/corretto/)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-4.0-green?logo=springboot)](https://spring.io/projects/spring-boot)
[![Gradle](https://img.shields.io/badge/Gradle-9-blue?logo=gradle)](https://gradle.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Services & Ports](#-services--ports)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Contributing — Branch & PR Rules](#-contributing--branch--pr-rules)
- [GitHub Branch Protection Setup](#-github-branch-protection-setup)
- [Full Specification](#-full-specification)

---

## 🌟 Overview

A full-stack **calorie and nutrition tracker** with:

- 🍎 Food logging (search, barcode scan, manual entry, copy from previous days)
- 🤖 **AI food photo recognition** — point camera at a meal, AI names foods and estimates portions (Ollama `qwen3-vl:8b`)
- 💬 **Natural language logging** — type *"I had 200g oatmeal with honey"* → AI creates diary entries (RAG + `gemma3:12b`)
- 🔍 **Semantic food search** — search in English or Russian, powered by `pgvector` + `nomic-embed-text`
- 📊 Analytics, streaks, weight tracking, TDEE calculator
- 🌍 Full **English 🇬🇧 + Russian 🇷🇺** support throughout
- 📱 **Web** (React 19) + **iOS** (React Native + Expo)
- 🔐 JWT auth, OAuth2 Google login, MFA (TOTP), Argon2id passwords
- 💯 **100% self-hosted AI** — Ollama runs locally inside Docker, zero external AI API costs

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Java 26 (Amazon Corretto) · Spring Boot 4 · Spring Cloud · Spring AI |
| **Build** | Gradle 9 (Kotlin DSL) — monorepo multi-project |
| **Architecture** | Microservices · Apache Kafka · API Gateway · Eureka · Config Server |
| **AI** | Ollama · `gemma3:12b` (text) · `qwen3-vl:8b` (vision) · `nomic-embed-text` (embeddings) |
| **Database** | PostgreSQL 17 + pgvector · Redis 7 · Flyway migrations |
| **Storage** | MinIO (food photos, avatars) |
| **Web Frontend** | React 19 + TypeScript + Bootstrap 5 + Vite |
| **Mobile** | React Native + Expo (iOS) |
| **Observability** | Zipkin · Prometheus · Grafana · Micrometer |
| **CI/CD** | GitHub Actions · Jib (Docker build, no daemon) · GHCR |
| **Security** | JWT · Argon2id · AES-256 · Bucket4j rate limiting · RBAC |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                   │
│      React 19 Web (Bootstrap 5)    React Native iOS (Expo)      │
└──────────────────┬───────────────────────────┬───────────────────┘
                   │ HTTPS / REST + SSE        │ HTTPS + Push
┌──────────────────▼───────────────────────────▼───────────────────┐
│           API GATEWAY  (Spring Cloud Gateway · :8080)            │
│   JWT validation · Rate limiting (Bucket4j) · Routing · CORS    │
└──┬──────────┬──────────┬──────────┬──────────┬──────────┬────────┘
   │          │          │          │          │          │
┌──▼──┐  ┌───▼──┐  ┌────▼───┐  ┌───▼──┐  ┌───▼──┐  ┌───▼────────┐
│Auth │  │User  │  │ Food   │  │Diary │  │ AI   │  │Analytics   │
│8081 │  │8082  │  │ 8083   │  │8084  │  │8085  │  │8086        │
└──┬──┘  └──────┘  └────────┘  └───┬──┘  └──────┘  └────────────┘
   │                                │
   │                         ┌──────▼──────────┐
   │                         │  Notification   │
   │                         │  Service :8087  │
   │                         └─────────────────┘
   └──────────────────────────────────┬──────────────────────────────
                                      │
          ┌───────────────────────────▼──────────────────────────┐
          │              APACHE KAFKA  (Event Bus)               │
          │  user.registered · diary.entry.created               │
          │  ai.food.recognized · analytics.report.ready         │
          └──────────────────────────────────────────────────────┘
                                      │
   ┌──────────┬───────────────────────┼──────────────────────────┐
   │          │                       │                          │
┌──▼───┐  ┌───▼─────┐  ┌─────────────▼──┐  ┌────────────────────▼─┐
│PgSQL │  │  Redis  │  │     MinIO       │  │  Ollama (AI)         │
│+pgvec│  │ Cache   │  │ Photos/Avatars  │  │ gemma3:12b           │
└──────┘  └─────────┘  └────────────────┘  │ qwen3-vl:8b (vision) │
                                            │ nomic-embed-text     │
                                            └──────────────────────┘
┌──────────────────────────────────────────────────────────────────┐
│             SPRING CLOUD INFRASTRUCTURE                          │
│  Eureka :8761 · Config Server :8888 · Zipkin :9411              │
│  Prometheus :9090 · Grafana :3001                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Services & Ports

| Service | Port | Database | Responsibility |
|---|---|---|---|
| **api-gateway** | 8080 | — | Routing, JWT validation, rate limiting, CORS |
| **auth-service** | 8081 | `auth_db` | Register, login, JWT, MFA, OAuth2 Google |
| **user-service** | 8082 | `user_db` | Profile, goals, TDEE, weight logs |
| **food-service** | 8083 | `food_db` | Food DB, barcode lookup, pgvector search |
| **diary-service** | 8084 | `diary_db` | Daily food logs, meals, water tracking |
| **ai-service** | 8085 | — | Ollama RAG pipeline, photo recognition |
| **analytics-service** | 8086 | `analytics_db` | Trends, charts, streaks |
| **notification-service** | 8087 | `notification_db` | Email, push, SSE reminders |
| **eureka-server** | 8761 | — | Service discovery |
| **config-server** | 8888 | — | Centralised config |
| **Zipkin** | 9411 | — | Distributed tracing |
| **Prometheus** | 9090 | — | Metrics collection |
| **Grafana** | 3001 | — | Metrics dashboards |

---

## 🚀 Quick Start

### Prerequisites

- **Java 26** — [Amazon Corretto 26](https://aws.amazon.com/corretto/)
- **Docker Desktop** — [docker.com](https://www.docker.com/products/docker-desktop/)
- **Node.js 22** — [nodejs.org](https://nodejs.org/)
- **Gradle 9** — or just use the included `./gradlew` wrapper (no install needed)

### 1. Clone & configure environment

```bash
git clone https://github.com/VladByPinsk/calorie-tracker.git
cd calorie-tracker

cp .env.example .env
# Open .env and fill in: DB_PASSWORD, JWT_SECRET, REDIS_PASSWORD, etc.
```

### 2. Start all infrastructure containers

```bash
cd docker
docker compose up -d
```

> First run takes a few minutes while images are pulled.

### 3. Pull AI models (first time only — ~9 GB)

```bash
bash docker/ollama/pull-models.sh
```

This pulls: `gemma3:12b` · `qwen3-vl:8b` · `nomic-embed-text`

### 4. Run all services

```bash
# Spring Cloud infrastructure first
./gradlew :infrastructure:eureka-server:bootRun &
./gradlew :infrastructure:config-server:bootRun &

# Wait ~10s, then start application services
./gradlew :services:auth-service:bootRun &
./gradlew :services:user-service:bootRun &
./gradlew :services:food-service:bootRun &
./gradlew :services:diary-service:bootRun &
./gradlew :services:ai-service:bootRun &
./gradlew :services:analytics-service:bootRun &
./gradlew :services:notification-service:bootRun &
./gradlew :services:api-gateway:bootRun &
```

> Or use Docker Compose to run everything: `docker compose up -d` (after building JARs with `./gradlew bootJar`)

### 5. Run web frontend

```bash
cd web
npm install
npm run dev
# → http://localhost:5173
```

### 6. Run tests

```bash
# All services
./gradlew test

# Single service
./gradlew :services:auth-service:test

# Web
cd web && npm test
```

---

## 📁 Project Structure

```
calorie-tracker/
├── services/
│   ├── api-gateway/               ← Spring Cloud Gateway
│   ├── auth-service/              ← JWT, MFA, OAuth2
│   ├── user-service/              ← profiles, goals, TDEE
│   ├── food-service/              ← food DB, barcode, pgvector
│   ├── diary-service/             ← daily logs, meals, water
│   ├── ai-service/                ← Ollama, RAG, photo recognition
│   ├── analytics-service/         ← trends, charts, streaks
│   └── notification-service/      ← push, email, SSE
├── infrastructure/
│   ├── eureka-server/             ← Service discovery
│   └── config-server/             ← Centralised config
├── web/                           ← React 19 + TypeScript + Bootstrap 5
├── mobile/                        ← React Native + Expo (iOS)
├── docker/
│   ├── docker-compose.yml         ← Full local dev stack
│   ├── postgres/init.sql          ← Creates all 6 databases + pgvector
│   ├── prometheus/prometheus.yml  ← Scrape config
│   ├── nginx/nginx.conf           ← Reverse proxy (prod)
│   └── ollama/pull-models.sh      ← First-time AI model download
├── scripts/
│   └── setup-branch-protection.sh ← GitHub branch rules (gh CLI)
├── build.gradle.kts               ← Root Gradle config (all subprojects)
├── settings.gradle.kts            ← Module includes
├── gradle.properties              ← Parallel build, caching
├── .env.example                   ← All required env variables
└── .github/
    ├── workflows/ci.yml           ← CI: test → build → docker push
    ├── CODEOWNERS                 ← All files owned by @VladByPinsk
    └── pull_request_template.md   ← PR checklist
```

---

## 🌿 Contributing — Branch & PR Rules

> **The `main` branch is fully protected. Nobody — including the repository owner — can push directly to it. Every change must go through a Pull Request and be approved.**

### Branch Model

```
main          ← 🔒 Production. Protected. PRs only. Requires owner approval.
develop       ← 🔒 Integration branch. Protected. PRs only.
feature/*     ← New features  →  PR into develop
fix/*         ← Bug fixes     →  PR into develop
release/*     ← Release prep  →  PR into main  (from develop)
hotfix/*      ← Urgent fixes  →  PR into main  (then backport to develop)
```

### Daily Workflow

```bash
# 1. Always branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/food-barcode-scanner

# 2. Write code, commit with Conventional Commits
git commit -m "feat(food): add barcode scanner integration with Open Food Facts"
git commit -m "test(food): add integration tests for barcode lookup endpoint"

# 3. Push your branch
git push origin feature/food-barcode-scanner

# 4. Open a Pull Request on GitHub
#    → Base: develop  ←  Compare: feature/food-barcode-scanner
#    → Fill in the PR template
#    → All CI checks must go green
#    → Request review from @VladByPinsk

# 5. After approval + green CI → Squash and Merge
```

### Commit Message Format ([Conventional Commits](https://www.conventionalcommits.org/))

```
<type>(<scope>): <short description>

Types:  feat · fix · docs · style · refactor · test · chore · ci · perf
Scopes: auth · user · food · diary · ai · analytics · notification · gateway
        web · mobile · docker · infra

Examples:
  feat(ai): add food photo recognition with qwen3-vl:8b
  fix(diary): correct calorie calculation for custom serving sizes
  chore(docker): update pgvector to pg17
  ci: add docker push job on main merge
  docs: update quick start guide
```

### PR Rules (enforced by GitHub)

| Rule | `main` | `develop` |
|---|---|---|
| Pull Request required | ✅ | ✅ |
| Direct push blocked | ✅ | ✅ |
| Force push blocked | ✅ | ✅ |
| Branch deletion blocked | ✅ | ✅ |
| **Required approvals** | **1 (owner)** | **1** |
| All CI checks must pass | ✅ | ✅ |
| Branch must be up to date | ✅ | ✅ |
| Stale reviews dismissed on new push | ✅ | ✅ |
| Conversations must be resolved | ✅ | ✅ |
| Linear history required (no merge commits) | ✅ | ❌ |
| Rules apply to admins too | ✅ | ❌ |

### CI Checks (must all pass before merge)

Every PR triggers the following jobs in `.github/workflows/ci.yml`:

| Job | What it runs |
|---|---|
| `Test auth-service` | `./gradlew :services:auth-service:test` |
| `Test user-service` | `./gradlew :services:user-service:test` |
| `Test food-service` | `./gradlew :services:food-service:test` |
| `Test diary-service` | `./gradlew :services:diary-service:test` |
| `Test ai-service` | `./gradlew :services:ai-service:test` |
| `Test analytics-service` | `./gradlew :services:analytics-service:test` |
| `Test notification-service` | `./gradlew :services:notification-service:test` |
| `Test api-gateway` | `./gradlew :services:api-gateway:bootJar` |
| `Test Web (React)` | `npm run lint && npm test && npm run build` |
| `Test Mobile (Expo)` | `npm run lint && npx expo export` |
| `Test Infrastructure` | Eureka + Config Server `bootJar` |

---

## 🔒 GitHub Branch Protection Setup

After pushing to GitHub for the first time, run this **once** to apply all branch protection rules:

### Option A — GitHub CLI (recommended)

```bash
# Install gh CLI if not present
brew install gh

# Authenticate (opens browser)
gh auth login

# Apply protection rules to main + develop
bash scripts/setup-branch-protection.sh
```

### Option B — GitHub Web UI (manual)

1. Go to **Settings → Branches → Add branch ruleset** (or classic rules)
2. For **`main`**, enable:
   - ✅ Require a pull request before merging
   - ✅ Required approving reviews: **1**
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners
   - ✅ Require status checks to pass (add all CI job names from the table above)
   - ✅ Require branches to be up to date before merging
   - ✅ Require conversation resolution before merging
   - ✅ Require linear history
   - ✅ Do not allow bypassing the above settings (applies to admins too)
   - ✅ Block force pushes
   - ✅ Block branch deletion
3. Repeat for **`develop`** (same, but uncheck linear history and admin enforcement)

Verify at: `https://github.com/VladByPinsk/calorie-tracker/settings/branches`

---

## 📋 Full Specification

See [`CALORIE_NUTRITION_TRACKER_SPEC.md`](./CALORIE_NUTRITION_TRACKER_SPEC.md) for:
- Complete feature list
- Full DB schema (all 6 databases)
- All REST API endpoints
- Kafka topics and event payloads
- AI pipeline details (RAG, photo recognition, embeddings)
- iOS architecture
- Internationalization (EN + RU)
- Testing strategy
- Phase-by-phase implementation plan

---

## 📜 License

MIT — see [LICENSE](LICENSE)

# 🥗 Calorie & Nutrition Tracker

> Full-stack microservice application | Java 21 · Spring Boot 3 · React 19 · React Native (Expo) · AI-powered

[![CI](https://github.com/VladByPinsk/calorie-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/VladByPinsk/calorie-tracker/actions/workflows/ci.yml)

See [`CALORIE_NUTRITION_TRACKER_SPEC.md`](./CALORIE_NUTRITION_TRACKER_SPEC.md) for the full technical specification.

## Quick Start

### Prerequisites
- Java 21 (Temurin)
- Docker Desktop
- Node.js 22
- Gradle 8 (or use `./gradlew` wrapper)

### 1. Environment
```bash
cp .env.example .env
# Edit .env — fill in DB_PASSWORD, JWT_SECRET, etc.
```

### 2. Start infrastructure
```bash
cd docker
docker compose up postgres redis kafka zookeeper minio ollama zipkin prometheus grafana -d
```

### 3. Pull AI models (first time, ~9 GB)
```bash
bash docker/ollama/pull-models.sh
```

### 4. Run services locally
```bash
./gradlew :infrastructure:eureka-server:bootRun &
./gradlew :infrastructure:config-server:bootRun &
./gradlew :services:auth-service:bootRun &
# ... etc
```

### 5. Run web frontend
```bash
cd web && npm install && npm run dev
```

## Architecture
See [spec section 3](./CALORIE_NUTRITION_TRACKER_SPEC.md#3-microservice-architecture).

| Service | Port |
|---|---|
| API Gateway | 8080 |
| Auth Service | 8081 |
| User Service | 8082 |
| Food Service | 8083 |
| Diary Service | 8084 |
| AI Service | 8085 |
| Analytics Service | 8086 |
| Notification Service | 8087 |
| Eureka | 8761 |
| Config Server | 8888 |
| Zipkin | 9411 |
| Prometheus | 9090 |
| Grafana | 3001 |

## Branch Strategy

```
main          ← production (protected, PRs only, all CI must pass)
develop       ← integration branch (protected, PRs only)
feature/*     ← feature branches → PR into develop
fix/*         ← bug fixes → PR into develop
release/*     ← release preparation → PR into main
hotfix/*      ← urgent prod fixes → PR into main + backport to develop
```

## Contributing
1. Branch off `develop`: `git checkout -b feature/your-feature`
2. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
3. Push and open a PR against `develop`
4. All CI checks must pass + 1 approval required

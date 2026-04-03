# 🥗 Calorie & Nutrition Tracker — Full Technical Specification

> **Stack:** Java 26 · Spring Boot 4 · Spring Cloud · PostgreSQL · Gradle (Kotlin DSL)
> **AI Stack:** Ollama (Local LLM) · Spring AI · pgvector · Custom RAG Pipeline · Tesseract OCR
> **AI Models:** `gemma3:12b` (text/NL) · `qwen3-vl:8b` (vision/food photos) · `nomic-embed-text` (embeddings)
> **Frontend:** React 19 + TypeScript + Bootstrap 5 · React Native + Expo (iOS)
> **Architecture:** Microservices · Apache Kafka · API Gateway · Service Discovery
> **Languages:** English 🇬🇧 + Russian 🇷🇺

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Full Feature List](#2-full-feature-list)
3. [Microservice Architecture](#3-microservice-architecture)
4. [AI Features](#4-ai-features)
5. [Database Schema (per service)](#5-database-schema-per-service)
6. [Kafka Event Bus](#6-kafka-event-bus)
7. [REST API Reference](#7-rest-api-reference)
8. [Inter-Service Communication](#8-inter-service-communication)
9. [Web Frontend Architecture](#9-web-frontend-architecture)
10. [iOS Mobile App Architecture](#10-ios-mobile-app-architecture)
11. [Internationalization (i18n)](#11-internationalization-i18n)
12. [Dependencies](#12-dependencies)
13. [Implementation Phases](#13-implementation-phases)
14. [Infrastructure & DevOps](#14-infrastructure--devops)
15. [Further Considerations](#15-further-considerations)
16. [Architecture Decision Records (ADRs)](#16-architecture-decision-records-adrs)
17. [Testing Strategy](#17-testing-strategy)
18. [Key User Journeys](#18-key-user-journeys)
19. [Performance & Scalability](#19-performance--scalability)
20. [UI/UX Design System](#20-uiux-design-system)
21. [Error Handling & Resilience Strategy](#21-error-handling--resilience-strategy)
22. [Glossary](#22-glossary)

---

## 1. Project Overview

A **full-stack, microservice-based calorie and nutrition tracking application** supporting English and Russian, with AI-powered food recognition, barcode scanning, natural language food logging, and personalized recommendations — all running on a fully self-hosted AI stack (Ollama) with no external AI API costs.

Available on **Web** (React 19) and **iOS** (React Native + Expo).

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    CLIENTS                                           │
│   React 19 Web (Bootstrap 5)          React Native iOS (Expo)       │
└────────────────────┬─────────────────────────┬───────────────────────┘
                     │ HTTPS / REST + SSE       │ HTTPS + Push
┌────────────────────▼─────────────────────────▼───────────────────────┐
│              API GATEWAY  (Spring Cloud Gateway · Port 8080)         │
│    JWT validation · Rate limiting (Bucket4j) · Routing · CORS       │
└──┬──────────┬──────────┬──────────┬──────────┬──────────┬───────────┘
   │          │          │          │          │          │
┌──▼──┐  ┌───▼──┐  ┌────▼───┐  ┌───▼──┐  ┌───▼──┐  ┌───▼────────┐
│Auth │  │User  │  │ Food   │  │Diary │  │ AI   │  │Analytics   │
│8081 │  │8082  │  │ 8083   │  │8084  │  │8085  │  │8086        │
└──┬──┘  └───┬──┘  └────┬───┘  └───┬──┘  └───┬──┘  └───┬────────┘
   │          │          │          │          │          │
   │          │          │       ┌──▼──────────▼──┐      │
   │          │          │       │  Notification  │      │
   │          │          │       │  Service 8087  │      │
   │          │          │       └────────────────┘      │
   └──────────┴──────────┴──────────────┬────────────────┘
                                        │
        ┌───────────────────────────────▼──────────────────────────┐
        │              APACHE KAFKA  (Event Bus)                   │
        │  food.logged · user.registered · diary.entry.created     │
        │  ai.recognition.completed · analytics.report.ready       │
        └───────────────────────────────────────────────────────────┘
                                        │
   ┌────────────┬───────────────────────┼──────────────────────────┐
   │            │                       │                          │
┌──▼───┐  ┌────▼────┐  ┌──────────────▼──┐  ┌────────────────────▼─┐
│PgSQL │  │  Redis  │  │     MinIO        │  │  Ollama (AI)          │
│multi │  │ Cache   │  │ Food Photos      │  │ llama3.1:8b           │
│  DB  │  │ Rate-lmt│  │ User Avatars     │  │ nomic-embed-text      │
│pgvec │  │         │  │                  │  │ llava:7b (vision)     │
└──────┘  └─────────┘  └──────────────────┘  └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│               SPRING CLOUD INFRASTRUCTURE                           │
│  Eureka (8761) · Config Server (8888) · Zipkin (9411)              │
│  Prometheus (9090) · Grafana (3001)                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### Monorepo Structure

```
calorie-tracker/
├── services/
│   ├── api-gateway/               ← Spring Cloud Gateway
│   ├── auth-service/              ← JWT, MFA, OAuth2
│   ├── user-service/              ← profiles, goals, TDEE, weight logs
│   ├── food-service/              ← food DB, barcode, external APIs, pgvector
│   ├── diary-service/             ← daily logs, meals, water
│   ├── ai-service/                ← Ollama, RAG, photo recognition
│   ├── analytics-service/         ← trends, charts, streaks
│   └── notification-service/      ← push, email, SSE
├── infrastructure/
│   ├── eureka-server/
│   └── config-server/
├── web/                           ← React 19 + TypeScript + Bootstrap 5
│   ├── src/
│   ├── public/
│   │   └── locales/               ← en/ ru/ i18n JSON files
│   └── package.json
├── mobile/                        ← React Native + Expo (iOS)
│   ├── app/                       ← Expo Router screens
│   ├── components/
│   ├── i18n/
│   └── package.json
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── nginx/
│   └── ollama/                    ← model pull init scripts
├── settings.gradle.kts            ← Gradle multi-project root
└── .github/
    └── workflows/
        └── ci.yml
```

---

## 2. Full Feature List

### 🍎 Food Logging
- Search food by name (semantic search via pgvector — finds "apple" when you type "яблоко")
- Barcode scan (web camera + iOS native camera) → Open Food Facts API lookup → auto-fill nutrition
- **AI food photo recognition** — point camera at meal → Ollama `llava:7b` identifies foods + estimates grams
- **Natural language logging** — type "I had 200g of oatmeal with milk and honey" → AI parses → creates diary entry
- Meal types: Breakfast, Lunch, Dinner, Snacks
- Portion size (g / ml / pieces) with custom serving sizes
- Quick-add: last 10 used foods per user
- Favourite foods list
- Custom food creation (user-defined macros)
- Copy meals from a previous day
- Saved meal combinations ("My usual breakfast")

### 💧 Water & Hydration
- Log water intake (ml / oz / glasses)
- Daily hydration goal with progress ring
- Quick-add presets (200ml, 330ml, 500ml)
- Hydration reminder notifications

### 🎯 Goals & Profile
- TDEE calculator (Mifflin-St Jeor equation) — age, gender, height, weight, activity level
- Goal types: Lose Weight, Maintain, Gain Muscle
- Auto-calculated daily calorie target with adjustable deficit/surplus
- Macro split goals (protein %, carbs %, fat %)
- Weekly weight logging with trend chart
- BMI display

### 📊 Daily Dashboard
- Calorie ring (consumed vs. goal)
- Macro rings (protein, carbs, fat, fiber)
- Meal-by-meal breakdown accordion
- Water progress bar
- Remaining calories + macros for the day
- "What can I eat?" AI suggestion based on remaining macros

### 📈 Analytics & Reports
- 7-day / 30-day calorie trend line chart
- Macro distribution doughnut chart over time
- Weight progress chart with goal line
- Streak counter (consecutive days with logs)
- Best/worst days analytics
- Calorie vs. goal compliance percentage

### 🤖 AI Features _(see Section 4)_
- Food photo recognition (Ollama `llava:7b`)
- Natural language food parsing (RAG + Ollama `llama3.1:8b`)
- "What can I eat?" meal suggestions
- Weekly nutrition digest email (AI-generated)
- Semantic food search (pgvector `nomic-embed-text`)
- Anomaly detection (very low/high calorie days flagged)

### 🔔 Notifications
- Meal reminders (configurable per meal type)
- Daily calorie goal reached / exceeded alerts
- Hydration reminders
- Weekly digest email (AI-generated, EN or RU)
- Streak milestone celebrations

### 🌍 Internationalization
- Full English 🇬🇧 and Russian 🇷🇺 UI
- Food names stored in both languages
- Dates, numbers, units formatted per locale
- AI responses generated in user's chosen language

### 📱 iOS App (React Native + Expo)
- All features of the web app
- Native camera for food photo capture + barcode scanning
- Push notifications (Expo Notifications)
- Offline mode with SQLite cache (log foods without internet, sync on reconnect)
- Dark mode support
- Haptic feedback on logging actions

### 🔐 Security
- JWT access tokens + refresh token rotation (`HttpOnly` cookies)
- OAuth2 Google login
- MFA (TOTP — Google Authenticator)
- Argon2id password hashing
- AES-256 column encryption for PII
- Rate limiting (Bucket4j + Redis) at API Gateway
- Full audit log per service
- RBAC: `ADMIN`, `USER`

---

## 3. Microservice Architecture

### Service Registry

| Service | Port | Database | Kafka Role | Responsibility |
|---|---|---|---|---|
| **api-gateway** | 8080 | — | — | Routing, JWT validation, rate limiting, CORS |
| **auth-service** | 8081 | `auth_db` | Producer: `user.registered` | Register, login, JWT issue, MFA, OAuth2 |
| **user-service** | 8082 | `user_db` | Consumer: `user.registered` | Profile, goals, TDEE, weight logs |
| **food-service** | 8083 | `food_db` | Producer: `food.indexed` | Food DB, barcode lookup, external APIs, pgvector |
| **diary-service** | 8084 | `diary_db` | Producer: `diary.entry.created` | Daily logs, meals, water tracking |
| **ai-service** | 8085 | — | Consumer + Producer | Photo recognition, NL parsing, RAG, suggestions |
| **analytics-service** | 8086 | `analytics_db` | Consumer: `diary.entry.created` | Trends, reports, streaks |
| **notification-service** | 8087 | `notification_db` | Consumer: multiple | Email, push, SSE, reminders |
| **eureka-server** | 8761 | — | — | Service discovery |
| **config-server** | 8888 | — | — | Centralised config (Git-backed) |

### Package Structure per Service

Each service follows the same internal structure:

```
com.calorietracker.{service-name}
├── config/          ← Spring config beans
├── domain/          ← JPA entities
├── repository/      ← Spring Data repositories
├── service/         ← Business logic
├── controller/      ← REST controllers
├── dto/             ← Java records (request/response)
├── mapper/          ← MapStruct mappers
├── event/           ← Kafka producers & consumers
├── security/        ← JWT filter (auth-service) or gateway filter
└── exception/       ← GlobalExceptionHandler
```

### Service Communication

```
Synchronous (REST via Gateway):
  Client → Gateway → food-service     (search, barcode lookup)
  Client → Gateway → diary-service    (log food, view diary)
  Client → Gateway → ai-service       (photo upload, NL query)
  ai-service → food-service           (fetch food details by ID)
  diary-service → food-service        (validate food exists)

Asynchronous (Kafka):
  auth-service   ──► user.registered     ──► user-service, notification-service
  diary-service  ──► diary.entry.created ──► analytics-service, notification-service
  ai-service     ──► ai.food.recognized  ──► diary-service (auto-create draft entry)
  analytics      ──► analytics.report.ready ──► notification-service (weekly digest)
```

---

## 4. AI Features

### 🧠 Philosophy: Same Self-Hosted Stack, Nutrition Domain

All AI runs locally inside Docker — no API keys, no costs, no data leaving your machine.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI SERVICE  (Port 8085)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Ollama (Docker)                             │  │
│  │  gemma3:12b         → text gen, NL parsing, summaries       │  │
│  │  nomic-embed-text   → food name/description embeddings      │  │
│  │  qwen3-vl:8b        → food photo recognition (multimodal)   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Spring AI     │  │  pgvector        │  │  Tesseract       │   │
│  │  ChatClient    │  │  (in food_db)    │  │  (barcode text   │   │
│  │  EmbeddingModel│  │  food_embeddings │  │   fallback)      │   │
│  └────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                     │
│  FoodPhotoRecognizer · NlFoodParser · MealSuggestionEngine         │
│  FoodEmbeddingIndexer · WeeklyDigestGenerator · AnomalyDetector   │
└─────────────────────────────────────────────────────────────────────┘
```

### What You Will Learn

| Technology | What You Learn |
|---|---|
| **Ollama qwen3-vl:8b** | Multimodal LLMs; image + text prompts; vision AI limitations |
| **pgvector (food domain)** | Semantic food search; embedding multilingual food names |
| **RAG for NL food parsing** | Context-grounded parsing; structured LLM output |
| **Spring AI** | `ChatClient`, `EmbeddingModel`; multimodal messages API |
| **Statistical anomaly detection** | Applying Z-score to nutrition data |
| **Microservice AI** | How to isolate AI as its own service; async result delivery via Kafka |

---

### Feature 1: Food Photo Recognition (Ollama qwen3-vl:8b — Multimodal)

> Point your camera at any meal → AI names the foods + estimates portion sizes.

```
Photo Upload (JPEG/PNG, max 10MB)
         │
         ▼
[1] IMAGE PRE-PROCESSING  (ImagePreprocessor.java)
    - Resize to 1024×1024 max (qwen3-vl performs best at this resolution)
    - Convert to Base64 string for Ollama multimodal API
         │
         ▼
[2] MULTIMODAL LLM  (Ollama llava:7b)
    Spring AI ChatClient with image message:
    System: "You are a nutrition expert. Identify all foods in this image.
             For each food, estimate: name (in {language}), weight in grams,
             calories, protein_g, carbs_g, fat_g.
             Return ONLY valid JSON array: [{name, weight_g, calories,
             protein_g, carbs_g, fat_g, confidence}]"
    Image: base64-encoded photo
         │
         ▼
[3] STRUCTURED OUTPUT PARSING  (StructuredOutputParser.java)
    - Parse JSON array → List<RecognizedFoodDto>
    - Filter items with confidence < 0.4 (too uncertain)
    - Cap at 8 items max
         │
         ▼
[4] FOOD DB MATCHING  (sync call to food-service)
    For each recognized food:
    - Vector search in food_embeddings: find closest DB match
    - If similarity > 0.85 → use DB nutritional data (more accurate)
    - Otherwise → use LLM-estimated values with "AI estimated" flag
         │
         ▼
[5] RETURN to client
    List<FoodRecognitionResultDto> { foodId?, name, weight_g,
        nutrition, source (DB | AI_ESTIMATED), confidence }
    Frontend shows editable card per food → user confirms → diary entry created
```

**Publish Kafka event:** `ai.food.recognized` → diary-service creates draft entries

---

### Feature 2: Natural Language Food Logging (RAG Pipeline)

> "I had 200g of oatmeal with whole milk and a banana" → creates 3 diary entries.

```
User text input (EN or RU detected automatically)
         │
         ▼
[1] LANGUAGE DETECTION  (Java — simple heuristic: Cyrillic chars > 20% = RU)
         │
         ▼
[2] EMBED THE QUERY  (OllamaEmbeddingService)
    nomic-embed-text → float[768]
         │
         ▼
[3] VECTOR SEARCH in food_embeddings  (VectorSearchRepository)
    SELECT food_id, name_en, name_ru, calories_per_100g, ...
    FROM food_embeddings
    ORDER BY embedding <=> query_vector
    LIMIT 15
    → Top candidate foods as RAG context
         │
         ▼
[4] LLM PARSING  (Ollama llama3.1:8b)
    Prompt template: nl-food-parse.st
    "Parse this food log entry: '{userText}'
     Available foods from database: {contextFoods JSON}
     Extract each food item. For each: match to context if possible,
     estimate quantity in grams.
     Return JSON array: [{foodId?, foodName, quantityG, mealType}]
     Respond in {language}."
         │
         ▼
[5] VALIDATION + ENRICHMENT
    - For items with foodId → fetch exact nutrition from food-service
    - For items without match → use LLM-estimated nutrition + flag
    - Validate quantities (0 < qty < 5000g)
         │
         ▼
[6] RETURN ParsedMealDto[] → frontend shows preview → user confirms
```

---

### Feature 3: Semantic Food Search (pgvector)

> Type "high protein breakfast" → finds chicken eggs, Greek yogurt, cottage cheese — not just keyword matches.

**Indexing (on food creation):**
```
food created/updated
→ FoodEmbeddingIndexer (Spring event listener)
→ Embed: "{name_en} {name_ru} {brand} {category}" via nomic-embed-text
→ Store in food_embeddings with food_id
```

**Search flow:**
```
Query string (e.g. "завтрак с высоким белком")
→ Embed query → float[768]
→ SELECT food_id, name_en, name_ru, calories_per_100g
   FROM food_embeddings
   WHERE (user_id IS NULL OR user_id = ?)        ← system + user's custom foods
   ORDER BY embedding <=> query_vector::vector
   LIMIT 20
→ Return ranked FoodSearchResultDto[]
```

**Combined search:** semantic score + keyword fallback (PostgreSQL `ts_vector`) with RRF (Reciprocal Rank Fusion) merge.

---

### Feature 4: "What Can I Eat?" Meal Suggestions

> Based on remaining macros for the day → AI suggests concrete meal ideas.

```
GET /api/v1/ai/suggestions?date={today}
         │
         ▼
[1] FETCH REMAINING MACROS  (call diary-service: today's consumed vs. goal)
    { remainingCalories: 620, remainingProtein: 45g, remainingCarbs: 60g,
      remainingFat: 20g, mealType: "DINNER" }
         │
         ▼
[2] VECTOR SEARCH  (find foods that fit macro profile)
    Embed "dinner {remainingCalories} calories {protein}g protein"
    Top 20 matching foods from food_embeddings
         │
         ▼
[3] RULES ENGINE  (MealSuggestionRules.java)
    Filter out: foods already eaten today, foods user disliked
    Score by: macro fit score (custom weighted formula)
    Top 5 foods selected
         │
         ▼
[4] LLM COMPOSITION  (Ollama llama3.1:8b)
    "Given these 5 food options: {foods}
     The user has {remainingCalories} kcal remaining for dinner.
     Suggest 3 meal combinations with exact portions.
     Format: [{mealName, foods:[{name, quantityG}], totalCalories, totalProtein}]
     Respond in {language}."
         │
         ▼
Return: List<MealSuggestionDto>
```

---

### Feature 5: Weekly Nutrition Digest (AI Email)

- **Schedule:** `@Scheduled` Monday 8:00 AM per user's timezone (notification-service)
- **Analytics-service** computes: avg daily calories, best macro day, worst day, weight delta, streak
- **AI-service** receives `analytics.report.ready` Kafka event → generates 4-sentence digest in user's language
- **Template:** `resources/prompts/weekly-nutrition-digest.st`
- **Delivery:** notification-service → SendGrid

---

### Feature 6: Anomaly Detection (Custom Java Statistics)

Same statistical approach as Finance Tracker, adapted for nutrition:

| Algorithm | Applied to | Flag condition |
|---|---|---|
| Z-Score | Daily calorie total (7-day rolling) | Z > 2.5 or Z < -2.5 |
| Rule-based | Days < 800 kcal | Always flag (potentially dangerous) |
| Rule-based | Days > 3× goal | Always flag |
| Trend | 7-day moving average weight | Unexpected direction vs. goal |

Flags create in-app notifications and are surfaced on the analytics page.

### AI Infrastructure

**Resilience (Resilience4j):**
```
Photo recognition: TimeLimiter 45s (llava is slow), Retry 2×, CircuitBreaker
NL parsing:       TimeLimiter 30s, Retry 3×, CircuitBreaker
Suggestions:      TimeLimiter 20s, Retry 2×, Fallback → top-5 by macro fit only
```

**Redis Caching:**
| Feature | Key | TTL |
|---|---|---|
| NL parse result | `ai:nlparse:{hash(text)}` | 30 min |
| Meal suggestions | `ai:suggest:{userId}:{date}:{mealType}` | 2 hours |
| Food embeddings | Stored in pgvector permanently | — |

---

## 5. Database Schema (per service)

> All services use `pgvector/pgvector:pg17` image (one PostgreSQL instance, multiple databases).
> First Flyway migration in each service: `CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS pgcrypto;`

---

### `auth_db`

```sql
CREATE TABLE users (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email          TEXT NOT NULL UNIQUE,           -- AES-256 encrypted
    password_hash  TEXT NOT NULL,                  -- Argon2id
    role           VARCHAR(20) NOT NULL DEFAULT 'USER',
    mfa_secret     TEXT,                           -- AES-256 encrypted
    mfa_enabled    BOOLEAN NOT NULL DEFAULT false,
    mfa_backup_codes TEXT[],
    active         BOOLEAN NOT NULL DEFAULT true,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT NOT NULL UNIQUE,
    device_info TEXT,
    ip_address  INET,
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked     BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID,
    action      VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id   UUID,
    ip_address  INET,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

### `user_db`

```sql
CREATE TABLE user_profiles (
    user_id          UUID PRIMARY KEY,             -- from auth-service
    full_name        TEXT NOT NULL,                -- AES-256 encrypted
    avatar_url       TEXT,
    date_of_birth    DATE,
    gender           VARCHAR(10),                  -- MALE, FEMALE, OTHER
    height_cm        NUMERIC(5,1),
    weight_kg        NUMERIC(5,1),
    activity_level   VARCHAR(20) NOT NULL DEFAULT 'MODERATE',
    -- SEDENTARY, LIGHT, MODERATE, ACTIVE, VERY_ACTIVE
    goal_type        VARCHAR(20) NOT NULL DEFAULT 'MAINTAIN',
    -- LOSE_WEIGHT, MAINTAIN, GAIN_MUSCLE
    calorie_deficit  INT NOT NULL DEFAULT 0,       -- kcal/day below TDEE (negative = surplus)
    daily_calorie_goal INT,                        -- computed from TDEE or manual override
    protein_goal_g   INT,
    carbs_goal_g     INT,
    fat_goal_g       INT,
    water_goal_ml    INT NOT NULL DEFAULT 2000,
    language         CHAR(2) NOT NULL DEFAULT 'en',  -- 'en' or 'ru'
    timezone         VARCHAR(50) NOT NULL DEFAULT 'UTC',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE weight_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    weight_kg   NUMERIC(5,1) NOT NULL,
    note        TEXT,
    logged_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_weight_logs_user ON weight_logs(user_id, logged_at DESC);

CREATE TABLE disliked_foods (
    user_id  UUID NOT NULL,
    food_id  UUID NOT NULL,
    PRIMARY KEY (user_id, food_id)
);
```

---

### `food_db`

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE foods (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_en           VARCHAR(255) NOT NULL,
    name_ru           VARCHAR(255),
    brand             VARCHAR(255),
    barcode           VARCHAR(50) UNIQUE,
    category          VARCHAR(100),
    calories_per_100g NUMERIC(7,2) NOT NULL,
    protein_per_100g  NUMERIC(6,2) NOT NULL DEFAULT 0,
    carbs_per_100g    NUMERIC(6,2) NOT NULL DEFAULT 0,
    fat_per_100g      NUMERIC(6,2) NOT NULL DEFAULT 0,
    fiber_per_100g    NUMERIC(6,2) NOT NULL DEFAULT 0,
    sugar_per_100g    NUMERIC(6,2),
    sodium_mg_per_100g NUMERIC(7,2),
    serving_size_g    NUMERIC(6,1),                  -- default serving
    serving_label_en  VARCHAR(100),                  -- e.g. "1 slice"
    serving_label_ru  VARCHAR(100),                  -- e.g. "1 ломтик"
    source            VARCHAR(20) NOT NULL DEFAULT 'OPENFOODFACTS',
    -- OPENFOODFACTS, USDA, USER, AI_ESTIMATED
    user_id           UUID,                          -- NULL = global food
    verified          BOOLEAN NOT NULL DEFAULT false,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_foods_barcode  ON foods(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_foods_name_en  ON foods USING gin(to_tsvector('english', name_en));
CREATE INDEX idx_foods_name_ru  ON foods USING gin(to_tsvector('russian', COALESCE(name_ru, '')));
CREATE INDEX idx_foods_user     ON foods(user_id)  WHERE user_id IS NOT NULL;

CREATE TABLE food_embeddings (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    food_id       UUID NOT NULL REFERENCES foods(id) ON DELETE CASCADE UNIQUE,
    content       TEXT NOT NULL,         -- embedded text: "name_en name_ru brand category"
    embedding     vector(768) NOT NULL,  -- nomic-embed-text
    model_version VARCHAR(50) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_food_embeddings_vector
    ON food_embeddings USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE TABLE barcode_cache (
    barcode      VARCHAR(50) PRIMARY KEY,
    food_id      UUID REFERENCES foods(id),
    fetched_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    source       VARCHAR(20) NOT NULL,
    raw_response JSONB                               -- cache raw API response
);
```

---

### `diary_db`

```sql
CREATE TABLE diary_entries (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    food_id             UUID NOT NULL,              -- reference to food-service
    food_name_en        VARCHAR(255) NOT NULL,      -- snapshot at log time
    food_name_ru        VARCHAR(255),
    quantity_g          NUMERIC(7,1) NOT NULL,
    meal_type           VARCHAR(10) NOT NULL,       -- BREAKFAST,LUNCH,DINNER,SNACK
    date                DATE NOT NULL,
    logged_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Computed nutrition snapshot (denormalized for performance)
    calories            NUMERIC(7,2) NOT NULL,
    protein_g           NUMERIC(6,2) NOT NULL,
    carbs_g             NUMERIC(6,2) NOT NULL,
    fat_g               NUMERIC(6,2) NOT NULL,
    fiber_g             NUMERIC(6,2) NOT NULL DEFAULT 0,
    source              VARCHAR(20) NOT NULL DEFAULT 'MANUAL',
    -- MANUAL, BARCODE, AI_PHOTO, NL_PARSE, COPIED
    ai_confidence       NUMERIC(4,3),               -- for AI_PHOTO entries
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_diary_user_date      ON diary_entries(user_id, date DESC);
CREATE INDEX idx_diary_user_date_meal ON diary_entries(user_id, date, meal_type);

CREATE TABLE water_logs (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL,
    amount_ml  INT NOT NULL,
    logged_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_water_user_date ON water_logs(user_id, logged_at DESC);

CREATE TABLE favourite_foods (
    user_id    UUID NOT NULL,
    food_id    UUID NOT NULL,
    added_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, food_id)
);

CREATE TABLE saved_meals (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    name_en     VARCHAR(255) NOT NULL,
    name_ru     VARCHAR(255),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE saved_meal_items (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saved_meal_id UUID NOT NULL REFERENCES saved_meals(id) ON DELETE CASCADE,
    food_id       UUID NOT NULL,
    quantity_g    NUMERIC(7,1) NOT NULL
);
```

---

### `analytics_db`

```sql
CREATE TABLE daily_summaries (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL,
    date             DATE NOT NULL,
    total_calories   NUMERIC(7,2) NOT NULL DEFAULT 0,
    total_protein_g  NUMERIC(6,2) NOT NULL DEFAULT 0,
    total_carbs_g    NUMERIC(6,2) NOT NULL DEFAULT 0,
    total_fat_g      NUMERIC(6,2) NOT NULL DEFAULT 0,
    total_fiber_g    NUMERIC(6,2) NOT NULL DEFAULT 0,
    water_ml         INT NOT NULL DEFAULT 0,
    goal_calories    INT NOT NULL,
    entries_count    INT NOT NULL DEFAULT 0,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, date)
);
CREATE INDEX idx_daily_summaries_user ON daily_summaries(user_id, date DESC);

CREATE TABLE streaks (
    user_id          UUID PRIMARY KEY,
    current_streak   INT NOT NULL DEFAULT 0,
    longest_streak   INT NOT NULL DEFAULT 0,
    last_logged_date DATE
);
```

---

### `notification_db`

```sql
CREATE TABLE notifications (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL,
    type       VARCHAR(30) NOT NULL,
    -- MEAL_REMINDER, GOAL_EXCEEDED, STREAK, WEEKLY_DIGEST, HYDRATION, ANOMALY
    title_en   VARCHAR(255) NOT NULL,
    title_ru   VARCHAR(255),
    body_en    TEXT NOT NULL,
    body_ru    TEXT,
    read       BOOLEAN NOT NULL DEFAULT false,
    sent_push  BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_notifications_user ON notifications(user_id, read, created_at DESC);

CREATE TABLE push_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    token       TEXT NOT NULL UNIQUE,
    platform    VARCHAR(10) NOT NULL DEFAULT 'IOS',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE notification_preferences (
    user_id              UUID PRIMARY KEY,
    meal_reminders       BOOLEAN NOT NULL DEFAULT true,
    hydration_reminders  BOOLEAN NOT NULL DEFAULT true,
    goal_alerts          BOOLEAN NOT NULL DEFAULT true,
    weekly_digest_email  BOOLEAN NOT NULL DEFAULT true,
    streak_alerts        BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE scheduled_reminders (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    meal_type   VARCHAR(10) NOT NULL,
    time_local  TIME NOT NULL,              -- in user's timezone
    enabled     BOOLEAN NOT NULL DEFAULT true
);
```

---

## 6. Kafka Event Bus

### Topic Definitions

| Topic | Producer | Consumer(s) | Description |
|---|---|---|---|
| `user.registered` | auth-service | user-service, notification-service | New user signed up |
| `user.profile.updated` | user-service | analytics-service | Goals/profile changed |
| `food.indexed` | food-service | ai-service | New food added → generate embedding |
| `diary.entry.created` | diary-service | analytics-service, notification-service | Food logged |
| `diary.entry.deleted` | diary-service | analytics-service | Entry removed |
| `water.logged` | diary-service | analytics-service, notification-service | Water intake logged |
| `ai.food.recognized` | ai-service | diary-service | Photo recognition complete → create draft |
| `ai.nl.parsed` | ai-service | diary-service | NL parse complete → create entries |
| `analytics.daily.updated` | analytics-service | notification-service | Daily summary recalculated |
| `analytics.report.ready` | analytics-service | ai-service, notification-service | Weekly report ready |
| `notification.push.send` | notification-service | notification-service (internal) | Trigger push delivery |

### Event Payload Schemas

```json
// user.registered
{
  "userId": "uuid",
  "email": "string (encrypted)",
  "language": "en | ru",
  "timestamp": "ISO-8601"
}

// diary.entry.created
{
  "entryId": "uuid",
  "userId": "uuid",
  "foodId": "uuid",
  "date": "YYYY-MM-DD",
  "mealType": "BREAKFAST | LUNCH | DINNER | SNACK",
  "calories": 320.5,
  "proteinG": 28.0,
  "carbsG": 15.0,
  "fatG": 12.0,
  "source": "MANUAL | BARCODE | AI_PHOTO | NL_PARSE"
}

// ai.food.recognized
{
  "requestId": "uuid",
  "userId": "uuid",
  "photoUrl": "string (MinIO path)",
  "recognizedFoods": [
    {
      "foodId": "uuid | null",
      "name": "string",
      "quantityG": 150,
      "calories": 210,
      "confidence": 0.87
    }
  ],
  "language": "en | ru",
  "timestamp": "ISO-8601"
}

// analytics.report.ready
{
  "userId": "uuid",
  "weekStart": "YYYY-MM-DD",
  "avgDailyCalories": 1850.0,
  "avgProteinG": 120.0,
  "weightDeltaKg": -0.4,
  "currentStreak": 7,
  "language": "en | ru"
}
```

### Kafka Configuration

```yaml
# application.yml (shared config via Config Server)
spring:
  kafka:
    bootstrap-servers: kafka:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      group-id: ${spring.application.name}
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
```

---

## 7. REST API Reference

> All routes via API Gateway at `https://your-domain.com/api/v1/`
> All endpoints require `Authorization: Bearer <token>` unless noted

### Auth — `/api/v1/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | None | Register email + password |
| `POST` | `/login` | None | Login → `{accessToken}` + `refreshToken` cookie |
| `POST` | `/refresh` | Cookie | Rotate refresh token |
| `POST` | `/logout` | Bearer | Revoke session |
| `POST` | `/mfa/setup` | Bearer | Get TOTP QR URI |
| `POST` | `/mfa/verify` | Bearer | Verify TOTP code |
| `GET` | `/oauth2/google` | None | OAuth2 redirect |

### Users — `/api/v1/users`

| Method | Path | Description |
|---|---|---|
| `GET` | `/me` | Get own profile |
| `PUT` | `/me` | Update profile (name, language, goals) |
| `POST` | `/me/tdee` | Calculate TDEE: `{gender, age, height, weight, activity}` → `{tdee, suggestedGoal}` |
| `GET` | `/me/weight` | List weight logs (paginated) |
| `POST` | `/me/weight` | Log weight |
| `DELETE` | `/me/weight/{id}` | Delete weight log |
| `GET` | `/me/push-token` | Get registered push token |
| `POST` | `/me/push-token` | Register Expo push token |

### Food — `/api/v1/foods`

| Method | Path | Description |
|---|---|---|
| `GET` | `/search?q={query}&lang={en\|ru}` | Semantic + keyword search (combined) |
| `GET` | `/{id}` | Get food details |
| `POST` | `/` | Create custom food |
| `PUT` | `/{id}` | Update custom food (own only) |
| `DELETE` | `/{id}` | Delete custom food (own only) |
| `GET` | `/barcode/{ean}` | Barcode lookup → Open Food Facts → USDA → local DB |
| `GET` | `/recent` | User's 10 most recently logged foods |
| `GET` | `/favourites` | User's favourite foods |
| `POST` | `/favourites/{foodId}` | Add to favourites |
| `DELETE` | `/favourites/{foodId}` | Remove from favourites |

### Diary — `/api/v1/diary`

| Method | Path | Description |
|---|---|---|
| `GET` | `/?date={YYYY-MM-DD}` | Get all diary entries for a date |
| `POST` | `/entries` | Log food entry |
| `PUT` | `/entries/{id}` | Update entry (quantity, meal type) |
| `DELETE` | `/entries/{id}` | Delete entry |
| `POST` | `/entries/bulk` | Create multiple entries (after AI recognition) |
| `GET` | `/water?date={date}` | Get water logs for date |
| `POST` | `/water` | Log water intake |
| `DELETE` | `/water/{id}` | Delete water log |
| `GET` | `/saved-meals` | List saved meal combinations |
| `POST` | `/saved-meals` | Save a meal combination |
| `POST` | `/saved-meals/{id}/log` | Log an entire saved meal to diary |
| `POST` | `/copy?from={date}&to={date}` | Copy all entries from one date to another |

### AI — `/api/v1/ai`

| Method | Path | Description |
|---|---|---|
| `POST` | `/food/recognize` | Multipart image → `List<RecognizedFoodDto>` |
| `POST` | `/food/parse-text` | Body: `{text, language}` → `List<ParsedFoodDto>` |
| `GET` | `/suggestions?date={date}&mealType={type}` | Meal suggestions for remaining macros |
| `GET` | `/insights` | Weekly nutrition analysis paragraph |
| `GET` | `/anomalies` | Detected anomaly days |
| `GET` | `/weekly-digest` | Latest weekly digest content |

### Analytics — `/api/v1/analytics`

| Method | Path | Query Params | Description |
|---|---|---|---|
| `GET` | `/summary` | `date` | Daily summary (calories, macros, water) |
| `GET` | `/trends/calories` | `days` (7 or 30) | Calorie trend time series |
| `GET` | `/trends/macros` | `days` | Macro distribution over time |
| `GET` | `/trends/weight` | `days` | Weight log time series |
| `GET` | `/streak` | — | Current + longest streak |
| `GET` | `/compliance` | `days` | % of days within calorie goal |

### Notifications — `/api/v1/notifications`

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | List notifications |
| `GET` | `/stream` | SSE for real-time notifications |
| `PATCH` | `/{id}/read` | Mark as read |
| `GET` | `/preferences` | Get preferences |
| `PUT` | `/preferences` | Update preferences |
| `GET` | `/reminders` | List meal reminders |
| `PUT` | `/reminders` | Update meal reminder times |

---

## 8. Inter-Service Communication

| Operation | Pattern | Why |
|---|---|---|
| User login / token validation | **Sync REST** | Gateway validates JWT inline on every request |
| Barcode food lookup | **Sync REST** | Client waits for result to fill form |
| Food search | **Sync REST** | Instant search — user expects real-time results |
| Diary entry create | **Sync REST** + async `diary.entry.created` Kafka | Client gets instant confirmation; analytics updates async |
| Food photo recognition | **Async** — POST returns `{requestId}`, SSE streams result | LLM inference takes 5–30s; don't block HTTP |
| NL food parse | **Async** — same pattern | Inference latency |
| Analytics recalculation | **Async Kafka** consumer | Eventual consistency acceptable for charts |
| Push notification delivery | **Async Kafka** | Delivery not time-critical |
| Weekly digest generation | **Async Kafka** → ai-service → notification-service | Multi-step async pipeline |
| food-service → ai-service (index embedding) | **Async Kafka** `food.indexed` | Don't block food creation on embedding |

### Async Photo Recognition Flow (SSE)

```
POST /ai/food/recognize (multipart)
  → returns: { requestId: "uuid" }

GET /notifications/stream  (SSE, already open)
  ← event: { type: "AI_RECOGNITION_COMPLETE",
              requestId: "uuid",
              results: [...] }

Frontend receives SSE event → shows results modal
```

---

## 9. Web Frontend Architecture

### Pages & Routes

| Route | Page | Description |
|---|---|---|
| `/login` | `LoginPage` | Email/pass + Google OAuth |
| `/register` | `RegisterPage` | Sign-up + language select |
| `/` | `DashboardPage` | Today's rings, diary accordion, water bar |
| `/diary/:date` | `DiaryPage` | Full diary for any date |
| `/diary/add` | `AddFoodPage` | Search, barcode, photo, NL input |
| `/foods/:id` | `FoodDetailPage` | Food nutrition card + add button |
| `/analytics` | `AnalyticsPage` | Charts: calories, macros, weight |
| `/ai` | `AiPage` | Suggestions, insights, anomalies |
| `/profile` | `ProfilePage` | Goals, TDEE calc, weight log |
| `/settings` | `SettingsPage` | Language, notifications, MFA |
| `/notifications` | `NotificationsPage` | Inbox |

### Component Tree (Key)

```
App
├── I18nProvider (i18next)
├── AuthProvider (Zustand)
├── Layout (Sidebar + Topbar + <Outlet />)
│
├── DashboardPage
│   ├── CalorieRing (Chart.js doughnut)
│   ├── MacroRings  (3× Chart.js doughnut)
│   ├── WaterProgressBar
│   ├── MealAccordion
│   │   └── DiaryEntryRow × n
│   └── QuickAddButton → AddFoodPage
│
├── AddFoodPage
│   ├── FoodSearchBar       (debounced, semantic)
│   ├── BarcodeInputWidget  (web: type EAN or upload photo)
│   ├── PhotoUploadZone     (react-dropzone → /ai/food/recognize)
│   │   └── RecognitionResultCards (editable per food)
│   ├── NlInputBox          (textarea → /ai/food/parse-text)
│   │   └── ParsedFoodPreview
│   └── FoodSearchResults   (TanStack Table)
│
├── AnalyticsPage
│   ├── CalorieTrendChart   (Chart.js line)
│   ├── MacroDistributionChart (Chart.js stacked bar)
│   ├── WeightChart         (Chart.js line + goal line)
│   └── StreakCard
│
└── ProfilePage
    ├── TdeeCalculatorForm  (React Hook Form + Zod)
    ├── GoalSettings
    └── WeightLogList
```

### State Management

| State | Tool |
|---|---|
| Auth (user, token, role, language) | Zustand (persisted to `localStorage`) |
| Server data (diary, foods, analytics) | TanStack Query v5 |
| Form state | React Hook Form + Zod |
| Real-time notifications | SSE + Zustand |
| UI (sidebar, modals, lang) | Zustand |

### i18n Web Setup

```typescript
// i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend)
  .use(initReactI18next)
  .init({
    lng: userStore.language,      // 'en' or 'ru' from Zustand
    fallbackLng: 'en',
    ns: ['common', 'food', 'diary', 'analytics', 'ai', 'auth'],
    backend: { loadPath: '/locales/{{lng}}/{{ns}}.json' },
  });

// Usage:
const { t } = useTranslation('diary');
<p>{t('breakfast')}</p>  // "Breakfast" or "Завтрак"
```

---

## 10. iOS Mobile App Architecture

### Tech Stack

| Concern | Solution |
|---|---|
| Framework | React Native + Expo SDK 52 (managed workflow) |
| Navigation | Expo Router (file-based, same mental model as Next.js) |
| Camera | `expo-camera` (food photos) |
| Barcode | `expo-barcode-scanner` (EAN-8, EAN-13, QR) |
| Push notifications | `expo-notifications` (APNs via Expo push service) |
| Offline storage | `expo-sqlite` (diary log cache) |
| State | Same Zustand + TanStack Query as web |
| Forms | React Hook Form + Zod (shared schemas with web) |
| i18n | `i18next` + `react-i18next` (shared translations) |

### Screen Map (Expo Router)

```
app/
├── (auth)/
│   ├── login.tsx
│   ├── register.tsx
│   └── mfa.tsx
├── (tabs)/
│   ├── index.tsx         ← Today's dashboard
│   ├── diary.tsx         ← Diary tab
│   ├── add.tsx           ← Add food (camera, search, NL)
│   ├── analytics.tsx     ← Charts tab
│   └── profile.tsx       ← Profile + settings
├── food/
│   └── [id].tsx          ← Food detail + add to diary
├── ai/
│   ├── recognize.tsx     ← Camera → AI photo recognition
│   └── suggestions.tsx   ← AI meal suggestions
└── _layout.tsx           ← Root layout + auth guard
```

### Key Mobile-Specific Components

```
components/
├── camera/
│   ├── FoodCamera.tsx         ← expo-camera full-screen capture
│   ├── BarcodeScanner.tsx     ← expo-barcode-scanner overlay
│   └── RecognitionOverlay.tsx ← bounding boxes on recognized foods
├── diary/
│   ├── CalorieRingNative.tsx  ← react-native-svg doughnut
│   ├── MacroBar.tsx           ← native progress bar
│   └── SwipeableEntry.tsx     ← swipe-to-delete diary entry
├── offline/
│   ├── OfflineBanner.tsx      ← shown when no network
│   └── SyncIndicator.tsx      ← shows pending sync count
└── shared/
    ├── HapticButton.tsx       ← Haptics.impactAsync on press
    └── DarkModeWrapper.tsx    ← useColorScheme hook
```

### Offline Sync Strategy

```
Offline diary logging:
  1. User logs food without internet
  2. diary entry saved to expo-sqlite local DB
     (table: pending_sync_entries with same schema as diary_entries)
  3. SyncManager runs when network reconnects:
     - POST /diary/entries for each pending entry
     - On success → delete from pending_sync_entries
     - On conflict (same date + food already exists) → last-write-wins
  4. TanStack Query refetchOnReconnect: true handles cache invalidation

Offline food search:
  - Last 200 searched + recently used foods cached in expo-sqlite
  - Shown as fallback results when offline
```

### Push Notification Setup (Expo + APNs)

```typescript
// On app launch (after auth):
const token = await Notifications.getExpoPushTokenAsync();
await api.post('/users/me/push-token', { token: token.data });

// Notification handler:
Notifications.addNotificationReceivedListener(notification => {
  // Update Zustand notification store
});
```

---

## 11. Internationalization (i18n)

### Strategy Overview

| Layer | Tool | Languages |
|---|---|---|
| Backend UI strings (emails, push titles) | Spring `MessageSource` | `messages_en.properties`, `messages_ru.properties` |
| Food database | Dual columns `name_en` + `name_ru` | Both stored; returned per `Accept-Language` header |
| AI responses | Prompt template includes `{language}` variable | LLM generates in requested language |
| Web frontend | `i18next` + `react-i18next` + HTTP backend | `en/`, `ru/` JSON files |
| iOS app | `i18next` + `react-i18next` | Same JSON files bundled in app |

### Backend i18n

```java
// User's language stored in user_profiles.language
// API Gateway propagates Accept-Language header to all downstream services

// food-service returns name based on request language:
public String getFoodName(Food food, String lang) {
    return "ru".equals(lang) && food.getNameRu() != null
        ? food.getNameRu()
        : food.getNameEn();
}

// notification-service picks correct title/body columns
// email templates: templates/email_en.html, templates/email_ru.html
```

### Spring MessageSource

```properties
# messages_en.properties
notification.meal.reminder=Time for {0}! Don't forget to log your meal.
notification.goal.exceeded=You've exceeded your daily calorie goal by {0} kcal.
notification.streak=🔥 {0}-day streak! Keep it up!

# messages_ru.properties
notification.meal.reminder=Время {0}! Не забудьте записать свой приём пищи.
notification.goal.exceeded=Вы превысили дневную норму калорий на {0} ккал.
notification.streak=🔥 {0} дней подряд! Так держать!
```

### Frontend i18n Namespace Structure

```
public/locales/
├── en/
│   ├── common.json      ← buttons, labels, errors
│   ├── food.json        ← food search, meal types
│   ├── diary.json       ← diary, water, portions
│   ├── analytics.json   ← chart labels, streaks
│   ├── ai.json          ← AI features UI text
│   └── auth.json        ← login, register, MFA
└── ru/
    ├── common.json
    ├── food.json
    ├── diary.json
    ├── analytics.json
    ├── ai.json
    └── auth.json
```

### AI Language Handling

```
// All AI prompt templates include language variable:
"Respond ONLY in {language}. {language} is either 'English' or 'Russian'."

// AI service resolves language from:
1. X-User-Language header (set by Gateway from user profile)
2. Fallback: 'en'

// Prompt files are language-agnostic templates:
// resources/prompts/food-recognition.st  ← single template, language injected
```

---

## 12. Dependencies

### Root `settings.gradle.kts`

```kotlin
rootProject.name = "calorie-tracker"

include(
    "services:api-gateway",
    "services:auth-service",
    "services:user-service",
    "services:food-service",
    "services:diary-service",
    "services:ai-service",
    "services:analytics-service",
    "services:notification-service",
    "infrastructure:eureka-server",
    "infrastructure:config-server"
)
```

### Shared `build.gradle.kts` conventions (most services)

```kotlin
plugins {
    id("org.springframework.boot") version "4.0.0"
    id("io.spring.dependency-management") version "1.1.7"
    id("java")
}

group = "com.calorietracker"
version = "0.0.1-SNAPSHOT"

java {
    toolchain { languageVersion = JavaLanguageVersion.of(26) }
}

repositories { mavenCentral() }

extra["springCloudVersion"] = "2024.0.0"
extra["springAiVersion"]    = "1.0.0"

dependencies {
    // ── Spring Boot ───────────────────────────────────────────────────────────
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-starter-data-redis")

    // ── Spring Cloud ──────────────────────────────────────────────────────────
    implementation("org.springframework.cloud:spring-cloud-starter-netflix-eureka-client")
    implementation("org.springframework.cloud:spring-cloud-starter-config")
    implementation("org.springframework.cloud:spring-cloud-starter-sleuth")   // distributed tracing
    implementation("org.springframework.cloud:spring-cloud-sleuth-zipkin")

    // ── Kafka ─────────────────────────────────────────────────────────────────
    implementation("org.springframework.kafka:spring-kafka")

    // ── Database ──────────────────────────────────────────────────────────────
    runtimeOnly("org.postgresql:postgresql")
    implementation("org.flywaydb:flyway-core")
    implementation("org.flywaydb:flyway-database-postgresql")

    // ── Mapping ───────────────────────────────────────────────────────────────
    implementation("org.mapstruct:mapstruct:1.6.3")
    annotationProcessor("org.mapstruct:mapstruct-processor:1.6.3")
    compileOnly("org.projectlombok:lombok")
    annotationProcessor("org.projectlombok:lombok")

    // ── Observability ─────────────────────────────────────────────────────────
    runtimeOnly("io.micrometer:micrometer-registry-prometheus")

    // ── Testing ───────────────────────────────────────────────────────────────
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:postgresql:1.20.4")
    testImplementation("org.testcontainers:kafka:1.20.4")
    testImplementation("org.testcontainers:junit-jupiter:1.20.4")
}

dependencyManagement {
    imports {
        mavenBom("org.springframework.cloud:spring-cloud-dependencies:${property("springCloudVersion")}")
        mavenBom("org.springframework.ai:spring-ai-bom:${property("springAiVersion")}")
    }
}
```

### Service-Specific Additions

**`auth-service/build.gradle.kts` extras:**
```kotlin
implementation("org.springframework.boot:spring-boot-starter-security")
implementation("org.springframework.boot:spring-boot-starter-oauth2-client")
implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
implementation("com.bucket4j:bucket4j-core:8.10.1")
implementation("com.password4j:password4j:1.8.2")            // Argon2id
implementation("com.warrenstrange:googleauth:1.5.0")          // TOTP
implementation("com.google.zxing:core:3.5.3")
```

**`food-service/build.gradle.kts` extras:**
```kotlin
implementation("org.springframework.ai:spring-ai-pgvector-store-spring-boot-starter")
implementation("org.springframework.ai:spring-ai-ollama-spring-boot-starter")
implementation("com.squareup.retrofit2:retrofit:2.11.0")      // Open Food Facts client
implementation("com.squareup.retrofit2:converter-gson:2.11.0")
```

**`ai-service/build.gradle.kts` extras:**
```kotlin
implementation("org.springframework.ai:spring-ai-ollama-spring-boot-starter")
implementation("org.springframework.ai:spring-ai-pgvector-store-spring-boot-starter")
implementation("net.sourceforge.tess4j:tess4j:5.11.0")        // Tesseract OCR (barcode fallback)
implementation("io.github.resilience4j:resilience4j-spring-boot3:2.2.0")
implementation("io.minio:minio:8.5.12")
```

**`api-gateway/build.gradle.kts` extras:**
```kotlin
implementation("org.springframework.cloud:spring-cloud-starter-gateway")
implementation("org.springframework.boot:spring-boot-starter-security")
implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
implementation("com.bucket4j:bucket4j-core:8.10.1")
implementation("com.bucket4j:bucket4j-redis:8.10.1")
```

**`notification-service/build.gradle.kts` extras:**
```kotlin
implementation("org.springframework.boot:spring-boot-starter-mail")
implementation("com.sendgrid:sendgrid-java:4.10.3")
implementation("org.springframework.boot:spring-boot-starter-web")  // SSE
```

---

### Web `package.json`

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0",
    "bootstrap": "^5.3.3",
    "react-bootstrap": "^2.10.0",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-table": "^8.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.0.0",
    "@hookform/resolvers": "^3.0.0",
    "axios": "^1.7.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.0.0",
    "i18next": "^23.0.0",
    "react-i18next": "^14.0.0",
    "i18next-http-backend": "^2.0.0",
    "i18next-browser-languagedetector": "^8.0.0",
    "date-fns": "^3.0.0",
    "react-datepicker": "^7.0.0",
    "react-dropzone": "^14.0.0",
    "react-hot-toast": "^2.0.0",
    "qrcode.react": "^3.0.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "vite": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "vitest": "^2.0.0",
    "@testing-library/react": "^16.0.0",
    "eslint": "^9.0.0",
    "prettier": "^3.0.0"
  }
}
```

---

### Mobile `package.json` (Expo SDK 52)

```json
{
  "dependencies": {
    "expo": "~52.0.0",
    "expo-router": "~4.0.0",
    "expo-camera": "~15.0.0",
    "expo-barcode-scanner": "~13.0.0",
    "expo-notifications": "~0.29.0",
    "expo-sqlite": "~14.0.0",
    "expo-file-system": "~17.0.0",
    "expo-haptics": "~13.0.0",
    "expo-image-manipulator": "~12.0.0",
    "react-native": "0.76.0",
    "react-native-svg": "^15.0.0",
    "react-native-reanimated": "~3.10.0",
    "react-native-gesture-handler": "~2.18.0",
    "@react-navigation/native": "^6.0.0",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.0.0",
    "@hookform/resolvers": "^3.0.0",
    "axios": "^1.7.0",
    "i18next": "^23.0.0",
    "react-i18next": "^14.0.0",
    "date-fns": "^3.0.0"
  }
}
```

---

## 13. Implementation Phases

> Each phase includes a **🔬 Technology Deep-Dive** block that explains what each tool does,
> why it was chosen, and what you will concretely learn by implementing that step.
> Treat these as mini-lessons attached to real tasks.

---

### 🏗 Phase 1 — Infrastructure Skeleton (Weeks 1–2)

**Goal:** Every service can start, discover each other, and receive routed traffic — before writing a single line of business logic.

---

#### 🔬 Technology Deep-Dive: Spring Cloud

**What is Spring Cloud?**
A collection of libraries that solve distributed-systems problems that don't exist in monoliths:
service discovery, centralised configuration, API routing, circuit breaking, and distributed tracing.
You use several Spring Cloud modules in this project:

| Module | What it does | Why you need it |
|---|---|---|
| **Eureka** (Netflix) | Acts as a phone book — every service registers itself with a name and address; other services look up that name instead of hardcoding IPs | Without this, you'd need to know the IP/port of every service at startup. With Docker, IPs change every run. |
| **Spring Cloud Config** | One central place for all `application.yml` files — stored in Git. Every service fetches its config at startup from the Config Server | Without this, you'd manage 8 separate `application.yml` files and can never change config without redeploying. With this, edit Git → restart service → new config. |
| **Spring Cloud Gateway** | A reactive API Gateway built on Spring WebFlux + Netty. Routes HTTP requests to the correct downstream service using path predicates. Also runs filters for JWT validation, rate limiting, and CORS before the request even reaches a service | Without a gateway, the React/iOS client would need to know the address of each of 8 services, handle auth per-service, and deal with CORS per-service. The Gateway is the single front door. |

**How Eureka service discovery works:**
```
1. eureka-server starts → empty registry
2. auth-service starts → registers itself as "AUTH-SERVICE" at 10.0.0.2:8081
3. api-gateway starts → fetches registry → knows AUTH-SERVICE = 10.0.0.2:8081
4. Request arrives at gateway for /api/v1/auth/** 
   → gateway looks up "AUTH-SERVICE" in local registry cache
   → forwards to 10.0.0.2:8081
5. If auth-service crashes → Eureka marks it DOWN after missed heartbeats
   → gateway stops routing to it automatically
```

**What you will learn:**
- How service meshes conceptually work (Eureka is a simpler version)
- How reactive routing works in Spring Cloud Gateway (filter chains, predicates)
- How centralised config reduces operational complexity
- The difference between client-side load balancing (Spring Cloud LoadBalancer) and server-side load balancing

---

#### 🔬 Technology Deep-Dive: Gradle Multi-Project Build

**What is a Gradle multi-project build?**
One root `settings.gradle.kts` declares all 10 subprojects. You can build everything with
`./gradlew build` or a single service with `./gradlew :services:auth-service:bootJar`.
Shared dependency versions live in a root `build.gradle.kts` convention plugin — no duplication.

**Why not separate repos?**
Polyrepo is the "real microservice" way, but for a solo learning project, a monorepo lets you:
- Make cross-service refactors atomically (one commit)
- Share DTO classes between services if you want (via a `shared-contracts` module)
- Run the entire system with one `docker-compose up` from the root

**What you will learn:**
- Gradle multi-project structure and dependency conventions
- How to write a `buildSrc` convention plugin to avoid repeating dependency blocks
- How to configure Java 26 toolchains in Gradle (different from `sourceCompatibility`)

---

#### 🔬 Technology Deep-Dive: Apache Kafka

**What is Kafka?**
A distributed, append-only log. Producers write messages to topics; consumers read from them at their own pace. Messages are persisted on disk (not lost when the consumer is down). Multiple consumer groups can read the same topic independently.

**Why not just REST calls between services?**
If diary-service calls analytics-service synchronously to update stats after every food log:
- If analytics-service is down → diary-service request fails → user gets an error
- If analytics-service is slow → diary-service hangs → cascading slowness

With Kafka:
- diary-service publishes `diary.entry.created` and immediately returns 200 to the user
- analytics-service consumes that event whenever it's ready — independently, at its own pace
- If analytics-service is down for 2 hours, it catches up when it restarts (Kafka retains messages)

**Core concepts you'll implement:**
```
Topic:     Named stream of records (e.g. "diary.entry.created")
Partition: Sub-stream within a topic for parallelism (use userId as key → same user's events always go to same partition → ordered per user)
Offset:    Position in the partition log. Each consumer group tracks its own offset.
Consumer Group: All instances of the same service share a group — Kafka distributes partitions between them (load balancing)
```

**What you will learn:**
- Producer/consumer patterns with `@KafkaListener` and `KafkaTemplate`
- Idempotent consumers (what happens if the same event is delivered twice?)
- Dead Letter Topics (DLT) — where failed messages go after max retries
- Partition key selection strategy (why `userId` is the right key for diary events)

---

#### Tasks

**Gradle & Project Structure:**
- [ ] Create root `settings.gradle.kts` including all 10 subprojects
- [ ] Create root `gradle/libs.versions.toml` (version catalog) — single source of truth for all library versions
- [ ] Create `buildSrc/src/main/kotlin/spring-service.gradle.kts` convention plugin with shared dependencies (web, jpa, eureka-client, config-client, kafka, actuator, mapstruct, lombok)
- [ ] Every service's `build.gradle.kts` applies the convention plugin + adds its own extras

**Spring Cloud Infrastructure:**
- [ ] `infrastructure/eureka-server`: apply `spring-cloud-starter-netflix-eureka-server`, `@EnableEurekaServer`, minimal `application.yml` (standalone mode, port 8761)
- [ ] `infrastructure/config-server`: apply `spring-cloud-config-server`, `@EnableConfigServer`, point to a local Git repo or `classpath:/config` folder for dev, port 8888
- [ ] Create `config/` folder at repo root with `application.yml` (shared), `auth-service.yml`, `food-service.yml`, etc. — Config Server serves these
- [ ] `services/api-gateway`: apply `spring-cloud-starter-gateway`, configure route predicates in `application.yml`:
  ```yaml
  spring.cloud.gateway.routes:
    - id: auth-service
      uri: lb://AUTH-SERVICE       # lb:// = load-balanced via Eureka
      predicates: [Path=/api/v1/auth/**]
    - id: food-service
      uri: lb://FOOD-SERVICE
      predicates: [Path=/api/v1/foods/**]
  ```
- [ ] Every service: add `spring-cloud-starter-netflix-eureka-client` + `spring-cloud-starter-config` + `bootstrap.yml` with service name and config server URL

**Docker & Local Infrastructure:**
- [ ] Write `docker/docker-compose.yml` with: `pgvector/pgvector:pg17`, Redis, Zookeeper, Kafka (`confluentinc/cp-kafka:7.7.0`), MinIO, Ollama
- [ ] Write `docker/postgres/init.sql` that creates all 6 databases: `CREATE DATABASE auth_db; CREATE DATABASE user_db;` etc.
- [ ] First Flyway migration `V1__extensions.sql` in every service: `CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS pgcrypto;`
- [ ] Confirm `pgvector` extension installs cleanly (run `SELECT * FROM pg_extension;`)

**Health & Verification:**
- [ ] Add `spring-boot-starter-actuator` to all services, expose `/actuator/health` and `/actuator/info`
- [ ] Start Eureka dashboard at `http://localhost:8761` → verify all services appear as `UP`
- [ ] Curl `http://localhost:8080/api/v1/auth/health` through the gateway → verify routing works
- [ ] ✅ **Milestone:** `docker-compose up` → all 10 services green in Eureka

---

### 🏗 Phase 2 — Auth Service + User Service (Weeks 3–4)

**Goal:** Register, login, MFA, and user profiles working end-to-end across two services communicating via Kafka.

---

#### 🔬 Technology Deep-Dive: JWT + Spring Security 7

**What is JWT (JSON Web Token)?**
A compact, self-contained token with three Base64url-encoded parts: `header.payload.signature`.
The payload carries claims: `sub` (userId), `role`, `exp` (expiry), `iat` (issued at).
The signature is computed with a secret key — the server verifies it without a database lookup.

```
Access token:  short-lived (15 min) — sent in Authorization header
Refresh token: long-lived (7 days) — stored in HttpOnly cookie (invisible to JS)

Flow:
  Login → server issues both tokens
  Every API request → client sends access token in header
  Access token expires → client sends refresh token cookie to /auth/refresh
  Server validates refresh token against DB → issues new access token
  Logout → server marks refresh token as revoked in DB
```

**Why `HttpOnly` cookies for the refresh token?**
An `HttpOnly` cookie cannot be read by JavaScript — so even if your React app has an XSS vulnerability, an attacker cannot steal the refresh token. The access token lives only in memory (Zustand store, never `localStorage`).

**What is Spring Security's filter chain?**
Spring Security is a chain of `Filter` implementations. Each filter runs before your controller:
```
Request → JwtAuthFilter (parse + validate token, set SecurityContext)
        → RateLimitFilter (Bucket4j check)
        → AuthorizationFilter (@PreAuthorize checks)
        → Your controller
```

**What you will learn:**
- How JWT is structured and validated without DB calls
- How Spring Security's `SecurityFilterChain` DSL works in Spring Boot 4
- The difference between stateless (JWT) and stateful (session) authentication
- How `@PreAuthorize("hasRole('ADMIN')")` method security works under the hood

---

#### 🔬 Technology Deep-Dive: Argon2id Password Hashing

**Why not BCrypt?**
BCrypt is CPU-bound only. Modern GPUs can brute-force BCrypt at millions of hashes/second.
**Argon2id** is memory-hard — it requires large amounts of RAM per attempt, making GPU attacks impractical. It's the winner of the Password Hashing Competition (2015) and is OWASP's recommended algorithm for new applications.

**Parameters you'll configure:**
```java
// Higher = slower = more secure, but also slower for your users
// Target: ~300–500ms on your server hardware
Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8()
// memory=16384 KB (16 MB), iterations=3, parallelism=1
```

**What you will learn:**
- Why memory-hard functions defeat GPU attacks
- How Spring Security's `PasswordEncoder` abstraction lets you swap algorithms
- How to benchmark hash time on your hardware and tune parameters

---

#### 🔬 Technology Deep-Dive: TOTP Multi-Factor Authentication

**How TOTP works (RFC 6238):**
```
1. Server generates a random 20-byte secret (base32-encoded)
2. Server shows a QR code encoding: otpauth://totp/App:email?secret=XXX&issuer=App
3. User scans with Google Authenticator → app stores the secret
4. Every 30 seconds: TOTP code = HMAC-SHA1(secret, floor(unixTime / 30))
   → 6-digit code displayed
5. User types code → server computes the same HMAC → if they match → authenticated
6. Server allows ±1 time step (±30 seconds) for clock skew
```

No network call, no SMS, no third-party — completely offline. The `googleauth` library handles steps 1 and 5.

**What you will learn:**
- How time-based one-time passwords work cryptographically
- Why HMAC-SHA1 is used and how the time window prevents replay attacks
- How to generate and validate QR code URIs in Java

---

#### 🔬 Technology Deep-Dive: Kafka as Cross-Service Event Bus

**The `user.registered` event — your first real Kafka flow:**
```
auth-service (Producer):
  @KafkaProducer
  After successful registration:
    kafkaTemplate.send("user.registered", userId, new UserRegisteredEvent(userId, email, language))

user-service (Consumer):
  @KafkaListener(topics = "user.registered", groupId = "user-service")
  public void onUserRegistered(UserRegisteredEvent event) {
      // Create empty profile row for this userId
      profileRepository.save(new UserProfile(event.userId(), event.language()));
  }

notification-service (Consumer — same topic, different group!):
  @KafkaListener(topics = "user.registered", groupId = "notification-service")
  public void onUserRegistered(UserRegisteredEvent event) {
      emailService.sendWelcomeEmail(event.email(), event.language());
  }
```

Two services consume the same event independently. auth-service doesn't know or care about either of them.

**What you will learn:**
- `@KafkaListener` annotation and consumer group semantics
- `KafkaTemplate<String, Object>` for type-safe publishing
- How to configure a Dead Letter Topic (DLT) so failed events don't disappear silently
- Idempotency: what if `user.registered` is delivered twice? → check `profileRepository.existsById(userId)` before saving

---

#### Tasks

**auth-service — Backend:**
- [ ] Flyway `V1__schema.sql`: `users`, `refresh_tokens`, `audit_logs` tables
- [ ] `JwtService.java`: generate signed access token (HMAC-SHA256, 15 min), refresh token (UUID, hashed before storing), parse + validate
- [ ] `AuthService.java`: `register()` — validate email uniqueness, hash password with Argon2id, save user, publish `user.registered` Kafka event; `login()` — verify hash, issue tokens; `refresh()` — validate token hash in DB, rotate; `logout()` — mark revoked
- [ ] `JwtAuthFilter.java`: extends `OncePerRequestFilter`, parses `Authorization: Bearer` header, validates signature + expiry, sets `SecurityContextHolder`
- [ ] `SecurityConfig.java`: `SecurityFilterChain` bean — permit `/api/v1/auth/**`, require auth for everything else; disable session (`STATELESS`); configure OAuth2 resource server with JWT decoder
- [ ] `MfaService.java`: generate TOTP secret (`GoogleAuthenticator.createCredentials()`), build QR URI, verify code with ±1 window, generate 10 one-time backup codes (BCrypt-hashed)
- [ ] `OAuth2SuccessHandler.java`: after Google login → look up or create user → issue JWT → redirect to frontend with token
- [ ] API Gateway `JwtGlobalFilter.java`: validates JWT on every request before routing; rejects 401 without hitting downstream services; extracts `userId` + `language` → adds `X-User-Id` and `X-User-Language` headers to downstream request
- [ ] Rate limiting at Gateway: `LoginRateLimitFilter` using Bucket4j + Redis — 5 requests/minute per IP on `/auth/login`

**user-service — Backend:**
- [ ] Flyway `V1__schema.sql`: `user_profiles`, `weight_logs`, `disliked_foods` tables
- [ ] Kafka consumer for `user.registered` → `profileRepository.save(new UserProfile(event.userId()))` (idempotent: check exists first)
- [ ] `TdeeCalculatorService.java`: Mifflin-St Jeor formula:
  ```
  Men:   BMR = 10×weight + 6.25×height − 5×age + 5
  Women: BMR = 10×weight + 6.25×height − 5×age − 161
  Activity multipliers: SEDENTARY×1.2, LIGHT×1.375, MODERATE×1.55, ACTIVE×1.725, VERY_ACTIVE×1.9
  ```
  Returns `{ tdee, suggestedGoal, macroSplit }` as a Java record
- [ ] `UserProfileService.java`: get/update profile, enforce owner-only access via `@PreAuthorize("#userId == authentication.principal.userId")`
- [ ] `WeightLogService.java`: create/list/delete weight entries; paginated list sorted by `logged_at DESC`

**Web Frontend:**
- [ ] Init Vite 6 + React 19 + TypeScript: `npm create vite@latest web -- --template react-ts`
- [ ] Install Bootstrap 5: `npm install bootstrap` → import in `main.tsx`
- [ ] Configure React Router v7 with `createBrowserRouter`, `AppLayout` (with sidebar), `AuthLayout` (centered card)
- [ ] **i18next setup** — *Technology note: i18next is the most widely used JS i18n library. `react-i18next` provides hooks (`useTranslation`) and components (`<Trans>`). The HTTP backend loads JSON translation files lazily from `/public/locales/en/` and `/public/locales/ru/` so translation files are never bundled into the JS bundle.*
  - [ ] `npm install i18next react-i18next i18next-http-backend i18next-browser-languagedetector`
  - [ ] `i18n/index.ts`: configure with HTTP backend, detect from `localStorage` → browser locale → `'en'` fallback
  - [ ] Create `public/locales/en/common.json` and `public/locales/ru/common.json` with base keys
  - [ ] `LanguageSwitcher.tsx` component: toggle between `en` and `ru`, persists to `localStorage`, calls `i18n.changeLanguage()`
- [ ] `authStore.ts` (Zustand): `{ user, accessToken, setAuth, clearAuth }` — persisted to `sessionStorage` (cleared on tab close)
- [ ] Axios `client.ts`: base URL from `VITE_API_BASE_URL`, request interceptor adds `Authorization: Bearer ${token}`, response interceptor catches 401 → calls `/auth/refresh` → retries original request → on second 401 redirects to `/login`
- [ ] `LoginPage.tsx`, `RegisterPage.tsx` with React Hook Form + Zod schemas, all labels via `useTranslation()`
- [ ] `MfaPage.tsx`: 6-digit code input + QR code display using `qrcode.react`
- [ ] `ProfilePage.tsx`: TDEE calculator form (React Hook Form), result card showing TDEE + suggested calorie goal

**iOS — React Native:**
- [ ] Init Expo project: `npx create-expo-app mobile --template blank-typescript`
- [ ] Configure Expo Router: `app/(auth)/login.tsx`, `app/(auth)/register.tsx`
- [ ] Install `i18next` + `react-i18next` — use same translation JSON files as web (copy to `mobile/i18n/locales/`)
- [ ] Language auto-detect: `expo-localization` → `Localization.locale` → set i18next language on app startup
- [ ] Zustand stores + Axios client (identical logic to web, React Native compatible)
- [ ] ✅ **Milestone:** Register → receive welcome email → login → see profile with TDEE result → switch language → all text changes

---

### 🏗 Phase 3 — Food Service + External APIs + pgvector (Weeks 5–7)

**Goal:** Users can search for foods semantically, scan barcodes, and add custom foods. Nutritional data flows in from two external APIs and is indexed as vector embeddings.

---

#### 🔬 Technology Deep-Dive: pgvector — Vector Similarity Search

**What is a vector embedding?**
When you feed text into an embedding model (like `nomic-embed-text`), it outputs a list of ~768 floating-point numbers — a **vector**. This vector is a point in 768-dimensional space. Similar texts produce vectors that are close together (small cosine distance).

```
"oatmeal"       → [0.12, -0.34, 0.87, ...]   ← 768 numbers
"овсянка"       → [0.13, -0.33, 0.85, ...]   ← very close! (same concept, different language)
"chicken breast"→ [0.55,  0.21, -0.12, ...]  ← far away
```

**What is pgvector?**
A PostgreSQL extension that adds a `vector(N)` column type and three distance operators:
- `<=>` cosine distance (best for text embeddings)
- `<->` L2 (Euclidean) distance
- `<#>` inner product

And a `USING hnsw` index for fast approximate nearest-neighbour (ANN) search — without it, every search would do a full table scan comparing your query vector against every row.

**HNSW (Hierarchical Navigable Small World) index:**
A graph-based index that builds a multi-layer graph of vectors at creation time.
At query time, it navigates the graph to find approximate nearest neighbours in `O(log n)` time instead of `O(n)`.
Parameters: `m` = number of connections per node (16 is a good default); `ef_construction` = search depth during build (64 = balanced speed/recall).

**What you will learn:**
- How vector embeddings encode semantic meaning
- Why cosine similarity works for text (magnitude doesn't matter, only direction)
- How to write a pgvector query in native JPA: `@Query(nativeQuery=true, value="SELECT ... ORDER BY embedding <=> CAST(:queryVector AS vector)")`
- The trade-off between HNSW recall (accuracy) and build time/memory

---

#### 🔬 Technology Deep-Dive: Retrofit — Type-Safe HTTP Clients

**What is Retrofit?**
An annotation-based HTTP client for Java/Kotlin (by Square). You define an interface, annotate methods with `@GET`, `@POST`, `@Path`, `@Query` — Retrofit generates the implementation at runtime.

```java
public interface OpenFoodFactsApi {
    @GET("product/{barcode}.json")
    Call<ProductResponse> getByBarcode(@Path("barcode") String barcode);
}
// Usage:
OpenFoodFactsApi api = new Retrofit.Builder()
    .baseUrl("https://world.openfoodfacts.org/api/v0/")
    .addConverterFactory(GsonConverterFactory.create())
    .build()
    .create(OpenFoodFactsApi.class);
```

**Why Retrofit over Spring's `RestClient`?**
For external APIs with complex response schemas and multiple endpoints, Retrofit's interface-based approach is cleaner and easier to mock in tests. `RestClient` (Spring's new fluent HTTP client) is better for internal service-to-service calls.

**What you will learn:**
- Retrofit interface definition + Gson/Jackson converter setup
- How to handle API errors gracefully (check `response.isSuccessful()`, parse error body)
- How to mock Retrofit clients in tests using `WireMock` or `MockWebServer`
- The barcode lookup chain: Open Food Facts → USDA → local DB cache → fallback to "unknown product"

---

#### 🔬 Technology Deep-Dive: Flyway — Database Migrations

**What is Flyway?**
A database migration tool. You write plain SQL files named `V{version}__{description}.sql` and Flyway runs them in order, tracking which ones have already been applied in a `flyway_schema_history` table.

**Why this matters in microservices:**
Each service owns its own database schema. Each service's `build.gradle.kts` includes `flyway-core` and has a separate `db/migration/` folder. When the service starts, it automatically runs any pending migrations. No manual `ALTER TABLE` ever.

```
food-service/src/main/resources/db/migration/
  V1__extensions.sql           ← CREATE EXTENSION IF NOT EXISTS vector
  V2__foods_schema.sql         ← CREATE TABLE foods (...)
  V3__food_embeddings.sql      ← CREATE TABLE food_embeddings (...) + HNSW index
  V4__barcode_cache.sql        ← CREATE TABLE barcode_cache (...)
  V5__seed_common_foods.sql    ← INSERT 500 common foods (EN + RU names)
```

**What you will learn:**
- How to write idempotent migrations (always use `IF NOT EXISTS`)
- How to handle the `flyway_schema_history` table and what happens if a migration fails halfway
- How to separate schema migrations from data migrations (keep them in different files)

---

#### Tasks

**food-service — Backend:**
- [ ] Flyway `V2__foods_schema.sql` → `V5__seed_data.sql` as described above
- [ ] `FoodRepository.java`: Spring Data JPA + custom JPQL for name search (`ILIKE`), user-scoped queries
- [ ] `VectorFoodSearchRepository.java`: `@Repository` with `@PersistenceContext EntityManager` — use `entityManager.createNativeQuery()` for pgvector `<=>` queries; returns `List<FoodSearchResultDto>` (projection)
- [ ] `FoodEmbeddingService.java`: injected `EmbeddingModel` (Spring AI Ollama) — `embed(String text)` returns `float[]`; `indexFood(Food food)` builds content string `"${nameEn} ${nameRu} ${brand} ${category}"` → embed → save to `food_embeddings`
- [ ] `FoodEmbeddingIndexer.java`: `@KafkaListener(topics = "food.indexed")` → call `foodEmbeddingService.indexFood(food)` — this is the async decoupling pattern: food creation is instant, embedding happens in background
- [ ] `CombinedFoodSearchService.java`: merge semantic results + PostgreSQL `ts_vector` keyword results using **Reciprocal Rank Fusion**:
  ```java
  // RRF score = Σ 1/(k + rank_i) for each result list
  // k = 60 (standard constant)
  // Merge maps: semanticRanks + keywordRanks → sort by combined RRF score
  ```
- [ ] `BarcodeService.java`: lookup chain with caching:
  1. Check `barcode_cache` (< 30 days old) → return cached food_id
  2. Call `OpenFoodFactsClient.getByBarcode(ean)` → map response fields to `Food` entity → save → cache
  3. If OFF returns no result → call `UsdaFoodClient.searchByBarcode(ean)` → map → save → cache
  4. If both fail → return `Optional.empty()` (frontend shows "manual entry" form)
- [ ] `OpenFoodFactsClient.java` (Retrofit interface) + `UsdaFoodClient.java` (Retrofit interface)
- [ ] Configure Retrofit beans in `FoodServiceConfig.java` with Gson converter + OkHttp interceptor for USDA `api_key` query param
- [ ] `FoodController.java`: all REST endpoints; note `GET /search` returns name in correct language based on `X-User-Language` header from Gateway

**Web + iOS:**
- [ ] `FoodSearchBar.tsx` / RN equivalent: debounced input (300ms, `setTimeout` in `useEffect`), calls `GET /foods/search?q={query}&lang={locale}`, displays `FoodSearchResult` cards showing name + calories/100g
- [ ] `FoodDetailPage.tsx` / screen: full macro table (calories, protein, carbs, fat, fiber, sugar, sodium), serving size selector dropdown, `AddToDiaryButton` → opens portion modal
- [ ] `BarcodeInputWidget.tsx` (web): simple text input for manual EAN entry + camera photo upload button (calls barcode lookup from image); iOS: `BarcodeScanner.tsx` using `expo-barcode-scanner` with camera overlay
- [ ] `FavouritesTab.tsx` + `RecentFoodsTab.tsx` using TanStack Query with appropriate stale times (favourites: 5 min; recent: 1 min)
- [ ] ✅ **Milestone:** Search "chicken breast" → get results in EN or RU → scan a real product barcode → nutritional data auto-fills

---

### 🏗 Phase 4 — Diary Service + Kafka Bus in Full Motion (Weeks 8–9)

**Goal:** The core logging loop works: user logs food → diary saves it → Kafka fires event → analytics and notifications react. Water tracking, saved meals, and the dashboard ring charts are live.

---

#### 🔬 Technology Deep-Dive: Database-per-Service Pattern

**Why each microservice has its own database:**
The core rule of microservices: **no service shares a database with another service**. Each service is the single source of truth for its own data. Other services must ask via API or listen to events — never by directly querying another service's table.

**Consequences you'll encounter during implementation:**
- `diary_entries` stores `food_id` (UUID) but there is no foreign key to `foods` in food_db — they are in different databases! Instead, diary-service calls food-service REST API to validate `food_id` on entry creation, then **snapshots** the nutritional values into the diary row. This means the diary entry is immutable after creation even if the food's nutritional data changes.
- `analytics_db` has its own `daily_summaries` table recomputed from Kafka events — it is a read-optimised projection, not the source of truth. If analytics-service is restarted from scratch, it could replay all `diary.entry.created` events from Kafka (from offset 0) to rebuild its state. This is the **event sourcing** pattern.

**What you will learn:**
- Why data duplication (snapshotting nutrition in diary) is intentional and correct in microservices
- The difference between source of truth and read models (CQRS pattern — Command Query Responsibility Segregation)
- How to implement eventual consistency: diary-service is strongly consistent; analytics-service is eventually consistent (a few seconds behind)

---

#### 🔬 Technology Deep-Dive: Server-Sent Events (SSE) for Real-Time Updates

**What is SSE?**
A one-way, long-lived HTTP connection where the **server** pushes events to the client. Unlike WebSockets (bidirectional), SSE is simpler — just a `Content-Type: text/event-stream` response that never closes.

**Why SSE instead of WebSocket here?**
- Notifications and AI results are server → client only. No need for bidirectional.
- SSE works over standard HTTP/2 — no special proxy configuration.
- Spring Boot supports SSE natively via `SseEmitter`.

```java
// notification-service:
private final Map<UUID, SseEmitter> emitters = new ConcurrentHashMap<>();

@GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter stream(@AuthenticationPrincipal UserDetails user) {
    SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
    emitters.put(user.getId(), emitter);
    emitter.onCompletion(() -> emitters.remove(user.getId()));
    return emitter;
}

// When Kafka event arrives:
public void pushToUser(UUID userId, Notification n) {
    SseEmitter emitter = emitters.get(userId);
    if (emitter != null) {
        emitter.send(SseEmitter.event().data(n));
    }
}
```

**What you will learn:**
- How long-polling, SSE, and WebSocket differ and when to use each
- How `SseEmitter` handles connection timeouts and reconnections
- How the frontend's `EventSource` API works in React (`useEffect` → `new EventSource(url)` → `es.onmessage`)
- Why SSE connections need to be stored per-user in a `ConcurrentHashMap` (thread safety in multi-threaded server)

---

#### 🔬 Technology Deep-Dive: TanStack Query — Server State Management

**What problem does it solve?**
Every time you fetch data from an API in React, you need: loading state, error state, caching, re-fetching on focus, invalidating stale data after mutations, and optimistic updates. Writing this with `useState` + `useEffect` leads to hundreds of lines of boilerplate.

**TanStack Query provides:**
```typescript
// Fetching diary entries:
const { data, isLoading, error } = useQuery({
  queryKey: ['diary', selectedDate],           // cache key
  queryFn: () => diaryApi.getEntries(selectedDate),
  staleTime: 30_000,                           // treat as fresh for 30s
});

// After logging a food entry:
const mutation = useMutation({
  mutationFn: (entry) => diaryApi.createEntry(entry),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['diary', selectedDate] });
    // ↑ tells TanStack Query: diary data for today is stale → refetch it
    // The CalorieRing updates automatically!
  },
});
```

**What you will learn:**
- The `queryKey` array as a cache key — why it should include all variables that affect the query
- `invalidateQueries` vs `setQueryData` (optimistic update) — when to use each
- `staleTime` vs `gcTime` (garbage collection time) — understanding the cache lifecycle
- How `useInfiniteQuery` works for paginated food search results

---

#### Tasks

**diary-service — Backend:**
- [ ] Flyway `V1__schema.sql`: all diary tables
- [ ] `DiaryEntryService.java`:
  - `create()`: call food-service REST (`GET /foods/{foodId}`) to validate + fetch nutrition → compute `calories = (quantity_g / 100) * calories_per_100g` → save snapshot → publish `diary.entry.created`
  - `getDayView()`: return all entries for a date + computed totals `{ totalCalories, totalProteinG, totalCarbsG, totalFatG, waterMl }`
  - `delete()`: hard delete + publish `diary.entry.deleted`
  - `bulkCreate()`: accepts `List<DiaryEntryRequest>` — wraps all in `@Transactional` — used by AI photo recognition result confirmation
- [ ] food-service REST call: use Spring's `RestClient` (new in Spring Boot 3.2+) with Eureka load-balanced `http://FOOD-SERVICE/foods/{foodId}` — this is the pattern for synchronous inter-service calls
- [ ] `CopyDayService.java`: fetch all entries for `fromDate` → map to new entries for `toDate` with current timestamp → bulk save → publish events for each
- [ ] `SavedMealService.java`: save a list of `(food_id, quantity_g)` pairs with a name; `logSavedMeal()` → `diaryEntryService.bulkCreate()` for the meal's items
- [ ] Publish `diary.entry.created` with full payload (userId, foodId, date, mealType, all macros, source)

**analytics-service — Backend:**
- [ ] Flyway `V1__schema.sql`: `daily_summaries`, `streaks`
- [ ] `DiarySummaryConsumer.java`: `@KafkaListener(topics = "diary.entry.created")` → upsert `daily_summaries` row: `INSERT ... ON CONFLICT (user_id, date) DO UPDATE SET total_calories = total_calories + EXCLUDED.calories, ...`; handle `diary.entry.deleted` (subtract)
- [ ] `StreakService.java`: after every `daily_summaries` update → check if `date = lastLoggedDate + 1` → increment `current_streak`; if gap → reset to 1; update `longest_streak` if beaten
- [ ] All analytics REST endpoints: trends returns `List<{date, calories, goal}>` sorted by date

**Web + iOS:**
- [ ] `DashboardPage.tsx` / screen:
  - `CalorieRing`: Chart.js doughnut, consumed vs. goal, colour changes (green/orange/red) based on % consumed
  - `MacroProgressBars`: three Bootstrap progress bars for protein, carbs, fat showing grams consumed vs. goal
  - `WaterProgressBar`: Bootstrap progress bar, quick-add buttons (+200ml, +330ml, +500ml)
  - `MealAccordion`: Bootstrap accordion, one panel per meal type, `DiaryEntryRow` per food with swipe-to-delete on mobile
- [ ] `AnalyticsPage.tsx`: 7-day calorie trend (Chart.js Line), macro doughnut (Chart.js Doughnut), weight chart (Chart.js Line with goal line annotation), `StreakCard` component
- [ ] iOS offline SQLite queue: `useDiarySync.ts` hook — on `createEntry()` → try API → if network error → save to `expo-sqlite` pending table → `AppState.addEventListener('change')` + `NetInfo.fetch()` → when online: flush pending queue
- [ ] ✅ **Milestone:** Log breakfast + lunch → CalorieRing updates instantly → check analytics → streak = 1

---

### 🏗 Phase 5 — AI Service (Weeks 10–13)

**Goal:** All AI features live. This is the most technically complex phase — split into four focused sub-phases so you learn one AI concept at a time.

---

#### 🔬 Technology Deep-Dive: Spring AI Framework

**What is Spring AI?**
Spring's official AI abstraction layer (GA as of 2024). It provides framework-level abstractions over different LLM providers so you can swap Ollama for OpenAI (or any other provider) by changing one config line.

**Key abstractions:**
| Interface | What it does | Concrete implementation (this project) |
|---|---|---|
| `ChatClient` | Sends a prompt, receives a text response | `OllamaChatClient` pointing to `llama3.1:8b` |
| `EmbeddingModel` | Converts text to a float[] vector | `OllamaEmbeddingModel` using `nomic-embed-text` |
| `VectorStore` | Stores and searches vector embeddings | `PgVectorStore` (PostgreSQL + pgvector) |
| `ChatClient` (vision) | Sends image + text prompt | `OllamaChatClient` pointing to `llava:7b` |

**ChatClient fluent API:**
```java
String response = ChatClient.create(chatModel)
    .prompt()
    .system("You are a nutrition expert.")
    .user(u -> u.text("What is in this image?").media(MimeTypeUtils.IMAGE_JPEG, imageResource))
    .call()
    .content();
```

**Structured output (key concept):**
LLMs return text. To get structured data, use `BeanOutputConverter<T>`:
```java
var converter = new BeanOutputConverter<>(new ParameterizedTypeReference<List<RecognizedFood>>() {});
String formatInstructions = converter.getFormat();  // "Respond with JSON: [{name: string, ...}]"
String rawJson = chatClient.prompt().user(prompt + formatInstructions).call().content();
List<RecognizedFood> foods = converter.convert(rawJson);  // deserialize
```

**What you will learn:**
- How to configure Spring AI's `@Bean` definitions for multiple Ollama models
- The difference between `ChatClient` (stateless, single-turn) and `ChatMemory` (multi-turn conversation)
- How `BeanOutputConverter` uses Jackson + JSON Schema to constrain LLM output format
- Why LLM output is non-deterministic and how to make your parsing resilient to small variations

---

#### 🔬 Technology Deep-Dive: Ollama — Local LLM Runner

**What is Ollama?**
A tool that lets you run open-weight LLMs locally. It downloads models (quantized GGUF files), serves an OpenAI-compatible HTTP API at `http://localhost:11434`, and handles GPU/CPU inference automatically.

**Three models you use and why each one:**

| Model | Size | What it does | Why this model |
|---|---|---|---|
| `llama3.1:8b` | ~4.7 GB | Text generation — NL parsing, summaries, meal suggestions | Best balance of quality vs. speed at 8B params; runs on 8 GB RAM |
| `nomic-embed-text` | ~274 MB | Converts text → float[768] embedding vector | Specifically fine-tuned for text similarity; handles Russian well |
| `llava:7b` | ~4.1 GB | Multimodal — understands images + text | Only widely available free multimodal model; sufficient for food recognition |

**Model quantization:**
Models are stored as quantized GGUF files (e.g., Q4_K_M = 4-bit quantisation with K-means). 4-bit means each weight uses 4 bits instead of 16–32 bits → 4–8× smaller → fits in RAM → acceptable quality loss (~3–5% accuracy drop vs. full precision).

**What you will learn:**
- How to interact with Ollama's REST API directly (useful for debugging)
- Why model quantisation exists and how it affects output quality
- How to pull and manage models: `ollama pull llama3.1:8b`, `ollama list`, `ollama run llama3.1:8b "test prompt"`
- The impact of `temperature` (randomness) and `top_p` (nucleus sampling) on output

---

#### 🔬 Technology Deep-Dive: RAG — Retrieval-Augmented Generation

**The core problem RAG solves:**
LLMs have knowledge cutoffs and hallucinate facts. If you ask `llama3.1:8b` "what are the macros of Chobani Greek Yogurt 0% Fat?", it might invent numbers. But if you **first retrieve** the real data from your food database and inject it into the prompt, the LLM summarises known facts instead of inventing them.

**RAG pipeline (generalised):**
```
1. EMBED the user's query → query vector
2. RETRIEVE the K most similar items from your knowledge base (pgvector search)
3. AUGMENT the prompt with retrieved context
4. GENERATE response using LLM with the context
```

**Applied to NL food logging:**
```
User: "I had a bowl of oatmeal with milk and a banana"

Step 1: Embed "I had a bowl of oatmeal with milk and a banana" → float[768]
Step 2: pgvector search → top 15 similar foods:
         [oatmeal (id:123, 389kcal/100g), rolled oats (id:124, 379kcal/100g),
          whole milk (id:456, 61kcal/100g), banana (id:789, 89kcal/100g), ...]
Step 3: Prompt = "Parse food items from: 'I had a bowl of oatmeal...'
                  Available foods in database: [{id:123,name:'oatmeal',...},...]
                  Return JSON: [{foodId, quantityG, mealType}]"
Step 4: LLM returns: [{foodId:123, quantityG:80}, {foodId:456, quantityG:200}, {foodId:789, quantityG:120}]
```

The LLM anchors its response to real database IDs — no hallucinated nutritional values.

**What you will learn:**
- The full RAG implementation lifecycle: indexing phase vs. query phase
- Why the retrieval step (pgvector) is more important than the generation step for factual accuracy
- How to write prompt templates that constrain output to a strict JSON schema
- How to handle the case where the retrieved context doesn't contain the right food (graceful degradation to LLM-estimated values)

---

#### 🔬 Technology Deep-Dive: Resilience4j — Fault Tolerance for AI Calls

**Why you need fault tolerance specifically for Ollama:**
LLMs are slow and occasionally fail. `llava:7b` processing a high-resolution image can take 20–45 seconds. If Ollama is overloaded or the model is still loading, it may return 503.

**Three Resilience4j patterns you'll implement:**

```
TimeLimiter:   Sets a max wait time per call.
               llava calls: 45s max. If exceeded → TimeoutException → fallback.

Retry:         Retries failed calls with exponential backoff.
               llama3.1 calls: retry 3× with 2s, 4s, 8s backoff.
               Don't retry on timeout (user already got SSE "failed" event).

CircuitBreaker: Tracks failure rate over a sliding window.
               If >50% of last 10 calls failed → OPEN circuit → instantly return fallback
               without hitting Ollama (it's clearly down).
               After 30s wait → HALF-OPEN → try one call → if OK → CLOSED again.
```

```java
@CircuitBreaker(name = "ollama", fallbackMethod = "recognitionFallback")
@TimeLimiter(name = "ollamaVision")
@Retry(name = "ollamaRetry")
public CompletableFuture<List<RecognizedFoodDto>> recognizeFood(byte[] imageBytes) {
    // ... Spring AI multimodal call
}

public CompletableFuture<List<RecognizedFoodDto>> recognitionFallback(byte[] img, Throwable t) {
    log.warn("Ollama unavailable for photo recognition: {}", t.getMessage());
    return CompletableFuture.completedFuture(Collections.emptyList());
    // Frontend shows "AI unavailable, please add manually"
}
```

**What you will learn:**
- How to configure Resilience4j in `application.yml` (no code annotations needed for config)
- The difference between circuit breaker state machine states: CLOSED → OPEN → HALF-OPEN
- How `CompletableFuture` enables non-blocking async operations in Java
- Why fallback methods must have the same signature + an extra `Throwable` parameter

---

#### Phase 5a — Ollama Setup + Food Photo Recognition (Week 10)

**Backend:**
- [ ] Add Ollama to `docker-compose.yml` with health check; write `docker/ollama/init-models.sh`:
  ```bash
  #!/bin/sh
  ollama pull llama3.1:8b
  ollama pull nomic-embed-text
  ollama pull llava:7b
  ```
- [ ] `AiConfig.java`: configure three Spring AI beans:
  - `ChatClient` bean named `textChatClient` → Ollama `llama3.1:8b`, temperature=0.3 (low = more deterministic output)
  - `ChatClient` bean named `visionChatClient` → Ollama `llava:7b`, temperature=0.1
  - `EmbeddingModel` bean → Ollama `nomic-embed-text`
- [ ] `ImagePreprocessor.java`: use `javax.imageio.ImageIO` + `java.awt.Graphics2D` to resize images exceeding 1024×1024 (maintains aspect ratio); convert to JPEG byte array; compute aspect ratio to warn user if image is too small
- [ ] `FoodPhotoRecognizer.java`:
  - Accept `byte[] imageBytes` + `String language`
  - Build multimodal Spring AI message with image + prompt loaded from `resources/prompts/food-recognition.st`
  - Use `BeanOutputConverter<List<RecognizedFoodItem>>` for structured output
  - For each recognized item: call food-service REST to find closest matching food via name search
  - Return `List<RecognitionResultDto>` with `{ foodId?, name, quantityG, nutrition, confidence, source }`
- [ ] `AiController.java`: `POST /ai/food/recognize` — multipart image upload → store photo in MinIO → call `FoodPhotoRecognizer` inside `CompletableFuture.supplyAsync()` → return `{ requestId }` immediately → on completion publish `ai.food.recognized` Kafka event
- [ ] Resilience4j config in `application.yml` for `ollama` circuit breaker + `ollamaVision` time limiter (45s)

**Web + iOS:**
- [ ] `PhotoUploadZone.tsx` (react-dropzone): drag-and-drop or click-to-select image → preview → POST to `/ai/food/recognize` → show `requestId` + loading spinner
- [ ] SSE listener in `useNotifications.ts`: when `{ type: 'AI_RECOGNITION_COMPLETE', requestId }` event received → show `RecognitionResultCards` modal
- [ ] `RecognitionResultCard.tsx`: one card per recognized food, editable `quantityG` input, confidence bar, food name (from DB match or AI estimate with different styling), confirm/remove toggle
- [ ] iOS `FoodCamera.tsx`: `expo-camera` full screen, capture button, submit to same endpoint

---

#### Phase 5b — NL Food Parsing + RAG Pipeline (Week 11)

**Backend:**
- [ ] `PromptTemplateEngine.java`: reads `.st` (StringTemplate) files from `resources/prompts/` using `ClassPathResource`; substitutes variables with a simple `String.replace("{key}", value)` or use the `ST` library for proper templating
- [ ] Create prompt files:
  - `resources/prompts/nl-food-parse.st` — NL parsing with RAG context injection
  - `resources/prompts/food-recognition.st` — multimodal food ID prompt
  - `resources/prompts/meal-suggestions.st` — macro-based meal suggestion prompt
  - `resources/prompts/weekly-digest.st` — weekly nutrition summary prompt
- [ ] `LanguageDetector.java`: simple heuristic — count Cyrillic characters; if > 15% of total chars → `"ru"` else `"en"` (no external library needed)
- [ ] `RagPipeline.java`:
  - `retrieveContext(String query, UUID userId)` → embed query → vector search via food-service REST `GET /foods/vector-search?q={base64vector}&limit=15`
  - `buildPrompt(String query, List<FoodContext> context, String language)` → load template → inject context JSON + language variable
  - `parseStructuredOutput(String rawLlmResponse)` → `BeanOutputConverter<List<ParsedFoodItem>>` → handle JSON parse failure with regex fallback
- [ ] `NlFoodParser.java`: orchestrate LanguageDetector → RagPipeline → validation (quantity 0–5000g) → enrich with food-service data for matched IDs
- [ ] `POST /ai/food/parse-text`: async same as photo recognition — returns `requestId`, pushes `AI_NL_PARSE_COMPLETE` SSE event

**Web + iOS:**
- [ ] `NlInputBox.tsx`: `<textarea>` with placeholder `"I had oatmeal with milk..."` / `"Я ел овсянку с молоком..."` (placeholder changes with language), POST on submit → show loading state → SSE triggers `ParsedFoodPreview` modal
- [ ] `ParsedFoodPreview.tsx`: list of parsed items with editability, same confirm flow as photo recognition

---

#### Phase 5c — Meal Suggestions + Analytics Insights (Week 12)

**Backend:**
- [ ] `MealSuggestionEngine.java`:
  1. Call analytics-service `GET /analytics/summary?date=today` → get remaining macros
  2. Embed `"${mealType} ${remainingCalories} kcal ${remainingProtein}g protein"` → vector search → top 20 candidate foods
  3. `MealSuggestionRules.java`: filter candidates — remove foods eaten today, remove disliked foods (call user-service), score by macro fit formula: `score = 1 - |actualProtein% - goalProtein%| - |actualCarbs% - goalCarbs%|`; take top 5
  4. Build prompt with top 5 foods + remaining macros → LLM → `List<MealSuggestionDto>`
- [ ] Redis caching: `ai:suggest:{userId}:{date}:{mealType}` with 2-hour TTL using Spring's `@Cacheable` + `RedisTemplate`
- [ ] `NutritionInsightService.java`: aggregate last 90 days of `daily_summaries` (call analytics-service) → build context JSON → LLM → one paragraph; cached per user per month

---

#### Phase 5d — Anomaly Detection + Weekly Digest (Week 13)

**Backend:**
- [ ] `CalorieAnomalyDetector.java`:
  - Z-Score: `double[] last7Totals = analyticsService.getLast7DayCalories(userId)` → compute mean + σ → if `|z| > 2.0` flag
  - Hard rules: `if totalCalories < 800` → always flag (health risk); `if totalCalories > 3 * goal` → always flag
  - Return `List<AnomalyDto>` — each with date, actual calories, expected range, severity (`LOW` / `HIGH`)
- [ ] `WeeklyDigestGenerator.java`: `@KafkaListener(topics = "analytics.report.ready")` → receive `AnalyticsReportReadyEvent` → load `weekly-digest.st` prompt → inject `{ avgCalories, avgProtein, weightDelta, streak, language }` → call LLM → result published to `notification.push.send` Kafka topic (notification-service picks it up and emails)
- [ ] All AI REST endpoints wired in `AiController`: `/insights`, `/anomalies`, `/suggestions`, `/weekly-digest`
- [ ] Complete AI usage logging to `ai_usage_logs` (latency_ms, model_used, tokens_in/out estimates, feature name, success/failure)

**Web + iOS:**
- [ ] `AiInsightsPage.tsx` / screen: tabbed view — Suggestions tab (meal suggestion cards), Insights tab (LLM paragraph + key stats), Anomalies tab (calendar highlighting flagged days)
- [ ] ✅ **Milestone:** Upload a food photo → result appears via SSE → confirm → diary entry created; type "I had eggs and toast" → 2 entries created with correct macros

---

### 🏗 Phase 6 — Notifications + Security Hardening (Weeks 14–15)

**Goal:** All notification channels operational; full production-grade security across all services.

---

#### 🔬 Technology Deep-Dive: Expo Push Notifications (APNs)

**How Expo push notifications work:**
```
1. iOS app starts → requests notification permission (UNUserNotificationCenter)
2. If granted → Expo SDK generates an Expo Push Token:
   "ExponentPushToken[xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx]"
3. App POSTs this token to your backend (user-service, push_tokens table)
4. When server wants to notify user:
   POST https://exp.host/--/api/v2/push/send
   { to: "ExponentPushToken[...]", title: "...", body: "..." }
5. Expo's server relays to Apple's APNs → iOS delivers notification
```

Expo abstracts APNs (Apple Push Notification Service) — you never deal with APNs certificates directly during development. For production, configure your Apple credentials in Expo EAS.

**What you will learn:**
- How APNs works conceptually (device token → Expo token → your server)
- How `expo-notifications` handles foreground vs. background notification receipt
- Why you must ask for notification permission at the right time (not on first launch)
- How to test push notifications on iOS Simulator using Expo's push notification tool

---

#### 🔬 Technology Deep-Dive: AES-256 Column Encryption with JPA AttributeConverter

**Why encrypt specific columns?**
Full disk encryption protects data at rest, but anyone with database access still sees plaintext `email` and `full_name` columns. Column-level encryption means even a compromised DB dump reveals only ciphertext for sensitive fields.

**How JPA `AttributeConverter` works:**
```java
@Converter
public class EncryptedStringConverter implements AttributeConverter<String, String> {
    private final AesEncryptionService aes;  // injected

    @Override
    public String convertToDatabaseColumn(String plaintext) {
        return aes.encrypt(plaintext);       // called before INSERT/UPDATE
    }

    @Override
    public String convertToEntityAttribute(String ciphertext) {
        return aes.decrypt(ciphertext);      // called after SELECT
    }
}

// On entity field:
@Convert(converter = EncryptedStringConverter.class)
@Column(name = "email")
private String email;
```

JPA calls your converter transparently — the service layer works with plaintext, the DB stores ciphertext.

**AES-256-GCM implementation:**
- Algorithm: AES-256-GCM (authenticated encryption — detects tampering)
- Key: 32-byte key from `ENCRYPTION_KEY` env variable (never hardcoded)
- Each encryption generates a fresh random 12-byte IV (nonce), prepended to ciphertext
- `AesEncryptionService.java` uses `javax.crypto.Cipher`

**What you will learn:**
- How AES-GCM authenticated encryption works (confidentiality + integrity in one operation)
- Why each encryption must use a unique IV/nonce (reusing the IV breaks GCM security)
- The trade-off: encrypted columns cannot be indexed for exact-match lookups (you cannot `SELECT WHERE email = ?` on encrypted data — use a separate HMAC index column for lookup)

---

#### 🔬 Technology Deep-Dive: Bucket4j Rate Limiting + Redis

**How Bucket4j works:**
Bucket4j implements the **Token Bucket** algorithm. Each IP (or user) gets a bucket with N tokens. Each request consumes 1 token. Tokens refill at a set rate. When the bucket is empty → 429 Too Many Requests.

```
Login endpoint bucket:
  Capacity: 5 tokens
  Refill: 5 tokens per 60 seconds (fixed window)
  Result: max 5 login attempts per minute per IP

Using Redis (distributed bucket):
  Multiple gateway instances share the same bucket state in Redis
  Without Redis, each gateway pod has its own bucket → attacker can bypass by hitting different pods
```

```java
// In API Gateway:
@Component
public class RateLimitFilter implements GlobalFilter {
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String ip = exchange.getRequest().getRemoteAddress().getAddress().getHostAddress();
        BucketProxyManager manager = Bucket4j.extension(JCacheExtension.class).proxyManagerForCache(redisCache);
        Bucket bucket = manager.builder()
            .addLimit(Bandwidth.classic(5, Refill.intervally(5, Duration.ofMinutes(1))))
            .build(ip);
        if (bucket.tryConsume(1)) return chain.filter(exchange);
        exchange.getResponse().setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
        return exchange.getResponse().setComplete();
    }
}
```

**What you will learn:**
- Token bucket vs. leaky bucket vs. sliding window rate limiting algorithms
- How to use Redis as a distributed counter (atomic increment with TTL)
- How to differentiate rate limits by IP vs. by authenticated userId
- Why rate limiting belongs in the Gateway (not in each service)

---

#### Tasks

**notification-service — Backend:**
- [ ] Flyway migrations: all notification tables
- [ ] `SseNotificationService.java`: `ConcurrentHashMap<UUID, SseEmitter>` — thread-safe emitter registry; `pushToUser(UUID userId, NotificationDto dto)` sends SSE event; heartbeat thread pings all emitters every 30s to keep connection alive
- [ ] `GET /notifications/stream`: creates `SseEmitter(Long.MAX_VALUE)` → registers in map → sends initial `{ type: "CONNECTED" }` event immediately (prevents browser timeout)
- [ ] Kafka consumers:
  - `diary.entry.created` consumer: check if `totalCalories > goalCalories` → create `GOAL_EXCEEDED` notification → `sseNotificationService.pushToUser()`
  - `analytics.report.ready` consumer: trigger `WeeklyDigestGenerator` (in ai-service via Kafka) or call ai-service REST
  - `user.registered` consumer: send welcome email via SendGrid
- [ ] `MealReminderScheduler.java`: `@Scheduled(cron = "0 * * * * *")` (every minute) → query `scheduled_reminders` for entries where `time_local = current_time_for_user_timezone` → send push notifications via Expo Push API
- [ ] `ExpoPushService.java`: HTTP POST to `https://exp.host/--/api/v2/push/send` using Spring's `RestClient`; handle chunked sending (max 100 tokens per request)
- [ ] `SendGridEmailService.java`: `sendgrid-java` SDK — template-based emails for welcome + weekly digest; select `en`/`ru` template based on user language

**Security Hardening (all services):**
- [ ] `EncryptedStringConverter.java` + `AesEncryptionService.java` in `auth-service` and `user-service` — apply `@Convert` to `email` and `fullName` columns
- [ ] `AuditAspect.java` in `auth-service` and `diary-service`: `@Around("@annotation(AuditLog)")` — intercept annotated service methods → extract userId from `SecurityContextHolder` → save `AuditLog` entity before/after method call
- [ ] Bucket4j + Redis rate limiting in `api-gateway`: separate buckets for `/auth/login` (5/min), `/auth/register` (3/min), `/ai/**` (20/min)
- [ ] CORS config in Gateway: `allowedOrigins` = `[VITE_APP_URL, https://your-ios-app-domain]` only
- [ ] MFA setup + verify endpoints fully integrated in web `SettingsPage.tsx` + iOS `SettingsScreen.tsx`

**Web + iOS:**
- [ ] `NotificationBell.tsx`: SSE connection via `EventSource`, Zustand `notificationStore` tracks unread count, badge count shown on bell icon
- [ ] `NotificationsPage.tsx`: list with `react-hot-toast` toasts for new real-time arrivals, mark-all-read button
- [ ] iOS: `expo-notifications` permission request → register push token on first login → `Notifications.addNotificationResponseReceivedListener` → navigate to relevant screen on tap
- [ ] `SettingsPage.tsx` / screen: notification preferences toggles, meal reminder time pickers, MFA enable/disable, language switcher
- [ ] ✅ **Milestone:** Log a meal that exceeds daily goal → push notification appears on iOS within 5 seconds

---

### 🏗 Phase 7 — Production Readiness + iOS TestFlight (Weeks 16–18)

**Goal:** The app is fully observable, deployable with a single command, and installable on an iPhone via TestFlight.

---

#### 🔬 Technology Deep-Dive: Distributed Tracing with Zipkin

**The problem in microservices:**
A single user request can span 5 services: Gateway → diary-service → food-service (validate) → analytics-service (Kafka) → notification-service (Kafka). If the request is slow or fails, which service is the bottleneck?

**How distributed tracing solves it:**
Every request gets a **Trace ID** (UUID generated at the Gateway). Each service-to-service call gets a **Span ID**. Both IDs are propagated via HTTP headers (`X-B3-TraceId`, `X-B3-SpanId`). Each service reports its spans to Zipkin.

```
Zipkin UI shows:
TraceID: abc123
  [Gateway]          0ms → 5ms    (JWT validation, routing)
  [diary-service]    5ms → 45ms   (business logic)
    [food-service]   10ms → 30ms  (nutrition validation REST call)
  [analytics-service] async       (Kafka consumer, separate trace)
```

Spring Cloud Sleuth instruments your `RestTemplate`/`RestClient`, `@KafkaListener`, and `@FeignClient` automatically — zero code changes needed.

**What you will learn:**
- How to read a Zipkin trace waterfall and identify bottlenecks
- The difference between a trace (full request journey) and a span (single operation)
- How `spring-cloud-sleuth-zipkin` auto-instruments your beans
- Why async Kafka consumers create child traces linked to the parent trace ID

---

#### 🔬 Technology Deep-Dive: Prometheus + Grafana

**Prometheus** scrapes metrics from your services' `/actuator/prometheus` endpoints every 15s and stores them as time-series data. **Grafana** queries Prometheus and renders dashboards.

**Key metrics you'll monitor:**
```
# Business metrics (custom Micrometer counters):
diary.entry.created.total              ← food logs per minute
ai.photo.recognition.duration.seconds  ← AI latency histogram
ai.photo.recognition.errors.total      ← AI failure count

# Kafka lag (via JMX metrics from Kafka):
kafka.consumer.lag{group, topic}       ← how far behind each consumer is

# JVM metrics (auto-collected by Micrometer):
jvm.memory.used{area="heap"}
jvm.threads.live
http.server.requests.seconds{quantile="0.95"}  ← p95 response time
```

**Custom Micrometer metric example:**
```java
@Service
public class DiaryEntryService {
    private final Counter foodLogCounter;

    public DiaryEntryService(MeterRegistry registry) {
        this.foodLogCounter = Counter.builder("diary.entry.created")
            .description("Number of food diary entries created")
            .tag("source", "unknown")
            .register(registry);
    }

    public DiaryEntry create(DiaryEntryRequest req) {
        // ... business logic ...
        foodLogCounter.increment(1, Tags.of("source", req.source().name()));
        return entry;
    }
}
```

**What you will learn:**
- How Micrometer's `MeterRegistry` abstraction works (same code → Prometheus, Datadog, CloudWatch, etc.)
- How to create Grafana dashboards from scratch with PromQL queries
- How to set up Prometheus alerting rules (`alert: HighAiLatency` if p95 > 30s)
- What Kafka consumer lag means and why high lag indicates a service falling behind

---

#### 🔬 Technology Deep-Dive: Expo EAS Build — iOS Distribution

**What is EAS (Expo Application Services)?**
Expo's cloud build service. You run `eas build --platform ios` locally → EAS builds your app on Apple's Mac build servers in the cloud → produces a `.ipa` file → you submit to TestFlight.

**Why not Xcode locally?**
You'd need a Mac with Xcode, an Apple Developer account ($99/year), and manual provisioning profile management. EAS handles all of this automatically.

**Build profiles (`eas.json`):**
```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "production": {
      "distribution": "store"
    }
  }
}
```

**What you will learn:**
- How iOS code signing works (certificates, provisioning profiles, bundle IDs)
- How to configure `app.json` for production (bundle ID, version, permissions)
- How `Info.plist` permission strings work (`NSCameraUsageDescription`, `NSMicrophoneUsageDescription`)
- The TestFlight distribution flow and how to invite testers

---

#### Tasks

**Backend — Observability:**
- [ ] Add custom Micrometer counters in diary-service (`diary.entry.created.total` tagged by `source`), ai-service (`ai.recognition.duration` histogram, `ai.recognition.errors` counter)
- [ ] Configure Zipkin exporter in all services: `management.zipkin.tracing.endpoint=http://zipkin:9411/api/v2/spans`, `management.tracing.sampling.probability=1.0` (100% in dev, 10% in prod)
- [ ] Write Prometheus scrape config `docker/prometheus.yml` with scrape targets for all services
- [ ] Build Grafana dashboard JSON with 4 panels: calorie logs/min, AI recognition p95 latency, Kafka consumer lag per topic, HTTP error rate per service

**Backend — API Documentation:**
- [ ] Add `springdoc-openapi-starter-webmvc-ui` to all services; each service exposes `/v3/api-docs` and `/swagger-ui.html`
- [ ] Add springdoc gateway aggregation: `springdoc.swagger-ui.urls` in `api-gateway` points to all service `/v3/api-docs` endpoints → single Swagger UI at `http://localhost:8080/swagger-ui.html` showing all APIs

**Backend — Dockerfiles (one per service):**
```dockerfile
# Multi-stage Gradle build
FROM eclipse-temurin:26-jdk-alpine AS builder
WORKDIR /app
COPY gradlew settings.gradle.kts build.gradle.kts gradle/ ./
RUN ./gradlew :services:{service-name}:dependencies --no-daemon   # cache layer
COPY services/{service-name}/src services/{service-name}/src
COPY services/{service-name}/build.gradle.kts services/{service-name}/
RUN ./gradlew :services:{service-name}:bootJar --no-daemon

FROM eclipse-temurin:26-jre-alpine
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /app/services/{service-name}/build/libs/*.jar app.jar
USER app
ENTRYPOINT ["java", "-Dspring.threads.virtual.enabled=true", "-jar", "app.jar"]
```
- [ ] Create Dockerfile for all 8 services + 2 infrastructure services

**GitHub Actions CI:**
```yaml
jobs:
  build-backend:
    strategy:
      matrix:
        service: [auth, user, food, diary, ai, analytics, notification, api-gateway]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '26', distribution: 'temurin' }
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew :services:${{ matrix.service }}-service:test
      - run: ./gradlew :services:${{ matrix.service }}-service:bootJar
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: services/${{ matrix.service }}-service/Dockerfile
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ghcr.io/${{ github.repository }}/${{ matrix.service }}-service:latest
```

**iOS — TestFlight:**
- [ ] Configure `app.json`: `"bundleIdentifier": "com.yourname.calorietracker"`, `"version": "1.0.0"`, `"buildNumber": "1"`, `"infoPlist"` with camera + notifications permission strings in EN + RU
- [ ] Configure `eas.json` with `development`, `preview`, `production` build profiles
- [ ] Run `eas build --platform ios --profile preview` → install on physical device via QR code
- [ ] Run `eas build --platform ios --profile production` → `eas submit --platform ios` → TestFlight
- [ ] Dark mode: implement `useColorScheme()` hook, toggle Bootstrap CSS variables on web; on iOS `Appearance.getColorScheme()` + conditional style objects

**Final Polish:**
- [ ] Offline sync indicator in iOS: `NetInfo` from `@react-native-community/netinfo` → show `OfflineBanner` component + pending sync count badge
- [ ] Write `README.md` with: architecture diagram, local dev setup steps (`docker-compose up`, model pull commands, env variable template), iOS setup steps (`eas build`)
- [ ] ✅ **Final Milestone:** `docker-compose up` → register → log 3 meals → upload receipt photo → AI fills in food → install iOS app via TestFlight → all features work on device

---

## 14. Infrastructure & DevOps

### Docker Compose (local dev)

```yaml
services:
  # ── Spring Cloud Infrastructure ─────────────────────────────────────────────
  eureka:
    build: ./infrastructure/eureka-server
    ports: ["8761:8761"]

  config-server:
    build: ./infrastructure/config-server
    ports: ["8888:8888"]
    depends_on: [eureka]

  # ── Application Services ─────────────────────────────────────────────────────
  api-gateway:
    build: ./services/api-gateway
    ports: ["8080:8080"]
    depends_on: [eureka, config-server, redis]

  auth-service:
    build: ./services/auth-service
    depends_on: [postgres, redis, kafka, eureka, config-server]

  user-service:
    build: ./services/user-service
    depends_on: [postgres, kafka, eureka, config-server]

  food-service:
    build: ./services/food-service
    depends_on: [postgres, kafka, ollama, eureka, config-server]

  diary-service:
    build: ./services/diary-service
    depends_on: [postgres, kafka, eureka, config-server]

  ai-service:
    build: ./services/ai-service
    depends_on: [ollama, kafka, redis, minio, eureka, config-server]

  analytics-service:
    build: ./services/analytics-service
    depends_on: [postgres, kafka, eureka, config-server]

  notification-service:
    build: ./services/notification-service
    depends_on: [postgres, kafka, redis, eureka, config-server]

  # ── Data & Messaging ──────────────────────────────────────────────────────────
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: calorietracker
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    # init.sql creates: auth_db, user_db, food_db, diary_db, analytics_db, notification_db
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U calorietracker"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}

  zookeeper:
    image: confluentinc/cp-zookeeper:7.7.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.7.0
    ports: ["9092:9092"]
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    depends_on: [zookeeper]

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    volumes: [minio_data:/data]

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: [ollama_data:/root/.ollama]
    healthcheck:
      test: ["CMD-SHELL", "ollama list || exit 1"]
      interval: 15s
      retries: 10
      start_period: 60s
    # First-time model pull (run once):
    # docker exec ollama sh -c "ollama pull llama3.1:8b && ollama pull nomic-embed-text && ollama pull llava:7b"

  # ── Observability ──────────────────────────────────────────────────────────────
  zipkin:
    image: openzipkin/zipkin
    ports: ["9411:9411"]

  prometheus:
    image: prom/prometheus
    volumes: [./docker/prometheus.yml:/etc/prometheus/prometheus.yml]
    ports: ["9090:9090"]

  grafana:
    image: grafana/grafana
    ports: ["3001:3000"]
    depends_on: [prometheus]

volumes:
  postgres_data:
  minio_data:
  ollama_data:     # ⚠ llama3.1:8b ≈ 4.7 GB · llava:7b ≈ 4.1 GB · nomic-embed-text ≈ 274 MB
```

### Environment Variables

```env
# Shared
DB_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
JWT_SECRET=<256-bit-random>
JWT_REFRESH_SECRET=<256-bit-random>
ENCRYPTION_KEY=<32-byte-aes-key-hex>

# OAuth2
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# AI (self-hosted — no external API key!)
SPRING_AI_OLLAMA_BASE_URL=http://ollama:11434
SPRING_AI_OLLAMA_CHAT_MODEL=llama3.1:8b
SPRING_AI_OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_VISION_MODEL=llava:7b

# External Food APIs (free tiers, no cost)
USDA_API_KEY=<free key from api.nal.usda.gov>
# Open Food Facts: no key needed (fully open)

# Storage & Email
MINIO_USER=...
MINIO_PASSWORD=...
SENDGRID_API_KEY=SG...
EXPO_PUSH_TOKEN_SECRET=...   # for server-side push signing

# Frontend (.env)
VITE_API_BASE_URL=https://your-domain.com/api/v1
VITE_DEFAULT_LANGUAGE=en

# Mobile (.env — Expo)
EXPO_PUBLIC_API_BASE_URL=https://your-domain.com/api/v1
```

### GitHub Actions CI

```yaml
jobs:
  build-services:
    strategy:
      matrix:
        service: [auth, user, food, diary, ai, analytics, notification, api-gateway]
    steps:
      - Checkout
      - Setup Java 26 (Temurin)
      - ./gradlew :services:{service}-service:test
      - ./gradlew :services:{service}-service:bootJar
      - Docker build + push to GHCR

  build-web:
    - Setup Node 22 · npm ci · npm run lint · npm test · npm run build

  build-mobile:
    - Setup Node 22 · npm ci · npx expo export
    - EAS Build (iOS simulator) on tag push
```

---

## 15. Further Considerations

1. **TDEE formula choice:** Spec uses **Mifflin-St Jeor** (most accurate for general population). Implement **Harris-Benedict** as alternative in `TdeeCalculator.java` using a Strategy pattern — let users pick in settings. Formula: `BMR = 10×weight(kg) + 6.25×height(cm) − 5×age + 5` (men) / `-161` (women); multiply by activity factor.

2. **llava:7b food recognition accuracy:** Expect ~70–80% accuracy on clear, well-lit single-dish photos. Multi-dish photos or heavily processed foods degrade accuracy. Always show the result as **editable** with confidence score. Set confidence threshold to 0.4 — anything below shows a "?" icon prompting manual correction.

3. **Open Food Facts API rate limits:** No hard limit, but fair-use policy applies. Cache all barcode responses in `barcode_cache` table (TTL: 30 days). For high-frequency lookups, store raw JSON in the cache column — no repeated API calls for the same barcode.

4. **USDA FoodData Central:** Free API key at `api.nal.usda.gov`. Rate limit: 3,600 req/hour. Use it as fallback when Open Food Facts has no result. USDA has excellent data for raw ingredients (meats, vegetables, grains) while Open Food Facts is better for packaged products.

5. **Kafka partition sizing:** Start with 3 partitions per topic. `diary.entry.created` will be the highest-volume topic — partition by `userId` (use userId as Kafka message key) to guarantee ordering per user.

6. **Offline sync conflict resolution:** Diary entries have a `logged_at` timestamp generated on the device. If the same `(userId, foodId, date, mealType, logged_at)` combination arrives twice (network retry), the diary-service endpoint is **idempotent** — check for duplicate `logged_at + foodId` before insert.

7. **iOS App Store requirements:** Camera usage requires `NSCameraUsageDescription` in `Info.plist`. Notifications require `UNUserNotificationCenter` permission prompt — only request it after user has logged their first meal (better conversion than asking on first launch).

8. **Monorepo Gradle build time:** With 8+ subprojects, cold build can be slow. Enable Gradle build cache (`org.gradle.caching=true` in `gradle.properties`) and Gradle daemon. Consider `--parallel` flag. Each service's tests run in isolation via Testcontainers.

9. **Russian food database coverage:** Open Food Facts has limited Russian product coverage. Consider importing the **Russian-language Open Food Facts dump** (`openfoodfacts-products.jsonl.gz`) for local products. Alternatively, manually seed 200–300 popular Russian foods (`Гречневая каша`, `Борщ`, `Творог`, etc.) in the Flyway seed migration.

10. **pgvector multilingual embeddings:** `nomic-embed-text` handles Russian well despite being primarily trained on English — Cyrillic text is embedded meaningfully. However, search quality improves if you **concatenate** `name_en + " " + name_ru` as the embedded content rather than embedding each language separately. Test with a small sample before committing.

---

*Estimated total effort: ~18 weeks solo (AI + microservices learning curve)*
*Recommended start: Phase 1 infrastructure skeleton — `./gradlew :infrastructure:eureka-server:bootRun` and watch all services discover each other.* 🚀

---

## 16. Architecture Decision Records (ADRs)

> ADRs document the **why** behind key technical choices. Each decision was made for a reason — these records prevent future "why did we do it this way?" confusion and are excellent talking points in technical interviews.

---

### ADR-001: Microservices over Monolith

**Status:** Accepted

**Context:** The application has 6 distinct domains (Auth, Food, Diary, AI, Analytics, Notifications) with different scaling needs and update frequencies.

**Decision:** Use microservices with database-per-service.

**Consequences:**
- ✅ Each service can be deployed, scaled, and updated independently
- ✅ AI service can be given more resources (CPU/GPU) without scaling all other services
- ✅ Food database can be shared across users without coupling to per-user diary data
- ✅ Massive learning opportunity: service discovery, distributed transactions, eventual consistency
- ❌ Significantly more operational complexity vs. a monolith
- ❌ Distributed tracing and debugging is harder
- ❌ Network calls between services add latency (mitigation: cache aggressively, use async Kafka for non-critical paths)

**Alternatives considered:** Spring Modulith (modular monolith) — rejected because it doesn't provide the same microservices learning value.

---

### ADR-002: Ollama (Local LLM) over OpenAI API

**Status:** Accepted

**Context:** AI features require text generation, embeddings, and image understanding.

**Decision:** Use Ollama with `llama3.1:8b`, `nomic-embed-text`, and `llava:7b` running locally in Docker.

**Consequences:**
- ✅ Zero API cost — no per-token billing
- ✅ Data never leaves your machine — full privacy
- ✅ Deep learning: understand how LLMs actually work, not just call an API
- ✅ Works offline
- ❌ Requires 8–16 GB RAM for model inference
- ❌ Inference is slower than cloud APIs (5–30s vs 1–3s)
- ❌ `llava:7b` food recognition quality is lower than GPT-4o Vision

**Alternatives considered:** OpenAI API — rejected (costs money, data leaves your machine, less educational). Hugging Face Inference API — rejected (requires internet, free tier is rate-limited).

---

### ADR-003: PostgreSQL + pgvector over Dedicated Vector DB

**Status:** Accepted

**Context:** AI features require semantic vector search over food names and descriptions.

**Decision:** Use pgvector extension on the existing PostgreSQL instance instead of a dedicated vector database (Pinecone, Weaviate, Qdrant).

**Consequences:**
- ✅ No additional service to deploy or manage
- ✅ Vector search lives in the same transaction as relational data (JOIN is possible)
- ✅ Familiar SQL interface — no new query language to learn
- ✅ pgvector HNSW index is performant enough for millions of food records
- ❌ Not suitable for billion-scale vector search (not a concern here)
- ❌ pgvector lacks some advanced filtering features of dedicated DBs (mitigated in v0.7+)

**Alternatives considered:** Qdrant — rejected (another Docker service, overkill for food search). Weaviate — rejected (same reason).

---

### ADR-004: Apache Kafka over RabbitMQ / HTTP Webhooks

**Status:** Accepted

**Context:** Services need to communicate asynchronously (diary entries → analytics, AI results → diary).

**Decision:** Apache Kafka as the event bus.

**Consequences:**
- ✅ Messages are persisted on disk — consumers can replay from any offset (useful for rebuilding analytics from scratch)
- ✅ Multiple independent consumer groups can read the same topic (analytics AND notifications both consume `diary.entry.created`)
- ✅ Industry standard — used at virtually every large-scale company
- ✅ Excellent learning value: offset management, consumer groups, partitioning
- ❌ More complex to set up than RabbitMQ (requires Zookeeper / KRaft)
- ❌ Higher memory footprint for local dev

**Alternatives considered:** RabbitMQ — rejected (message-oriented, not log-oriented; no message replay). HTTP webhooks — rejected (tight coupling, no retry guarantees).

---

### ADR-005: React Native + Expo over Flutter or Native Swift

**Status:** Accepted

**Context:** iOS app needed. Team (solo dev) already knows React from the web app.

**Decision:** React Native + Expo SDK.

**Consequences:**
- ✅ Shared knowledge with web React app (same hooks, same state management, same i18next)
- ✅ Expo abstracts iOS complexity (code signing, push notifications, camera)
- ✅ Code sharing potential: Zustand stores, Zod schemas, API client, translations
- ✅ Expo EAS Build for TestFlight without a Mac build machine
- ❌ Performance-critical animations require `react-native-reanimated` boilerplate
- ❌ Camera/barcode is `expo-camera` — slightly less control than native

**Alternatives considered:** Flutter — rejected (different language, Dart, no knowledge overlap with web). Native Swift — rejected (full rebuild, no code reuse, much higher time investment).

---

### ADR-006: Spring Cloud Gateway as API Gateway over NGINX / Kong

**Status:** Accepted

**Context:** All client traffic must be routed to appropriate microservices with JWT validation.

**Decision:** Spring Cloud Gateway (reactive, built on Netty + WebFlux).

**Consequences:**
- ✅ Written in Java — same language as all other services, same `build.gradle.kts`, same deployment model
- ✅ Integrates natively with Eureka service discovery (`lb://SERVICE-NAME` routing)
- ✅ JWT validation filter is easy to write in Java alongside Spring Security
- ✅ Bucket4j rate limiting integrates naturally as a `GlobalFilter`
- ❌ Higher memory footprint than NGINX for pure routing
- ❌ Less battle-tested at truly extreme traffic (millions of req/s) vs NGINX

**Alternatives considered:** NGINX — rejected (no native Eureka integration, config in a different language). Kong — rejected (overkill, requires separate management plane).

---

### ADR-007: Gradle (Kotlin DSL) over Maven

**Status:** Accepted

**Context:** Build system for Java 26 + Spring Boot 4 multi-project monorepo.

**Decision:** Gradle with Kotlin DSL (`build.gradle.kts`).

**Consequences:**
- ✅ Multi-project builds with `settings.gradle.kts` — single `./gradlew build` for all services
- ✅ Kotlin DSL provides IDE auto-completion and type safety vs. XML Maven
- ✅ Version catalogs (`libs.versions.toml`) eliminate version duplication across subprojects
- ✅ Faster incremental builds than Maven (build cache + incremental compilation)
- ❌ Steeper learning curve than Maven XML for newcomers
- ❌ Kotlin DSL error messages can be cryptic when syntax is wrong

**Alternatives considered:** Maven — rejected (verbose XML, no first-class multi-project build support). Bazel — rejected (extreme complexity, not needed at this scale).

---

## 17. Testing Strategy

> A senior developer ships confidence, not just code. This section defines testing at every layer of the stack.

### Testing Pyramid

```
           /\
          /E2E\          ← Few: full user journey tests (Playwright / Detox)
         /------\
        /Integr. \       ← Some: service-to-service + DB tests (Testcontainers)
       /------------\
      / Unit Tests   \   ← Many: pure business logic, fast, no I/O
     /________________\
```

---

### Unit Testing — Backend (JUnit 5 + Mockito)

**What to unit test:**
- Service-layer business logic (all methods in `*Service.java`)
- Utility classes: `TdeeCalculatorService`, `AnomalyDetector`, `LanguageDetector`, `ImagePreprocessor`
- JWT validation logic in `JwtService`
- Prompt building in `PromptTemplateEngine`
- Structured output parsing in `StructuredOutputParser`

**What NOT to unit test:**
- Controllers (test via integration tests)
- JPA repositories (test via integration tests with real DB)
- Kafka consumers (test via integration tests with Testcontainers Kafka)

**Patterns:**
```java
// Test TDEE calculation (pure math — no mocking needed):
@Test
void tdee_male_moderate_activity() {
    TdeeCalculatorService sut = new TdeeCalculatorService();
    TdeeResult result = sut.calculate(new TdeeRequest(
        Gender.MALE, 30, 180.0, 80.0, ActivityLevel.MODERATE
    ));
    // BMR = 10*80 + 6.25*180 - 5*30 + 5 = 1880
    // TDEE = 1880 * 1.55 = 2914
    assertThat(result.tdee()).isCloseTo(2914, within(10));
}

// Test anomaly detection Z-score (mock analytics data):
@Test
void zScore_detects_high_calorie_day() {
    double[] history = {1800, 1850, 1900, 1750, 1820, 1880};  // mean ~1833, σ ~55
    CalorieAnomalyDetector sut = new CalorieAnomalyDetector();
    List<Anomaly> anomalies = sut.detect(3500.0, history);     // z = (3500-1833)/55 = 30 → anomaly
    assertThat(anomalies).hasSize(1);
    assertThat(anomalies.get(0).severity()).isEqualTo(Severity.HIGH);
}
```

---

### Integration Testing — Backend (Testcontainers)

**What is Testcontainers?**
A Java library that starts real Docker containers (PostgreSQL, Kafka, Redis) during tests and tears them down after. No mocking of database behaviour — tests run against the real thing.

```java
@SpringBootTest
@Testcontainers
class DiaryServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("pgvector/pgvector:pg17")
            .withDatabaseName("diary_db_test");

    @Container
    static KafkaContainer kafka =
        new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.7.0"));

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    @Autowired DiaryEntryService diaryEntryService;
    @Autowired DiaryEntryRepository repository;

    @Test
    void createEntry_snapshotsNutrition_andPublishesKafkaEvent() {
        // Stub food-service REST call with WireMock:
        wireMockServer.stubFor(get(urlPathEqualTo("/foods/uuid-123"))
            .willReturn(aResponse()
                .withHeader("Content-Type", "application/json")
                .withBody("""{"id":"uuid-123","nameEn":"Oatmeal","caloriesPer100g":389}""")));

        DiaryEntryRequest req = new DiaryEntryRequest("uuid-123", 80.0, MealType.BREAKFAST, LocalDate.now());
        DiaryEntry entry = diaryEntryService.create(req, userId);

        assertThat(entry.getCalories()).isCloseTo(311.2, within(0.1));  // 80 * 3.89
        assertThat(repository.findById(entry.getId())).isPresent();
        // Verify Kafka event was published:
        kafkaConsumer.subscribe(List.of("diary.entry.created"));
        ConsumerRecord<String, DiaryEntryCreatedEvent> record = kafkaConsumer.poll(Duration.ofSeconds(5)).iterator().next();
        assertThat(record.value().calories()).isCloseTo(311.2, within(0.1));
    }
}
```

**Test coverage targets per service:**

| Service | Unit | Integration |
|---|---|---|
| auth-service | JWT logic, password hashing, TOTP | Login flow, token refresh, MFA end-to-end |
| food-service | Barcode chain logic, RRF merge, embedding content builder | pgvector search, Flyway migrations, Retrofit client mock |
| diary-service | Calorie computation, copy-day logic | Bulk create, Kafka event publishing, food-service REST stub |
| ai-service | LanguageDetector, AnomalyDetector algorithms, StructuredOutputParser | Ollama mocked via WireMock, RAG pipeline with fake pgvector results |
| analytics-service | TDEE calc, streak algorithm | Kafka consumption → daily_summaries upsert |

---

### Mocking Ollama in Tests (WireMock)

Never call real Ollama in automated tests — it's slow and non-deterministic.

```java
// In ai-service tests: WireMock stubs the Ollama HTTP API
@BeforeEach
void setupOllama() {
    wireMock.stubFor(post(urlPathEqualTo("/api/chat"))
        .withRequestBody(matchingJsonPath("$.model", equalTo("llama3.1:8b")))
        .willReturn(aResponse()
            .withHeader("Content-Type", "application/json")
            .withBody("""
                {"message":{"role":"assistant","content":
                "[{\\"foodId\\":\\"uuid-123\\",\\"quantityG\\":80,\\"mealType\\":\\"BREAKFAST\\"}]"
                }}""")));
}

@Test
void nlFoodParser_parsesOatmealEntry() {
    List<ParsedFoodItem> result = nlFoodParser.parse("I had 80g of oatmeal for breakfast", "en");
    assertThat(result).hasSize(1);
    assertThat(result.get(0).quantityG()).isEqualTo(80.0);
    assertThat(result.get(0).mealType()).isEqualTo(MealType.BREAKFAST);
}
```

---

### Contract Testing (Pact)

**What is contract testing?**
In microservices, if diary-service calls food-service REST API, who ensures the contract (request/response schema) doesn't break when food-service changes? Contract tests.

**Pact** framework: the consumer (diary-service) writes a "pact" defining what it expects from the provider (food-service). The provider verifies it can satisfy the pact.

```java
// diary-service (Consumer):
@Pact(consumer = "diary-service", provider = "food-service")
RequestResponsePact getFoodById(PactDslWithProvider builder) {
    return builder
        .given("food with id uuid-123 exists")
        .uponReceiving("a request for food uuid-123")
        .path("/foods/uuid-123").method("GET")
        .willRespondWith().status(200)
        .body(new PactDslJsonBody()
            .stringType("id", "uuid-123")
            .stringType("nameEn", "Oatmeal")
            .numberType("caloriesPer100g", 389.0))
        .toPact();
}
```

**What you will learn:**
- Consumer-Driven Contract Testing — one of the most important patterns in microservices
- How Pact broker works to share contracts between services in CI
- The difference between contract tests and integration tests

---

### Frontend Testing (Vitest + Testing Library)

```typescript
// Test CalorieRing renders correct percentage:
it('shows 75% fill when 1500 of 2000 calories consumed', () => {
  render(<CalorieRing consumed={1500} goal={2000} />);
  expect(screen.getByTestId('calorie-percentage')).toHaveTextContent('75%');
  expect(screen.getByTestId('remaining-label')).toHaveTextContent('500 kcal left');
});

// Test food search with mocked API:
it('searches food and displays results', async () => {
  server.use(rest.get('/api/v1/foods/search', (req, res, ctx) =>
    res(ctx.json([{ id: '1', nameEn: 'Oatmeal', caloriesPer100g: 389 }]))
  ));
  render(<FoodSearchBar />);
  await userEvent.type(screen.getByRole('searchbox'), 'oat');
  await waitFor(() => expect(screen.getByText('Oatmeal')).toBeInTheDocument());
});
```

**MSW (Mock Service Worker):** intercepts API calls at the network level in tests — same mocks reused for Storybook and Playwright E2E tests.

---

### E2E Testing (Playwright — Web)

```typescript
// Critical path: log a food via barcode scan
test('barcode scan creates diary entry', async ({ page }) => {
  await page.goto('/diary/add');
  await page.fill('[data-testid="barcode-input"]', '5449000000996');  // Coca-Cola barcode
  await page.click('[data-testid="barcode-lookup-btn"]');
  await expect(page.locator('[data-testid="food-name"]')).toContainText('Coca-Cola');
  await page.fill('[data-testid="quantity-input"]', '330');
  await page.click('[data-testid="add-to-diary-btn"]');
  await expect(page.locator('[data-testid="diary-entry-row"]')).toContainText('Coca-Cola');
  await expect(page.locator('[data-testid="calorie-ring-consumed"]')).toContainText('139');
});
```

**Key E2E test scenarios:**
1. Register → set TDEE goal → log 3 meals → verify calorie ring fills correctly
2. Search food in Russian → results shown in Russian → log → diary shows Russian name
3. Upload food photo → AI recognizes 2 items → user edits quantity → confirm → diary entries created
4. Scan barcode → food not in DB → Open Food Facts finds it → diary entry created
5. Log food exceeding daily goal → push notification appears within 10 seconds

---

### iOS Testing (Detox)

```javascript
// Detox E2E test for barcode scanner:
describe('Barcode Scanner', () => {
  it('should scan barcode and add food to diary', async () => {
    await element(by.id('add-food-tab')).tap();
    await element(by.id('barcode-scanner-btn')).tap();
    // Detox can inject mock camera frames
    await device.launchApp({ permissions: { camera: 'YES' } });
    await expect(element(by.id('food-name-label'))).toBeVisible();
    await element(by.id('confirm-add-btn')).tap();
    await expect(element(by.id('diary-entry-0'))).toBeVisible();
  });
});
```

---

### Test Data Strategy

```java
// TestDataFactory.java — shared test builders
public class TestDataFactory {
    public static Food oatmeal() {
        return Food.builder()
            .id(UUID.fromString("11111111-0000-0000-0000-000000000001"))
            .nameEn("Oatmeal").nameRu("Овсянка")
            .caloriesPer100g(389.0).proteinPer100g(16.9)
            .carbsPer100g(66.3).fatPer100g(6.9)
            .source(FoodSource.USDA).verified(true)
            .build();
    }

    public static DiaryEntry breakfastEntry(UUID userId) {
        return DiaryEntry.builder()
            .userId(userId).foodId(oatmeal().getId())
            .quantityG(80.0).mealType(MealType.BREAKFAST)
            .date(LocalDate.now()).calories(311.2)
            .build();
    }
}
```

---

## 18. Key User Journeys

> These are the **5 most critical flows** in the application. Trace each one end-to-end through all services — useful for understanding the system and for defining acceptance criteria.

---

### Journey 1: First-Time User Setup

```
Step 1: User opens web app → lands on /register
        → RegisterPage: enters email, password, selects language (EN/RU)
        → POST /api/v1/auth/register
        → auth-service: hash password (Argon2id), save user
        → Kafka: publish user.registered
        → auth-service: issue JWT, return accessToken

Step 2: user-service consumes user.registered → creates empty UserProfile row
        notification-service consumes user.registered → sends welcome email (EN or RU template)

Step 3: Frontend redirects to /profile
        → ProfilePage shows TDEE Calculator form (React Hook Form)
        → User enters: gender=MALE, age=28, height=182cm, weight=78kg, activity=MODERATE
        → POST /api/v1/users/me/tdee
        → user-service: Mifflin-St Jeor → TDEE = 2843 kcal
        → Response: { tdee: 2843, suggestedGoal: 2343 (500 deficit for weight loss) }
        → User sets goal type = LOSE_WEIGHT, accepts suggested 2343 kcal

Step 4: PUT /api/v1/users/me → saves goal
        → Dashboard now shows CalorieRing with goal = 2343, consumed = 0

Total services touched: auth-service, user-service, notification-service
Kafka events: user.registered
Time to complete: ~3 minutes for the user
```

---

### Journey 2: Log Food via Barcode (Most Common Action)

```
Step 1: User taps barcode icon in iOS app
        → expo-barcode-scanner activates camera
        → User points camera at product (e.g. Chobani Greek Yogurt, EAN: 0818290013015)
        → expo-barcode-scanner fires onBarcodeScanned callback with { type, data: "0818290013015" }

Step 2: GET /api/v1/foods/barcode/0818290013015
        → food-service BarcodeService:
          ① Check barcode_cache (miss — first lookup)
          ② Call Open Food Facts: GET https://world.openfoodfacts.org/api/v0/product/0818290013015.json
          ③ OFF returns product with nutrition facts
          ④ Map OFF response → Food entity → save to foods table
          ⑤ Save to barcode_cache
          ⑥ Publish food.indexed Kafka event (async embedding will happen)
          ⑦ Return FoodDto to client

Step 3: iOS shows FoodDetailScreen with:
        - Name: "Chobani Greek Yogurt 0% Fat"
        - Calories: 59 kcal per 100g
        - Quantity input pre-set to serving size: 150g (= 88.5 kcal)
        - Meal type selector: BREAKFAST (default based on time of day)

Step 4: User taps "Add to Diary"
        → POST /api/v1/diary/entries { foodId, quantityG: 150, mealType: BREAKFAST, date: today }
        → diary-service:
          ① Calls food-service REST GET /foods/{foodId} → get fresh nutrition snapshot
          ② Computes: calories = 150/100 * 59 = 88.5 kcal
          ③ Saves diary_entry row with nutrition snapshot
          ④ Publishes diary.entry.created Kafka event
          ⑤ Returns DiaryEntryDto

Step 5: Kafka consumers react:
        → analytics-service: UPDATE daily_summaries SET total_calories += 88.5 WHERE user_id=? AND date=today
        → notification-service: check if (88.5 + previousTotal) > dailyGoal → not yet → no alert

Step 6: iOS:
        → TanStack Query invalidates ['diary', today] and ['analytics', 'summary', today]
        → CalorieRing re-renders: consumed updated
        → Haptic feedback fires (Haptics.notificationAsync SUCCESS)

Total services: api-gateway, food-service, diary-service, analytics-service, notification-service
Kafka events: food.indexed, diary.entry.created
Time from scan to diary update: ~2 seconds
```

---

### Journey 3: AI Food Photo Recognition (Showpiece Feature)

```
Step 1: User taps camera icon on AddFoodPage
        → FoodCamera.tsx opens expo-camera full-screen
        → User photographs their lunch plate (pasta + salad)
        → expo-image-manipulator resizes to 1024×1024, compresses to JPEG

Step 2: POST /api/v1/ai/food/recognize (multipart, Content-Type: multipart/form-data)
        → api-gateway routes to ai-service
        → ai-service:
          ① Stores image in MinIO: bucket=food-photos, key=userId/requestId.jpg
          ② Launches CompletableFuture.supplyAsync():
             a) ImagePreprocessor: resize + Base64 encode
             b) Build multimodal prompt (load food-recognition.st template, inject language=en)
             c) Spring AI ChatClient with llava:7b + image message
             d) llava:7b inference (10–30 seconds)
             e) BeanOutputConverter parses JSON: [{name, weightG, calories, confidence}]
             f) For each item: call food-service vector search to find DB match
          ③ Returns immediately: { requestId: "uuid-abc" }

Step 3: iOS frontend:
        → Shows "Analyzing your meal..." skeleton screen
        → SSE EventSource already connected to /notifications/stream
        → After 15 seconds: SSE event arrives:
          { type: "AI_RECOGNITION_COMPLETE", requestId: "uuid-abc",
            results: [
              { name: "Pasta Carbonara", weightG: 250, calories: 430, confidence: 0.82, foodId: "food-uuid-1" },
              { name: "Caesar Salad",    weightG: 120, calories: 180, confidence: 0.71, foodId: null }
            ]}

Step 4: RecognitionResultCards modal appears:
        → Card 1: "Pasta Carbonara · 250g · 430 kcal" ← editable quantity
        → Card 2: "Caesar Salad · 120g · 180 kcal ⚠️ AI estimated" ← no DB match, show warning
        → User edits Card 1 quantity to 200g → calories update to 344 kcal in real time
        → User taps "Confirm All"

Step 5: POST /api/v1/diary/entries/bulk
        → diary-service creates 2 entries
        → Publishes 2 × diary.entry.created events
        → CalorieRing updates: +344 + 180 = +524 kcal

Total services: api-gateway, ai-service, food-service, diary-service, analytics-service
Kafka events: ai.food.recognized, diary.entry.created × 2
Async duration: 10–30 seconds (llava inference)
```

---

### Journey 4: Natural Language Food Logging in Russian

```
Step 1: User (language = RU) types in NlInputBox:
        "Сегодня на обед я ел борщ 300г и хлеб 2 куска"
        ("For lunch today I had 300g borscht and 2 slices of bread")

Step 2: POST /api/v1/ai/food/parse-text { text: "Сегодня на обед...", language: "ru" }
        → Returns immediately: { requestId: "uuid-xyz" }
        → Async pipeline starts:

Step 3: RagPipeline executes:
        ① LanguageDetector: Cyrillic chars > 80% → language = "ru"
        ② EmbeddingService: embed "Сегодня на обед я ел борщ 300г и хлеб 2 куска" → float[768]
        ③ food-service VectorSearch: top 15 foods ordered by cosine similarity:
           [борщ/borscht (0.94), хлеб/bread (0.91), ржаной хлеб/rye bread (0.88), ...]
        ④ PromptTemplateEngine: loads nl-food-parse.st, injects:
           - userText = "Сегодня на обед я ел борщ 300г и хлеб 2 куска"
           - contextFoods = [{id:"b-uuid", nameRu:"Борщ", caloriesPer100g:45}, ...]
           - language = "Russian"
        ⑤ llama3.1:8b inference (~5 seconds):
           Returns: [
             { foodId: "b-uuid", foodName: "Борщ", quantityG: 300, mealType: "LUNCH" },
             { foodId: "h-uuid", foodName: "Хлеб пшеничный", quantityG: 60, mealType: "LUNCH" }
           ]
           (model correctly interprets "2 куска" ≈ 60g based on standard slice weight)

Step 4: SSE event: AI_NL_PARSE_COMPLETE → ParsedFoodPreview modal:
        - "Борщ · 300г · 135 ккал"    ← matched to DB food
        - "Хлеб пшеничный · 60г · 153 ккал"   ← matched to DB food
        → User confirms → POST /diary/entries/bulk

Total services: api-gateway, ai-service, food-service, diary-service, analytics-service
Kafka events: diary.entry.created × 2
LLM inference: ~5 seconds (llama3.1:8b text only)
```

---

### Journey 5: Weekly Digest Email (Automated, No User Action)

```
Monday 8:00 AM (user's timezone: Europe/Moscow = UTC+3):
→ notification-service MealReminderScheduler fires @Scheduled every minute
→ Detects: weeklyDigest due for userId "u-123" (language = "ru")

Step 1: notification-service publishes analytics.report.requested Kafka event
        → analytics-service consumer: compute weekly stats:
          { avgDailyCalories: 1920, avgProtein: 98g, weightDelta: -0.3kg, streak: 5, weekStart: "2026-03-23" }
        → analytics-service publishes analytics.report.ready event with stats

Step 2: ai-service consumes analytics.report.ready:
        ① Load weekly-digest.st prompt
        ② Inject stats + language="Russian"
        ③ llama3.1:8b generates:
           "На этой неделе вы потребляли в среднем 1920 ккал в день, что соответствует вашей цели.
            Вы снизили вес на 0.3 кг. Ваша серия составляет 5 дней подряд — отличная работа!
            Попробуйте увеличить потребление белка: сейчас 98г, рекомендуется 120г."
        ④ Publishes notification.email.send Kafka event with digest text + userId

Step 3: notification-service consumes notification.email.send:
        → Looks up user email + language preference
        → Selects email_weekly_digest_ru.html template
        → Injects AI digest text
        → SendGrid API: sends email

Total services: notification-service, analytics-service, ai-service, notification-service
Kafka events: analytics.report.requested → analytics.report.ready → notification.email.send
User experience: opens email on Monday morning, reads personalized Russian summary
```

---

## 19. Performance & Scalability

### Database Query Optimization

**HikariCP connection pool tuning** (per service `application.yml`):
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10          # Start small; increase if connection waits appear
      minimum-idle: 2
      connection-timeout: 30000      # 30s max wait for connection
      idle-timeout: 600000           # Release idle connections after 10 min
      max-lifetime: 1800000          # Recycle connections every 30 min
      leak-detection-threshold: 60000 # Warn if connection held > 60s
```

**Slow query detection — critical indexes to verify:**
```sql
-- diary-service: most common query — get all entries for a user+date
EXPLAIN ANALYZE
SELECT * FROM diary_entries WHERE user_id = ? AND date = ?;
-- Must use: idx_diary_user_date (bitmap index scan, not seq scan)

-- food-service: semantic search with user filter
EXPLAIN ANALYZE
SELECT food_id FROM food_embeddings
WHERE (user_id IS NULL OR user_id = ?)
ORDER BY embedding <=> ?::vector LIMIT 20;
-- Must use: idx_food_embeddings_vector (HNSW index scan)
-- If sequential scan: check pgvector.hnsw.ef_search parameter
```

**N+1 query prevention:**
```java
// BAD — N+1: loads diary entries then queries food name per entry:
diaryEntries.forEach(e -> e.setFoodName(foodService.getById(e.getFoodId()).getNameEn()));

// GOOD — snapshot pattern: name is already stored in diary_entry row
// (this is why we snapshot food name and nutrition at log time)
diaryEntries.stream().map(DiaryEntryDto::from).collect(toList());
// Zero additional queries!
```

---

### Caching Strategy (Multi-Layer)

```
Layer 1: Browser cache (React)
  TanStack Query staleTime:
    - Daily diary entries:    30 seconds (changes frequently)
    - Food search results:    5 minutes  (changes rarely)
    - User profile/goals:     10 minutes (changes very rarely)
    - Analytics trends:       5 minutes  (Kafka updates async anyway)

Layer 2: Redis (server-side)
  Key pattern + TTL:
    - food:barcode:{ean}            → 30 days   (barcode data rarely changes)
    - food:search:{hash(query)}     → 1 hour    (search results stable)
    - ai:suggest:{userId}:{date}    → 2 hours   (regenerating LLM is expensive)
    - ai:insight:{userId}:{month}   → 6 hours   (monthly insight stable)
    - user:profile:{userId}         → 10 minutes (low-change data)

Layer 3: pgvector HNSW index
  Configured ef_search at query time based on precision need:
    - Food search (user-facing): ef_search=40  (higher recall)
    - AI internal context retrieval: ef_search=20 (speed over recall)
```

**Spring `@Cacheable` on food-service:**
```java
@Service
public class FoodService {
    @Cacheable(value = "food:barcode", key = "#barcode", unless = "#result == null")
    public Optional<FoodDto> findByBarcode(String barcode) {
        return barcodeService.lookup(barcode);  // only called on cache miss
    }

    @CacheEvict(value = "food:search", allEntries = true)
    public FoodDto createFood(CreateFoodRequest req) { ... }  // invalidates search cache
}
```

---

### Kafka Consumer Lag Monitoring

**Consumer lag** = the difference between the latest message offset in a topic and the offset the consumer has processed. High lag = a service is falling behind.

Alert thresholds (set in Prometheus):
```yaml
# prometheus/alerts.yml
- alert: KafkaConsumerLagHigh
  expr: kafka_consumer_lag{group="analytics-service", topic="diary.entry.created"} > 100
  for: 5m
  annotations:
    summary: "Analytics service is 100+ diary events behind"
```

---

### Virtual Threads (Java 21+ / Project Loom)

All services enable virtual threads via:
```yaml
spring:
  threads:
    virtual:
      enabled: true
```

**Why it matters for this app:**
- Every Ollama AI call blocks the thread for 5–30 seconds waiting for inference
- With platform threads (default): 200 blocked threads = 200 × 1MB stack = 200 MB RAM wasted
- With virtual threads: 200 blocked virtual threads = ~few KB total (OS thread freed while waiting)
- Result: ai-service handles 100× more concurrent AI requests without scaling horizontally

---

### Horizontal Scaling Considerations

Services that can scale horizontally (stateless):
```
api-gateway       ← multiple instances behind load balancer; Eureka handles registration
food-service      ← stateless; pgvector queries are read-heavy
diary-service     ← stateless; Kafka partitioning by userId ensures ordering
analytics-service ← stateless; Kafka consumer group auto-rebalances partitions

Services that need sticky sessions or can't easily scale:
notification-service ← SSE emitters stored in-memory ConcurrentHashMap
  Mitigation: move emitter registry to Redis pub/sub → any instance can push to any user
ai-service         ← Ollama is the bottleneck, not the Spring app; scale Ollama instead
```

---

## 20. UI/UX Design System

### Color Palette (Bootstrap CSS Variables)

```scss
// web/src/styles/_variables.scss — overrides Bootstrap defaults
:root {
  // Brand colors
  --bs-primary:         #2ECC71;   // Calorie green — "on track"
  --bs-primary-rgb:     46, 204, 113;
  --bs-secondary:       #3498DB;   // Info blue
  --bs-success:         #27AE60;   // Goal achieved
  --bs-warning:         #F39C12;   // Approaching limit (80–100%)
  --bs-danger:          #E74C3C;   // Exceeded goal
  --bs-dark:            #2C3E50;   // Sidebar background
  --bs-body-bg:         #F8F9FA;   // Page background (light mode)

  // Macro colors (used in rings and bars)
  --macro-protein:      #E74C3C;   // Red
  --macro-carbs:        #F39C12;   // Orange
  --macro-fat:          #3498DB;   // Blue
  --macro-fiber:        #27AE60;   // Green

  // Calorie ring states
  --ring-safe:          #2ECC71;   // 0–79% of goal
  --ring-warning:       #F39C12;   // 80–99% of goal
  --ring-exceeded:      #E74C3C;   // 100%+ of goal
}

[data-bs-theme="dark"] {
  --bs-body-bg:         #1A1A2E;
  --bs-body-color:      #E8E8E8;
  --bs-dark:            #16213E;
  --bs-card-bg:         #0F3460;
}
```

---

### Typography

```scss
// Font stack — system fonts first (no loading delay)
--bs-font-sans-serif: 'Inter', -apple-system, BlinkMacSystemFont,
                      'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
--bs-font-size-base:  0.9375rem;  // 15px (slightly tighter than Bootstrap's 16px)

// Russian text note: Inter has excellent Cyrillic support — no fallback needed
```

---

### Component Design Conventions

**CalorieRing — the hero component:**
```
Outer ring:  total consumed / goal (colour-coded by state)
Inner text:  consumed kcal (large, bold)
Below text:  "X kcal remaining" or "X kcal over" in red
Size:        160px diameter on desktop, 120px on mobile
Animation:   CSS transition 0.5s ease on arc length change
```

**MacroProgressBar:**
```
[Protein ████████░░░░] 98g / 150g  (65%)
[Carbs   ██████░░░░░░] 180g / 270g (67%)
[Fat     █████████░░░] 58g / 75g   (77%)

Color: each macro has its own color (see palette above)
Shows: grams consumed / goal, percentage, Bootstrap progress bar
```

**MealAccordion — diary view:**
```
▼ BREAKFAST  (7:30 AM)                    430 kcal
  🥣 Oatmeal         80g    312 kcal    [edit] [×]
  🥛 Whole milk     200ml   122 kcal    [edit] [×]
▶ LUNCH      (1:00 PM)                    620 kcal
▶ DINNER     (7:00 PM)                    0 kcal      ← empty, collapsed
▶ SNACKS                                  90 kcal
```

**Mobile bottom tab bar:**
```
[🏠 Today] [📖 Diary] [➕ Add] [📈 Stats] [👤 Profile]
                        ↑
              Large central FAB (Floating Action Button)
              Taps open: Search / Camera / Barcode / NL Input
```

---

### Responsive Breakpoints (Bootstrap)

| Breakpoint | Width | Layout changes |
|---|---|---|
| `xs` | < 576px | Single column, bottom tab bar, compact rings |
| `sm` | ≥ 576px | Two-column diary list |
| `md` | ≥ 768px | Sidebar collapses to icons-only |
| `lg` | ≥ 992px | Full sidebar with text labels |
| `xl` | ≥ 1200px | Dashboard shows 3 columns (diary + charts + AI suggestions) |

---

### Loading & Empty States

Every data-driven component has three states:

```
Loading:  Skeleton placeholders (Bootstrap placeholder animation)
          CalorieRing → grey circle skeleton
          DiaryEntry rows → 3 × grey bar skeletons

Empty:    Friendly illustration + CTA
          No diary entries yet → "📷 Add your first meal" button
          No favourite foods → "❤️ Tap ♡ on any food to save it here"

Error:    Error card with retry button
          AI unavailable → "🤖 AI is thinking... try again in a moment"
          Network error → "📶 No connection — your changes will sync when back online"
```

---

### Form Design Rules

- All forms use React Hook Form + Zod (never uncontrolled inputs)
- Validation errors shown inline below the field (not as modal alerts)
- Submit button shows loading spinner during API call, disabled to prevent double-submit
- Quantity inputs: always show unit suffix (`g` / `ml`) inside the input field
- Date pickers: `react-datepicker` on web, `@react-native-community/datetimepicker` on iOS
- All form labels and errors use `useTranslation()` — never hardcoded English strings

---

## 21. Error Handling & Resilience Strategy

### HTTP Error Response Format

All services return a consistent error body (enforced by `GlobalExceptionHandler.java` in each service):

```json
{
  "timestamp": "2026-03-29T10:30:00Z",
  "status": 422,
  "error": "VALIDATION_FAILED",
  "message": "Quantity must be between 1 and 5000 grams",
  "messageRu": "Количество должно быть от 1 до 5000 граммов",
  "field": "quantityG",
  "traceId": "abc123def456",
  "service": "diary-service"
}
```

**Key fields:**
- `error`: machine-readable error code (frontend maps to icons/actions)
- `message` + `messageRu`: both languages always returned (frontend picks based on user language)
- `traceId`: Zipkin trace ID — paste into Zipkin UI to see full request journey
- `service`: which microservice threw the error

---

### Error Code Taxonomy

| Code | HTTP Status | Meaning | Frontend Action |
|---|---|---|---|
| `VALIDATION_FAILED` | 422 | Input validation error | Show inline field error |
| `FOOD_NOT_FOUND` | 404 | Food ID doesn't exist | Show "Food not found" toast |
| `BARCODE_NOT_FOUND` | 404 | Barcode not in any database | Show "Unknown product — add manually" |
| `AI_UNAVAILABLE` | 503 | Ollama is down / circuit open | Show "AI unavailable, try again later" |
| `AI_PARSE_FAILED` | 422 | LLM output couldn't be parsed | Show "Couldn't understand that, try rephrasing" |
| `RATE_LIMITED` | 429 | Too many requests | Show "Too many requests, wait X seconds" with countdown |
| `UNAUTHORIZED` | 401 | Token expired/invalid | Trigger silent refresh → retry |
| `FORBIDDEN` | 403 | Insufficient role | Show "Access denied" |
| `SERVICE_UNAVAILABLE` | 503 | Downstream service down | Show generic "Something went wrong, retrying..." |

---

### AI Fallback Chain

Every AI feature has a defined fallback so the app never completely breaks when Ollama is down:

```
Food Photo Recognition:
  Primary:   llava:7b recognition → structured food list
  Fallback1: If confidence < 0.4 on all items → return empty list + show "Couldn't identify foods"
  Fallback2: Circuit open (Ollama down) → return empty list + show "AI unavailable" banner
  User experience: App stays functional — user adds foods manually

NL Food Parsing:
  Primary:   RAG pipeline → llama3.1:8b → parsed food items
  Fallback1: LLM output parse fails → return raw LLM text + "We couldn't structure this, try again"
  Fallback2: Circuit open → skip NL, show manual food search

Meal Suggestions:
  Primary:   vector search + llama3.1:8b → 3 meal ideas
  Fallback1: LLM unavailable → return top 5 foods by macro fit score only (no LLM description)
  Fallback2: vector search fails → return user's 5 most-logged foods for the meal type
  User experience: Suggestions always appear (may be simpler without LLM)

Weekly Digest:
  Primary:   llama3.1:8b → personalized paragraph
  Fallback:  Template-based email (no LLM) with just the raw stats formatted
  User experience: Email always arrives on Monday; sometimes AI-generated, sometimes template
```

---

### Retry Budget on Frontend (Axios)

```typescript
// client.ts — don't retry forever
const retryConfig = {
  retries: 2,
  retryDelay: (retryCount: number) => Math.pow(2, retryCount) * 1000,  // 1s, 2s
  retryCondition: (error: AxiosError) => {
    // Only retry network errors and 503 (service temporarily down)
    // Never retry 400/401/403/404/422 — those are client errors, retrying won't help
    return !error.response || error.response.status === 503;
  }
};
```

---

### Circuit Breaker States Monitoring

Expose Resilience4j circuit breaker states via Actuator → Prometheus → Grafana:
```yaml
management.endpoint.health.show-details: always
management.health.circuitbreakers.enabled: true

# Grafana panel: circuit breaker state
# metric: resilience4j_circuitbreaker_state{name="ollama"}
# values: 0=CLOSED (healthy), 1=OPEN (failing), 2=HALF_OPEN (testing)
```

Alert in Prometheus: `alert if ollama circuit breaker state = OPEN for > 5 minutes`

---

## 22. Glossary

### Nutrition Domain Terms

| Term | Definition |
|---|---|
| **Calorie (kcal)** | Unit of food energy. 1 kcal = 4.184 kJ. In common use "calorie" means kilocalorie. |
| **Macronutrient** | The three main nutrients providing energy: Protein (4 kcal/g), Carbohydrates (4 kcal/g), Fat (9 kcal/g) |
| **Micronutrient** | Vitamins and minerals (not tracked in this v1 app) |
| **TDEE** | Total Daily Energy Expenditure — the total calories your body burns in a day including activity |
| **BMR** | Basal Metabolic Rate — calories burned at complete rest (keeping organs alive) |
| **Mifflin-St Jeor** | Most accurate BMR formula for general population (used in this app) |
| **Calorie deficit** | Consuming fewer calories than TDEE → body burns stored fat → weight loss |
| **Calorie surplus** | Consuming more calories than TDEE → body stores energy → weight gain |
| **Macro split** | The percentage of daily calories from each macronutrient (e.g. 40% carbs, 30% protein, 30% fat) |
| **50/30/20 rule** | Budget rule applied to nutrition: 50% calories from carbs, 30% protein, 20% fat |
| **EAN barcode** | European Article Number — the 8 or 13-digit barcode on packaged food products |
| **Serving size** | Manufacturer's suggested portion (e.g. "1 cup / 240ml") — stored as `serving_size_g` |
| **Fibre / Dietary fibre** | Indigestible carbohydrates; has health benefits; some apps subtract fibre from carb count ("net carbs") |

---

### Technical Terms

| Term | Definition |
|---|---|
| **Embedding** | A list of floating-point numbers representing text in a high-dimensional vector space. Similar texts have similar (close) vectors. |
| **pgvector** | PostgreSQL extension that stores vectors and supports similarity search with distance operators |
| **HNSW** | Hierarchical Navigable Small World — graph-based index for fast approximate nearest-neighbour vector search |
| **Cosine similarity** | Measures the angle between two vectors (1 = identical direction, 0 = perpendicular). Used for text embeddings because magnitude doesn't matter. |
| **RAG** | Retrieval-Augmented Generation — an AI pattern that retrieves relevant context from a database before generating a response, grounding the LLM in real data |
| **LLM** | Large Language Model — a neural network trained on text that can generate, summarise, translate, and reason about language (e.g. `llama3.1:8b`) |
| **Ollama** | Tool for running LLMs locally on your machine using quantized GGUF model files |
| **GGUF** | File format for quantized LLM weights (successor to GGML). Quantized models use 4–8 bits per weight instead of 32 bits → smaller, faster, slight quality loss |
| **Quantization** | Reducing the precision of model weights (e.g. from float32 to int4) to reduce model size and memory usage |
| **Spring AI** | Spring Framework's official abstraction layer for AI/LLM integration — provides `ChatClient`, `EmbeddingModel`, `VectorStore` interfaces |
| **Kafka offset** | Position of a message in a Kafka partition log. Consumers track their offset to know which messages they've processed |
| **Consumer group** | A set of Kafka consumers that share message consumption from a topic — Kafka distributes partitions between group members |
| **Circuit breaker** | Fault-tolerance pattern: after N failures, "opens" the circuit and returns fallback immediately instead of calling the failing service |
| **Distributed tracing** | Tracking a single request as it passes through multiple services, using a shared Trace ID propagated via HTTP headers |
| **JWT** | JSON Web Token — compact, self-contained token encoding claims (userId, role, expiry), cryptographically signed |
| **Argon2id** | Memory-hard password hashing algorithm — resistant to GPU brute-force attacks |
| **TOTP** | Time-based One-Time Password (RFC 6238) — 6-digit code generated every 30s using a shared secret and current time |
| **Eureka** | Netflix's service registry — services register themselves by name; other services look up names to find addresses |
| **API Gateway** | Single entry point for all client traffic — handles routing, auth, rate limiting, and CORS |
| **Testcontainers** | Java library that starts real Docker containers (PostgreSQL, Kafka, Redis) during automated tests |
| **SSE** | Server-Sent Events — one-directional, long-lived HTTP connection where the server pushes events to the client |
| **EAS** | Expo Application Services — Expo's cloud build and deployment service for React Native apps |

---

*Estimated total effort: ~18 weeks solo (AI + microservices learning curve)*
*Recommended start: Phase 1 infrastructure skeleton — `./gradlew :infrastructure:eureka-server:bootRun` and watch all services discover each other.* 🚀


#!/usr/bin/env python3
"""One-shot script to generate all infrastructure skeleton files for calorie-tracker."""
import os

BASE = "/Users/uladzislau/IdeaProjects/calorie-tracker"

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"  created: {path}")

# ────────────────────────────────────────────────────────────────────────────
# Service build.gradle.kts files
# ────────────────────────────────────────────────────────────────────────────

COMMON = """\
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
    implementation("org.springframework.cloud:spring-cloud-starter-netflix-eureka-client")
    implementation("org.springframework.kafka:spring-kafka")
    runtimeOnly("org.postgresql:postgresql")
    implementation("org.flywaydb:flyway-database-postgresql")
    implementation("io.micrometer:micrometer-registry-prometheus")
    implementation("io.micrometer:micrometer-tracing-bridge-brave")
    implementation("io.zipkin.reporter2:zipkin-reporter-brave")
    testImplementation("org.testcontainers:postgresql")
    testImplementation("org.testcontainers:kafka")
    testImplementation("org.springframework.security:spring-security-test")"""

def svc_gradle(name, extra=""):
    return (
        'plugins {\n'
        '    id("org.springframework.boot")\n'
        '    id("com.google.cloud.tools.jib")\n'
        '}\n\n'
        'dependencies {\n'
        + COMMON + "\n"
        + (extra or "")
        + '}\n\n'
        'jib {\n'
        '    from { image = "eclipse-temurin:21-jre-alpine" }\n'
        '    to   { image = "ghcr.io/VladByPinsk/calorie-tracker/' + name + ':${project.version}" }\n'
        '}\n'
    )

w("services/user-service/build.gradle.kts", svc_gradle("user-service"))

w("services/food-service/build.gradle.kts", svc_gradle(
    "food-service",
    '    implementation("org.springframework.ai:spring-ai-pgvector-store-spring-boot-starter")\n'
    '    implementation("org.springframework.boot:spring-boot-starter-data-redis")\n'
))

w("services/diary-service/build.gradle.kts", svc_gradle("diary-service"))

w("services/analytics-service/build.gradle.kts", svc_gradle("analytics-service"))

w("services/notification-service/build.gradle.kts", svc_gradle(
    "notification-service",
    '    implementation("org.springframework.boot:spring-boot-starter-mail")\n'
    '    implementation("org.springframework.boot:spring-boot-starter-websocket")\n'
))

w("services/ai-service/build.gradle.kts",
    'plugins {\n'
    '    id("org.springframework.boot")\n'
    '    id("com.google.cloud.tools.jib")\n'
    '}\n\n'
    'dependencies {\n'
    '    implementation("org.springframework.boot:spring-boot-starter-web")\n'
    '    implementation("org.springframework.boot:spring-boot-starter-security")\n'
    '    implementation("org.springframework.boot:spring-boot-starter-validation")\n'
    '    implementation("org.springframework.boot:spring-boot-starter-actuator")\n'
    '    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")\n'
    '    implementation("org.springframework.cloud:spring-cloud-starter-netflix-eureka-client")\n'
    '    implementation("org.springframework.kafka:spring-kafka")\n'
    '    implementation("org.springframework.boot:spring-boot-starter-data-redis")\n'
    '    implementation("org.springframework.ai:spring-ai-ollama-spring-boot-starter")\n'
    '    implementation("org.springframework.ai:spring-ai-pgvector-store-spring-boot-starter")\n'
    '    implementation("io.minio:minio:8.5.14")\n'
    '    implementation("io.micrometer:micrometer-registry-prometheus")\n'
    '    implementation("io.micrometer:micrometer-tracing-bridge-brave")\n'
    '    implementation("io.zipkin.reporter2:zipkin-reporter-brave")\n'
    '    testImplementation("org.springframework.boot:spring-boot-starter-test")\n'
    '    testImplementation("org.testcontainers:postgresql")\n'
    '    testImplementation("org.testcontainers:kafka")\n'
    '}\n\n'
    'jib {\n'
    '    from { image = "eclipse-temurin:21-jre-alpine" }\n'
    '    to   { image = "ghcr.io/VladByPinsk/calorie-tracker/ai-service:${project.version}" }\n'
    '}\n'
)

# ────────────────────────────────────────────────────────────────────────────
# Application stubs (main classes + application.yml)
# ────────────────────────────────────────────────────────────────────────────

SERVICES = [
    ("auth-service",         "auth",         "AuthServiceApplication",         8081),
    ("user-service",         "user",         "UserServiceApplication",         8082),
    ("food-service",         "food",         "FoodServiceApplication",         8083),
    ("diary-service",        "diary",        "DiaryServiceApplication",        8084),
    ("ai-service",           "ai",           "AiServiceApplication",           8085),
    ("analytics-service",    "analytics",    "AnalyticsServiceApplication",    8086),
    ("notification-service", "notification", "NotificationServiceApplication", 8087),
]

GATEWAY_ROUTES = {
    "auth-service":         8081,
    "user-service":         8082,
    "food-service":         8083,
    "diary-service":        8084,
    "ai-service":           8085,
    "analytics-service":    8086,
    "notification-service": 8087,
}

for svc, pkg, cls, port in SERVICES:
    java_pkg = f"com.calorietracker.{pkg}"
    java_path = f"services/{svc}/src/main/java/com/calorietracker/{pkg}/{cls}.java"
    w(java_path,
        f"package {java_pkg};\n\n"
        "import org.springframework.boot.SpringApplication;\n"
        "import org.springframework.boot.autoconfigure.SpringBootApplication;\n\n"
        "@SpringBootApplication\n"
        f"public class {cls} {{\n"
        f"    public static void main(String[] args) {{\n"
        f"        SpringApplication.run({cls}.class, args);\n"
        "    }\n"
        "}\n"
    )

    w(f"services/{svc}/src/main/resources/application.yml",
        f"spring:\n"
        f"  application:\n"
        f"    name: {svc}\n"
        f"  config:\n"
        f"    import: optional:configserver:http://localhost:8888\n"
        f"  datasource:\n"
        f"    url: jdbc:postgresql://localhost:5432/{pkg}_db\n"
        f"    username: calorietracker\n"
        f"    password: ${{DB_PASSWORD}}\n"
        f"  jpa:\n"
        f"    hibernate.ddl-auto: validate\n"
        f"  flyway:\n"
        f"    enabled: true\n"
        f"  kafka:\n"
        f"    bootstrap-servers: ${{KAFKA_BOOTSTRAP_SERVERS:localhost:9092}}\n"
        f"\n"
        f"server:\n"
        f"  port: {port}\n"
        f"\n"
        f"eureka:\n"
        f"  client:\n"
        f"    service-url:\n"
        f"      defaultZone: http://localhost:8761/eureka/\n"
        f"\n"
        f"management:\n"
        f"  endpoints.web.exposure.include: health,info,prometheus,metrics\n"
        f"  tracing.sampling.probability: 1.0\n"
        f"  zipkin.tracing.endpoint: http://localhost:9411/api/v2/spans\n"
    )

# ai-service doesn't have a DB datasource
ai_yml_path = "services/ai-service/src/main/resources/application.yml"
w(ai_yml_path,
    "spring:\n"
    "  application:\n"
    "    name: ai-service\n"
    "  config:\n"
    "    import: optional:configserver:http://localhost:8888\n"
    "  ai:\n"
    "    ollama:\n"
    "      base-url: ${SPRING_AI_OLLAMA_BASE_URL:http://localhost:11434}\n"
    "      chat.model: gemma3:12b\n"
    "      embedding.model: nomic-embed-text\n"
    "  data:\n"
    "    redis.host: localhost\n"
    "  kafka:\n"
    "    bootstrap-servers: ${KAFKA_BOOTSTRAP_SERVERS:localhost:9092}\n"
    "\n"
    "server:\n"
    "  port: 8085\n"
    "\n"
    "eureka:\n"
    "  client:\n"
    "    service-url:\n"
    "      defaultZone: http://localhost:8761/eureka/\n"
    "\n"
    "management:\n"
    "  endpoints.web.exposure.include: health,info,prometheus,metrics\n"
    "  tracing.sampling.probability: 1.0\n"
    "  zipkin.tracing.endpoint: http://localhost:9411/api/v2/spans\n"
)

# ────────────────────────────────────────────────────────────────────────────
# API Gateway main class + application.yml
# ────────────────────────────────────────────────────────────────────────────

w("services/api-gateway/src/main/java/com/calorietracker/gateway/ApiGatewayApplication.java",
    "package com.calorietracker.gateway;\n\n"
    "import org.springframework.boot.SpringApplication;\n"
    "import org.springframework.boot.autoconfigure.SpringBootApplication;\n\n"
    "@SpringBootApplication\n"
    "public class ApiGatewayApplication {\n"
    "    public static void main(String[] args) {\n"
    "        SpringApplication.run(ApiGatewayApplication.class, args);\n"
    "    }\n"
    "}\n"
)

routes_yaml = ""
for svc_name, svc_port in GATEWAY_ROUTES.items():
    prefix = svc_name.replace("-service", "")
    routes_yaml += (
        f"      - id: {svc_name}\n"
        f"        uri: lb://{svc_name}\n"
        f"        predicates:\n"
        f"          - Path=/api/v1/{prefix}/**\n"
        f"        filters:\n"
        f"          - StripPrefix=0\n"
    )

w("services/api-gateway/src/main/resources/application.yml",
    "spring:\n"
    "  application:\n"
    "    name: api-gateway\n"
    "  config:\n"
    "    import: optional:configserver:http://localhost:8888\n"
    "  cloud:\n"
    "    gateway:\n"
    "      routes:\n"
    + routes_yaml
    + "  data:\n"
    "    redis.host: localhost\n"
    "\n"
    "server:\n"
    "  port: 8080\n"
    "\n"
    "jwt:\n"
    "  secret: ${JWT_SECRET}\n"
    "\n"
    "eureka:\n"
    "  client:\n"
    "    service-url:\n"
    "      defaultZone: http://localhost:8761/eureka/\n"
    "\n"
    "management:\n"
    "  endpoints.web.exposure.include: health,info,prometheus,metrics\n"
    "  tracing.sampling.probability: 1.0\n"
    "  zipkin.tracing.endpoint: http://localhost:9411/api/v2/spans\n"
)

# ────────────────────────────────────────────────────────────────────────────
# Eureka server
# ────────────────────────────────────────────────────────────────────────────

w("infrastructure/eureka-server/src/main/java/com/calorietracker/eureka/EurekaServerApplication.java",
    "package com.calorietracker.eureka;\n\n"
    "import org.springframework.boot.SpringApplication;\n"
    "import org.springframework.boot.autoconfigure.SpringBootApplication;\n"
    "import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;\n\n"
    "@SpringBootApplication\n"
    "@EnableEurekaServer\n"
    "public class EurekaServerApplication {\n"
    "    public static void main(String[] args) {\n"
    "        SpringApplication.run(EurekaServerApplication.class, args);\n"
    "    }\n"
    "}\n"
)

w("infrastructure/eureka-server/src/main/resources/application.yml",
    "spring:\n"
    "  application:\n"
    "    name: eureka-server\n"
    "\n"
    "server:\n"
    "  port: 8761\n"
    "\n"
    "eureka:\n"
    "  instance.hostname: localhost\n"
    "  client:\n"
    "    register-with-eureka: false\n"
    "    fetch-registry: false\n"
    "    service-url.defaultZone: http://localhost:8761/eureka/\n"
    "\n"
    "management:\n"
    "  endpoints.web.exposure.include: health,info\n"
)

# ────────────────────────────────────────────────────────────────────────────
# Config server
# ────────────────────────────────────────────────────────────────────────────

w("infrastructure/config-server/src/main/java/com/calorietracker/config/ConfigServerApplication.java",
    "package com.calorietracker.config;\n\n"
    "import org.springframework.boot.SpringApplication;\n"
    "import org.springframework.boot.autoconfigure.SpringBootApplication;\n"
    "import org.springframework.cloud.config.server.EnableConfigServer;\n\n"
    "@SpringBootApplication\n"
    "@EnableConfigServer\n"
    "public class ConfigServerApplication {\n"
    "    public static void main(String[] args) {\n"
    "        SpringApplication.run(ConfigServerApplication.class, args);\n"
    "    }\n"
    "}\n"
)

w("infrastructure/config-server/src/main/resources/application.yml",
    "spring:\n"
    "  application:\n"
    "    name: config-server\n"
    "  cloud:\n"
    "    config:\n"
    "      server:\n"
    "        native:\n"
    "          search-locations: classpath:/config\n"
    "      # Switch to git backend in production:\n"
    "      # git:\n"
    "      #   uri: https://github.com/VladByPinsk/calorie-tracker-config\n"
    "  profiles.active: native\n"
    "\n"
    "server:\n"
    "  port: 8888\n"
    "\n"
    "eureka:\n"
    "  client:\n"
    "    service-url:\n"
    "      defaultZone: http://localhost:8761/eureka/\n"
)

# ────────────────────────────────────────────────────────────────────────────
# Docker: postgres init.sql
# ────────────────────────────────────────────────────────────────────────────

w("docker/postgres/init.sql",
    "-- Creates all service databases and enables pgvector extension\n\n"
    "CREATE DATABASE auth_db;\n"
    "CREATE DATABASE user_db;\n"
    "CREATE DATABASE food_db;\n"
    "CREATE DATABASE diary_db;\n"
    "CREATE DATABASE analytics_db;\n"
    "CREATE DATABASE notification_db;\n\n"
    "-- Enable pgvector in food_db (used for semantic food search)\n"
    r"\connect food_db" + "\n"
    "CREATE EXTENSION IF NOT EXISTS vector;\n\n"
    r"\connect auth_db" + "\n"
    "CREATE EXTENSION IF NOT EXISTS pgcrypto;\n\n"
    r"\connect user_db" + "\n"
    "CREATE EXTENSION IF NOT EXISTS pgcrypto;\n"
)

# ────────────────────────────────────────────────────────────────────────────
# Docker: docker-compose.yml (dev)
# ────────────────────────────────────────────────────────────────────────────

w("docker/docker-compose.yml",
    """version: '3.9'

name: calorie-tracker

services:

  # ── Spring Cloud Infrastructure ─────────────────────────────────────────────
  eureka:
    build:
      context: ..
      dockerfile: infrastructure/eureka-server/Dockerfile
    ports: ["8761:8761"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8761/actuator/health"]
      interval: 10s
      retries: 10

  config-server:
    build:
      context: ..
      dockerfile: infrastructure/config-server/Dockerfile
    ports: ["8888:8888"]
    depends_on:
      eureka: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/actuator/health"]
      interval: 10s
      retries: 10

  # ── Application Services ─────────────────────────────────────────────────────
  api-gateway:
    build:
      context: ..
      dockerfile: services/api-gateway/Dockerfile
    ports: ["8080:8080"]
    environment:
      JWT_SECRET: ${JWT_SECRET}
      SPRING_DATA_REDIS_HOST: redis
    depends_on:
      eureka: { condition: service_healthy }
      config-server: { condition: service_healthy }
      redis: { condition: service_healthy }

  auth-service:
    build:
      context: ..
      dockerfile: services/auth-service/Dockerfile
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      JWT_REFRESH_SECRET: ${JWT_REFRESH_SECRET}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SPRING_REDIS_HOST: redis
      GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
      GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
    depends_on:
      postgres: { condition: service_healthy }
      kafka: { condition: service_healthy }
      eureka: { condition: service_healthy }
      config-server: { condition: service_healthy }

  user-service:
    build:
      context: ..
      dockerfile: services/user-service/Dockerfile
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    depends_on:
      postgres: { condition: service_healthy }
      kafka: { condition: service_healthy }
      eureka: { condition: service_healthy }

  food-service:
    build:
      context: ..
      dockerfile: services/food-service/Dockerfile
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      USDA_API_KEY: ${USDA_API_KEY}
      SPRING_AI_OLLAMA_BASE_URL: http://ollama:11434
    depends_on:
      postgres: { condition: service_healthy }
      kafka: { condition: service_healthy }
      ollama: { condition: service_healthy }
      eureka: { condition: service_healthy }

  diary-service:
    build:
      context: ..
      dockerfile: services/diary-service/Dockerfile
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    depends_on:
      postgres: { condition: service_healthy }
      kafka: { condition: service_healthy }
      eureka: { condition: service_healthy }

  ai-service:
    build:
      context: ..
      dockerfile: services/ai-service/Dockerfile
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SPRING_AI_OLLAMA_BASE_URL: http://ollama:11434
      MINIO_ENDPOINT: http://minio:9000
      MINIO_USER: ${MINIO_USER}
      MINIO_PASSWORD: ${MINIO_PASSWORD}
      SPRING_DATA_REDIS_HOST: redis
    depends_on:
      ollama: { condition: service_healthy }
      kafka: { condition: service_healthy }
      minio: { condition: service_healthy }
      eureka: { condition: service_healthy }

  analytics-service:
    build:
      context: ..
      dockerfile: services/analytics-service/Dockerfile
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    depends_on:
      postgres: { condition: service_healthy }
      kafka: { condition: service_healthy }
      eureka: { condition: service_healthy }

  notification-service:
    build:
      context: ..
      dockerfile: services/notification-service/Dockerfile
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
      EXPO_PUSH_TOKEN_SECRET: ${EXPO_PUSH_TOKEN_SECRET}
    depends_on:
      postgres: { condition: service_healthy }
      kafka: { condition: service_healthy }
      eureka: { condition: service_healthy }

  # ── Data & Messaging ──────────────────────────────────────────────────────────
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: calorietracker
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U calorietracker"]
      interval: 5s
      retries: 10
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 5s
      retries: 10
    ports: ["6379:6379"]

  zookeeper:
    image: confluentinc/cp-zookeeper:7.7.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    healthcheck:
      test: ["CMD", "bash", "-c", "echo ruok | nc localhost 2181"]
      interval: 10s
      retries: 10

  kafka:
    image: confluentinc/cp-kafka:7.7.0
    ports: ["9092:9092"]
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_NUM_PARTITIONS: 3
    depends_on:
      zookeeper: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      retries: 10
      start_period: 30s

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    volumes: [minio_data:/data]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      retries: 10

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: [ollama_data:/root/.ollama]
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:11434/api/tags || exit 1"]
      interval: 15s
      retries: 10
      start_period: 60s

  # ── Observability ──────────────────────────────────────────────────────────────
  zipkin:
    image: openzipkin/zipkin:latest
    ports: ["9411:9411"]

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    ports: ["9090:9090"]
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on: [prometheus]

volumes:
  postgres_data:
  minio_data:
  ollama_data:
  grafana_data:
"""
)

# ────────────────────────────────────────────────────────────────────────────
# Docker: Prometheus config
# ────────────────────────────────────────────────────────────────────────────

w("docker/prometheus/prometheus.yml",
    "global:\n"
    "  scrape_interval: 15s\n"
    "  evaluation_interval: 15s\n\n"
    "scrape_configs:\n"
    "  - job_name: 'api-gateway'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['api-gateway:8080']\n\n"
    "  - job_name: 'auth-service'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['auth-service:8081']\n\n"
    "  - job_name: 'user-service'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['user-service:8082']\n\n"
    "  - job_name: 'food-service'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['food-service:8083']\n\n"
    "  - job_name: 'diary-service'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['diary-service:8084']\n\n"
    "  - job_name: 'ai-service'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['ai-service:8085']\n\n"
    "  - job_name: 'analytics-service'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['analytics-service:8086']\n\n"
    "  - job_name: 'notification-service'\n"
    "    metrics_path: /actuator/prometheus\n"
    "    static_configs:\n"
    "      - targets: ['notification-service:8087']\n"
)

# ────────────────────────────────────────────────────────────────────────────
# Docker: Ollama model pull script
# ────────────────────────────────────────────────────────────────────────────

w("docker/ollama/pull-models.sh",
    "#!/usr/bin/env bash\n"
    "# Run once after 'docker compose up ollama' to pull required AI models.\n"
    "# Total download: ~9 GB — run on a fast connection.\n"
    "set -euo pipefail\n\n"
    "CONTAINER=calorie-tracker-ollama-1\n\n"
    "echo '==> Pulling gemma3:12b (text generation + NL parsing)...'\n"
    "docker exec \"$CONTAINER\" ollama pull gemma3:12b\n\n"
    "echo '==> Pulling qwen3-vl:8b (food photo vision recognition)...'\n"
    "docker exec \"$CONTAINER\" ollama pull qwen3-vl:8b\n\n"
    "echo '==> Pulling nomic-embed-text (semantic food search embeddings)...'\n"
    "docker exec \"$CONTAINER\" ollama pull nomic-embed-text\n\n"
    "echo '==> All models pulled successfully.'\n"
    "docker exec \"$CONTAINER\" ollama list\n"
)

# ────────────────────────────────────────────────────────────────────────────
# Nginx config
# ────────────────────────────────────────────────────────────────────────────

w("docker/nginx/nginx.conf",
    "worker_processes auto;\n\n"
    "events { worker_connections 1024; }\n\n"
    "http {\n"
    "    include       mime.types;\n"
    "    default_type  application/octet-stream;\n"
    "    sendfile      on;\n"
    "    gzip          on;\n"
    "    gzip_types    text/plain text/css application/json application/javascript;\n\n"
    "    # Rate limiting\n"
    "    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;\n\n"
    "    upstream api_gateway {\n"
    "        server api-gateway:8080;\n"
    "    }\n\n"
    "    server {\n"
    "        listen 80;\n"
    "        server_name _;\n\n"
    "        # Redirect HTTP to HTTPS\n"
    "        return 301 https://$host$request_uri;\n"
    "    }\n\n"
    "    server {\n"
    "        listen 443 ssl http2;\n"
    "        server_name _;\n\n"
    "        ssl_certificate     /etc/nginx/certs/cert.pem;\n"
    "        ssl_certificate_key /etc/nginx/certs/key.pem;\n"
    "        ssl_protocols       TLSv1.2 TLSv1.3;\n"
    "        ssl_ciphers         HIGH:!aNULL:!MD5;\n\n"
    "        # React web app\n"
    "        location / {\n"
    "            root   /usr/share/nginx/html;\n"
    "            index  index.html;\n"
    "            try_files $uri $uri/ /index.html;  # SPA routing\n"
    "        }\n\n"
    "        # API proxy to Spring Cloud Gateway\n"
    "        location /api/ {\n"
    "            limit_req zone=api burst=50 nodelay;\n"
    "            proxy_pass         http://api_gateway;\n"
    "            proxy_set_header   Host $host;\n"
    "            proxy_set_header   X-Real-IP $remote_addr;\n"
    "            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;\n"
    "            proxy_set_header   X-Forwarded-Proto $scheme;\n"
    "            proxy_read_timeout 120s;\n"
    "        }\n"
    "    }\n"
    "}\n"
)

# ────────────────────────────────────────────────────────────────────────────
# .env.example
# ────────────────────────────────────────────────────────────────────────────

w(".env.example",
    "# Copy to .env and fill in your values — NEVER commit .env to git!\n\n"
    "# ─── Database ──────────────────────────────────────────────────────────────────\n"
    "DB_PASSWORD=change_me_strong_password\n\n"
    "# ─── Redis ─────────────────────────────────────────────────────────────────────\n"
    "REDIS_PASSWORD=change_me_redis_password\n\n"
    "# ─── JWT (generate with: openssl rand -hex 64) ─────────────────────────────────\n"
    "JWT_SECRET=generate_256_bit_random_hex\n"
    "JWT_REFRESH_SECRET=generate_another_256_bit_random_hex\n\n"
    "# ─── Encryption (generate with: openssl rand -hex 32) ──────────────────────────\n"
    "ENCRYPTION_KEY=generate_32_byte_aes_key_hex\n\n"
    "# ─── OAuth2 Google ─────────────────────────────────────────────────────────────\n"
    "GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com\n"
    "GOOGLE_CLIENT_SECRET=your-google-client-secret\n\n"
    "# ─── MinIO ─────────────────────────────────────────────────────────────────────\n"
    "MINIO_USER=minioadmin\n"
    "MINIO_PASSWORD=change_me_minio_password\n\n"
    "# ─── Email (SendGrid) ──────────────────────────────────────────────────────────\n"
    "SENDGRID_API_KEY=SG.your_sendgrid_api_key\n\n"
    "# ─── Expo Push Notifications ───────────────────────────────────────────────────\n"
    "EXPO_PUSH_TOKEN_SECRET=your_expo_push_secret\n\n"
    "# ─── External Food APIs (free) ─────────────────────────────────────────────────\n"
    "# Get free key at: https://api.nal.usda.gov\n"
    "USDA_API_KEY=your_usda_api_key\n"
    "# Open Food Facts needs no key\n\n"
    "# ─── Observability ─────────────────────────────────────────────────────────────\n"
    "GRAFANA_PASSWORD=admin\n\n"
    "# ─── Frontend (web/.env) ───────────────────────────────────────────────────────\n"
    "VITE_API_BASE_URL=http://localhost:8080\n"
    "VITE_DEFAULT_LANGUAGE=en\n\n"
    "# ─── Mobile (mobile/.env — Expo) ───────────────────────────────────────────────\n"
    "EXPO_PUBLIC_API_BASE_URL=http://localhost:8080\n"
)

# ────────────────────────────────────────────────────────────────────────────
# GitHub Actions CI
# ────────────────────────────────────────────────────────────────────────────

w(".github/workflows/ci.yml",
    "name: CI\n\n"
    "on:\n"
    "  push:\n"
    "    branches: ['**']\n"
    "  pull_request:\n"
    "    branches: [main, develop]\n\n"
    "env:\n"
    "  REGISTRY: ghcr.io\n"
    "  IMAGE_PREFIX: ghcr.io/vladbyPinsk/calorie-tracker\n\n"
    "jobs:\n\n"
    "  # ─── Lint & Test: Java services ────────────────────────────────────────────\n"
    "  test-services:\n"
    "    name: Test ${{ matrix.service }}\n"
    "    runs-on: ubuntu-latest\n"
    "    strategy:\n"
    "      fail-fast: false\n"
    "      matrix:\n"
    "        service:\n"
    "          - auth-service\n"
    "          - user-service\n"
    "          - food-service\n"
    "          - diary-service\n"
    "          - ai-service\n"
    "          - analytics-service\n"
    "          - notification-service\n"
    "          - api-gateway\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n\n"
    "      - name: Set up Java 21\n"
    "        uses: actions/setup-java@v4\n"
    "        with:\n"
    "          java-version: '21'\n"
    "          distribution: temurin\n"
    "          cache: gradle\n\n"
    "      - name: Run tests\n"
    "        run: ./gradlew :services:${{ matrix.service }}:test\n\n"
    "      - name: Build JAR\n"
    "        run: ./gradlew :services:${{ matrix.service }}:bootJar\n\n"
    "  # ─── Lint & Test: Web frontend ─────────────────────────────────────────────\n"
    "  test-web:\n"
    "    name: Test Web (React)\n"
    "    runs-on: ubuntu-latest\n"
    "    defaults:\n"
    "      run:\n"
    "        working-directory: web\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n\n"
    "      - uses: actions/setup-node@v4\n"
    "        with:\n"
    "          node-version: '22'\n"
    "          cache: npm\n"
    "          cache-dependency-path: web/package-lock.json\n\n"
    "      - run: npm ci\n"
    "      - run: npm run lint\n"
    "      - run: npm test -- --watchAll=false --passWithNoTests\n"
    "      - run: npm run build\n\n"
    "  # ─── Lint: Mobile (Expo) ────────────────────────────────────────────────────\n"
    "  test-mobile:\n"
    "    name: Test Mobile (Expo)\n"
    "    runs-on: ubuntu-latest\n"
    "    defaults:\n"
    "      run:\n"
    "        working-directory: mobile\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n\n"
    "      - uses: actions/setup-node@v4\n"
    "        with:\n"
    "          node-version: '22'\n"
    "          cache: npm\n"
    "          cache-dependency-path: mobile/package-lock.json\n\n"
    "      - run: npm ci\n"
    "      - run: npm run lint\n"
    "      - run: npx expo export --platform web\n\n"
    "  # ─── Docker Build & Push (only on main) ────────────────────────────────────\n"
    "  docker-push:\n"
    "    name: Docker Push ${{ matrix.service }}\n"
    "    runs-on: ubuntu-latest\n"
    "    needs: [test-services]\n"
    "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'\n"
    "    strategy:\n"
    "      matrix:\n"
    "        service:\n"
    "          - auth-service\n"
    "          - user-service\n"
    "          - food-service\n"
    "          - diary-service\n"
    "          - ai-service\n"
    "          - analytics-service\n"
    "          - notification-service\n"
    "          - api-gateway\n"
    "    permissions:\n"
    "      contents: read\n"
    "      packages: write\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n\n"
    "      - name: Set up Java 21\n"
    "        uses: actions/setup-java@v4\n"
    "        with:\n"
    "          java-version: '21'\n"
    "          distribution: temurin\n"
    "          cache: gradle\n\n"
    "      - name: Log in to GHCR\n"
    "        uses: docker/login-action@v3\n"
    "        with:\n"
    "          registry: ghcr.io\n"
    "          username: ${{ github.actor }}\n"
    "          password: ${{ secrets.GITHUB_TOKEN }}\n\n"
    "      - name: Build & push with Jib\n"
    "        run: ./gradlew :services:${{ matrix.service }}:jib\n"
    "          -Djib.to.auth.username=${{ github.actor }}\n"
    "          -Djib.to.auth.password=${{ secrets.GITHUB_TOKEN }}\n\n"
    "  # ─── Infrastructure services (eureka + config-server) ──────────────────────\n"
    "  test-infrastructure:\n"
    "    name: Test Infrastructure\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n\n"
    "      - name: Set up Java 21\n"
    "        uses: actions/setup-java@v4\n"
    "        with:\n"
    "          java-version: '21'\n"
    "          distribution: temurin\n"
    "          cache: gradle\n\n"
    "      - run: ./gradlew :infrastructure:eureka-server:bootJar\n"
    "      - run: ./gradlew :infrastructure:config-server:bootJar\n"
)

# ────────────────────────────────────────────────────────────────────────────
# GitHub branch protection setup script (GitHub CLI)
# ────────────────────────────────────────────────────────────────────────────

w("scripts/setup-branch-protection.sh",
    "#!/usr/bin/env bash\n"
    "# Sets up GitHub branch protection rules using GitHub CLI (gh).\n"
    "# Prerequisites: brew install gh && gh auth login\n"
    "set -euo pipefail\n\n"
    "REPO='VladByPinsk/calorie-tracker'\n\n"
    "echo '==> Setting up branch protection for: main'\n\n"
    "gh api \\\n"
    "  --method PUT \\\n"
    "  -H 'Accept: application/vnd.github+json' \\\n"
    "  /repos/${REPO}/branches/main/protection \\\n"
    "  --input - << 'JSON'\n"
    "{\n"
    '  "required_status_checks": {\n'
    '    "strict": true,\n'
    '    "contexts": [\n'
    '      "Test auth-service",\n'
    '      "Test user-service",\n'
    '      "Test food-service",\n'
    '      "Test diary-service",\n'
    '      "Test ai-service",\n'
    '      "Test analytics-service",\n'
    '      "Test notification-service",\n'
    '      "Test api-gateway",\n'
    '      "Test Web (React)",\n'
    '      "Test Mobile (Expo)",\n'
    '      "Test Infrastructure"\n'
    "    ]\n"
    "  },\n"
    '  "enforce_admins": true,\n'
    '  "required_pull_request_reviews": {\n'
    '    "dismiss_stale_reviews": true,\n'
    '    "require_code_owner_reviews": true,\n'
    '    "required_approving_review_count": 1,\n'
    '    "require_last_push_approval": true\n'
    "  },\n"
    '  "restrictions": null,\n'
    '  "allow_force_pushes": false,\n'
    '  "allow_deletions": false,\n'
    '  "block_creations": false,\n'
    '  "required_conversation_resolution": true,\n'
    '  "lock_branch": false,\n'
    '  "required_linear_history": true\n'
    "}\n"
    "JSON\n\n"
    "echo '==> Setting up branch protection for: develop'\n\n"
    "gh api \\\n"
    "  --method PUT \\\n"
    "  -H 'Accept: application/vnd.github+json' \\\n"
    "  /repos/${REPO}/branches/develop/protection \\\n"
    "  --input - << 'JSON'\n"
    "{\n"
    '  "required_status_checks": {\n'
    '    "strict": true,\n'
    '    "contexts": [\n'
    '      "Test auth-service",\n'
    '      "Test user-service",\n'
    '      "Test food-service",\n'
    '      "Test diary-service",\n'
    '      "Test ai-service",\n'
    '      "Test analytics-service",\n'
    '      "Test notification-service",\n'
    '      "Test api-gateway",\n'
    '      "Test Web (React)",\n'
    '      "Test Mobile (Expo)"\n'
    "    ]\n"
    "  },\n"
    '  "enforce_admins": false,\n'
    '  "required_pull_request_reviews": {\n'
    '    "dismiss_stale_reviews": true,\n'
    '    "required_approving_review_count": 1\n'
    "  },\n"
    '  "restrictions": null,\n'
    '  "allow_force_pushes": false,\n'
    '  "allow_deletions": false,\n'
    '  "required_conversation_resolution": true\n'
    "}\n"
    "JSON\n\n"
    "echo '==> Branch protection rules applied.'\n"
)

# ────────────────────────────────────────────────────────────────────────────
# CODEOWNERS
# ────────────────────────────────────────────────────────────────────────────

w(".github/CODEOWNERS",
    "# Global owner — all files require review\n"
    "* @VladByPinsk\n\n"
    "# Infrastructure changes require extra care\n"
    "docker/              @VladByPinsk\n"
    ".github/workflows/   @VladByPinsk\n"
    "infrastructure/      @VladByPinsk\n"
    "scripts/             @VladByPinsk\n"
)

# ────────────────────────────────────────────────────────────────────────────
# PR template
# ────────────────────────────────────────────────────────────────────────────

w(".github/pull_request_template.md",
    "## Summary\n"
    "<!-- What does this PR do? Link the Jira/GitHub issue it resolves. -->\n"
    "Closes #\n\n"
    "## Type of change\n"
    "- [ ] Bug fix\n"
    "- [ ] New feature\n"
    "- [ ] Breaking change\n"
    "- [ ] Refactor / tech debt\n"
    "- [ ] Infrastructure / DevOps\n"
    "- [ ] Documentation\n\n"
    "## Checklist\n"
    "- [ ] Tests added / updated\n"
    "- [ ] All CI checks pass\n"
    "- [ ] No secrets or credentials committed\n"
    "- [ ] Flyway migration added (if DB schema changed)\n"
    "- [ ] Spec / docs updated (if API contract changed)\n"
    "- [ ] Docker Compose works locally (`docker compose up`)\n"
)

# ────────────────────────────────────────────────────────────────────────────
# README
# ────────────────────────────────────────────────────────────────────────────

w("README.md",
    "# 🥗 Calorie & Nutrition Tracker\n\n"
    "> Full-stack microservice application | Java 21 · Spring Boot 3 · React 19 · React Native (Expo) · AI-powered\n\n"
    "[![CI](https://github.com/VladByPinsk/calorie-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/VladByPinsk/calorie-tracker/actions/workflows/ci.yml)\n\n"
    "See [`CALORIE_NUTRITION_TRACKER_SPEC.md`](./CALORIE_NUTRITION_TRACKER_SPEC.md) for the full technical specification.\n\n"
    "## Quick Start\n\n"
    "### Prerequisites\n"
    "- Java 21 (Temurin)\n"
    "- Docker Desktop\n"
    "- Node.js 22\n"
    "- Gradle 8 (or use `./gradlew` wrapper)\n\n"
    "### 1. Environment\n"
    "```bash\n"
    "cp .env.example .env\n"
    "# Edit .env — fill in DB_PASSWORD, JWT_SECRET, etc.\n"
    "```\n\n"
    "### 2. Start infrastructure\n"
    "```bash\n"
    "cd docker\n"
    "docker compose up postgres redis kafka zookeeper minio ollama zipkin prometheus grafana -d\n"
    "```\n\n"
    "### 3. Pull AI models (first time, ~9 GB)\n"
    "```bash\n"
    "bash docker/ollama/pull-models.sh\n"
    "```\n\n"
    "### 4. Run services locally\n"
    "```bash\n"
    "./gradlew :infrastructure:eureka-server:bootRun &\n"
    "./gradlew :infrastructure:config-server:bootRun &\n"
    "./gradlew :services:auth-service:bootRun &\n"
    "# ... etc\n"
    "```\n\n"
    "### 5. Run web frontend\n"
    "```bash\n"
    "cd web && npm install && npm run dev\n"
    "```\n\n"
    "## Architecture\n"
    "See [spec section 3](./CALORIE_NUTRITION_TRACKER_SPEC.md#3-microservice-architecture).\n\n"
    "| Service | Port |\n"
    "|---|---|\n"
    "| API Gateway | 8080 |\n"
    "| Auth Service | 8081 |\n"
    "| User Service | 8082 |\n"
    "| Food Service | 8083 |\n"
    "| Diary Service | 8084 |\n"
    "| AI Service | 8085 |\n"
    "| Analytics Service | 8086 |\n"
    "| Notification Service | 8087 |\n"
    "| Eureka | 8761 |\n"
    "| Config Server | 8888 |\n"
    "| Zipkin | 9411 |\n"
    "| Prometheus | 9090 |\n"
    "| Grafana | 3001 |\n\n"
    "## Branch Strategy\n\n"
    "```\n"
    "main          ← production (protected, PRs only, all CI must pass)\n"
    "develop       ← integration branch (protected, PRs only)\n"
    "feature/*     ← feature branches → PR into develop\n"
    "fix/*         ← bug fixes → PR into develop\n"
    "release/*     ← release preparation → PR into main\n"
    "hotfix/*      ← urgent prod fixes → PR into main + backport to develop\n"
    "```\n\n"
    "## Contributing\n"
    "1. Branch off `develop`: `git checkout -b feature/your-feature`\n"
    "2. Commit with [Conventional Commits](https://www.conventionalcommits.org/)\n"
    "3. Push and open a PR against `develop`\n"
    "4. All CI checks must pass + 1 approval required\n"
)

print("\nAll files created successfully!")


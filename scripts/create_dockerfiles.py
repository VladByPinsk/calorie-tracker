#!/usr/bin/env python3
"""Generate Dockerfiles for all services."""
import os

BASE = "/Users/uladzislau/IdeaProjects/calorie-tracker"

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"  created: {path}")

DOCKERFILE = """\
# Multi-stage build — keeps final image small
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY {svc_path}/build.gradle.kts {svc_path}/
COPY {svc_path}/src {svc_path}/src
RUN ./gradlew :{gradle_module}:bootJar --no-daemon -q

FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/{svc_path}/build/libs/*.jar app.jar
EXPOSE {port}
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
"""

services = [
    ("services/api-gateway",         ":services:api-gateway",         8080),
    ("services/auth-service",        ":services:auth-service",        8081),
    ("services/user-service",        ":services:user-service",        8082),
    ("services/food-service",        ":services:food-service",        8083),
    ("services/diary-service",       ":services:diary-service",       8084),
    ("services/ai-service",          ":services:ai-service",          8085),
    ("services/analytics-service",   ":services:analytics-service",   8086),
    ("services/notification-service",":services:notification-service",8087),
    ("infrastructure/eureka-server", ":infrastructure:eureka-server", 8761),
    ("infrastructure/config-server", ":infrastructure:config-server", 8888),
]

for svc_path, gradle_module, port in services:
    content = DOCKERFILE.format(
        svc_path=svc_path,
        gradle_module=gradle_module,
        port=port
    )
    w(f"{svc_path}/Dockerfile", content)

# Gradle wrapper shell script
w("gradlew",
    "#!/bin/sh\n"
    '#\n'
    '# Gradle start up script for UN*X\n'
    '#\n'
    'APP_HOME=$(cd "$(dirname "$0")" && pwd)\n'
    'exec java -jar "$APP_HOME/gradle/wrapper/gradle-wrapper.jar" "$@"\n'
)
os.chmod(os.path.join(BASE, "gradlew"), 0o755)

# Flyway migration placeholders for services with DB
db_services = [
    ("services/auth-service",        "auth"),
    ("services/user-service",        "user"),
    ("services/food-service",        "food"),
    ("services/diary-service",       "diary"),
    ("services/analytics-service",   "analytics"),
    ("services/notification-service","notification"),
]
for svc_path, db in db_services:
    w(f"{svc_path}/src/main/resources/db/migration/V1__init.sql",
        f"-- {db}_db initial schema\n"
        f"-- TODO: Add CREATE TABLE statements for {db} service entities\n"
    )

# Kafka topics documentation
w("docker/kafka/topics.md",
    "# Kafka Topics\n\n"
    "| Topic | Producer | Consumers | Partitions | Description |\n"
    "|---|---|---|---|---|\n"
    "| `user.registered` | auth-service | user-service, notification-service | 3 | Fired when a new user registers |\n"
    "| `diary.entry.created` | diary-service | analytics-service, notification-service | 3 | Fired on every food log entry |\n"
    "| `food.indexed` | food-service | ai-service | 3 | Fired when a food item is added/updated in the DB |\n"
    "| `ai.food.recognized` | ai-service | diary-service | 3 | AI identified foods from a photo — diary creates draft entries |\n"
    "| `analytics.report.ready` | analytics-service | notification-service | 1 | Weekly digest ready to send |\n\n"
    "> **Partitioning key:** All user-scoped topics use `userId` as the Kafka message key\n"
    "> to guarantee ordering per user.\n"
)

# Web package.json placeholder
w("web/package.json",
    '{\n'
    '  "name": "calorie-tracker-web",\n'
    '  "version": "0.1.0",\n'
    '  "private": true,\n'
    '  "scripts": {\n'
    '    "dev": "vite",\n'
    '    "build": "tsc && vite build",\n'
    '    "lint": "eslint src --ext .ts,.tsx",\n'
    '    "test": "vitest run",\n'
    '    "preview": "vite preview"\n'
    '  },\n'
    '  "dependencies": {\n'
    '    "react": "^19.0.0",\n'
    '    "react-dom": "^19.0.0",\n'
    '    "react-router-dom": "^7.1.0",\n'
    '    "bootstrap": "^5.3.3",\n'
    '    "axios": "^1.8.4",\n'
    '    "react-hook-form": "^7.54.2",\n'
    '    "zod": "^3.24.2",\n'
    '    "@hookform/resolvers": "^3.10.0",\n'
    '    "i18next": "^24.2.3",\n'
    '    "react-i18next": "^15.4.1",\n'
    '    "i18next-browser-languagedetector": "^8.0.4",\n'
    '    "recharts": "^2.15.1",\n'
    '    "react-datepicker": "^7.6.0"\n'
    '  },\n'
    '  "devDependencies": {\n'
    '    "@types/react": "^19.0.0",\n'
    '    "@types/react-dom": "^19.0.0",\n'
    '    "@vitejs/plugin-react": "^4.3.4",\n'
    '    "typescript": "^5.7.3",\n'
    '    "vite": "^6.2.0",\n'
    '    "vitest": "^3.0.7",\n'
    '    "@testing-library/react": "^16.2.0",\n'
    '    "eslint": "^9.21.0",\n'
    '    "@typescript-eslint/eslint-plugin": "^8.24.1",\n'
    '    "eslint-plugin-react-hooks": "^5.1.0"\n'
    '  }\n'
    '}\n'
)

# Mobile package.json placeholder
w("mobile/package.json",
    '{\n'
    '  "name": "calorie-tracker-mobile",\n'
    '  "version": "0.1.0",\n'
    '  "main": "expo-router/entry",\n'
    '  "scripts": {\n'
    '    "start": "expo start",\n'
    '    "android": "expo run:android",\n'
    '    "ios": "expo run:ios",\n'
    '    "lint": "eslint app components --ext .ts,.tsx",\n'
    '    "test": "jest --passWithNoTests"\n'
    '  },\n'
    '  "dependencies": {\n'
    '    "expo": "~52.0.0",\n'
    '    "expo-router": "~4.0.0",\n'
    '    "expo-camera": "~16.0.0",\n'
    '    "expo-barcode-scanner": "~13.0.0",\n'
    '    "expo-notifications": "~0.29.0",\n'
    '    "expo-sqlite": "~14.0.0",\n'
    '    "react": "18.3.1",\n'
    '    "react-native": "0.76.5",\n'
    '    "axios": "^1.8.4",\n'
    '    "i18next": "^24.2.3",\n'
    '    "react-i18next": "^15.4.1",\n'
    '    "react-native-safe-area-context": "4.14.0",\n'
    '    "react-native-screens": "~4.4.0",\n'
    '    "@react-native-community/datetimepicker": "8.2.0"\n'
    '  },\n'
    '  "devDependencies": {\n'
    '    "@babel/core": "^7.25.0",\n'
    '    "@types/react": "~18.3.12",\n'
    '    "typescript": "^5.7.3",\n'
    '    "jest": "^29.7.0",\n'
    '    "@testing-library/react-native": "^13.0.0",\n'
    '    "eslint": "^9.21.0"\n'
    '  }\n'
    '}\n'
)

print("\nDone!")


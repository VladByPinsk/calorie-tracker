# Multi-stage build — keeps final image small
FROM eclipse-temurin:26-jdk-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY services/auth-service/build.gradle.kts services/auth-service/
COPY services/auth-service/src services/auth-service/src
RUN ./gradlew ::services:auth-service:bootJar --no-daemon -q

FROM eclipse-temurin:26-jre-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/services/auth-service/build/libs/*.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

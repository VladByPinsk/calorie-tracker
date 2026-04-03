# Multi-stage build — keeps final image small
FROM eclipse-temurin:26-jdk-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY services/api-gateway/build.gradle.kts services/api-gateway/
COPY services/api-gateway/src services/api-gateway/src
RUN ./gradlew ::services:api-gateway:bootJar --no-daemon -q

FROM eclipse-temurin:26-jre-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/services/api-gateway/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

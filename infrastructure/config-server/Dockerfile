# Multi-stage build — keeps final image small
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY infrastructure/config-server/build.gradle.kts infrastructure/config-server/
COPY infrastructure/config-server/src infrastructure/config-server/src
RUN ./gradlew ::infrastructure:config-server:bootJar --no-daemon -q

FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/infrastructure/config-server/build/libs/*.jar app.jar
EXPOSE 8888
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

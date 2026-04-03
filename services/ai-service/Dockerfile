# Multi-stage build — keeps final image small
FROM amazoncorretto:26-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY services/ai-service/build.gradle.kts services/ai-service/
COPY services/ai-service/src services/ai-service/src
RUN ./gradlew ::services:ai-service:bootJar --no-daemon -q

FROM amazoncorretto:26-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/services/ai-service/build/libs/*.jar app.jar
EXPOSE 8085
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

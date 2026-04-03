# Multi-stage build — keeps final image small
FROM amazoncorretto:26-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY services/notification-service/build.gradle.kts services/notification-service/
COPY services/notification-service/src services/notification-service/src
RUN ./gradlew ::services:notification-service:bootJar --no-daemon -q

FROM amazoncorretto:26-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/services/notification-service/build/libs/*.jar app.jar
EXPOSE 8087
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

# Multi-stage build — keeps final image small
FROM amazoncorretto:26-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY services/user-service/build.gradle.kts services/user-service/
COPY services/user-service/src services/user-service/src
RUN ./gradlew ::services:user-service:bootJar --no-daemon -q

FROM amazoncorretto:26-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/services/user-service/build/libs/*.jar app.jar
EXPOSE 8082
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

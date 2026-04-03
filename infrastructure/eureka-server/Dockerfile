# Multi-stage build — keeps final image small
FROM amazoncorretto:26-alpine AS builder
WORKDIR /app
COPY gradlew .
COPY gradle gradle
COPY settings.gradle.kts .
COPY build.gradle.kts .
COPY gradle.properties .
COPY infrastructure/eureka-server/build.gradle.kts infrastructure/eureka-server/
COPY infrastructure/eureka-server/src infrastructure/eureka-server/src
RUN ./gradlew ::infrastructure:eureka-server:bootJar --no-daemon -q

FROM amazoncorretto:26-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring
WORKDIR /app
COPY --from=builder /app/infrastructure/eureka-server/build/libs/*.jar app.jar
EXPOSE 8761
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

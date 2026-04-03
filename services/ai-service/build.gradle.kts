plugins {
    id("org.springframework.boot")
    id("com.google.cloud.tools.jib")
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-starter-oauth2-resource-server")
    implementation("org.springframework.cloud:spring-cloud-starter-netflix-eureka-client")
    implementation("org.springframework.kafka:spring-kafka")
    implementation("org.springframework.boot:spring-boot-starter-data-redis")
    implementation("org.springframework.ai:spring-ai-ollama-spring-boot-starter")
    implementation("org.springframework.ai:spring-ai-pgvector-store-spring-boot-starter")
    implementation("io.minio:minio:8.5.14")
    implementation("io.micrometer:micrometer-registry-prometheus")
    implementation("io.micrometer:micrometer-tracing-bridge-brave")
    implementation("io.zipkin.reporter2:zipkin-reporter-brave")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:postgresql")
    testImplementation("org.testcontainers:kafka")
}

jib {
    from { image = "eclipse-temurin:26-jre-alpine" }
    to   { image = "ghcr.io/VladByPinsk/calorie-tracker/ai-service:${project.version}" }
}

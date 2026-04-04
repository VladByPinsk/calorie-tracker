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
    implementation("org.springframework.ai:spring-ai-ollama:1.1.4")
    implementation("org.springframework.ai:spring-ai-pgvector-store:1.1.4")
    implementation("io.minio:minio:9.0.0")
    implementation("io.micrometer:micrometer-registry-prometheus")
    implementation("io.micrometer:micrometer-tracing-bridge-brave")
    implementation("io.zipkin.reporter2:zipkin-reporter-brave")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:postgresql")
    testImplementation("org.testcontainers:kafka")
}

jib {
    from { image = "amazoncorretto:26-alpine" }
    to   { image = "ghcr.io/VladByPinsk/calorie-tracker/ai-service:${project.version}" }
}

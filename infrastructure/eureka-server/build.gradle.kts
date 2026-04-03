plugins {
    id("org.springframework.boot")
    id("com.google.cloud.tools.jib")
}

dependencies {
    implementation("org.springframework.cloud:spring-cloud-starter-netflix-eureka-server")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
}

jib {
    from { image = "eclipse-temurin:21-jre-alpine" }
    to   { image = "ghcr.io/vladbyPinsk/calorie-tracker/eureka-server:${project.version}" }
}


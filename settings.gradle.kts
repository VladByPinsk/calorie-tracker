rootProject.name = "calorie-tracker"

// ─── Spring Cloud Infrastructure ──────────────────────────────────────────────
include(":infrastructure:eureka-server")
include(":infrastructure:config-server")

// ─── Application Microservices ────────────────────────────────────────────────
include(":services:api-gateway")
include(":services:auth-service")
include(":services:user-service")
include(":services:food-service")
include(":services:diary-service")
include(":services:ai-service")
include(":services:analytics-service")
include(":services:notification-service")

pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }
}


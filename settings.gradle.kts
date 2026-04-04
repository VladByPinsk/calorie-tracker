// pluginManagement and dependencyResolutionManagement MUST be first in settings.gradle.kts
pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

// ─── Toolchain resolver: lets Gradle auto-provision Amazon Corretto 26 on CI ─
plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
        // Spring repos only for Spring-namespaced artifacts (Spring Boot 4, Spring Cloud 2025, Spring AI 1.0).
        // Content filtering prevents non-Spring libs (bucket4j, minio, etc.) from hitting these
        // repos and getting a 401.
        maven {
            url = uri("https://repo.spring.io/milestone")
            content {
                includeGroupByRegex("org\\.springframework.*")
                includeGroupByRegex("io\\.spring.*")
            }
        }
        maven {
            url = uri("https://repo.spring.io/release")
            content {
                includeGroupByRegex("org\\.springframework.*")
                includeGroupByRegex("io\\.spring.*")
            }
        }
    }
}

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



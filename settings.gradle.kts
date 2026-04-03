// pluginManagement and dependencyResolutionManagement MUST be first in settings.gradle.kts
pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
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



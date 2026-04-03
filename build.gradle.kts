import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    java
    id("org.springframework.boot") version "3.4.4" apply false
    id("io.spring.dependency-management") version "1.1.7" apply false
    id("com.google.cloud.tools.jib") version "3.4.4" apply false
}

// ─── Versions catalogue ───────────────────────────────────────────────────────
val javaVersion        = JavaVersion.VERSION_21
val springBootVersion  = "3.4.4"
val springCloudVersion = "2024.0.1"
val springAiVersion    = "1.0.0-M6"
val mapstructVersion   = "1.6.3"
val lombokVersion      = "1.18.36"
val testcontainersVer  = "1.20.4"
val flywayVersion      = "11.3.4"

// ─── Apply to ALL sub-projects ────────────────────────────────────────────────
subprojects {
    apply(plugin = "java")
    apply(plugin = "io.spring.dependency-management")

    group = "com.calorietracker"
    version = "0.0.1-SNAPSHOT"

    java {
        sourceCompatibility = javaVersion
        targetCompatibility = javaVersion
    }

    configurations {
        compileOnly { extendsFrom(configurations.annotationProcessor.get()) }
    }

    the<io.spring.gradle.dependencymanagement.dsl.DependencyManagementExtension>().apply {
        imports {
            mavenBom("org.springframework.boot:spring-boot-dependencies:$springBootVersion")
            mavenBom("org.springframework.cloud:spring-cloud-dependencies:$springCloudVersion")
            mavenBom("org.springframework.ai:spring-ai-bom:$springAiVersion")
            mavenBom("org.testcontainers:testcontainers-bom:$testcontainersVer")
        }
    }

    dependencies {
        // Lombok
        compileOnly("org.projectlombok:lombok:$lombokVersion")
        annotationProcessor("org.projectlombok:lombok:$lombokVersion")
        testCompileOnly("org.projectlombok:lombok:$lombokVersion")
        testAnnotationProcessor("org.projectlombok:lombok:$lombokVersion")

        // MapStruct
        implementation("org.mapstruct:mapstruct:$mapstructVersion")
        annotationProcessor("org.mapstruct:mapstruct-processor:$mapstructVersion")

        // Testing
        testImplementation("org.springframework.boot:spring-boot-starter-test")
        testRuntimeOnly("org.junit.platform:junit-platform-launcher")
    }

    tasks.withType<Test> {
        useJUnitPlatform()
    }
}


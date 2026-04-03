plugins {
    java
    id("org.springframework.boot") version "4.0.0" apply false
    id("com.google.cloud.tools.jib") version "3.4.4" apply false
}

// ─── Shared version constants (referenced in sub-projects via rootProject.ext) ─
ext {
    set("springBootVersion",  "4.0.0")
    set("springCloudVersion", "2025.0.0")
    set("springAiVersion",    "1.0.0")
    set("mapstructVersion",   "1.6.3")
    set("lombokVersion",      "1.18.40")
    set("testcontainersVer",  "1.21.0")
    set("flywayVersion",      "11.3.4")
    set("jwtVersion",         "0.12.6")
}

// ─── Apply to ALL sub-projects ────────────────────────────────────────────────
subprojects {
    apply(plugin = "java")

    group = "com.calorietracker"
    version = "0.0.1-SNAPSHOT"

    // Java 26 toolchain — Gradle auto-provisions Amazon Corretto 26 if not present
    java {
        toolchain {
            languageVersion.set(JavaLanguageVersion.of(26))
            vendor.set(JvmVendorSpec.AMAZON)
        }
    }

    configurations {
        compileOnly { extendsFrom(configurations.annotationProcessor.get()) }
    }

    dependencies {
        val lombokVersion    = rootProject.ext["lombokVersion"]    as String
        val mapstructVersion = rootProject.ext["mapstructVersion"] as String

        // ── BOMs — Gradle native platform() replaces io.spring.dependency-management ─
        "implementation"(platform("org.springframework.boot:spring-boot-dependencies:${rootProject.ext["springBootVersion"]}"))
        "implementation"(platform("org.springframework.cloud:spring-cloud-dependencies:${rootProject.ext["springCloudVersion"]}"))
        "implementation"(platform("org.springframework.ai:spring-ai-bom:${rootProject.ext["springAiVersion"]}"))
        "testImplementation"(platform("org.testcontainers:testcontainers-bom:${rootProject.ext["testcontainersVer"]}"))

        // Lombok
        "compileOnly"("org.projectlombok:lombok:$lombokVersion")
        "annotationProcessor"("org.projectlombok:lombok:$lombokVersion")
        "testCompileOnly"("org.projectlombok:lombok:$lombokVersion")
        "testAnnotationProcessor"("org.projectlombok:lombok:$lombokVersion")

        // MapStruct
        "implementation"("org.mapstruct:mapstruct:$mapstructVersion")
        "annotationProcessor"("org.mapstruct:mapstruct-processor:$mapstructVersion")

        // Testing
        "testImplementation"("org.springframework.boot:spring-boot-starter-test")
        "testRuntimeOnly"("org.junit.platform:junit-platform-launcher")
    }

    tasks.withType<Test> {
        useJUnitPlatform()
    }
}

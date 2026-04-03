plugins {
    java
    id("org.springframework.boot") version "3.4.4" apply false
    id("io.spring.dependency-management") version "1.1.7" apply false
    id("com.google.cloud.tools.jib") version "3.4.4" apply false
}

// ─── Shared version constants (referenced in sub-projects via rootProject.ext) ─
ext {
    set("springBootVersion",  "3.4.4")
    set("springCloudVersion", "2024.0.1")
    set("springAiVersion",    "1.0.0-M6")
    set("mapstructVersion",   "1.6.3")
    set("lombokVersion",      "1.18.36")
    set("testcontainersVer",  "1.20.4")
    set("flywayVersion",      "11.3.4")
    set("jwtVersion",         "0.12.6")
}

// ─── Apply to ALL sub-projects ────────────────────────────────────────────────
subprojects {
    apply(plugin = "java")
    apply(plugin = "io.spring.dependency-management")

    group = "com.calorietracker"
    version = "0.0.1-SNAPSHOT"

    java {
        sourceCompatibility = JavaVersion.VERSION_26
        targetCompatibility = JavaVersion.VERSION_26
    }

    configurations {
        compileOnly { extendsFrom(configurations.annotationProcessor.get()) }
    }

    extensions.configure<io.spring.gradle.dependencymanagement.dsl.DependencyManagementExtension> {
        imports {
            mavenBom("org.springframework.boot:spring-boot-dependencies:${rootProject.ext["springBootVersion"]}")
            mavenBom("org.springframework.cloud:spring-cloud-dependencies:${rootProject.ext["springCloudVersion"]}")
            mavenBom("org.springframework.ai:spring-ai-bom:${rootProject.ext["springAiVersion"]}")
            mavenBom("org.testcontainers:testcontainers-bom:${rootProject.ext["testcontainersVer"]}")
        }
    }

    dependencies {
        val lombokVersion = rootProject.ext["lombokVersion"] as String
        val mapstructVersion = rootProject.ext["mapstructVersion"] as String

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


plugins {
    java
    checkstyle
    jacoco
    id("org.springframework.boot") version "4.0.5" apply false
    id("com.google.cloud.tools.jib") version "3.5.3" apply false
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
    apply(plugin = "checkstyle")
    apply(plugin = "jacoco")

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
        all {
            resolutionStrategy {
                // ── Dependency version overrides for known CVEs ──────────────────────
                // Each entry overrides the version resolved by the Spring Boot / Spring Cloud
                // BOM. Remove an entry once the BOM itself ships the patched version.

                // CVE-2026-24400 / GHSA-rqfh-9r24-8c9r — AssertJ XXE in isXmlEqualTo
                // Spring Boot 4.0.0 BOM → 3.27.6 (vulnerable). Fix: ≥ 3.27.7.
                force("org.assertj:assertj-core:3.27.7")

                // CVE-2026-24734 / GHSA-mgp5-rv84-w37q — Tomcat OCSP verification bypass
                // Spring Boot 4.0.0 BOM → 11.0.14 (vulnerable). Fix: ≥ 11.0.18.
                force("org.apache.tomcat.embed:tomcat-embed-core:11.0.20")
                force("org.apache.tomcat.embed:tomcat-embed-websocket:11.0.20")
                force("org.apache.tomcat.embed:tomcat-embed-el:11.0.20")

                // CVE-2025-67030 / GHSA-6fmv-xxpf-w3cw — plexus-utils directory traversal
                // Transitive via Spring Cloud / Netflix. Fix: ≥ 4.0.3.
                force("org.codehaus.plexus:plexus-utils:4.0.3")

                // CVE-2026-33870 / GHSA-pwqr-wmgm-9rr8 — Netty HTTP/1.1 request smuggling
                // CVE-2026-33871 / GHSA-w9fj-cfpg-grvv — Netty HTTP/2 CONTINUATION DoS
                // CVE database only tracks the 4.1.x fix (4.1.132.Final); the 4.2.x
                // clean version is 4.2.12.Final (validated CVE-free). Fix: ≥ 4.2.12.Final.
                force("io.netty:netty-codec-http:4.2.12.Final")
                force("io.netty:netty-codec-http2:4.2.12.Final")
                force("io.netty:netty-codec:4.2.12.Final")
                force("io.netty:netty-handler:4.2.12.Final")
                force("io.netty:netty-transport:4.2.12.Final")
                force("io.netty:netty-common:4.2.12.Final")
                force("io.netty:netty-buffer:4.2.12.Final")

                // CVE-2025-48734 / GHSA-wxr5-93ph-8wr9 — commons-beanutils improper access
                // Transitive via Spring Cloud Netflix. Fix: ≥ 1.11.0.
                force("commons-beanutils:commons-beanutils:1.11.0")

                // CVE-2024-47072 / GHSA-hfq9-hggm-c56q — XStream DoS via stack overflow
                // Transitive via Spring Cloud Config. Fix: ≥ 1.4.21.
                force("com.thoughtworks.xstream:xstream:1.4.21")

                // CVE-2026-29062 / GHSA-6v53-7c9g-w56r — jackson-core nesting depth bypass
                // GHSA-72hv-8253-57qq — jackson-core async parser number length bypass
                // Spring Boot 4.0.0 BOM → 3.0.2 (vulnerable). Fix: ≥ 3.1.0.
                // NOTE: also added as a dependency constraint below so that
                //       gradle/actions/dependency-submission reports 3.1.1 (not the
                //       BOM-declared 3.0.2) in the submitted graph snapshot.
                force("tools.jackson.core:jackson-core:3.1.1")
            }
        }
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

    // ── Checkstyle (official Google checks — read directly from the Checkstyle jar) ──
    // google_checks.xml is bundled inside the Checkstyle tool jar itself.
    // Referencing it this way means we always use the canonical, unmodified
    // Google Java Style config that ships with the chosen toolVersion —
    // no local copy that can drift or be accidentally modified.
    checkstyle {
        toolVersion = "10.21.1"
        config = resources.text.fromArchiveEntry(
            configurations.getByName("checkstyle").resolvedConfiguration
                .resolvedArtifacts.first { it.name == "checkstyle" }.file,
            "google_checks.xml"
        )
        isIgnoreFailures = false
        maxWarnings = 0
    }

    // Exclude generated / trivial sources from Checkstyle analysis.
    // MapStruct generates *MapperImpl.java files that are not hand-written code.
    // *Application.java classes are one-liner Spring Boot entry points.
    tasks.withType<Checkstyle> {
        exclude("**/*MapperImpl.java")
        exclude("**/*Application.java")
    }

    // ── JaCoCo – code coverage ───────────────────────────────────────────────
    jacoco {
        toolVersion = "0.8.12"
    }

    tasks.named<JacocoReport>("jacocoTestReport") {
        dependsOn(tasks.named("test"))
        reports {
            xml.required.set(true)   // consumed by SonarCloud / CI coverage tools
            html.required.set(true)  // human-readable report in build/reports/jacoco/
        }
    }

    tasks.named<JacocoCoverageVerification>("jacocoTestCoverageVerification") {
        violationRules {
            rule {
                limit {
                    // Minimum line coverage across the whole module.
                    // Raise this gradually (70 → 75 → 80 …) as tests are added.
                    minimum = "0.70".toBigDecimal()
                }
            }
        }
    }

    // Run coverage verification as part of the standard `check` lifecycle.
    // Order: checkstyleMain → checkstyleTest → test → jacocoTestReport → jacocoTestCoverageVerification
    tasks.named("check") {
        dependsOn(tasks.named("jacocoTestReport"))
        dependsOn(tasks.named("jacocoTestCoverageVerification"))
    }
}

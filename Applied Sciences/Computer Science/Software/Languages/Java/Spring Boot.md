---
title: "Spring Boot"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java, spring, backend, api]
date: "2026-04-07"
---

# Spring Boot

Spring Boot est un framework Java qui simplifie le développement d'applications Spring en fournissant une auto-configuration, un serveur web intégré et une gestion de dépendances simplifiée.

## Frameworks — concepts généraux

Un framework est une fondation pré-construite qui fournit une structure, des règles et des bibliothèques pour développer une application. Il permet de se concentrer sur la logique métier plutôt que sur les aspects techniques répétitifs.

**Inversion of Control (IoC)** : le flux d'exécution n'est plus contrôlé par le développeur mais par le framework. Le code appelle les APIs du framework, pas l'inverse.

**Avantages des frameworks :**
- Efficacité : réduction du code répétitif
- Structure : encourage les design patterns cohérents
- Sécurité : protections intégrées contre SQLi, XSS
- Communauté : documentation abondante et support actif

## Spring vs Spring Boot

**Spring** est un framework open-source pour les applications Java d'entreprise. Il supporte l'injection de dépendances (DI), la programmation orientée aspect (AOP) et la gestion transactionnelle. Sa configuration est cependant complexe.

**Spring Boot** simplifie Spring avec :
- **Auto-configuration** : détecte et configure automatiquement les composants
- **Serveur web intégré** (Tomcat/Jetty/Undertow) — pas de déploiement WAR nécessaire
- **Starter dependencies** : un seul artefact Maven/Gradle inclut toutes les dépendances nécessaires

## Architecture REST

REST (Representational State Transfer) est un style architectural pour concevoir des APIs web. Une API respectant les principes REST est dite **RESTful**.

### Principes REST

| Principe | Description |
|----------|-------------|
| **Client-Server** | Séparation stricte client/serveur, développement indépendant |
| **Stateless** | Chaque requête contient toutes les informations nécessaires ; le serveur ne conserve pas d'état de session entre les requêtes |
| **Uniform Interface** | Ressources identifiées par URI ; manipulation via représentations HTTP standard |
| **Layered System** | Le client ne sait pas s'il communique directement avec le serveur ou via un intermédiaire (cache, load balancer) |

### Méthodes HTTP

| Méthode | Description | Idempotent | Exemple |
|---------|-------------|-----------|---------|
| **GET** | Lire une ressource | Oui | `GET /users/123` |
| **POST** | Créer une ressource | Non | `POST /users` |
| **PUT** | Remplacer entièrement une ressource | Oui | `PUT /users/123` |
| **DELETE** | Supprimer une ressource | Oui | `DELETE /users/123` |
| **PATCH** | Modifier partiellement une ressource | Non | `PATCH /users/123` |

**Idempotent** : exécuter l'opération plusieurs fois donne le même résultat que l'exécuter une seule fois.

## Annotations Spring Boot principales

```java
// Point d'entrée de l'application
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// Contrôleur REST
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired  // Injection de dépendance
    private UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }

    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        User created = userService.save(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id,
                                            @RequestBody User user) {
        return ResponseEntity.ok(userService.update(id, user));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## Spring Data JPA — Persistance

JPA (Jakarta Persistence API) est la spécification standard Java pour l'ORM (Object-Relational Mapping) : le mapping entre classes Java et tables SQL.

```java
// Entité JPA (mappée sur une table)
import jakarta.persistence.*;

@Entity  // Classe = table en base
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String email;

    // Constructeurs, getters, setters
}
```

```java
// Repository : CRUD automatique sans SQL manuel
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Spring génère automatiquement l'implémentation CRUD
    // Méthodes dérivées du nom :
    List<User> findByName(String name);
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);

    // Requête JPQL personnalisée
    @Query("SELECT u FROM User u WHERE u.name LIKE %:keyword%")
    List<User> searchByName(@Param("keyword") String keyword);
}
```

```java
// Service
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    public User findById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("User not found: " + id));
    }

    public User save(User user) {
        return userRepository.save(user);
    }

    public void delete(Long id) {
        userRepository.deleteById(id);
    }
}
```

## Configuration (application.properties)

```properties
# Base de données
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=postgres
spring.datasource.password=secret
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA / Hibernate
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# Port du serveur
server.port=8080

# Profil actif
spring.profiles.active=dev
```

## Maven — pom.xml (dépendances essentielles)

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<dependencies>
    <!-- Web + REST -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- JPA + Hibernate -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- PostgreSQL -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Tests -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

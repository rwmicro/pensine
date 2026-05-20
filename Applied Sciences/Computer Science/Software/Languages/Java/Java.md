---
title: "Java"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-16"
---

# Java

## Vue d'ensemble

Java est un langage de programmation orienté objet, fortement typé, compilé et exécuté sur la JVM (Java Virtual Machine), connu pour sa portabilité ("Write Once, Run Anywhere").

## Caractéristiques principales

### Principes fondamentaux

**Orienté Objet**
- Classes et objets
- Encapsulation
- Héritage
- Polymorphisme
- Abstraction

**Platform Independent**
- Bytecode compilé
- JVM pour chaque plateforme
- WORA (Write Once, Run Anywhere)

**Robuste et Sécurisé**
- Strong typing
- Garbage collection automatique
- Exception handling
- Pas de pointeurs
- Security Manager

## Installation et Setup

### JDK Installation

```bash
# Vérifier version
java -version
javac -version

# Installation (Ubuntu/Debian)
sudo apt install openjdk-17-jdk

# Installation (macOS)
brew install openjdk@17
```

### Variables d'environnement

```bash
export JAVA_HOME=/path/to/jdk
export PATH=$JAVA_HOME/bin:$PATH
```

## Syntaxe de base

### Hello World

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

### Types de données

**Primitifs**
```java
byte    // 8 bits  (-128 à 127)
short   // 16 bits
int     // 32 bits
long    // 64 bits
float   // 32 bits
double  // 64 bits
char    // 16 bits Unicode
boolean // true/false
```

**Référence**
```java
String
Arrays
Classes
Interfaces
```

### Variables

```java
int age = 25;
String name = "John";
final double PI = 3.14159; // Constante
var list = new ArrayList<String>(); // Type inference (Java 10+)
```

### Opérateurs

```java
// Arithmétiques: +, -, *, /, %
// Comparaison: ==, !=, >, <, >=, <=
// Logiques: &&, ||, !
// Assignment: =, +=, -=, *=, /=
// Ternaire: condition ? true : false
```

## Structures de contrôle

### Conditionnelles

```java
if (condition) {
    // code
} else if (otherCondition) {
    // code
} else {
    // code
}

switch (value) {
    case 1:
        // code
        break;
    case 2:
        // code
        break;
    default:
        // code
}

// Switch expressions (Java 14+)
String result = switch (day) {
    case MONDAY, FRIDAY -> "Start/End of week";
    case SATURDAY, SUNDAY -> "Weekend";
    default -> "Midweek";
};
```

### Boucles

```java
// For loop
for (int i = 0; i < 10; i++) {
    System.out.println(i);
}

// Enhanced for (foreach)
for (String item : array) {
    System.out.println(item);
}

// While
while (condition) {
    // code
}

// Do-while
do {
    // code
} while (condition);
```

## Programmation Orientée Objet

### Classes et Objets

```java
public class Person {
    // Attributs
    private String name;
    private int age;
    
    // Constructeur
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // Getters/Setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    // Méthode
    public void introduce() {
        System.out.println("Hi, I'm " + name);
    }
}

// Utilisation
Person person = new Person("John", 25);
person.introduce();
```

### Héritage

```java
public class Student extends Person {
    private String studentId;
    
    public Student(String name, int age, String studentId) {
        super(name, age); // Appel constructeur parent
        this.studentId = studentId;
    }
    
    @Override
    public void introduce() {
        super.introduce();
        System.out.println("Student ID: " + studentId);
    }
}
```

### Interfaces

```java
public interface Drawable {
    void draw(); // Méthode abstraite
    
    default void display() { // Méthode par défaut (Java 8+)
        System.out.println("Displaying...");
    }
    
    static void info() { // Méthode statique
        System.out.println("Drawable interface");
    }
}

public class Circle implements Drawable {
    @Override
    public void draw() {
        System.out.println("Drawing circle");
    }
}
```

### Classes abstraites

```java
public abstract class Shape {
    protected String color;
    
    public abstract double area(); // Méthode abstraite
    
    public void setColor(String color) { // Méthode concrète
        this.color = color;
    }
}

public class Rectangle extends Shape {
    private double width, height;
    
    @Override
    public double area() {
        return width * height;
    }
}
```

## Modificateurs d'accès

| Modificateur | Même classe | Même package | Sous-classe | Partout |
|-------------|------------|-------------|-------------|---------|
| `private` | Oui | Non | Non | Non |
| (par défaut) | Oui | Oui | Non | Non |
| `protected` | Oui | Oui | Oui | Non |
| `public` | Oui | Oui | Oui | Oui |

Les attributs devraient être `private` et accessibles via des getters/setters (encapsulation).

## Enumérations (Enum)

Une `enum` est un type dont les valeurs possibles sont des constantes nommées.

```java
public enum Jour {
    LUNDI, MARDI, MERCREDI, JEUDI, VENDREDI, SAMEDI, DIMANCHE;

    public boolean estWeekend() {
        return this == SAMEDI || this == DIMANCHE;
    }
}

// Utilisation
Jour aujourd_hui = Jour.MERCREDI;
System.out.println(aujourd_hui.estWeekend());  // false

// Itérer sur les valeurs
for (Jour j : Jour.values()) {
    System.out.println(j);
}

// Switch avec enum
switch (aujourd_hui) {
    case LUNDI -> System.out.println("Début de semaine");
    case VENDREDI -> System.out.println("Fin de semaine");
    default -> System.out.println("Milieu de semaine");
}
```

Enum avec attributs :

```java
public enum Planete {
    MERCURE(3.303e+23, 2.4397e6),
    VENUS  (4.869e+24, 6.0518e6),
    TERRE  (5.976e+24, 6.37814e6);

    private final double masse;
    private final double rayon;

    Planete(double masse, double rayon) {
        this.masse = masse;
        this.rayon = rayon;
    }

    public double gravite() {
        final double G = 6.67300E-11;
        return G * masse / (rayon * rayon);
    }
}
```

## Types primitifs — tableau complet

| Type | Taille | Plage | Valeur par défaut |
|------|--------|-------|-------------------|
| `byte` | 1 octet | -128 à 127 | 0 |
| `short` | 2 octets | -32 768 à 32 767 | 0 |
| `int` | 4 octets | -2 147 483 648 à 2 147 483 647 | 0 |
| `long` | 8 octets | -9,2×10^18 à 9,2×10^18 | 0L |
| `float` | 4 octets | ±3,4×10^38 (7 chiffres significatifs) | 0.0f |
| `double` | 8 octets | ±1,7×10^308 (15 chiffres significatifs) | 0.0 |
| `char` | 2 octets | '\u0000' à '\uffff' (Unicode) | '\u0000' |
| `boolean` | 1 bit | true / false | false |

Les types non-primitifs (String, Integer, etc.) commencent par une majuscule et peuvent être `null`.

## Collections Framework

### List

```java
List<String> list = new ArrayList<>();
list.add("Apple");
list.add("Banana");
list.remove(0);
String first = list.get(0);

// LinkedList
List<String> linkedList = new LinkedList<>();
```

### Set

```java
Set<Integer> set = new HashSet<>();
set.add(1);
set.add(2);
set.add(1); // Ignoré (pas de doublons)

// TreeSet (trié)
Set<Integer> treeSet = new TreeSet<>();
```

### Map

```java
Map<String, Integer> map = new HashMap<>();
map.put("Apple", 1);
map.put("Banana", 2);
int value = map.get("Apple");

// Iteration
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
```

### Queue

```java
Queue<String> queue = new LinkedList<>();
queue.offer("First");
queue.offer("Second");
String head = queue.poll();
```

## Gestion d'exceptions

```java
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Division by zero");
} catch (Exception e) {
    System.out.println("General error");
} finally {
    System.out.println("Always executed");
}

// Try with resources (Java 7+)
try (FileReader fr = new FileReader("file.txt")) {
    // Auto-closeable
} catch (IOException e) {
    e.printStackTrace();
}
```

### Custom exceptions

```java
public class CustomException extends Exception {
    public CustomException(String message) {
        super(message);
    }
}

public void method() throws CustomException {
    throw new CustomException("Error occurred");
}
```

## Streams et Lambda (Java 8+)

### Lambda expressions

```java
// Avant Java 8
Runnable r1 = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello");
    }
};

// Avec Lambda
Runnable r2 = () -> System.out.println("Hello");

// Avec paramètres
Comparator<Integer> comp = (a, b) -> a.compareTo(b);
```

### Streams

```java
List<String> names = Arrays.asList("John", "Jane", "Bob");

// Filter
names.stream()
    .filter(name -> name.startsWith("J"))
    .forEach(System.out::println);

// Map
List<Integer> lengths = names.stream()
    .map(String::length)
    .collect(Collectors.toList());

// Reduce
int sum = numbers.stream()
    .reduce(0, Integer::sum);

// Sorted
names.stream()
    .sorted()
    .forEach(System.out::println);
```

### Optional

```java
Optional<String> optional = Optional.of("value");

optional.ifPresent(System.out::println);

String value = optional.orElse("default");
String value2 = optional.orElseGet(() -> "computed default");
```

## Input/Output

### File Reading

```java
// BufferedReader
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
}

// Files (Java 7+)
List<String> lines = Files.readAllLines(Paths.get("file.txt"));
```

### File Writing

```java
try (BufferedWriter bw = new BufferedWriter(new FileWriter("file.txt"))) {
    bw.write("Hello, World!");
}

// Files
Files.write(Paths.get("file.txt"), "Content".getBytes());
```

## Multithreading

### Creating Threads

```java
// Extending Thread
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread running");
    }
}

// Implementing Runnable
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Thread running");
    }
}

// Usage
new MyThread().start();
new Thread(new MyRunnable()).start();

// Lambda
new Thread(() -> System.out.println("Running")).start();
```

### Synchronization

```java
public class Counter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}
```

### ExecutorService

```java
ExecutorService executor = Executors.newFixedThreadPool(5);

executor.submit(() -> {
    System.out.println("Task executed");
});

executor.shutdown();
```

## Frameworks populaires

### Spring Framework

**Spring Boot**
- Auto-configuration
- Standalone applications
- Production-ready

**Spring MVC**
- Web applications
- RESTful APIs

**Spring Data**
- Database access
- JPA, MongoDB, etc.

### Jakarta EE (anciennement Java EE)

- Enterprise applications
- Servlets, JSP
- EJB, JPA

### Build Tools

**Maven**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

**Gradle**
```groovy
implementation 'org.springframework.boot:spring-boot-starter-web'
```

## Testing

### JUnit

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    @Test
    void testAdd() {
        Calculator calc = new Calculator();
        assertEquals(5, calc.add(2, 3));
    }
}
```

### Mockito

```java
import static org.mockito.Mockito.*;

UserService userService = mock(UserService.class);
when(userService.getUser(1)).thenReturn(new User("John"));

verify(userService).getUser(1);
```

## Best Practices

1. **Naming conventions**
   - Classes: PascalCase
   - Methods/variables: camelCase
   - Constants: UPPER_SNAKE_CASE

2. **SOLID Principles**
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

3. **Design Patterns**
   - Singleton
   - Factory
   - Observer
   - Strategy
   - etc.

4. **Exception Handling**
   - Catch specific exceptions
   - Don't swallow exceptions
   - Use try-with-resources

5. **Performance**
   - Use StringBuilder for concatenation
   - Prefer primitives over wrappers
   - Close resources properly

## Ressources

- [Oracle Java Documentation](https://docs.oracle.com/en/java/)
- [Java API Docs](https://docs.oracle.com/en/java/javase/17/docs/api/)
- [Effective Java (Book)](https://www.oreilly.com/library/view/effective-java/9780134686097/)
- Baeldung - Java tutorials

## Versions Java

- Java 8 (LTS) - Lambdas, Streams
- Java 11 (LTS) - HTTP Client, var
- Java 17 (LTS) - Records, Sealed Classes
- Java 21 (LTS) - Virtual Threads, Pattern Matching

## Sujets à approfondir

- [ ] Reflection
- [ ] Annotations
- [ ] Generics avancés
- [ ] CompletableFuture
- [ ] Module System (Java 9+)
- [ ] Records (Java 14+)
- [ ] Pattern Matching (Java 16+)


*Dernière mise à jour: 2026-01-01*

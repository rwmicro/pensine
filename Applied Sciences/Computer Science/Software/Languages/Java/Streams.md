---
title: "Streams API"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-25"
---

# Streams API

L'API Streams (Java 8) permet de traiter des séquences d'éléments de façon fonctionnelle et déclarative. Un pipeline de stream décrit **ce qu'on veut faire**, pas comment l'itérer. L'évaluation est **paresseuse** : les opérations intermédiaires ne s'exécutent que lorsqu'une opération terminale est invoquée.

## Anatomie d'un pipeline

```
Source → [op. intermédiaire]* → op. terminale
```

```java
List<String> noms = List.of("Alice", "Bob", "Charlie", "Anna", "Bernard");

long compte = noms.stream()           // source
    .filter(n -> n.startsWith("A"))   // intermédiaire (lazy)
    .map(String::toUpperCase)         // intermédiaire (lazy)
    .sorted()                         // intermédiaire (lazy)
    .count();                         // terminale — déclenche tout
// compte = 2
```

Un stream **ne modifie jamais la source** et ne peut être consommé qu'une seule fois.

## Création d'un stream

```java
// Depuis une collection
List.of(1, 2, 3).stream()
Set.of("a", "b").stream()

// Depuis un tableau
Arrays.stream(new int[]{1, 2, 3})
Stream.of("x", "y", "z")

// Stream infini
Stream.iterate(0, n -> n + 2)           // 0, 2, 4, 6, ...
Stream.iterate(1, n -> n < 1000, n -> n * 2)  // Java 9 — avec prédicat d'arrêt
Stream.generate(Math::random)           // valeurs aléatoires

// Intervalle de nombres (primitifs)
IntStream.range(0, 5)                  // 0, 1, 2, 3, 4
IntStream.rangeClosed(1, 5)           // 1, 2, 3, 4, 5
LongStream.range(0, 1_000_000L)

// Depuis un fichier (chaque ligne = un élément)
Files.lines(Path.of("data.txt"), StandardCharsets.UTF_8)
```

## Opérations intermédiaires (lazy)

Ces opérations retournent un nouveau `Stream` — elles ne font rien tant qu'une terminale n'est pas appelée.

### filter

```java
// Conserver les éléments qui satisfont le prédicat
Stream.of(1, 2, 3, 4, 5)
    .filter(n -> n % 2 == 0)
    .toList();   // [2, 4]
```

### map

```java
// Transformer chaque élément
List<String> noms = List.of("alice", "bob");
noms.stream()
    .map(String::toUpperCase)
    .toList();   // ["ALICE", "BOB"]

// Conversion de type
Stream.of("1", "2", "3")
    .map(Integer::parseInt)
    .toList();   // [1, 2, 3]
```

### flatMap

```java
// Aplatir un stream de collections en un seul stream
List<List<Integer>> matrices = List.of(
    List.of(1, 2, 3),
    List.of(4, 5, 6)
);
matrices.stream()
    .flatMap(Collection::stream)
    .toList();   // [1, 2, 3, 4, 5, 6]

// Cas typique : extraire des mots d'un texte
List<String> phrases = List.of("bonjour monde", "hello world");
phrases.stream()
    .flatMap(p -> Arrays.stream(p.split(" ")))
    .toList();   // ["bonjour", "monde", "hello", "world"]
```

### distinct, sorted, limit, skip

```java
Stream.of(3, 1, 4, 1, 5, 9, 2, 6, 5)
    .distinct()          // supprime les doublons : [3, 1, 4, 5, 9, 2, 6]
    .sorted()            // ordre naturel : [1, 2, 3, 4, 5, 6, 9]
    .skip(2)             // sauter les 2 premiers : [3, 4, 5, 6, 9]
    .limit(3)            // garder seulement 3 : [3, 4, 5]
    .toList();

// sorted avec Comparator
Stream.of("banana", "apple", "cherry")
    .sorted(Comparator.comparingInt(String::length))
    .toList();   // ["apple", "banana", "cherry"]
```

### peek

```java
// Pour déboguer — ne modifie pas les éléments
Stream.of(1, 2, 3)
    .filter(n -> n > 1)
    .peek(n -> System.out.println("après filter : " + n))
    .map(n -> n * 10)
    .peek(n -> System.out.println("après map : " + n))
    .toList();
```

### mapToInt / mapToLong / mapToDouble

```java
// Conversion vers des streams de primitifs (évite l'autoboxing)
List<String> mots = List.of("chat", "chien", "oiseau");
int totalCaracteres = mots.stream()
    .mapToInt(String::length)
    .sum();   // 17
```

## Opérations terminales

### collect

```java
import java.util.stream.Collectors;

List<String> noms = Stream.of("Alice", "Bob", "Charlie")
    .filter(n -> n.length() > 3)
    .collect(Collectors.toList());   // liste mutable

// Java 16+ : méthode raccourcie
List<String> noms = stream.toList();   // liste immuable

// Vers un Set
Set<String> ensemble = stream.collect(Collectors.toSet());

// Vers une Map
Map<String, Integer> longueurs = Stream.of("Alice", "Bob", "Charlie")
    .collect(Collectors.toMap(
        s -> s,           // clé
        String::length    // valeur
    ));
// {"Alice"=5, "Bob"=3, "Charlie"=7}

// Jointure en chaîne
String csv = Stream.of("Alice", "Bob", "Charlie")
    .collect(Collectors.joining(", ", "[", "]"));
// "[Alice, Bob, Charlie]"
```

### groupingBy

```java
// Regrouper par critère → Map<K, List<V>>
Map<Integer, List<String>> parLongueur = Stream.of("chat", "chien", "oiseau", "lynx")
    .collect(Collectors.groupingBy(String::length));
// {4=["chat", "lynx"], 5=["chien"], 6=["oiseau"]}

// Avec collecteur en aval (downstream)
Map<Integer, Long> comptesParLongueur = Stream.of("chat", "chien", "oiseau", "lynx")
    .collect(Collectors.groupingBy(
        String::length,
        Collectors.counting()
    ));
// {4=2, 5=1, 6=1}

// Partitionnement (cas spécial : prédicat → deux groupes)
Map<Boolean, List<Integer>> partitionné = IntStream.rangeClosed(1, 10)
    .boxed()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));
// {true=[2,4,6,8,10], false=[1,3,5,7,9]}
```

### reduce

```java
// Réduction avec identité
int somme = Stream.of(1, 2, 3, 4, 5)
    .reduce(0, Integer::sum);   // 15

// Sans identité → Optional
Optional<Integer> produit = Stream.of(1, 2, 3, 4)
    .reduce((a, b) -> a * b);   // Optional[24]

// Forme optimisée pour primitifs
int somme2 = IntStream.rangeClosed(1, 100).sum();           // 5050
double moy = IntStream.rangeClosed(1, 100).average().orElse(0);
```

### Opérations de recherche et test

```java
List<Integer> nombres = List.of(1, 3, 5, 7, 9, 2, 4);

nombres.stream().anyMatch(n -> n % 2 == 0);    // true  — au moins un pair
nombres.stream().allMatch(n -> n > 0);          // true  — tous positifs
nombres.stream().noneMatch(n -> n < 0);         // true  — aucun négatif

nombres.stream().findFirst().orElse(-1);        // 1 — premier élément
nombres.stream().findAny().orElse(-1);          // quelconque (utile en parallèle)

nombres.stream().min(Integer::compareTo);       // Optional[1]
nombres.stream().max(Integer::compareTo);       // Optional[9]
nombres.stream().count();                       // 7
```

### forEach

```java
Stream.of("Alice", "Bob").forEach(System.out::println);
// forEach est terminale — ne retourne rien
// forEachOrdered garantit l'ordre (important pour les streams parallèles)
```

## Optional

`Optional<T>` est un conteneur qui encapsule soit une valeur, soit son absence. Il évite les `NullPointerException`.

```java
Optional<String> opt = Stream.of("", "Alice", "Bob")
    .filter(s -> !s.isEmpty())
    .findFirst();   // Optional["Alice"]

// Consommer la valeur
opt.ifPresent(System.out::println);            // "Alice"
opt.ifPresentOrElse(                           // Java 9+
    s -> System.out.println("Trouvé : " + s),
    () -> System.out.println("Absent")
);

// Extraire avec valeur par défaut
String val = opt.orElse("inconnu");
String val2 = opt.orElseGet(() -> calculerDefaut());
String val3 = opt.orElseThrow(() -> new NoSuchElementException("absent"));

// Transformer
Optional<Integer> longueur = opt.map(String::length);   // Optional[5]
Optional<String>  upper    = opt.map(String::toUpperCase);

// Chaîner des Optionals
Optional<String> resultat = opt
    .filter(s -> s.length() > 3)
    .map(String::toUpperCase);   // Optional["ALICE"]
```

## Streams parallèles

```java
// Convertir un stream séquentiel en parallèle
long compte = names.parallelStream()
    .filter(n -> n.startsWith("A"))
    .count();

// Ou via parallel()
Stream.of(1, 2, 3, 4, 5)
    .parallel()
    .map(n -> n * 2)
    .toList();
```

Les streams parallèles utilisent le `ForkJoinPool.commonPool()`. Ils sont bénéfiques pour des opérations coûteuses sur de grandes collections. Les opérations doivent être **sans effets de bord** et **associatives** (pour `reduce`). `forEachOrdered` garantit l'ordre mais réduit le parallélisme.

## Opérations sur les streams de primitifs

`IntStream`, `LongStream`, `DoubleStream` évitent l'autoboxing et offrent des méthodes supplémentaires.

```java
IntStream.rangeClosed(1, 10)
    .filter(n -> n % 2 != 0)    // [1, 3, 5, 7, 9]
    .map(n -> n * n)             // [1, 9, 25, 49, 81]
    .sum();                      // 165

// Statistiques
IntSummaryStatistics stats = IntStream.of(3, 1, 4, 1, 5, 9, 2, 6)
    .summaryStatistics();
stats.getMin();     // 1
stats.getMax();     // 9
stats.getAverage(); // 3.875
stats.getSum();     // 31
stats.getCount();   // 8

// Conversion entre streams
IntStream.range(1, 4).boxed()      // IntStream → Stream<Integer>
Stream.of(1, 2, 3).mapToInt(x -> x)  // Stream<Integer> → IntStream
```

## Récapitulatif

| Opération | Type | Déclenche ? | Retour |
|---|---|---|---|
| `filter` | Intermédiaire | Non | `Stream<T>` |
| `map` | Intermédiaire | Non | `Stream<R>` |
| `flatMap` | Intermédiaire | Non | `Stream<R>` |
| `distinct` | Intermédiaire | Non | `Stream<T>` |
| `sorted` | Intermédiaire | Non | `Stream<T>` |
| `limit` / `skip` | Intermédiaire | Non | `Stream<T>` |
| `peek` | Intermédiaire | Non | `Stream<T>` |
| `collect` | Terminale | Oui | `R` |
| `toList` | Terminale | Oui | `List<T>` |
| `forEach` | Terminale | Oui | `void` |
| `reduce` | Terminale | Oui | `T` / `Optional<T>` |
| `count` | Terminale | Oui | `long` |
| `min` / `max` | Terminale | Oui | `Optional<T>` |
| `findFirst` / `findAny` | Terminale | Oui | `Optional<T>` |
| `anyMatch` / `allMatch` / `noneMatch` | Terminale | Oui | `boolean` |

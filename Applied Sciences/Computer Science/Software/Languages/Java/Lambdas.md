---
title: "Lambdas et interfaces fonctionnelles"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-25"
---

# Lambdas et interfaces fonctionnelles

Les lambdas (Java 8) permettent d'exprimer des comportements comme des valeurs : une lambda est une fonction anonyme que l'on peut passer en argument, stocker dans une variable, ou retourner depuis une méthode. Elles sont fondées sur le concept d'**interface fonctionnelle**.

## Interface fonctionnelle

Une interface fonctionnelle possède **exactement une méthode abstraite**. L'annotation `@FunctionalInterface` est optionnelle mais recommandée — elle provoque une erreur de compilation si l'interface n'est pas fonctionnelle.

```java
@FunctionalInterface
interface Transformateur<T, R> {
    R transformer(T entree);

    // Méthodes default et static autorisées sans briser le contrat
    default Transformateur<T, R> avecLog() {
        return entree -> {
            R res = this.transformer(entree);
            System.out.println(entree + " → " + res);
            return res;
        };
    }
}

Transformateur<String, Integer> longueur = s -> s.length();
longueur.transformer("Bonjour");   // 7
```

## Syntaxe lambda

```java
// Forme complète
(String s1, String s2) -> { return s1.compareTo(s2); }

// Inférence de type (types omis)
(s1, s2) -> { return s1.compareTo(s2); }

// Corps expression (return implicite)
(s1, s2) -> s1.compareTo(s2)

// Un seul paramètre — parenthèses optionnelles
s -> s.length()

// Aucun paramètre
() -> System.out.println("bonjour")

// Corps multi-instructions
(x, y) -> {
    int somme = x + y;
    System.out.println("somme : " + somme);
    return somme;
}
```

## Interfaces fonctionnelles standard (java.util.function)

### Function\<T, R\>

```java
// T → R : transformer un type en un autre
Function<String, Integer> longueur = String::length;
Function<Integer, String> enChaine = Object::toString;

longueur.apply("Bonjour");   // 7

// Composition
Function<String, String> pipeline = longueur.andThen(enChaine);
// andThen : exécuter longueur puis enChaine
// compose : exécuter enChaine puis longueur (ordre inverse)
pipeline.apply("Java");   // "4"

// Fonction identité
Function<String, String> id = Function.identity();
```

### Predicate\<T\>

```java
// T → boolean
Predicate<String> estVide    = String::isEmpty;
Predicate<String> estLong    = s -> s.length() > 5;
Predicate<Integer> estPositif = n -> n > 0;

estVide.test("");        // true
estLong.test("Bonjour"); // true

// Composition
Predicate<String> nonVide    = estVide.negate();
Predicate<String> longOuVide = estLong.or(estVide);
Predicate<String> longEtNonVide = estLong.and(nonVide);

// Usage avec filter
List<String> mots = List.of("", "chat", "chien", "hi");
mots.stream().filter(nonVide).toList();   // ["chat", "chien", "hi"]
```

### Consumer\<T\>

```java
// T → void : consommer sans retourner
Consumer<String> afficher   = System.out::println;
Consumer<String> logFichier = s -> ecrireDansFichier(s);

afficher.accept("Bonjour");

// Chaîner
Consumer<String> afficherEtLogger = afficher.andThen(logFichier);
afficherEtLogger.accept("test");

// Usage
List.of("Alice", "Bob").forEach(afficher);
```

### Supplier\<T\>

```java
// void → T : produire une valeur sans paramètre
Supplier<List<String>> nouvelleListe = ArrayList::new;
Supplier<LocalDate>    maintenant    = LocalDate::now;

List<String> liste = nouvelleListe.get();

// Usage courant : valeur par défaut différée
Optional<String> opt = Optional.empty();
String valeur = opt.orElseGet(() -> calculerValeurParDefaut());
```

### BiFunction\<T, U, R\>

```java
// (T, U) → R : deux entrées, une sortie
BiFunction<String, Integer, String> repeter =
    (s, n) -> s.repeat(n);

repeter.apply("ha", 3);   // "hahaha"
```

### UnaryOperator\<T\> et BinaryOperator\<T\>

```java
// UnaryOperator<T> : spécialisation de Function<T, T>
UnaryOperator<String> mettreMajuscule = String::toUpperCase;
UnaryOperator<Integer> doubler        = n -> n * 2;

// BinaryOperator<T> : spécialisation de BiFunction<T, T, T>
BinaryOperator<Integer> additionner = Integer::sum;
BinaryOperator<String>  concatener  = String::concat;

// Usage dans reduce
List.of(1, 2, 3, 4).stream()
    .reduce(0, additionner);   // 10
```

### Interfaces primitives

Pour éviter l'autoboxing, Java fournit des variantes spécialisées :

| Interface | Signature |
|---|---|
| `IntFunction<R>` | `int → R` |
| `ToIntFunction<T>` | `T → int` |
| `IntUnaryOperator` | `int → int` |
| `IntBinaryOperator` | `(int, int) → int` |
| `IntPredicate` | `int → boolean` |
| `IntConsumer` | `int → void` |
| `IntSupplier` | `() → int` |

Idem pour `Long` et `Double`.

## Références de méthodes (Method References)

Une référence de méthode est un raccourci syntaxique pour une lambda qui ne fait qu'appeler une méthode existante.

```java
// 1. Méthode statique
// Lambda : n -> Integer.parseInt(n)
Function<String, Integer> parser = Integer::parseInt;

// 2. Méthode d'instance sur un objet particulier
String prefixe = "Bonjour";
// Lambda : s -> prefixe.concat(s)
UnaryOperator<String> ajouter = prefixe::concat;

// 3. Méthode d'instance sur un type (le premier paramètre reçoit this)
// Lambda : s -> s.toUpperCase()
Function<String, String> majuscule = String::toUpperCase;
// Lambda : (s1, s2) -> s1.compareTo(s2)
Comparator<String> comp = String::compareTo;

// 4. Constructeur
// Lambda : () -> new ArrayList<>()
Supplier<List<String>>  factory1 = ArrayList::new;
// Lambda : n -> new int[n]
IntFunction<int[]>      factory2 = int[]::new;
```

| Forme | Equivalent lambda |
|---|---|
| `Classe::methodeStatique` | `(args) -> Classe.methodeStatique(args)` |
| `instance::methodeInstance` | `(args) -> instance.methodeInstance(args)` |
| `Classe::methodeInstance` | `(obj, args) -> obj.methodeInstance(args)` |
| `Classe::new` | `(args) -> new Classe(args)` |

## Closures et portée lexicale

Une lambda peut capturer des variables extérieures, à condition qu'elles soient **effectivement finales** (effectively final : non modifiées après leur affectation initiale).

```java
String message = "Bonjour"; // effectively final
Runnable r = () -> System.out.println(message);
// message = "Autre";   // si cette ligne était présente, erreur de compilation

// Les champs d'objet peuvent être modifiés (pas de restriction)
class Compteur {
    int n = 0;
    Runnable incrementer = () -> n++;   // ok — n est un champ, pas une variable locale
}
```

## Comparators chaînés

```java
record Etudiant(String nom, double moyenne, int age) {}

List<Etudiant> etudiants = List.of(
    new Etudiant("Alice", 15.5, 20),
    new Etudiant("Bob",   15.5, 22),
    new Etudiant("Charlie", 14.0, 19)
);

// Tri : d'abord par moyenne décroissante, puis par nom croissant
Comparator<Etudiant> comparateur = Comparator
    .comparingDouble(Etudiant::moyenne).reversed()
    .thenComparing(Etudiant::nom);

etudiants.stream().sorted(comparateur).toList();
// [Alice(15.5), Bob(15.5), Charlie(14.0)]
```

## Récapitulatif des interfaces standard

| Interface | Paramètres | Retour | Méthode |
|---|---|---|---|
| `Function<T, R>` | `T` | `R` | `apply` |
| `BiFunction<T, U, R>` | `T, U` | `R` | `apply` |
| `UnaryOperator<T>` | `T` | `T` | `apply` |
| `BinaryOperator<T>` | `T, T` | `T` | `apply` |
| `Predicate<T>` | `T` | `boolean` | `test` |
| `BiPredicate<T, U>` | `T, U` | `boolean` | `test` |
| `Consumer<T>` | `T` | `void` | `accept` |
| `BiConsumer<T, U>` | `T, U` | `void` | `accept` |
| `Supplier<T>` | — | `T` | `get` |
| `Runnable` | — | `void` | `run` |
| `Callable<V>` | — | `V` | `call` |
| `Comparator<T>` | `T, T` | `int` | `compare` |

---
title: "Generics"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-25"
---

# Generics

Les génériques (introduits en Java 5) permettent d'écrire des classes, interfaces et méthodes paramétrées par des types. Ils apportent la sûreté de type à la compilation et éliminent la majorité des casts explicites.

## Motivation

```java
// Sans génériques (Java 1.4)
List liste = new ArrayList();
liste.add("Alice");
String s = (String) liste.get(0);  // cast obligatoire — risque de ClassCastException

// Avec génériques
List<String> liste = new ArrayList<>();
liste.add("Alice");
String s = liste.get(0);           // pas de cast — le compilateur vérifie les types
liste.add(42);                     // erreur de compilation
```

## Classes génériques

```java
public class Paire<A, B> {
    private final A premier;
    private final B second;

    public Paire(A premier, B second) {
        this.premier = premier;
        this.second  = second;
    }

    public A getPremier() { return premier; }
    public B getSecond()  { return second;  }

    @Override
    public String toString() {
        return "(" + premier + ", " + second + ")";
    }
}

Paire<String, Integer> p = new Paire<>("Alice", 30);
String nom = p.getPremier();  // "Alice" — pas de cast
```

## Méthodes génériques

La déclaration du paramètre de type se place avant le type de retour.

```java
public class Utils {

    // Méthode générique indépendante de la classe
    public static <T> void echanger(T[] tableau, int i, int j) {
        T temp      = tableau[i];
        tableau[i]  = tableau[j];
        tableau[j]  = temp;
    }

    // Plusieurs paramètres de type
    public static <K, V> Map<V, K> inverser(Map<K, V> map) {
        Map<V, K> resultat = new HashMap<>();
        map.forEach((k, v) -> resultat.put(v, k));
        return resultat;
    }
}

String[] mots = {"chat", "chien", "oiseau"};
Utils.echanger(mots, 0, 2);  // le compilateur infère T = String
```

## Bornes de type (Bounded Type Parameters)

### Borne supérieure — `extends`

```java
// T doit être Number ou une sous-classe (Integer, Double, etc.)
public static <T extends Number> double somme(List<T> liste) {
    double total = 0;
    for (T element : liste) {
        total += element.doubleValue();  // méthode de Number accessible
    }
    return total;
}

somme(List.of(1, 2, 3));        // T = Integer
somme(List.of(1.5, 2.5));      // T = Double
// somme(List.of("a", "b"));   // erreur de compilation
```

### Intersection de types

```java
// T doit implémenter Comparable ET Serializable
public static <T extends Comparable<T> & Serializable> T maximum(T a, T b) {
    return a.compareTo(b) >= 0 ? a : b;
}
```

## Wildcards (?)

Les wildcards expriment une inconnue de type dans les paramètres de méthode. Ils ne servent pas à déclarer des variables locales.

### Wildcard non borné — `<?>`

```java
// Accepte List<String>, List<Integer>, List<Objet>...
public static void afficher(List<?> liste) {
    for (Object element : liste) {
        System.out.println(element);
    }
}
```

### Wildcard borné supérieur — `<? extends T>`

Pour **lire** depuis une collection : le type est T ou une sous-classe de T.

```java
// Accepte List<Integer>, List<Double>, List<Long>...
public static double sommerWildcard(List<? extends Number> liste) {
    return liste.stream().mapToDouble(Number::doubleValue).sum();
}

List<Integer> entiers = List.of(1, 2, 3);
List<Double>  doubles = List.of(1.5, 2.5);
sommerWildcard(entiers);  // ok
sommerWildcard(doubles);  // ok
```

### Wildcard borné inférieur — `<? super T>`

Pour **écrire** dans une collection : le type est T ou un super-type de T.

```java
// Accepte List<Integer>, List<Number>, List<Object>
public static void ajouterEntiers(List<? super Integer> liste) {
    liste.add(1);
    liste.add(2);
    liste.add(3);
}
```

### Principe PECS (Producer Extends, Consumer Super)

| Usage | Wildcard | Mnémotechnique |
|---|---|---|
| Lire depuis la collection | `? extends T` | **P**roducer **E**xtends |
| Écrire dans la collection | `? super T` | **C**onsumer **S**uper |
| Lire et écrire | `T` (paramètre borné) | pas de wildcard |

```java
// Copier les éléments de src vers dst
public static <T> void copier(List<? extends T> src, List<? super T> dst) {
    for (T element : src) {
        dst.add(element);
    }
}
```

## Type Erasure

Java implémente les génériques par **effacement de type** : à la compilation, les paramètres de type sont remplacés par leur borne (`Object` si non borné, ou la borne supérieure). Le bytecode ne contient plus d'information de type générique.

```java
// Code source
List<String> strings = new ArrayList<>();
List<Integer> ints   = new ArrayList<>();

// Après effacement (bytecode)
List strings = new ArrayList();
List ints    = new ArrayList();

// Conséquence : au runtime, les deux ont le même type
System.out.println(strings.getClass() == ints.getClass());  // true
```

### Limites dues à l'effacement

```java
// Impossible de créer des tableaux génériques
T[] tableau = new T[10];                // erreur de compilation

// Impossible d'utiliser instanceof avec un type générique
if (objet instanceof List<String>) {}   // erreur de compilation
if (objet instanceof List<?>)      {}   // ok (wildcard non borné)

// Impossible d'instancier T directement
T instance = new T();                   // erreur de compilation

// Contournement par réflexion
public static <T> T creer(Class<T> clazz) throws Exception {
    return clazz.getDeclaredConstructor().newInstance();
}
```

## Comparable et Comparator

```java
// Comparable — ordre naturel (implements dans la classe)
public class Etudiant implements Comparable<Etudiant> {
    String nom;
    double moyenne;

    @Override
    public int compareTo(Etudiant autre) {
        return Double.compare(this.moyenne, autre.moyenne);
    }
}

List<Etudiant> liste = new ArrayList<>(/* ... */);
Collections.sort(liste);   // utilise compareTo

// Comparator — ordre externe, plusieurs critères
Comparator<Etudiant> parNom = Comparator.comparing(e -> e.nom);
Comparator<Etudiant> parMoyenneDesc = Comparator
    .comparingDouble((Etudiant e) -> e.moyenne)
    .reversed();
Comparator<Etudiant> compose = parNom.thenComparing(parMoyenneDesc);

liste.sort(compose);
```

## Collections génériques — interfaces principales

```
Iterable<T>
└── Collection<T>
    ├── List<T>      → ArrayList, LinkedList
    ├── Set<T>       → HashSet, TreeSet, LinkedHashSet
    └── Queue<T>     → ArrayDeque, PriorityQueue
Map<K, V>            → HashMap, TreeMap, LinkedHashMap
```

```java
// Déclaration via l'interface (recommandé)
List<String>       liste   = new ArrayList<>();
Set<Integer>       ensemble = new HashSet<>();
Map<String, Long>  compteur = new HashMap<>();
Deque<Double>      pile    = new ArrayDeque<>();
```

## Récapitulatif des paramètres de type conventionnels

| Lettre | Convention |
|---|---|
| `T` | Type générique (Type) |
| `E` | Élément (collections) |
| `K` | Clé (Key) |
| `V` | Valeur (Value) |
| `N` | Nombre (Number) |
| `R` | Résultat (Return type) |
| `A`, `B` | Paires de types |

---
title: "HashMap"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-16"
---

# HashMap

`HashMap<K, V>` est la structure de données de Java pour associer des clés à des valeurs (table de hachage). Elle fait partie de l'interface `Map<K, V>` du framework Collections.

## Principe de fonctionnement

Une HashMap maintient un tableau interne de buckets. Lors d'une insertion, la clé est passée à `hashCode()`, puis le hash est réduit modulo la capacité pour obtenir l'index du bucket. En cas de collision, les entrées sont chaînées (liste chaînée ou arbre rouge-noir si la chaîne dépasse 8 éléments depuis Java 8).

```
Clé "alice" → hashCode() → 1234567 → 1234567 % 16 = 7 → bucket[7] → entrée ("alice", objet)
```

**Facteur de charge** : quand le taux de remplissage dépasse 0.75 (par défaut), la capacité est doublée (rehashing). Le rehashing recopie toutes les entrées dans le nouveau tableau — O(n) ponctuel, O(1) amorti.

## Importer et créer

```java
import java.util.HashMap;
import java.util.Map;

// Création standard
HashMap<String, Integer> scores = new HashMap<>();

// Via l'interface Map (recommandé pour le polymorphisme)
Map<String, Integer> scores = new HashMap<>();

// Avec capacité initiale et facteur de charge personnalisés
Map<String, Integer> scores = new HashMap<>(32, 0.6f);

// Copier une autre Map
Map<String, Integer> copie = new HashMap<>(scores);
```

## Opérations CRUD

```java
Map<String, Integer> scores = new HashMap<>();

// Insérer / Mettre à jour
scores.put("Alice", 95);
scores.put("Bob", 82);
scores.put("Alice", 98);  // Écrase l'ancienne valeur — retourne 95

// Lire
int s = scores.get("Alice");         // 98
int defaut = scores.getOrDefault("Charlie", 0);  // 0 — clé absente

// Vérifier l'existence
boolean existeClé  = scores.containsKey("Bob");     // true
boolean existeVal  = scores.containsValue(82);       // true

// Taille et vacuité
int taille = scores.size();       // 2
boolean vide = scores.isEmpty();  // false

// Supprimer
scores.remove("Bob");             // supprime l'entrée
scores.remove("Alice", 99);      // supprime seulement si la valeur associée est 99

// Vider
scores.clear();
```

## Opérations avancées (Java 8+)

```java
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);
scores.put("Bob", 82);

// putIfAbsent — n'écrase pas si la clé existe déjà
scores.putIfAbsent("Alice", 0);   // Alice conserve 95
scores.putIfAbsent("Charlie", 75); // Charlie est ajouté avec 75

// computeIfAbsent — calculer et insérer si absent
Map<String, List<String>> groupes = new HashMap<>();
groupes.computeIfAbsent("A", k -> new ArrayList<>()).add("Alice");
groupes.computeIfAbsent("A", k -> new ArrayList<>()).add("Bob");
// groupes.get("A") == ["Alice", "Bob"]

// computeIfPresent — modifier uniquement si la clé existe
scores.computeIfPresent("Alice", (clé, val) -> val + 5); // Alice → 100

// compute — calculer dans tous les cas
scores.compute("Alice", (clé, val) -> val == null ? 0 : val + 10); // 110

// merge — fusionner une nouvelle valeur avec l'existante
scores.merge("Alice", 5, Integer::sum);  // Alice → 115
scores.merge("Nouveau", 50, Integer::sum); // Nouveau → 50

// replaceAll — modifier toutes les valeurs
scores.replaceAll((clé, val) -> val * 2); // doubler tous les scores

// getOrDefault pour les lookups sûrs
int note = scores.getOrDefault("Inconnu", -1); // -1
```

## Itération

```java
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);
scores.put("Bob", 82);
scores.put("Charlie", 78);

// 1. forEach (Java 8+) — le plus lisible
scores.forEach((clé, valeur) ->
    System.out.printf("%-10s : %d%n", clé, valeur));

// 2. entrySet — accès aux paires clé-valeur
for (Map.Entry<String, Integer> entrée : scores.entrySet()) {
    System.out.println(entrée.getKey() + " → " + entrée.getValue());
}

// 3. keySet — uniquement les clés
for (String clé : scores.keySet()) {
    System.out.println(clé);
}

// 4. values — uniquement les valeurs
for (int valeur : scores.values()) {
    System.out.println(valeur);
}

// 5. Stream
scores.entrySet().stream()
    .filter(e -> e.getValue() >= 90)
    .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
    .forEach(e -> System.out.println(e.getKey() + " : " + e.getValue()));
```

## HashMap vs autres implémentations de Map

| Classe | Ordre | Null key | Thread-safe | Performances |
|---|---|---|---|---|
| `HashMap` | Non garanti | Oui (1 max) | Non | Meilleur en général |
| `LinkedHashMap` | Insertion ou accès | Oui (1 max) | Non | Légèrement plus lent |
| `TreeMap` | Trié par clé (Comparable) | Non | Non | O(log n) |
| `Hashtable` | Non garanti | Non | Oui (synchronisé) | Lent (legacy) |
| `ConcurrentHashMap` | Non garanti | Non | Oui | Haute performance multi-thread |

**LinkedHashMap** : étend HashMap en maintenant une liste doublement chaînée des entrées. Parfait pour le cache LRU.

```java
// Cache LRU avec LinkedHashMap
Map<String, String> cache = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, String> eldest) {
        return size() > 100;  // limite à 100 entrées
    }
};
```

**TreeMap** : les clés sont triées selon leur ordre naturel ou un `Comparator`. Accès, insertion et suppression en O(log n).

```java
TreeMap<String, Integer> arbre = new TreeMap<>();
arbre.put("Charlie", 78);
arbre.put("Alice", 95);
arbre.put("Bob", 82);

System.out.println(arbre.firstKey()); // "Alice" (ordre alphabétique)
System.out.println(arbre.lastKey());  // "Charlie"
System.out.println(arbre.headMap("Bob")); // {Alice=95} — clés < "Bob"
System.out.println(arbre.tailMap("Bob")); // {Bob=82, Charlie=78} — clés >= "Bob"
```

## HashMap et ConcurrentHashMap (multi-threading)

`HashMap` n'est pas thread-safe. En contexte multi-thread :

```java
// Option 1 : ConcurrentHashMap (haute performance)
import java.util.concurrent.ConcurrentHashMap;
Map<String, Integer> concurrent = new ConcurrentHashMap<>();

// Option 2 : Collections.synchronizedMap (simple mais moins performant)
Map<String, Integer> sync = Collections.synchronizedMap(new HashMap<>());
// Nécessite une synchronisation externe pour les itérations :
synchronized (sync) {
    for (Map.Entry<String, Integer> e : sync.entrySet()) { ... }
}
```

`ConcurrentHashMap` utilise un segmentation fine (segment locking ou lock stripping) pour permettre des lectures et écritures concurrentes sur différents buckets sans bloquer la map entière.

## Règles pour les clés

Pour que HashMap fonctionne correctement, les objets utilisés comme clés doivent :

1. Implémenter `equals()` de façon cohérente
2. Implémenter `hashCode()` tel que : si `a.equals(b)` alors `a.hashCode() == b.hashCode()`
3. Être immuables (ou leurs champs utilisés dans `hashCode`/`equals` ne doivent pas changer après insertion)

```java
// Mauvais exemple : utiliser un objet mutable comme clé
List<String> liste = new ArrayList<>(Arrays.asList("a", "b"));
map.put(liste, 42);
liste.add("c");        // Modifie le hashCode !
map.get(liste);        // Peut retourner null — la clé n'est plus retrouvable
```

## Complexité

| Opération | Complexité moyenne | Complexité pire cas |
|---|---|---|
| `put` | O(1) amorti | O(n) — toutes les clés dans le même bucket |
| `get` | O(1) | O(n) ou O(log n) avec arbre (Java 8+) |
| `remove` | O(1) | O(n) |
| `containsKey` | O(1) | O(n) |
| Itération | O(n + capacité) | O(n + capacité) |

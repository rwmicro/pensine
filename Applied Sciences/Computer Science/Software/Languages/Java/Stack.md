---
title: "Stack (Pile)"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-16"
---

# Stack (Pile)

Une pile est une structure de données abstraite qui suit le principe **LIFO** (Last In, First Out) : le dernier élément inséré est le premier à être retiré. On peut visualiser une pile comme une pile d'assiettes : on empile par le dessus, on désempile par le dessus.

## La classe Stack (legacy)

Java fournit une classe `Stack<E>` dans `java.util`, héritée de `Vector`. Cet héritage est considéré comme une erreur de conception : `Stack` hérite de toutes les méthodes de `Vector` (accès par index, insertion au milieu), ce qui viole la sémantique LIFO d'une pile et expose des opérations qui ne devraient pas exister sur une pile.

```java
import java.util.Stack;

Stack<Integer> pile = new Stack<>();
pile.push(10);
pile.push(20);
pile.push(30);

System.out.println(pile.pop());      // 30 — retire et retourne le sommet
System.out.println(pile.peek());     // 20 — consulte sans retirer
System.out.println(pile.search(10)); // 2 — position depuis le sommet (1-indexé)
System.out.println(pile.empty());    // false
System.out.println(pile.size());     // 2
```

`search(Object o)` retourne la distance depuis le sommet (1 = au sommet), ou -1 si l'élément est absent.

## Deque et ArrayDeque : l'approche recommandée

La documentation Java officielle recommande d'utiliser `Deque<E>` (double-ended queue) comme interface et `ArrayDeque<E>` comme implémentation lorsqu'on a besoin d'une pile. `ArrayDeque` est plus rapide que `Stack` car elle n'est pas synchronisée et n'a pas l'overhead de `Vector`.

```java
import java.util.Deque;
import java.util.ArrayDeque;

Deque<String> pile = new ArrayDeque<>();

// Empiler
pile.push("a");     // équivalent à addFirst()
pile.push("b");
pile.push("c");

// Sommet sans retirer
System.out.println(pile.peek());  // "c"

// Désempiler
System.out.println(pile.pop());   // "c" — équivalent à removeFirst()
System.out.println(pile.pop());   // "b"

// Vérification
System.out.println(pile.isEmpty()); // false
System.out.println(pile.size());    // 1
```

### Méthodes Deque utilisées comme Stack

| Opération pile | Méthode Deque (préférer) | Méthode sûre (ne lève pas d'exception) |
|---|---|---|
| Empiler | `push(e)` / `addFirst(e)` | `offerFirst(e)` |
| Désempiler | `pop()` / `removeFirst()` | `pollFirst()` (retourne null si vide) |
| Consulter sommet | `peek()` / `peekFirst()` | `peekFirst()` (retourne null si vide) |
| Taille | `size()` | — |
| Vide ? | `isEmpty()` | — |

## Stack vs Queue

| Critère | Stack (Pile) | Queue (File) |
|---|---|---|
| Principe | LIFO | FIFO (First In, First Out) |
| Insertion | `push` (sommet) | `offer` / `add` (queue) |
| Retrait | `pop` (sommet) | `poll` / `remove` (tête) |
| Interface Java | `Deque` (côté head) | `Queue` |
| Implémentation | `ArrayDeque` | `ArrayDeque` ou `LinkedList` |
| Cas d'usage typique | DFS, annulation, parsing | BFS, traitement par lots, messaging |

`ArrayDeque` peut servir à la fois de pile et de file selon les méthodes utilisées.

## Implémentation d'une pile avec liste chaînée

Implémenter une pile manuellement est un exercice classique qui illustre le chaînage de noeuds.

```java
public class PileChainee<T> {

    private static class Noeud<T> {
        T valeur;
        Noeud<T> suivant;

        Noeud(T valeur, Noeud<T> suivant) {
            this.valeur  = valeur;
            this.suivant = suivant;
        }
    }

    private Noeud<T> sommet = null;
    private int taille = 0;

    public void push(T valeur) {
        sommet = new Noeud<>(valeur, sommet);
        taille++;
    }

    public T pop() {
        if (isEmpty()) throw new java.util.EmptyStackException();
        T val = sommet.valeur;
        sommet = sommet.suivant;
        taille--;
        return val;
    }

    public T peek() {
        if (isEmpty()) throw new java.util.EmptyStackException();
        return sommet.valeur;
    }

    public boolean isEmpty() { return sommet == null; }
    public int size()        { return taille; }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("[");
        Noeud<T> courant = sommet;
        while (courant != null) {
            sb.append(courant.valeur);
            if (courant.suivant != null) sb.append(", ");
            courant = courant.suivant;
        }
        return sb.append("]").toString();
    }
}
```

## Complexité des opérations

| Opération | Complexité | Notes |
|---|---|---|
| `push` | O(1) | Insertion en tête (liste chaînée) ou redimensionnement amortissable (ArrayDeque) |
| `pop` | O(1) | Suppression en tête |
| `peek` | O(1) | Lecture seule du sommet |
| `isEmpty` | O(1) | |
| `size` | O(1) | |
| `search` (Stack legacy) | O(n) | Parcours linéaire |

`ArrayDeque` utilise un tableau circulaire qui se redimensionne (doublement) lorsqu'il est plein. Le coût amorti de `push` reste O(1) même avec des redimensionnements occasionnels.

## Cas d'usage

### Évaluation d'expressions mathématiques (notation polonaise inverse)

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class RPN {
    public static int evaluer(String[] tokens) {
        Deque<Integer> pile = new ArrayDeque<>();
        for (String t : tokens) {
            switch (t) {
                case "+" -> { int b = pile.pop(); pile.push(pile.pop() + b); }
                case "-" -> { int b = pile.pop(); pile.push(pile.pop() - b); }
                case "*" -> { int b = pile.pop(); pile.push(pile.pop() * b); }
                default  -> pile.push(Integer.parseInt(t));
            }
        }
        return pile.pop();
    }

    public static void main(String[] args) {
        // "3 4 + 2 *" = (3 + 4) * 2 = 14
        System.out.println(evaluer(new String[]{"3", "4", "+", "2", "*"}));
    }
}
```

### DFS (Depth-First Search) itératif

```java
import java.util.*;

public class DFS {
    static void dfs(Map<Integer, List<Integer>> graphe, int depart) {
        Deque<Integer> pile    = new ArrayDeque<>();
        Set<Integer>   visites = new HashSet<>();
        pile.push(depart);

        while (!pile.isEmpty()) {
            int noeud = pile.pop();
            if (visites.contains(noeud)) continue;
            visites.add(noeud);
            System.out.println("Visite : " + noeud);
            for (int voisin : graphe.getOrDefault(noeud, List.of())) {
                if (!visites.contains(voisin)) pile.push(voisin);
            }
        }
    }
}
```

### Vérification des parenthèses

```java
public static boolean estEquilibre(String s) {
    Deque<Character> pile = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        if (c == '(' || c == '[' || c == '{') {
            pile.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (pile.isEmpty()) return false;
            char ouverture = pile.pop();
            if ((c == ')' && ouverture != '(') ||
                (c == ']' && ouverture != '[') ||
                (c == '}' && ouverture != '{')) return false;
        }
    }
    return pile.isEmpty();
}
```

### Undo/Redo

```java
Deque<String> historique = new ArrayDeque<>();
Deque<String> futur      = new ArrayDeque<>();

void executer(String action) {
    historique.push(action);
    futur.clear();
}

void annuler() {
    if (!historique.isEmpty()) futur.push(historique.pop());
}

void retablir() {
    if (!futur.isEmpty()) historique.push(futur.pop());
}
```


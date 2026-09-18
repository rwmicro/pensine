---
title: "Assembleur x86-64"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Assembleur"
tags: [sciences-appliquées, informatique, assembleur, x86-64, nasm, bas-niveau, linux]
date: "2026-09-18"
---

# Assembleur x86-64

Tous les langages de programmation sont des fictions utiles. Une variable, une fonction, un objet n'existent pas dans le processeur : ce sont des conventions que le compilateur traduit en quelque chose de beaucoup plus pauvre. L'assembleur est le niveau où ces fictions s'arrêtent. Il ne reste que trois choses : des registres, de la mémoire, et une liste d'instructions que le processeur sait exécuter.

Cette note couvre l'assembleur x86-64 sous Linux, avec la syntaxe NASM. Elle sert de socle à [[Reverse Engineering]] et [[Binary Exploitation]], qui supposent tous deux qu'on sait lire ce que produit un désassembleur.

> [!important] Idée clé
> L'assembleur n'est pas un langage de plus dans la liste. C'est la **nomenclature des opérations que le matériel sait faire**, et rien d'autre. Il n'y a pas de types : un registre contient 64 bits, l'interprétation de ces bits — entier signé, adresse, caractère — n'existe que dans la tête du programmeur. Il n'y a pas de fonctions : seulement des adresses vers lesquelles on saute, avec une convention partagée sur qui range quoi où. Il n'y a pas de portée : tout est visible par tout le monde. Comprendre l'assembleur, c'est surtout comprendre que **tout ce qui structure un programme de haut niveau est une discipline volontaire**, pas une contrainte du matériel.

## Pourquoi des registres

Le processeur ne calcule que sur des données qu'il a sous la main. La mémoire principale est un réservoir immense mais lointain : les ordres de grandeur sont sans appel.

| Emplacement | Latence approximative |
|---|---|
| Registre | sous la nanoseconde |
| Cache L1 | environ 1 ns |
| Mémoire principale | environ 100 ns |

Un accès à la RAM coûte donc cent fois un accès au cache L1, et davantage encore par rapport à un registre. Les **registres généraux** sont ces quelques emplacements minuscules, internes au processeur, où les données doivent transiter pour être traitées. Leur rareté est la contrainte structurante de toute la programmation en assembleur : x86-64 n'en offre que seize.

| Registre 64 bits | 32 bits | 16 bits | 8 bits (bas) |
|---|---|---|---|
| `rax` | `eax` | `ax` | `al` |
| `rbx` | `ebx` | `bx` | `bl` |
| `rcx` | `ecx` | `cx` | `cl` |
| `rdx` | `edx` | `dx` | `dl` |
| `rsi` | `esi` | `si` | `sil` |
| `rdi` | `edi` | `di` | `dil` |
| `rbp` | `ebp` | `bp` | `bpl` |
| `rsp` | `esp` | `sp` | `spl` |
| `r8` à `r15` | `r8d` à `r15d` | `r8w` à `r15w` | `r8b` à `r15b` |

Ce ne sont pas seize registres plus des variantes : ce sont les **mêmes** registres vus par une fenêtre plus étroite. Écrire dans `al` modifie les huit bits de poids faible de `rax` et laisse le reste intact. Les quatre premiers offrent en plus un accès aux bits 8 à 15 sous les noms `ah`, `bh`, `ch`, `dh`, héritage de l'architecture 16 bits.

> [!warning] Piège
> Écrire dans un registre 32 bits **remet à zéro les 32 bits hauts** du registre 64 bits correspondant. `mov eax, 1` met `rax` à 1, pas seulement ses 32 bits bas. Cette règle ne vaut que pour les écritures 32 bits : `mov al, 1` et `mov ax, 1` préservent, eux, le reste du registre. C'est l'asymétrie la plus déroutante de l'architecture, et elle explique pourquoi les compilateurs émettent si souvent `xor eax, eax` là où on attendrait `xor rax, rax` — l'encodage est plus court et l'effet identique.

Le x86-64 dispose d'autres familles de registres — segment, contrôle, débogage, `rflags`, et les registres vectoriels `xmm`/`ymm`/`zmm` utilisés pour le flottant et le SIMD. Les registres généraux suffisent pour l'essentiel du code entier.

## Boutisme

Un mot de plusieurs octets doit être rangé en mémoire dans un ordre. Le x86-64 est **petit-boutiste** (*little-endian*) : l'octet de poids le plus faible occupe l'adresse la plus basse.

Pour la valeur `0x0A0B0C0D` rangée à partir de l'adresse 0 :

| Ordre | adresse 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Petit-boutiste (x86-64) | `0x0D` | `0x0C` | `0x0B` | `0x0A` |
| Grand-boutiste (réseau, SPARC) | `0x0A` | `0x0B` | `0x0C` | `0x0D` |

C'est ce qui donne aux vidages hexadécimaux leur allure d'octets inversés, et c'est la source d'une classe entière de bogues dès qu'on lit un format de fichier ou une trame réseau, qui sont eux conventionnellement grand-boutistes.

## Anatomie d'un programme

Un programme assembleur se découpe en **sections**, qui deviendront les segments de l'exécutable.

| Section | Contenu |
|---|---|
| `.data` | Données initialisées, durée de vie du programme |
| `.bss` | Données non initialisées, réservées mais non stockées dans le fichier |
| `.text` | Le code, c'est-à-dire les instructions |
| `.rodata` | Données constantes en lecture seule |

Chaque ligne suit une structure unique :

```
[étiquette:] instruction [opérandes] [; commentaire]
```

Les crochets marquent ce qui est facultatif. Une instruction se lit comme un appel de fonction dont les opérandes seraient les paramètres, la destination venant toujours en premier en syntaxe Intel :

```assembly
mov rax, 48    ; place la valeur 48 dans rax
```

### Le point d'entrée

Le processeur doit savoir où commencer. C'est le rôle du symbole `_start`, désigné comme point d'entrée par l'éditeur de liens, ce qui suppose qu'il soit visible depuis l'extérieur du fichier objet — d'où la directive `global`.

```assembly
section .text
        global _start

_start:
```

### La chaîne de construction

```mermaid
flowchart LR
    A["hello.asm<br/>source NASM"] -->|"nasm -f elf64"| B["hello.o<br/>fichier objet"]
    B -->|"ld"| C["hello<br/>exécutable ELF"]
    C -->|"execve"| D["processus en mémoire"]
```

```bash
nasm -f elf64 -o hello.o hello.asm   # assemblage vers un fichier objet
ld -o hello hello.o                  # édition de liens vers un exécutable
readelf -S hello                     # inspection des sections du binaire produit
```

L'assemblage traduit les instructions en code machine mais laisse les adresses indéterminées ; l'édition de liens les résout et fixe le point d'entrée. Le résultat est un fichier au format **ELF**, le format exécutable standard sous Linux, décrit dans [[Fondamentaux]]. `readelf -S` montre que l'éditeur de liens a ajouté ses propres sections à celles qu'on avait déclarées.

## Déclarer des données

NASM fournit des pseudo-instructions pour réserver de la place, nommées d'après la taille.

| Pseudo-instruction | Taille | Nom |
|---|---|---|
| `DB` | 1 octet | *byte* |
| `DW` | 2 octets | *word* |
| `DD` | 4 octets | *doubleword* |
| `DQ` | 8 octets | *quadword* |
| `DT`, `DO`, `DY`, `DZ` | 10, 16, 32, 64 octets | formats étendus et vectoriels |

```assembly
section .data
        num1 db 100                  ; un octet valant 100
        num2 dw 1024                 ; deux octets valant 1024
        msg  db "Somme correcte", 10 ; chaîne suivie du saut de ligne (10 en ASCII)

section .bss
        buffer resb 64               ; 64 octets réservés, non initialisés
```

Les variantes `RESB` à `RESZ` réservent sans initialiser : elles n'occupent aucune place dans le fichier, seulement dans la mémoire du processus au chargement.

> [!warning] Piège
> En syntaxe NASM, écrire le nom d'une variable donne son **adresse**, pas son contenu. Il faut des crochets pour déréférencer.
> ```assembly
> mov rax, msg          ; rax reçoit l'ADRESSE de msg
> mov rax, [rel msg]    ; rax reçoit le CONTENU de msg
> ```
> Le préfixe `rel` demande un adressage relatif au compteur ordinal (`rip`), nécessaire pour produire du code indépendant de la position — condition de l'ASLR. La directive `default rel` en tête de fichier l'applique partout et évite d'y penser à chaque ligne.

## Parler au noyau

L'assembleur n'a pas de bibliothèque standard. Pour afficher un texte, deux voies seulement : lier le programme à la bibliothèque C et appeler `printf`, ou s'adresser directement au noyau par un **appel système**.

La seconde voie est la plus instructive, car elle met à nu ce que fait réellement `printf` au fond de sa pile d'abstractions. Les appels système de Linux x86-64 sont numérotés ; la table de correspondance vit dans les sources du noyau, sous `arch/x86/entry/syscalls/syscall_64.tbl`.

La convention est fixée par l'**ABI System V**, et c'est ici que se niche le piège le plus classique : les appels système et les fonctions ordinaires n'utilisent pas les mêmes registres.

| Rôle | Appel système (`syscall`) | Fonction (`call`) |
|---|---|---|
| Numéro / — | `rax` | sans objet |
| 1er argument | `rdi` | `rdi` |
| 2e argument | `rsi` | `rsi` |
| 3e argument | `rdx` | `rdx` |
| **4e argument** | **`r10`** | **`rcx`** |
| 5e argument | `r8` | `r8` |
| 6e argument | `r9` | `r9` |
| Au-delà de 6 | impossible | sur la pile |
| Valeur de retour | `rax` | `rax` |

> [!warning] Piège
> Le quatrième argument passe par `r10` pour un appel système et par `rcx` pour un appel de fonction. La raison est matérielle : l'instruction `syscall` écrase `rcx`, où le processeur range l'adresse de retour, ainsi que `r11`, où il sauvegarde `rflags`. `rcx` était donc inutilisable comme registre d'argument. Conséquence pratique : **toute valeur utile détenue dans `rcx` ou `r11` est perdue après un `syscall`**, et il faut la sauvegarder avant.

### Exemple complet

```assembly
;; Affiche un message puis sort proprement
section .data
        msg db "hello, world!", 10   ; 14 octets au total

section .text
        global _start

_start:
        ;; sys_write(1, msg, 14)
        mov rax, 1          ; numéro de l'appel système : write
        mov rdi, 1          ; 1er argument : descripteur 1, la sortie standard
        mov rsi, msg        ; 2e argument : adresse du tampon
        mov rdx, 14         ; 3e argument : nombre d'octets à écrire
        syscall

        ;; sys_exit(0)
        mov rax, 60         ; numéro de l'appel système : exit
        mov rdi, 0          ; 1er argument : code de retour, 0 pour succès
        syscall
```

> [!tip] À retenir
> L'appel à `sys_exit` n'est pas une politesse. Sans lui, l'exécution continue au-delà de la dernière instruction, sur ce qui suit en mémoire — et le programme se termine par une erreur de segmentation. Il n'existe pas de « fin de programme » implicite : la sortie est un appel système comme un autre.

## La pile

Seize registres ne suffisent jamais. La **pile** est la réponse de l'architecture à cette pénurie : une zone de mémoire ordinaire, mais dont l'accès suit une discipline dernier entré, premier sorti.

Deux propriétés la rendent contre-intuitive :

- Elle **croît vers les adresses basses**. « Empiler » diminue l'adresse ; le « sommet » de la pile est son adresse la plus basse.
- Elle est gérée par trois registres dédiés.

| Registre | Nom | Rôle |
|---|---|---|
| `rsp` | *stack pointer* | Pointe le sommet de la pile. `push` le décrémente de 8, `pop` l'incrémente |
| `rbp` | *base pointer* | Pointe la base du cadre de la fonction courante, point d'ancrage fixe |
| `rip` | *instruction pointer* | Adresse de la prochaine instruction. `call` l'empile, `ret` le dépile |

### Cadre de pile

Chaque fonction se taille une tranche de pile, son **cadre**. Elle l'ouvre par un prologue et le referme par un épilogue :

```assembly
foo:
        push rbp          ; prologue : sauvegarde la base de l'appelant
        mov  rbp, rsp     ;            installe la nouvelle base

        ;; corps de la fonction

        mov rsp, rbp      ; épilogue : libère les locales
        pop rbp           ;            restaure la base de l'appelant
        ret               ; dépile l'adresse de retour et y saute
```

Une fois `rbp` installé, il ne bouge plus de toute la fonction. Il devient le repère par rapport auquel tout s'adresse, et le signe de l'écart dit la nature de ce qu'on atteint :

| Adresse | Contenu |
|---|---|
| `[rbp+16]` et au-delà | 7e argument et suivants, empilés par l'appelant |
| `[rbp+8]` | Adresse de retour, empilée par `call` |
| `[rbp]` | Ancien `rbp`, sauvegardé par le prologue |
| `[rbp-8]`, `[rbp-16]`… | Variables locales de la fonction courante |

> [!important] Idée clé
> **Les décalages positifs remontent vers l'appelant, les négatifs descendent dans la fonction courante.** C'est toute la logique du cadre de pile, et c'est ce qui permet à un désassembleur — ou à un lecteur humain — de reconstituer la signature et les variables locales d'une fonction dont on n'a pas le code source. Une instruction `mov DWORD [rbp-4], edi` se lit sans ambiguïté : le premier argument, entier 32 bits, est recopié dans la première variable locale.

Les instructions `enter` et `leave` condensent prologue et épilogue. `leave` équivaut exactement à `mov rsp, rbp` suivi de `pop rbp`, et reste couramment émis par les compilateurs ; `enter`, en revanche, est notoirement lent et pratiquement abandonné.

> [!warning] Piège
> L'ABI System V exige que `rsp` soit **aligné sur 16 octets au moment où s'exécute un `call`**. Un `push` de trop et l'alignement est rompu : le programme fonctionne tant qu'il reste en assembleur pur, puis s'effondre sans explication dès le premier appel à une fonction de la bibliothèque C qui utilise des instructions SSE, lesquelles exigent cet alignement. C'est l'une des causes les plus fréquentes de plantage inexplicable chez qui débute.

## Contrôle de flux

Il n'y a ni `if`, ni `while`, ni `for` — seulement des comparaisons qui positionnent des drapeaux, et des sauts qui les consultent.

L'instruction `cmp` effectue une soustraction dont elle jette le résultat, ne conservant que son effet sur le registre `rflags`. Les sauts conditionnels lisent ensuite ces drapeaux.

| Instruction | Saute si | Comparaison |
|---|---|---|
| `JE` / `JZ` | égal | — |
| `JNE` / `JNZ` | différent | — |
| `JG` / `JGE` | supérieur / supérieur ou égal | signée |
| `JL` / `JLE` | inférieur / inférieur ou égal | signée |
| `JA` / `JAE` | supérieur / supérieur ou égal | non signée |
| `JB` / `JBE` | inférieur / inférieur ou égal | non signée |
| `JMP` | toujours | — |

```assembly
        cmp rax, 50       ; compare rax à 50
        jne .autre        ; si différent, saute à .autre
        ;; suite exécutée si rax vaut 50
.autre:
```

> [!warning] Piège
> Deux familles de sauts existent pour la même comparaison apparente : `JG`/`JL` interprètent les valeurs comme signées, `JA`/`JB` comme non signées. Le processeur ne sait pas ce que représentent les bits qu'il compare : **c'est le choix de l'instruction de saut qui tranche**. Confondre les deux produit un code correct sur les petites valeurs et faux dès qu'un bit de poids fort est mis — une valeur non signée supérieure à 2^63 étant lue comme un nombre négatif.

Les boucles se construisent avec une étiquette et un saut arrière : on place l'étiquette avant le corps, on teste la condition à la fin, et on retourne à l'étiquette tant qu'elle tient.

## Arithmétique

| Instruction | Opération |
|---|---|
| `ADD`, `SUB` | Addition, soustraction |
| `MUL`, `IMUL` | Multiplication non signée, signée |
| `DIV`, `IDIV` | Division non signée, signée |
| `INC`, `DEC` | Incrémentation, décrémentation |
| `NEG` | Négation |

> [!warning] Piège
> `DIV` et `IDIV` ne prennent qu'un opérande, le diviseur, et travaillent sur des registres implicites : le dividende est le couple `rdx:rax` pris comme un entier de 128 bits, le quotient atterrit dans `rax` et le reste dans `rdx`. **Oublier de mettre `rdx` à zéro avant une division 64 bits** fait diviser par un dividende arbitraire, ce qui provoque le plus souvent une exception matérielle et la mort immédiate du processus. Le réflexe est `xor rdx, rdx` juste avant `div`.

## Ce que l'assembleur révèle de la sécurité

Le mécanisme d'appel de fonction est bâti sur une confiance totale : `ret` dépile huit octets et saute à l'adresse ainsi obtenue, **sans la vérifier**. Si un écrasement de tampon a remplacé l'adresse de retour rangée en `[rbp+8]`, le processeur saute où on lui dit de sauter. C'est le fondement du débordement de pile.

```C
void foo() {
    char buffer[8];
    gets(buffer);        // aucune borne : écrit autant que l'entrée en fournit
}
```

Le tampon occupe `[rbp-8]` à `[rbp-1]`. Neuf caractères saisis, et l'écriture mord sur l'ancien `rbp` ; quelques-uns de plus, et elle atteint l'adresse de retour.

Les défenses modernes découlent toutes de cette lecture :

| Protection | Principe |
|---|---|
| Canaris de pile | Une valeur aléatoire placée entre les locales et l'adresse de retour, vérifiée à la sortie de la fonction |
| ASLR | Randomisation des adresses de chargement, qui rend imprévisible l'adresse vers laquelle détourner l'exécution |
| Pile non exécutable (NX) | La pile est marquée non exécutable : y injecter du code ne sert plus à rien |

Aucune n'élimine la classe de vulnérabilités, elles en augmentent le coût — d'où le déplacement des techniques d'exploitation vers la réutilisation de code déjà présent et exécutable, développée dans [[Binary Exploitation]].

> [!tip] À retenir
> Les erreurs de disposition de pile ne sont pas cantonnées au code étudiant. **CVE-2017-1000253** visait le chargeur d'exécutables du noyau Linux : l'espace de garde de 128 Mo censé séparer la pile du programme chargé pouvait être franchi par un binaire suffisamment volumineux, ouvrant une élévation de privilèges. Voir [[Linux Privilege Escalation]].

## Cohabiter avec le C

L'assembleur pur est rare. Trois formes d'articulation avec un langage de haut niveau se rencontrent, toutes reposant sur le respect de la convention d'appel System V :

- **Appeler du C depuis l'assembleur** : déclarer le symbole `extern`, respecter les registres d'arguments et l'alignement de pile, lier avec `gcc` plutôt que `ld` pour embarquer la bibliothèque C.
- **Appeler de l'assembleur depuis le C** : exposer le symbole avec `global`, le déclarer `extern` côté C, assembler séparément et lier les deux fichiers objets.
- **Assembleur en ligne** : insérer des instructions dans une fonction C via `__asm__`, en déclarant au compilateur les registres lus, écrits et détruits. C'est la forme qu'on rencontre dans le noyau Linux pour les primitives que le C ne peut pas exprimer.

## Outillage

| Outil | Usage |
|---|---|
| `nasm` | Assembleur, syntaxe Intel |
| `ld`, `gcc` | Édition de liens, avec ou sans bibliothèque C |
| `objdump -d` | Désassemblage d'un binaire existant |
| `readelf -S` | Inspection des sections ELF |
| `gdb` | Exécution pas à pas, lecture des registres et de la pile |
| Compiler Explorer | Visualisation immédiate de l'assembleur produit par un compilateur |

> [!tip] Méthode
> La manière la plus rapide d'apprendre à lire l'assembleur n'est pas de l'écrire : c'est d'écrire du C simple, de le compiler **sans optimisation** (`-O0 -masm=intel`) et de lire ce que le compilateur en fait. Avec les optimisations actives, le compilateur élimine tout ce qui est calculable à la compilation et le rapport entre source et sortie devient illisible.

## À lire ensuite

- [[Architecture des Processeurs]] — pipeline, caches et exécution spéculative sous les instructions
- [[Systèmes Numériques]] — représentation binaire, complément à deux, logique booléenne
- [[Gestion de la Mémoire]] — pagination, mémoire virtuelle et espace d'adressage d'un processus
- [[Fondamentaux]] — format ELF, chargement d'un exécutable, frontière utilisateur/noyau
- [[Reverse Engineering]] — lire et comprendre un binaire dont on n'a pas la source
- [[Binary Exploitation]] — exploitation des débordements et contournement des protections
- [[Linux Privilege Escalation]] — élévation de privilèges, dont les vulnérabilités noyau

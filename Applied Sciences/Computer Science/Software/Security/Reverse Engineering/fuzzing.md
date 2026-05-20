---
title: "Fuzzing"
domain: "Applied Sciences"
subdomain: "Computer Science > Security"
tags: [sciences-appliquées, informatique, sécurité]
date: "2025-11-06"
---

# Fuzzing

Le fuzzing (ou fuzz testing) est une technique de test automatisé qui consiste à envoyer des données invalides, aléatoires ou inattendues à un système afin de découvrir des bugs, crashes, et vulnérabilités de sécurité.

## Principes fondamentaux

### Pourquoi fuzzer

Les développeurs pensent en termes de chemins valides ; les attaquants exploitent les chemins inattendus. Le fuzzing automatise l'exploration de l'espace d'entrée pour trouver :

- Débordements de tampon (buffer overflows)
- Use-after-free, double free, heap corruption
- Injections (SQL, commande, format string)
- Chemins non gérés provoquant des crashes ou des comportements undefined
- Fuites d'informations (divulgation de mémoire, paths internes)

### Types de fuzzers

| Type | Description | Exemples |
|------|-------------|---------|
| Blackbox | Aucune connaissance du code source | wfuzz, ffuf, Boofuzz |
| Greybox | Utilise la couverture de code comme feedback | AFL++, libFuzzer, Honggfuzz |
| Whitebox | Analyse symbolique ou concolic du code | KLEE, SAGE, SymCC |
| Mutation-based | Modifie des entrées valides existantes | AFL++, Radamsa |
| Generation-based | Génère des entrées depuis une grammaire | Peach, Boofuzz, grammarinator |

### Métriques clés

- **Couverture de code (code coverage)** : % de branches/lignes exécutées
- **Corpus** : ensemble des entrées de test collectées
- **Throughput** : nombre d'exécutions par seconde
- **Crash triage** : déduplication et classification des crashes

## Fuzzing web (découverte d'endpoints)

### ffuf — Fast web fuzzer

```bash
# Découverte de répertoires
ffuf -u http://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt

# Avec extension
ffuf -u http://target.com/FUZZ -w wordlist.txt -e .php,.html,.txt,.bak

# Fuzzing de paramètres GET
ffuf -u "http://target.com/page?FUZZ=value" -w params.txt

# Fuzzing de la valeur d'un paramètre
ffuf -u "http://target.com/page?id=FUZZ" -w /usr/share/wordlists/wfuzz/Injections/SQL.txt

# POST avec body JSON
ffuf -u http://target.com/api/login \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"username":"FUZZ","password":"test"}' \
     -w usernames.txt

# Filtrer par code HTTP (exclure 404)
ffuf -u http://target.com/FUZZ -w wordlist.txt -fc 404

# Filtrer par taille de réponse
ffuf -u http://target.com/FUZZ -w wordlist.txt -fs 1234

# Fuzzing de sous-domaines
ffuf -u http://FUZZ.target.com -w subdomains.txt -H "Host: FUZZ.target.com"

# Récursif
ffuf -u http://target.com/FUZZ -w wordlist.txt -recursion -recursion-depth 2

# Output JSON pour traitement
ffuf -u http://target.com/FUZZ -w wordlist.txt -o results.json -of json
```

### wfuzz

```bash
# Découverte basique
wfuzz -c -z file,wordlist.txt http://target.com/FUZZ

# Masquer codes 404
wfuzz -c -z file,wordlist.txt --hc 404 http://target.com/FUZZ

# Fuzzing de cookies
wfuzz -c -z file,payloads.txt -b "session=FUZZ" http://target.com/profile

# Authentification basique
wfuzz -c -z file,passwords.txt --basic admin:FUZZ http://target.com/admin
```

### Wordlists utiles

| Source | Chemin | Usage |
|--------|--------|-------|
| SecLists | `/usr/share/seclists/` | Référence complète |
| dirb | `/usr/share/wordlists/dirb/common.txt` | Répertoires courants |
| dirbuster | `/usr/share/wordlists/dirbuster/` | Découverte approfondie |
| rockyou | `/usr/share/wordlists/rockyou.txt` | Passwords |
| wfuzz | `/usr/share/wordlists/wfuzz/` | Payloads injection |

## Fuzzing réseau et protocoles

### Boofuzz — Framework Python pour protocoles réseau

```python
from boofuzz import *

def main():
    session = Session(
        target=Target(
            connection=TCPSocketConnection("192.168.1.100", 21)  # FTP
        )
    )

    s_initialize("FTP USER")
    s_static("USER ")
    s_string("administrator")  # champ fuzzé
    s_static("\r\n")

    session.connect(s_get("FTP USER"))
    session.fuzz()

if __name__ == "__main__":
    main()
```

### Radamsa — Mutateur générique

```bash
# Générer 100 mutations d'un input valide
echo "test_input" | radamsa -n 100 > fuzz_inputs.txt

# Muter un fichier (ex: PDF)
radamsa input.pdf -o fuzzed_##.pdf -n 1000

# Fuzzer une cible réseau directement
echo "GET / HTTP/1.0\r\n\r\n" | radamsa -n 100 | nc target.com 80
```

## Coverage-guided fuzzing (greybox)

### AFL++ — American Fuzzy Lop

Le fuzzer greybox de référence. Instrumente le binaire pour tracker la couverture de code, et priorise les inputs qui découvrent de nouvelles branches.

```bash
# Compiler avec instrumentation AFL
CC=afl-clang-fast ./configure
make

# Ou avec afl-gcc
afl-gcc -o target_afl source.c

# Créer le corpus initial
mkdir corpus_in corpus_out
echo "test" > corpus_in/seed1

# Lancer AFL++
afl-fuzz -i corpus_in -o corpus_out -- ./target_afl @@
# @@ : AFL remplace par le path du fichier généré

# Avec timeout personnalisé (ms)
afl-fuzz -i corpus_in -o corpus_out -t 1000 -- ./target_afl @@

# Fuzzing parallèle (maître + 3 secondaires)
afl-fuzz -i corpus_in -o corpus_out -M fuzzer1 -- ./target_afl @@
afl-fuzz -i corpus_in -o corpus_out -S fuzzer2 -- ./target_afl @@
afl-fuzz -i corpus_in -o corpus_out -S fuzzer3 -- ./target_afl @@

# Statistiques en temps réel
afl-whatsup corpus_out/

# Triage des crashes
afl-tmin -i corpus_out/crashes/id:000000 -o minimized -- ./target_afl @@
```

**Interprétation du dashboard AFL++ :**
- `total paths` : nombre de chemins de code uniques trouvés
- `crashes` : inputs provoquant un crash (SIGSEGV, SIGABRT, etc.)
- `hangs` : inputs dépassant le timeout
- `exec speed` : throughput (viser > 1000 exec/s)
- `stability` : cohérence de la couverture (< 90% = problème)

### libFuzzer — Fuzzing en-process

Intégré directement dans le binaire comme bibliothèque. Pas de fork(), très rapide.

```c
// target.c — fonction cible à fuzzer
#include <stdint.h>
#include <stddef.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;

    // Code à tester
    if (data[0] == 'F' && data[1] == 'U' &&
        data[2] == 'Z' && data[3] == 'Z') {
        __builtin_trap();  // Simule un bug
    }
    return 0;
}
```

```bash
# Compiler avec libFuzzer
clang -g -fsanitize=fuzzer,address target.c -o target_fuzz

# Lancer
./target_fuzz corpus_dir/ -max_len=1024

# Avec dictionnaire
./target_fuzz corpus_dir/ -dict=keywords.dict

# Reproduire un crash
./target_fuzz crash-abc123
```

### AddressSanitizer (ASan)

Détecter les accès mémoire invalides pendant le fuzzing :

```bash
# Compiler avec ASan + UBSan + fuzzer
clang -fsanitize=address,undefined,fuzzer target.c -o target_fuzz

# Variables d'environnement
ASAN_OPTIONS=abort_on_error=1:symbolize=1 ./target_fuzz corpus/
```

## Fuzzing d'APIs REST

### Schemathesis — Fuzzing basé sur OpenAPI

```bash
# Depuis une spec OpenAPI
schemathesis run http://api.target.com/openapi.json

# Tester les injections spécifiquement
schemathesis run http://api.target.com/openapi.json --checks all

# Depuis un fichier local
schemathesis run schema.yaml --base-url http://localhost:8000

# Format de sortie JUnit
schemathesis run schema.yaml --junit-xml report.xml
```

### RESTler — Fuzzer Microsoft pour REST APIs

```bash
# Compilation (dotnet required)
dotnet build

# Test stateful
python restler.py compile --api_spec openapi.json
python restler.py fuzz --grammar_file Compile/grammar.py --time_budget 24
```

## Fuzzing de fichiers (parsers)

Les parsers de formats (PDF, XML, ZIP, images) sont des cibles privilégiées :

```bash
# Fuzzer un parser PDF avec AFL++
afl-gcc -o pdf_parser_afl pdf_parser.c

mkdir seeds
cp sample.pdf seeds/
afl-fuzz -i seeds -o crashes -t 5000 -- ./pdf_parser_afl @@

# Ou avec libFuzzer + ASan (plus efficace)
clang -fsanitize=address,fuzzer pdf_parser.c -o pdf_fuzz
./pdf_fuzz seeds/ -max_len=10000000

# Honggfuzz pour targets compilées
honggfuzz -i seeds/ -o corpus/ -- ./pdf_parser ___FILE___
```

## Analyse des résultats

### Triage des crashes

```bash
# Minimiser un crash (trouver le plus petit input déclenchant le bug)
afl-tmin -i crash_file -o minimized -- ./target @@

# Analyser avec GDB
gdb -ex "run < crash_file" -ex "bt" -ex "quit" ./target

# Avec ASan, le rapport indique directement le type de bug :
# heap-buffer-overflow, stack-buffer-overflow, use-after-free, etc.

# Déduplication (éviter les doublons)
afl-collect -r corpus_out/crashes ./target @@
```

### Types de bugs découverts

| Bug | Description | Dangerosité |
|-----|-------------|-------------|
| Heap buffer overflow | Écriture hors des limites du tas | Critique (RCE possible) |
| Stack buffer overflow | Écriture hors des limites de la pile | Critique (RCE/contrôle EIP) |
| Use-after-free | Accès à mémoire libérée | Critique |
| Integer overflow | Dépassement d'entier | Variable |
| Null pointer dereference | Accès à l'adresse 0 | DoS |
| Format string | %n en paramètre contrôlable | Critique |
| Race condition | TOCTOU, atomicité | Variable |
| Infinite loop | Hang sur input malformé | DoS |

## Outils récapitulatif

| Outil | Cible | Type |
|-------|-------|------|
| ffuf | Web endpoints | Blackbox mutation |
| wfuzz | Web parameters | Blackbox |
| AFL++ | Binaires C/C++ | Greybox coverage |
| libFuzzer | Fonctions C/C++ | In-process greybox |
| Honggfuzz | Binaires | Greybox |
| Boofuzz | Protocoles réseau | Generation-based |
| Radamsa | Tout (générique) | Mutation-based |
| Schemathesis | APIs REST/OpenAPI | Generation-based |
| Peach | Protocoles/fichiers | Generation-based |
| ClusterFuzz | Infrastructure cloud | Coverage-guided |
| OSS-Fuzz | Open source (Google) | Coverage-guided |

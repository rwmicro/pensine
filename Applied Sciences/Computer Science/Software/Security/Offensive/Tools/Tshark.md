---
title: "TShark"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Offensive > Tools"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2025-02-15"
---

TShark is a text-based tool, and it is suitable for data carving, in-depth packet analysis, and automation with scripts. This strength and flexibility come out of the nature of the CLI tools, as the produced/processed data can be pipelined to additional tools. The most common tools used in packet analysis are listed below.

### **Caractéristiques principales**

- **Analyse réseau en ligne de commande** : Permet de capturer et d'inspecter des paquets réseau sans interface graphique.
- **Support de nombreux protocoles** : Analyse des milliers de protocoles réseau (HTTP, DNS, TCP, UDP, etc.).
- **Capture en temps réel** : Affiche les paquets en direct ou les enregistre dans un fichier.
- **Filtres** : Utilise les filtres de capture et d'affichage pour sélectionner des paquets spécifiques.
- **Exportation** : Enregistre les données capturées dans différents formats pour une analyse ultérieure.
- **Flexibilité** : Compatible avec des scripts pour une automatisation avancée.

### **Commandes de base**

#### 1. **Capturer des paquets en temps réel** :

```bash
tshark -i <interface>
```

Exemple :

```bash
tshark -i eth0
```

#### 2. **Filtrer les paquets à capturer** :

Utilisez des filtres BPF (Berkeley Packet Filter) :

```bash
tshark -i eth0 -f "tcp port 80"
```

> Capture uniquement le trafic TCP sur le port 80.

#### 3. **Analyser un fichier de capture** :

```bash
tshark -r fichier.pcap
```

#### 4. **Afficher uniquement certains champs** :

```bash
tshark -T fields -e <champ>
```

Exemple :

```bash
tshark -T fields -e ip.src -e ip.dst -e tcp.port
```

> Affiche uniquement les adresses IP source, destination, et le port TCP.

#### 5. **Exporter les données dans un fichier** :

```bash
tshark -i eth0 -w fichier.pcap
```

> Enregistre les paquets capturés dans un fichier au format **PCAP**.

#### 6. **Lire les paquets avec un filtre d'affichage** :

```bash
tshark -r fichier.pcap -Y "<filtre>"
```

Exemple :

```bash
tshark -r capture.pcap -Y "http.request.method == GET"
```

#### 7. **Statistiques** :

Afficher des statistiques sur les protocoles :

```bash
tshark -z io,stat,10
```

> Affiche des statistiques sur 10 secondes d'intervalle.

### **Filtres courants**

#### Filtres de capture :

- `tcp port 80` : Capture le trafic TCP sur le port 80.
- `host 192.168.1.1` : Capture tout le trafic lié à l'hôte spécifié.

#### Filtres d'affichage :

- `http.request` : Affiche les requêtes HTTP.
- `ip.addr == 192.168.1.1` : Affiche les paquets impliquant cette adresse IP.
- `tcp.flags.syn == 1` : Affiche les paquets SYN (début de connexion TCP).

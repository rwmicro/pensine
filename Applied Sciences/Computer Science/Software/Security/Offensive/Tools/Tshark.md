---
title: "TShark"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Offensive > Tools"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2025-02-15"
prerequis: ["[[Recon Automation]]"]
---

# TShark

Un analyste reçoit une capture réseau de deux gigaoctets et une question simple : quels noms de domaine la machine infectée a-t-elle résolus ? Ouvrir le fichier dans Wireshark et faire défiler des millions de paquets à l'écran serait interminable. Une seule ligne de commande suffit pourtant : `tshark -r capture.pcap -Y dns.flags.response==0 -T fields -e dns.qry.name | sort | uniq -c | sort -rn`. **TShark** est la version en ligne de commande de Wireshark. Il partage le même moteur de dissection, qui reconnaît des milliers de protocoles, et les mêmes filtres, mais il produit du texte, que l'on peut trier, filtrer et enchaîner avec les outils classiques du terminal ou intégrer dans des scripts.

> [!important] Idée clé
> L'intérêt de tshark n'est pas de remplacer Wireshark pour la lecture manuelle — c'est de rendre l'analyse réseau scriptable. `-T fields -e` extrait un champ précis sur des milliers de paquets pour le piper vers `grep`/`awk`/`jq`, ce qu'une interface graphique ne permet pas d'automatiser.

## Capturer ou lire une capture

TShark travaille dans deux modes. En capture, il écoute une interface réseau (`-i`) et affiche les paquets au fil de l'eau, une ligne par paquet. On liste les interfaces disponibles avec `tshark -D`. Capturer demande en général des privilèges, ou l'appartenance au groupe `wireshark` sur Linux.

```bash
tshark -D                 # Lister les interfaces
tshark -i eth0            # Capturer et afficher en direct
tshark -i eth0 -c 100     # S'arrêter après 100 paquets
```

Pour garder une trace, on enregistre les paquets bruts dans un fichier avec `-w`, au format pcapng par défaut (ou pcap avec `-F pcap`). On les relira ensuite avec `-r`, autant de fois qu'il le faudra, avec TShark ou avec Wireshark.

```bash
tshark -i eth0 -w capture.pcapng
tshark -r capture.pcapng
```

## Deux sortes de filtres

La distinction la plus importante, et la plus source d'erreurs, est celle entre les deux familles de filtres, qui n'ont ni la même syntaxe ni le même rôle.

Les **filtres de capture** (`-f`) utilisent la syntaxe BPF (*Berkeley Packet Filter*), celle de tcpdump. Ils s'appliquent pendant la capture, dans le noyau : les paquets qui ne correspondent pas ne sont jamais enregistrés. Ils sont très rapides mais rudimentaires, puisqu'ils ne connaissent que les adresses, les ports et les protocoles de bas niveau. On les utilise pour limiter le volume d'une capture longue.

```bash
tshark -i eth0 -f "tcp port 80"          # Seulement le trafic TCP sur le port 80
tshark -i eth0 -f "host 192.168.1.1"     # Seulement le trafic de cet hôte
```

Les **filtres d'affichage** (`-Y`) utilisent la syntaxe de Wireshark. Ils s'appliquent après la dissection, sur des paquets déjà capturés, et connaissent chaque champ de chaque protocole : la méthode d'une requête HTTP, le nom demandé dans une requête DNS, les drapeaux TCP. Ce qui est filtré n'est pas perdu, simplement masqué, et on peut relire le même fichier avec un autre filtre.

```bash
tshark -r capture.pcap -Y "http.request.method == GET"
tshark -r capture.pcap -Y "ip.addr == 192.168.1.1"
tshark -r capture.pcap -Y "tcp.flags.syn == 1 && tcp.flags.ack == 0"   # Débuts de connexion
```

La règle pratique : filtrer large à la capture pour ne rien manquer, puis filtrer finement à l'affichage.

## Extraire des champs

C'est ici que TShark dépasse l'interface graphique. Avec `-T fields`, il n'affiche plus des lignes résumées mais uniquement les champs demandés par `-e`, séparés par des tabulations. Le nom des champs est celui des filtres d'affichage, que l'on retrouve dans Wireshark en cliquant sur un champ. Le résultat se prête directement à `sort`, `uniq`, `awk` ou à un import dans un tableur.

```bash
# Qui parle à qui
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.dstport

# Les hôtes HTTP les plus visités
tshark -r capture.pcap -Y http.request -T fields -e http.host | sort | uniq -c | sort -rn

# Avec un en-tête et un séparateur CSV
tshark -r capture.pcap -T fields -E header=y -E separator=, -e frame.time -e ip.src -e ip.dst
```

D'autres formats de sortie existent : `-T json` ou `-T ek` produisent du JSON exploitable avec `jq` ou importable dans Elasticsearch, et `-V` affiche le détail complet de chaque paquet, comme le panneau central de Wireshark.

## Statistiques

L'option `-z` calcule des statistiques plutôt que d'afficher les paquets ; on l'associe souvent à `-q` pour ne garder que le résumé. Elle donne une vue d'ensemble rapide d'une capture inconnue : quels protocoles, quelles conversations, quels volumes.

```bash
tshark -r capture.pcap -q -z io,stat,10        # Volume par tranche de 10 secondes
tshark -r capture.pcap -q -z conv,tcp          # Conversations TCP
tshark -r capture.pcap -q -z io,phs            # Hiérarchie des protocoles
tshark -r capture.pcap -q -z http,tree         # Requêtes et codes HTTP
```

Pour un premier contact avec une capture, l'enchaînement est souvent le même : la hiérarchie des protocoles pour savoir ce qu'elle contient, les conversations pour repérer les échanges les plus volumineux, puis des filtres d'affichage et des extractions de champs pour creuser.

## Ressources

- La page de manuel `man tshark` et la [référence des filtres d'affichage](https://www.wireshark.org/docs/dfref/) de Wireshark.
- Sur la machine, `tshark -G fields` liste tous les champs disponibles.

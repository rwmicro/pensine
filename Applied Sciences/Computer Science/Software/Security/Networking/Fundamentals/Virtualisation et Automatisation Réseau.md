---
title: "Virtualisation et Automatisation Réseau"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, réseau, virtualisation, automatisation, sdn]
date: "2026-04-07"
---

# Virtualisation et Automatisation Réseau

## Virtualisation réseau

La virtualisation réseau permet de créer des réseaux logiques indépendants de l'infrastructure physique. Elle offre une économie significative de ressources : au lieu d'acquérir 2000 machines physiques, une entreprise peut centraliser ses ressources sur quelques serveurs hébergeant des machines virtuelles.

### Avantages

| Avantage | Description |
|----------|-------------|
| Prototypage facilité | Création de réseaux isolés avec variables contrôlées ; retour à l'état précédent en cas d'échec |
| Provisionnement rapide | Déployer un serveur virtuel est beaucoup plus rapide qu'un serveur physique |
| Haute disponibilité | Fonctionnalités fault tolerance intégrées : live migration, storage migration, DRS |
| Reprise sur sinistre | L'abstraction matérielle permet une récupération sans dépendance au hardware |
| Support étendu | Les plateformes de virtualisation maintiennent le support d'OS et applications plus longtemps |

### Hyperviseur

Un hyperviseur est un logiciel qui permet à une machine physique (Physical Machine) de créer et exécuter plusieurs machines virtuelles (VM) simultanément.

| Type | Description | Exemples |
|------|-------------|---------|
| **Type 1** (bare-metal) | Installé directement sur le hardware, remplace le firmware | VMware ESXi, Microsoft Hyper-V, Xen |
| **Type 2** (hosted) | Installé sur un OS hôte, fonctionne comme une application standard | VMware Workstation, VirtualBox, Parallels |

## SDN (Software Defined Networking)

Le SDN sépare le **plan de contrôle** (control plane) du **plan de données** (data plane) pour accroître la flexibilité et permettre l'automatisation.

### Plans d'un équipement réseau

**Plan de contrôle** : "cerveau" de l'équipement. Détermine le forwarding des paquets. Contient les tables de routage (IPv4/IPv6), les tables de topologie OSPF/EIGRP, les tables STP, les tables ARP. Traité par le CPU.

**Plan de données (forwarding plane)** : exécute le forwarding effectif du trafic selon les instructions du control plane. Traité par des processeurs spécialisés (ASIC) sans impliquer le CPU.

### Types de SDN

| Type | Principe | Exemple |
|------|----------|---------|
| **Device-based SDN** | Programmation individuelle de chaque équipement via API (C, Java, Python) | Cisco OnePK |
| **Controller-based SDN** | Contrôleur centralisé gérant tous les équipements et les flux | Cisco Open SDN Controller |
| **Policy-based SDN** | Contrôleur + politiques de haut niveau avec interface GUI, sans programmation requise | Cisco APIC-EM |

## Automatisation réseau

L'automatisation réseau est le processus d'automatisation de la configuration, gestion, test, déploiement et exploitation des équipements physiques et virtuels. Tout équipement contrôlable via API ou CLI peut être automatisé.

### Bénéfices

| Bénéfice | Description |
|----------|-------------|
| Réduction des erreurs | Élimine les erreurs de configuration manuelle (typos, oublis) |
| Réduction des coûts | Moins de main-d'œuvre nécessaire pour les tâches répétitives |
| Résilience accrue | Récupération automatique des incidents sans intervention manuelle |
| Disponibilité améliorée | Cohérence des configurations sur tous les sites et branches |
| Visibilité | Analyse en temps réel du comportement réseau |

### Cycle de vie CI-CT-CD

Les pratiques d'intégration continue (CI), test continu (CT) et déploiement continu (CD) permettent de développer, valider, tester et déployer des services réseau plus rapidement et à moindre coût via l'infrastructure virtualisée (VNF — Virtual Network Functions, CNF — Cloud-Native Functions).

### Ansible

Ansible est l'un des outils d'automatisation réseau les plus utilisés. Il permet de configurer simultanément plusieurs équipements sans compétences avancées en programmation.

**Architecture :**

| Composant | Rôle |
|-----------|------|
| Control node | Machine exécutant Ansible |
| Managed nodes | Équipements gérés par Ansible |
| Inventory | Liste des hôtes gérés (`/etc/ansible/hosts`) |
| Playbook | Fichier YAML décrivant les tâches à exécuter |
| Module | Programme envoyé sur le nœud géré via SSH pour exécuter une tâche |

**Caractéristiques clés :**
- Communication via SSH (pas d'agent sur les nœuds gérés)
- Idempotence : un playbook peut être rejoué sans effet négatif sur un système déjà configuré
- Playbooks écrits en YAML, lisibles et auto-documentés

```yaml
# Exemple de playbook Ansible
---
- name: Configurer les routeurs Cisco
  hosts: routers
  gather_facts: no

  tasks:
    - name: Activer OSPF
      cisco.ios.ios_config:
        lines:
          - router ospf 1
          - network 10.0.0.0 0.0.0.255 area 0
        parents: []

    - name: Sauvegarder la configuration
      cisco.ios.ios_command:
        commands: write memory
```

```ini
# Fichier inventory (/etc/ansible/hosts)
[routers]
router1 ansible_host=192.168.1.1
router2 ansible_host=192.168.1.2

[switches]
sw1 ansible_host=192.168.1.10
sw2 ansible_host=192.168.1.11

[network:children]
routers
switches
```

```bash
# Exécuter un playbook
ansible-playbook -i inventory.ini playbook.yml

# Test de connectivité
ansible all -i inventory.ini -m ping

# Commande ad-hoc
ansible routers -i inventory.ini -m cisco.ios.ios_command \
    -a "commands='show ip route'"
```

### Autres outils d'automatisation réseau

| Outil | Usage |
|-------|-------|
| Ansible | Configuration management, agentless, YAML |
| Puppet | Configuration management, agent-based, DSL propriétaire |
| Chef | Configuration management, Ruby, agent-based |
| Terraform | Infrastructure as Code, provisionnement déclaratif |
| NAPALM | Bibliothèque Python multi-vendeur pour la gestion réseau |
| Netmiko | Bibliothèque Python SSH pour équipements réseau |
| Nornir | Framework Python d'automatisation réseau |

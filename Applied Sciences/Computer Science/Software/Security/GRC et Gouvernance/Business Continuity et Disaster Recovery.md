---
title: Business Continuity et Disaster Recovery
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [bcdr, disaster-recovery, business-continuity, rpo, rto, backup, résilience]
date: 2026-03-22
---

# Business Continuity et Disaster Recovery

La continuité d'activité (BC) et la reprise après sinistre (DR) sont les deux facettes de la résilience organisationnelle face aux incidents majeurs : ransomware, panne matérielle, catastrophe naturelle, erreur humaine.

## Concepts fondamentaux

```mermaid
graph LR
    incident[Incident\nmajeur]
    incident --> rpo[RPO\nDonnées perdues\n(combien de temps\nd'historique ?)"]
    incident --> rto[RTO\nTemps d'indisponibilité\n(combien de temps\npour reprendre ?)"]

    rpo --> backup[Politique de\nsauvegarde]
    rto --> dr[Plan de\nReprise d'Activité]
```

**RPO — Recovery Point Objective**
Quantité maximale de données qu'on accepte de perdre, exprimée en temps.
- RPO = 0 : zéro perte de données (réplication synchrone)
- RPO = 4h : on accepte de perdre jusqu'à 4h de données → sauvegarde toutes les 4h minimum

**RTO — Recovery Time Objective**
Temps maximal acceptable pour remettre le système en service.
- RTO = 0 : haute disponibilité permanente (basculement automatique)
- RTO = 4h : le système peut être indisponible 4h maximum

```mermaid
graph LR
    subgraph "Timeline d'un incident"
        last_backup[Dernière\nsauvegarde] -->|RPO\n(données perdues)| incident2[Incident]
        incident2 -->|RTO\n(temps de reprise)| restored[Système\nrestaré]
    end
```

## Stratégies de disponibilité

| Stratégie | RTO | RPO | Coût | Description |
|---|---|---|---|---|
| Cold standby | Jours | Heures | Faible | Serveur de secours éteint, démarrage manuel |
| Warm standby | Heures | Minutes | Moyen | Environnement prêt, données partiellement à jour |
| Hot standby | Minutes | Secondes | Élevé | Réplication synchrone, basculement rapide |
| Active-Active | Quasi zéro | Quasi zéro | Très élevé | Deux sites actifs simultanément |

## Règle 3-2-1 des sauvegardes

Standard minimum de l'industrie :

```
3 copies des données (production + 2 backups)
2 supports différents (disque local + NAS, ou cloud)
1 copie hors site (offsite ou cloud différent)
```

**Extension 3-2-1-1-0 (recommandée post-ransomware) :**
```
3 copies
2 supports différents
1 copie hors site
1 copie offline (air-gapped, non connectée)
0 erreur de restauration (tester régulièrement)
```

```bash
# Backup Linux avec rsync vers un NAS
rsync -avz --delete /data/ backup-nas:/backups/$(date +%Y%m%d)/

# Rotation automatique (conserver 7 jours, 4 semaines, 12 mois)
# Scheme GFS (Grandfather-Father-Son)

# Vérification intégrité (hash)
find /backups -name "*.tar.gz" -exec sha256sum {} \; > checksums.txt

# Tester la restauration (CRITIQUE — le backup non testé n'existe pas)
tar -xzf backup_2026-03-22.tar.gz -C /tmp/restore_test/
diff -r /data/ /tmp/restore_test/  # Comparer avec l'original
```

## Sauvegarde cloud

```bash
# AWS S3 — bucket immuable (versioning + object lock)
# Empêche la suppression par ransomware même avec credentials compromis
aws s3api put-bucket-versioning --bucket my-backups \
  --versioning-configuration Status=Enabled

aws s3api put-object-lock-configuration --bucket my-backups \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",  # Immuable même pour l'admin
        "Days": 30
      }
    }
  }'

# Chiffrement côté client avant upload
aws s3 cp backup.tar.gz s3://my-backups/ \
  --sse aws:kms \
  --sse-kms-key-id arn:aws:kms:...

# Cross-region replication (résilience géographique)
aws s3api put-bucket-replication --bucket my-backups \
  --replication-configuration file://replication.json
```

## Plan de Continuité d'Activité (PCA)

Le PCA décrit comment l'organisation continue à fonctionner pendant et après un incident.

### Business Impact Analysis (BIA)

```
Étapes :
1. Identifier les processus métier critiques
2. Pour chaque processus : définir RPO et RTO
3. Identifier les dépendances (systèmes, fournisseurs, personnel)
4. Quantifier l'impact financier de l'indisponibilité

Exemple :
Processus : Traitement des commandes e-commerce
RTO : 2 heures (10 000€/h de CA perdu)
RPO : 15 minutes (perte de commandes inacceptable)
Dépendances : BDD Oracle, passerelle paiement, ERP SAP
```

### Scénarios de sinistre

```
Scénario 1 : Panne serveur unique
→ Redémarrage VM ou failover automatique (RTO 15 min)

Scénario 2 : Ransomware
→ Isolation réseau immédiate
→ Restauration depuis backup clean (offline)
→ RTO : 24-72h selon étendue

Scénario 3 : Panne datacenter (incendie, inondation)
→ Basculement vers site DR secondaire
→ RTO : 4-8h

Scénario 4 : Perte total du datacenter principal
→ Reconstruction sur cloud (DR as a Service)
→ RTO : 24-48h

Scénario 5 : Coupure fournisseur SaaS critique
→ Procédures dégradées manuelles
→ Contacter le fournisseur, SLA de reprise
```

## Plan de Reprise d'Activité (PRA)

Document opérationnel précisant les actions techniques de reprise.

```
Structure d'un PRA :

1. Critères de déclenchement
   → Qui décide ? Sur quels critères ?
   → Seuil d'indisponibilité, confirmation de la gravité

2. Équipe de reprise
   → Responsable DRP : [nom, tel]
   → Équipe technique : [noms, tels de secours]
   → Contacts fournisseurs critiques : [liste]

3. Procédures de reprise par système
   → Ordre de reprise (AD d'abord, puis DNS, puis apps)
   → Procédures step-by-step pour chaque système
   → Temps estimé pour chaque étape

4. Tests de restauration
   → Fréquence des tests (mensuel, trimestriel)
   → Résultats et écarts documentés

5. Communication
   → Template de communication interne/externe
   → Page de statut (status.monentreprise.com)
```

## Reprise après ransomware — Procédure détaillée

```bash
# PHASE 1 : Isolation (J0, H0)
# Déconnecter du réseau sans éteindre (préserver RAM/preuves)
# Identifier le périmètre de compromission (quelles machines ?)

# PHASE 2 : Évaluation (J0, H1-4)
# Les sauvegardes sont-elles intactes ?
aws s3 ls s3://my-backups/ --recursive | tail -20  # Dernière sauvegarde
# Les backups ne sont PAS sur le réseau compromis
# Vérifier les checksums des sauvegardes

# PHASE 3 : Reconstruction (J1-J3)
# Option A : Restauration depuis backup (préféré)
# 1. Déployer des serveurs neufs (ou VMs propres)
# 2. Appliquer les patches système d'abord
# 3. Restaurer les données depuis backup externe
# 4. Vérifier l'intégrité (pas de malware dans les backups)
# 5. Reconnecter progressivement avec monitoring renforcé

# Option B : Nettoyage (si backup impossible)
# RISQUÉ — l'attaquant peut avoir des backdoors
# Réserver aux systèmes sans données critiques

# PHASE 4 : Hardening post-incident
# Changer TOUS les mots de passe (AD compris)
# Réinitialiser krbtgt 2 fois (si AD compromis)
# Activer MFA partout
# Revoir les accès VPN et RDP exposés
# Déployer EDR sur tous les endpoints
```

## Haute disponibilité des bases de données

```sql
-- PostgreSQL — Streaming Replication
-- Serveur primaire : postgresql.conf
wal_level = replica
max_wal_senders = 10
synchronous_commit = on  -- RPO = 0 (synchrone)

-- Serveur secondaire : recovery.conf
primary_conninfo = 'host=primary_server port=5432 user=replica'
standby_mode = on

-- Vérifier la réplication
SELECT client_addr, state, sent_lsn, replay_lsn,
       sent_lsn - replay_lsn AS replication_lag
FROM pg_stat_replication;
```

## Tests et exercices

Un PRA non testé n'est pas un PRA.

| Test | Fréquence | Description |
|---|---|---|
| Test de restauration de fichiers | Mensuel | Restaurer un fichier spécifique depuis backup |
| Test de restauration système | Trimestriel | Restaurer un serveur complet en environnement isolé |
| Test de basculement | Semestriel | Basculer vers le site DR, vérifier le fonctionnement |
| Exercice de crise complet | Annuel | Simulation complète d'un incident majeur (tabletop ou réel) |

```bash
# Test de restauration automatisé
#!/bin/bash
# Restaurer la sauvegarde d'hier dans un environnement de test
BACKUP=$(aws s3 ls s3://my-backups/ | sort | tail -1 | awk '{print $4}')
aws s3 cp s3://my-backups/$BACKUP /tmp/restore_test/

# Monter et vérifier
tar -xzf /tmp/restore_test/$BACKUP -C /tmp/restored/
[ -f /tmp/restored/database.sql ] && echo "OK" || echo "ERREUR"

# Notifier l'équipe
curl -X POST $SLACK_WEBHOOK -d "{\"text\": \"Test backup $BACKUP : OK\"}"
```

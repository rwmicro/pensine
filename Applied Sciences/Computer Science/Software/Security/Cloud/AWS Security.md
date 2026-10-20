---
title: "AWS Security"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Cloud"
tags: [aws, cloud-security, iam, s3, imds, kms, cloudtrail, durcissement]
date: "2026-10-20"
prerequis: ["[[Cloud Security]]", "[[Zero Trust Architecture]]", "[[Sécurité Réseau]]"]
---

# AWS Security

AWS est une plateforme API-first : chaque ressource est créée, lue ou modifiée par un appel HTTP signé, autorisé par IAM. Le plan de contrôle est joignable depuis toute adresse IP disposant des bons identifiants : la frontière de sécurité n'est donc ni le VPC ni le pare-feu, mais l'identité et la politique d'autorisation. Un attaquant qui obtient des clés valides n'exploite souvent aucune vulnérabilité : il appelle l'API légitime avec des droits excessifs.

> [!abstract] Définition — Principal
> Un **principal** est l'entité qui signe une requête AWS : utilisateur IAM, session de rôle STS, rôle de service, compte fédéré ou service agissant pour le client. Dans une politique, `Principal` désigne qui est autorisé ; `Action`, `Resource` et `Condition` désignent ce qui l'est et dans quel contexte.

## Responsabilité partagée et topologie des comptes

AWS sécurise *le* cloud (hôtes, hyperviseur Nitro, backbone, infrastructure des services managés) ; le client sécurise *ce qu'il y met* : données, identités, configuration, OS des instances, code des fonctions. La frontière varie : sur EC2, le client gère l'OS et le patching ; sur RDS ou Lambda, il conserve données, identités et politiques réseau applicatives.

Le **compte** est l'unité de cloisonnement la plus solide : quotas, facturation et frontière IAM. Deux ressources de comptes différents ne peuvent s'appeler sans autorisation explicite des deux côtés. D'où un compte par environnement et par fonction (production, staging, données, réseau, journalisation, sécurité), réunis par AWS Organizations.

```mermaid
flowchart TD
    idp["IdP externe\nSAML ou OIDC"] --> idc["IAM Identity Center\n(permission sets)"]
    org["Organization\n(compte de management)"] --> scp["SCP\n(plafond de droits)"]
    org --> ou["OU Production"]
    ou --> acc["Compte membre\n(cloison forte)"]
    idc --> role["Rôle IAM\n(session temporaire)"]
    scp --> role
    role --> res["Ressources\nS3, EC2, KMS, RDS"]
    log["Compte journalisation\n(immuable)"] -.->|"CloudTrail org"| acc
```

Les **OU** regroupent les comptes par sensibilité ; les **SCP** plafonnent les permissions de tous les principaux, root compris. Une SCP ne donne jamais de droit, elle restreint, et ne s'applique pas au compte de management — raison de ne rien y exécuter.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ProtectAuditTrail",
      "Effect": "Deny",
      "Action": ["cloudtrail:StopLogging", "cloudtrail:DeleteTrail",
                 "guardduty:DeleteDetector", "kms:ScheduleKeyDeletion"],
      "Resource": "*"
    },
    {
      "Sid": "DenyOutsideApprovedRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["eu-west-3", "eu-west-1"]
        }
      }
    }
  ]
}
```

AWS Control Tower automatise ce socle : landing zone, comptes de journalisation et d'audit centralisés, garde-fous, account factory. Sans lui, l'organisation dérive vers des comptes orphelins.

## IAM : le moteur d'autorisation

IAM empile les couches : un **deny explicite** l'emporte toujours ; puis les SCP et *resource control policies* doivent autoriser ; puis la **permission boundary** ; enfin une politique *identity-based* ou *resource-based* doit accorder. Pour un accès inter-comptes, les deux côtés doivent être d'accord.

Une politique d'identité s'attache à un utilisateur, un groupe ou un rôle ; une politique de ressource s'attache au bucket, à la file, à la clé KMS ou à la fonction Lambda. La **trust policy** d'un rôle dit qui peut appeler `sts:AssumeRole`, pas ce que le rôle pourra faire. Les rôles sont le mécanisme privilégié : credentials temporaires via STS, expiration d'une heure par défaut, fédération sans clé longue durée. **IAM Identity Center** fédère l'IdP, attribue des *permission sets* à des groupes et produit des sessions par compte. Les clés `AKIA...` restent réservées aux machines incompatibles avec un rôle : inventoriées, tournées, surveillées par `GetAccessKeyLastUsed`.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::111122223333:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": "repo:acme/api:ref:refs/heads/main"}
    }
  }]
}
```

Cette fédération OIDC pour la CI/CD supprime les clés statiques : la condition `sub` limite l'usurpation à un dépôt et une branche. Trop permissive (`repo:acme/*`), elle reproduit le risque d'une clé.

Les **session tags** permettent l'ABAC : `sts:AssumeRole --tags Key=team,Value=payments`, sous réserve de `sts:TagSession`. Les politiques référencent `${aws:PrincipalTag/team}`. Un rôle unique suffit pour plusieurs équipes, mais un appelant qui peut poser un tag arbitraire contourne le modèle : une condition sur les valeurs est indispensable.

> [!quiz] Une permission boundary accorde-t-elle des droits ?
> Non. Elle plafonne les droits qu'une politique d'identité peut accorder. Un principal avec une boundary permissive et aucune politique d'identité n'a aucun droit ; avec `AdministratorAccess` et une boundary restrictive, il est limité à l'intersection. La boundary s'évalue avant l'allow.

## Chemins d'escalade IAM

L'escalade AWS ne casse pas IAM : elle utilise une permission légitime pour créer une identité ou une ressource plus privilégiée. Trois primitives suffisent : modifier une politique, créer une identité, ou faire exécuter du code via un rôle de service puissant.

| Permission détenue | Mécanisme | Résultat |
|---|---|---|
| `iam:CreatePolicyVersion` | Nouvelle version d'une politique attachée à soi, `--set-as-default` | Droits remplacés par `*:*` |
| `iam:AttachUserPolicy`, `AttachRolePolicy` | Attacher `AdministratorAccess` | Élévation directe |
| `iam:PutUserPolicy`, `PutRolePolicy` | Injecter une politique inline | Élévation directe |
| `iam:CreateAccessKey` | Clé pour un autre utilisateur | Persistance |
| `iam:UpdateAssumeRolePolicy` | Se faire confiance, puis `sts:AssumeRole` | Prise de contrôle d'un rôle |
| `iam:PassRole` + `ec2:RunInstances` | Instance avec profil admin | Exécution avec le rôle |
| `iam:PassRole` + `lambda:CreateFunction` | Fonction avec rôle puissant | Exécution arbitraire |
| `iam:PassRole` + `glue:CreateDevEndpoint` | Endpoint Glue | Shell avec le rôle |
| `codebuild:StartBuild`, `ssm:SendCommand` | Projet ou instance à rôle puissant | Exécution de commandes |
| `sts:AssumeRole` | Endosser un rôle supérieur | Chaînage |

```bash
aws iam create-policy-version \
  --policy-arn arn:aws:iam::111122223333:policy/ReadOnly \
  --policy-document file://admin.json --set-as-default

aws ec2 run-instances --image-id ami-0123456789abcdef0 \
  --instance-type t3.micro \
  --iam-instance-profile Name=AdminInstanceProfile \
  --user-data file://bootstrap.sh
```

`iam:PassRole` ne donne aucun droit direct : il autorise à *transmettre* un rôle à un service. Si ce rôle est administratif et que le service exécute du code (EC2, Lambda, Glue, SageMaker, CloudFormation), l'appelant hérite de ses droits. La parade associe `iam:PassedToService` à une restriction d'ARN.

Le **confused deputy** est le pendant côté ressource. Une politique Lambda qui autorise `sns.amazonaws.com` sans `aws:SourceArn` laisse n'importe quel compte déclencher la fonction ; une trust policy sans `aws:SourceAccount` laisse un tiers faire assumer le rôle par le service. `aws:SourceArn`, `aws:SourceAccount`, `aws:PrincipalOrgID` et `aws:ResourceAccount` sont les contre-mesures, et Access Analyzer les signale : le service privilégié devient l'instrument de l'élévation.

```mermaid
flowchart LR
    ssrf["SSRF sur une application\nEC2"] --> imds["IMDSv1\n169.254.169.254"]
    imds --> creds["Credentials\ndu rôle d'instance"]
    creds --> enum["Énumération\niam:List*, s3:List*"]
    enum --> esc["Escalade\niam:CreatePolicyVersion"]
    esc --> admin["AdministratorAccess"]
    admin --> exfil["Exfiltration\nS3 externe"]
```

## S3 : exposition, chiffrement et immuabilité

S3 concentre les fuites cloud : objets nombreux, politiques superposées, accès anonyme possible. L'accès effectif combine politique de bucket, ACL héritées, politique d'identité et les quatre réglages **Block Public Access** — `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets`. Posés au niveau du compte, ils empêchent aussi qu'un bucket futur naisse public.

Une politique de bucket doit nommer un principal précis ou restreindre par `aws:PrincipalOrgID`. `"Principal": "*"` sans condition expose le bucket au monde ; `aws:ResourceAccount` protège contre le détournement vers un compte tiers.

Le chiffrement serveur a trois modes. **SSE-S3** utilise des clés AWS sans politique client. **SSE-KMS** confie la clé à KMS : politique de clé, grants et `EncryptionContext` deviennent des contrôles d'accès, chaque `GetObject` déclenchant `kms:Decrypt`. **SSE-C** laisse le client fournir la clé à chaque requête, qu'AWS ne stocke pas, ce qui interdit les presigned URLs classiques.

Les **presigned URLs** sont signées avec les credentials du signataire et héritent de ses droits. Elles ne se révoquent pas individuellement : il faut révoquer la session ou la clé. Leur durée maximale est de sept jours en SigV4 ; une URL fuitée reste exploitable et contourne les contrôles réseau.

Les **access points** ajoutent un point d'entrée nommé avec sa propre politique, restreignable à un VPC. Le **versioning** conditionne Object Lock et la réplication. **Object Lock** en mode compliance rend un objet immuable, même pour le root. Le **logging** repose sur les server access logs (best-effort) ou les événements de données CloudTrail, préférables pour la preuve. La réplication inter-comptes vers un compte isolé reste la meilleure défense contre un attaquant qui obtient les droits de suppression.

## EC2, VPC et le service de métadonnées

Un **security group** est un pare-feu stateful par interface : uniquement des autorisations, le retour étant implicite. Une **NACL** est stateless, au niveau du subnet, avec autorisations et refus évalués par ordre et ports éphémères à ouvrir. Le SG segmente les instances, la NACL filtre à la frontière du subnet. Une architecture Zero Trust référence des SG sources plutôt que des CIDR.

L'**Instance Metadata Service** expose à l'instance ses informations et les credentials temporaires de son rôle. IMDSv1 répond à un `GET` non authentifié sur `169.254.169.254` : toute SSRF lit les credentials. C'est le scénario Capital One de 2019 — un WAF mal configuré permit une SSRF vers IMDSv1, le rôle disposait de `s3:ListBuckets` et `s3:GetObject`, et les données de plus de cent millions de clients furent copiées vers un bucket externe.

**IMDSv2** impose un `PUT` préalable pour obtenir un jeton, puis l'en-tête `X-aws-ec2-metadata-token`. La réponse est limitée à un saut réseau, ce qui bloque proxy et conteneur. Cela casse la SSRF naïve, pas un attaquant qui exécute déjà du code sur l'instance : il fera le `PUT` lui-même.

```bash
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/security-credentials/

aws ec2 modify-instance-metadata-defaults \
  --http-tokens required --http-put-response-hop-limit 1
```

Les autres surfaces EC2 sont les **AMI publiques** contenant des secrets, les **snapshots EBS publics**, les volumes non chiffrés et les **user data** en clair, lisibles via `ec2:DescribeInstanceAttribute`. Le chiffrement EBS par défaut s'active au niveau du compte et de chaque région. Les **VPC endpoints** (gateway S3/DynamoDB, interface PrivateLink) gardent le trafic AWS hors d'Internet ; une politique d'endpoint restreint les buckets accessibles et constitue une barrière d'exfiltration.

## Lambda, conteneurs, bases de données et KMS

Lambda cumule trois risques. Les **variables d'environnement** sont chiffrées au repos mais lisibles en clair par toute identité disposant de `lambda:GetFunctionConfiguration` : un secret doit vivre dans Secrets Manager. La **politique de ressource** (`AddPermission`) décide qui invoque la fonction ; sans `SourceArn`, c'est une porte ouverte au confused deputy. Le **rôle d'exécution** partagé transforme une fonction compromise en accès à toutes ses ressources.

ECS sépare le **rôle d'exécution** (image, logs) du **rôle de tâche** (permissions applicatives) ; les confondre donne au conteneur les droits d'infrastructure. EKS ajoute IRSA ou Pod Identity pour projeter un rôle dans un service account, et des access entries pour mapper les rôles au plan de contrôle. Un pod qui atteint l'IMDS du nœud récupère le rôle du nœud, souvent plus large : la limite d'un saut est essentielle.

RDS expose snapshots publics, instances accessibles depuis Internet, mot de passe unique et chiffrement choisi à la création seulement. L'authentification IAM évite les mots de passe statiques ; Secrets Manager gère la rotation.

**KMS** est le point de convergence des chiffrements. Une **CMK** possède une politique de clé qui est le contrôle d'accès primaire : IAM seul ne suffit pas. Les **grants** délèguent temporairement sans modifier la politique et n'apparaissent pas dans `GetKeyPolicy` ; il faut `ListGrants` ou CloudTrail. L'**encryption context** est une donnée d'association authentifiée, non secrète, qui doit correspondre exactement au déchiffrement et lie un chiffré à un tenant.

```json
{
  "Sid": "AppEncryptViaS3Only",
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::111122223333:role/app-api"},
  "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "kms:ViaService": "s3.eu-west-3.amazonaws.com",
      "kms:EncryptionContext:tenant": "acme"
    }
  }
}
```

La rotation annuelle automatique change le matériel sans invalider les chiffrés. La suppression planifiée ouvre une fenêtre de 7 à 30 jours : c'est un levier de rançongiciel, car supprimer la clé rend sauvegardes et snapshots illisibles. `kms:ScheduleKeyDeletion` et `kms:DisableKey` doivent être réservés à un rôle de rupture de verre et alertés.

## Détection

CloudTrail est la source primaire : événements de gestion dans toutes les régions avec un trail multi-région, événements de données S3 et Lambda en option payante. Un trail d'organisation, chiffré KMS, avec validation d'intégrité et destination dans un compte isolé, est le minimum. Les événements s'interrogent dans CloudTrail Lake ou via Athena.

```sql
SELECT eventtime, eventname, useridentity.arn, sourceipaddress, requestparameters
FROM cloudtrail_logs
WHERE eventname IN ('CreatePolicyVersion', 'AttachUserPolicy', 'PutUserPolicy',
                    'CreateAccessKey', 'UpdateAssumeRolePolicy', 'ScheduleKeyDeletion')
  AND errorcode IS NULL
  AND from_unixtime(eventtime) > current_timestamp - interval '7' day
ORDER BY eventtime DESC LIMIT 200;
```

GuardDuty analyse CloudTrail, flux VPC, DNS, journaux EKS et accès S3. Les findings utiles sont `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS`, `CredentialAccess:IAMUser/AnomalousBehavior`, `Persistence:IAMUser/AnomalousBehavior` et `Exfiltration:S3/ObjectRead.Unusual`. Il détecte l'anomalie statistique ou la signature, pas une exfiltration lente avec des credentials légitimes.

Security Hub agrège les findings ASFF et évalue CIS, FSBP et PCI DSS. Config enregistre l'état des ressources et applique des remédiations SSM. Inspector scanne EC2, ECR et Lambda pour les CVE. Macie classe les données S3 et signale les informations personnelles. Access Analyzer identifie accès externes et permissions inutilisées. Detective reconstruit un graphe d'enquête ; VPC Flow Logs complètent la vision réseau.

Les alertes à fort signal sont peu nombreuses : usage du root, désactivation de MFA, création de clé, modification de politique ou de trust policy, arrêt de trail, suppression de clé KMS, security group ouvert à `0.0.0.0/0` sur un port d'administration, pic de coût.

## Outils d'audit

| Outil | Usage | Commande |
|---|---|---|
| Prowler | Conformité CIS, FSBP, PCI | `prowler aws --compliance cis_aws_3.0` |
| ScoutSuite | Audit multi-cloud, rapport HTML | `scout aws --report-dir ./rapport` |
| Pacu | Exploitation et énumération | `run iam__privesc_scan` |
| PMapper | Graphe IAM, requêtes d'escalade | `pmapper graph create` |
| Cloudsplaining | Politiques IAM sur-permissives | `cloudsplaining scan --input-file default.json` |
| enumerate-iam | Permissions réelles d'une clé | `python3 enumerate-iam.py --access-key ...` |
| Steampipe | Inventaire cloud en SQL | `steampipe query "select * from aws_iam_user"` |
| Cartography | Relations cloud dans Neo4j | `cartography --aws-sync-all-profiles` |

Pacu reproduit les techniques de cette note (`iam__privesc_scan`, `iam__enum_permissions`, `s3__bucket_finder`, `ec2__enum`). PMapper répond côté défense à « ce principal peut-il atteindre cette ressource, et par quel chemin ».

## Durcissement

Le socle est automatisable. Supprimer les utilisateurs IAM au profit d'Identity Center ; interdire les clés longues durées ; imposer MFA, matérielle pour les administrateurs. Ne jamais utiliser le root et supprimer ses clés. Restreindre les régions par SCP, activer Block Public Access et le chiffrement EBS/S3 par défaut avec des CMK dédiées, imposer IMDSv2, séparer les rôles. Prévoir un *break-glass* : rôle d'urgence sans usage courant, endossement alerté, credentials hors ligne.

Le moindre privilège ne s'écrit pas à la main. Access Analyzer génère des politiques depuis CloudTrail, les findings « unused permissions » révèlent les droits dormants, une revue trimestrielle élimine la dette. Les SCP se versionnent en IaC.

## Réponse à incident

La réponse commence par la préservation : journaux, snapshots et images sont éphémères ou modifiables. Copier les logs vers un compte isolé, créer un snapshot avant toute action destructive, capturer la mémoire via SSM ou EDR. Ensuite contenir.

```bash
aws iam attach-user-policy --user-name svc-deploy \
  --policy-arn arn:aws:iam::aws:policy/AWSRevokeOlderSessions
aws iam update-access-key --access-key-id AKIAIOSFODNN7EXAMPLE \
  --status Inactive --user-name svc-deploy
aws iam delete-login-profile --user-name svc-deploy
aws ec2 modify-instance-attribute --instance-id i-0123456789abcdef0 \
  --groups sg-0a1b2c3d4e5f67890
aws ec2 create-snapshot --volume-id vol-0123456789abcdef0 \
  --description "forensic-2026-10-20"
```

Le containment d'une identité dépasse la clé : révoquer les sessions, retirer les politiques ajoutées, supprimer les clés créées, examiner les trust policies, inventorier les ressources créées (minage, persistance, règles EventBridge). La rotation des secrets de Secrets Manager, Systems Manager et Lambda suit. La restauration s'appuie sur l'IaC et des sauvegardes immuables.

## Limites et angles morts

CloudTrail n'enregistre pas certains accès de facturation et rate les accès S3 sans événements de données, coûteux sur de gros buckets. Les grants KMS sont invisibles dans la politique de clé. Une SCP qui bloque une action produit un simple `AccessDenied` chez le service appelé.

GuardDuty détecte l'anormal, pas l'intentionnel lent : un rôle légitime, depuis une IP résidentielle, à rythme humain, produit peu de signal. Un détecteur absent dans une région ouverte crée un angle mort. Macie et Inspector, facturés à l'usage, sont souvent limités aux comptes critiques alors que la compromission chemine par un compte de développement.

Le durcissement a ses limites. IMDSv2 protège de la SSRF distante, pas de l'exécution locale. Le moindre privilège IAM ne protège pas d'une politique de bucket ou de clé mal écrite. Une fédération OIDC au `sub` trop large reproduit le risque d'une clé statique.

## Lecture ATT&CK

| Technique | ID | Manifestation AWS | Détection |
|---|---|---|---|
| Valid Accounts: Cloud Accounts | T1078.004 | Rôle ou clé utilisé depuis une IP inhabituelle | GuardDuty, `sourceIPAddress` et `userAgent` |
| Data from Cloud Storage | T1530 | `s3:GetObject` massif, listing | Événements de données, volume, Macie |
| Unsecured Credentials: Cloud Instance Metadata API | T1552.005 | Lecture de `169.254.169.254` | GuardDuty, Flow Logs vers l'IP link-local |
| Implant Internal Image | T1525 | Image ECR ou AMI backdoorée | Inspector, scan ECR, signature, `PutImage` |
| Transfer Data to Cloud Account | T1537 | Snapshots ou réplication vers un compte externe | `ModifySnapshotAttribute`, `PutBucketReplication` |
| Exfiltration to Cloud Storage | T1567.002 | Envoi vers un bucket ou service tiers | Flow Logs, proxy egress |

Ces techniques se chaînent : T1552.005 fournit les credentials, T1078.004 les légitime, T1530 sélectionne les données, T1537 ou T1567.002 les exporte.

> [!quiz] Un bucket privé peut-il fuiter via une presigned URL ?
> Oui. L'URL est signée avec les credentials d'un principal autorisé ; elle n'exige aucun accès public. Si elle fuit, elle reste valide jusqu'à expiration (sept jours maximum) ou révocation de la session signataire. Il faut raccourcir les durées, éviter de journaliser les URLs et signer côté serveur avec un scope minimal.

> [!quiz] Pourquoi une politique de clé KMS peut-elle annuler un droit IAM ?
> Parce que KMS exige l'autorisation de la politique de clé en plus de la politique d'identité. Un rôle avec `kms:Decrypt` sur `*` ne déchiffre pas une CMK dont la politique ne l'autorise pas. La politique de ressource est ici un point de contrôle obligatoire.

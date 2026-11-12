---
title: "Sécurité des e-mails"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau, email]
date: "2025-03-14"
prerequis: ["[[Protocoles Réseau]]", "[[DNS en profondeur]]"]
---

# Sécurité des e-mails

Un mardi matin, la comptable d'une PME reçoit un message de son directeur : il est en déplacement, un fournisseur doit être payé en urgence, voici le nouveau RIB. Le nom d'expéditeur est le bon, la signature aussi. Elle fait le virement. Le directeur n'a jamais envoyé ce message. Cette « arnaque au président » fonctionne parce que le courrier électronique a été conçu, au début des années 1980, pour un petit réseau de chercheurs qui se faisaient confiance : rien, dans le protocole d'origine, ne vérifie que l'expéditeur est bien celui qu'il prétend être, ni ne protège le contenu des regards. Toute la sécurité de l'e-mail a été ajoutée après coup, couche par couche.

## Le trajet d'un e-mail et ses protocoles

Un e-mail emprunte trois protocoles différents. Votre logiciel de messagerie le **soumet** à votre serveur d'envoi avec **SMTP** (*Simple Mail Transfer Protocol*). Ce serveur le **relaie** ensuite, toujours en SMTP, jusqu'au serveur du destinataire, qu'il trouve en interrogeant les enregistrements MX du DNS. Le destinataire, enfin, le **consulte** avec **IMAP** (*Internet Message Access Protocol*), qui laisse les messages sur le serveur et synchronise plusieurs appareils, ou avec **POP3** (*Post Office Protocol*), qui les télécharge, et que l'on n'utilise presque plus.

|**Protocole**|**Rôle**|**Port en clair (ou STARTTLS)**|**Port en TLS direct**|
|---|---|---|---|
|SMTP (relais entre serveurs)|Acheminement d'un serveur à l'autre|25|aucun|
|SMTP (soumission)|Envoi depuis le client vers son serveur|587 (STARTTLS)|465|
|IMAP|Consultation des e-mails sur le serveur|143|993|
|POP3|Récupération des e-mails depuis le serveur|110|995|

## Protéger la connexion

Le premier problème est la confidentialité du transport : sans chiffrement, n'importe qui sur le chemin peut lire les messages et les mots de passe. Deux méthodes existent. Avec **TLS direct** (ports 465, 993, 995), la connexion est chiffrée dès le premier octet. Avec **STARTTLS** (ports 587, 143, 110), la connexion commence en clair, puis le client demande à passer en chiffré ; un attaquant placé sur le chemin peut supprimer cette demande et forcer la conversation à rester en clair, c'est pourquoi les recommandations actuelles (RFC 8314) préfèrent le TLS direct pour les clients.

Entre serveurs, sur le port 25, le chiffrement reste opportuniste : on l'utilise si l'autre côté l'accepte. Des mécanismes comme **MTA-STS** et **DANE** permettent à un domaine d'exiger le chiffrement des messages qu'il reçoit. Enfin, le serveur de soumission doit exiger une authentification, faute de quoi il devient un « relais ouvert » utilisé par les spammeurs.

## Prouver l'origine : SPF, DKIM et DMARC

Le deuxième problème, celui de l'arnaque au président, est l'usurpation d'identité. Trois mécanismes, tous publiés dans le DNS du domaine expéditeur, y répondent.

**SPF** (*Sender Policy Framework*) publie la liste des serveurs autorisés à envoyer du courrier pour le domaine. Le serveur destinataire vérifie que la machine qui lui parle figure dans cette liste. Mais SPF vérifie l'adresse d'enveloppe utilisée par les serveurs, pas l'adresse `From` que voit l'utilisateur, et il casse quand un message est transféré.

**DKIM** (*DomainKeys Identified Mail*) fait signer chaque message par le serveur d'envoi, avec une clé privée dont la clé publique est publiée dans le DNS. Le destinataire vérifie la signature et sait ainsi que le message, ses en-têtes signés et son corps n'ont pas été modifiés depuis qu'il a quitté un serveur du domaine signataire.

**DMARC** (*Domain-based Message Authentication, Reporting and Conformance*) fait le lien. Il exige que le domaine validé par SPF ou par DKIM corresponde au domaine du `From` visible, c'est l'**alignement**, et indique au destinataire quoi faire en cas d'échec : ne rien faire (`p=none`), mettre en quarantaine (`p=quarantine`) ou rejeter (`p=reject`). Il demande aussi des rapports, qui permettent au propriétaire du domaine de voir qui envoie du courrier en son nom.

> [!important] Distinction clé
> SPF valide l'**enveloppe** du mail (le serveur émetteur), DKIM valide le **contenu** (signature du corps et des headers), et DMARC ne fait rien de nouveau lui-même — il dit juste au destinataire quoi faire (rejeter, quarantaine, rien) quand SPF et/ou DKIM échouent. Un domaine avec SPF et DKIM configurés mais sans DMARC laisse chaque fournisseur de messagerie décider seul de la politique à appliquer.

> [!warning] Piège fréquent
> SPF seul ne protège pas contre l'usurpation d'affichage : un attaquant peut passer SPF en envoyant depuis son propre domaine mail, tout en affichant un nom d'expéditeur qui ressemble à celui d'une entreprise connue. Seul DMARC en mode `reject`, combiné à un `From` correctement vérifié, ferme réellement cette voie.

Le déploiement se fait par étapes : publier SPF et DKIM, puis DMARC en mode `none` pour lire les rapports et repérer les services légitimes oubliés (outil d'e-mailing, facturation), avant de passer progressivement à `quarantine` puis `reject`. Depuis 2024, Gmail et Yahoo exigent SPF, DKIM et DMARC des expéditeurs de gros volumes.

Ces mécanismes n'empêchent pas tout. Un attaquant peut enregistrer un domaine ressemblant (`rn` à la place de `m`, un tiret en plus) et le configurer parfaitement, ou jouer seulement sur le nom affiché. C'est pourquoi les filtres, et la vigilance, restent nécessaires.

## Filtrer le spam et le phishing

Les fournisseurs de messagerie combinent de nombreux signaux pour classer les messages : résultats SPF, DKIM et DMARC, réputation de l'adresse IP et du domaine expéditeur, listes de blocage publiques, analyse du contenu, des liens et des pièces jointes, souvent ouvertes dans un bac à sable. On peut y ajouter ses propres listes d'expéditeurs bloqués ou autorisés. Aucun filtre n'étant parfait, la sensibilisation des utilisateurs, à reconnaître une urgence suspecte, vérifier un lien avant de cliquer ou confirmer une demande de virement par un autre canal, reste une ligne de défense essentielle.

## Chiffrer le contenu de bout en bout

Le chiffrement TLS ne protège le message que pendant son transport, d'un serveur à l'autre : sur les serveurs eux-mêmes, il est stocké en clair. Pour qu'il ne soit lisible que par son destinataire, il faut le chiffrer de bout en bout. **PGP**, et son implémentation libre **GnuPG**, s'appuient sur des clés que les utilisateurs échangent et vérifient eux-mêmes. **S/MIME** utilise des certificats délivrés par des autorités de certification, ce qui le rend plus répandu en entreprise. Les deux permettent aussi de signer un message, et donc d'en prouver l'auteur. Ils restent peu utilisés par le grand public, à cause de la difficulté de gérer les clés, et ils ne chiffrent pas l'objet ni les métadonnées.

## Protéger son compte

Enfin, la messagerie est souvent la clé de tous les autres comptes, puisque c'est par elle qu'on réinitialise les mots de passe. Elle mérite un mot de passe long et unique, une authentification à deux facteurs, de préférence par clé de sécurité ou application plutôt que par SMS, et une vérification attentive des destinataires et des pièces jointes avant chaque envoi.

## Ressources

- RFC 7208 (SPF), RFC 6376 (DKIM), RFC 7489 (DMARC) et RFC 8314 (TLS pour la messagerie).
- Les guides de l'ANSSI et de Cybermalveillance.gouv.fr sur la sécurité de la messagerie et l'arnaque au président.
- Des outils comme MXToolbox ou internet.nl pour tester la configuration d'un domaine.

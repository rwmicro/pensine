---
title: "Attention moderne — KV cache, GQA, MLA"
domain: "Applied Sciences"
subdomain: "Computer Science > Data Science > Machine Learning > LLM"
tags: [llm, attention, kv-cache, gqa, mla, rope, flashattention, long-contexte, transformers]
date: "2026-11-26"
prerequis: ["[[Transformers]]"]
---

# Attention moderne — KV cache, GQA, MLA

En 2023, un modèle ouvert lisait 4 000 tokens, quelques pages. En 2026, DeepSeek V4, GLM-5.3, Kimi K3 et Qwen3.8 en lisent un million, l'équivalent d'une dizaine de romans. L'attention du Transformer de 2017 n'a pas changé de principe, mais presque tout ce qui l'entoure a été repensé, parce que son coût explose avec la longueur du texte. Cette note explique pourquoi la génération demande de garder en mémoire un « cache » qui finit par peser plus lourd que le modèle lui-même, et comment les astuces successives (partager les clés, les compresser, les tourner, ne lire que les bonnes) ont permis de passer de quelques pages à des bibliothèques entières.

Le mécanisme d'attention de base (requêtes, clés, valeurs, têtes multiples) est expliqué dans [[Transformers]].

## Générer, un token à la fois

Un modèle de langage génère du texte mot par mot. Pour produire le token numéro 1 001, chacune de ses couches calcule une **requête** (query) pour ce token, et la compare aux **clés** (keys) des 1 000 tokens précédents ; les scores obtenus pondèrent les **valeurs** (values) de ces mêmes tokens. Les clés et valeurs des tokens passés ne changent pas d'une étape à l'autre. Les recalculer à chaque nouveau token serait du gaspillage pur : on les garde en mémoire, et l'on n'ajoute à chaque pas que celles du dernier token. C'est le **cache KV**.

> [!abstract] Définition — Cache KV
> Mémoire qui conserve, pour chaque couche et chaque token déjà traité, les vecteurs clé (K) et valeur (V) de l'attention, afin de ne pas les recalculer à chaque token généré. Sa taille croît linéairement avec la longueur du contexte et le nombre de requêtes servies en parallèle.

Sa taille se calcule simplement. Pour chaque token, chaque couche stocke une clé et une valeur par tête d'attention :

$$\text{cache par token} = 2 \times \text{couches} \times \text{têtes KV} \times \text{dimension par tête} \times \text{octets}$$

Pour Llama 3.1 8B (32 couches, 8 têtes de clés et valeurs de dimension 128, en 16 bits), cela fait 2 × 32 × 8 × 128 × 2 = 131 072 octets, 128 Kio par token. Sur une fenêtre de 128 000 tokens, le cache atteint 16 Gio, autant que les poids du modèle. Et un serveur qui répond à 32 utilisateurs en parallèle en garde 32.

La génération a donc deux régimes très différents. La lecture du texte fourni, le **prefill**, traite tous les tokens du prompt d'un coup : de grosses multiplications de matrices, limitées par la puissance de calcul. La génération proprement dite, le **decode**, traite un seul token à la fois, mais doit relire tous les poids et tout le cache à chaque pas : elle est limitée par la **bande passante mémoire**. Réduire le cache, c'est accélérer directement la génération.

```widget:memoire-llm
modele: Llama 3.1 8B
methode: inference
bits: 16
contexte: 8192
gpu: 24
objectif: Avec Llama 3.1 8B en 16 bits sur une carte de 24 Go, quelle est la plus longue fenêtre de contexte qui tient encore ?
cible: kv_kio=128, bits=16, gpu=24, contexte=32768, tient=1
indice: Les poids occupent déjà 16 Go ; il reste environ 8 Go pour le cache, à 128 Kio par token.
erreur: contexte>32768 → Le cache déborde : 64 000 tokens demandent 8,6 Go de plus. ;; bits<16 → Gardez les poids en 16 bits pour cette question.
bravo: 32 000 tokens (4,3 Go de cache). Passer les poids en 4 bits libérerait 12 Go de plus pour le contexte.
objectif-2: Choisissez DeepSeek-V3 : combien de Kio son cache prend-il par token, alors qu'il est 80 fois plus gros que Llama 3.1 8B ?
cible-2: kv_kio=69
indice-2: Sélectionnez le modèle dans la liste et lisez la ligne « Cache KV par token ».
bravo-2: 69 Kio, deux fois moins que Llama 3.1 8B : c'est l'effet de l'attention latente (MLA), expliquée plus bas.
```

## Partager les clés : MQA et GQA

Dans l'attention multi-têtes d'origine (MHA), chaque tête a ses propres requêtes, clés et valeurs. Avec 32 têtes, le cache stocke 32 clés et 32 valeurs par couche et par token.

En 2019, Noam Shazeer a proposé l'**attention multi-requêtes** (MQA) : les têtes gardent chacune leurs requêtes, mais partagent une seule clé et une seule valeur. Le cache est divisé par le nombre de têtes. La qualité baisse un peu, car toutes les têtes doivent chercher dans la même « bibliothèque ».

Le compromis qui s'est imposé est l'**attention à requêtes groupées** (GQA, Google, 2023) : les têtes sont réparties en quelques groupes, et chaque groupe partage une clé et une valeur. Llama 3.1 8B a 32 têtes de requêtes et 8 groupes : son cache est quatre fois plus petit qu'en MHA, pour une qualité presque identique. C'est devenu le choix par défaut des modèles denses.

| Variante | Têtes de requêtes | Paires clé-valeur gardées | Cache, pour 32 têtes |
|---|---|---|---|
| MHA (2017) | 32 | 32, une par tête | × 1 |
| GQA (2023) | 32 | 8, une par groupe de 4 têtes | ÷ 4 |
| MQA (2019) | 32 | 1, partagée par toutes | ÷ 32 |

## Compresser les clés : l'attention latente de DeepSeek

DeepSeek a pris une autre voie en 2024 avec DeepSeek-V2 : l'**attention latente multi-têtes** (MLA). Au lieu de partager les clés, on les **compresse**. Pour chaque token, le modèle calcule un petit vecteur « latent » de 512 nombres, et c'est lui seul qu'on garde dans le cache. Au moment de l'attention, on reconstruit à partir de lui les clés et valeurs de toutes les têtes, par une multiplication de matrice. Mieux : cette reconstruction peut être fusionnée algébriquement dans le calcul des requêtes, si bien qu'on ne reconstruit jamais vraiment les clés.

Une difficulté technique, la position des tokens (voir plus bas), oblige à garder à part une petite clé de 64 nombres. Au total, 576 nombres par couche et par token, contre 2 × 128 × 128 = 32 768 pour l'attention multi-têtes de même taille : un cache 57 fois plus petit. DeepSeek-V2 annonçait une réduction de 93 % par rapport à son modèle précédent, avec une qualité égale ou meilleure que MHA. Kimi K3 a repris le principe (« Gated MLA »), et son cache ne pèse que 27 Kio par token.

## Coder la position en tournant : RoPE

L'attention, par construction, ne sait pas dans quel ordre sont les tokens : elle compare des vecteurs, sans notion de place. Le Transformer de 2017 ajoutait donc à chaque token un vecteur de position fixe. La méthode qui s'est imposée est le **RoPE** (*Rotary Position Embedding*, 2021).

L'idée est géométrique. On découpe les vecteurs de requête et de clé en paires de nombres, vues comme des points du plan, et l'on fait **tourner** chaque paire d'un angle proportionnel à la position du token. Quand on compare la requête du token m à la clé du token n par un produit scalaire, les deux rotations se compensent en partie, et le résultat ne dépend que de l'écart m − n. Le modèle perçoit ainsi naturellement les distances relatives : « trois mots plus tôt » a le même sens au début et à la fin du texte. Chaque paire tourne à sa propre vitesse, des plus rapides, qui distinguent les voisins immédiats, aux plus lentes, qui repèrent des positions éloignées, comme les aiguilles d'une horloge.

RoPE a un avantage pratique : on peut **étendre** le contexte d'un modèle après coup, en ralentissant les rotations pour que des positions lointaines ressemblent à celles vues à l'entraînement. Les méthodes d'interpolation (NTK, YaRN en 2023) permettent ainsi de passer de 32 000 à 128 000 tokens, voire d'un contexte natif de 262 000 tokens à un million pour Qwen3.8-Flash-Next, avec un court réentraînement.

## Calculer sans écrire : FlashAttention

Le calcul de l'attention lui-même pose un autre problème. Pour n tokens, la matrice des scores fait n × n cases : 10^12 nombres pour un million de tokens. L'écrire dans la mémoire principale du GPU, puis la relire pour appliquer le softmax, prendrait plus de temps que les calculs eux-mêmes.

**FlashAttention** (Tri Dao et ses collègues, 2022) calcule exactement le même résultat sans jamais écrire cette matrice. Il découpe les requêtes, clés et valeurs en tuiles assez petites pour tenir dans la mémoire ultra-rapide intégrée aux cœurs de calcul, et met à jour le softmax tuile par tuile grâce à une astuce de renormalisation en ligne. Le résultat n'est pas une approximation : c'est la même attention, deux à quatre fois plus rapide et avec une mémoire linéaire au lieu de quadratique. Ses versions successives (2023, 2024) suivent les nouvelles générations de GPU, et il est utilisé partout.

## Ne lire que l'essentiel : attentions parcimonieuses et hybrides

FlashAttention rend l'attention plus rapide, mais pas moins coûteuse en principe : chaque nouveau token compare toujours sa requête à toutes les clés précédentes. Pour aller vers le million de tokens, les modèles de 2025 et 2026 ont cessé de tout lire.

L'**attention parcimonieuse** de DeepSeek (DSA, introduite avec DeepSeek-V3.2 en 2025) ajoute un petit « indexeur » très rapide qui estime, pour chaque requête, quels tokens passés sont pertinents, et l'attention complète ne porte que sur les 2 048 meilleurs. GLM-5.3 l'utilise. DeepSeek V4 va plus loin avec une attention hybride, qui combine une attention parcimonieuse sur des blocs compressés et une attention très fortement compressée : à un million de tokens, l'éditeur annonce 27 % du calcul et 10 % du cache de DeepSeek-V3.2.

D'autres équipes mélangent deux types de couches. Les couches d'**attention linéaire** (comme Gated DeltaNet ou la Kimi Delta Attention) ne gardent pas un cache qui grandit avec le texte, mais un état de taille fixe, une sorte de mémoire résumée mise à jour à chaque token, qui coûte la même chose au premier et au millionième token. Elles retrouvent mal un détail précis. On les intercale donc avec des couches d'attention classique, capables de retrouver une information exacte. Qwen3.8-Flash-Next alterne trois couches DeltaNet pour une d'attention parcimonieuse ; Kimi K3 compte 69 couches KDA pour 24 couches MLA.

| Technique | Ce qu'elle réduit | Exemple |
|---|---|---|
| GQA | Cache KV (÷ 4 à ÷ 8) | Llama 3, Mistral |
| MLA | Cache KV (÷ 50 environ) | DeepSeek-V3, Kimi K3 |
| RoPE + YaRN | Rien, mais permet d'étendre le contexte | Presque tous |
| FlashAttention | Mémoire et temps du calcul, résultat exact | Partout |
| Attention parcimonieuse | Calcul par token à long contexte | DeepSeek V3.2 et V4, GLM-5.3 |
| Couches linéaires hybrides | Cache et calcul, au prix d'une mémoire approximative | Qwen3.8-Flash-Next, Kimi K3 |

> [!warning] Piège
> Une fenêtre d'un million de tokens ne garantit pas qu'un modèle exploite bien un million de tokens. Les tests du type « aiguille dans une botte de foin », qui cachent une phrase dans un long texte, sont faciles ; raisonner sur des informations dispersées dans tout le contexte l'est beaucoup moins, et les performances baissent souvent bien avant la limite annoncée. La longueur utile se mesure, elle ne se lit pas sur la fiche.

## Questions de révision

> [!quiz] Pourquoi garde-t-on un cache KV pendant la génération ?
> Parce que les clés et valeurs des tokens passés ne changent pas : les garder évite de les recalculer à chaque nouveau token, au prix d'une mémoire qui grandit avec le contexte.

> [!quiz] Combien pèse le cache KV de Llama 3.1 8B pour 128 000 tokens en 16 bits ?
> - [ ] Environ 1 Go.
>   C'est l'ordre de grandeur pour 8 000 tokens.
> - [x] Environ 16 Gio.
>   128 Kio par token × 131 072 tokens = 16 Gio, autant que les poids du modèle.
> - [ ] Rien, le cache est compressé.
>   Llama 3.1 utilise GQA, qui divise le cache par quatre, mais ne le supprime pas.

> [!quiz] Quelle est la différence entre GQA et MLA ?
> GQA réduit le cache en faisant partager les mêmes clés et valeurs à des groupes de têtes ; MLA le réduit en ne stockant qu'un petit vecteur latent par token, à partir duquel on reconstruit les clés et valeurs de toutes les têtes.

> [!quiz] Pourquoi le produit scalaire de deux vecteurs tournés par RoPE ne dépend-il que de leur écart de position ?
> - [x] Parce que tourner la requête de m angles et la clé de n angles revient, dans le produit scalaire, à une rotation de m − n.
>   Le produit scalaire est invariant par rotation commune ; seule la différence des angles compte.
> - [ ] Parce que RoPE ajoute la position au vecteur.
>   C'était la méthode du Transformer de 2017, pas celle de RoPE.
> - [ ] Parce que les vecteurs sont normalisés.
>   La normalisation ne joue aucun rôle dans cette propriété.

> [!quiz] FlashAttention calcule-t-il une approximation de l'attention ?
> Non : il calcule exactement le même résultat, mais par tuiles, sans jamais écrire la matrice n × n des scores en mémoire principale, ce qui le rend plus rapide et économe.

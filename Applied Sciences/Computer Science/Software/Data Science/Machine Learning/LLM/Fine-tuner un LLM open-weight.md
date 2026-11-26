---
title: "Fine-tuner un LLM open-weight"
domain: "Applied Sciences"
subdomain: "Computer Science > Data Science > Machine Learning > LLM"
tags: [llm, fine-tuning, lora, qlora, unsloth, trl, moe, gpu, pratique]
date: "2026-11-26"
prerequis: ["[[Fine Tuning]]", "[[Mixture of Experts]]"]
---

# Fine-tuner un LLM open-weight

Télécharger les poids de DeepSeek V4 ou de GLM-5.3 est gratuit. Les adapter à ses propres données l'est beaucoup moins : il faudrait plusieurs serveurs remplis de cartes graphiques à 30 000 euros pièce. Mais un modèle de 8 à 30 milliards de paramètres se fine-tune sur une seule carte, parfois sur un ordinateur portable, en quelques heures, et donne souvent de meilleurs résultats sur une tâche précise qu'un modèle géant utilisé tel quel. Cette note est un guide pratique : quand fine-tuner (et quand ne pas le faire), combien de mémoire il faut et pourquoi, comment préparer les données, quels réglages choisir, ce qui change avec un MoE, et comment mesurer le résultat.

Les principes du transfert d'apprentissage et de LoRA sont expliqués dans [[Fine Tuning]] ; les architectures MoE dans [[Mixture of Experts]].

## D'abord, faut-il fine-tuner ?

Le fine-tuning change la **façon** dont un modèle répond plus que ce qu'il sait. Il est excellent pour imposer un format (toujours répondre en JSON valide), un style (le ton d'une marque, une langue rare), un comportement spécialisé (classer des tickets, extraire des champs d'un contrat), ou pour faire tenir dans un petit modèle rapide ce qu'un grand modèle faisait bien. Il est mauvais pour **ajouter des connaissances** : un modèle à qui l'on montre la documentation interne d'une entreprise l'apprend mal, invente des détails, et l'oublie dès que la documentation change.

| Besoin | Meilleure approche |
|---|---|
| Répondre à partir de documents qui évoluent | Recherche documentaire ([[RAG]]) |
| Changer le ton, le format, la langue de sortie | Prompt soigné, puis fine-tuning si ça ne suffit pas |
| Une tâche étroite et répétitive, à grand volume | Fine-tuning d'un petit modèle |
| Apprendre à raisonner sur des problèmes vérifiables | Fine-tuning puis renforcement (GRPO) |
| Utiliser un grand modèle moins cher | Distillation : fine-tuner un petit modèle sur ses réponses |

La règle pratique est de commencer par un bon prompt sur un bon modèle, de mesurer, et de ne fine-tuner que si l'écart à combler est clair et mesurable.

## Combien de mémoire, et pourquoi

Le premier obstacle est la mémoire du GPU. Elle se calcule assez bien en comptant les octets par paramètre.

Un **fine-tuning complet** met à jour tous les poids. En précision mixte avec l'optimiseur Adam, chaque paramètre coûte environ 16 octets : 2 pour le poids en 16 bits, 2 pour son gradient, 4 pour une copie en 32 bits qui accumule les petites mises à jour, et 8 pour les deux moyennes mobiles que tient Adam. Un modèle de 8 milliards de paramètres demande donc 128 Go avant même de compter les activations : plusieurs cartes de 80 Go.

**LoRA** (*Low-Rank Adaptation*) gèle tous les poids d'origine et n'entraîne que de petites matrices ajoutées à côté, de l'ordre de 0,1 à 1 % des paramètres. Les poids gelés n'ont besoin ni de gradient ni d'état d'optimiseur : 2 octets par paramètre. **QLoRA** va plus loin en stockant ces poids gelés en 4 bits, soit environ un demi-octet par paramètre, et ne les décompresse qu'au moment du calcul.

```widget:memoire-llm
modele: Llama 3.1 8B
methode: full
gpu: 80
objectif: Pour un fine-tuning complet de Llama 3.1 8B, quelle configuration de GPU suffit ?
cible: methode=full, params=8, tient=1
indice: Il faut environ 16 octets par paramètre.
erreur: methode!=full → Restez sur le fine-tuning complet pour cette question. ;; gpu<=80 → 128 Go ne tiennent pas sur une seule carte de 80 Go.
bravo: Il faut un serveur à plusieurs GPU : c'est le prix du fine-tuning complet.
objectif-2: Trouvez une méthode qui permet de fine-tuner ce même modèle sur un ordinateur portable avec 8 Go de mémoire graphique.
cible-2: methode=qlora, params=8, gpu=8, tient=1
indice-2: Il faut que les poids gelés tiennent dans 8 Go : en 16 bits, ils en font déjà 16.
bravo-2: QLoRA : environ 5 Go de poids et d'adaptateurs. Il restera à loger les activations, en gardant des séquences courtes.
```

À ces chiffres s'ajoutent les **activations**, les résultats intermédiaires gardés pour la rétropropagation, qui croissent avec la longueur des exemples et la taille du lot. Le *gradient checkpointing*, qui recalcule une partie des activations au lieu de les garder, les réduit beaucoup au prix d'environ 30 % de temps en plus.

## Choisir le modèle de départ

Pour un premier projet, le bon point de départ est un modèle **dense** de 7 à 32 milliards de paramètres, sous une licence permissive (Apache 2.0 ou MIT), dont la version « instruct » se débrouille déjà correctement sur la tâche. Les familles Qwen et gpt-oss sont les plus utilisées en 2026, avec un outillage mûr. Un modèle plus petit, bien fine-tuné, bat souvent un modèle plus gros utilisé tel quel sur une tâche étroite, et il coûte dix fois moins cher à servir.

Les grands MoE de 2026 sont une autre affaire. DeepSeek V4-Flash (284 milliards de paramètres) demande déjà, même en LoRA, de l'ordre de deux cartes H200 de 141 Go ; DeepSeek V4-Pro, GLM-5.3 et Kimi K3 demandent un véritable cluster. Pour un particulier, la voie réaliste vers ces modèles est la **distillation** : faire générer par le grand modèle, via une API, des milliers de bonnes réponses sur sa tâche, puis fine-tuner un petit modèle dessus. La licence du grand modèle doit l'autoriser ; celles de DeepSeek (MIT) et de GLM le permettent.

## Les données : peu, mais bonnes

La qualité des exemples compte beaucoup plus que leur nombre. Quelques centaines d'exemples très soignés suffisent souvent pour un format ou un style, quelques milliers pour une tâche spécialisée. Chaque exemple est une conversation, au format que comprennent les outils :

```json
{"messages": [
  {"role": "system", "content": "Tu classes les tickets du support en une catégorie."},
  {"role": "user", "content": "Mon colis est arrivé ouvert et il manque un article."},
  {"role": "assistant", "content": "{\"categorie\": \"livraison\", \"urgence\": \"moyenne\"}"}
]}
```

Trois règles évitent la plupart des échecs. Utiliser le **modèle de conversation** (*chat template*) exact du modèle de départ : chaque famille balise différemment les rôles, et un mauvais balisage dégrade le modèle en silence. N'entraîner que sur les **réponses** de l'assistant, pas sur les questions, pour que le modèle apprenne à répondre et non à imiter l'utilisateur. Et garder de côté un **jeu de test** que le modèle ne verra jamais pendant l'entraînement.

## Les réglages qui comptent

LoRA ajoute à une matrice de poids W de taille d × d un produit B A de deux matrices fines, de taille d × r et r × d, où le **rang** r vaut typiquement 8 à 64. Le modèle calcule W x + (α / r) B A x : seul le petit terme est entraîné, et le facteur α (*lora_alpha*) règle son poids.

| Réglage | Valeur de départ | Pourquoi |
|---|---|---|
| Rang r | 16 à 32 | Assez pour un format ou une tâche ; monter à 64 ou plus pour beaucoup de données |
| lora_alpha | égal à r | Garde l'échelle des mises à jour stable quand on change r |
| Modules ciblés | toutes les couches linéaires, attention et MLP | Cibler seulement l'attention donne nettement moins bien |
| Taux d'apprentissage | 1e-4 à 2e-4 | Environ dix fois celui d'un fine-tuning complet |
| Époques | 1 à 3 | Au-delà, le modèle récite ses exemples |
| Lot effectif | 16 à 64 exemples | Par accumulation de gradients si la mémoire manque |

Une étude de Thinking Machines (« LoRA Without Regret », 2025) a précisé ces règles : appliqué à toutes les couches, y compris les MLP, et avec un taux d'apprentissage environ dix fois plus élevé, LoRA égale le fine-tuning complet sur des jeux de données de taille petite à moyenne. Il ne décroche que quand les données dépassent ce que ses petites matrices peuvent absorber.

## En pratique : Unsloth et TRL

Les deux outils les plus utilisés en 2026 sont **TRL**, la bibliothèque de Hugging Face qui fournit les entraîneurs (SFT, DPO, GRPO), et **Unsloth**, qui accélère l'entraînement et réduit la mémoire grâce à des noyaux de calcul optimisés. Axolotl et LLaMA-Factory proposent la même chose à partir d'un simple fichier de configuration. Le squelette d'un entraînement ressemble à ceci (les noms de paramètres évoluent d'une version à l'autre, la documentation fait foi) :

```python
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen3-8B",
    max_seq_length=4096,
    load_in_4bit=True,          # QLoRA ; False pour LoRA en 16 bits
)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    use_gradient_checkpointing="unsloth",
)

dataset = load_dataset("json", data_files="tickets.jsonl", split="train")

trainer = SFTTrainer(
    model=model,
    processing_class=tokenizer,
    train_dataset=dataset,
    args=SFTConfig(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,   # lot effectif de 16
        learning_rate=2e-4,
        num_train_epochs=2,
        output_dir="sortie",
    ),
)
trainer.train()
model.save_pretrained("adaptateur-tickets")   # quelques dizaines de Mo
```

Le résultat est un **adaptateur** de quelques dizaines de mégaoctets, qu'on charge par-dessus le modèle de base. On peut le fusionner dans les poids, puis convertir le tout au format GGUF pour llama.cpp ou Ollama ; ou le servir tel quel avec vLLM, qui sait charger plusieurs adaptateurs sur un même modèle de base. Pour aller plus loin, le même modèle peut ensuite passer par DPO (préférences) ou GRPO (récompenses vérifiables), avec les entraîneurs correspondants de TRL (voir [[Modèles de raisonnement et apprentissage par renforcement]]).

## Le cas particulier des MoE

Fine-tuner un MoE demande quelques précautions supplémentaires. Tous les experts doivent tenir en mémoire, même si chaque token n'en utilise que quelques-uns : Qwen3-30B-A3B, qui n'a que 3 milliards de paramètres actifs, demande environ 63 Go en LoRA 16 bits d'après Unsloth, autant qu'un modèle dense de 30 milliards. On **gèle le routeur** : le réentraîner sur peu de données perturbe l'équilibre de charge appris au pré-entraînement, et les outils le désactivent par défaut. On applique LoRA aux projections des experts et de l'attention. Enfin, début 2026, Unsloth déconseillait QLoRA pour les MoE, la bibliothèque de quantification bitsandbytes ne gérant pas encore leurs experts en 4 bits : il faut alors LoRA en 16 bits.

Le modèle MoE le plus accessible reste gpt-oss-20b (21 milliards de paramètres, 3,6 milliards actifs), qu'Unsloth fine-tune en moins de 13 Go.

## Mesurer, et se méfier

Une courbe de perte qui descend ne dit pas que le modèle est meilleur, seulement qu'il ressemble davantage à ses exemples. Il faut évaluer sur le jeu de test mis de côté, en comparant au modèle de départ et, si possible, à un bon prompt sur un grand modèle. Pour des réponses ouvertes, un grand modèle peut servir de juge, à condition de vérifier à la main un échantillon de ses verdicts.

> [!warning] Piège
> Le fine-tuning fait oublier. Un modèle entraîné intensivement sur une tâche étroite perd une partie de ses capacités générales : c'est l'**oubli catastrophique**. Il peut aussi perdre ses garde-fous de sécurité, même avec des données anodines. LoRA, qui ne modifie qu'un petit sous-espace, en limite l'ampleur ; garder quelques exemples généraux dans le mélange et tester le modèle hors de sa tâche permettent de le repérer.

## Questions de révision

> [!quiz] Pourquoi un fine-tuning complet coûte-t-il environ 16 octets par paramètre ?
> Poids en 16 bits (2), gradient en 16 bits (2), copie en 32 bits pour accumuler les mises à jour (4), et les deux moments d'Adam en 32 bits (4 + 4).

> [!quiz] Le fine-tuning est-il un bon moyen d'apprendre au modèle la documentation interne d'une entreprise ?
> - [ ] Oui, c'est son usage principal.
>   Le fine-tuning change surtout le comportement et le format, et ajoute mal des connaissances.
> - [x] Non, une recherche documentaire (RAG) convient mieux.
>   Le modèle retrouve les passages à jour au lieu de les mémoriser imparfaitement.
> - [ ] Oui, à condition de faire beaucoup d'époques.
>   Plus d'époques mène au surapprentissage et à la récitation, pas à une connaissance fiable.

> [!quiz] Pourquoi gèle-t-on le routeur quand on fine-tune un MoE ?
> Parce que le réentraîner sur peu de données dérègle l'équilibre de charge appris au pré-entraînement : quelques experts risquent de recevoir tous les tokens.

> [!quiz] Quel taux d'apprentissage choisir pour LoRA, comparé au fine-tuning complet ?
> - [x] Environ dix fois plus élevé.
>   Les petites matrices de LoRA demandent des pas plus grands ; 1e-4 à 2e-4 est un bon départ.
> - [ ] Le même.
>   Avec le même taux, LoRA apprend trop lentement.
> - [ ] Dix fois plus faible.
>   C'est l'inverse : LoRA supporte et demande un taux plus élevé.

> [!quiz] Comment profiter d'un très grand modèle comme DeepSeek V4 sans pouvoir le fine-tuner ?
> Par distillation : on lui fait produire de bonnes réponses sur sa tâche, puis on fine-tune un petit modèle dessus, si la licence du grand modèle l'autorise.

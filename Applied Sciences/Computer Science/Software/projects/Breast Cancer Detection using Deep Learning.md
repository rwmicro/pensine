---
title: "Breast Cancer Detection using Deep Learning"
domain: "Applied Sciences"
subdomain: "Computer Science > projects"
tags: [sciences-appliquées, informatique]
date: "2025-02-15"
---

# Breast Cancer Detection using Deep Learning

Projet de détection du cancer du sein par deep learning, à partir d'images histologiques (coupes de tissu au microscope).


## Objectif

Entraîner un modèle CNN (Convolutional Neural Network) à classifier des images de biopsies comme **bénignes** ou **malignes**.


## Dataset — BreaKHis

Le dataset standard pour ce type de projet est **BreaKHis** (Breast Cancer Histopathological Image Classification).

- **Source** : [Kaggle BreaKHis](https://www.kaggle.com/datasets/ambarish/breakhis)
- **~7 900 images** de tissus mammaires
- **2 classes** : bénin (benign) / malin (malignant)
- **4 grossissements** : 40×, 100×, 200×, 400×
- **Format** : PNG, 700×460 pixels

Alternative : **CBIS-DDSM** (mammographies) sur TCIA.


## Architecture recommandée

### Option 1 : Transfer Learning (recommandé pour débuter)
Utiliser un modèle pré-entraîné sur ImageNet et le fine-tuner.

```python
import torch
import torchvision.models as models
import torch.nn as nn

# Charger ResNet50 pré-entraîné
model = models.resnet50(pretrained=True)

# Remplacer la dernière couche pour 2 classes
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 2)

# Geler les couches basses (optionnel)
for param in model.parameters():
    param.requires_grad = False
for param in model.fc.parameters():
    param.requires_grad = True
```

Modèles efficaces : **ResNet50**, **EfficientNet-B0**, **VGG16**, **DenseNet121**

### Option 2 : CNN from scratch
```python
model = nn.Sequential(
    nn.Conv2d(3, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32, 64, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(64 * 56 * 56, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, 2)
)
```


## Pipeline complet

```python
from torchvision import transforms, datasets
from torch.utils.data import DataLoader

# 1. Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# 2. Dataset
dataset = datasets.ImageFolder('data/', transform=transform)
train_set, val_set = torch.utils.data.random_split(dataset, [0.8, 0.2])
train_loader = DataLoader(train_set, batch_size=32, shuffle=True)

# 3. Loss & Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

# 4. Training loop
for epoch in range(20):
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
```


## Métriques d'évaluation

Pour un problème médical, l'**accuracy seule ne suffit pas** — le dataset est souvent déséquilibré.

| Métrique | Importance |
|----------|-----------|
| **Accuracy** | Vue globale |
| **Sensitivity (Recall)** | Taux de vrais positifs — crucial (rater un cancer = dangereux) |
| **Specificity** | Taux de vrais négatifs |
| **AUC-ROC** | Performance globale du classificateur |
| **F1-Score** | Équilibre précision/rappel |

```python
from sklearn.metrics import classification_report, roc_auc_score
print(classification_report(y_true, y_pred))
```


## Résultats typiques

Avec ResNet50 + fine-tuning sur BreaKHis :
- Accuracy : **~90-95%**
- AUC-ROC : **~0.95+**

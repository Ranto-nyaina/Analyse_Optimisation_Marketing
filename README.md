# 📊 Dashboard — Analyse & Optimisation Marketing

Projet académique du **Module 8** portant sur l'analyse et l'optimisation marketing : segmentation client, performance des campagnes, et modélisation exploratoire du churn / CLV.

L'objectif est de fournir un dashboard interactif permettant d'explorer les données clients, ventes et campagnes marketing, et d'illustrer une démarche de segmentation et de prédiction de churn, avec un regard critique sur les limites méthodologiques du modèle.

---

## 🎯 Objectif du projet

Un dashboard marketing doit permettre de répondre à trois besoins concrets :

* comprendre qui sont les clients et comment les regrouper (segmentation) ;
* évaluer la performance des campagnes marketing par canal ;
* anticiper le risque de perte de clients (churn) et leur valeur potentielle (CLV).

Ce projet propose donc une solution qui :

* recalcule en direct une segmentation K-means à partir des données clients et ventes ;
* calcule les indicateurs clés de performance des campagnes (CTR, conversion, CPC, CPA) ;
* expose les résultats d'un modèle exploratoire de churn et de CLV ;
* donne un accès direct aux données brutes pour vérification et audit.

---

## 📌 Problématique

**Comment exploiter les données clients, ventes et campagnes pour segmenter la clientèle, mesurer l'efficacité marketing par canal, et identifier les clients à risque de churn — tout en assumant les limites d'un modèle entraîné sur un très petit échantillon ?**

---

## 🗂️ Données utilisées

Le projet s'appuie sur 4 fichiers sources :

| Fichier | Rôle |
|---|---|
| `customers_data.csv` | Données clients, utilisées pour la segmentation |
| `sales_data.csv` | Historique des ventes, utilisé pour la segmentation et le proxy de churn |
| `marketing_data.csv` | Données de campagnes, utilisées pour les KPI par canal |
| `churn_clv_results.csv` | Résultats du modèle exploratoire churn/CLV (généré par `churn_clv.py`) |
| `churn_clv_summary.json` | Résumé synthétique des résultats churn/CLV |

⚠️ **Point critique à connaître dès maintenant** : le modèle de churn est entraîné sur **5 clients seulement**, avec un **proxy de churn** (absence de vente enregistrée) faute de véritable variable de résiliation. Les résultats sont **illustratifs**, pas fiables statistiquement. Voir [Limites du projet](#-limites-du-projet) et la section 6 du rapport pour le détail méthodologique.

---

# 🏗️ Architecture du projet

```text
        ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
        │ customers_data.csv│   │  sales_data.csv    │   │ marketing_data.csv│
        └─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
                  │                        │                        │
                  └───────────┬────────────┘                        │
                              ▼                                     ▼
                  ┌───────────────────────┐               ┌───────────────────────┐
                  │  Segmentation K-means │               │   KPI Campagnes       │
                  │  (recalcul en direct) │               │  CTR / Conversion /   │
                  │                       │               │  CPC / CPA par canal  │
                  └───────────┬───────────┘               └───────────┬───────────┘
                              │                                       │
        ┌─────────────────────┐                                      │
        │   churn_clv.py      │                                      │
        │ (script exploratoire│                                      │
        │  churn/CLV, hors    │                                      │
        │  live du dashboard) │                                      │
        └──────────┬───────────┘                                     │
                   ▼                                                 │
        ┌───────────────────────┐                                    │
        │ churn_clv_results.csv │                                    │
        │ churn_clv_summary.json│                                    │
        └──────────┬─────────────┘                                   │
                   │                                                 │
                   └───────────────────┬─────────────────────────────┘
                                        ▼
                             ┌───────────────────────┐
                             │      Streamlit         │
                             │      app.py             │
                             │  (Segmentation /        │
                             │   Campagnes / Churn &   │
                             │   CLV / Données)        │
                             └───────────────────────┘
```

Point important : la segmentation et les KPI campagnes sont **recalculés en direct** à chaque lancement du dashboard. Le churn/CLV, lui, est **précalculé** par `churn_clv.py` et simplement lu par le dashboard — il faut relancer ce script manuellement si les données sources changent.

---

# 🛠️ Technologies utilisées

## Langage

* Python 3

## Analyse et traitement de données

* Pandas
* NumPy

## Machine Learning

* Scikit-learn (K-means pour la segmentation)

## Dashboard

* Streamlit

## Gestion du projet

* Git
* GitHub

---

# 📁 Structure du projet

```text
dashboard-marketing/
│
├── data/
│   ├── customers_data.csv
│   ├── sales_data.csv
│   ├── marketing_data.csv
│   ├── churn_clv_results.csv
│   └── churn_clv_summary.json
│
├── churn_clv.py
├── app.py
│
├── requirements.txt
└── README.md
```

---

# 🔄 Pipeline de traitement

## 1. Segmentation client

Réalisée directement dans `app.py` à partir de `customers_data.csv` et `sales_data.csv`.

* Algorithme : **K-means**
* Nombre de groupes : **3**
* Recalcul : à chaque chargement du dashboard (pas de modèle sauvegardé)

## 2. Analyse des campagnes

Réalisée directement dans `app.py` à partir de `marketing_data.csv`.

Indicateurs calculés par canal :

* **CTR** (taux de clic)
* **Taux de conversion**
* **CPC** (coût par clic)
* **CPA** (coût par acquisition)

## 3. Churn & CLV

Réalisée en amont, hors dashboard, par le script `churn_clv.py`.

* Génère `churn_clv_results.csv` et `churn_clv_summary.json`
* Le dashboard se contente de **lire** ces fichiers dans l'onglet dédié
* L'avertissement de fiabilité est affiché directement dans l'onglet, pas seulement dans la documentation

### Régénérer les résultats churn/CLV

Si les fichiers CSV sources changent, il faut relancer le script manuellement — le dashboard ne le fait pas automatiquement :

```bash
python churn_clv.py
```

---

# 📊 Contenu du dashboard

Le dashboard est organisé en 4 onglets :

### 🧩 Segmentation

* Clustering K-means (3 groupes) recalculé en direct
* Basé sur `customers_data.csv` et `sales_data.csv`

### 📣 Campagnes

* CTR, taux de conversion, CPC, CPA par canal
* Basé sur `marketing_data.csv`

### ⚠️ Churn & CLV

* Résultats du modèle exploratoire (`churn_clv.py`)
* Avertissement de fiabilité affiché directement dans l'onglet
* À ne pas interpréter comme un modèle de production

### 🗄️ Données

* Consultation brute des 4 fichiers sources, pour audit et vérification

---

# 🚀 Installation

## 1. Cloner le projet

```bash
git clone <url-du-depot>
cd dashboard-marketing
```

## 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 3. Lancer le dashboard

```bash
streamlit run app.py
```

Le dashboard s'ouvre dans le navigateur, par défaut à l'adresse :

```text
http://localhost:8501
```

---

# ⚠️ Limites du projet

À prendre au sérieux avant toute lecture des résultats churn/CLV :

* le modèle de churn est entraîné sur **5 clients seulement** — ce n'est pas un échantillon statistiquement exploitable ;
* le churn est approximé par un **proxy** (absence de vente enregistrée), pas par une vraie variable de résiliation — ce proxy peut confondre churn réel et simple pause d'achat ;
* les résultats churn/CLV sont **illustratifs**, destinés à démontrer une démarche méthodologique, pas à produire une prédiction fiable ;
* la segmentation K-means est recalculée à chaque lancement, sans contrôle de stabilité des clusters d'une exécution à l'autre ;
* aucune métrique de performance (précision, rappel, silhouette score) n'est actuellement affichée dans le dashboard pour objectiver la qualité des modèles.

Le détail méthodologique complet est disponible dans la section 6 du rapport.

---

# 🚀 Perspectives d'amélioration

### Churn & CLV

* collecter une vraie variable de résiliation plutôt qu'un proxy ;
* augmenter la taille de l'échantillon avant toute conclusion opérationnelle ;
* afficher les métriques de performance du modèle (précision, rappel, AUC) dans le dashboard.

### Segmentation

* fixer une graine aléatoire (seed) pour la reproductibilité des clusters ;
* afficher un score de qualité du clustering (silhouette score) ;
* sauvegarder le modèle plutôt que de le recalculer à chaque lancement.

### Architecture

* séparer clairement le calcul (batch) de l'affichage (dashboard) pour la segmentation, comme c'est déjà le cas pour le churn/CLV ;
* ajouter des tests automatisés sur les calculs de KPI ;
* versionner les résultats churn/CLV avec un horodatage.

---

# 📚 Compétences mises en œuvre

* Analyse de données marketing
* Segmentation client (K-means)
* Calcul d'indicateurs de performance (CTR, conversion, CPC, CPA)
* Modélisation exploratoire (churn, CLV)
* Esprit critique méthodologique (taille d'échantillon, proxy, limites)
* Dashboard interactif (Streamlit)
* Git / GitHub

---

# 👨‍🎓 Contexte académique

**Module :** Module 8 — Analyse et Optimisation Marketing
**Projet :** Dashboard interactif (segmentation, campagnes, churn/CLV)

---

# 📌 Conclusion

Ce dashboard propose une chaîne d'analyse marketing complète : segmentation client recalculée en direct, KPI de performance par canal, et exploration d'un modèle de churn/CLV.

Sa principale valeur pédagogique n'est pas la fiabilité du modèle de churn — délibérément limité par la taille de l'échantillon — mais la démonstration d'une démarche complète **Données → Segmentation → KPI → Modélisation exploratoire → Dashboard**, avec une transparence assumée sur les limites méthodologiques plutôt qu'une présentation de résultats surinterprétés.

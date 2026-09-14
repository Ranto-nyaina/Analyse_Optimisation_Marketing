# Dashboard — Analyse & Optimisation Marketing

Dashboard interactif du module M8 (segmentation, campagnes, churn/CLV).

## Installation et lancement

```bash
pip install -r requirements.txt
streamlit run app.py
```

Le dashboard s'ouvre ensuite dans le navigateur à l'adresse indiquée dans le terminal
(par défaut http://localhost:8501).

## Contenu

- **Segmentation** : clustering K-means (3 groupes) recalculé en direct à partir de
  `customers_data.csv` et `sales_data.csv`.
- **Campagnes** : CTR, taux de conversion, CPC, CPA par canal à partir de `marketing_data.csv`.
- **Churn & CLV** : résultats du modèle exploratoire (`churn_clv.py`), avec l'avertissement
  de fiabilité affiché directement dans l'onglet.
- **Données** : consultation brute des 4 fichiers sources.

## Régénérer les résultats churn/CLV

Si les fichiers CSV sources changent, relancer :

```bash
python churn_clv.py
```

Cela met à jour `churn_clv_results.csv` et `churn_clv_summary.json`, lus par le dashboard.

## Limite à connaître

Le modèle de churn est entraîné sur 5 clients avec un proxy de churn (absence de vente
enregistrée), faute de vraie variable de résiliation. Les résultats sont illustratifs.
Voir la section 6 du rapport pour le détail méthodologique.

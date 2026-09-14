# Analyse & Optimisation Marketing — Segmentation Client

Projet pédagogique — École Nationale d'Informatique (ENI), Université de Fianarantsoa
Mention Intelligence Artificielle.

Exploitation de données clients, produits, ventes et campagnes pour segmenter la
clientèle, analyser les comportements d'achat, évaluer les performances marketing et
proposer une stratégie digitale personnalisée assistée par l'IA.

## Structure du dépôt

```
.
├── rapport/
│   ├── Rapport_Analyse_Optimisation_Marketing.docx
│   └── Rapport_Analyse_Optimisation_Marketing.pdf
├── presentation/
│   └── Presentation_Analyse_Optimisation_Marketing.pptx
├── dashboard/
│   ├── app.py                  # application Streamlit
│   ├── churn_clv.py             # pipeline churn / CLV (module M6)
│   ├── churn_clv_results.csv    # sortie du pipeline (générée)
│   ├── churn_clv_summary.json   # sortie du pipeline (générée)
│   ├── requirements.txt
│   └── README.md
└── data/
    ├── customers_data.csv
    ├── sales_data.csv
    ├── products_data.csv
    └── marketing_data.csv
```

## Lancer le dashboard en local

```bash
git clone <url-de-ce-depot>
cd <nom-du-depot>/dashboard
pip install -r requirements.txt
python churn_clv.py        # régénère les résultats churn/CLV si data/ a changé
streamlit run app.py
```

## Modules couverts (cf. cahier des charges pédagogique)

| Module | Contenu | Où le trouver |
|---|---|---|
| M1 | Enjeux stratégiques | rapport, section 1 |
| M2 | Exploration des données | rapport, section 2-3 ; dashboard, onglet Données |
| M3-M4 | Segmentation & profils | rapport, section 4 ; dashboard, onglet Segmentation |
| M5 | Performance campagnes | rapport, section 5 ; dashboard, onglet Campagnes |
| M6 | Churn / CLV | rapport, section 6 ; dashboard, onglet Churn & CLV |
| M7 | Stratégie digitale | rapport, section 7 |
| M8 | Dashboard interactif | dossier dashboard/ |
| M9 | Présentation finale | presentation/, rapport section 9 |

## Avertissement méthodologique

L'échantillon fourni est volontairement restreint (5 clients, 5 ventes, 5 produits,
5 campagnes). Les résultats de segmentation et du modèle churn/CLV sont illustratifs :
voir le rapport (sections 4 et 6) et le dashboard pour le détail des limites.

## Licence / usage

Projet académique — ENI Fianarantsoa. Usage pédagogique uniquement.

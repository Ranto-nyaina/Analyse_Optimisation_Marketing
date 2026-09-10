"""
Module 6 -- Prediction churn / CLV
-----------------------------------
ATTENTION METHODOLOGIQUE (a lire avant toute utilisation des resultats) :
Avec 5 clients seulement, aucun modele de machine learning ne peut etre
valide statistiquement. Ce script produit tout de meme un pipeline complet
(feature engineering, label proxy, entrainement, evaluation) pour repondre
a la demande du cahier des charges, mais les metriques de performance
(accuracy, etc.) n'ont ici qu'une valeur pedagogique / illustrative :
elles ne mesurent pas une capacite de generalisation reelle.
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler

REF_DATE = pd.Timestamp("2023-02-01")  # date de reference = juste apres la derniere campagne connue

customers = pd.read_csv("customers_data.csv", parse_dates=["Join_Date"])
sales = pd.read_csv("sales_data.csv", parse_dates=["Date"])

# ---- agregats de vente par client ----
sales_agg = sales.groupby("Customer_ID").agg(
    Nb_Achats=("Sale_ID", "count"),
    Qte_Totale=("Quantity", "sum"),
    CA_Observe=("Sale_Price", lambda s: (s * sales.loc[s.index, "Quantity"]).sum()),
    Derniere_Date=("Date", "max"),
).reset_index()

df = customers.merge(sales_agg, on="Customer_ID", how="left")
df[["Nb_Achats", "Qte_Totale", "CA_Observe"]] = df[["Nb_Achats", "Qte_Totale", "CA_Observe"]].fillna(0)

# ---- anciennete (jours depuis inscription) ----
df["Anciennete_j"] = (REF_DATE - df["Join_Date"]).dt.days

# ---- proxy de churn : aucune vente enregistree dans l'historique fourni ----
# ATTENTION : c'est une regle metier (proxy), pas une donnee reelle de resiliation.
df["Churn_proxy"] = (df["Nb_Achats"] == 0).astype(int)

# ---- recence (jours depuis dernier achat ; si aucun achat -> anciennete) ----
df["Recence_j"] = np.where(
    df["Derniere_Date"].notna(),
    (REF_DATE - df["Derniere_Date"]).dt.days,
    df["Anciennete_j"],
)

# ---- CLV historique observee (depense totale connue) ----
df["CLV_historique"] = df["Total_Spent"]

# ---- CLV projetee sur 12 mois (regle simple : depense / anciennete * 365) ----
df["CLV_projetee_12m"] = np.where(
    df["Anciennete_j"] > 0,
    (df["Total_Spent"] / df["Anciennete_j"]) * 365,
    df["Total_Spent"],
).round(2)

# =========================================================
# Modele exploratoire de churn (Regression Logistique)
# =========================================================
features = ["Age", "Total_Spent", "Anciennete_j", "Recence_j"]
X = df[features].values
y = df["Churn_proxy"].values

scaler = StandardScaler()
Xs = scaler.fit_transform(X)

model_note = ""
loo_predictions = []
if y.sum() == 0 or y.sum() == len(y):
    model_note = "Impossible d'entrainer/valider (une seule classe presente dans le proxy de churn)."
else:
    loo = LeaveOneOut()
    correct = 0
    for train_idx, test_idx in loo.split(Xs):
        # garde-fou : si l'ensemble d'entrainement ne contient qu'une classe,
        # la regression logistique ne peut pas etre ajustee -> on le signale
        if len(set(y[train_idx])) < 2:
            loo_predictions.append(None)
            continue
        clf = LogisticRegression()
        clf.fit(Xs[train_idx], y[train_idx])
        pred = clf.predict(Xs[test_idx])[0]
        loo_predictions.append(int(pred))
        if pred == y[test_idx][0]:
            correct += 1
    valid = [p for p in loo_predictions if p is not None]
    model_note = (
        f"Validation leave-one-out sur {len(valid)}/{len(y)} clients evaluables "
        f"(les autres cas n'ont pas pu etre testes : classe unique dans le pli d'entrainement). "
        f"Cette 'accuracy' n'est PAS une mesure fiable : echantillon bien trop petit."
    )

# modele final entraine sur l'ensemble des 5 clients (pour illustrer les coefficients uniquement)
clf_full = LogisticRegression()
clf_full.fit(Xs, y)
proba = clf_full.predict_proba(Xs)[:, 1]
df["Risque_churn_modele"] = (proba * 100).round(1)

coefs = dict(zip(features, clf_full.coef_[0].round(3).tolist()))

out = df[[
    "Customer_ID", "Name", "Age", "Anciennete_j", "Nb_Achats", "Recence_j",
    "Churn_proxy", "Risque_churn_modele", "CLV_historique", "CLV_projetee_12m",
]].copy()
out = out.rename(columns={
    "Customer_ID": "ID", "Name": "Client", "Anciennete_j": "Anciennete (j)",
    "Nb_Achats": "Nb achats", "Recence_j": "Recence (j)",
    "Churn_proxy": "Churn proxy (regle)", "Risque_churn_modele": "Risque churn modele (%)",
})

out.to_csv("churn_clv_results.csv", index=False)

summary = {
    "reference_date": str(REF_DATE.date()),
    "n_clients": int(len(df)),
    "n_churn_proxy_positifs": int(y.sum()),
    "model_coefficients": coefs,
    "model_validation_note": model_note,
    "avertissement": (
        "Le proxy de churn (aucune vente enregistree) est une regle metier faute de "
        "variable de resiliation reelle dans les donnees fournies. Le modele de "
        "regression logistique est entraine sur 5 observations seulement : ses "
        "coefficients et probabilites sont a but illustratif / pedagogique et ne "
        "doivent pas etre utilises pour une decision commerciale reelle sans un "
        "historique beaucoup plus large et un vrai libelle de churn."
    ),
}
with open("churn_clv_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(out.to_string(index=False))
print()
print(json.dumps(summary, ensure_ascii=False, indent=2))

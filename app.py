import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="Analyse & Optimisation Marketing — ENI Fianarantsoa",
    page_icon="📊",
    layout="wide",
)

NAVY = "#1E2761"
CORAL = "#F4623A"
ICE = "#CADCFC"

# =========================================================
# Chargement des donnees
# =========================================================
@st.cache_data
def load_data():
    customers = pd.read_csv("customers_data.csv", parse_dates=["Join_Date"])
    sales = pd.read_csv("sales_data.csv", parse_dates=["Date"])
    products = pd.read_csv("products_data.csv")
    marketing = pd.read_csv("marketing_data.csv", parse_dates=["Start_Date", "End_Date"])
    sales["Revenue"] = sales["Quantity"] * sales["Sale_Price"]
    sales_full = sales.merge(products, on="Product_ID", how="left").merge(
        customers[["Customer_ID", "Name"]], on="Customer_ID", how="left"
    )
    return customers, sales, products, marketing, sales_full


customers, sales, products, marketing, sales_full = load_data()

try:
    churn_clv = pd.read_csv("churn_clv_results.csv")
    with open("churn_clv_summary.json", encoding="utf-8") as f:
        churn_summary = json.load(f)
except FileNotFoundError:
    churn_clv, churn_summary = None, None

# =========================================================
# En-tete
# =========================================================
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown(
        f"<div style='background:{NAVY};border-radius:12px;height:70px;"
        f"display:flex;align-items:center;justify-content:center;'>"
        f"<span style='color:white;font-weight:700;font-size:22px;'>ENI</span></div>",
        unsafe_allow_html=True,
    )
with col_title:
    st.title("Analyse & Optimisation Marketing")
    st.caption("Dashboard interactif — segmentation client, performance des campagnes, churn & CLV — ENI Fianarantsoa")

st.divider()

# =========================================================
# KPI globaux
# =========================================================
total_ca = sales_full["Revenue"].sum()
total_clients = customers.shape[0]
total_budget = marketing["Budget"].sum()
total_conversions = marketing["Conversions"].sum()
ctr_global = marketing["Clicks"].sum() / marketing["Impressions"].sum() * 100
conv_rate = marketing["Conversions"].sum() / marketing["Clicks"].sum() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Chiffre d'affaires", f"{total_ca:,.2f}".replace(",", " "))
k2.metric("Clients", f"{total_clients}")
k3.metric("Budget marketing", f"{total_budget:,.0f}".replace(",", " "))
k4.metric("CTR global", f"{ctr_global:.2f} %")
k5.metric("Taux de conversion", f"{conv_rate:.2f} %")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["🧩 Segmentation", "📣 Campagnes", "🔮 Churn & CLV", "🗂️ Données"]
)

# =========================================================
# Onglet 1 — Segmentation
# =========================================================
with tab1:
    st.subheader("Segmentation client (K-means, 3 groupes)")
    st.caption(
        "Standardisation puis clustering sur l'âge, la dépense totale, le nombre "
        "d'achats, la quantité, le chiffre d'affaires observé et la diversité produits. "
        "⚠️ Échantillon de 5 clients : lecture illustrative, pas un résultat validé statistiquement."
    )

    sales_agg = sales.groupby("Customer_ID").agg(
        Nb_Achats=("Sale_ID", "count"),
        Qte_Totale=("Quantity", "sum"),
        CA_Observe=("Revenue", "sum"),
        Nb_Produits_Diff=("Product_ID", "nunique"),
    ).reset_index()
    seg_df = customers.merge(sales_agg, on="Customer_ID", how="left").fillna(0)

    feats = ["Age", "Total_Spent", "Nb_Achats", "Qte_Totale", "CA_Observe", "Nb_Produits_Diff"]
    X = StandardScaler().fit_transform(seg_df[feats])
    n_clusters = min(3, seg_df.shape[0])
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(X)
    seg_df["cluster"] = km.labels_

    # etiquette lisible par ordre de CA observe moyen du cluster
    order = seg_df.groupby("cluster")["CA_Observe"].mean().sort_values(ascending=False).index
    labels_map = {}
    names = ["Forte valeur", "Intermédiaire", "Faible activité"]
    for i, c in enumerate(order):
        labels_map[c] = names[i] if i < len(names) else f"Segment {i+1}"
    seg_df["Segment"] = seg_df["cluster"].map(labels_map)

    c1, c2 = st.columns([2, 3])
    with c1:
        st.dataframe(
            seg_df[["Name", "Age", "Total_Spent", "Nb_Achats", "CA_Observe", "Segment"]]
            .rename(columns={"Name": "Client", "Total_Spent": "Dépense totale", "Nb_Achats": "Nb achats", "CA_Observe": "CA observé"}),
            hide_index=True, use_container_width=True,
        )
    with c2:
        fig = px.scatter(
            seg_df, x="Total_Spent", y="CA_Observe", color="Segment", text="Name",
            size=[18] * len(seg_df), color_discrete_sequence=[NAVY, "#545F9E", CORAL],
            labels={"Total_Spent": "Dépense totale déclarée", "CA_Observe": "CA observé (ventes)"},
        )
        fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="white")))
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Actions recommandées par segment**")
    reco = {
        "Forte valeur": "Fidélisation, offres premium, cross-sell.",
        "Intermédiaire": "Bundles, recommandations ciblées, relance après achat.",
        "Faible activité": "Retargeting e-mail / réseaux sociaux, offre de retour.",
    }
    cols = st.columns(3)
    for col, seg_name in zip(cols, names):
        with col:
            st.info(f"**{seg_name}**\n\n{reco[seg_name]}")

# =========================================================
# Onglet 2 — Campagnes
# =========================================================
with tab2:
    st.subheader("Performance des campagnes marketing")
    m = marketing.copy()
    m["CTR (%)"] = (m["Clicks"] / m["Impressions"] * 100).round(2)
    m["Taux conversion (%)"] = (m["Conversions"] / m["Clicks"] * 100).round(2)
    m["CPC"] = (m["Budget"] / m["Clicks"]).round(2)
    m["CPA"] = (m["Budget"] / m["Conversions"]).round(2)

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(
            m, x="Channel", y="Taux conversion (%)", color="Channel",
            color_discrete_sequence=[NAVY, "#36407A", "#545F9E", "#7683BE", CORAL],
            text="Taux conversion (%)",
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", height=380,
                            title="Taux de conversion par canal")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.bar(
            m, x="Channel", y="CTR (%)", color="Channel",
            color_discrete_sequence=[NAVY, "#36407A", "#545F9E", "#7683BE", CORAL],
            text="CTR (%)",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white", height=380,
                            title="CTR par canal")
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        m[["Channel", "Budget", "Impressions", "Clicks", "Conversions", "CTR (%)", "Taux conversion (%)", "CPC", "CPA"]],
        hide_index=True, use_container_width=True,
    )
    st.warning(
        "ROI non calculé : les données fournies ne permettent pas de relier une vente à une campagne précise. "
        "Un chiffre de ROI construit sans cette attribution serait trompeur."
    )

# =========================================================
# Onglet 3 — Churn & CLV
# =========================================================
with tab3:
    st.subheader("Prédiction churn / valeur client (CLV)")
    if churn_clv is None:
        st.error("Fichier churn_clv_results.csv introuvable — lancez d'abord churn_clv.py.")
    else:
        st.error(
            "⚠️ **Fiabilité limitée.** Le modèle ci-dessous est entraîné sur **5 clients seulement**, "
            "sans variable réelle de résiliation (le churn est un proxy : « aucune vente enregistrée »). "
            "Les probabilités affichées sont illustratives / pédagogiques et **ne doivent pas servir de base "
            "à une décision commerciale réelle**."
        )
        c1, c2 = st.columns([3, 2])
        with c1:
            st.dataframe(churn_clv, hide_index=True, use_container_width=True)
        with c2:
            fig = px.bar(
                churn_clv.sort_values("Risque churn modele (%)", ascending=True),
                x="Risque churn modele (%)", y="Client", orientation="h",
                color="Risque churn modele (%)", color_continuous_scale=[ICE, CORAL],
            )
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320, coloraxis_showscale=False,
                               title="Risque de churn estimé (modèle exploratoire)")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("**CLV projetée sur 12 mois** (dépense actuelle extrapolée sur l'ancienneté du client)")
        fig2 = px.bar(
            churn_clv.sort_values("CLV_projetee_12m", ascending=True),
            x="CLV_projetee_12m", y="Client", orientation="h", color_discrete_sequence=[NAVY],
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320,
                            title="CLV projetée à 12 mois")
        st.plotly_chart(fig2, use_container_width=True)

        if churn_summary:
            with st.expander("Détails méthodologiques du modèle"):
                st.json(churn_summary)

# =========================================================
# Onglet 4 — Données brutes
# =========================================================
with tab4:
    st.subheader("Données sources")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**Clients**")
        st.dataframe(customers, hide_index=True, use_container_width=True)
        st.markdown("**Produits**")
        st.dataframe(products, hide_index=True, use_container_width=True)
    with d2:
        st.markdown("**Ventes**")
        st.dataframe(sales, hide_index=True, use_container_width=True)
        st.markdown("**Campagnes**")
        st.dataframe(marketing, hide_index=True, use_container_width=True)

st.divider()
st.caption("Projet pédagogique — Analyse & Optimisation Marketing — Université de Fianarantsoa / ENI")

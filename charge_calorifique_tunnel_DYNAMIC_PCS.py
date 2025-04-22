import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calcul de la charge calorifique HRR_STIB", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB V3.1")
st.markdown("""
Ce calculateur vous permet d'estimer l'énergie thermique libérée en cas d'incendie pour différents éléments installés dans un tunnel (câbles, cloisons, revêtements, etc.),
ainsi que de générer une courbe HRR (Heat Release Rate) et d’évaluer la contribution au feu selon la distance d'exposition. Vous pouvez également analyser le risque d'inflammation
en fonction du flux thermique reçu, selon un seuil critique propre au matériau.
""")

# Liste enrichie de matériaux avec seuils critiques
materiaux_info = {
    "Câble PVC": {"pcs": 20, "inflammation": 5, "flux_critique": 20},
    "Câble PE": {"pcs": 40, "inflammation": 4, "flux_critique": 18},
    "Composite (FRP)": {"pcs": 20, "inflammation": 6, "flux_critique": 16},
    "Plastique": {"pcs": 35, "inflammation": 4, "flux_critique": 15},
    "Caoutchouc": {"pcs": 30, "inflammation": 6, "flux_critique": 14},
    "Bois": {"pcs": 17, "inflammation": 8, "flux_critique": 12},
    "Panneau OSB": {"pcs": 18, "inflammation": 7, "flux_critique": 11},
    "Panneau OSB 3": {"pcs": 17, "inflammation": 7, "flux_critique": 11},
    "Plaque Geproc": {"pcs": 0, "inflammation": 0, "flux_critique": 999},
    "Polystyrène": {"pcs": 39, "inflammation": 2, "flux_critique": 10},
    "MDF": {"pcs": 18, "inflammation": 7, "flux_critique": 12},
    "Gyproc RF (rose)": {"pcs": 1, "inflammation": 10, "flux_critique": 999}
}

# Nom du projet
st.subheader("🐷 Nom du projet")
nom_projet = st.text_input("Nom de l'analyse ou du projet", "Projet STIB")
st.markdown(f"**Projet :** {nom_projet}")

st.info("🔽 Vous pouvez maintenant sélectionner les matériaux et entrer les paramètres pour calculer la charge calorifique et générer les courbes.\n\n👉 Continuez ci-dessous.")

# Choix matériau
st.subheader("🔍 Sélection du matériau")
liste_materiaux = ["-- Aucun --"] + list(materiaux_info.keys())
materiau_choisi = st.selectbox("Matériau (pré-remplit les valeurs)", liste_materiaux)

if materiau_choisi != "-- Aucun --":
    infos = materiaux_info[materiau_choisi]
    pcs_defaut = infos["pcs"]
    st.markdown(f"**PCS :** {infos['pcs']} MJ/kg")
    st.markdown(f"**Seuil critique :** {infos['flux_critique']} kW/m²")
    nom_element_defaut = materiau_choisi
else:
    pcs_defaut = 0.0
    nom_element_defaut = "Élément"

# Distance d'exposition
st.subheader("🌡️ Distance par rapport à la source de chaleur")
distance = st.slider("Distance (m)", 0.5, 5.0, 2.0, step=0.5)

if distance <= 1:
    flux = 30
elif distance <= 2:
    flux = 20
elif distance <= 3:
    flux = 12
else:
    flux = 8

st.markdown(f"**Flux thermique estimé :** ~ {flux} kW/m²")

# Évaluation du risque par flux critique
if materiau_choisi != "-- Aucun --":
    seuil = infos["flux_critique"]
    if flux > seuil + 5:
        niveau = "🔴 Risque élevé d'inflammation"
    elif flux > seuil:
        niveau = "🟠 Risque modéré"
    elif flux > seuil - 5:
        niveau = "🟡 Risque faible"
    else:
        niveau = "🟢 Risque négligeable"
    st.markdown(f"**Analyse :** {niveau}")

# Formulaire
st.subheader("🧾 Ajouter un élément")
with st.form("formulaire"):
    nom = st.text_input("Nom de l'élément", nom_element_defaut)
    unite = st.selectbox("Unité", ["m", "m²"])
    qte = st.number_input("Quantité", 0.0, step=1.0)
    masse = st.number_input("Masse (kg/unité)", 0.0, step=0.1)
    pcs = st.number_input("PCS (MJ/kg)", 0.0, step=0.5, value=pcs_defaut)
    ajouter = st.form_submit_button("Ajouter")

    if ajouter and nom:
        st.session_state.setdefault("elements", []).append({
            "Élément": nom,
            "Unité": unite,
            "Quantité": qte,
            "Masse (kg/unité)": masse,
            "PCS (MJ/kg)": pcs
        })

# Résultats
if "elements" in st.session_state and st.session_state["elements"]:
    df = pd.DataFrame(st.session_state["elements"])
    df["Charge calorifique (MJ)"] = df["Quantité"] * df["Masse (kg/unité)"] * df["PCS (MJ/kg)"]
    df["Équiv. essence (L)"] = (df["Charge calorifique (MJ)"] / 34).round(0).astype(int)

    st.subheader("📊 Résultats")
    st.dataframe(df, use_container_width=True)

    total_mj = df["Charge calorifique (MJ)"].sum()
    total_kwh = total_mj / 3.6
    total_l = df["Équiv. essence (L)"].sum()

    st.markdown(f"**Total énergie : {total_mj:.2f} MJ**")
    st.markdown(f"**Soit : {total_kwh:.1f} kWh**")
    st.markdown(f"**Équivalent essence : {total_l} litres**")

    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    st.download_button("📥 Télécharger Excel", output.getvalue(), "charge_calorifique_tunnel.xlsx")

# Message vide
else:
    st.info("Ajoutez un élément pour voir les résultats.")

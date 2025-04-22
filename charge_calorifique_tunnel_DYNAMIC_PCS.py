import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Calcul de charge calorifique HRR_STIB", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB V3.1")

st.markdown("""
Ce calculateur vous permet d'estimer l’énergie thermique libérée en cas d'incendie pour différents éléments installés dans un tunnel (câbles, cloisons, revêtements, etc.),
ainsi que de générer une courbe HRR (Heat Release Rate) et d’évaluer la contribution au feu selon la distance d’exposition.
Vous pouvez également analyser le risque d'inflammation en fonction du flux thermique reçu, selon un seuil critique propre au matériau.
""")

# 🔧 Matériaux et propriétés
materiaux_info = {
    "Câble PVC": {"pcs": 20, "densite": "~1.2 kg/m", "flux_critique": 20},
    "Câble PE": {"pcs": 40, "densite": "~1.0 kg/m", "flux_critique": 18},
    "Composite (FRP)": {"pcs": 20, "densite": "4–10 kg/m²", "flux_critique": 16},
    "Plastique": {"pcs": 35, "densite": "variable", "flux_critique": 15},
    "Caoutchouc": {"pcs": 30, "densite": "variable", "flux_critique": 14},
    "Bois": {"pcs": 17, "densite": "8–15 kg/m²", "flux_critique": 12},
    "Panneau OSB": {"pcs": 18, "densite": "10 kg/m²", "flux_critique": 11},
    "Panneau OSB 3": {"pcs": 17, "densite": "10–12 kg/m²", "flux_critique": 11},
    "Plaque Geproc": {"pcs": 0, "densite": "~10 kg/m²", "flux_critique": 999},
    "Polystyrène": {"pcs": 39, "densite": "10–20 kg/m³", "flux_critique": 10},
    "MDF": {"pcs": 18, "densite": "12–14 kg/m²", "flux_critique": 12},
    "Gyproc RF (rose)": {"pcs": 1, "densite": "~10 kg/m²", "flux_critique": 999}
}

# 🎯 Nom du projet
st.subheader("🧠 Nom du projet")
nom_projet = st.text_input("Nom de l'analyse ou du projet", "")
if nom_projet:
    st.markdown(f"**Projet :** {nom_projet}")
    st.info("⬇️ Vous pouvez maintenant sélectionner les matériaux et entrer les paramètres pour calculer la charge calorifique et générer les courbes.\n\n👉 Continuez ci-dessous.")

    # 🔍 Sélection du matériau
    st.subheader("🔎 Sélection du matériau")
    materiaux = ["-- Aucun --"] + list(materiaux_info.keys())
    selected_material = st.selectbox("Matériau (avec données par défaut)", materiaux)

    if selected_material != "-- Aucun --":
        mat_data = materiaux_info[selected_material]
        pcs_default = float(mat_data["pcs"])
        flux_crit = mat_data["flux_critique"]
        st.markdown(f"**PCS :** {pcs_default} MJ/kg  \n**Flux critique :** {flux_crit} kW/m²")

        # 🌡️ Distance
        st.subheader("🌡️ Distance par rapport à la source de chaleur")
        distance_m = st.slider("Distance estimée (m)", 0.5, 5.0, 2.0, step=0.5)
        if distance_m <= 1:
            flux = 30
        elif distance_m <= 2:
            flux = 20
        elif distance_m <= 3:
            flux = 12
        else:
            flux = 8
        st.markdown(f"**Flux thermique estimé :** ~ {flux} kW/m²")

        # 🟢🟡🟠🔴 Risque basé sur le flux critique
        if flux >= flux_crit + 10:
            st.markdown("**Analyse :** 🔴 Risque élevé d'inflammation")
        elif flux >= flux_crit + 2:
            st.markdown("**Analyse :** 🟠 Risque modéré")
        elif flux >= flux_crit:
            st.markdown("**Analyse :** 🟡 Risque faible")
        else:
            st.markdown("**Analyse :** 🟢 Risque négligeable")

        # 🧾 Ajouter un élément
        st.subheader("🧾 Ajouter un élément")
        with st.form("add_form"):
            element = st.text_input("Nom de l'élément", selected_material)
            unite = st.selectbox("Unité", ["m", "m²"])
            quantite = st.number_input("Quantité", min_value=0.0, step=1.0)
            masse = st.number_input("Masse linéaire/surfacique (kg/unité)", min_value=0.0, step=0.1)
            pcs = st.number_input("PCS (MJ/kg)", min_value=0.0, step=0.5, value=float(pcs_default))
            submit = st.form_submit_button("Ajouter")

            if submit and element:
                st.session_state.setdefault("elements", []).append({
                    "Élément": element,
                    "Unité": unite,
                    "Quantité": quantite,
                    "Masse (kg/unité)": masse,
                    "PCS (MJ/kg)": pcs
                })

        # Résultats
        if "elements" in st.session_state and st.session_state["elements"]:
            df = pd.DataFrame(st.session_state["elements"])
            df["Charge calorifique (MJ)"] = df["Quantité"] * df["Masse (kg/unité)"] * df["PCS (MJ/kg)"]
            df["kWh"] = df["Charge calorifique (MJ)"] / 3.6
            df["Équiv. essence (L)"] = (df["Charge calorifique (MJ)"] / 34).round(0).astype(int)

            st.subheader("📊 Résultats")
            st.dataframe(df, use_container_width=True)

            total_mj = df["Charge calorifique (MJ)"].sum()
            total_kwh = df["kWh"].sum()
            total_l = df["Équiv. essence (L)"].sum()
            st.markdown(f"**Total énergie : {total_mj:.2f} MJ**")
            st.markdown(f"**Soit : {total_kwh:.1f} kWh**")
            st.markdown(f"**Équivalent essence : {total_l} litres**")

            output = BytesIO()
            df.to_excel(output, index=False, engine="openpyxl")
            st.download_button("📥 Télécharger Excel", output.getvalue(), "charge_calorifique_tunnel.xlsx")

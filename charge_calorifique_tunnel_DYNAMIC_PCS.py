import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Calcul de charge calorifique HRR_STIB", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB – V4.1 avec HRR cumulative")

# === Base de données des matériaux ===
materiaux_info = {
    "Câble PVC": {"pcs": 20, "densite": "~1.2 kg/m", "combustion": "4–6 min", "hrr": "300–500 kW", "inflammation": 5, "flux_critique": 20},
    "Câble PE": {"pcs": 40, "densite": "~1.0 kg/m", "combustion": "4–8 min", "hrr": "400–800 kW", "inflammation": 4, "flux_critique": 18},
    "Composite (FRP)": {"pcs": 20, "densite": "4–10 kg/m²", "combustion": "10–20 min", "hrr": "600–1000 kW", "inflammation": 6, "flux_critique": 16},
    "Plastique": {"pcs": 35, "densite": "variable", "combustion": "5–10 min", "hrr": "500–900 kW", "inflammation": 4, "flux_critique": 15},
    "Caoutchouc": {"pcs": 30, "densite": "variable", "combustion": "10–15 min", "hrr": "500–700 kW", "inflammation": 6, "flux_critique": 14},
    "Bois": {"pcs": 17, "densite": "8–15 kg/m²", "combustion": "20–30 min", "hrr": "300–500 kW/m²", "inflammation": 8, "flux_critique": 12},
    "Panneau OSB": {"pcs": 18, "densite": "10 kg/m²", "combustion": "15–25 min", "hrr": "250–400 kW/m²", "inflammation": 7, "flux_critique": 11},
    "Panneau OSB 3": {"pcs": 17, "densite": "10–12 kg/m²", "combustion": "15–25 min", "hrr": "300–450 kW/m²", "inflammation": 7, "flux_critique": 11},
    "Plaque Geproc": {"pcs": 0, "densite": "~10 kg/m²", "combustion": "Non combustible", "hrr": "≈0", "inflammation": 0, "flux_critique": 999},
    "Polystyrène": {"pcs": 39, "densite": "10–20 kg/m³", "combustion": "3–6 min", "hrr": ">1000 kW/m²", "inflammation": 2, "flux_critique": 10},
    "MDF": {"pcs": 18, "densite": "12–14 kg/m²", "combustion": "15–25 min", "hrr": "300–400 kW", "inflammation": 7, "flux_critique": 12},
    "Gyproc RF (rose)": {"pcs": 0.1, "densite": "~10 kg/m²", "combustion": "Très résistant", "hrr": "≈0", "inflammation": 10, "flux_critique": 999},
    "Feu de rame": {"pcs": 25, "densite": "N/A", "combustion": "20–30 min", "hrr": "5–15 MW", "inflammation": 8, "flux_critique": 15},
}

# === Sélection du matériau ===
st.subheader("🔍 Sélection du matériau")
material_list = ["-- Aucun --"] + list(materiaux_info.keys())
selected_material = st.selectbox("Matériau (avec données par défaut)", material_list)

if selected_material != "-- Aucun --":
    info = materiaux_info[selected_material]
    st.markdown(f"**PCS :** {info['pcs']} MJ/kg")
    st.markdown(f"**Densité type :** {info['densite']}")
    st.markdown(f"**Durée de combustion typique :** {info['combustion']}")
    st.markdown(f"**HRR max estimé :** {info['hrr']}")
    default_pcs = info['pcs']
    default_element_name = selected_material
else:
    default_pcs = 0.0
    default_element_name = "Câble électrique"

# === Distance et analyse d'inflammation ===
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

# Analyse de risque
if selected_material != "-- Aucun --":
    seuil = info["flux_critique"]
    if flux >= seuil + 5:
        commentaire = "🔴 Risque élevé d'inflammation"
    elif flux >= seuil:
        commentaire = "🟠 Risque modéré"
    elif flux >= seuil - 5:
        commentaire = "🟡 Risque faible"
    else:
        commentaire = "🟢 Risque négligeable"

    st.markdown(f"**Analyse :** {commentaire}")

# === Ajout d’éléments ===
st.subheader("🧾 Ajouter un élément")
with st.form("element_form"):
    element = st.text_input("Nom de l'élément", default_element_name)
    unite = st.selectbox("Unité", ["m", "m²"])
    quantite = st.number_input("Quantité", min_value=0.0, step=1.0)
    masse = st.number_input("Masse linéaire/surfacique (kg/unité)", min_value=0.0, step=0.1)
    pcs = st.number_input("PCS (MJ/kg)", min_value=0.0, step=0.5, value=float(default_pcs))
    submit = st.form_submit_button("Ajouter")

    if submit and element:
        st.session_state.setdefault("elements", []).append({
            "Élément": element,
            "Unité": unite,
            "Quantité": quantite,
            "Masse (kg/unité)": masse,
            "PCS (MJ/kg)": pcs
        })

# === Résultats ===
if "elements" in st.session_state and st.session_state["elements"]:
    df = pd.DataFrame(st.session_state["elements"])
    df["Charge calorifique (MJ)"] = df["Quantité"] * df["Masse (kg/unité)"] * df["PCS (MJ/kg)"]
    df["Équiv. essence (L)"] = (df["Charge calorifique (MJ)"] / 34).round(0).astype(int)

    st.subheader("📊 Résultats")
    st.dataframe(df, use_container_width=True)

    total_mj = df["Charge calorifique (MJ)"].sum()
    total_l = df["Équiv. essence (L)"].sum()
    st.markdown(f"**Total énergie : {total_mj:.2f} MJ**")
    st.markdown(f"**Équivalent essence : {total_l} litres**")

# === Courbe HRR cumulative ===
st.subheader("📈 HRR cumulative – OSB & Feu de rame")
duree_totale = 1200
t = np.linspace(0, duree_totale, 800)

def hrr_osb(t):
    alpha_osb = 0.047
    t_peak = np.sqrt(10000 / alpha_osb)
    hrr = np.where(t < t_peak, alpha_osb * t**2, 10000)
    hrr = np.where(t > t_peak + 300, np.clip(10000 * (1 - (t - t_peak - 300)/300), 0, 10000), hrr)
    return hrr

def hrr_rame(t):
    alpha_rame = 0.012
    t_peak = np.sqrt(7000 / alpha_rame)
    hrr = np.where(t < t_peak, alpha_rame * t**2, 7000)
    hrr = np.where(t > t_peak + 400, np.clip(7000 * (1 - (t - t_peak - 400)/400), 0, 7000), hrr)
    return hrr

osb_active = st.checkbox("Intégrer panneau OSB (100 m²)", value=True)
r

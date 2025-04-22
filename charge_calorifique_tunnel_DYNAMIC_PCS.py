import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calcul de charge calorifique HRR_STIB", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB V1")
st.markdown("""
Ce calculateur vous permet d'estimer l'énergie thermique libérée en cas d'incendie pour différents éléments installés dans un tunnel (câbles, cloisons, revêtements, etc.),
ainsi que de générer une courbe HRR (Heat Release Rate) et d'évaluer la contribution au feu selon la distance d'exposition.
""")

# Liste enrichie de matériaux avec données
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
    "Gyproc RF (rose)": {"pcs": 1, "densite": "~10 kg/m²", "combustion": "Très résistant", "hrr": "≈0", "inflammation": 10, "flux_critique": 999}
}

# Sélection du matériau
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

# Distance et flux thermique
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

flux_txt = f"Flux estimé ≈ {flux} kW/m²"
st.markdown(f"**{flux_txt}**")

# Risque d’inflammation + jauge visuelle
if selected_material != "-- Aucun --":
    flux_crit = info['flux_critique']
    if flux >= flux_crit:
        risque = "🔴 Élevé"
        niveau = 3
    elif flux >= flux_crit * 0.8:
        risque = "🟠 Modéré"
        niveau = 2
    elif flux >= flux_crit * 0.5:
        risque = "🟡 Faible"
        niveau = 1
    else:
        risque = "🟢 Négligeable"
        niveau = 0

    st.markdown(f"**🧯 Risque d'inflammation :** {risque} (seuil critique ≈ {flux_crit} kW/m²)")
    st.progress((niveau + 1) * 25 if niveau < 4 else 100)

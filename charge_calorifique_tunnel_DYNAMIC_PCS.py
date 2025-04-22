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
    "Câble PVC": {"pcs": 20, "densite": "~1.2 kg/m", "combustion": "4–6 min", "hrr": "300–500 kW", "inflammation": 5},
    "Câble PE": {"pcs": 40, "densite": "~1.0 kg/m", "combustion": "4–8 min", "hrr": "400–800 kW", "inflammation": 4},
    "Composite (FRP)": {"pcs": 20, "densite": "4–10 kg/m²", "combustion": "10–20 min", "hrr": "600–1000 kW", "inflammation": 6},
    "Plastique": {"pcs": 35, "densite": "variable", "combustion": "5–10 min", "hrr": "500–900 kW", "inflammation": 4},
    "Caoutchouc": {"pcs": 30, "densite": "variable", "combustion": "10–15 min", "hrr": "500–700 kW", "inflammation": 6},
    "Bois": {"pcs": 17, "densite": "8–15 kg/m²", "combustion": "20–30 min", "hrr": "300–500 kW/m²", "inflammation": 8},
    "Panneau OSB": {"pcs": 18, "densite": "10 kg/m²", "combustion": "15–25 min", "hrr": "250–400 kW/m²", "inflammation": 7},
    "Panneau OSB 3": {"pcs": 17, "densite": "10–12 kg/m²", "combustion": "15–25 min", "hrr": "300–450 kW/m²", "inflammation": 7},
    "Plaque Geproc": {"pcs": 0, "densite": "~10 kg/m²", "combustion": "Non combustible", "hrr": "≈0", "inflammation": 0},
    "Polystyrène": {"pcs": 39, "densite": "10–20 kg/m³", "combustion": "3–6 min", "hrr": ">1000 kW/m²", "inflammation": 2},
    "MDF": {"pcs": 18, "densite": "12–14 kg/m²", "combustion": "15–25 min", "hrr": "300–400 kW", "inflammation": 7},
    "Gyproc RF (rose)": {"pcs": 1, "densite": "~10 kg/m²", "combustion": "Très résistant", "hrr": "≈0", "inflammation": 10}
}

# Sélection du matériau
st.subheader("🔍 Sélection du matériau")
material_list = ["-- Aucun --"] + list(materiaux_info.keys())
selected_material = st.selectbox("Matériau (avec données par défaut)", material_list)

if selected_material != "-- Aucun --":
    info = materiaux_info[selected_material]
    st.markdown(f"**PCS :** {info['pcs']} MJ/kg  ")
    st.markdown(f"**Densité type :** {info['densite']}  ")
    st.markdown(f"**Durée de combustion typique :** {info['combustion']}  ")
    st.markdown(f"**HRR max estimé :** {info['hrr']}")
    default_pcs = info['pcs']
    default_element_name = selected_material
else:
    default_pcs = 0.0
    default_element_name = "Câble électrique"

# Choix de la distance d’exposition
st.subheader("🌡️ Distance par rapport à la source de chaleur")
distance_m = st.slider("Distance estimée par rapport à la source de feu (m)", 0.5, 5.0, 2.0, step=0.5)

if distance_m <= 1:
    flux = 30
    flux_txt = "> 25 kW/m² (inflammation très probable)"
elif distance_m <= 2:
    flux = 20
    flux_txt = "15–25 kW/m² (inflammation probable après quelques minutes)"
elif distance_m <= 3:
    flux = 12
    flux_txt = "10–15 kW/m² (inflammation possible à long terme)"
else:
    flux = 8
    flux_txt = "< 10 kW/m² (peu de probabilité d’inflammation)"

st.markdown(f"**Flux thermique estimé à {distance_m} m :** {flux_txt}")

# Évaluation du risque d'inflammation (simple modèle basé sur flux et matériau)
if selected_material != "-- Aucun --":
    sensib = info['inflammation']
    score = round(flux * (10 - sensib) / 10)
    if score >= 20:
        commentaire = "🔥 Risque d'inflammation élevé (court terme)"
    elif score >= 10:
        commentaire = "⚠️ Risque d'inflammation modéré"
    elif score > 0:
        commentaire = "🟡 Risque faible mais présent"
    else:
        commentaire = "✅ Risque négligeable ou matériau incombustible"
    st.markdown(f"**Analyse d'inflammation :** {commentaire}")

# Formulaire d'ajout
st.subheader("🧾 Ajouter un élément")
with st.form("element_form"):
    element = st.text_input("Nom de l'élément", default_element_name)
    unite = st.selectbox("Unité de mesure", ["m", "m²"])
    quantite = st.number_input("Quantité (longueur ou surface)", min_value=0.0, step=1.0)
    masse = st.number_input("Masse linéaire ou surfacique (kg/unité)", min_value=0.0, step=0.1)
    pcs = st.number_input("Pouvoir calorifique supérieur (MJ/kg)", min_value=0.0, step=0.5, value=float(default_pcs))
    submit = st.form_submit_button("Ajouter")

    if submit and element:
        st.session_state.setdefault("elements", []).append({
            "Élément": element,
            "Unité de mesure": unite,
            "Quantité": quantite,
            "Masse (kg/unité)": masse,
            "PCS (MJ/kg)": pcs
        })

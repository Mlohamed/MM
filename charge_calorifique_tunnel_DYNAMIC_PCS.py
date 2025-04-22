import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calcul de charge calorifique HRR_STIB", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB V2")
st.markdown("""
Ce calculateur vous permet d'estimer l'énergie thermique libérée en cas d'incendie pour différents éléments installés dans un tunnel (câbles, cloisons, revêtements, etc.),
aussi que de générer une courbe HRR (Heat Release Rate) et d'évaluer la contribution au feu selon la distance d'exposition.
Vous pouvez également analyser le risque d'inflammation en fonction du flux thermique reçu et simuler une montée en puissance du feu selon plusieurs profils.
""")

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

st.subheader("👤 Informations utilisateur (facultatif)")
nom_utilisateur = st.text_input("Votre nom ou projet", "")
if nom_utilisateur:
    st.markdown(f"**Projet :** {nom_utilisateur}")

st.markdown("---")
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

# Choix du profil alpha et durée pour courbe HRR
st.subheader("📈 Simulation HRR (Heat Release Rate)")
alpha_choice = st.selectbox("Profil de croissance du feu (α)", ["Lent (0.00293)", "Moyen (0.0117)", "Rapide (0.0469)", "Ultra rapide (0.1876)"])
duree_feu = st.slider("Durée du feu pour la courbe HRR (min)", 5, 30, 10)

d_alpha = {
    "Lent (0.00293)": 0.00293,
    "Moyen (0.0117)": 0.0117,
    "Rapide (0.0469)": 0.0469,
    "Ultra rapide (0.1876)": 0.1876
}

alpha_val = d_alpha[alpha_choice]

time_s = np.arange(0, duree_feu * 60 + 1, 1)
hrr_curve = alpha_val * time_s**2

st.line_chart(pd.DataFrame({"HRR (kW)": hrr_curve}, index=time_s))

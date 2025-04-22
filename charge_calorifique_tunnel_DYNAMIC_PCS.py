import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calcul de charge calorifique HRR_STIB", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB V22")
st.markdown("""
Ce calculateur vous permet d'estimer l'énergie thermique libérée en cas d'incendie pour différents éléments installés dans un tunnel (câbles, cloisons, revêtements, etc.),
aussi que de générer une courbe HRR (Heat Release Rate) et d’évaluer la contribution au feu selon la distance d’exposition.
Vous pouvez également analyser le risque d'inflammation en fonction du flux thermique reçu, et nommer votre projet pour les exports.
""")

# Sidebar - Lien vers documentation ou fiche
st.sidebar.header("🔎 Aide et infos")
st.sidebar.markdown("- [Documentation PCS & HRR (PDF)](https://www.example.com)")
st.sidebar.markdown("- [Références ISO / NFPA](https://www.nfpa.org)")

# Champs pour le nom de projet
st.subheader("🎯 Nom du projet")
nom_projet = st.text_input("Nom de l'analyse ou du projet", "")
if nom_projet:
    st.markdown(f"**Projet :** {nom_projet}")
    st.info("\U0001F4C4 Vous pouvez maintenant sélectionner les matériaux et entrer les paramètres pour calculer la charge calorifique et générer les courbes.\n\n👉 Continuez ci-dessous.")

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

# --- Interface suivante ici ---
# Placez le reste de l'application (sélection matériaux, formulaire, calculs, graphique, etc.) à la suite

st.subheader("🔍 Sélection du matériau")
material_list = ["-- Aucun --"] + list(materiaux_info.keys())
selected_material = st.selectbox("Matériau (avec données par défaut)", material_list)

if selected_material != "-- Aucun --":
    info = materiaux_info[selected_material]
    st.markdown(f"**PCS :** {info['pcs']} MJ/kg")
    st.markdown(f"**Densité type :** {info['densite']}")
    st.markdown(f"**Durée de combustion typique :** {info['combustion']}")
    st.markdown(f"**HRR max estimé :** {info['hrr']}")

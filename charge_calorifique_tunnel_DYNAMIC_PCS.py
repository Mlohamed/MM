import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calcul de charge calorifique HRR_STIB", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB V2")
st.markdown("""
Ce calculateur vous permet d'estimer l'énergie thermique libérée en cas d'incendie pour différents éléments installés dans un tunnel (câbles, cloisons, revêtements, etc.),
ainsi que de générer une courbe HRR (Heat Release Rate) et d'évaluer la contribution au feu selon la distance d'exposition.
Vous pouvez également analyser le risque d'inflammation en fonction du flux thermique reçu et simuler une montée en puissance du feu selon plusieurs profils.
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

# Sidebar - Lien vers documentation ou fiche
st.sidebar.header("🔎 Aide et infos")
st.sidebar.markdown("- [Documentation PCS & HRR (PDF)](https://www.example.com)")
st.sidebar.markdown("- [Références ISO / NFPA](https://www.nfpa.org)")

# Introduction de l'utilisateur
st.subheader("👤 Informations utilisateur (facultatif)")
nom_utilisateur = st.text_input("Votre nom ou projet", "")

if nom_utilisateur:
    st.markdown(f"**Projet :** {nom_utilisateur}")
else:
    st.markdown("**Projet :** _(non spécifié)_")

# Suite à développer : sélection matériau, distance, jauge de risque, calculs, courbes, etc.
```

# Tu peux maintenant afficher dynamiquement le nom du projet dans l'application.
Souhaites-tu que ce nom soit également ajouté dans l'en-tête du fichier Excel ou sur les graphes HRR ?

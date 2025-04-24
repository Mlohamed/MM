import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from io import BytesIO
import os

st.set_page_config(page_title="🔥 Calcul de la charge calorifique HRR_STIB", layout="centered")
st.title("🔥 Calcul de la charge calorifique HRR_STIB – V3.2")

# Matériaux simplifiés (exemple)
materiaux_info = {
    "Câble PVC": 20,
    "Bois": 17,
    "Polystyrène": 39,
    "MDF": 18,
    "Panneau OSB": 17
}

# Sélection et ajout
selected_material = st.selectbox("Matériau", list(materiaux_info.keys()))
pcs = materiaux_info[selected_material]
quantite = st.number_input("Quantité", min_value=0.0, step=1.0)
masse = st.number_input("Masse (kg/unité)", min_value=0.0, step=0.1)
unite = st.selectbox("Unité", ["m", "m²"])
if st.button("Ajouter"):
    st.session_state.setdefault("elements", []).append({
        "Élément": selected_material,
        "Unité": unite,
        "Quantité": quantite,
        "Masse (kg/unité)": masse,
        "PCS (MJ/kg)": pcs
    })

# Affichage tableau
if "elements" in st.session_state and st.session_state["elements"]:
    df = pd.DataFrame(st.session_state["elements"])
    df["Charge calorifique (MJ)"] = df["Quantité"] * df["Masse (kg/unité)"] * df["PCS (MJ/kg)"]
    df["Équiv. essence (L)"] = (df["Charge calorifique (MJ)"] / 34).round(0).astype(int)

    total_mj = df["Charge calorifique (MJ)"].sum()
    total_kwh = total_mj / 3.6
    total_l = df["Équiv. essence (L)"].sum()

    st.dataframe

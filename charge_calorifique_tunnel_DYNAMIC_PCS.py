import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Calcul de la charge calorifique HRR_STIB V3.2", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB – V3.2")

# Matériaux avec PCS par défaut
materiaux_info = {
    "Câble PVC": 20,
    "Câble PE": 40,
    "Composite (FRP)": 20,
    "Plastique": 35,
    "Caoutchouc": 30,
    "Bois": 17,
    "Panneau OSB": 18,
    "Panneau OSB 3": 17,
    "Plaque Geproc": 0,
    "Polystyrène": 39,
    "MDF": 18,
    "Gyproc RF (rose)": 1
}

# Interface utilisateur
st.subheader("📋 Ajouter un élément")
col1, col2 = st.columns(2)
with col1:
    selected_material = st.selectbox("Matériau", list(materiaux_info.keys()))
    quantite = st.number_input("Quantité", min_value=0.0, step=1.0)
with col2:
    masse = st.number_input("Masse (kg/unité)", min_value=0.0, step=0.1)
    unite = st.selectbox("Unité", ["m", "m²"])

pcs_defaut = materiaux_info[selected_material]
pcs = st.number_input("PCS (MJ/kg)", min_value=0.0, step=0.5, value=float(pcs_defaut))

if st.button("Ajouter"):
    st.session_state.setdefault("elements", []).append({
        "Élément": selected_material,
        "Unité": unite,
        "Quantité": quantite,
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

    st.markdown(f"**🔺 Total énergie : {total_mj:.2f} MJ**")
    st.markdown(f"**⚡ Soit : {total_kwh:.1f} kWh**")
    st.markdown(f"**⛽ Équivalent essence : {total_l} litres**")

    output_excel = BytesIO()
    df.to_excel(output_excel, index=False, engine='openpyxl')
    st.download_button("📥 Télécharger Excel", output_excel.getvalue(), file_name="charge_calorifique_tunnel.xlsx")

    # Génération PDF automatique
    st.subheader("📄 Générer une fiche technique (PDF)")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title("Fiche technique - Charge calorifique")

    pdf.cell(200, 10, txt="Fiche technique - Charge calorifique", ln=True, align='C')
    pdf.ln(10)

    for index, row in df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Élément']} – {row['Quantité']} {row['Unité']} – {row['Masse (kg/unité)']} kg/unité – {row['PCS (MJ/kg)']} MJ/kg", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Total énergie : {total_mj:.2f} MJ", ln=True)
    pdf.cell(200, 10, txt=f"Équivalent essence : {total_l} litres", ln=True)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    st.download_button("📄 Télécharger PDF", data=pdf_output.getvalue(), file_name="fiche_technique_charge_calorifique.pdf")


import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Calcul de charge calorifique", layout="centered")

st.title("🔥 Calcul de la charge calorifique en tunnel")
st.markdown("""
Ce calculateur vous permet d'estimer l'énergie thermique libérée en cas d'incendie pour différents éléments installés dans un tunnel (câbles, couvercles FRP, etc.).
""")

# Liste de matériaux avec PCS par défaut (MJ/kg)
pcs_reference = {
    "Câble PVC": 20,
    "Câble PE": 40,
    "Câble XLPE": 38,
    "Composite (FRP)": 20,
    "Plastique": 35,
    "Caoutchouc": 30,
    "Bois": 17
}

# Formulaire de saisie
elements = []
st.subheader("Ajouter un élément")

with st.form("element_form"):
    element = st.text_input("Nom de l'élément", "Câble électrique")
    unite = st.selectbox("Unité de mesure", ["m", "m²"])
    quantite = st.number_input("Quantité (longueur ou surface)", min_value=0.0, step=1.0)
    masse = st.number_input("Masse linéaire ou surfacique (kg/unité)", min_value=0.0, step=0.1)
    
    pcs_material = st.selectbox("Matériau (pour PCS par défaut)", ["-- Aucun --"] + list(pcs_reference.keys()))
    default_pcs = pcs_reference.get(pcs_material, 0.0)
    
    if pcs_material != "-- Aucun --":
        st.markdown(f"**🔎 PCS proposé pour ce matériau : `{default_pcs} MJ/kg`**")

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

# Affichage des résultats
if "elements" in st.session_state and st.session_state["elements"]:
    df = pd.DataFrame(st.session_state["elements"])
    df["Charge calorifique (MJ)"] = df["Quantité"] * df["Masse (kg/unité)"] * df["PCS (MJ/kg)"]
    df["Équiv. litres essence"] = (df["Charge calorifique (MJ)"] / 34).round(0).astype(int)

    st.subheader("🧮 Résultat")
    st.dataframe(df, use_container_width=True)

    total_mj = df["Charge calorifique (MJ)"].sum()
    total_l = df["Équiv. litres essence"].sum()

    st.markdown(f"**➡️ Charge calorifique totale : {total_mj:.2f} MJ**")
    st.markdown(f"**➡️ Équivalent essence : {total_l} litres**")

    # Téléchargement Excel
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Télécharger le tableau en Excel",
        data=processed_data,
        file_name="charge_calorifique_tunnel.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Ajoutez au moins un élément pour afficher les résultats.")

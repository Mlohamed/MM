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

# Matériaux de référence
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

# Sidebar
st.sidebar.header("🔎 Aide et infos")
st.sidebar.markdown("- [Documentation PCS & HRR (PDF)](https://www.example.com)")
st.sidebar.markdown("- [Références ISO / NFPA](https://www.nfpa.org)")

# Nom du projet
st.subheader("👤 Informations utilisateur (facultatif)")
nom_projet = st.text_input("Votre nom ou projet", "")
if nom_projet:
    st.markdown(f"**Projet :** {nom_projet}")

# Sélection matériau
st.markdown("---")
st.subheader("🔍 Sélection du matériau")
material_list = ["-- Aucun --"] + list(materiaux_info.keys())
selected_material = st.selectbox("Matériau (avec PCS par défaut)", material_list)

if selected_material != "-- Aucun --":
    info = materiaux_info[selected_material]
    default_pcs = info['pcs']
    st.markdown(f"**PCS :** {info['pcs']} MJ/kg")
    st.markdown(f"**HRR estimé :** {info['hrr']}")
    st.markdown(f"**Densité :** {info['densite']}")
else:
    default_pcs = 0

# Formulaire
st.subheader("🧾 Ajouter un élément")
with st.form("formulaire"):
    element = st.text_input("Nom de l'élément", selected_material if selected_material != "-- Aucun --" else "")
    unite = st.selectbox("Unité de mesure", ["m", "m²"])
    quantite = st.number_input("Quantité (longueur ou surface)", min_value=0.0, step=1.0)
    masse = st.number_input("Masse linéaire ou surfacique (kg/unité)", min_value=0.0, step=0.1)
    pcs = st.number_input("Pouvoir calorifique supérieur (MJ/kg)", min_value=0.0, value=float(default_pcs), step=0.5)
    submit = st.form_submit_button("Ajouter")

    if submit and element:
        st.session_state.setdefault("elements", []).append({
            "Élément": element,
            "Unité": unite,
            "Quantité": quantite,
            "Masse (kg/unité)": masse,
            "PCS (MJ/kg)": pcs
        })

# Affichage des résultats
if "elements" in st.session_state and st.session_state["elements"]:
    df = pd.DataFrame(st.session_state["elements"])
    df["Charge calorifique (MJ)"] = df["Quantité"] * df["Masse (kg/unité)"] * df["PCS (MJ/kg)"]
    st.subheader("📊 Résultat")
    st.dataframe(df)

    total_mj = df["Charge calorifique (MJ)"].sum()
    equivalent_essence = int(total_mj / 34)
    st.markdown(f"**🔹 Charge calorifique totale : {total_mj:.2f} MJ**")
    st.markdown(f"**🔹 Équivalent essence : {equivalent_essence} litres**")

    # Sélection du profil alpha
    st.subheader("🔥 Génération de la courbe HRR (Quadratique)")
    alpha_option = st.selectbox("Profil de feu (vitesse de croissance)", ["Lent (α = 0.00293)", "Moyen (α = 0.012)", "Rapide (α = 0.0469)", "Ultra-rapide (α = 0.1876)"])
    alpha_val = float(alpha_option.split("=")[-1].replace(")", "").strip())

    duree = st.slider("Durée du feu pour la courbe HRR (minutes)", 5, 30, 10)
    duree_sec = duree * 60
    t = np.linspace(0, duree_sec, 300)
    hrr = alpha_val * t**2
    hrr = np.minimum(hrr, total_mj * 1000 / duree_sec)  # limitation par énergie totale

    fig, ax = plt.subplots()
    ax.plot(t/60, hrr / 1000, label=f"Courbe HRR (α = {alpha_val})")
    ax.set_xlabel("Temps (min)")
    ax.set_ylabel("HRR (MW)")
    ax.set_title("Courbe de puissance calorifique libérée")
    ax.legend()
    st.pyplot(fig)

    # Export Excel
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    st.download_button("📥 Télécharger les résultats Excel", data=output.getvalue(), file_name="resultats_calorifique.xlsx")

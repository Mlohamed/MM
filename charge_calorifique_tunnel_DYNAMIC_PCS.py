import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calcul de charge calorifique HRR_STIB V3.3", layout="centered")

st.title("🔥 Calcul de la charge calorifique HRR_STIB – V3.4")

# === Base de données des matériaux ===
materiaux_info = {
    "Câble PVC": {"pcs": 20, "inflammation": 5},
    "Câble PE": {"pcs": 40, "inflammation": 4},
    "Composite (FRP)": {"pcs": 20, "inflammation": 6},
    "Plastique": {"pcs": 35, "inflammation": 4},
    "Caoutchouc": {"pcs": 30, "inflammation": 6},
    "Bois": {"pcs": 17, "inflammation": 8},
    "Panneau OSB": {"pcs": 18, "inflammation": 7},
    "Panneau OSB 3": {"pcs": 17, "inflammation": 7},
    "Plaque Geproc": {"pcs": 0, "inflammation": 0},
    "Polystyrène": {"pcs": 39, "inflammation": 2},
    "MDF": {"pcs": 18, "inflammation": 7},
    "Gyproc RF (rose)": {"pcs": 1, "inflammation": 10}
}

# === Sélection du matériau ===
st.subheader("🔍 Sélection du matériau")
material_list = ["-- Aucun --"] + list(materiaux_info.keys())
selected_material = st.selectbox("Matériau (avec données par défaut)", material_list)

if selected_material != "-- Aucun --":
    default_pcs = materiaux_info[selected_material]["pcs"]
    default_element_name = selected_material
else:
    default_pcs = 0.0
    default_element_name = "Câble électrique"

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

    # === Courbe HRR multi-matériaux cumulée ===
    st.subheader("📈 Courbe HRR cumulée par matériau")
    duree_totale = st.selectbox("Durée de feu", [600, 1200, 1800], format_func=lambda x: f"{x//60} minutes")
    alpha_choice = st.radio("Vitesse de croissance du feu", [
        "Lente (α = 0.004 kW/s²)",
        "Moyenne (α = 0.012 kW/s²)",
        "Rapide (α = 0.047 kW/s²)",
        "Ultra-rapide (α = 0.105 kW/s²)"
    ])
    alpha_dict = {
        "Lente (α = 0.004 kW/s²)": 0.004,
        "Moyenne (α = 0.012 kW/s²)": 0.012,
        "Rapide (α = 0.047 kW/s²)": 0.047,
        "Ultra-rapide (α = 0.105 kW/s²)": 0.105
    }
    alpha = alpha_dict[alpha_choice]

    t_monte = duree_totale // 3
    t_plateau = duree_totale // 3
    t_descente = duree_totale // 3

    t1 = np.linspace(0, t_monte, 200)
    t2 = np.linspace(t_monte, t_monte + t_plateau, 200)
    t3 = np.linspace(t_monte + t_plateau, duree_totale, 200)
    t_total = np.concatenate([t1, t2, t3])

    fig, ax = plt.subplots(figsize=(10, 5))
    hrr_cumule = np.zeros_like(t_total)

    for _, row in df.iterrows():
        energie = row["Charge calorifique (MJ)"] * 1000  # MJ → kJ
        hrr_monte = alpha * t1**2
        HRRmax = hrr_monte[-1]
        hrr_plateau = np.ones_like(t2) * HRRmax
        hrr_descente = np.linspace(HRRmax, 0, len(t3))
        hrr_total = np.concatenate([hrr_monte, hrr_plateau, hrr_descente])
        facteur = energie / np.trapz(hrr_total, t_total)
        hrr_total *= facteur
        hrr_cumule += hrr_total
        ax.plot(t_total, hrr_total / 1000, label=row["Élément"])  # en MW

    ax.plot(t_total, hrr_cumule / 1000, label="Total", color="black", linewidth=2, linestyle="--")
    ax.set_xlabel("Temps (s)")
    ax.set_ylabel("HRR (MW)")
    ax.set_title("HRR cumulée multi-matériaux")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

else:
    st.info("Ajoutez au moins un élément pour afficher les résultats.")

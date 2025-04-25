import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Calcul de la charge calorifique HRR_STIB V4.0", layout="centered")
st.title("🔥 Calcul de la charge calorifique HRR_STIB – V4.0")

st.markdown("""
Ce calculateur vous permet :
- d’estimer l’énergie thermique libérée (PCS × masse),
- de simuler une courbe HRR (t² + plateau + extinction),
- de personnaliser les temps du feu,
- de télécharger les résultats (Excel + PNG).
""")

# 🔹 Matériaux de base
materiaux_info = {
    "Panneau OSB": {"pcs": 18, "densite": 10, "flux_critique": 12},
    "Câble PVC": {"pcs": 20, "densite": 1.2, "flux_critique": 18},
    "Polystyrène": {"pcs": 39, "densite": 0.03, "flux_critique": 10},
    "Gyproc RF (rose)": {"pcs": 1, "densite": 10, "flux_critique": 999}
}

# 🔄 Import CSV matériaux
uploaded_file = st.file_uploader("📥 Importer une base matériaux (.csv)", type=["csv"])
if uploaded_file:
    df_materiaux = pd.read_csv(uploaded_file)
    materiaux_info = {
        row["Nom"]: {"pcs": row["PCS"], "densite": row["Densite"], "flux_critique": row["FluxCritique"]}
        for idx, row in df_materiaux.iterrows()
    }

# 📋 Sélection matériau
selected_material = st.selectbox("Matériau", list(materiaux_info.keys()))
pcs = materiaux_info[selected_material]["pcs"]
densite = materiaux_info[selected_material]["densite"]

surface = st.number_input("Surface totale exposée (m²)", min_value=1.0, value=200.0)
masse_totale = surface * densite
energie_totale_MJ = masse_totale * pcs
energie_par_m2 = energie_totale_MJ / surface

st.markdown(f"**PCS :** {pcs} MJ/kg  ")
st.markdown(f"**Masse estimée :** {masse_totale:.1f} kg")
st.markdown(f"**Énergie totale :** {energie_totale_MJ:.0f} MJ  ")
st.markdown(f"**Charge calorifique surfacique :** {energie_par_m2:.1f} MJ/m²")

# ⏱️ Paramètres personnalisés HRR
t_monte = st.slider("Temps de montée (s)", 60, 1800, 600, 60)
t_plateau = st.slider("Durée du plateau (s)", 60, 1800, 600, 60)
t_descente = st.slider("Temps d’extinction (s)", 60, 1800, 600, 60)

alpha = 0.01  # simplifié
hrr_max = (surface * 200) / 1000  # en MW

# ⏱️ Vecteurs temporels
t1 = np.linspace(0, t_monte, 150)
t2 = np.linspace(t_monte, t_monte + t_plateau, 100)
t3 = np.linspace(t_monte + t_plateau, t_monte + t_plateau + t_descente, 100)

# 🔥 HRR
hrr1 = alpha * t1**2
hrr1 = np.clip(hrr1, 0, hrr_max)
hrr2 = np.ones_like(t2) * hrr1[-1]
hrr3 = np.linspace(hrr1[-1], 0, len(t3))

t_total = np.concatenate([t1, t2, t3])
hrr_total = np.concatenate([hrr1, hrr2, hrr3])
energie_kJ = np.trapz(hrr_total * 1000, t_total)
energie_MJ = energie_kJ / 1000

# 📊 Graphique
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t_total / 60, hrr_total, label=f"{selected_material}", color="orange")
ax.set_xlabel("Temps (min)")
ax.set_ylabel("HRR (MW)")
ax.set_title("Courbe HRR simulée")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# 📦 Export Excel
df_export = pd.DataFrame({
    "Temps (s)": t_total,
    "HRR (kW)": hrr_total * 1000
})
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df_export.to_excel(writer, index=False, sheet_name="Courbe HRR")
st.download_button("📥 Télécharger les données HRR (Excel)", output.getvalue(), file_name="hrr_v4_export.xlsx")

# 📸 Export image PNG
img_buffer = BytesIO()
fig.savefig(img_buffer, format='png')
st.download_button("📸 Télécharger le graphique (PNG)", img_buffer.getvalue(), file_name="hrr_v4_graph.png")

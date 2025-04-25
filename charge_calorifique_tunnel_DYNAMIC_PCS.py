import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Calcul de la charge calorifique HRR_STIB V3.3", layout="centered")
st.title("🔥 Calcul de la charge calorifique HRR_STIB – V3.3")

st.markdown("""
Ce calculateur vous permet :
- d’estimer l’énergie thermique libérée en cas d’incendie (PCS × masse),
- d’évaluer le risque d’inflammation selon la distance,
- de simuler une courbe HRR réaliste (alpha t² + plateau + extinction),
- de comparer avec un feu de rame (5 ou 15 MW).
""")

# 🔹 Matériaux
materiaux_info = {
    "Panneau OSB": {"pcs": 18, "densite": 10, "flux_critique": 12},
    "Panneau OSB 3": {"pcs": 17, "densite": 11, "flux_critique": 11},
    "Câble PVC": {"pcs": 20, "densite": 1.2, "flux_critique": 18},
    "Polystyrène": {"pcs": 39, "densite": 0.03, "flux_critique": 10},
    "Gyproc RF (rose)": {"pcs": 1, "densite": 10, "flux_critique": 999}
}

# 🧠 Nom du projet
nom_projet = st.text_input("Nom du projet ou scénario", "")

# 🔍 Sélection matériau
selected_material = st.selectbox("Matériau", list(materiaux_info.keys()))
pcs = materiaux_info[selected_material]["pcs"]
densite = materiaux_info[selected_material]["densite"]
flux_critique = materiaux_info[selected_material]["flux_critique"]

# 📏 Paramètres physiques
surface = st.number_input("Surface totale exposée (m²)", min_value=1.0, value=200.0)
masse_totale = surface * densite
energie_totale_MJ = masse_totale * pcs

st.markdown(f"**PCS :** {pcs} MJ/kg &nbsp;&nbsp;&nbsp; **Masse estimée :** {masse_totale:.1f} kg")
st.markdown(f"**Énergie totale estimée :** {energie_totale_MJ:.0f} MJ")

# 🌡️ Distance d’exposition
distance = st.slider("Distance à la source de feu (m)", 0.5, 5.0, 1.0, 0.5)

if distance <= 1:
    alpha = 0.012
    flux_txt = "> 25 kW/m² – Risque élevé"
elif distance <= 2:
    alpha = 0.006
    flux_txt = "15–25 kW/m² – Risque modéré"
elif distance <= 3:
    alpha = 0.003
    flux_txt = "10–15 kW/m² – Risque faible"
else:
    alpha = 0.0015
    flux_txt = "< 10 kW/m² – Risque négligeable"

st.markdown(f"**Flux estimé :** {flux_txt}")
hrr_max = (surface * 200) / 1000  # 200 kW/m² en conditions réalistes → en MW

# 🔥 Feu de rame
feu_rame = st.radio("Feu de rame de comparaison", ["M6/M7 – 5 MW", "Mx – 15 MW"])
hrr_rame_const = 5 if "5 MW" in feu_rame else 15

# 📈 Simulation HRR
st.subheader("📈 Courbe HRR simulée (t² + plateau + décroissance)")
t_monte, t_plateau, t_descente = 600, 600, 600  # 10 min + 10 + 10
t1 = np.linspace(0, t_monte, 150)
t2 = np.linspace(t_monte, t_monte + t_plateau, 100)
t3 = np.linspace(t_monte + t_plateau, t_monte + t_plateau + t_descente, 100)

hrr1 = alpha * t1**2
hrr1 = np.clip(hrr1, 0, hrr_max)
hrr2 = np.ones_like(t2) * hrr1[-1]
hrr3 = np.linspace(hrr1[-1], 0, len(t3))

t_total = np.concatenate([t1, t2, t3])
hrr_total = np.concatenate([hrr1, hrr2, hrr3])

# HRR rame (courbe alpha t² + plateau)
alpha_rame = hrr_rame_const / (t_monte**2)
hrr_rame_1 = alpha_rame * t1**2
hrr_rame_1 = np.clip(hrr_rame_1, 0, hrr_rame_const)
hrr_rame_2 = np.ones_like(t2) * hrr_rame_1[-1]
hrr_rame_3 = np.linspace(hrr_rame_1[-1], 0, len(t3))
hrr_rame_total = np.concatenate([hrr_rame_1, hrr_rame_2, hrr_rame_3])

# 🔻 Calcul énergie
energie_kJ = np.trapz(hrr_total * 1000, t_total)
energie_MJ = energie_kJ / 1000

# 📊 Affichage
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t_total / 60, hrr_total, label=f"{selected_material} à {distance:.1f} m", color="orange")
ax.plot(t_total / 60, hrr_rame_total, label=feu_rame, linestyle="--", color="blue")
ax.set_xlabel("Temps (min)")
ax.set_ylabel("HRR (MW)")
ax.set_title("Courbe HRR simulée")
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.markdown(f"**Énergie dégagée simulée :** {energie_MJ:.0f} MJ")

# 📥 Export Excel (optionnel)
df_export = pd.DataFrame({
    "Temps (s)": t_total,
    "HRR matériau (kW)": hrr_total * 1000,
    "HRR rame (kW)": hrr_rame_total * 1000
})
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df_export.to_excel(writer, index=False, sheet_name="Courbe HRR")
st.download_button("📥 Télécharger les données HRR (Excel)", output.getvalue(), file_name="hrr_simulation.xlsx")

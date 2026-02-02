# import streamlit as st
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt


# # =========================================================
# # 🎨 Thème dark compatible Streamlit (robuste)
# # =========================================================
# def apply_streamlit_dark_theme():
#     bg = st.get_option("theme.backgroundColor") or "#0E1117"
#     fg = st.get_option("theme.textColor") or "#FAFAFA"

#     plt.rcParams.update({
#         "figure.facecolor": bg,
#         "axes.facecolor": bg,
#         "axes.edgecolor": fg,
#         "axes.labelcolor": fg,
#         "xtick.color": fg,
#         "ytick.color": fg,
#         "text.color": fg,
#         "grid.color": fg,
#     })


# # =========================================================
# # 🧪 Simulation TEMPORAIRE du CSV KPI
# # (structure IDENTIQUE au CSV final)
# # =========================================================
# def simulate_kpi(system_id, n_runs=4):
#     rows = []
#     for _ in range(n_runs):
#         rows.append({
#             "system_id": system_id,

#             # ===== KPI DE FRÉQUENCE =====
#             "Average of failure per month": np.random.normal(10 + system_id, 1),
#             "Average of failure per trimestre": np.random.normal(30 + system_id, 2),
#             "Average of failure per year": np.random.normal(120 + system_id * 5, 5),

#             # ===== KPI DE STABILITÉ =====
#             "Stability per month": np.random.uniform(1.0, 2.0),
#             "Stability per trimestre": np.random.uniform(3.0, 5.0),
#             "Stability per year": np.random.uniform(8.0, 15.0),

#             # ===== KPI DE PERFORMANCE =====
#             "Preventive Effectiveness Ratio (PER)": np.random.uniform(0.5, 0.9),
#             "Précision du détecteur": np.random.uniform(0.7, 0.95),
#             "Taux de détection (Rappel)": np.random.uniform(0.6, 0.9),

#             # ===== KPI DE COÛT =====
#             "Average cost of one system": np.random.normal(9000 + system_id * 500, 400),
#             "Standard Deviation": np.random.uniform(500, 1200),
#         })
#     return pd.DataFrame(rows)


# # =========================================================
# # 📊 GRAPHE 1 — Stabilité Monte-Carlo (boxplot)
# # =========================================================
# def plot_stability(df):
#     apply_streamlit_dark_theme()
#     fig, ax = plt.subplots()

#     df.boxplot(
#         column="Average cost of one system",
#         by="system_id",
#         ax=ax
#     )

#     ax.set_title("Stability of Average Cost per System (4 runs)")
#     ax.set_xlabel("System")
#     ax.set_ylabel("Average cost of one system")
#     plt.suptitle("")

#     st.pyplot(fig)


# # =========================================================
# # 📊 GRAPHE 2 — Comparaison inter-systèmes (mean ± std)
# # =========================================================
# def plot_comparison(df):
#     apply_streamlit_dark_theme()

#     grouped = df.groupby("system_id")["Average cost of one system"]
#     means = grouped.mean()
#     stds = grouped.std()

#     fig, ax = plt.subplots()
#     ax.bar(means.index, means.values, yerr=stds.values, capsize=6)

#     ax.set_xlabel("System")
#     ax.set_ylabel("Average cost of one system")
#     ax.set_title("Comparison of systems (mean ± std)")

#     st.pyplot(fig)


# # =========================================================
# # 📊 GRAPHE 3 — Compromis KPI vs KPI
# # =========================================================
# def plot_tradeoff(df):
#     apply_streamlit_dark_theme()
#     fig, ax = plt.subplots()

#     ax.scatter(
#         df["Preventive Effectiveness Ratio (PER)"],
#         df["Average cost of one system"],
#         alpha=0.8
#     )

#     ax.set_xlabel("Preventive Effectiveness Ratio (PER)")
#     ax.set_ylabel("Average cost of one system")
#     ax.set_title("Trade-off: Cost vs Preventive Effectiveness")

#     st.pyplot(fig)


# # =========================================================
# # 📊 GRAPHE 4 — Performance du détecteur
# # =========================================================
# def plot_detector(df):
#     apply_streamlit_dark_theme()
#     fig, ax = plt.subplots()

#     ax.scatter(
#         df["Précision du détecteur"],
#         df["Taux de détection (Rappel)"],
#         alpha=0.8
#     )

#     ax.set_xlabel("Précision du détecteur")
#     ax.set_ylabel("Taux de détection (Rappel)")
#     ax.set_title("Detector performance")

#     st.pyplot(fig)


# # =========================================================
# # 📊 GRAPHE 5 — Corrélation entre KPI (stat descriptive)
# # =========================================================
# def plot_correlation(df):
#     apply_streamlit_dark_theme()

#     kpi_cols = [
#         "Average of failure per month",
#         "Average of failure per year",
#         "Stability per year",
#         "Preventive Effectiveness Ratio (PER)",
#         "Précision du détecteur",
#         "Taux de détection (Rappel)",
#         "Average cost of one system",
#     ]

#     corr = df[kpi_cols].corr()

#     fig, ax = plt.subplots()
#     im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)

#     ax.set_xticks(range(len(kpi_cols)))
#     ax.set_yticks(range(len(kpi_cols)))
#     ax.set_xticklabels(kpi_cols, rotation=45, ha="right")
#     ax.set_yticklabels(kpi_cols)

#     fig.colorbar(im, ax=ax)
#     ax.set_title("Correlation between KPI")

#     st.pyplot(fig)


# # =========================================================
# # 🧭 PAGE KPI (appelée depuis app.py)
# # =========================================================
# def page_kpi():
#     st.header("📈 KPI — Statistiques descriptives et analyse Monte-Carlo")

#     st.caption(
#         "Les données affichées sont **simulées temporairement** afin d’illustrer "
#         "les analyses KPI prévues. La structure est identique au CSV final."
#     )

#     # ===== Simulation de 2 systèmes × 4 runs =====
#     df = pd.concat(
#         [
#             simulate_kpi(system_id=0),
#             simulate_kpi(system_id=1),
#         ],
#         ignore_index=True,
#     )

#     st.subheader("Aperçu du CSV KPI simulé")
#     st.dataframe(df, use_container_width=True)

#     st.divider()
#     st.subheader("Stabilité intra-système")
#     plot_stability(df)

#     st.divider()
#     st.subheader("Comparaison inter-systèmes")
#     plot_comparison(df)

#     st.divider()
#     st.subheader("Analyse des compromis (KPI vs KPI)")
#     plot_tradeoff(df)

#     st.divider()
#     st.subheader("Performance du détecteur")
#     plot_detector(df)

#     st.divider()
#     st.subheader("Corrélations globales entre KPI")
#     plot_correlation(df)

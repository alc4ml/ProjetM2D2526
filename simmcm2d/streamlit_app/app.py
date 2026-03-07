sys.path.append(os.path.dirname(__file__))
import streamlit as st
from core.session import init_session
from views.configuration import page_configuration
from views.simulation import page_simulation
from views.graphes import page_graphes
from views.kpi import page_analyse_descriptive
from pathlib import Path
import pandas as pd
import sys
import os

# from views.kpi import page_kpi


# ======================================================
# CONFIG GLOBALE
# ======================================================
st.set_page_config(
    page_title="Simulateur de Maintenance Prédictive",
    layout="wide",
)

init_session()

query_params = st.query_params

if "page" in query_params:
    st.session_state.page = query_params["page"]


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

if "last_dataset" not in st.session_state:

    dataset_files = list(OUTPUT_DIR.glob("sample_system_dataset_*.csv"))
    table_files = list(OUTPUT_DIR.glob("sample_system_table_*.csv"))

    if dataset_files and table_files:

        # on prend les fichiers les plus récents
        last_dataset_path = max(dataset_files, key=lambda f: f.stat().st_mtime)
        last_table_path = max(table_files, key=lambda f: f.stat().st_mtime)

        st.session_state.last_dataset = pd.read_csv(last_dataset_path)
        st.session_state.last_dataset_path = last_dataset_path
        st.session_state.last_table_path = last_table_path  
# ======================================================
# SIDEBAR — NAVIGATION
# ======================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0;">
            <h2 style="margin-bottom: 0.2rem;">Maintenance Prédictive</h2>
            <p style="opacity: 0.7; margin-top: 0;">
                Simulateur (Test de fiabilité)
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if "page" not in st.session_state:
        st.session_state.page = "Configuration"

    def nav_button(label, page_name):
        is_active = st.session_state.page == page_name
        if st.button(
            label,
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.page = page_name
            st.query_params["page"] = page_name

    nav_button("Configuration", "Configuration")
    nav_button("Simulation", "Simulation")
    nav_button("Graphes", "Graphes")
    nav_button("Analyse descriptive", "Analyse descriptive")

    # st.divider()

    # st.caption(
    #     "Projet académique —\n"
    #     "Maintenance prédictive & simulation stochastique"
    # )


# ======================================================
# ROUTING
# ======================================================
page = st.session_state.page

if page == "Configuration":
    page_configuration()

elif page == "Simulation":
    page_simulation()

elif page == "Graphes":
    page_graphes()

elif page == "Analyse descriptive":
    # page_kpi()
    page_analyse_descriptive()

else:
    st.error("Page inconnue.")

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[2]))

from simmcm2d.util import sample_datasets
from core.session import init_session
from views.configuration import page_configuration
from views.simulation import page_simulation
from views.graphes import page_graphes
from views.kpi import page_analyse_descriptive
from views.estimation import page_estimation


APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = Path(__file__).resolve().parent / "okd.png"
OUTPUT_DIR = Path("outputs")


# ======================================================
# CONFIG GLOBALE
# ======================================================
st.set_page_config(
    page_title="Simulateur de Maintenance Prédictive",
    layout="wide",
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] button[kind="primary"],
        section[data-testid="stSidebar"] button[kind="secondary"] {
            border-radius: 10px;
        }
        section[data-testid="stSidebar"] img {
            margin-bottom: 0.5rem;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

init_session()

query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"]

OUTPUT_DIR.mkdir(exist_ok=True)

if "last_dataset" not in st.session_state:
    dataset_files = list(OUTPUT_DIR.glob("sample_system_dataset_*.csv"))
    table_files = list(OUTPUT_DIR.glob("sample_system_table_*.csv"))

    if dataset_files and table_files:
        last_dataset_path = max(dataset_files, key=lambda f: f.stat().st_mtime)
        last_table_path = max(table_files, key=lambda f: f.stat().st_mtime)

        st.session_state.last_dataset = pd.read_csv(last_dataset_path)
        st.session_state.last_dataset_path = last_dataset_path
        st.session_state.last_table_path = last_table_path


# ======================================================
# SIDEBAR — NAVIGATION
# ======================================================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown(
        """
        <div style="padding-top: 0.2rem; padding-bottom: 0.4rem;">
            <h2 style="margin: 0; font-size: 1.35rem;">Maintenance Prédictive</h2>
            <p style="margin: 0.25rem 0 0 0; opacity: 0.75; font-size: 0.95rem;">
                Simulateur de fiabilité & analyse
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    # st.caption("Navigation")

    if "page" not in st.session_state:
        st.session_state.page = "Configuration"

    def nav_button(label, page_name, icon=""):
        is_active = st.session_state.page == page_name
        button_label = f"{icon} {label}" if icon else label

        if st.button(
            button_label,
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.page = page_name
            st.query_params["page"] = page_name

    nav_button("Configuration", "Configuration", "⚙️")
    nav_button("Simulation", "Simulation", "▶️")
    nav_button("Graphes", "Graphes", "📈")
    nav_button("Analyse descriptive", "Analyse descriptive", "📊")
    nav_button("Estimation", "Estimation", "🔎")

    st.divider()
    st.caption("État")

    if "last_dataset_path" in st.session_state:
        st.success("Dernière simulation chargée")
        st.caption(st.session_state.last_dataset_path.name)
    else:
        st.info("Aucune simulation chargée")

    st.divider()
    st.caption("Projet académique")
    st.caption("Maintenance prédictive & simulation stochastique")


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
    page_analyse_descriptive()

elif page == "Estimation":
    page_estimation()

else:
    st.error("Page inconnue.")
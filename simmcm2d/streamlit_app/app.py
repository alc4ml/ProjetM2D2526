import streamlit as st
from core.session import init_session
from views.configuration import page_configuration
from views.simulation import page_simulation
from views.graphes import page_graphes
# from views.kpi import page_kpi


# ======================================================
# CONFIG GLOBALE
# ======================================================
st.set_page_config(
    page_title="Simulateur de Maintenance Prédictive",
    layout="wide",
)

init_session()


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

    nav_button("Configuration", "Configuration")
    nav_button("Simulation", "Simulation")
    nav_button("Graphes", "Graphes")
    nav_button("KPI", "KPI")

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

elif page == "KPI":
    # page_kpi()
    st.info("Page KPI à venir.")

else:
    st.error("Page inconnue.")

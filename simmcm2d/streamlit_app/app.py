import streamlit as st
from core.session import init_session
from views.configuration import page_configuration
from views.simulation import page_simulation
from views.graphes import page_graphes

st.set_page_config(page_title="Maintenance prédictive", layout="wide")
init_session()

#sidebar
st.sidebar.markdown("")

if "page" not in st.session_state:
    st.session_state.page = "Configuration"

def nav_button(label, page_name):
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = page_name

nav_button("🛠️ Configuration", "Configuration")
nav_button("⚙️ Simulation", "Simulation")
nav_button("📊 Graphes Notebook", "Graphes")
nav_button("📈 KPI", "KPI")

#Routing
page = st.session_state.page

if page == "Configuration":
    page_configuration()
elif page == "Simulation":
    page_simulation()
elif page == "Graphes":
    page_graphes()
else:
    st.info("KPI à venir")

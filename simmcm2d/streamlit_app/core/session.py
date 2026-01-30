import json
import streamlit as st
from core.defaults import DEFAULT_CONFIG

def init_session():
    if "default_config" not in st.session_state:
        st.session_state.default_config = DEFAULT_CONFIG
    if "config" not in st.session_state:
        st.session_state.config = json.loads(json.dumps(DEFAULT_CONFIG))
    if "df" not in st.session_state:
        st.session_state.df = None

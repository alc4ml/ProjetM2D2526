import importlib.util
from pathlib import Path

import pandas as pd
import streamlit as st


MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "parameter_estimation"
    / "parameter_estimation"
    / "estimate_parameters.py"
)

spec = importlib.util.spec_from_file_location("estimate_parameters_module", MODULE_PATH)
estimate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(estimate_module)

estimate_parameters_filepath = estimate_module.estimate_parameters_filepath


def page_estimation():
    st.header("🔎 Estimation des paramètres")

    if "last_dataset_path" not in st.session_state:
        st.warning("Veuillez d'abord lancer une simulation.")
        return

    st.subheader("Dataset utilisé")
    st.write(st.session_state.last_dataset_path.name)

    if "last_dataset" in st.session_state:
        st.subheader("Aperçu du dataset")
        st.dataframe(st.session_state.last_dataset.head(20), use_container_width=True)

    try:
        insp_param, comp_param = estimate_parameters_filepath(
            st.session_state.last_dataset_path
        )

        mu, sigma = insp_param
        eta, beta = comp_param

        df_parametres = pd.DataFrame([{
            "mu_inspection": mu,
            "sigma_inspection": sigma,
            "eta_failure": eta,
            "beta_failure": beta,
        }])

        st.subheader("Paramètres estimés")
        st.dataframe(df_parametres, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur lors de l'estimation des paramètres : {e}")
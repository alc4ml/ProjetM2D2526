import json
import streamlit as st
from simmcm2d import sample_datasets_conf
from pathlib import Path
import pandas as pd
from datetime import datetime

PARAM_TABLE_PATH = Path("examples") / "sample_system_datatable.csv"
OUTPUT_DIR = Path("outputs")

def page_simulation():
    st.header("⚙️ Simulation")

    if st.button("▶️ Lancer la simulation"):
        cfg = st.session_state.config

        OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

        # --- nom unique du CSV généré ---
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_filename = f"simulation_data_{run_id}.csv"
        cfg["output_data_filepath"] = str(OUTPUT_DIR / data_filename)

        # --- sauvegarde temporaire config JSON ---
        run_config_path = OUTPUT_DIR / "run_config.json"
        with open(run_config_path, "w") as f:
            json.dump(cfg, f, indent=2)

        # --- simulation ---
        df = sample_datasets_conf(run_config_path)
        st.session_state.df = df

        st.success("Simulation terminée")
        st.dataframe(df.head(50))

        # ==============================
        # Enregistrement des paramètres
        # ==============================

        row = {}

        # paramètres
        row.update(cfg["param"])
        row.update(cfg["costs"])

        # méta
        for k in [
            "n_systems",
            "n_events",
            "time_origin",
            "id_0_component",
            "id_0_system",
            "output_data_filepath",
        ]:
            row[k] = cfg.get(k)

        row_df = pd.DataFrame([row])

        # append ou création
        if PARAM_TABLE_PATH.exists():
            row_df.to_csv(PARAM_TABLE_PATH, mode="a", header=False, index=False)
        else:
            row_df.to_csv(PARAM_TABLE_PATH, index=False)

        st.info("Paramètres ajoutés à l’historique des simulations")

    # ==============================
    # Affichage & gestion historique
    # ==============================
    st.divider()
    st.subheader("📊 Historique des simulations")

    if PARAM_TABLE_PATH.exists():
        hist_df = pd.read_csv(PARAM_TABLE_PATH)
        st.dataframe(hist_df)

        if st.button("🧹 Réinitialiser l’historique"):
            PARAM_TABLE_PATH.unlink()
            st.success("Historique supprimé")
            st.rerun()
    else:
        st.info("Aucune simulation enregistrée pour l’instant.")

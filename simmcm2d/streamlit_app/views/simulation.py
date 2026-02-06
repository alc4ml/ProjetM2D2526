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

        # --- identifiant unique du run ---
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_filename = f"simulation_data_{run_id}.csv"

        cfg["output_data_filepath"] = str(OUTPUT_DIR / data_filename)
        cfg["output_table_filepath"] = str(PARAM_TABLE_PATH)

        # --- sauvegarde config ---
        run_config_path = OUTPUT_DIR / "run_config.json"
        with open(run_config_path, "w") as f:
            json.dump(cfg, f, indent=2)

        # --- simulation (le moteur écrit déjà le CSV KPI) ---
        df = sample_datasets_conf(run_config_path)
        st.session_state.df = df

        # ==================================================
        # 🔧 POST-TRAITEMENT DU CSV KPI (sans toucher au moteur)
        # ==================================================
        try:
            table_df = pd.read_csv(PARAM_TABLE_PATH)

            # On corrige UNIQUEMENT la dernière ligne (run courant)
            last_idx = table_df.index[-1]

            # paramètres du modèle
            for k, v in cfg.get("param", {}).items():
                table_df.loc[last_idx, k] = v

            # coûts
            for k, v in cfg.get("costs", {}).items():
                table_df.loc[last_idx, k] = v

            # paramètres globaux
            for k in [
                "n_systems",
                "n_events",
                "time_origin",
                "id_0_system",
                "id_0_component",
            ]:
                table_df.loc[last_idx, k] = cfg.get(k)

            # traçabilité du run (optionnel mais très propre)
            table_df.loc[last_idx, "run_id"] = run_id

            # réécriture du CSV
            table_df.to_csv(PARAM_TABLE_PATH, index=False)

        except Exception as e:
            st.warning(f"Post-traitement du CSV KPI impossible : {e}")

        st.success("Simulation terminée (KPI enregistrés et corrigés)")
        st.dataframe(df.head(50))

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

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

from simmcm2d import sample_datasets


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def page_simulation():
    st.header("⚙️ Simulation")

    cfg = st.session_state.config

    if st.button("▶️ Lancer la simulation", use_container_width=True):
        with st.spinner("Simulation en cours…"):
            # =========================
            # Génération des noms uniques
            # =========================
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            dataset_path = OUTPUT_DIR / f"sample_system_dataset_{timestamp}.csv"
            table_path = OUTPUT_DIR / f"sample_system_table_{timestamp}.csv"

            # =========================
            # Récupération paramètres
            # =========================
            param = cfg["param"]
            costs = cfg["costs"]

            n_systems = cfg["n_systems"]
            date_first = cfg["time"]["date_start"]
            date_final = cfg["time"]["date_end"]

            id_0_component = cfg.get("id_0_component", 0)
            id_0_system = cfg.get("id_0_system", 0)

            # =========================
            # Lancement simulation
            # =========================
            df = sample_datasets(
                param=param,
                costs=costs,
                n_systems=n_systems,
                date_first=date_first,
                date_final=date_final,
                id_0_component=id_0_component,
                id_0_system=id_0_system,
                output_data_filepath=dataset_path,
                output_table_filepath=table_path,
            )

            st.session_state.last_dataset = df
            st.session_state.last_dataset_path = dataset_path
            st.session_state.last_table_path = table_path

        st.success("Simulation terminée avec succès 🎉")

    # =========================
    # Résultats
    # =========================
    if "last_dataset" in st.session_state:
        st.subheader("📄 Aperçu du dataset généré")
        st.dataframe(st.session_state.last_dataset.head(50))

        st.download_button(
            "⬇️ Télécharger le dataset",
            data=st.session_state.last_dataset_path.read_bytes(),
            file_name=st.session_state.last_dataset_path.name,
            mime="text/csv",
            use_container_width=True,
        )

        st.divider()
        st.subheader("📊 Paramètres & KPI de la simulation")

        table_df = pd.read_csv(st.session_state.last_table_path)
        st.dataframe(table_df)

        st.download_button(
            "⬇️ Télécharger le fichier paramètres + KPI",
            data=st.session_state.last_table_path.read_bytes(),
            file_name=st.session_state.last_table_path.name,
            mime="text/csv",
            use_container_width=True,
        )

    else:
        st.info("Aucune simulation lancée pour l’instant.")

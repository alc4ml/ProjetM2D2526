import json
import streamlit as st
from core.utils import clamp_float


def page_configuration():
    st.header("🛠️ Simulateur de maintenance prédictive — Configuration")

    # Raccourcis
    cfg = st.session_state.config
    default_cfg = st.session_state.default_config
    param = cfg.get("param", {})
    costs = cfg.get("costs", {})
    time_cfg = cfg.get("time", {})
    meta = cfg.get("meta", {})

    # Bandeau haut
    colA, colB = st.columns([3, 2])
    with colA:
        st.caption("")
    with colB:
        if st.button("🔄 Réinitialiser aux valeurs par défaut", use_container_width=True):
            st.session_state.config = json.loads(json.dumps(default_cfg))
            st.success("Configuration réinitialisée.")
            st.rerun()

    left, right = st.columns(2)

    # =========================
    # Colonne gauche
    # =========================
    with left:
        # ---- Coûts
        with st.expander("💰 Coûts du système", expanded=True):
            costs["failure"] = st.number_input(
                "Coût de panne (€)", min_value=0,
                value=int(costs.get("failure", 1200)), step=50
            )
            costs["replacement"] = st.number_input(
                "Coût de remplacement (€)", min_value=0,
                value=int(costs.get("replacement", 1000)), step=50
            )
            costs["inspection"] = st.number_input(
                "Coût d’inspection (€)", min_value=0,
                value=int(costs.get("inspection", 100)), step=10
            )
            costs["component"] = st.number_input(
                "Coût du composant (€)", min_value=0,
                value=int(costs.get("component", 100)), step=10
            )

            st.caption("Utilisés pour le calcul des coûts cumulés et moyens.")

        # ---- Inspections (normale)
        with st.expander("📅 Inspections — Loi normale", expanded=True):
            param["mu"] = st.number_input(
                "μ (mu) — moyenne (heures)",
                min_value=0.0, value=float(param.get("mu", 168.0)), step=1.0
            )
            param["sigma"] = st.number_input(
                "σ (sigma) — écart-type (heures)",
                min_value=0.0, value=float(param.get("sigma", 25.2)), step=0.1
            )

        # ---- Qualité inspection
        with st.expander("🔍 Qualité de l’inspection", expanded=True):
            thr = float(param.get("inspection_threshold", 0.5))
            dev = float(param.get("inspection_deviation", 0.05))

            param["inspection_threshold"] = st.slider(
                "Seuil de décision", 0.0, 1.0,
                clamp_float(thr, 0.0, 1.0), 0.01
            )
            param["inspection_deviation"] = st.slider(
                "Incertitude (déviation)", 0.0, 0.5,
                clamp_float(dev, 0.0, 0.5), 0.01
            )

    # =========================
    # Colonne droite
    # =========================
    with right:
        # ---- Weibull
        with st.expander("⚙️ Vie du composant — Loi de Weibull", expanded=True):
            param["eta"] = st.number_input(
                "η (eta) — échelle (heures)",
                min_value=0.0, value=float(param.get("eta", 720.0)), step=1.0
            )
            param["beta"] = st.number_input(
                "β (beta)",
                min_value=0.1, value=float(param.get("beta", 3.0)), step=0.1
            )
            param["expiration"] = st.number_input(
                "Âge d’expiration (heures)",
                min_value=0.0, value=float(param.get("expiration", 792.0)), step=1.0
            )

        # ---- Délai remplacement
        with st.expander("⏱️ Délai de remplacement — Loi exponentielle", expanded=True):
            param["theta"] = st.number_input(
                "θ (theta) — paramètre (heures)",
                min_value=0.0, value=float(param.get("theta", 12.0)), step=0.5
            )

        # ---- Population
        with st.expander("👥 Population de systèmes", expanded=True):
            cfg["n_systems"] = st.number_input(
                "Capacité maximale de la flotte (K)",
                min_value=1, value=int(cfg.get("n_systems", 250)), step=1
            )

            param["r"] = st.number_input(
                "Taux de naissance (r)",
                min_value=0.0, value=float(param.get("r", 5e-4)),
                format="%.6f"
            )
            param["nu"] = st.number_input(
                "Taux de mort (ν)",
                min_value=0.0, value=float(param.get("nu", 5e-5)),
                format="%.6f"
            )

        # ---- Fenêtre temporelle
        with st.expander("📆 Fenêtre de simulation", expanded=True):
            time_cfg["date_start"] = st.text_input(
                "Date de début",
                value=time_cfg.get("date_start", "2010-01-01")
            )
            time_cfg["date_end"] = st.text_input(
                "Date de fin",
                value=time_cfg.get("date_end", "2025-12-31 12:00")
            )

        # # ---- Métadonnées
        # with st.expander("🧾 Métadonnées (UI / export)", expanded=False):
        #     meta["output_data_filepath"] = st.text_input(
        #         "Nom du fichier dataset",
        #         value=meta.get("output_data_filepath", "sample_system_dataset_0.csv")
        #     )
        #     meta["output_table_filepath"] = st.text_input(
        #         "Nom du fichier table KPI",
        #         value=meta.get("output_table_filepath", "sample_system_datatable.csv")
        #     )

        st.write("")
        if st.button("✅ Enregistrer la configuration", use_container_width=True):
            cfg["param"] = param
            cfg["costs"] = costs
            cfg["time"] = time_cfg
            cfg["meta"] = meta
            st.session_state.config = cfg
            st.success("Configuration enregistrée.")

    # Debug
    st.divider()
    with st.expander("🧪 Aperçu de la configuration (debug)", expanded=False):
        st.json(st.session_state.config)

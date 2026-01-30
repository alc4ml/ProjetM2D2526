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

    # Bandeau haut
    colA, colB = st.columns([3, 2])
    with colA:
        st.caption("Configuration par défaut définie dans le code (UI-first)")
    with colB:
        if st.button("🔄 Réinitialiser aux valeurs par défaut", use_container_width=True):
            st.session_state.config = json.loads(json.dumps(default_cfg))
            st.success("Configuration réinitialisée.")
            st.rerun()

    # Layout principal
    left, right = st.columns(2)

    # =========================
    # Colonne gauche
    # =========================
    with left:
        # ---- Coûts
        with st.expander("💰 Coûts du système", expanded=True):
            costs["failure"] = st.number_input(
                "Coût de panne (€)",
                min_value=0,
                value=int(costs.get("failure", 1200)),
                step=50,
            )
            costs["replacement"] = st.number_input(
                "Coût de remplacement (€)",
                min_value=0,
                value=int(costs.get("replacement", 1000)),
                step=50,
            )
            costs["inspection"] = st.number_input(
                "Coût d’inspection (€)",
                min_value=0,
                value=int(costs.get("inspection", 100)),
                step=10,
            )
            costs["component"] = st.number_input(
                "Coût du composant (€)",
                min_value=0,
                value=int(costs.get("component", 100)),
                step=10,
            )

            st.caption(
                "Ces coûts sont utilisés pour calculer le coût cumulé par système."
            )

        # ---- Loi normale (inspection)
        with st.expander("📅 Loi normale — Intervalles d’inspection", expanded=True):
            param["mu"] = st.number_input(
                "μ (mu) — moyenne (heures)",
                min_value=0.0,
                value=float(param.get("mu", 168.0)),
                step=1.0,
            )
            param["sigma"] = st.number_input(
                "σ (sigma) — écart-type (heures)",
                min_value=0.0,
                value=float(param.get("sigma", 25.2)),
                step=0.1,
            )

            st.caption(
                "Les inspections sont planifiées selon une loi normale autour de μ."
            )

        # ---- Qualité d’inspection
        with st.expander("🔍 Qualité de l’inspection", expanded=True):
            thr = float(param.get("inspection_threshold", 0.5))
            dev = float(param.get("inspection_deviation", 0.05))

            param["inspection_threshold"] = st.slider(
                "Seuil de décision",
                0.0,
                1.0,
                clamp_float(thr, 0.0, 1.0),
                0.01,
            )
            param["inspection_deviation"] = st.slider(
                "Déviation de mesure",
                0.0,
                0.5,
                clamp_float(dev, 0.0, 0.5),
                0.01,
            )

            st.caption(
                "L’inspection estime l’usure (CDF Weibull) et ajoute une incertitude "
                "via une loi Beta."
            )

    # =========================
    # Colonne droite
    # =========================
    with right:
        # ---- Loi de Weibull
        with st.expander("⚙️ Loi de Weibull — Vie du composant", expanded=True):
            param["eta"] = st.number_input(
                "η (eta) — échelle (heures)",
                min_value=0.0,
                value=float(param.get("eta", 720.0)),
                step=1.0,
            )
            param["beta"] = st.number_input(
                "β (beta)",
                min_value=0.1,
                value=float(param.get("beta", 3.0)),
                step=0.1,
            )
            param["expiration"] = st.number_input(
                "Âge d’expiration (heures)",
                min_value=0.0,
                value=float(param.get("expiration", 792.0)),
                step=1.0,
            )

            st.caption(
                "Le composant est remplacé automatiquement à l’âge d’expiration, "
                "même sans panne."
            )

        # ---- Loi exponentielle
        with st.expander("⏱️ Loi exponentielle — Délai après décision", expanded=True):
            param["theta"] = st.number_input(
                "θ (theta) — paramètre (heures)",
                min_value=0.0,
                value=float(param.get("theta", 12.0)),
                step=0.5,
            )

            st.caption(
                "Si un remplacement est requis mais non urgent, le délai est tiré "
                "selon une loi exponentielle."
            )

        # ---- Paramètres globaux
        with st.expander("🧮 Paramètres de simulation", expanded=True):
            cfg["n_systems"] = st.number_input(
                "Nombre de systèmes",
                min_value=1,
                value=int(cfg.get("n_systems", 10)),
                step=1,
            )
            cfg["n_events"] = st.number_input(
                "Nombre d’événements",
                min_value=1,
                value=int(cfg.get("n_events", 10000)),
                step=100,
            )

            with st.expander("⚙️ Paramètres avancés", expanded=False):
                cfg["time_origin"] = st.number_input(
                    "time_origin",
                    value=float(cfg.get("time_origin", 0)),
                    step=1.0,
                )
                cfg["id_0_system"] = st.number_input(
                    "id_0_system",
                    value=int(cfg.get("id_0_system", 0)),
                    step=1,
                )
                cfg["id_0_component"] = st.number_input(
                    "id_0_component",
                    value=int(cfg.get("id_0_component", 0)),
                    step=1,
                )

        st.write("")
        if st.button("✅ Enregistrer la configuration", use_container_width=True):
            cfg["param"] = param
            cfg["costs"] = costs
            st.session_state.config = cfg
            st.success("Configuration enregistrée. Elle sera utilisée pour la simulation.")

    # Debug
    st.divider()
    with st.expander("Aperçu JSON de la configuration (debug)", expanded=False):
        st.json(st.session_state.config)

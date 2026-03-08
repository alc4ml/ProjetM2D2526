# views/graphes.py
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import scipy.stats as stats


# =========================
# Utils
# =========================
def _get_config() -> dict:
    return st.session_state.get("config", {})


def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


def _hist(x, bins: int, xlabel: str, title: str):
    fig, ax = plt.subplots()
    ax.hist(np.asarray(x), bins=bins)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    st.pyplot(fig, clear_figure=True)


# =========================
# Page Graphes
# =========================
def page_graphes():
    st.markdown("## 📊 Graphes")
    st.caption(
        "Distributions théoriques et visualisation des données issues de la simulation"
    )
    st.divider()

    cfg = _get_config()
    if not cfg:
        st.warning("Aucune configuration trouvée. Va d’abord dans l’onglet **Configuration**.")
        return

    param = cfg.get("param", {})

    # Paramètres utiles
    eta = _safe_float(param.get("eta", 720))
    beta = _safe_float(param.get("beta", 3))
    mu = _safe_float(param.get("mu", 168))
    sigma = _safe_float(param.get("sigma", 25.2))
    theta = _safe_float(param.get("theta", 12))
    inspection_deviation = _safe_float(param.get("inspection_deviation", 0.05))

    tab_theo, tab_data = st.tabs(
        ["📐 Distributions (théorie)", "🧾 Graphes sur données simulées"]
    )

    # ======================================================
    # DISTRIBUTIONS THÉORIQUES (FIDÈLES AU NOTEBOOK)
    # ======================================================
    with tab_theo:
        st.subheader("Distributions des variables (théorie)")

        n = st.slider("Taille d’échantillon", 1_000, 50_000, 10_000, step=1_000)
        bins = st.slider("Nombre de bins", 10, 120, 50, step=5)

        col1, col2 = st.columns(2)

        # Weibull — âges de panne
        with col1:
            fail_ages = eta * np.random.weibull(beta, size=n)
            _hist(
                fail_ages,
                bins=bins,
                xlabel="failing time (hours)",
                title="Distribution of Component 'Fail Ages'",
            )

        # Normale — intervalles d’inspection
        with col2:
            inspection_windows = np.random.normal(loc=mu, scale=sigma, size=n)
            _hist(
                inspection_windows,
                bins=bins,
                xlabel="inspection interval (hours)",
                title="Distribution of Time Intervals Between Inspection",
            )

        col3, col4 = st.columns(2)

        # Cumsum inspections
        with col3:
            inspection_times = np.cumsum(inspection_windows)
            fig, ax = plt.subplots()
            ax.hist(inspection_times, bins=bins)
            ax.set_xlabel("inspection times (hours)")
            ax.set_title("Sample of Inspection Times")
            ax.set_yticks([])
            st.pyplot(fig, clear_figure=True)

        # Exponentielle — délai de remplacement
        with col4:
            repl_delay = np.random.exponential(theta, size=n)
            _hist(
                repl_delay,
                bins=bins,
                xlabel="replacement time interval (hours)",
                title="Distribution of Replacement Delay After Required",
            )

        # Beta — qualité d’inspection
        st.subheader("Inspection Wear Measurement Distributions")

        dev = max(0.0, min(inspection_deviation, 0.49))
        n_panels = 11
        cdfs = np.linspace(0.01, 0.99, n_panels)
        sample = np.linspace(0, 1, 200)

        fig, ax = plt.subplots(1, n_panels, sharey=True, figsize=(16, 8))
        for i in range(n_panels):
            age_cdf = float(cdfs[i])
            var = dev * age_cdf * (1 - age_cdf)
            max_var = 0.99 * age_cdf * (1 - age_cdf)
            var = min(var, max_var)

            k = age_cdf * (1 - age_cdf) / max(var, 1e-9) - 1.0
            a = age_cdf * k
            b = (1 - age_cdf) * k

            pdf = stats.beta.pdf(sample, a, b)
            ax[i].plot(pdf, sample)
            ax[i].axhline(y=age_cdf, color="gray")
            ax[i].set_xlabel(f"{age_cdf:.2f}")
            ax[i].set_xticks([])

        fig.suptitle("Inspection Wear Measurement Distributions")
        fig.supxlabel("Cumulated Density Representing Component Wear")
        st.pyplot(fig, clear_figure=True)

    # ======================================================
    # 🧾 GRAPHES SUR DONNÉES SIMULÉES
    # ======================================================
    with tab_data:
        st.subheader("Graphes basés sur la simulation courante")

        # IMPORTANT : aligné avec page_simulation.py
        df = st.session_state.get("last_dataset", None)

        if df is None:
            st.info("Aucune simulation disponible. Lance d’abord une simulation.")
            return

        st.caption(f"{len(df)} lignes × {len(df.columns)} colonnes")
        st.dataframe(df.head(25), use_container_width=True)

        # Histogramme des âges de panne
        if {"event_type", "component_age"}.issubset(df.columns):
            st.subheader("Distribution of Component Ages in Failure")
            failures = df[df["event_type"] == "failure"]["component_age"].dropna()

            if len(failures) > 0:
                _hist(
                    failures.values,
                    bins=bins,
                    xlabel="component age at failure (hours)",
                    title="Distribution of Component Ages in Failure",
                )
            else:
                st.info("Aucune panne détectée dans la simulation.")
        else:
            st.info("Colonnes attendues non trouvées : event_type, component_age")

        # Timeline des événements (version notebook / ancien code)
        needed = {"event_type", "event_date", "system_id"}
        if needed.issubset(df.columns):
            st.subheader("Sample of Inspection Times")

            n_events_show = st.slider(
                "Nombre d’événements affichés",
                1_000, 50_000, 10_000, step=1_000
            )

            df_ = df.head(n_events_show)

            fig, ax = plt.subplots()

            for e_type in df_["event_type"].dropna().unique():
                sub = df_[df_["event_type"] == e_type]
                ax.scatter(
                    sub["event_date"],
                    sub["system_id"],
                    label=e_type,
                    alpha=0.8,
                    s=1,   # très petit comme dans le notebook
                )

            ax.legend()
            ax.set_xlabel("event date")
            ax.set_ylabel("system id")
            ax.set_title("Sample of Inspection Times")
            plt.xticks(rotation=45)

            st.pyplot(fig, clear_figure=True)
        else:
            st.info("Colonnes attendues non trouvées : event_type, event_date, system_id")


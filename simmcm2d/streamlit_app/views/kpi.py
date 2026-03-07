import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter


def page_analyse_descriptive():

    st.header("📊 Analyse descriptive")

    if "last_dataset" not in st.session_state:
        st.warning("Veuillez d'abord lancer une simulation dans la page Simulation.")
        return

    df = st.session_state.last_dataset.copy()

    st.subheader("Aperçu du dataset")
    st.dataframe(df.head(20))

    # ================================
    # On crée les colonnes pour les graphes
    # ================================
    col1, col2 = st.columns(2)

    # Distribution des types d'événements
    with col1:
        fig, ax = plt.subplots()
        sns.countplot(data=df, x="event_type", ax=ax)
        ax.set_title("Distribution of event types")
        st.pyplot(fig)

    # Time between events
    df = df.sort_values(["system_id", "event_time"])
    df["delta_t"] = df["usage_since_last_event_h"]

    with col2:
        fig, ax = plt.subplots()
        sns.histplot(df["delta_t"], bins=50, ax=ax)
        ax.set_title("Time between consecutive events (hours)")
        st.pyplot(fig)

    # Timeline globale
    col1, col2 = st.columns(2)
    df["event_date"] = pd.to_datetime(df["event_date"])
    events_over_time = df.groupby(df.event_date.dt.to_period("Q")).size()
    with col1:
        fig, ax = plt.subplots()
        events_over_time.plot(kind="line", marker="o", ax=ax)
        ax.set_title("Number of events over time")
        ax.set_ylabel("Number of events")
        st.pyplot(fig)

    # Component age at failure
    failures = df[df.event_type == "failure"]
    with col2:
        fig, ax = plt.subplots()
        sns.histplot(failures["component_age"], bins=40, ax=ax)
        ax.set_title("Component age at failure")
        ax.set_xlabel("Component age")
        st.pyplot(fig)

    # Monthly failures
    col1, col2 = st.columns(2)
    failures["month"] = failures["event_date"].dt.to_period("M")
    monthly_failures = failures.groupby("month").size()
    with col1:
        fig, ax = plt.subplots()
        monthly_failures.plot(kind="line", marker="o", ax=ax)
        ax.set_title("Monthly number of failures")
        ax.set_ylabel("Failures per month")
        st.pyplot(fig)

    # Kaplan-Meier
    with col2:
        kmf = KaplanMeierFitter()
        events = df[df.event_type.isin(["failure", "replacement"])].copy()
        events["event"] = events.event_type == "failure"
        kmf.fit(durations=events["component_age"], event_observed=events["event"])
        fig, ax = plt.subplots()
        kmf.plot_survival_function(ax=ax)
        ax.set_title("Empirical survival function")
        ax.set_xlabel("Component age")
        ax.set_ylabel("Survival probability")
        st.pyplot(fig)

    # Empirical failure hazard
    col1, col2 = st.columns(2)
    bins = np.linspace(0, failures.component_age.max(), 20)
    failures["age_bin"] = pd.cut(failures["component_age"], bins)
    hazard = failures.groupby("age_bin").size()
    with col1:
        fig, ax = plt.subplots()
        hazard.plot(kind="line", marker="o", ax=ax)
        ax.set_title("Empirical failure hazard")
        ax.set_ylabel("Number of failures")
        st.pyplot(fig)

    # Inspection outcomes
    with col2:
        fig, ax = plt.subplots()
        sns.countplot(data=df, x="event_report", ax=ax)
        ax.set_title("Inspection outcomes")
        st.pyplot(fig)

    # Cost distribution by event type
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sns.boxplot(data=df, x="event_type", y="cost_event", ax=ax)
        ax.set_title("Cost distribution by event type")
        st.pyplot(fig)

    # Cost vs number of failures per system
    with col2:
        system_summary = df.groupby("system_id").agg(
            total_cost=("cost_cumulated", "max"),
            n_failures=("event_type", lambda x: (x == "failure").sum())
        )
        fig, ax = plt.subplots()
        sns.scatterplot(data=system_summary, x="n_failures", y="total_cost", ax=ax)
        ax.set_title("Cost vs number of failures per system")
        st.pyplot(fig)


    # ================================
# Paramètres et coûts retrouvés
# ================================
    # st.subheader("📋 Paramètres et coûts retrouvés")

    # if "last_table_path" in st.session_state:
    #     # On lit le CSV des KPI généré par la simulation
    #     table_df = pd.read_csv(st.session_state.last_table_path)

    #     # On affiche tout le tableau
    #     st.dataframe(table_df)

    #     # Vérifie si une colonne de coût existe
    #     possible_cost_cols = [col for col in table_df.columns if "cost" in col.lower()]
    #     if possible_cost_cols:
    #         cost_col = possible_cost_cols[0]  # on prend la première trouvée
    #         st.markdown(f"**Paramètre minimisant le coût total ({cost_col}) :**")
    #         best_row = table_df.loc[table_df[cost_col].idxmin()]
    #         st.dataframe(best_row)
    #     else:
    #         st.warning("Aucune colonne de coût trouvée dans le CSV KPI.")

    # else:
    #     st.info("Aucun fichier KPI disponible. Veuillez d'abord lancer une simulation.")
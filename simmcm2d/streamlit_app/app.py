import json
from pathlib import Path
import streamlit as st

# -----------------------------
# Utils
# -----------------------------
DEFAULT_CONF_PATH = Path("examples") / "sample_system_dataset.json"

def load_json_config(path: Path) -> dict:
    if not path.exists():
        # fallback minimal si le fichier n'existe pas
        return {
            "param": {
                "eta": 720,
                "beta": 3,
                "expiration": 792,
                "mu": 168,
                "sigma": 25.2,
                "theta": 12,
                "inspection_deviation": 0.05,
                "inspection_threshold": 0.5
            },
            "costs": {
                "replacement": 1000,
                "inspection": 100,
                "component": 100,
                "failure": 1200
            },
            "n_systems": 10,
            "n_events": 10000,
            "time_origin": 0,
            "id_0_component": 0,
            "id_0_system": 0,
        }
    return json.loads(path.read_text(encoding="utf-8"))

def clamp_float(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def init_session():
    if "default_config" not in st.session_state:
        st.session_state.default_config = load_json_config(DEFAULT_CONF_PATH)
    if "config" not in st.session_state:
        # config courante = copie de la config par défaut
        st.session_state.config = json.loads(json.dumps(st.session_state.default_config))

# -----------------------------
# Page: Configuration
# -----------------------------
def page_configuration():
    st.header("🛠️ Simulateur de maintenance prédictive — Configuration")

    colA, colB = st.columns([3, 2])
    with colA:
        st.caption(f"Configuration chargée : `{DEFAULT_CONF_PATH.as_posix()}`")
    with colB:
        if st.button("🔄 Réinitialiser aux valeurs par défaut", use_container_width=True):
            st.session_state.config = json.loads(json.dumps(st.session_state.default_config))
            st.success("Configuration réinitialisée.")
            st.rerun()

    cfg = st.session_state.config
    param = cfg.get("param", {})
    costs = cfg.get("costs", {})

    # --- LAYOUT 2 colonnes comme l'image ---
    left, right = st.columns([1, 1])

    # -------- Colonne gauche
    with left:
        with st.expander("💰 Coûts du système", expanded=True):
            costs["failure"] = st.number_input("Coût de panne (€)", min_value=0, value=int(costs.get("failure", 1200)), step=50)
            costs["replacement"] = st.number_input("Coût de remplacement (€)", min_value=0, value=int(costs.get("replacement", 1000)), step=50)
            costs["inspection"] = st.number_input("Coût d’inspection (€)", min_value=0, value=int(costs.get("inspection", 100)), step=10)
            costs["component"] = st.number_input("Coût du composant (€)", min_value=0, value=int(costs.get("component", 100)), step=10)
            st.caption("Ces coûts sont utilisés pour calculer le coût cumulé par système.")

        with st.expander("📅 Loi normale — Intervalles d’inspection", expanded=True):
            param["mu"] = st.number_input("μ (mu) — moyenne (heures)", min_value=0.0, value=float(param.get("mu", 168.0)), step=1.0)
            param["sigma"] = st.number_input("σ (sigma) — écart-type (heures)", min_value=0.0, value=float(param.get("sigma", 25.2)), step=0.1)
            st.caption("Les inspections sont planifiées selon une loi normale autour de μ.")

        with st.expander("🔍 Qualité de l’inspection", expanded=True):
            # threshold entre 0 et 1
            thr = float(param.get("inspection_threshold", 0.5))
            dev = float(param.get("inspection_deviation", 0.05))
            param["inspection_threshold"] = st.slider("Seuil de décision", 0.0, 1.0, clamp_float(thr, 0.0, 1.0), 0.01)
            param["inspection_deviation"] = st.slider("Déviation de mesure", 0.0, 0.5, clamp_float(dev, 0.0, 0.5), 0.01)
            st.caption("L’inspection estime l’usure (CDF Weibull) et ajoute une incertitude via une loi Beta.")

    # -------- Colonne droite
    with right:
        with st.expander("⚙️ Loi de Weibull — Vie du composant", expanded=True):
            param["eta"] = st.number_input("η (eta) — échelle (heures)", min_value=0.0, value=float(param.get("eta", 720.0)), step=1.0)
            param["beta"] = st.number_input("β (beta) — forme", min_value=0.1, value=float(param.get("beta", 3.0)), step=0.1)
            param["expiration"] = st.number_input("Âge d’expiration (heures)", min_value=0.0, value=float(param.get("expiration", 792.0)), step=1.0)
            st.caption("Le composant est remplacé automatiquement à l’âge d’expiration, même sans panne.")

        with st.expander("⏱️ Loi exponentielle — Délai après décision", expanded=True):
            param["theta"] = st.number_input("θ (theta) — paramètre (heures)", min_value=0.0, value=float(param.get("theta", 12.0)), step=0.5)
            st.caption("Si un remplacement est requis mais non urgent, le délai est tiré selon une loi exponentielle.")

        with st.expander("🧮 Paramètres de simulation", expanded=True):
            cfg["n_systems"] = st.number_input("Nombre de systèmes", min_value=1, value=int(cfg.get("n_systems", 10)), step=1)
            cfg["n_events"] = st.number_input("Nombre d’événements", min_value=1, value=int(cfg.get("n_events", 10000)), step=100)
            # avancés (pliables)
            with st.expander("⚙️ Avancés", expanded=False):
                cfg["time_origin"] = st.number_input("time_origin", value=float(cfg.get("time_origin", 0)), step=1.0)
                cfg["id_0_system"] = st.number_input("id_0_system", value=int(cfg.get("id_0_system", 0)), step=1)
                cfg["id_0_component"] = st.number_input("id_0_component", value=int(cfg.get("id_0_component", 0)), step=1)

        st.write("")
        if st.button("✅ Enregistrer la configuration", use_container_width=True):
            cfg["param"] = param
            cfg["costs"] = costs
            st.session_state.config = cfg
            st.success("Configuration enregistrée. Elle sera utilisée pour la simulation.")

    st.divider()
    with st.expander("📄 Aperçu JSON de la configuration (debug)", expanded=False):
        st.json(st.session_state.config)

# -----------------------------
# Stub pages (on codera après)
# -----------------------------
def page_simulation():
    st.header("⚙️ Simulation de données")
    st.info("À coder ensuite : bouton Run, génération CSV+JSON, aperçu df, téléchargements.")

def page_graphes():
    st.header("📊 Graphes")
    st.info("À coder ensuite : histogrammes + timeline (basés sur df).")

def page_kpi():
    st.header("📈 KPI (à venir)")
    st.info("À coder plus tard.")

# -----------------------------
# Main
# -----------------------------
st.set_page_config(page_title="Maintenance prédictive", layout="wide")
init_session()

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Aller à :",
    ["Configuration", "Simulation de données", "Graphes", "KPI (à venir)"],
    index=0
)

if page == "Configuration":
    page_configuration()
elif page == "Simulation de données":
    page_simulation()
elif page == "Graphes":
    page_graphes()
else:
    page_kpi()

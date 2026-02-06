DEFAULT_CONFIG = {
    # =====================
    # Paramètres scientifiques (core)
    # =====================
    "param": {
        # Composant (Weibull)
        "eta": 720,
        "beta": 3,
        "expiration": 792,

        # Inspections
        "mu": 168,
        "sigma": 25.2,
        "theta": 12,
        "inspection_deviation": 0.05,
        "inspection_threshold": 0.5,

        # Dynamique de population
        "r": 5e-4,
        "nu": 5e-5,
    },

    # =====================
    # Coûts (core)
    # =====================
    "costs": {
        "replacement": 1000,
        "inspection": 100,
        "component": 100,
        "failure": 1200,
    },

    # =====================
    # Population (core)
    # =====================
    "population": {
        "n_systems": 250,   # capacité maximale K
        "id_0_system": 0,
        "id_0_component": 0,
    },

    # =====================
    # Temps de simulation (core)
    # =====================
    "time": {
        "date_first": "2010-01-01",
        "date_final": "2025-12-31 12:00",
    },

    # =====================
    # UI / orchestration (hors core)
    # =====================
    "ui": {
        "auto_generate_filenames": True,
        "output_dir": "outputs",
    }
}

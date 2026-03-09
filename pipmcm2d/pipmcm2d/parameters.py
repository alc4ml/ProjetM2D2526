import pandas as pd
import numpy as np
from scipy.optimize import minimize


def estimate_inspection_parameters(df):
    # ---------------------------------------------------------
    # 1. ESTIMATION DES INSPECTIONS (Loi Normale)
    # ---------------------------------------------------------
    try:
        df_insp = df[df['event_type'] == 'inspection']
        # On prend le temps depuis le dernier événement pour les inspections
        intervalles = df_insp['usage_since_last_event_h'].dropna()
        
        mu_est = np.mean(intervalles)
        sigma_est = np.std(intervalles)

    except Exception as e:
        print("Erreur lors de l'estimation des inspections:", e)

    return mu_est, sigma_est


def estimate_component_parameters(df):
    # ---------------------------------------------------------
    # 2. ESTIMATION DES PANNES (Loi de Weibull avec Censure)
    # ---------------------------------------------------------
    try:
        # Grouper par composant pour trouver sa fin de vie
        comp_group = df.groupby('component_id')
        max_age = comp_group['component_age'].max()
        
        # Le composant a-t-il subi une panne ? (Sinon, il a été censuré/remplacé)
        has_failed = comp_group['event_type'].apply(lambda x: 'failure' in x.values)
        
        t = max_age.values
        failed = has_failed.values

        # Fonction de Log-Vraisemblance Négative pour Weibull avec Censure
        def weibull_neg_log_likelihood(params, t, failed):
            eta, beta = params
            if eta <= 0 or beta <= 0:
                return np.inf
            
            # Pannes : on connaît l'heure exacte du décès (Log de la Densité de probabilité)
            log_pdf = np.log(beta) - np.log(eta) + (beta - 1) * np.log(t[failed] / eta) - (t[failed] / eta)**beta
            
            # Remplacements préventifs : on sait juste qu'il a survécu jusqu'à t (Log de la Fonction de Survie)
            log_surv = - (t[~failed] / eta)**beta
            
            # On retourne l'inverse de la somme car on utilise la fonction "minimize"
            return - (np.sum(log_pdf) + np.sum(log_surv))

        # Valeurs initiales au hasard pour aider l'algorithme (eta=500, beta=2)
        initial_guess = [500.0, 2.0]
        # Limites pour éviter que l'algorithme ne teste des valeurs absurdes
        bounds = ((1, 5000), (0.1, 10))

        # Lancement de l'optimisation mathématique
        resultat = minimize(weibull_neg_log_likelihood, initial_guess, args=(t, failed), bounds=bounds)
        
        eta_est, beta_est = resultat.x
        
    except Exception as e:
        print("Erreur lors de l'estimation de Weibull:", e)

    return eta_est, beta_est


def estimate_parameters(df):
    insp_param = estimate_inspection_parameters(df)
    comp_param = estimate_component_parameters(df)

    return insp_param, comp_param


def estimate_parameters_filepath(csv_filepath):
    df = pd.read_csv(csv_filepath)

    return estimate_parameters(df)





    
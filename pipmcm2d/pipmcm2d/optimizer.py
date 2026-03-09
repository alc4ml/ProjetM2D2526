import numpy as np 
from joblib import Parallel, delayed

from simmcm2d import sample_datasets, get_kpi


def compute_cost(
    theta,
    fixed_param,
    costs,
    n_systemes=30,
    M=5,
    date_first="2010-01-01",
    date_final="2020-12-31 12:00",
    seeds=None,         
    alpha_std=0.4,
):
    
    if seeds is None:
        raise ValueError("compute_cost: 'seeds' doit être fourni pour garantir la reproductibilité.")

    param = fixed_param.copy()
    param.update({
        "mu": float(theta[0]),
        "sigma": float(theta[1]),
        "theta": float(theta[2]),
        "inspection_deviation": float(theta[3]),
        "inspection_threshold": float(theta[4]),
    })

    couts = []

    for s in np.asarray(seeds)[:M]:
        # On force le seed utilisé par sample_datasets 
        np.random.seed(int(s))

        df = sample_datasets(
            param=param,
            costs=costs,
            n_systems=n_systemes,
            date_first=date_first,
            date_final=date_final,
        )

        kpi = get_kpi(df, costs)

        avg_cost = kpi.get("Total average cost of one system", None)
        std_cost = kpi.get("Standard Deviation", 0.0)

        if avg_cost is None or not np.isfinite(avg_cost):
            return 1e12

        cost = float(avg_cost) + float(alpha_std) * float(std_cost)
        if not np.isfinite(cost):
            return 1e12

        couts.append(cost)

    return float(np.mean(couts)) if couts else 1e12


def algorithme_genetique(
    fixed_param,
    costs,
    bornes,
    rng,                      
    taille_pop=30,
    max_generation=50,
    elitisme=2,
    tournoi_k=4,
    proba_mutation=0.30,
    sigma_mutation=0.15,
    alpha_std=0.4,
    n_systemes=30,
    M_test=3,
    M_validate=20,
    patience=8,
    min_delta=1e-6,
    n_jobs=-1,
    immigration_rate=0.20,
    date_first="2010-01-01",
    date_final="2020-12-31 12:00",
):

    dim = len(bornes)
    bornes = np.array(bornes, dtype=float)

    # Initialisation population 
    population = np.zeros((taille_pop, dim), dtype=float)
    for j in range(dim):
        lo, hi = bornes[j]
        population[:, j] = rng.uniform(lo, hi, size=taille_pop)

    meilleur_theta = None
    meilleur_cout_valid = float("inf")

    hist_best_fast = []
    hist_mean_fast = []
    hist_best_valid = []

    best_since = 0
 
    # Pour paralléliser les calculs, 
    try:
        joblib_ok = True
    except Exception:
        joblib_ok = False

    print(f"{'génération':>10} | {'Best_fast':>12} | {'Mean_fast':>12} | {'Best_valid':>12}")

    for gen in range(1, max_generation + 1):

        # Seeds fixes pour cette génération 
        seeds_gen = rng.integers(0, 2**31 - 1, size=max(M_test, M_validate), dtype=np.int64)

        def eval_fast(theta):
            return compute_cost(
                theta=theta,
                fixed_param=fixed_param,
                costs=costs,
                n_systemes=n_systemes,
                M=M_test,
                seeds=seeds_gen,        
                alpha_std=alpha_std,
                date_first=date_first,
                date_final=date_final,
            )

        if joblib_ok and n_jobs != 1:
            fitness_fast = np.array(
                Parallel(n_jobs=n_jobs)(delayed(eval_fast)(population[p]) for p in range(taille_pop)),
                dtype=float
            )
        else:
            fitness_fast = np.array([eval_fast(population[p]) for p in range(taille_pop)], dtype=float)

        gen_best_idx = int(np.argmin(fitness_fast))
        best_fast = float(fitness_fast[gen_best_idx])
        mean_fast = float(np.mean(fitness_fast))

        theta_best_fast = population[gen_best_idx].copy()

        best_valid = float(
            compute_cost(
                theta=theta_best_fast,
                fixed_param=fixed_param,
                costs=costs,
                n_systemes=n_systemes,
                M=M_validate,
                seeds=seeds_gen,        
                alpha_std=alpha_std,
                date_first=date_first,
                date_final=date_final,
            )
        )

        if best_valid + min_delta < meilleur_cout_valid:
            meilleur_cout_valid = best_valid
            meilleur_theta = theta_best_fast.copy()
            best_since = gen

        hist_best_fast.append(best_fast)
        hist_mean_fast.append(mean_fast)
        hist_best_valid.append(best_valid)

        print(f"{gen:10d} | {best_fast:12.2f} | {mean_fast:12.2f} | {best_valid:12.2f}")

        if gen - best_since >= patience:
            print(f"Arret anticipé: aucune amélioration (Validée) depuis {patience} générations.")
            break

        # Reproduction
        idx_sorted = np.argsort(fitness_fast)
        elites = population[idx_sorted[:elitisme]].copy()

        nouvelle_pop = [e for e in elites]

        while len(nouvelle_pop) < taille_pop:

            def tournament_select():
                contestants = rng.choice(taille_pop, size=tournoi_k, replace=False)
                best = contestants[np.argmin(fitness_fast[contestants])]
                return population[best]

            parent1 = tournament_select()
            parent2 = tournament_select()

            mask = rng.integers(0, 2, size=dim).astype(bool)
            enfant = np.where(mask, parent1, parent2).astype(float)

            for j in range(dim):
                if rng.random() < proba_mutation:
                    lo, hi = bornes[j]
                    amplitude = hi - lo
                    enfant[j] += rng.normal(0.0, sigma_mutation * amplitude)
                    enfant[j] = float(np.clip(enfant[j], lo, hi))

            nouvelle_pop.append(enfant)

        population = np.array(nouvelle_pop, dtype=float)

        # Immigration 
        n_imm = int(np.floor(immigration_rate * taille_pop))
        if n_imm > 0:
            replace_candidates = np.arange(elitisme, taille_pop)
            if replace_candidates.size > 0:
                n_imm = min(n_imm, replace_candidates.size)
                replace_idx = rng.choice(replace_candidates, size=n_imm, replace=False)

                for idx in replace_idx:
                    for j in range(dim):
                        lo, hi = bornes[j]
                        population[idx, j] = rng.uniform(lo, hi)

    return meilleur_theta, meilleur_cout_valid, hist_best_fast, hist_mean_fast, hist_best_valid
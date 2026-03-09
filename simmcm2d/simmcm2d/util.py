import pandas as pd
from .classes import *

def component_factory(id_0, expiration, eta, beta):
    id_component = id_0
    while True:
        id_component += 1
        yield Component(id_component, expiration, eta, beta)


def system_factory(id_0, component_factory):
    id_system = id_0
    while True:
        id_system += 1
        component = next(component_factory)
        yield System(id_system, component)


def get_kpi(system_df, costs):
    df = system_df.copy()
    df['event_date'] = pd.to_datetime(df['event_date'])

    nb_pannes = np.sum(df["event_type"] == "failure")
    
    # Number of failure per month
    failures = df[df.event_type == "failure"]
    failures = df[df.event_type == "failure"].copy() 
    failures['month'] = failures['event_date'].dt.to_period("M")

    monthly_failures = failures.groupby("month").size()

    # Number of failure per trimestre
    failures = df[df.event_type == "failure"]
    failures = df[df.event_type == "failure"].copy()
    failures['trimestre'] = failures['event_date'].dt.to_period("Q")

    trimestre_failures = failures.groupby("trimestre").size()

    # Number of failure per year
    failures = df[df.event_type == "failure"]
    failures = df[df.event_type == "failure"].copy()
    failures['year'] = failures['event_date'].dt.to_period("Y")

    year_failures = failures.groupby("year").size()

    # Number of reparation per months
    replacement = df[df.event_type == "replacement"]
    replacement = df[df.event_type == "replacement"].copy()
    replacement['month'] = replacement['event_date'].dt.to_period("M")
    
    monthly_replacement = replacement.groupby("month").size()

    # Number of reparation per trimestre
    replacement = df[df.event_type == "replacement"]
    replacement = df[df.event_type == "replacement"].copy()
    replacement['trimestre'] = replacement['event_date'].dt.to_period("Q")
    
    trimestre_replacement = replacement.groupby("trimestre").size()
    
    # Number of reparation per year
    replacement = df[df.event_type == "replacement"]
    replacement = df[df.event_type == "replacement"].copy()
    replacement['year'] = replacement['event_date'].dt.to_period("Y")
    
    year_replacement = replacement.groupby("year").size()

    failures_by_system = df[df.event_type == "failure"].groupby('system_id').size()
    # Moyenne de pannes par système sur toute la durée
    avg_fail_lifetime = failures_by_system.mean()

    failures['month'] = failures['event_date'].dt.to_period("M")
    avg_f_sys_mo = failures.groupby(['month', 'system_id']).size().mean()

    failures['trimestre'] = failures['event_date'].dt.to_period("Q")
    avg_f_sys_tri = failures.groupby(['trimestre', 'system_id']).size().mean()

    failures['year'] = failures['event_date'].dt.to_period("Y")
    avg_f_sys_yr = failures.groupby(['year', 'system_id']).size().mean()

    # Calculs des Remplacements par système
    replacements_only = df[df.event_type == "replacement"].copy()
    # Moyenne de remplacements par système sur toute la durée de vie
    avg_repl_lifetime = replacements_only.groupby('system_id').size().mean() if not replacements_only.empty else 0

    replacements_only['m'] = replacements_only['event_date'].dt.to_period("M")
    avg_r_sys_mo = replacements_only.groupby(['m', 'system_id']).size().mean()

    replacements_only['q'] = replacements_only['event_date'].dt.to_period("Q")
    avg_r_sys_tri = replacements_only.groupby(['q', 'system_id']).size().mean()
    # Annuel
    replacements_only['y'] = replacements_only['event_date'].dt.to_period("Y")
    avg_r_sys_yr = replacements_only.groupby(['y', 'system_id']).size().mean()

    
    # Ratio (it's the same ratio for month, trimestre and year)
    monthly_ratio = monthly_replacement.describe()["mean"] / monthly_failures.describe()["mean"]

    detections = len(df[df['FF'] == True])
    fausses_alertes = len(df[df['FF'] == False])
    precision = detections / (detections + fausses_alertes) if (detections + fausses_alertes) > 0 else 0
    rappel = detections / nb_pannes if nb_pannes > 0 else 0

    # Costs

    df['cost_event'] = df['event_type'].map(costs)
    cost_per_system = df.groupby('system_id')['cost_cumulated'].last().reset_index()
    
    # Total cost of the fleet per month
    df['month'] = df['event_date'].dt.to_period('M')
    monthly_fleet_cost = df.groupby('month')['cost_event'].sum().reset_index()  # Calculer le coût total de la flotte par mois (On fait la somme de tous les 'cost_event' pour chaque mois)
    systems_per_month = df.groupby('month')['system_id'].nunique().reset_index() # Nb de systèmes étaient actifs par mois 
    fleet_kpi = pd.merge(monthly_fleet_cost, systems_per_month, on='month')  # Fusionner et calculer le coût moyen par système pour chaque mois
    fleet_kpi.columns = ['Mois', 'Cout_Total_Flotte', 'Nombre_Systemes']
    moyenne_mensuelle_flotte = fleet_kpi['Cout_Total_Flotte'].mean() # Calculer la moyenne globale de la flotte sur un mois
    
    # Mean cost for 1 system per month
    cost_per_sys_per_month = df.groupby(['month', 'system_id'])['cost_event'].sum().reset_index()
    average_cost_per_month = cost_per_sys_per_month.groupby('month')['cost_event'].mean() 
    cost_for_one_syst_month = average_cost_per_month.mean()

     # Total cost of the fleet per trimestre
    df['trimestre'] = df['event_date'].dt.to_period('Q')
    trimestre_fleet_cost = df.groupby('trimestre')['cost_event'].sum().reset_index()  # Calculer le coût total de la flotte par trimestre (On fait la somme de tous les 'cost_event' pour chaque trimestre)
    systems_per_trimestre = df.groupby('trimestre')['system_id'].nunique().reset_index() # Nb de systèmes étaient actifs par trimestre
    fleet_kpi = pd.merge(trimestre_fleet_cost, systems_per_trimestre, on='trimestre')  # Fusionner et calculer le coût moyen par système pour chaque trimestre
    fleet_kpi.columns = ['Trimestre', 'Cout_Total_Flotte_Trimestre', 'Nombre_Systemes_Trimestre']
    moyenne_trimestrielle_flotte = fleet_kpi['Cout_Total_Flotte_Trimestre'].mean() # Calculer la moyenne globale de la flotte sur un trimestre
        
    # Mean cost for 1 system per trimestre
    cost_per_sys_per_trim = df.groupby(['trimestre', 'system_id'])['cost_event'].sum().reset_index()
    average_cost_per_trimestre = cost_per_sys_per_trim.groupby('trimestre')['cost_event'].mean() # Moyenne par trimestre: Pour chaque trimestre, on calcule la moyenne des coûts des systèmes présents
    cost_for_one_syst_trimestre = average_cost_per_trimestre.mean() # Moyenne des moyennes: On fait la moyenne sur toutes les périodes trimestrielles


    # Total cost of the fleet per year
    df['year'] = df['event_date'].dt.to_period('Y')
    year_fleet_cost = df.groupby('year')['cost_event'].sum().reset_index()  # Calculer le coût total de la flotte par trimestre (On fait la somme de tous les 'cost_event' pour chaque year)
    systems_per_year = df.groupby('year')['system_id'].nunique().reset_index() # Nb de systèmes étaient actifs par an
    fleet_kpi = pd.merge(year_fleet_cost, systems_per_year, on='year')  # Fusionner et calculer le coût moyen par système pour chaque année
    fleet_kpi.columns = ['Year', 'Cout_Total_Flotte_Year', 'Nombre_Systemes_Year']
    moyenne_annuelle_flotte = fleet_kpi['Cout_Total_Flotte_Year'].mean() # Calculer la moyenne globale de la flotte sur une année
        
    # Mean cost for 1 system per year
    cost_per_sys_per_year = df.groupby(['year', 'system_id'])['cost_event'].sum().reset_index()
    average_cost_per_year = cost_per_sys_per_year.groupby('year')['cost_event'].mean() 
    cost_for_one_syst_year = average_cost_per_year.mean() 

    
    KPI = {
        # Failure Metrics (Fleet)
        "avg_fail_m": round(monthly_failures.mean(), 2),
        "avg_fail_t": round(trimestre_failures.mean(), 2),
        "avg_fail_y": round(year_failures.mean(), 1),
        
        "std_fail_m": round(monthly_failures.std(), 2),
        "std_fail_t": round(trimestre_failures.std(), 2),
        "std_fail_y": round(year_failures.std(), 2),

        # Replacement Metrics (Fleet)
        "avg_repl_m": round(monthly_replacement.mean(), 2),
        "avg_repl_t": round(trimestre_replacement.mean(), 2),
        "avg_repl_y": round(year_replacement.mean(), 1),
        
        "std_repl_m": round(monthly_replacement.std(), 2),
        "std_repl_t": round(trimestre_replacement.std(), 2),
        "std_repl_y": round(year_replacement.std(), 2),

        # Per System Metrics (Reliability)
        "avg_fail_syst_total": round(avg_fail_lifetime, 2),
        "avg_fail_syst_m": round(avg_f_sys_mo, 3), # On garde 3 ici car souvent très petit
        "avg_fail_syst_t": round(avg_f_sys_tri, 2),
        "avg_fail_syst_y": round(avg_f_sys_yr, 2),
            
        "avg_repl_syst_total": round(avg_repl_lifetime, 2),
        "avg_repl_syst_m": round(avg_r_sys_mo, 3),
        "avg_repl_syst_t": round(avg_r_sys_tri, 2),
        "avg_repl_syst_y": round(avg_r_sys_yr, 2),
        
        # Efficiency and Detection
        "PER": round(monthly_ratio, 2),
        "Precision": round(precision, 2),
        "Recall": round(rappel, 2),
        
        # Cost Metrics
        "cost_per_syst": round(cost_per_system['cost_cumulated'].mean(), 2), # Total average cost of 1 system
        "Std_per_syst": round(cost_per_system['cost_cumulated'].std(), 2), # ecart type 1 system
        
        "cost_fleet_m": round(moyenne_mensuelle_flotte, 2), # Total cost of the fleet per month
        "avg_cost_syst_m": round(cost_for_one_syst_month, 2), # Average cost for 1 system per month
        
        "cost_fleet_t": round(moyenne_trimestrielle_flotte, 2),
        "avg_cost_syst_t": round(cost_for_one_syst_trimestre, 2),
        
        "cost_fleet_y": round(moyenne_annuelle_flotte, 2),
        "avg_cost_syst_y": round(cost_for_one_syst_year, 2)
        
    }
    return KPI


def sample_to_table(system_df, output_table_filepath, param, costs,
                    n_systems, date_first, date_final,
                    id_0_component, id_0_system,
                    output_data_filepath=None):
    try:
        table_df = pd.read_csv(output_table_filepath)
    except:
        table_df = pd.DataFrame()
    new_row = dict()
    new_row.update(param)
    new_row.update(costs)
    new_row.update({
        "n_systems": n_systems,
        "date_first": date_first,
        "date_final": date_final,
        "id_0_component": id_0_component,
        "id_0_system": id_0_system,
        "output_data_filepath":output_data_filepath
    })
    KPI = get_kpi(system_df, costs)
    new_row.update(KPI)
    new_row = pd.DataFrame([new_row])
    table_df =  pd.concat([table_df, new_row])
    table_df.to_csv(output_table_filepath, index=False)


def sample_datasets(param, costs, n_systems = 1,
                    date_first="2010-01-01 12:00",
                    date_final="2025-12-31 12:00",
                    id_0_component=0, id_0_system=0,
                    output_data_filepath=None, output_table_filepath=None):

    c_factory = component_factory(
        id_0=id_0_component,
        eta=param["eta"],
        beta=param["beta"],
        expiration=param["expiration"])
    s_factory = system_factory(
        id_0=id_0_system,
        component_factory=c_factory)    
    inspector = Inspector(
        deviation=param["inspection_deviation"],
        threshold=param["inspection_threshold"])
    
    system_data = []

    manager = Manager(n_systems, s_factory, c_factory, inspector, param, costs)

    # start iterations
    date_first_ = pd.to_datetime(date_first)
    date_final_ = pd.to_datetime(date_final)
    max_time_timedelta = date_final_-date_first_
    while True:
        # compute next event
        event_data = manager.next_event()
        # check if time has been reached and break
        last_event_seconds = manager.t_last_event*60*60
        if last_event_seconds > max_time_timedelta.total_seconds():
            break

        # otherwise, continue
        system_data.append(event_data)

    # create dataframe
    system_df = pd.DataFrame(system_data)
    
    # format dates and times
    time_seconds = (system_df.event_date*60*60).astype(int)
    system_df.event_date = pd.to_datetime(time_seconds, origin=date_first_, unit='s')
    system_df.event_time = system_df.event_date.dt.time
    system_df.event_date = system_df.event_date.dt.date
    system_df.system_age = system_df.system_age.round(2)
    system_df.component_age = system_df.component_age.round(2)
    system_df.usage_since_last_event_h = system_df.usage_since_last_event_h.round(2)

    # save generated data if path given
    if output_data_filepath is not None:
        system_df.to_csv(output_data_filepath)

    # add report to table if path given
    if output_table_filepath is not None:
        sample_to_table(system_df, output_table_filepath, param, costs,
                        n_systems, date_first, date_final,
                        id_0_component, id_0_system,
                        output_data_filepath)

    return system_df

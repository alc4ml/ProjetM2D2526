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

    # Ratio (it's the same ratio for month, trimestre and year)
    monthly_ratio = monthly_replacement.describe()["mean"] / monthly_failures.describe()["mean"]

    detections = len(df[df['FF'] == True])
    fausses_alertes = len(df[df['FF'] == False])
    precision = detections / (detections + fausses_alertes) if (detections + fausses_alertes) > 0 else 0
    rappel = detections / (detections + nb_pannes) if (detections + nb_pannes) > 0 else 0

    # Costs
    df['cost_event'] = df['event_type'].map(costs)
    cost_per_system = df.groupby('system_id')['cost_cumulated'].last().reset_index()

    KPI = {
        "Average of failure per month": monthly_failures.describe()["mean"],
        "Average of failure per trimestre": trimestre_failures.describe()["mean"],
        "Average of failure per year":year_failures.describe()["mean"],
        "Stability per month":monthly_failures.describe()["std"],
        "Stability per trimestre":trimestre_failures.describe()["std"],
        "Stability per year":year_failures.describe()["std"],

        "Average of replacement per month": monthly_replacement.describe()["mean"],
        "Average of replacement per trimestre": trimestre_replacement.describe()["mean"],
        "Average of replacement per year":year_replacement.describe()["mean"],
        "Stability per month":monthly_replacement.describe()["std"],
        "Stability per trimestre":trimestre_replacement.describe()["std"],
        "Stability per year":year_replacement.describe()["std"],
        
        "Preventive Effectiveness Ratio (PER)": monthly_ratio,
        
        "Précision du détecteur": round(precision, 2),
        "Taux de détection (Rappel)": round(rappel, 2),
        
        "Average cost of one system": cost_per_system['cost_cumulated'].describe()["mean"],
        "Standard Deviation": cost_per_system['cost_cumulated'].describe()["std"]
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

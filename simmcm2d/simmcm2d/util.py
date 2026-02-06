import json
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

    detections = len(df[df['FF'] == 'True'])
    fausses_alertes = len(df[df['FF'] == 'False'])
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


def sample_datasets(param, costs, n_systems = 1, n_events = 1000,
                    time_origin=0, id_0_component=0, id_0_system=0,
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
    for _ in range(n_events):
        event_data = manager.next_event()
        system_data.append(event_data)

    # create dataframe
    system_df = pd.DataFrame(system_data)
    
    # format dates and times
    system_df.event_date = pd.to_datetime(
        (system_df.event_date*60*60).astype(int), unit='s', origin=time_origin)
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
        try:
            table_df = pd.read_csv(output_table_filepath)
        except:
            table_df = pd.DataFrame()
        new_row = dict()
        new_row.update(param)
        new_row.update(costs)
        new_row.update({
            "n_systems": 10,
            "n_events": 10000,
            "time_origin": 0,
            "id_0_component": 0,
            "id_0_system": 0,
            "output_data_filepath":output_data_filepath
        })
        KPI = get_kpi(system_df, costs)
        new_row.update(KPI)
        new_row = pd.DataFrame([new_row])
        table_df =  pd.concat([table_df, new_row])
        table_df.to_csv(output_table_filepath, index=False)

    return system_df


def sample_datasets_conf(configuration_filepth):
    
    # read configuration from file
    with open(configuration_filepth, "r") as file:
        conf = json.load(file)
    
    # decode and return from configuration
    return sample_datasets(**conf)
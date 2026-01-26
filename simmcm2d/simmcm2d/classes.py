import numpy as np
import scipy as scp

class Component:
    def __init__(self, id_component, expiration, eta, beta):
        self.id = id_component

        # distribution parameters
        self.eta = eta
        self.beta = beta

        # age, expiration amd fail
        self.age = 0
        self.age_expi = expiration
        self.age_fail = eta*np.random.weibull(beta)


class System:
    def __init__(self, id_system, component):
        self.id = id_system
        
        # age and 
        self.age = 0
        # component
        self.component = component
        # cummulated costs
        self.cost_cumulated = 0


class Inspector:
    def __init__(self, deviation, threshold):
        self.deviation = deviation
        self.threshold = threshold
    
    def component_cdf(self, component):
        age = component.age
        eta = component.eta
        beta = component.beta

        age_cdf = scp.stats.weibull_min.cdf(age/eta, beta)

        return age_cdf
    
    def inspect(self, component):
        # exact cdf
        age_cdf = self.component_cdf(component)

        # adds imprecision by sampling from a Beta
        var = self.deviation*age_cdf*(1-age_cdf)
        a = age_cdf*(age_cdf*(1-age_cdf)/var-1)
        b = (1-age_cdf)*(age_cdf*(1-age_cdf)/var-1)
        age_beta = np.random.beta(a,b)

        # conditional report
        replace = age_beta > self.threshold

        return replace
    
    def inspect_ff(self, component):
        # exact cdf
        age_cdf = self.component_cdf(component)
        replace = age_cdf > self.threshold

        return replace
    
    def schedule_next(self, time_last_inspection, mu, sigma):
        time_next_inspection = time_last_inspection
        time_next_inspection += np.random.normal(mu, sigma)

        return time_next_inspection
    
    def schedule_replacement(self, time_last_event, theta, urgent=False):
        time_replacement = time_last_event
        time_replacement += 0 if urgent else np.random.exponential(theta)

        return time_replacement


class Manager:
    def __init__(self, n_systems, system_factory, component_factory, inspector,
                 param, costs):
        
        # initialize parameters
        self.param = param
        self.costs = costs

        # initialize systems
        self.systems = [next(system_factory) for _ in range(n_systems)]

        # inspector and factory
        self.inspector = inspector
        self.component_factory = component_factory

        # components to be reused
        self.components_reuse = []

        # access to event times
        self.t_last_event = 0
        self.t_last_inspection = {system.id:0 for system in self.systems}
        self.t_next_inspection = {system.id:self.inspector.schedule_next(
            self.t_last_event, self.param["mu"], self.param["sigma"]) for system in self.systems}
        self.t_plan_replacement = {system.id:np.inf for system in self.systems}
        self.t_last_event_system = {system.id:0 for system in self.systems}


    def next_times(self, system):
        # compute relevant event times
        t_to_fail = system.component.age_fail-system.component.age
        t_to_insp = self.t_next_inspection[system.id]-self.t_last_event
        t_to_repl = self.t_plan_replacement[system.id]-self.t_last_event
        
        # closest event to happen
        t_to_evnt = min(t_to_fail, t_to_insp, t_to_repl)

        # return diferent times
        return t_to_evnt, t_to_fail, t_to_insp, t_to_repl
    

    def schedule_replacement(self, system, urgent=False):
        t_replacement_ = self.inspector.schedule_replacement(
                self.t_last_event, self.param["theta"], urgent=urgent)
        self.t_plan_replacement[system.id] = t_replacement_


    def replace_component(self, system):
        # save old and get new component
        old_component = system.component
        if len(self.components_reuse) > 0:
            component_reuse = True
            new_component = self.components_reuse.pop(0)
        else:
            component_reuse = False
            new_component = next(self.component_factory)
        
        # replace component
        system.component = new_component

        # save old component if possible
        has_not_expired = old_component.age < old_component.age_expi
        has_not_failled = old_component.age < old_component.age_fail
        ff = None
        if has_not_expired and has_not_failled:
            ff = self.inspector.inspect_ff(old_component)
            if not ff:
                self.components_reuse.append(old_component)
        
        return ff, component_reuse
    

    def next_event_(self, system):
        # compute next relevant event times
        t_to_events = self.next_times(system=system)
        t_to_evnt, t_to_fail, t_to_insp, t_to_repl = t_to_events

        # update all system and component ages
        self.t_last_event += t_to_evnt
        for system_ in self.systems:
            system_.age += t_to_evnt
            system_.component.age += t_to_evnt

        # save info to report before replacement
        component_id = system.component.id
        component_age = system.component.age
        usage_since_last_event_h = self.t_last_event
        usage_since_last_event_h -= self.t_last_event_system[system.id]
        
        # update last event time for system
        self.t_last_event_system[system.id] = self.t_last_event

        # evaluate different event cases
        ff = None
        event_report = None
        if t_to_evnt == t_to_repl:
            event_type = "replacement"
            # replace
            ff, component_reuse = self.replace_component(system)
            
            # compute cost
            event_cost = self.costs["replacement"]
            if component_reuse:
                event_report = "reused"
            else:
                event_report = "unused"
                event_cost += self.costs["component"]

            # unschedule replacement
            self.t_plan_replacement[system.id] = np.inf

        elif t_to_evnt == t_to_fail:
            event_type = "failure"
            event_cost = self.costs["failure"]
            # schedule imediate replacement
            self.schedule_replacement(system, urgent=True)
            
        elif t_to_evnt == t_to_insp:
            event_type = "inspection"
            event_cost = self.costs["inspection"]

            # checks expiration date
            if system.component.age >= system.component.age_expi:
                replace = True
                event_report = "expired"
            else:
                # checks wear level
                replace = self.inspector.inspect(system.component)
                if replace:
                    event_report = "wornout"

            # schedule a replacement if necessary
            if replace:
                self.schedule_replacement(system, urgent=False)

            # schedule next inspection
            self.t_last_inspection[system.id] = self.t_last_event
            self.t_next_inspection[system.id] = self.inspector.schedule_next(
                self.t_last_event, self.param["mu"], self.param["sigma"])

        else:
            raise Exception("An Unknown Event Type Occurred")

        # update cost
        system.cost_cumulated += event_cost

        # event data
        event_data = {
            'system_id':system.id,
            'component_id':component_id,
            'event_date':self.t_last_event,
            'event_time':None,
            'event_type':event_type,
            'event_report':event_report,
            'system_age':system.age,
            'component_age':component_age,
            'usage_since_last_event_h':usage_since_last_event_h,
            'FF':ff,
            'cost_event':event_cost,
            'cost_cumulated':system.cost_cumulated}
        
        return event_data
    

    def next_event(self):
        # sort all systems by closest event time
        get_next_event_time = lambda system: self.next_times(system)[0]
        ordered_by_time = sorted(self.systems, key=get_next_event_time)

        # run closest event and return results
        next_event_system = ordered_by_time[0]
        return self.next_event_(next_event_system)
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 16:15:43 2022

@author: theoa
"""

from assets.Asset import AssetM
import pyomo.environ as pyo


class CHPM(AssetM):
    
    def __init__(self, node, name, params):
        
        super().__init__(node, name, "produce", True, True)
        
        self.min_elec_prod = params['min_prod']
        self.max_elec_prod = params['max_prod']
        self.elec_prod_cost = params['prod_cost']
        self.heat_to_power_ratio = params['ratio']

        """
        self.min_time_btw_maint=8030 #hours
        self.opt_time_btw_maint=8760 #hours
        self.max_time_btw_maint=9490 #hours
        self.time_during_maint=48 #hours
        """
    
    def populate(self, time_series):
        time = range(len(time_series))
        model = self.model
        # TODO put his in the wring spot  (maybe at creation of CHP)
        production_price = [self.elec_prod_cost for t in time]
        
        # boundary and constraints
        model.chp_on = pyo.Var(time, domain=pyo.Binary)
        model.produce = pyo.Var(time, domain=pyo.NonNegativeReals)
        model.produce_h = pyo.Var(time, domain=pyo.NonNegativeReals)

        model.on_rule_max = pyo.Constraint(time, rule=lambda model, t: model.produce[t] <= self.max_elec_prod *
                                                                       model.chp_on[t])
        model.on_rule_min = pyo.Constraint(time, rule=lambda model, t: model.produce[t] >= self.min_elec_prod *
                                                                       model.chp_on[t])

        model.add_component('cost', pyo.Var(domain=pyo.NonNegativeReals, initialize=0.0))
        model.cost_rule = pyo.Constraint(expr=pyo.sum_product(model.produce, production_price, index=time)
                                              == model.cost)

        model.chp_rule = pyo.Constraint(time, rule=lambda model, t: model.produce_h[t] == model.produce[t] *
                                                                    self.heat_to_power_ratio)

        return self.model
        

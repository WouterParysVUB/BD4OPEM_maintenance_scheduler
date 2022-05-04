# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 16:16:57 2022

@author: theoa
"""

# import sys
from random import Random

# sys.path.append("Users\theoa\Desktop\VUB\BD4OPEM\Bomb\assets")

from assets.Asset import AssetM
import pyomo.environ as pyo


class ConsumerM(AssetM):
    
    def __init__(self, node, name):
        super().__init__(node, name, "demand", False, False)

    def populate(self, time_series):
        model = self.model
        time = range(len(time_series))
                
        # boundary and constraints
        model.demand = pyo.Var(time, domain=pyo.NonNegativeReals)
        demand_gen = [3 + Random().random() * 8 for t in time]
        model.demand_rule = pyo.Constraint(time, rule=lambda model, t: model.demand[t] == demand_gen[t])

        model.demand_h = pyo.Var(time, domain=pyo.NonNegativeReals)
        demand_gen_h = [Random().random() * 20 for t in time]
        model.demand_rule_h = pyo.Constraint(time, rule=lambda model, t: model.demand_h[t] == demand_gen_h[t])

        model.add_component('cost', pyo.Var(domain=pyo.NonNegativeReals, initialize=0.0))

        # TODO this line should be added
        return self.model
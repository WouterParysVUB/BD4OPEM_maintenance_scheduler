# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 16:15:58 2022

@author: theoa
"""

from assets.Asset import AssetM
import pyomo.environ as pyo


class BoilerM(AssetM):

    def __init__(self, node, name, params):
        super().__init__(node, name, "produce", False, True)

        self.min_heat_prod = params['min_prod']
        self.max_heat_prod = params['max_prod']
        self.heat_prod_cost = params['prod_cost']

    def populate(self, time_series):
        model = self.model
        time = range(len(time_series))
        production_cost = [self.heat_prod_cost for t in time]

        # boundary and constraints
        model.produce_h = pyo.Var(time, domain=pyo.NonNegativeReals)

        model.cost = pyo.Var(domain=pyo.NonNegativeReals, initialize=0.0)
        # model.add_component('cost', pyo.Var(domain=pyo.NonNegativeReals, initialize=0.0))
        model.cost_rule = pyo.Constraint(expr=pyo.sum_product(model.produce_h, production_cost, index=time)
                                              == model.cost)

        # TODO this line should be added
        return self.model

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 16:15:43 2022

@author: theoa
"""

from assets.Asset import AssetM
import pyomo.environ as pyo


class PublicGridM(AssetM):

    def __init__(self, node, name, cost):
        super().__init__(node, name, "produce", True, False)

        self.min_elec_prod = 0
        self.max_elec_prod = 40
        self.elec_prod_cost = cost

    def populate(self, time_series):
        time = range(len(time_series))
        model = self.model
        # TODO put his in the wring spot  (maybe at creation of the grid)
        buy_price = [self.elec_prod_cost for t in time]

        # boundary and constraints
        model.produce = pyo.Var(time, domain=pyo.NonNegativeReals, bounds=(self.min_elec_prod, self.max_elec_prod))
        model.add_component('cost', pyo.Var(domain=pyo.NonNegativeReals, initialize=0.0))

        model.cost_rule = pyo.Constraint(expr=pyo.sum_product(model.produce, buy_price, index=time)
                                              == model.cost)

        return self.model



# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 14:54:14 2022

@author: theoa
"""

import sys
import os

"""os.getcwd()
sys.path.append(os.getcwd())
print(os.getcwd())"""

# asset_dir = os.getcwd() + "\\" + "assets"
# sys.path.append(asset_dir)

"""print(asset_dir)"""

# from assets.Asset import AssetM
# from assets.CHP import CHPM
# from assets.Boiler import BoilerM
# from assets.Consumer import ConsumerM

import pyomo.environ as pyo
from datetime import timedelta, datetime
from datetime import date


# import pytz

class NodeM():
    """
    Node that contains information about all the components for the simulation
    :ivar local_tz: the timezone of the node
    :type local_tz: timezone
    :ivar start_time: start time of the simulation
    :type start_time: datetime.datetime
    :ivar end_time: end time of the simulation
    :type end_time: datetime.datetime
    :ivar time_step: time between each step
    :type time_step: datetime.timedelta
    :ivar utc_datetime: simulation time in utc
    :type utc_datetime: datetime.datetime
    :ivar datetime: simulation time in node zone
    :type datetime: datetime.datetime
    :ivar environments: list containing all the environments of node
    :type environments: list[Environment]
    :ivar nodes: list containing all the nodes of node
    :type nodes: list[Node]
    :ivar branches:
    """

    def __init__(self):  # , start_time, end_time, time_step, timezone="UTC"):

        # set time parameters

        # self.local_tz = pytz.timezone(timezone)
        self.start_time: datetime.datetime = datetime(2021, 1, 1, 0, 0, 0)
        self.end_time: datetime.datetime = datetime(2021, 6, 1, 0, 0, 0)
        self.time_step: datetime.timedelta = timedelta(hours=1)
        self.time_series: list = [self.start_time]
        time = self.start_time
        while time < self.end_time:
            time += self.time_step
            self.time_series.append(time)
        self.assets = []
        self.model = pyo.ConcreteModel()

        # TODO remove this line
        # super().__init__(start_time, end_time, time_step, timezone)
        self.sorted_assets = {}

    def populate(self):

        model = self.model

        assets_ = {
            "elec_produce": [],
            "heat_produce": [],
            "demand": []
        }

        for asset in self.assets:
            model.add_component(asset.name, asset.populate(self.time_series))
            if asset.elec_production:
                assets_['elec_produce'].append(asset)
            if asset.heat_production:
                assets_['heat_produce'].append(asset)
            if asset.type == 'demand':
                assets_['demand'].append(asset)

        self.sorted_assets = assets_

        return self.model

    def create_constraints(self):
        model = self.model
        time = range(len(self.time_series))

        e_produce_assets = self.sorted_assets['elec_produce']
        print(e_produce_assets)
        h_produce_assets = self.sorted_assets['heat_produce']
        print(h_produce_assets)
        demand_assets = self.sorted_assets["demand"]
        print(demand_assets)

        # support variables for electricity production and consumption
        model.tot_production = pyo.Var(time, domain=pyo.NonNegativeReals)
        model.tot_consumption = pyo.Var(time, domain=pyo.NonNegativeReals)

        model.prod_rule = pyo.Constraint(time, rule=lambda model, t: model.tot_production[t] ==
                                                                     pyo.quicksum(prod_asset.model.produce[t] for
                                                                                  prod_asset in e_produce_assets))

        model.cons_rule = pyo.Constraint(time, rule=lambda model, t: model.tot_consumption[t] ==
                                                                     pyo.quicksum(prod_asset.model.demand[t] for
                                                                                  prod_asset in demand_assets))

        model.demand_rule = pyo.Constraint(time, rule=lambda model, t: model.tot_consumption[t] ==
                                                                       model.tot_production[t])

        # support variables for heat production and consumption
        model.tot_production_h = pyo.Var(time, domain=pyo.NonNegativeReals)
        model.tot_consumption_h = pyo.Var(time, domain=pyo.NonNegativeReals)

        model.prod_rule_h = pyo.Constraint(time, rule=lambda model, t: model.tot_production_h[t] ==
                                                                     pyo.quicksum(prod_asset.model.produce_h[t] for
                                                                                  prod_asset in h_produce_assets))

        model.cons_rule_h = pyo.Constraint(time, rule=lambda model, t: model.tot_consumption_h[t] ==
                                                                     pyo.quicksum(prod_asset.model.demand_h[t] for
                                                                                  prod_asset in demand_assets))

        model.demand_rule_h = pyo.Constraint(time, rule=lambda model, t: model.tot_consumption_h[t] ==
                                                                       model.tot_production_h[t])

    def create_objective(self):
        model = self.model

        model.total_cost = sum([asset.model.cost for asset in self.assets])

        print(model.total_cost)

        model.obj = pyo.Objective(rule=lambda model: model.total_cost, sense=pyo.minimize)

    def pre_solve(self):
        self.populate()
        self.create_constrains()
        self.create_objective()

    def solve(self):
        results = pyo.SolverFactory('gurobi').solve(self.model, tee=False)
        return results

    def post_solve(self):
        model = self.model
        for asset in self.assets:
            print(asset.model.cost.extract_values())
        for asset in self.sorted_assets['elec_produce']:
            print('elec:', asset.model.produce.extract_values())
        for asset in self.sorted_assets['heat_produce']:
            print('heat:', asset.model.produce_h.extract_values())
            if asset.elec_production:
                print('state chp:', asset.model.chp_on.extract_values())
        # print(model.tot_production.extract_values())
        for asset in self.sorted_assets['demand']:
            print('elec_d:', asset.model.demand.extract_values())
            print('heat_d:', asset.model.demand_h.extract_values())
        # print(model.tot_consumption.extract_values())

        return self.time_series, self.assets, self.sorted_assets

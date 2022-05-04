# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 15:35:48 2022

@author: theoa
"""

from Node import NodeM
from assets.Asset import AssetM
from assets.Boiler import BoilerM
from assets.CHP import CHPM
from assets.Consumer import ConsumerM
from assets.PublicGrid import PublicGridM

from matplotlib import pyplot as plt


# construct scenario
if __name__ == '__main__':
    my_node = NodeM()
    boiler1 = BoilerM(my_node, 'boiler1', {'min_prod': 0, 'max_prod': 15, 'prod_cost': 30})
    boiler2 = BoilerM(my_node, 'boiler2', {'min_prod': 0, 'max_prod': 15, 'prod_cost': 32})
    chp1 = CHPM(my_node, 'chp1', {'min_prod': 2, 'max_prod': 5, 'prod_cost': 75, 'ratio': 1.5})
    chp2 = CHPM(my_node, 'chp2', {'min_prod': 2, 'max_prod': 5, 'prod_cost': 100, 'ratio': 2.32})
    consumer = ConsumerM(my_node, 'consumer1')
    pub_grid = PublicGridM(my_node, 'grid1', 80)

    print('Assets in current Node:')
    print([(asset.name, asset.type) for asset in my_node.assets])
    print('')

    print('Built up model by populating assets and creating constraints + objective on node level')
    my_node.populate()
    my_node.create_constraints()
    my_node.create_objective()
    print('')
    print('Solve model:')
    result = my_node.solve()
    # print(result)
    time_series, assets, sorted_assets = my_node.post_solve()

    #

    #

    #

    # plot results
    plt_len = 100

    plt.figure('electricity')
    time = range(len(time_series))[:plt_len]
    plot_lower = [0 for t in time]
    for asset in sorted_assets['elec_produce']:
        values = [asset.model.produce.extract_values()[t] for t in time]
        y_to_plot = [a + b for a, b in zip(plot_lower, values)]
        plt.fill_between(time, y_to_plot, plot_lower, label=asset.name)
        plot_lower = y_to_plot
    for asset in sorted_assets['demand']:
        values = [asset.model.demand.extract_values()[t] for t in time]
        plt.plot(time, values, label=asset.name, color='black')
    plt.legend()

    plt.figure('heat')
    time = range(len(time_series))[:plt_len]
    plot_lower = [0 for t in time]
    for asset in sorted_assets['heat_produce']:
        values = [asset.model.produce_h.extract_values()[t] for t in time]
        y_to_plot = [a + b for a, b in zip(plot_lower, values)]
        plt.fill_between(time, y_to_plot, plot_lower, label=asset.name)
        plot_lower = y_to_plot
    for asset in sorted_assets['demand']:
        values = [asset.model.demand_h.extract_values()[t] for t in time]
        plt.plot(time, values, label=asset.name, color='black')
    plt.legend()

    plt.show()





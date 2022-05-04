# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 16:29:54 2022

@author: theoa
"""

import pyomo.environ as pyo
from Node import NodeM


class AssetM(object):

    def __init__(self, node, name, type_str, prod_e, prod_h):
        self.parent_node: NodeM = node
        self.name: str = name
        self.type: str = type_str
        self.elec_production: bool = prod_e
        self.heat_production: bool = prod_h
        self.model = pyo.Block(concrete=True)
        node.assets += [self]

        super().__init__()

    def populate(self):
        """
        Create a pyomo environ block and create rules based on the initialised attributes. Only add rules that are
        for the asset itself.
        :return: pyomo.core.base.Block
        """
        pass
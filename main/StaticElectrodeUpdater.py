#!/usr/bin/env python

from main.ElectrodeUpdater import ElectrodeUpdater

import pygimli as pg
import numpy as np

# ElectrodeUpdater that just reuses the previous electrode configuration
class StaticElectrodeUpdater(ElectrodeUpdater):

    def __init__(self, world_x, spacing):
        self.__world_x = world_x
        self.__spacing = spacing

        self.__folder = None

    def init_scheme(self):
        # TODO
        return None

    def set_essentials(self, folder):
        self.__folder = folder

    def update_scheme(self, old_scheme, fop, inv_grid, inv_result):
        return old_scheme



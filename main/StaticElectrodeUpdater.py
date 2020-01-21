#!/usr/bin/env python

from main.ElectrodeUpdater import ElectrodeUpdater

import pygimli as pg
import numpy as np

# ElectrodeUpdater that just reuses the previous electrode configuration
class StaticElectrodeUpdater(ElectrodeUpdater):

    def __init__(self):
        self.__folder = None

    def set_essentials(self, folder):
        self.__folder = folder

    def init_electrodes(self, world_x, max_spacing):
        electrode_count = np.ceil(world_x / max_spacing)
        return pg.utils.grange(start=0, end=world_x, n=electrode_count)

    def update_scheme(self, old_scheme, world_x, min_spacing, max_spacing,
                          fop, inv_grid, inv_result):
        return old_scheme



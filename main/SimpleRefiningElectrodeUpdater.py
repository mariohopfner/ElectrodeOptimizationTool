#!/usr/bin/env python

from main.ElectrodeUpdater import ElectrodeUpdater

import pygimli as pg
import numpy as np

# ElectrodeUpdater that halves the electrode spacing
class SimpleRefiningElectrodeUpdater(ElectrodeUpdater):

    def __init__(self):
        self.__folder = None

    def set_essentials(self, folder):
        self.__folder = folder

    def init_electrodes(self, world_x, max_spacing):
        electrode_count = np.ceil(world_x / max_spacing) + 1
        return pg.utils.grange(start=0, end=world_x, n=electrode_count)

    def update_scheme(self, old_scheme, world_x, min_spacing, max_spacing,
                          fop, inv_grid, inv_result):

        # new_electrodes = [old_electrodes[0]]
        # for i in range(1, len(old_electrodes)):
        #     if (old_electrodes[i] - old_electrodes[i - 1]) > 2*min_spacing:
        #         new_electrodes.append(old_electrodes[i - 1] + (old_electrodes[i] - old_electrodes[i - 1]) / 2)
        #     new_electrodes.append(old_electrodes[i])
        # return pg.RVector(new_electrodes)
        # TODO
        return old_scheme

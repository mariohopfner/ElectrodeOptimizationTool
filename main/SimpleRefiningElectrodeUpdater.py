#!/usr/bin/env python

from main.ElectrodeUpdater import ElectrodeUpdater

import pygimli as pg
import numpy as np

# ElectrodeUpdater that halves the electrode spacing
class SimpleRefiningElectrodeUpdater(ElectrodeUpdater):

    def __init__(self, world_x, spacing):
        self.__world_x = world_x
        self.__spacing = spacing

        self.__folder = None

    def set_essentials(self, folder):
        self.__folder = folder

    def init_scheme(self):
        # TODO
        return None

    def update_scheme(self, old_scheme, fop, inv_grid, inv_result):

        # new_electrodes = [old_electrodes[0]]
        # for i in range(1, len(old_electrodes)):
        #     if (old_electrodes[i] - old_electrodes[i - 1]) > 2*min_spacing:
        #         new_electrodes.append(old_electrodes[i - 1] + (old_electrodes[i] - old_electrodes[i - 1]) / 2)
        #     new_electrodes.append(old_electrodes[i])
        # return pg.RVector(new_electrodes)
        # TODO
        return old_scheme

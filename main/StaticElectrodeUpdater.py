#!/usr/bin/env python

import numpy as np
import pygimli as pg
import pybert as pb

import util.schemeUtil as schemeUtil

from main.ElectrodeUpdater import ElectrodeUpdater

class StaticElectrodeUpdater(ElectrodeUpdater):
    """ An ElectrodeUpdater-implementation providing static electrode configurations-

    This class is an implementation of the abstract ElectrodeUpdater-class providing unchanging electrode "updates".
    After initializing the electrode scheme, the configurations will stay the same for every iteration.

    Parameter:
        world_x: A float describing the worlds x dimension.
        spacing: A float describing the distance between electrodes.
        configs: A list with strings indicating the configuration types used for data acquisition.

    Typical usage example:
        electrode_updater = StaticElectrodeUpdater(...)
        fic = FlexibleInversionController(..., electrode_updater)
    """
    def __init__(self, world_x: float, spacing: float, electrode_offset: float, configs: list):
        self.__world_x = world_x
        self.__spacing = spacing
        self.__electrode_offset = electrode_offset
        self.__configs = configs
        self.__folder_tmp = None

    def init_scheme(self):
        """ Creates the initial measurement scheme.

        Creates an initial electrode setup with the selected electrode configuration types.

        Returns:
            The scheme containing the initial electrode configurations.
        """
        electrode_count = np.ceil((self.__world_x - 2 * self.__electrode_offset) / self.__spacing) + 1
        electrodes = pg.utils.grange(start=self.__electrode_offset, end=self.__world_x - self.__electrode_offset,
                                     n=electrode_count)
        # Create initial scheme
        scheme = pb.createData(elecs=electrodes, schemeName=self.__configs[0])
        for i in range(1, len(self.__configs) - 1):
            scheme_tmp = pb.createData(elecs=electrodes, schemeName=self.__configs[i])
            scheme = schemeUtil.merge_schemes(scheme1=scheme, scheme2=scheme_tmp, tmp_dir=self.__folder_tmp)
        return scheme

    def set_essentials(self, folder):
        """ Sets a few parameters at runtime.

        Utility method for setting parameters at runtime (or after FlexibleInversionController construction) which can
        be set before.

        Parameter:
            folder: the folder which is used for persisting iteration-specific data
        """
        self.__folder_tmp = folder + 'tmp/'

    def update_scheme(self, old_scheme, fop, inv_grid, inv_result, iteration_subdir):
        """ Returns old_scheme to not change the electrode configurations.

        Parameter:
            old_scheme: The currently used measurement scheme.
            fop: The forward operator, the last inversion used.
            inv_grid: The mesh used in the last inversion.
            inv_result: The resistivities on inv_grid.
            iteration_subdir: Subfolder to save files for debugging and testing purposes.

        Returns:
            The old scheme.
        """
        return old_scheme

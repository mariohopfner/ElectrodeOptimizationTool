#!/usr/bin/env python

class ElectrodeUpdater:
    """ An abstract class providing an interface for class initializing and updated electrode schemes.
    """

    def init_scheme(self):
        """ Creates the initial measurement scheme.

        Returns:
            The scheme containing the initial electrode configurations.
        """
        pass

    def update_scheme(self, old_scheme, fop, inv_grid, inv_result, iteration_subdir):
        """ Updates the used electrode configurations based on different criteria.

        Parameter:
            old_scheme: The currently used measurement scheme.
            fop: The forward operator, the last inversion used.
            inv_grid: The mesh used in the last inversion.
            inv_result: The resistivities on inv_grid.
            iteration_subdir: Subfolder to save files for debugging and testing purposes.

        Returns:
            The updated scheme.
        """
        pass

    def set_essentials(self, folder):
        """ Sets a few parameters at runtime.

        Parameter:
            folder: the folder which is used for persisting iteration-specific data
        """
        pass